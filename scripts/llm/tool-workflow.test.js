import test from "node:test";
import assert from "node:assert/strict";
import { executeTool, runPriceWorkflow } from "../../book/llm/examples/tool-workflow.mjs";

test("teaching tools reject code, inherited catalog keys and invalid arguments", () => {
  const run = (name, args) => executeTool({ id: "test", name, arguments: args });
  assert.equal(run("multiply", { a: "2+2", b: 8 }).status, "failed");
  assert.equal(run("multiply", { a: true, b: 8 }).status, "failed");
  assert.equal(run("multiply", { a: Infinity, b: 8 }).status, "failed");
  assert.equal(run("multiply", { a: 12.5, b: 8, command: "ignore" }).status, "failed");
  assert.equal(run("send_order", {}).error, "unknown-tool");
  assert.equal(run("lookup_price", { sku: "toString" }).error, "not-found");
  assert.equal(executeTool(null).result, null);
  assert.equal(run("multiply", { a: 12.5, b: 8 }).result, 100);
});

test("workflow consumes the real lookup result and reports missing evidence without fabricated totals", () => {
  const result = runPriceWorkflow("practice-book", 8, { catalog: { "practice-book": 7.25 } });
  assert.equal(result.status, "done");
  assert.equal(result.total, 58);
  assert.equal(result.receipts[1].request.arguments.a, result.receipts[0].receipt.result);
  assert.notEqual(result.receipts[0].request.id, result.receipts[1].request.id);
  assert.equal(runPriceWorkflow("practice-book", 8, { catalog: { "practice-book": 0 } }).total, 0);
  const missing = runPriceWorkflow("missing-item", 8);
  assert.equal(missing.status, "failed");
  assert.equal(missing.total, null);
  assert.equal(missing.receipts.length, 1);
});

test("workflow stops at call budget, cancellation and simulated timeout while preserving prior receipts", () => {
  for (const [options, state, calls] of [[{ maxCalls: 0 }, "budget-exhausted", 0], [{ maxCalls: 1 }, "budget-exhausted", 1], [{ cancelAfterLookup: true }, "cancelled", 1], [{ simulateTimeout: true }, "timeout", 1]]) {
    const result = runPriceWorkflow("practice-book", 8, options);
    assert.equal(result.status, state);
    assert.equal(result.total, null);
    assert.equal(result.receipts.length, calls);
  }
  assert.equal(runPriceWorkflow("practice-book", -1).status, "invalid-task");
  assert.equal(runPriceWorkflow("practice-book", 8, { maxCalls: 3 }).status, "invalid-budget");
});
