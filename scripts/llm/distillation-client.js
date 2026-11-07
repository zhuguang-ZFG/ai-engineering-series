(function () {
  "use strict";
  const data = JSON.parse(document.getElementById("lab-data").textContent);
  if (data.lesson.id !== "L05") return;
  const fixture = data.distillation;
  const api = globalThis.LLMDistillation;
  const $ = id => document.getElementById(id);
  let logits = [...fixture.student];
  let steps = 0;
  let last = null;
  const teacher = () => fixture[$("distill-teacher").value];
  const temperature = () => Number($("distill-temperature").value);
  const alpha = () => Number($("distill-alpha").value);
  function render() {
    const result = api.evaluate(teacher(), logits, temperature(), alpha(), fixture.target);
    $("distill-temperature-value").textContent = temperature().toFixed(1);
    $("distill-alpha-value").textContent = alpha().toFixed(1);
    $("distill-distributions").replaceChildren(...fixture.labels.map((label, index) => {
      const row = document.createElement("tr");
      for (const [column, text] of [label, ...[result.teacher[index], result.student[index], result.inference[index]].map(value => (value * 100).toFixed(2) + "%")].entries()) {
        const cell = document.createElement(column ? "td" : "th");
        if (!column) cell.scope = "row";
        cell.textContent = text;
        row.append(cell);
      }
      return row;
    }));
    $("distill-loss").textContent = `第 ${steps} 步：KL(p(T)‖q(T)) = ${result.kl.toFixed(6)}；硬标签 CE = ${result.hardLoss.toFixed(6)}；混合损失 L = ${result.loss.toFixed(6)}。不同 T/α 的总损失不作直接优劣比较。`;
    $("distill-update").textContent = last ? `旧学生分数：[${last.beforeLogits.map(value => value.toFixed(6)).join(", ")}]\n混合梯度：[${last.before.gradient.map(value => value.toFixed(6)).join(", ")}]\n新值 = 旧值 − 0.4 × 梯度\n新学生分数：[${logits.map(value => value.toFixed(6)).join(", ")}]\n教师分数始终为 [${teacher().join(", ")}]` : "尚未更新参数。教师分数固定，两个学生分布来自同一组学生分数。";
    $("distill-step").disabled = $("distill-many").disabled = steps >= fixture.maxSteps;
  }
  function reset() {
    logits = [...fixture.student]; steps = 0; last = null;
    render();
    $("distill-status").textContent = "学生已重置；先比较分布，再更新。只改温度不会训练参数。";
  }
  function train(count) {
    for (let i = 0; i < count && steps < fixture.maxSteps; i++) {
      const beforeLogits = [...logits];
      const update = api.step(teacher(), logits, temperature(), alpha(), fixture.target, fixture.learningRate);
      last = { ...update, beforeLogits };
      logits = update.logits; steps++;
    }
    render();
    $("distill-status").textContent = steps >= fixture.maxSteps ? "已到 100 步上限；可重置后换条件比较。" : `已更新学生 ${steps} 步；教师没有训练。`;
  }
  $("distill-step").addEventListener("click", () => train(1));
  $("distill-many").addEventListener("click", () => train(25));
  $("distill-reset").addEventListener("click", reset);
  $("distill-teacher").addEventListener("change", reset);
  for (const id of ["distill-temperature", "distill-alpha"]) $(id).addEventListener("input", reset);
  $("distillation-lab").hidden = false;
  reset();
})();
