/* Numerical snapshots shared by the step drawings and their paper edition. */
const core = require("./core.cjs");
const distillation = require("./distillation.cjs");
const { isDeepStrictEqual } = require("node:util");

// The diagrams include worked equations and spatial arrangements for one fixed
// lesson example. A new fixture must trigger an editorial/layout review rather
// than silently combine fresh calculations with the old handwritten labels.
function assertStoryboardFixture(name, fixture) {
  const expected = {
    generation: {
      prompt: "他端起杯子，喝了一口",
      first: [{ piece: "水", logit: 2.4 }, { piece: "茶", logit: 1.8 }, { piece: "咖啡", logit: 0.9 }],
      next: [{ piece: "。", logit: 2 }, { piece: "，", logit: 0.4 }],
    },
    attention: {
      initialPosition: 1, tokens: ["我", "把", "苹果", "切开"],
      Q: [[1, 0], [0.2, 1], [1, 0.5], [0.5, 1]],
      K: [[1, 0], [0.2, 1], [0.8, 0.4], [1, 1]],
      V: [[1, 0], [0, 2], [2, 1], [4, 3]],
    },
    distillation: {
      labels: ["水", "茶", "咖啡"], teacher: [3, 2, 0], student: [0, 0, 0],
      target: 0, temperature: 2, alpha: 0.7, learningRate: 0.4,
    },
  }[name];
  if (!expected) throw new Error(`Unknown storyboard fixture: ${name}`);
  const actual = name === "generation" ? {
    prompt: fixture.prompt, first: fixture.states?.[fixture.prompt], next: fixture.states?.[fixture.prompt + "水"],
  } : Object.fromEntries(Object.keys(expected).map(key => [key, fixture[key]]));
  if (!isDeepStrictEqual(actual, expected)) throw new Error(`${name}: storyboard fixture changed; review its handwritten labels, equations, candidate order and prose before updating this contract`);
}

function generationFrames(fixture, seed = 42, temperature = 1) {
  const before = core.candidates(fixture, fixture.prompt, temperature);
  const session = core.createSession(fixture, seed);
  const after = session.step(temperature);
  const selected = after.history[0];
  if (!selected || after.stopped) throw new Error("The generation storyboard needs a nonterminal first step");
  const next = core.candidates(fixture, after.text, temperature);
  return { seed, temperature, prompt: fixture.prompt, before, selected, text: after.text, next };
}

function attentionFrames(fixture) {
  const position = fixture.initialPosition;
  const result = core.attention(fixture.Q, fixture.K, fixture.V, position);
  const contributions = fixture.V.map((value, i) => value.map(number => number * result.weights[i]));
  return { position, tokens: [...fixture.tokens], query: [...fixture.Q[position]], keys: fixture.K.map(row => [...row]), values: fixture.V.map(row => [...row]), ...result, contributions };
}

function distillationFrames(fixture) {
  const update = distillation.step(fixture.teacher, fixture.student, fixture.temperature, fixture.alpha, fixture.target, fixture.learningRate);
  return { labels: [...fixture.labels], teacherLogits: [...fixture.teacher], initialLogits: [...fixture.student], temperature: fixture.temperature, alpha: fixture.alpha, learningRate: fixture.learningRate, target: fixture.target, ...update };
}

module.exports = { assertStoryboardFixture, generationFrames, attentionFrames, distillationFrames };
