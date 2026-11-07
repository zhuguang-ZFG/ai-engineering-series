(function () {
  "use strict";
  function logProbabilities(logits, temperature) {
    if (!Array.isArray(logits) || logits.length < 2 || logits.some(value => !Number.isFinite(value) || Math.abs(value) > 100)) throw new RangeError("需要至少两个有限分数，绝对值不超过 100");
    if (!Number.isFinite(temperature) || temperature < 0.5 || temperature > 10) throw new RangeError("蒸馏温度须在 0.5–10 之间");
    const scaled = logits.map(value => value / temperature);
    const max = Math.max(...scaled);
    const normalizer = Math.log(scaled.reduce((sum, value) => sum + Math.exp(value - max), 0));
    return scaled.map(value => value - max - normalizer);
  }
  function evaluate(teacher, student, temperature = 2, alpha = 0.7, target = 0) {
    const teacherLog = logProbabilities(teacher, temperature);
    const studentLog = logProbabilities(student, temperature);
    if (teacher.length !== student.length) throw new RangeError("词表和候选顺序必须对齐");
    if (!Number.isFinite(alpha) || alpha < 0 || alpha > 1 || !Number.isInteger(target) || target < 0 || target >= student.length) throw new RangeError("软目标权重或硬标签无效");
    const p = teacherLog.map(Math.exp);
    const q = studentLog.map(Math.exp);
    const inference = logProbabilities(student, 1).map(Math.exp);
    const kl = p.reduce((sum, value, index) => sum + value * (teacherLog[index] - studentLog[index]), 0);
    const hardLoss = -logProbabilities(student, 1)[target];
    const gradient = student.map((_, index) => alpha * temperature * (q[index] - p[index]) + (1 - alpha) * (inference[index] - Number(index === target)));
    return { teacher: p, student: q, inference, kl, hardLoss, loss: alpha * temperature ** 2 * kl + (1 - alpha) * hardLoss, gradient };
  }
  function step(teacher, student, temperature, alpha, target, learningRate = 0.4) {
    if (!Number.isFinite(learningRate) || learningRate < 0.01 || learningRate > 1) throw new RangeError("学习率须在 0.01–1 之间");
    const before = evaluate(teacher, student, temperature, alpha, target);
    const logits = student.map((value, index) => value - learningRate * before.gradient[index]);
    const after = evaluate(teacher, logits, temperature, alpha, target);
    return { before, logits, after };
  }
  const api = { evaluate, step };
  if (typeof module !== "undefined" && module.exports) module.exports = api;
  else globalThis.LLMDistillation = Object.freeze(api);
})();
