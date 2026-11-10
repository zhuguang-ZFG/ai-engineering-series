import test from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import api from "./core.cjs";

const fixture = (name) => JSON.parse(readFileSync(new URL(`../../book/llm/fixtures/${name}.json`, import.meta.url), "utf8"));
const model = fixture("generation");
const materials = fixture("materials");

test("softmax stays normalized and finite for extreme scores and small temperatures", () => {
  for (const scores of [[10000, 9999, -10000], [Number.MAX_VALUE, -Number.MAX_VALUE], [0, 0, 0]]) {
    for (const temperature of [Number.MIN_VALUE, 0.1, 1, 2]) {
      const p = api.probabilities(scores, temperature);
      assert.ok(p.every((value) => Number.isFinite(value) && value >= 0 && value <= 1));
      assert.ok(Math.abs(p.reduce((a, b) => a + b, 0) - 1) < 1e-10);
    }
  }
});

test("temperature flattens the distribution; zero chooses the first maximum", () => {
  const scores = [2.4, 1.8, 0.9];
  assert.ok(api.probabilities(scores, 0.1)[0] > api.probabilities(scores, 2)[0]);
  assert.ok(api.probabilities(scores, 0.1)[2] < api.probabilities(scores, 2)[2]);
  assert.deepEqual(api.probabilities([2, 2, 1], 0), [1, 0, 0]);
  for (const value of [-1, Infinity, NaN, 2.1]) assert.throws(() => api.probabilities(scores, value), RangeError);
  for (const value of [[], [NaN], [Infinity]]) assert.throws(() => api.probabilities(value, 1), RangeError);
});

test("sampling excludes zero-probability candidates at interval boundaries", () => {
  assert.equal(api.choose([0, 1, 0], () => 0), 1);
  assert.equal(api.choose([0.5, 0.5], () => 0.5), 1);
  for (const value of [-0.1, 1, NaN]) assert.throws(() => api.choose([1], () => value), RangeError);
});

test("generation appends a piece and changes the next candidates, then stops without leaking EOS", () => {
  const original = JSON.stringify(model);
  const session = api.createSession(model);
  assert.deepEqual(api.candidates(model, session.snapshot().text, 0).map((item) => item.piece), ["水", "茶", "咖啡"]);
  session.step(0);
  assert.equal(session.snapshot().text, model.prompt + "水");
  assert.deepEqual(api.candidates(model, session.snapshot().text, 0).map((item) => item.piece), ["。", "，"]);
  session.step(0);
  const final = session.step(0);
  assert.equal(final.stopped, true);
  assert.equal(final.steps, 3);
  assert.equal(final.text, model.prompt + "水。");
  assert.equal(final.text.includes(model.stopToken), false);
  assert.deepEqual(session.step(2), final);
  const copy = session.snapshot();
  copy.history[0].piece = "mutation";
  assert.notEqual(session.snapshot().history[0].piece, "mutation");
  assert.equal(JSON.stringify(model), original);
});

test("unknown contexts and length caps stop explicitly, including inherited property names", () => {
  for (const prompt of ["unknown", "constructor", "toString"]) {
    const session = api.createSession({ ...model, prompt });
    assert.match(session.step(1).reason, /未覆盖/);
    assert.equal(session.snapshot().steps, 0);
  }
  const session = api.createSession({ ...model, maxSteps: 1 });
  assert.match(session.step(0).reason, /上限/);
  assert.equal(session.step(1).steps, 1);
});

test("all supported branches terminate and fresh sessions replay fixed seeds", () => {
  for (let seed = 0; seed < 100; seed++) {
    const a = api.createSession(model, seed);
    const b = api.createSession(model, seed);
    for (let i = 0; i < model.maxSteps + 1; i++) {
      assert.deepEqual(a.step(1.7), b.step(1.7));
    }
    assert.equal(a.snapshot().stopped, true);
    assert.equal(a.snapshot().text.includes(model.stopToken), false);
  }
  for (const seed of [-1, 0.5, 4294967296, NaN]) assert.throws(() => api.createSession(model, seed), RangeError);
});

test("100-draw comparisons replay and do not advance a running generation", () => {
  const session = api.createSession(model, 42);
  const before = session.snapshot();
  const result = api.sampleMany(model, before.text, 1, 42);
  assert.equal(result.reduce((sum, item) => sum + item.count, 0), 100);
  assert.deepEqual(api.sampleMany(model, before.text, 1, 42), result);
  assert.deepEqual(session.snapshot(), before);
  assert.deepEqual(api.sampleMany(model, before.text, 0, 9).map((item) => item.count), [100, 0, 0]);
  assert.equal(api.sampleMany(model, "unknown", 1), null);
  assert.throws(() => api.sampleMany(model, before.text, 1, 42, 1001), RangeError);
});

test("evidence distinguishes missing, unsupported, supported and conflicting claims", () => {
  const { documents: [a, b, c], claims } = materials;
  assert.deepEqual(api.auditClaims([], claims).map((item) => item.status), ["missing", "missing", "missing", "missing"]);
  assert.deepEqual(api.auditClaims([a], claims).map((item) => item.status), ["supported", "supported", "missing", "supported"]);
  assert.equal(api.auditClaims([a, b], claims)[2].status, "unsupported");
  assert.equal(api.auditClaims([a, b], [{ field: "地点", value: "社区阅览室" }])[0].status, "supported");
  assert.equal(api.auditClaims([a, c], claims)[1].status, "conflict");
  assert.equal(api.auditClaims([c, a], claims)[1].status, "conflict");
  for (const result of api.auditClaims([a, b, c], claims)) {
    for (const evidence of result.evidence) {
      const doc = materials.documents.find((item) => item.id === evidence.documentId);
      assert.ok(doc.text.includes(evidence.quote));
    }
  }
});

test("token snapshots preserve raw UTF-8 bytes, including incomplete character fragments", () => {
  const data = fixture("tokens");
  let partial = false;
  let changed = false;
  for (const encoding of Object.values(data.encodings)) {
    for (const example of encoding.examples) {
      const bytes = Buffer.from(example.tokens.flatMap((token) => token.bytes));
      assert.deepEqual(bytes, Buffer.from(example.text, "utf8"));
      assert.equal(example.codePoints, [...example.text].length);
      assert.equal(example.utf8Bytes, bytes.length);
      partial ||= example.tokens.some((token) => token.label === "〈字节片段〉");
      const compare = data.encodings.o200k_base.examples.find((item) => item.id === example.id);
      changed ||= compare.tokens.length !== example.tokens.length;
    }
  }
  assert.equal(partial, true);
  assert.equal(changed, true);
  assert.equal(api.visibleToken("\u200d"), "〈连接符〉");
  assert.equal(api.visibleToken("\u0301"), "◌\u0301");
  assert.equal(api.visibleToken(" e\n"), "␠e↵");
});
