(function () {
  "use strict";
  const { lesson, fixture } = JSON.parse(document.getElementById("lab-data").textContent);
  const api = globalThis.LLMLab;
  const $ = (id) => document.getElementById(id);
  const h = (value) => String(value).replace(/[&<>"']/g, (ch) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[ch]);

  if (lesson.id === "L01") {
    function renderTokens() {
      const example = fixture.encodings[$("encoding").value].examples.find((item) => item.id === $("token-input").value);
      $("token-text").textContent = example.text;
      $("token-counts").innerHTML = `<span>Unicode 码点 <b>${example.codePoints}</b></span><span>UTF-8 字节 <b>${example.utf8Bytes}</b></span><span>token <b>${example.tokens.length}</b></span>`;
      $("token-pieces").innerHTML = example.tokens.map((token, i) => `<button type="button" class="token-piece" data-token="${i}" aria-pressed="false">${h(api.visibleToken(token.label))}<strong>ID ${token.id}</strong></button>`).join("");
      const selectToken = (index) => {
        const token = example.tokens[index];
        $("token-detail").textContent = `第 ${index + 1} 片，ID ${token.id}。UTF-8 字节（十六进制）：${token.bytes.map((byte) => byte.toString(16).padStart(2, "0").toUpperCase()).join(" ")}。`;
        $("token-pieces").querySelectorAll("button").forEach((button, i) => button.setAttribute("aria-pressed", String(i === index)));
      };
      $("token-pieces").querySelectorAll("button").forEach((button) => button.addEventListener("click", () => selectToken(Number(button.dataset.token))));
      selectToken(0);
      const bytes = Uint8Array.from(example.tokens.flatMap((token) => token.bytes));
      const restored = new TextDecoder("utf-8", { fatal: true }).decode(bytes);
      $("token-status").textContent = restored === example.text ? "按顺序拼接所有片段字节后，已无损还原原文（含空格与换行）。" : "还原失败，请核对数据。";
    }
    $("token-input").addEventListener("change", renderTokens);
    $("encoding").addEventListener("change", renderTokens);
    renderTokens();
  }

  if (lesson.id === "L02") {
    let seed = 42;
    let session = api.createSession(fixture, seed);
    const temperature = () => Number($("temperature").value);
    function renderGeneration() {
      const state = session.snapshot();
      $("generated-text").innerHTML = `${h(fixture.prompt)}<mark>${h(state.text.slice(fixture.prompt.length))}</mark>`;
      $("temperature-value").textContent = temperature().toFixed(1);
      const options = state.stopped ? null : api.candidates(fixture, state.text, temperature());
      $("candidate-bars").innerHTML = options ? options.map((item) => `<li class="bar-row"><div class="bar-title"><span>${h(item.piece)}</span><span>${(item.probability * 100).toFixed(1)}%</span></div><div class="bar-track" aria-hidden="true"><div class="bar-fill" style="width:${(item.probability * 100).toFixed(4)}%"></div></div></li>`).join("") : "<li>本轮已结束。重置后可再比较分布。</li>";
      $("generate-step").disabled = state.stopped;
      $("sample-many").disabled = state.stopped;
      $("generation-history").innerHTML = state.history.map((item, i) => `<li>第 ${i + 1} 步：${item.piece === fixture.stopToken ? "选中停止符" : `接上“${h(item.piece)}”`}，选择时概率 ${(item.probability * 100).toFixed(1)}%</li>`).join("");
      return state;
    }
    $("generate-step").addEventListener("click", () => {
      const before = session.snapshot();
      const after = session.step(temperature());
      renderGeneration();
      $("sample-result").replaceChildren();
      $("generation-status").textContent = after.stopped ? after.reason : `第 ${after.steps} 步接上“${after.text.slice(before.text.length)}”。下面的候选已经按新句子更新。`;
    });
    $("temperature").addEventListener("input", () => {
      renderGeneration();
      $("sample-result").replaceChildren();
      $("generation-status").textContent = session.snapshot().stopped ? "本轮已结束。重置后再观察温度变化。" : `温度已改为 ${temperature().toFixed(1)}，候选分布已更新；当前句子还没变。`;
    });
    $("reset-generation").addEventListener("click", () => {
      if (!$("seed").reportValidity()) return;
      seed = Number($("seed").value);
      session = api.createSession(fixture, seed);
      renderGeneration();
      $("sample-result").replaceChildren();
      $("generation-status").textContent = `已按种子 ${seed} 重置，保留当前温度。相同种子、温度和操作顺序可重放本地结果。`;
    });
    $("sample-many").addEventListener("click", () => {
      const results = api.sampleMany(fixture, session.snapshot().text, temperature(), seed);
      $("sample-result").innerHTML = `<h3>当前这一步的 100 次抽样</h3><p>${results.map((item) => `${h(item.piece)}：${item.count} 次`).join("；")}</p><p class="caption">没有追加正文；使用本轮重置时的种子，重新比较同一分布。有限抽样不等于理论比例。</p>`;
    });
    renderGeneration();
  }

  if (lesson.id === "L07") {
    const documents = [...document.querySelectorAll('input[name="document"]')];
    const suspects = [...document.querySelectorAll('input[name="suspect"]')];
    function clearFeedback(message) {
      fixture.claims.forEach((_, i) => $("verdict-" + i).replaceChildren());
      $("corrected-answer").hidden = true;
      $("audit-status").textContent = message;
    }
    documents.forEach((input) => input.addEventListener("change", () => clearFeedback("材料已更改，重新核对后才显示判断。")));
    suspects.forEach((input) => input.addEventListener("change", () => clearFeedback("判断已更改，点击核对查看反馈。")));
    $("reset-materials").addEventListener("click", () => {
      documents.forEach((input, i) => { input.checked = i === 0; });
      suspects.forEach((input) => { input.checked = false; });
      clearFeedback("已回到通知 A。地点有依据吗？");
    });
    $("audit-materials").addEventListener("click", () => {
      const selected = fixture.documents.filter((doc) => documents.some((input) => input.checked && input.value === doc.id));
      const results = api.auditClaims(selected, fixture.claims);
      const labels = { supported: "有材料支持", missing: "材料未提供", unsupported: "与材料不符", conflict: "材料有冲突，先核对版本" };
      let correct = 0;
      results.forEach((result, index) => {
        const needsCheck = result.status !== "supported";
        if (suspects[index].checked === needsCheck) correct++;
        $("verdict-" + index).innerHTML = `<p class="verdict ${result.status}">${labels[result.status]}</p>${result.evidence.map((item) => `<p class="evidence"><a href="#doc-${h(item.documentId)}">通知 ${h(item.documentId)}</a>“${h(item.quote)}”</p>`).join("") || '<p class="evidence">所选材料中找不到这一项。</p>'}`;
      });
      $("audit-status").textContent = selected.length ? `已核对 ${selected.length} 份材料。你的 ${correct}/4 项判断与练习标注一致；请回查每条原句。` : "没有选择材料，四项都缺少依据。请先选择通知。";
      $("corrected-answer").hidden = false;
      $("corrected-answer").innerHTML = `<h3>按材料保留的结果</h3>${results.map((result) => `<p><b>${h(result.field)}</b>：${result.status === "missing" ? "未知（材料未提供）" : result.status === "conflict" ? `${[...new Set(result.evidence.map((item) => h(item.value)))].join(" / ")}（冲突待核对）` : h(result.evidence[0].value)}</p>`).join("")}<p class="caption">这里只比对人工标注的事实。版本有效性仍要由人根据真实来源确认。</p>`;
    });
  }

  $("quiz-form").addEventListener("submit", (event) => {
    event.preventDefault();
    const selected = Number(new FormData(event.currentTarget).get("answer"));
    $("quiz-feedback").textContent = `${selected === lesson.correct ? "判断正确。" : "再回看实验里的证据。"} ${lesson.feedback}`;
  });
  document.querySelector(".lab[data-experiment]").hidden = false;
  $("quiz-form").hidden = false;
})();
