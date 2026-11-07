import { readFileSync, existsSync } from "node:fs";
import { resolve, join } from "node:path";
import assert from "node:assert/strict";
import api from "./core.cjs";
import distill from "./distillation.cjs";

export function validateData(root = resolve(import.meta.dirname, "../.."), { allowPendingOutputs = false } = {}) {
  const folder = join(root, "book/llm");
  const json = (file) => JSON.parse(readFileSync(join(folder, file), "utf8"));
  const course = json("course.json");
  const sources = json("sources.json").sources;
  const known = new Set(sources.map((item) => item.id));
  assert.equal(known.size, sources.length, "Duplicate source IDs");
  for (const source of sources) {
    for (const key of ["id", "title", "checkedOn", "method", "scope", "claims"]) assert.ok(source[key]?.length, `${source.id}: missing ${key}`);
  }
  const ids = new Set();
  const slugs = new Set();
  const ready = course.lessons.filter((lesson) => lesson.status === "ready");
  for (const lesson of course.lessons) {
    assert.ok(!ids.has(lesson.id), `Duplicate lesson ${lesson.id}`);
    ids.add(lesson.id);
    assert.ok(["ready", "planned"].includes(lesson.status));
    if (lesson.status !== "ready") continue;
    for (const key of ["slug", "title", "shortTitle", "file", "experiment", "figure", "sources", "objective", "question", "options", "feedback"]) assert.ok(lesson[key]?.length, `${lesson.id}: missing ${key}`);
    assert.match(lesson.slug, /^[a-z][a-z-]+$/);
    assert.ok(!slugs.has(lesson.slug), "Duplicate slug");
    slugs.add(lesson.slug);
    assert.ok(Number.isInteger(lesson.correct) && lesson.correct >= 0 && lesson.correct < lesson.options.length);
    assert.ok(lesson.sources.every((id) => known.has(id)), `${lesson.id}: unknown source`);
    assert.match(lesson.file, /^[a-z-]+\.md$/);
    assert.match(lesson.figure, /^[a-z-]+\.svg$/);
    assert.ok(existsSync(join(folder, "lessons", lesson.file)));
    assert.ok(existsSync(join(folder, "deepening", lesson.file)), `${lesson.id}: missing worked explanation`);
    assert.ok(existsSync(join(root, "book/assets/handdraw/llm", lesson.figure)));
    for (const id of lesson.prerequisites) assert.ok(ready.some((item) => item.id === id), `Unavailable prerequisite ${id}`);
  }
  assert.equal(ids.size, 12, "Expected 12 planned lessons");
  const experiments = new Set();
  for (const [file, id, kind] of [["tokens", "X01", "recorded"], ["generation", "X02", "toy"], ["materials", "X06", "illustrative"], ["vectors", "X03", "illustrative"], ["attention", "X04", "toy"], ["training", "X05", "toy"], ["assistant", "D06", "illustrative"], ["evidence", "X06B", "illustrative"], ["retrieval", "X07", "toy"], ["tools", "X08", "toy"], ["approaches", "D11", "illustrative"], ["project", "D12", "illustrative"], ["distillation", "X09", "toy"]]) {
    const data = json(`fixtures/${file}.json`);
    assert.equal(data.id, id);
    assert.equal(data.kind, kind);
    experiments.add(id);
    for (const key of ["source", "version", "limitations", "expectedObservations"]) assert.ok(data[key]?.length, `${id}: missing ${key}`);
  }
  for (const lesson of ready) for (const experiment of [lesson.experiment, ...(lesson.extraExperiments ?? [])]) assert.ok(experiments.has(experiment), `Unavailable experiment ${lesson.id}`);
  const kd = json("fixtures/distillation.json");
  assert.equal(kd.labels.length, kd.teacher.length);
  assert.doesNotThrow(() => distill.step(kd.teacher, kd.student, kd.temperature, kd.alpha, kd.target, kd.learningRate));
  assert.ok(course.quickRoute.every(id => ready.some(lesson => lesson.id === id)), "Unavailable quick route");
  const vectors = json("fixtures/vectors.json");
  for (const item of [...vectors.contexts.map(c => c.representation), ...vectors.references.map(r => r.vector)]) assert.doesNotThrow(() => api.cosine(vectors.token.initial, item));
  const attention = json("fixtures/attention.json");
  attention.tokens.forEach((_, i) => assert.doesNotThrow(() => api.attention(attention.Q, attention.K, attention.V, i)));
  const training = json("fixtures/training.json");
  assert.doesNotThrow(() => api.createTrainer(training).step(training.learningRate));
  const models = json("models.json");
  assert.match(models.checkedOn, /^\d{4}-\d{2}-\d{2}$/);
  assert.equal(models.status, "official-reference-only");
  assert.ok(models.task.length && models.limitations.length && models.recordFields.length);
  for (const model of models.models) assert.ok(model.name.length && known.has(model.source) && model.url.startsWith("https://"));
  const material = json("fixtures/materials.json");
  for (const doc of [...material.documents, ...json("fixtures/project.json").documents]) {
    for (const fact of doc.facts) assert.ok(doc.text.includes(fact.quote), `${doc.id}: quote not in original`);
  }
  for (const doc of json("fixtures/retrieval.json").documents) for (const sentence of doc.sentences) for (const fact of sentence.facts) assert.ok(sentence.text.includes(fact.quote), `${doc.id}: quote not in sentence`);
  const model = json("fixtures/generation.json");
  for (const [context, choices] of Object.entries(model.states)) {
    assert.ok(choices.length && choices.every((item) => Number.isFinite(item.logit)));
    for (const choice of choices) {
      if (choice.piece !== model.stopToken) assert.ok(Object.hasOwn(model.states, context + choice.piece), `Uncovered branch after ${context}`);
    }
  }
  const review = json("review/tasks.json");
  const legacyTokens = json("fixtures/legacy-tokenization.json");
  assert.equal(legacyTokens.kind, "recorded");
  for (const encoding of Object.values(legacyTokens.encodings)) {
    assert.equal(Buffer.from(encoding.tokens.flatMap(token => token.bytes)).toString("utf8"), legacyTokens.text);
    assert.ok(encoding.rankSha256.length === 64);
  }
  const canonicalLegacy = ["principles", "transformer", "prompt", "rag", "context", "agent", "multimodal", "embedding", "protocols"].map(name => readFileSync(join(folder, `legacy-${name}.md`), "utf8")).join("\n");
  const pendingPages = new Set([
    ...ready.map(lesson => lesson.slug), "index", "principles-reference", "transformer-reference", "architecture-guide", "advanced", "prompt-reference", "rag-reference",
    "applications-guide", "context-reference", "agent-reference", "execution-guide", "multimodal-reference", "embedding-reference", "protocols-reference", "deck", "cards", "check-understanding", "review-guide"
  ].map(name => `../exports/llm/${name}.html`));
  for (const match of canonicalLegacy.matchAll(/(?:href|src)="([^"]+)"|\]\(([^)]+)\)/g)) {
    const target = match[1] ?? match[2];
    if (target.startsWith("https://")) continue;
    assert.ok(existsSync(resolve(root, "book", target)) || (allowPendingOutputs && pendingPages.has(target)), `Legacy chapter missing local reference: ${target}`);
  }
  const rubric = json("review/rubric.json");
  assert.equal(review.kind, "illustrative");
  assert.equal(rubric.status, "unrun", "Actual reading results belong in local-feedback, not the rubric");
  assert.equal(review.version, rubric.version);
  assert.equal(review.tasks.length, 6);
  assert.equal(new Set(review.tasks.map(task => task.id)).size, 6);
  assert.equal(new Set(rubric.criteria.map(item => item.task)).size, 6);
  assert.deepEqual(new Set(review.tasks.map(task => task.objective)), new Set(["O1", "O2", "O3", "O4", "O5"]));
  for (const task of review.tasks) {
    assert.match(task.id, /^R0[1-6]$/);
    assert.ok(task.questions.length && task.material.length && task.answerLabel.length);
    assert.ok(Number.isInteger(task.lines) && task.lines >= 4 && task.lines <= 12);
    assert.ok(task.lessons.every(id => ids.has(id)));
    assert.ok((task.documents ?? []).every(id => review.documents.some(doc => doc.id === id)));
    assert.ok(rubric.criteria.some(item => item.task === task.id && item.mustInclude.length && item.example && item.hint));
  }
  for (const item of rubric.criteria) for (const evidence of item.evidence ?? []) {
    const doc = review.documents.find(doc => doc.id === evidence.document);
    assert.ok(doc?.text.includes(evidence.quote), `${item.task}: review quote not in source`);
  }
  return { course, ready };
}
