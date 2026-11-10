import api from "./core.cjs";

export function principlesExperiment(lesson, fixture, h) {
  if (lesson.id === "L03") return `<h2 id="experiment-title">同一个“苹果”，两种语境</h2>
<label for="vector-context">选择句子<select id="vector-context">${fixture.contexts.map(c => `<option value="${h(c.id)}">${h(c.text)}</option>`).join("")}</select></label>
<p class="sentence" id="vector-sentence"></p><dl class="readings"><div><dt>示意 token ID</dt><dd>${fixture.token.id}</dd></div><div><dt>初始查表向量</dt><dd id="initial-vector"></dd></div><div><dt>上下文后示意表示</dt><dd id="context-vector"></dd></div></dl>
<div id="vector-plot" class="plot"></div><p class="caption">● 当前语境；① 水果；② 设备；③ 与①同平面；④ 零向量。坐标仅取前两维，重合点用双圈显示。</p>
<div id="vector-similarities"></div><details class="numbers"><summary>展开全部三维数字</summary><div id="vector-numbers"></div></details>
<button id="reset-vectors" type="button">回到水果语境</button><p class="status" id="vector-status" role="status"></p>`;

  if (lesson.id === "L04") return `<h2 id="experiment-title">这一行能用到哪些位置？</h2>
<label for="attention-position">当前位置<select id="attention-position">${fixture.tokens.map((token, i) => `<option value="${i}" ${i === fixture.initialPosition ? "selected" : ""}>${i + 1} · ${h(token)}</option>`).join("")}</select></label>
<p class="sentence" id="attention-prefix"></p><label class="check-control"><input id="change-future" type="checkbox">只修改未来位置的 V（第一维 +100，第二维 +50）</label>
<div id="attention-weights"></div><p class="byte-detail" id="attention-sum"></p><p class="status" id="attention-status" role="status"></p>
<details class="numbers"><summary>展开 Q/K/V 与计算过程</summary><div id="attention-numbers"></div></details><button id="reset-attention" type="button">重置位置和未来值</button>`;

  if (lesson.id === "L05") return `<h2 id="experiment-title">让小模型学着接下一步</h2>
<details class="numbers" open><summary>训练集与未见组合</summary><p>训练集（保留重复）：${fixture.sequences.map(s => h(s.join(""))).join("、")}</p><p>未见组合：${fixture.heldOut.map(s => h(s.join(""))).join("、")}</p></details>
<label class="range-control" for="learning-rate">学习率 <output id="learning-rate-value">${fixture.learningRate}</output><input type="range" id="learning-rate" min="0.05" max="2" step="0.05" value="${fixture.learningRate}"></label>
<div class="actions"><button class="primary" id="train-step" type="button">更新一步</button><button id="train-run" type="button">连续训练</button><button id="train-pause" type="button" disabled>暂停</button><button id="train-reset" type="button">重置参数</button></div>
<p class="status" id="training-status" role="status"></p><dl class="readings" id="training-metrics" aria-label="当前训练指标"></dl>
<div id="loss-plot" class="plot"></div><p class="caption" id="loss-axis"></p><p class="caption">实线：训练损失；虚线：未见组合损失。纵轴为交叉熵（自然对数），越低表示这组目标平均获得的概率越高。</p>
<div class="control-grid"><label for="previous-token">前一个 token<select id="previous-token">${fixture.vocabulary.map(t => `<option ${t === "喝" ? "selected" : ""}>${h(t)}</option>`).join("")}</select></label><label for="target-token">观察的下一个 token<select id="target-token">${fixture.vocabulary.map(t => `<option ${t === "水" ? "selected" : ""}>${h(t)}</option>`).join("")}</select></label></div>
<ul id="training-prediction" class="bars" aria-label="当前下一步分布"></ul><button id="predict-only" type="button">只预测一次，不训练</button><p id="prediction-status" role="status"></p>
<details class="numbers"><summary>展开选中参数的一步更新</summary><div id="gradient-detail"></div></details><details class="numbers"><summary>查看最近的实算曲线点</summary><div id="loss-points"></div></details>`;

  if (lesson.id === "L06") return `<h2 id="experiment-title">比较训练信号，再核对一句回答</h2>
<label for="assistant-stage">训练阶段<select id="assistant-stage">${fixture.stages.map(stage => `<option value="${h(stage.id)}">${h(stage.name)}</option>`).join("")}</select></label><div id="stage-detail"></div>
<p class="byte-detail">对话格式示意：<code>user：提取时间 → assistant：周六14:00</code>。这是消息角色与边界，不是第四个训练阶段。</p>
<fieldset><legend>${h(fixture.challenge.prompt)}</legend>${fixture.challenge.answers.map(a => `<label class="answer-choice"><input type="radio" name="assistant-answer" value="${h(a.id)}">${h(a.text)}</label>`).join("")}</fieldset>
<div class="actions"><button class="primary" id="check-assistant" type="button">核对依据</button><button id="reset-assistant" type="button">重新比较</button></div><p class="status" id="assistant-status" role="status">先选择你认为有依据的一句。</p>`;
  return null;
}

export function principlesStatic(lesson, fixture, h) {
  if (lesson.id === "L03") return `<p>初始查表向量始终是 [${fixture.token.initial.join(", ")}]。水果语境后示意表示为 [${fixture.contexts[0].representation.join(", ")}]，公司语境为 [${fixture.contexts[1].representation.join(", ")}]。</p><p>水果表示与同平面异第三维向量的三维余弦为 ${api.cosine(fixture.contexts[0].representation, fixture.references[2].vector).toFixed(4)}。图上重合，完整表示仍不同。零向量余弦未定义。</p>`;
  if (lesson.id === "L04") {
    const result = api.attention(fixture.Q, fixture.K, fixture.V, fixture.initialPosition);
    return `<p>选第二个位置“把”，可见“我、把”。权重为 [${result.weights.map(v => v.toFixed(4)).join(", ")}]，汇总 V 得 [${result.output.map(v => v.toFixed(4)).join(", ")}]。</p><p>未来两项权重为零，修改它们的 V 不改变当前输出。移到最后一项时全部位置可见。</p>`;
  }
  if (lesson.id === "L05") {
    const trainer = api.createTrainer(fixture);
    const before = trainer.snapshot();
    for (let i = 0; i < 100; i++) trainer.step(fixture.learningRate);
    const after = trainer.snapshot();
    return `<p>种子 ${fixture.seed}，学习率 ${fixture.learningRate}，训练集：${fixture.sequences.map(s => h(s.join(""))).join("、")}。未见组合：${fixture.heldOut.map(s => h(s.join(""))).join("、")}。</p><p>本地复算 100 步：训练损失 ${before.loss.toFixed(4)} → ${after.loss.toFixed(4)}；未见组合损失 ${before.heldOut.toFixed(4)} → ${after.heldOut.toFixed(4)}。使用更新后的参数预测不会再更新它们。</p>`;
  }
  if (lesson.id === "L06") return `${fixture.stages.map(stage => `<p><b>${h(stage.name)}</b>：${h(stage.signal)}。${h(stage.effect)}</p>`).join("")}<p>${h(fixture.challenge.prompt)} ${h(fixture.challenge.feedback)}</p>`;
  return null;
}
