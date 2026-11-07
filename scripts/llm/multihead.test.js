import test from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { multihead, multiply } from "../../book/llm/examples/multihead.mjs";

const fixture = JSON.parse(readFileSync(new URL("../../book/llm/fixtures/multihead.json", import.meta.url), "utf8"));
const run = (input = fixture.input, WO = fixture.WO, position = fixture.position) => multihead(input, fixture.heads, WO, position);
const close = (a, b) => assert.ok(Math.abs(a - b) < 1e-12, `${a} != ${b}`);

test("multihead projects inputs, concatenates head results and mixes them through WO", () => {
  const result = run();
  const logistic = Math.E / (1 + Math.E);
  assert.deepEqual(result.heads[0].Q, [[1], [0], [1]]);
  assert.deepEqual(result.heads[1].V, [[0], [1], [1]]);
  assert.deepEqual(result.heads[0].weights, [0.5, 0.5, 0]);
  close(result.heads[1].weights[1], logistic);
  close(result.concatenated[0], 0.5);
  close(result.concatenated[1], logistic);
  close(result.output[0], 0.5 + logistic);
  close(result.output[1], 0.5 - logistic);
  assert.deepEqual(run(fixture.input, [[1, 0], [0, 1]]).output, result.concatenated);
});

test("projected multihead preserves causal independence and does not mutate input", () => {
  const original = structuredClone(fixture);
  const changed = fixture.input.map((row, i) => i === 2 ? [999, -999] : [...row]);
  assert.deepEqual(run(changed).output, run().output);
  assert.deepEqual(run(changed).heads.map(head => head.weights), run().heads.map(head => head.weights));
  assert.notDeepEqual(run(changed, fixture.WO, 2).output, run(fixture.input, fixture.WO, 2).output);
  assert.notDeepEqual(run([[2, 0], [0, 1], [1, 1]]).output, run().output);
  assert.deepEqual(fixture, original);
  assert.throws(() => multiply([[1, 2]], [[1]]), /dimensions/);
  assert.throws(() => multiply([[Infinity]], [[1]]), /finite/);
  assert.throws(() => multiply([[1], [1, 2]], [[1]]), /rectangular/);
  assert.throws(() => run(fixture.input, [[1]], 1), /dimensions/);
  assert.throws(() => run(fixture.input, fixture.WO, 3), /位置/);
});
