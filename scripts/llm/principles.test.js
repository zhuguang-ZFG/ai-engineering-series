import test from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import api from "./core.cjs";

const fixture = name => JSON.parse(readFileSync(new URL(`../../book/llm/fixtures/${name}.json`, import.meta.url), "utf8"));
const close = (actual, expected, tolerance = 1e-10) => assert.ok(Math.abs(actual - expected) < tolerance, `${actual} != ${expected}`);

test("cosine uses all dimensions, distinguishes projections, and leaves zero direction undefined", () => {
  const data = fixture("vectors");
  const a = data.contexts[0].representation;
  const b = data.references[2].vector;
  close(api.cosine(a, a), 1);
  close(api.cosine(a, a.map(v => -v)), -1);
  close(api.cosine(a.slice(0, 2), b.slice(0, 2)), 1);
  assert.ok(api.cosine(a, b) < 0.9);
  assert.equal(api.cosine(a, [0, 0, 0]), null);
  close(api.cosine([1e300, 1e300], [1e300, 1e300]), 1);
  close(api.cosine([Number.MAX_VALUE, Number.MAX_VALUE], [Number.MAX_VALUE, Number.MAX_VALUE]), 1);
  for (const [x, y] of [[[], []], [[1], [1, 2]], [[NaN], [1]], [[Infinity], [1]]]) assert.throws(() => api.cosine(x, y), RangeError);
});

test("causal attention masks all future positions and computes actual weighted V", () => {
  const { Q, K, V } = fixture("attention");
  for (let position = 0; position < Q.length; position++) {
    const result = api.attention(Q, K, V, position);
    close(result.weights.reduce((a, b) => a + b, 0), 1);
    assert.ok(result.weights.every(v => Number.isFinite(v) && v >= 0));
    for (let i = position + 1; i < Q.length; i++) { assert.equal(result.weights[i], 0); assert.equal(result.scores[i], null); }
    const changed = V.map((row, i) => row.map(v => i > position ? v + 100 : v));
    assert.deepEqual(api.attention(Q, K, changed, position), result);
    const keys = K.map((row, i) => row.map(v => i > position ? v - 80 : v));
    assert.deepEqual(api.attention(Q, keys, V, position), result);
  }
  assert.deepEqual(api.attention(Q, K, V, 0).output, V[0]);
  const r = api.attention(Q, K, V, 1);
  const expectedFirst = Math.exp(0.2 / Math.sqrt(2)) / (Math.exp(0.2 / Math.sqrt(2)) + Math.exp(1.04 / Math.sqrt(2)));
  close(r.weights[0], expectedFirst);
  close(r.output[0], expectedFirst);
  close(r.output[1], (1 - expectedFirst) * 2);
  assert.notDeepEqual(api.attention(Q, K, V.map((row, i) => i === 0 ? [10, 20] : row), 1).output, r.output);
});

test("attention rejects malformed matrices and out-of-range positions", () => {
  const { Q, K, V } = fixture("attention");
  for (const args of [[null, K, V, 0], [[], [], [], 0], [Q, K.slice(1), V, 0], [Q, [[1], ...K.slice(1)], V, 0], [Q, K, [[NaN, 0], ...V.slice(1)], 0], [Q, K, V, -1], [Q, K, V, 4], [Q, K, V, 0.5]]) assert.throws(() => api.attention(...args), RangeError);
});

test("training gradient matches independent finite differences and displayed update", () => {
  const data = fixture("training");
  const trainer = api.createTrainer(data);
  trainer.step(data.learningRate);
  const { logits, lastUpdate: { before, gradient, learningRate } } = trainer.snapshot();
  const index = token => data.vocabulary.indexOf(token);
  const examples = data.sequences.flatMap(s => s.slice(0, -1).map((token, i) => [index(token), index(s[i + 1])]));
  const objective = matrix => examples.reduce((sum, [from, to]) => sum - Math.log(api.probabilities(matrix[from], 1)[to]), 0) / examples.length;
  const epsilon = 1e-5;
  for (let i = 0; i < logits.length; i++) for (let j = 0; j < logits[i].length; j++) {
    const plus = structuredClone(before);
    const minus = structuredClone(before);
    plus[i][j] += epsilon; minus[i][j] -= epsilon;
    close(gradient[i][j], (objective(plus) - objective(minus)) / (2 * epsilon), 1e-8);
    close(logits[i][j], before[i][j] - learningRate * gradient[i][j]);
  }
});

test("training replays, reduces actual loss, and predictions leave parameters/history untouched", () => {
  const data = fixture("training");
  const original = JSON.stringify(data);
  const a = api.createTrainer(data);
  const b = api.createTrainer(data);
  const initial = a.snapshot();
  for (let i = 0; i < 100; i++) { a.step(0.8); b.step(0.8); }
  const state = a.snapshot();
  assert.ok(state.loss < initial.loss - 0.5);
  assert.deepEqual(state, b.snapshot());
  for (const token of data.vocabulary) { const p = a.predict(token); close(p.reduce((x, y) => x + y, 0), 1); }
  assert.deepEqual(a.snapshot(), state);
  assert.equal(state.history.length, 101);
  close(state.history.at(-1).loss, state.loss);
  close(state.history.at(-1).heldOut, state.heldOut);
  assert.equal(JSON.stringify(data), original);
  state.logits[0][0] = 1000; state.history[0].loss = 1000; state.lastUpdate.gradient[0][0] = 1000;
  assert.deepEqual(a.snapshot(), b.snapshot());
});

test("training caps steps and rejects bad rates/configuration without mutating state", () => {
  const data = fixture("training");
  const trainer = api.createTrainer({ ...data, maxSteps: 1 });
  const before = trainer.snapshot();
  for (const rate of [0, -1, 2.1, NaN, Infinity]) assert.throws(() => trainer.step(rate), RangeError);
  assert.deepEqual(trainer.snapshot(), before);
  assert.throws(() => trainer.predict("未知"), RangeError);
  assert.equal(trainer.step(0.8), true);
  const after = trainer.snapshot();
  assert.equal(trainer.step(0.8), false);
  assert.deepEqual(trainer.snapshot(), after);
  for (const config of [null, { ...data, seed: -1 }, { ...data, vocabulary: ["我", "我"] }, { ...data, maxSteps: 501 }, { ...data, heldOut: [] }, { ...data, sequences: [["我", "未知"]] }, { ...data, sequences: [["我"]] }]) assert.throws(() => api.createTrainer(config), RangeError);
});
