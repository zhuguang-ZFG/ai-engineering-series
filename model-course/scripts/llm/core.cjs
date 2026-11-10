/* Shared by the offline page and Node tests. No network or UI dependencies. */
(function () {
  "use strict";

  function probabilities(logits, temperature) {
    if (!Array.isArray(logits) || !logits.length || logits.some((n) => !Number.isFinite(n))) {
      throw new RangeError("候选分数必须是非空的有限数值数组");
    }
    if (!Number.isFinite(temperature) || temperature < 0 || temperature > 2) {
      throw new RangeError("温度必须在 0–2 之间");
    }
    const max = Math.max(...logits);
    if (temperature === 0) return logits.map((_, i) => i === logits.indexOf(max) ? 1 : 0);
    const values = logits.map((n) => Math.exp((n - max) / temperature));
    const total = values.reduce((sum, n) => sum + n, 0);
    return values.map((n) => n / total);
  }

  function random(seed) {
    let state = seed >>> 0;
    return () => {
      state = (Math.imul(state, 1664525) + 1013904223) >>> 0;
      return state / 4294967296;
    };
  }

  function choose(distribution, rng) {
    const sample = rng();
    if (!Number.isFinite(sample) || sample < 0 || sample >= 1) throw new RangeError("Invalid random sample");
    let cumulative = 0;
    for (let i = 0; i < distribution.length; i++) {
      cumulative += distribution[i];
      if (sample < cumulative) return i;
    }
    return distribution.length - 1;
  }

  function candidates(model, text, temperature) {
    const state = Object.hasOwn(model.states, text) ? model.states[text] : null;
    if (!state) return null;
    const distribution = probabilities(state.map((item) => item.logit), temperature);
    return state.map((item, i) => ({ ...item, probability: distribution[i] }));
  }

  function createSession(model, seed = 42) {
    if (!Number.isInteger(seed) || seed < 0 || seed > 4294967295) throw new RangeError("种子必须是 32 位非负整数");
    let text = model.prompt;
    let steps = 0;
    let stopped = false;
    let reason = "";
    const rng = random(seed);
    const history = [];
    return {
      snapshot() { return { text, steps, stopped, reason, history: history.map((item) => ({ ...item })) }; },
      step(temperature) {
        if (stopped) return this.snapshot();
        const options = candidates(model, text, temperature);
        if (!options) { stopped = true; reason = "教学模型未覆盖这个上下文"; return this.snapshot(); }
        const selected = options[choose(options.map((item) => item.probability), rng)];
        history.push({ before: text, piece: selected.piece, probability: selected.probability });
        steps++;
        if (selected.piece === model.stopToken) {
          stopped = true;
          reason = "选中了停止符，生成结束";
        } else {
          text += selected.piece;
          if (steps >= model.maxSteps) { stopped = true; reason = "已达到教学模型的步数上限"; }
        }
        return this.snapshot();
      },
    };
  }

  function sampleMany(model, text, temperature, seed = 42, count = 100) {
    if (!Number.isInteger(count) || count < 1 || count > 1000) throw new RangeError("Invalid sample count");
    const options = candidates(model, text, temperature);
    if (!options) return null;
    const rng = random(seed);
    const counts = options.map(() => 0);
    for (let i = 0; i < count; i++) counts[choose(options.map((item) => item.probability), rng)]++;
    return options.map((item, index) => ({ ...item, count: counts[index] }));
  }

  function auditClaims(documents, claims) {
    return claims.map((claim) => {
      const evidence = documents.flatMap((doc) => {
        const fact = doc.facts.find((item) => item.field === claim.field);
        return fact ? [{ documentId: doc.id, ...fact }] : [];
      });
      const values = [...new Set(evidence.map((item) => item.value))];
      const status = values.length === 0 ? "missing" : values.length > 1 ? "conflict" : values[0] === claim.value ? "supported" : "unsupported";
      return { ...claim, status, evidence };
    });
  }

  function visibleToken(text) {
    const visible = text.replaceAll(" ", "␠").replaceAll("\n", "↵").replaceAll("\t", "⇥")
      .replaceAll("\u200d", "〈连接符〉").replaceAll("\ufe0f", "〈样式符〉");
    return /^\p{Mark}/u.test(visible) ? "◌" + visible : visible;
  }

  function finiteVector(vector) {
    if (!Array.isArray(vector) || !vector.length || vector.some((value) => !Number.isFinite(value))) throw new RangeError("向量需要有限数值");
  }

  function cosine(a, b) {
    finiteVector(a); finiteVector(b);
    if (a.length !== b.length) throw new RangeError("向量维度不同");
    const aScale = Math.max(...a.map(Math.abs));
    const bScale = Math.max(...b.map(Math.abs));
    if (aScale === 0 || bScale === 0) return null;
    const aNorm = Math.hypot(...a.map(value => value / aScale));
    const bNorm = Math.hypot(...b.map(value => value / bScale));
    return Math.max(-1, Math.min(1, a.reduce((sum, value, i) => sum + (value / aScale / aNorm) * (b[i] / bScale / bNorm), 0)));
  }

  function attention(Q, K, V, position) {
    if (![Q, K, V].every(Array.isArray) || !Q.length || K.length !== Q.length || V.length !== Q.length) throw new RangeError("矩阵行数不同");
    for (const matrix of [Q, K, V]) {
      for (const row of matrix) { finiteVector(row); if (row.length !== matrix[0].length) throw new RangeError("矩阵维度不同"); }
    }
    if (Q[0].length !== K[0].length || !Number.isInteger(position) || position < 0 || position >= Q.length) throw new RangeError("无效位置或 Q/K 维度");
    const scores = K.slice(0, position + 1).map((key) => Q[position].reduce((sum, value, i) => sum + value * key[i], 0) / Math.sqrt(key.length));
    const visibleWeights = probabilities(scores, 1);
    const weights = K.map((_, i) => visibleWeights[i] ?? 0);
    const output = V[0].map((_, column) => V.reduce((sum, row, i) => sum + weights[i] * row[column], 0));
    return { scores: K.map((_, i) => scores[i] ?? null), weights, output };
  }

  function createTrainer(config) {
    if (!config || !Array.isArray(config.vocabulary) || !Number.isInteger(config.seed) || config.seed < 0 || config.seed > 4294967295) throw new RangeError("无效训练配置或种子");
    const size = config.vocabulary.length;
    const index = new Map(config.vocabulary.map((value, i) => [value, i]));
    const maxSteps = config.maxSteps;
    if (!size || index.size !== size || config.vocabulary.some(token => typeof token !== "string" || !token.length) || !Number.isInteger(maxSteps) || maxSteps < 1 || maxSteps > 500) throw new RangeError("无效训练配置");
    const pairs = (sequences) => {
      if (!Array.isArray(sequences)) throw new RangeError("语料必须是序列数组");
      return sequences.flatMap((sequence) => {
        if (!Array.isArray(sequence) || sequence.length < 2 || sequence.some((token) => !index.has(token))) throw new RangeError("词表不含语料中的片段或序列过短");
        return sequence.slice(0, -1).map((token, i) => [index.get(token), index.get(sequence[i + 1])]);
      });
    };
    const train = pairs(config.sequences);
    const heldOut = pairs(config.heldOut);
    if (!train.length || !heldOut.length) throw new RangeError("训练与验证都需要 token 对");
    const rng = random(config.seed);
    let logits = Array.from({ length: size }, () => Array.from({ length: size }, () => (rng() - 0.5) * 0.1));
    let steps = 0;
    let lastUpdate = null;
    const copy = (matrix) => matrix.map((row) => [...row]);
    const loss = (examples) => examples.reduce((total, [from, to]) => {
      const max = Math.max(...logits[from]);
      return total + Math.log(logits[from].reduce((sum, value) => sum + Math.exp(value - max), 0)) + max - logits[from][to];
    }, 0) / examples.length;
    const history = [{ step: 0, loss: loss(train), heldOut: loss(heldOut) }];
    return {
      snapshot() {
        return { steps, logits: copy(logits), loss: loss(train), heldOut: loss(heldOut), history: history.map((point) => ({ ...point })),
          lastUpdate: lastUpdate ? { before: copy(lastUpdate.before), gradient: copy(lastUpdate.gradient), learningRate: lastUpdate.learningRate } : null };
      },
      predict(token) {
        if (!index.has(token)) throw new RangeError("词表未覆盖这个输入");
        return probabilities(logits[index.get(token)], 1);
      },
      step(learningRate) {
        if (!Number.isFinite(learningRate) || learningRate < 0.01 || learningRate > 2) throw new RangeError("学习率必须在 0.01–2 之间");
        if (steps >= maxSteps) return false;
        const gradient = Array.from({ length: size }, () => Array(size).fill(0));
        for (const [from, to] of train) {
          const distribution = probabilities(logits[from], 1);
          distribution.forEach((value, column) => { gradient[from][column] += (value - Number(column === to)) / train.length; });
        }
        lastUpdate = { before: copy(logits), gradient, learningRate };
        logits = logits.map((row, i) => row.map((value, j) => value - learningRate * gradient[i][j]));
        steps++;
        history.push({ step: steps, loss: loss(train), heldOut: loss(heldOut) });
        return true;
      },
    };
  }

  const api = { probabilities, random, choose, candidates, createSession, sampleMany, auditClaims, visibleToken, cosine, attention, createTrainer };
  if (typeof module !== "undefined" && module.exports) module.exports = api;
  else globalThis.LLMLab = Object.freeze(api);
})();
