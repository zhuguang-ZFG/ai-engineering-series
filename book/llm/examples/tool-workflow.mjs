import { readFileSync } from "node:fs";
import { pathToFileURL } from "node:url";

const fixture = JSON.parse(readFileSync(new URL("../fixtures/tool-workflow.json", import.meta.url), "utf8"));

// This teaching executor performs local reads and arithmetic only.
export function executeTool(request, catalog = fixture.catalog) {
  const fail = error => ({ id: request?.id ?? null, status: "failed", result: null, error });
  const args = request?.arguments;
  if (!request || typeof request.id !== "string" || !request.id || !args || typeof args !== "object" || Array.isArray(args)) return fail("invalid-request");
  const sameKeys = keys => Object.keys(args).length === keys.length && keys.every(key => Object.hasOwn(args, key));
  let result;
  if (request.name === "lookup_price") {
    if (!sameKeys(["sku"]) || typeof args.sku !== "string" || args.sku.length > 80) return fail("invalid-sku");
    if (!Object.hasOwn(catalog, args.sku)) return fail("not-found");
    result = catalog[args.sku];
    if (!Number.isFinite(result) || result < 0) return fail("invalid-price");
  } else if (request.name === "multiply") {
    if (!sameKeys(["a", "b"]) || ![args.a, args.b].every(value => typeof value === "number" && Number.isFinite(value) && Math.abs(value) <= 1e6)) return fail("invalid-number");
    result = args.a * args.b;
  } else return fail("unknown-tool");
  return { id: request.id, status: "succeeded", result, error: null };
}

export function runPriceWorkflow(sku, quantity, options = {}) {
  const { catalog = fixture.catalog, maxCalls = 2, cancelAfterLookup = false, simulateTimeout = false } = options;
  const receipts = [];
  const stop = status => ({ status, total: null, receipts });
  if (typeof sku !== "string" || !Number.isInteger(quantity) || quantity < 1 || quantity > 10000) return stop("invalid-task");
  if (!Number.isInteger(maxCalls) || maxCalls < 0 || maxCalls > 2) return stop("invalid-budget");
  const call = request => {
    if (receipts.length >= maxCalls) return null;
    // Timeout here is a teaching branch; no asynchronous service is called.
    const receipt = simulateTimeout
      ? { id: request.id, status: "timeout", result: null, error: "simulated-timeout" }
      : executeTool(request, catalog);
    receipts.push({ request, receipt });
    return receipt;
  };
  const price = call({ id: "lookup-1", name: "lookup_price", arguments: { sku } });
  if (!price) return stop("budget-exhausted");
  if (price.status !== "succeeded") return stop(price.status);
  if (cancelAfterLookup) return stop("cancelled");
  // Feed the actual successful lookup result to the next tool.
  const total = call({ id: "multiply-1", name: "multiply", arguments: { a: price.result, b: quantity } });
  if (!total) return stop("budget-exhausted");
  if (total.status !== "succeeded") return stop(total.status);
  return { status: "done", total: total.result, receipts };
}

if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) {
  console.log(JSON.stringify(runPriceWorkflow(fixture.task.sku, fixture.task.quantity), null, 2));
  console.log(JSON.stringify(runPriceWorkflow("missing-item", 8), null, 2));
}
