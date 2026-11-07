(function () {
  "use strict";
  const { lesson, fixture } = JSON.parse(document.getElementById("lab-data").textContent);
  const api = globalThis.LLMLab;
  const $ = (id) => document.getElementById(id);
  const h = (value) => String(value).replace(/[&<>"']/g, ch => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[ch]);
  const vector = (values) => `[${values.map(value => value.toFixed(4)).join(", ")}]`;
  const row = (term, value) => `<div><dt>${h(term)}</dt><dd>${h(value)}</dd></div>`;
  const bars = (labels, values) => labels.map((label, i) => `<li class="bar-row"><div class="bar-title"><span>${h(label)}</span><span>${(values[i] * 100).toFixed(2)}%</span></div><div class="bar-track" aria-hidden="true"><div class="bar-fill" style="width:${values[i] * 100}%"></div></div></li>`).join("");

  if (lesson.id === "L03") {
    function render() {
      const context = fixture.contexts.find(c => c.id === $("vector-context").value);
      $("vector-sentence").textContent = context.text;
      $("initial-vector").textContent = vector(fixture.token.initial);
      $("context-vector").textContent = vector(context.representation);
      $("vector-similarities").innerHTML = `<dl class="readings">${fixture.references.map((ref, i) => { const similarity = api.cosine(context.representation, ref.vector); return row(`${i + 1} · ${ref.label}`, similarity === null ? "未定义（零向量）" : `三维余弦 ${similarity.toFixed(4)}`); }).join("")}</dl>`;
      $("vector-numbers").innerHTML = fixture.references.map((ref, i) => `<p>${i + 1} · ${h(ref.label)}<br><code>${vector(ref.vector)}</code></p>`).join("");
      const x = v => 40 + v[0] * 290;
      const y = v => 210 - v[1] * 150;
      $("vector-plot").innerHTML = `<svg viewBox="0 0 360 260" role="img" aria-label="前两维平面，水果与第三个参考向量重合；完整数值见下方列表"><path d="M40 30 L40 210 L338 210" class="plot-axis"/><text x="20" y="28">维2</text><text x="291" y="245">维1</text>${fixture.references.map((ref, i) => `<circle cx="${x(ref.vector)}" cy="${y(ref.vector)}" r="${i === 2 ? 12 : 7}" fill="none" class="plot-reference"/><text x="${x(ref.vector) - 8}" y="${y(ref.vector) - (i === 2 ? 42 : 19)}">${i + 1}</text>`).join("")}<circle cx="${x(context.representation)}" cy="${y(context.representation)}" r="4" class="plot-current"/></svg>`;
      $("vector-status").textContent = "初始查表向量固定；相似度按当前语境的三维示意表示实算。";
    }
    $("vector-context").addEventListener("change", render);
    $("reset-vectors").addEventListener("click", () => { $("vector-context").selectedIndex = 0; render(); });
    render();
  }

  if (lesson.id === "L04") {
    function render() {
      const position = Number($("attention-position").value);
      const changed = $("change-future");
      changed.disabled = position === fixture.tokens.length - 1;
      if (changed.disabled) changed.checked = false;
      const values = fixture.V.map((v, i) => v.map((n, j) => n + (changed.checked && i > position ? (j === 0 ? 100 : 50) : 0)));
      const base = api.attention(fixture.Q, fixture.K, fixture.V, position);
      const current = api.attention(fixture.Q, fixture.K, values, position);
      $("attention-prefix").textContent = `可见：${fixture.tokens.slice(0, position + 1).join(" → ")}`;
      $("attention-weights").innerHTML = `<ul class="bars">${bars(fixture.tokens.map((t, i) => `${i + 1} · ${t}${i > position ? "（未来，屏蔽）" : "（可见）"}`), current.weights)}</ul>`;
      $("attention-sum").textContent = `可见权重和 ${current.weights.reduce((a, b) => a + b, 0).toFixed(6)}；输出 ${vector(current.output)}。`;
      $("attention-status").textContent = changed.disabled ? "已到最后位置，没有未来项可修改。" : `${changed.checked ? "已修改未来 V" : "未来 V 保持原值"}；基线输出 ${vector(base.output)}，当前输出 ${vector(current.output)}，差值 ${vector(current.output.map((v, i) => v - base.output[i]))}。`;
      $("attention-numbers").innerHTML = `<p>当前 Q = <code>${vector(fixture.Q[position])}</code>；分数 = Q·K / √2。</p>${fixture.tokens.map((token, i) => `<div class="calculation"><b>${i + 1} · ${h(token)}</b><p>K = <code>${vector(fixture.K[i])}</code><br>V = <code>${vector(values[i])}</code><br>分数 ${current.scores[i] === null ? "屏蔽，不进入 softmax" : current.scores[i].toFixed(6)}<br>权重 × V = <code>${vector(values[i].map(v => v * current.weights[i]))}</code></p></div>`).join("")}<p>把各项“权重 × V”逐维相加，得到当前输出。</p>`;
    }
    $("attention-position").addEventListener("change", render);
    $("change-future").addEventListener("change", render);
    $("reset-attention").addEventListener("click", () => { $("attention-position").value = fixture.initialPosition; $("change-future").checked = false; render(); });
    render();
  }

  if (lesson.id === "L05") {
    let trainer = api.createTrainer(fixture);
    let running = false;
    let frame = null;
    const rate = () => Number($("learning-rate").value);
    function stop() { running = false; if (frame !== null) cancelAnimationFrame(frame); frame = null; }
    function render() {
      const state = trainer.snapshot();
      const prev = $("previous-token").value;
      const target = $("target-token").value;
      const from = fixture.vocabulary.indexOf(prev);
      const to = fixture.vocabulary.indexOf(target);
      $("learning-rate-value").textContent = rate().toFixed(2);
      $("training-metrics").innerHTML = row("训练步数", `${state.steps} / ${fixture.maxSteps}`) + row("训练损失", state.loss.toFixed(4)) + row("未见组合损失", state.heldOut.toFixed(4));
      $("training-status").textContent = state.steps >= fixture.maxSteps ? "达到 500 步上限，已停止。可重置后再比较。" : running ? "正在逐步更新，可随时暂停。" : "已暂停。可以单步更新、只预测，或重置同一种子。";
      $("train-step").disabled = running || state.steps >= fixture.maxSteps;
      $("train-run").disabled = running || state.steps >= fixture.maxSteps;
      $("train-pause").disabled = !running;
      $("predict-only").disabled = running;
      $("training-prediction").innerHTML = bars(fixture.vocabulary, trainer.predict(prev));
      const update = state.lastUpdate;
      if (update) {
        const before = update.before[from][to];
        const gradient = update.gradient[from][to];
        const oldP = api.probabilities(update.before[from], 1)[to];
        const newP = trainer.predict(prev)[to];
        $("gradient-detail").innerHTML = `<p>观察 <b>${h(prev)} → ${h(target)}</b>，最近一步（${state.steps - 1} → ${state.steps}）：</p><dl class="readings">${row("更新前参数", before.toFixed(6))}${row("平均梯度", gradient.toFixed(6))}${row("该步学习率", update.learningRate.toFixed(2))}${row("更新后参数", state.logits[from][to].toFixed(6))}${row("更新前目标概率", `${(oldP * 100).toFixed(4)}%`)}${row("更新后目标概率", `${(newP * 100).toFixed(4)}%`)}</dl><p><code>${before.toFixed(6)} − ${update.learningRate.toFixed(2)} × (${gradient.toFixed(6)}) = ${state.logits[from][to].toFixed(6)}</code></p><p class="caption">这是选中参数的一步更新；训练同时更新整张表。只看前一个 token 的 bigram 无法利用更早的“我/她”。</p>`;
      } else $("gradient-detail").textContent = "还没有更新。先点“更新一步”，再比较参数与概率。";
      const ceiling = Math.ceil(Math.max(...state.history.flatMap(p => [p.loss, p.heldOut])) * 10) / 10;
      const visibleSteps = Math.max(20, Math.ceil(state.steps / 20) * 20);
      const point = (p, key) => `${(22 + p.step / visibleSteps * 316).toFixed(2)},${(186 - p[key] / ceiling * 162).toFixed(2)}`;
      $("loss-plot").innerHTML = `<svg viewBox="0 0 360 210" role="img" aria-label="实算损失曲线，数值与最近曲线点在图后列出"><path d="M22 20 L22 186 L338 186" class="plot-axis"/><polyline points="${state.history.map(p => point(p, "loss")).join(" ")}" class="loss-training"/><polyline points="${state.history.map(p => point(p, "heldOut")).join(" ")}" class="loss-held-out"/></svg>`;
      $("loss-axis").textContent = `横轴：0 → ${visibleSteps} 步，随进度扩展；纵轴：0 → ${ceiling.toFixed(1)}。目前 ${state.steps} 步。`;
      $("loss-points").innerHTML = state.history.slice(-8).map(p => `<p>第 ${p.step} 步：训练 ${p.loss.toFixed(6)}；未见组合 ${p.heldOut.toFixed(6)}</p>`).join("");
    }
    function advance() {
      if (!running) return;
      for (let i = 0; i < 2; i++) if (!trainer.step(rate())) { stop(); break; }
      if (trainer.snapshot().steps >= fixture.maxSteps) stop();
      render();
      if (running) frame = requestAnimationFrame(advance);
    }
    $("train-step").addEventListener("click", () => { trainer.step(rate()); $("prediction-status").textContent = ""; render(); });
    $("train-run").addEventListener("click", () => { running = true; $("prediction-status").textContent = ""; render(); frame = requestAnimationFrame(advance); });
    $("train-pause").addEventListener("click", () => { stop(); render(); });
    $("train-reset").addEventListener("click", () => { stop(); trainer = api.createTrainer(fixture); $("learning-rate").value = fixture.learningRate; $("previous-token").value = "喝"; $("target-token").value = "水"; $("prediction-status").textContent = ""; render(); });
    for (const id of ["previous-token", "target-token", "learning-rate"]) $(id).addEventListener("input", () => { $("prediction-status").textContent = ""; render(); });
    $("predict-only").addEventListener("click", () => {
      const before = trainer.snapshot();
      trainer.predict($("previous-token").value);
      const after = trainer.snapshot();
      $("prediction-status").textContent = JSON.stringify(before) === JSON.stringify(after) ? `已用当前参数预测；仍是第 ${after.steps} 步，参数没有更新。` : "状态异常，请重置后重试。";
    });
    window.addEventListener("pagehide", stop);
    document.addEventListener("visibilitychange", () => { if (document.hidden) { stop(); render(); } });
    window.addEventListener("pageshow", render);
    render();
  }

  if (lesson.id === "L06") {
    function render() {
      const stage = fixture.stages.find(s => s.id === $("assistant-stage").value);
      $("stage-detail").innerHTML = `<dl class="readings">${row("训练信号", stage.signal)}${row("期望变化", stage.effect)}</dl><p class="byte-detail">${h(stage.example)}</p><p>${h(stage.boundary)}</p>`;
    }
    $("assistant-stage").addEventListener("change", render);
    document.querySelectorAll('[name="assistant-answer"]').forEach(input => input.addEventListener("change", () => { $("assistant-status").textContent = "选择已变更，重新核对依据。"; }));
    $("check-assistant").addEventListener("click", () => {
      const id = document.querySelector('[name="assistant-answer"]:checked')?.value;
      const answer = fixture.challenge.answers.find(a => a.id === id);
      $("assistant-status").textContent = answer ? `${answer.supported ? "判断有依据。" : "这句补了材料里没有的地点。"}${fixture.challenge.feedback}` : "请先选择一句回答，再核对。";
    });
    $("reset-assistant").addEventListener("click", () => { $("assistant-stage").selectedIndex = 0; document.querySelectorAll('[name="assistant-answer"]').forEach(input => { input.checked = false; }); $("assistant-status").textContent = "先选择你认为有依据的一句。"; render(); });
    render();
  }
})();
