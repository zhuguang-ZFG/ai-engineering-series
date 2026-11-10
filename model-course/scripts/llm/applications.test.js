import test from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import api from "./applications.cjs";
const fixture = name => JSON.parse(readFileSync(new URL(`../../book/llm/fixtures/${name}.json`, import.meta.url), "utf8"));

test("citation presence is checked independently of factual support and conflict", () => {
  const documents = fixture("materials").documents;
  const statuses = ["not-supporting", "not-supporting", "missing-quote", "missing-source", "not-supporting", "supporting"];
  fixture("evidence").cases.forEach((item, i) => {
    const result = api.checkCitation(documents.filter(doc => item.documents.includes(doc.id)), item.claim, item.citation);
    assert.equal(result.citationStatus, statuses[i]);
    if (item.id === "conflict") assert.equal(result.status, "conflict");
    if (item.id === "fake-source") assert.equal(result.status, "supported");
  });
});

test("retrieval only uses positive scored chunks, is repeatable, and changes with query/chunking", () => {
  const data = fixture("retrieval");
  const original = structuredClone(data);
  const a = api.retrieve(data, data.defaultQuery, 1, 3);
  assert.deepEqual(a.hits.map(hit => hit.id), ["R1-1", "R2-1", "R3-1"]);
  assert.ok(a.hits.every(hit => hit.score > 0));
  assert.deepEqual(api.retrieve(data, data.defaultQuery, 1, 3), a);
  assert.ok(!a.context.includes("咖啡角"));
  const report = api.summarize(a.hits, ["报名截止", "地点"]);
  assert.equal(report.fields[0].status, "conflict");
  assert.equal(report.fields[1].status, "missing");
  const larger = api.retrieve(data, data.defaultQuery, 3, 8);
  assert.ok(larger.hits.some(hit => hit.text.includes("活动地点为社区阅览室")));
  assert.ok(larger.hits.some(hit => hit.documentId === "R5"));
  assert.equal(api.summarize(larger.hits, ["地点"]).fields[0].values[0], "社区阅览室");
  for (const query of ["", " ！ ", "火星温度"]) { const result = api.retrieve(data, query); assert.equal(result.hits.length, 0); assert.equal(result.context, ""); }
  assert.deepEqual(data, original);
  for (const args of [[data, "x", 0, 1], [data, "x", 1, 0], [data, "x", 4, 2], [data, "x", 1, 9], [data, "x".repeat(201)]]) assert.throws(() => api.retrieve(...args), RangeError);
});

test("tool validates before executing, returns actual arithmetic, and never repeats a terminal execution", () => {
  const scenarios = fixture("tools").scenarios;
  const request = structuredClone(scenarios[0].request);
  const session = api.createToolSession(request);
  request.arguments.a = 900;
  assert.equal(session.snapshot().executions, 0);
  assert.equal(session.step().state, "validated");
  assert.equal(session.snapshot().executions, 0);
  assert.equal(session.step().state, "executed");
  assert.equal(session.snapshot().result, 100);
  assert.equal(session.step().state, "returned");
  assert.equal(session.step().state, "done");
  const final = session.snapshot();
  assert.equal(final.executions, 1);
  assert.deepEqual(session.step(), final);
  assert.deepEqual(session.cancel(), final);
  final.request.arguments.a = -1; final.history[0].message = "changed";
  assert.equal(session.snapshot().request.arguments.a, 12.5);
});

test("tool failure, cancellation, timeout and overflow preserve the absence of success", () => {
  for (const item of fixture("tools").scenarios.slice(1)) {
    const session = api.createToolSession(item.request, item.simulation);
    for (let i = 0; i < 8; i++) session.step();
    const state = session.snapshot();
    assert.equal(state.state, "failed"); assert.equal(state.result, null); assert.ok(state.executions <= 1);
  }
  for (const steps of [0, 1, 2, 3]) {
    const session = api.createToolSession(fixture("tools").scenarios[0].request);
    for (let i = 0; i < steps; i++) session.step();
    const state = session.cancel();
    assert.equal(state.state, "cancelled"); assert.equal(state.result, null);
    assert.deepEqual(session.step(), state);
    if (steps >= 2) assert.match(state.history.at(-1).message, /已经发生/);
  }
  const overflow = api.createToolSession({ tool: "calculator", arguments: { operation: "multiply", a: Number.MAX_VALUE, b: 2 } });
  overflow.step(); assert.equal(overflow.step().state, "failed");
  for (const input of [null, [], 3, "text", {}, { tool: "calculator", arguments: { operation: "constructor", a: 1, b: 2 } }]) assert.equal(api.createToolSession(input).step().state, "failed");
});

test("project cases preserve unknowns, conflicts, instructions and scope in exported reports", () => {
  const data = fixture("project");
  const expected = ["complete", "incomplete", "conflict", "no-evidence", "complete", "no-evidence", "out-of-scope"];
  data.cases.forEach((item, i) => {
    const docs = data.documents.filter(doc => item.documents.includes(doc.id));
    const report = api.summarize(docs, data.fields, item.outOfScope);
    assert.equal(report.status, expected[i]);
    const md = api.reportMarkdown(report);
    assert.ok(md.includes(report.note));
    if (item.id === "missing") { assert.equal(report.fields[2].status, "missing"); assert.match(md, /材料未提供/); }
    if (item.id === "injection") { assert.deepEqual(report.fields[2].values, ["邻里工坊"]); assert.ok(md.includes("忽略任务要求")); }
    if (item.id === "conflict") { assert.equal(report.fields[1].evidence.length, 2); assert.match(md, /周日10:00 \/ 周六10:00/); }
    for (const field of report.fields) for (const evidence of field.evidence) assert.ok(docs.find(doc => doc.id === evidence.documentId).text.includes(evidence.quote));
  });
});
