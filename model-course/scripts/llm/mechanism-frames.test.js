import test from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import frames from "./mechanism-frames.cjs";
const fixture = name => JSON.parse(readFileSync(new URL(`../../book/llm/fixtures/${name}.json`, import.meta.url), "utf8"));
const near = (actual, expected) => assert.ok(Math.abs(actual - expected) < 1e-12, `${actual} != ${expected}`);

test("generation drawings replay one sampled choice and recompute the next context", () => {
  const model = fixture("generation"), unchanged = structuredClone(model);
  const result = frames.generationFrames(model);
  assert.deepEqual(result, frames.generationFrames(model));
  assert.equal(result.selected.piece, "水");
  assert.equal(result.text, result.prompt + result.selected.piece);
  assert.deepEqual(result.next.map(item => item.piece), ["。", "，"]);
  near(result.before.reduce((sum, item) => sum + item.probability, 0), 1);
  near(result.next[0].probability, 1 / (1 + Math.exp(-1.6)));
  assert.notDeepEqual(result.before, frames.generationFrames(model, 42, 0).before);
  assert.deepEqual(model, unchanged);
});

test("attention drawing masks the future before normalizing and sums weighted values", () => {
  const model = fixture("attention"), result = frames.attentionFrames(model);
  assert.equal(result.position, 1);
  assert.deepEqual(result.scores.slice(2), [null, null]);
  assert.deepEqual(result.weights.slice(2), [0, 0]);
  near(result.weights[0], 1 / (1 + Math.exp((1.04 - 0.2) / Math.sqrt(2))));
  result.output.forEach((number, column) => near(number, result.contributions.reduce((sum, vector) => sum + vector[column], 0)));
  const changed = structuredClone(model);
  changed.V[2] = [999, -999]; changed.V[3] = [-888, 888];
  assert.deepEqual(frames.attentionFrames(changed).output, result.output);
});

test("distillation drawing changes only student logits and reports actual one-step loss", () => {
  const model = fixture("distillation"), unchanged = structuredClone(model);
  const result = frames.distillationFrames(model);
  result.logits.forEach((number, i) => near(number, model.student[i] - model.learningRate * result.before.gradient[i]));
  assert.ok(result.after.loss < result.before.loss);
  assert.deepEqual(result.before.teacher, result.after.teacher);
  assert.deepEqual(result.teacherLogits, model.teacher);
  assert.deepEqual(model, unchanged);
  const wrong = frames.distillationFrames({ ...model, teacher: model.wrongTeacher });
  assert.notDeepEqual(wrong.logits, result.logits);
  assert.ok(wrong.after.student[1] > wrong.before.student[1]);
});

test("storyboard contracts reject changed fixed examples before rendering stale equations", () => {
  for (const name of ["generation", "attention", "distillation"]) {
    assert.doesNotThrow(() => frames.assertStoryboardFixture(name, fixture(name)));
  }
  const mutations = [
    ["generation", model => model.states[model.prompt].reverse()],
    ["generation", model => { model.states[model.prompt][0].piece = "果汁"; }],
    ["generation", model => { model.states[model.prompt + "水"][0].logit = 3; }],
    ["attention", model => { model.Q[1][0] = 0.3; }],
    ["attention", model => { model.V[0][1] = 1; }],
    ["distillation", model => { model.temperature = 3; }],
    ["distillation", model => { model.alpha = 0.5; }],
    ["distillation", model => { model.learningRate = 0.2; }],
    ["distillation", model => { model.teacher = model.wrongTeacher; }],
    ["distillation", model => { model.student[0] = 1; }],
  ];
  for (const [name, mutate] of mutations) {
    const model = fixture(name);
    mutate(model);
    assert.throws(() => frames.assertStoryboardFixture(name, model), /storyboard fixture changed; review/);
  }
});
