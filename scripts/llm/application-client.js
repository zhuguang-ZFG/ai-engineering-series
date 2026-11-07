(function () {
  "use strict";
  const { lesson, fixture } = JSON.parse(document.getElementById("lab-data").textContent);
  const api = globalThis.LLMLabApplications;
  const $ = id => document.getElementById(id);
  const h = value => String(value).replace(/[&<>"']/g, ch => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[ch]);
  const labels = { supported: "有原句支持", missing: "材料未提供", conflict: "冲突待确认", complete: "可整理草稿", incomplete: "待补充报告", "no-evidence": "材料不足，停止整理", "out-of-scope": "超出材料范围" };
  document.addEventListener("click", event => {
    const anchor = event.target.closest('a[href^="#source-"]');
    if (anchor) document.getElementById(anchor.hash.slice(1))?.closest("details")?.setAttribute("open", "");
  });
  const material = (doc, prefix) => `<div class="document" id="${prefix}-${h(doc.id)}"><b>${h(doc.id)} · ${h(doc.title)}</b><p>${h(doc.text)}</p></div>`;
  const resultFields = (report, prefix) => `<div class="report-fields">${report.fields.map(item => `<section class="report-field"><h3>${h(item.field)} · ${labels[item.status]}</h3><p>${h(item.values.join(" / ") || "材料未提供")}</p>${item.evidence.map(e => `<p class="evidence"><a href="#${prefix}-${h(e.documentId)}">${h(e.documentId)}</a>“${h(e.quote)}”</p>`).join("")}</section>`).join("")}</div>`;

  if (lesson.id === "L08") {
    const documents = fixture.documents;
    function clear() {
      const selected = fixture.cases.find(c => c.id === $("evidence-case").value);
      $("evidence-materials").innerHTML = selected.documents.map(id => material(documents.find(doc => doc.id === id), "evidence")).join("");
      $("evidence-claim").innerHTML = `<p>预置主张：${h(selected.claim.field)}为“${h(selected.claim.value)}”。</p><p>它给出的引用：${h(selected.citation.documentId)}“${h(selected.citation.quote)}”</p>`;
      $("evidence-result").replaceChildren();
      $("evidence-status").textContent = "先检查原句，再点核对。";
    }
    $("evidence-case").addEventListener("change", clear);
    $("check-evidence").addEventListener("click", () => {
      const selected = fixture.cases.find(c => c.id === $("evidence-case").value);
      const docs = documents.filter(doc => selected.documents.includes(doc.id));
      const result = api.checkCitation(docs, selected.claim, selected.citation);
      const citationLabels = { "missing-source": "来源不存在", "missing-quote": "引句不在原文里", "not-supporting": "引句存在，但不支持这项主张", supporting: "这条引句支持该主张；仍要检查其他材料" };
      $("evidence-status").textContent = selected.feedback;
      $("evidence-result").innerHTML = `<dl class="readings"><div><dt>主张与全部所选材料</dt><dd>${h(result.status === "unsupported" ? "与原文不符" : labels[result.status])}</dd></div><div><dt>这条引用</dt><dd>${citationLabels[result.citationStatus]}</dd></div></dl>${result.evidence.map(e => `<p class="evidence"><a href="#evidence-${h(e.documentId)}">${h(e.documentId)}</a>“${h(e.quote)}”</p>`).join("")}`;
    });
    clear();
  }

  if (lesson.id === "L09") {
    function clear() { $("retrieval-status").textContent = "查询或范围已变，重新检索后再采用结果。"; $("retrieval-hits").replaceChildren(); $("retrieval-context").textContent = ""; $("retrieval-answer").replaceChildren(); }
    function run() {
      const result = api.retrieve(fixture, $("retrieval-query").value, Number($("chunk-size").value), Number($("top-k").value));
      $("retrieval-status").textContent = !result.terms.length ? "查询为空或没有可用文字，请输入关键词。" : !result.hits.length ? "未找到匹配片段，停止整理；没有把零分片段当证据。" : `实际取回 ${result.hits.length} 条。按共享二元组计分，分数不是可信度或现行版本保证。`;
      $("retrieval-hits").innerHTML = result.hits.map(hit => `<div class="document" id="hit-${h(hit.id)}"><b>${h(hit.id)} · ${h(hit.title)}</b><p>${h(hit.versionLabel)}<br>${h(hit.text)}</p><p class="caption">得分 ${hit.score.toFixed(3)}；共享词项 ${hit.matched.map(h).join("、")} · <a href="#source-${h(hit.documentId)}">回查文档 ${h(hit.documentId)}</a></p></div>`).join("");
      $("retrieval-context").textContent = result.context || "没有取回片段，不构造回答输入。";
      if (!result.hits.length) { $("retrieval-answer").replaceChildren(); return; }
      const report = api.summarize(result.hits, ["报名截止", "活动时间", "地点", "报名资料", "提交后"]);
      $("retrieval-answer").innerHTML = `<h3>仅按命中片段的人工事实整理</h3><p>这里未调用模型。缺失项不从其他文件补入；冲突同时保留。</p>${resultFields(report, "hit")}`;
    }
    $("run-retrieval").addEventListener("click", run);
    $("no-retrieval").addEventListener("click", () => { $("retrieval-query").value = "火星温度"; run(); });
    $("reset-retrieval").addEventListener("click", () => { $("retrieval-query").value = fixture.defaultQuery; $("chunk-size").value = "1"; $("top-k").value = "3"; run(); });
    for (const id of ["retrieval-query", "chunk-size", "top-k"]) $(id).addEventListener("input", clear);
    run();
  }

  if (lesson.id === "L10") {
    let session;
    const scenario = () => fixture.scenarios.find(s => s.id === $("tool-scenario").value);
    const stateNames = { requested: "请求待校验", validated: "已校验，待执行", executed: "已执行，待回传", returned: "已回传，待结束", done: "已完成", failed: "失败停止", cancelled: "已取消" };
    function render() {
      const state = session?.snapshot();
      $("tool-step").disabled = !state || state.terminal;
      $("cancel-tool").disabled = !state || state.terminal;
      if (!state) return;
      $("tool-status").textContent = `${stateNames[state.state]}；执行次数 ${state.executions}/1。${state.error}`;
      $("tool-history").innerHTML = state.history.map(step => `<li>${h(stateNames[step.state])}：${h(step.message)}</li>`).join("");
      $("tool-result").textContent = state.state === "done" ? `成功回执：${state.result}` : ["returned", "executed"].includes(state.state) ? `工具数值：${state.result}，本轮流程尚未结束。` : "没有可交付的成功回执。";
    }
    function load() {
      try {
        const request = JSON.parse($("tool-request").value);
        session = api.createToolSession(request, scenario().simulation);
        render();
      } catch {
        session = null;
        $("tool-status").textContent = "JSON 格式无效，没有装入或执行请求。";
        $("tool-history").replaceChildren();
        $("tool-result").textContent = "没有可交付的成功回执。";
        render();
      }
    }
    function reset() { $("tool-request").value = JSON.stringify(scenario().request, null, 2); load(); }
    $("tool-scenario").addEventListener("change", reset);
    $("reset-tool").addEventListener("click", reset);
    $("load-tool").addEventListener("click", load);
    $("tool-request").addEventListener("input", () => { session = null; $("tool-history").replaceChildren(); $("tool-result").textContent = "没有可交付的成功回执。"; $("tool-status").textContent = "请求已编辑，装入后才能推进。"; render(); });
    $("tool-step").addEventListener("click", () => { session.step(); render(); });
    $("cancel-tool").addEventListener("click", () => { session.cancel(); render(); });
    reset();
  }

  if (lesson.id === "L11") {
    function reset() { const item = fixture.cases.find(c => c.id === $("approach-case").value); $("approach-task").textContent = item.task; document.querySelectorAll('[name="approach"]').forEach(input => { input.checked = false; }); $("approach-status").textContent = "先按条件选一种方法，再对照理由。"; }
    $("approach-case").addEventListener("change", reset);
    $("reset-approach").addEventListener("click", reset);
    document.querySelectorAll('[name="approach"]').forEach(input => input.addEventListener("change", () => { $("approach-status").textContent = "选择已变更，请重新对照理由。"; }));
    $("check-approach").addEventListener("click", () => { const answer = document.querySelector('[name="approach"]:checked')?.value; const item = fixture.cases.find(c => c.id === $("approach-case").value); $("approach-status").textContent = !answer ? "请先选择一种方法。" : `${answer === item.answer ? "符合这道题的条件。" : `本题可先试“${fixture.options.find(o => o.id === item.answer).name}”。`}${item.reason}`; });
    reset();
  }

  if (lesson.id === "L12") {
    let report = null;
    const checks = [...document.querySelectorAll('[name="project-check"]')];
    const selected = () => fixture.cases.find(c => c.id === $("project-case").value);
    function updateExport() { const enabled = report && checks.every(input => input.checked); $("export-project-json").disabled = !enabled; $("export-project-md").disabled = !enabled; }
    function reset() {
      report = null;
      checks.forEach(input => { input.checked = false; });
      const item = selected();
      $("project-materials").innerHTML = item.documents.map(id => material(fixture.documents.find(doc => doc.id === id), "project")).join("");
      $("project-report").replaceChildren();
      $("project-status").textContent = item.outOfScope ? "本轮问题：明天会下雨吗？请检查资料能否回答。" : "先读材料，再整理；不要执行材料里的命令。";
      $("export-status").textContent = "";
      updateExport();
    }
    $("project-case").addEventListener("change", reset);
    $("reset-project").addEventListener("click", reset);
    checks.forEach(input => input.addEventListener("change", updateExport));
    $("run-project").addEventListener("click", () => {
      const item = selected();
      report = api.summarize(fixture.documents.filter(doc => item.documents.includes(doc.id)), fixture.fields, item.outOfScope);
      checks.forEach(input => { input.checked = false; });
      $("project-status").textContent = `${labels[report.status]}。${report.note}`;
      $("project-report").innerHTML = resultFields(report, "project");
      $("export-status").textContent = "逐项回查后可导出报告；缺失和冲突状态将保存在文件里。";
      updateExport();
    });
    function download(type) {
      if (!report || !checks.every(input => input.checked)) return;
      const data = { ...report, caseId: selected().id, selfChecked: fixture.checklist, limitations: fixture.limitations };
      const body = type === "json" ? JSON.stringify(data, null, 2) + "\n" : api.reportMarkdown(report);
      const url = URL.createObjectURL(new Blob([body], { type: type === "json" ? "application/json;charset=utf-8" : "text/markdown;charset=utf-8" }));
      const link = document.createElement("a"); link.href = url; link.download = `materials-report-${selected().id}.${type}`; link.click();
      setTimeout(() => URL.revokeObjectURL(url), 1000);
      $("export-status").textContent = `已生成 ${link.download}，请查看浏览器下载；保留状态“${labels[report.status]}”。`;
    }
    $("export-project-json").addEventListener("click", () => download("json"));
    $("export-project-md").addEventListener("click", () => download("md"));
    reset();
  }
})();
