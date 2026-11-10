import assert from "node:assert/strict";
import { pathToFileURL } from "node:url";
import { resolve } from "node:path";
const labIndex = process.argv.indexOf("--lab");
if (labIndex >= 0 && !process.argv[labIndex + 1]) throw new Error("Provide --lab <module.mjs>");
const labUrl = labIndex < 0 ? new URL("./review-lab.mjs", import.meta.url)
  : pathToFileURL(resolve(process.argv[labIndex + 1]));
const { createReviewLab, deferred, waitForAbort } = await import(labUrl.href);

const sourceIndex = process.argv.indexOf("--source");
if (sourceIndex < 0 || !process.argv[sourceIndex + 1]) throw new Error("Provide --source <Cordis index.ts>");
const cordis = await import(pathToFileURL(resolve(process.argv[sourceIndex + 1])).href);
const { Context, FiberState } = cordis;
const { ReviewJournal, ReviewTools, reviewPlugin, policy } = createReviewLab(cordis);
const cases = [];
async function check(name, body) {
  const ctx = new Context();
  try { await body(ctx); cases.push({ name, passed: true }); console.log(`PASS ${name}`); }
  finally { await ctx.fiber.dispose(); }
}
async function providers(ctx) {
  const journal = ctx.plugin(ReviewJournal);
  await journal.await();
  const tools = ctx.plugin(ReviewTools);
  await tools.await();
  return { journal, tools };
}
const kinds = journal => journal.snapshot().map(event => event.kind);

await check("one plugin waits for both services then owns its tool and listener", async ctx => {
  const plugin = ctx.plugin(reviewPlugin());
  await plugin.await();
  assert.equal(plugin.state, FiberState.PENDING);
  await ctx.plugin(ReviewJournal).await();
  await plugin.await();
  assert.equal(plugin.state, FiberState.PENDING);
  await ctx.plugin(ReviewTools).await();
  await plugin.await();
  assert.equal(plugin.state, FiberState.ACTIVE);
  assert.deepEqual(await ctx.bookTools.call("review_text", { text: "TODO\n校对" }),
    { lines: 2, characters: 7, todo: true });
  ctx.emit("book/note", "first");
  const journal = ctx.bookJournal;
  await plugin.dispose();
  await assert.rejects(ctx.bookTools.call("review_text", { text: "x" }), /TOOL_NOT_FOUND/);
  const count = journal.entries.length;
  ctx.emit("book/note", "late");
  assert.equal(journal.entries.length, count);
  assert.deepEqual(kinds(journal), ["plugin:load", "tool:start", "tool:result", "tool:settled",
    "note", "plugin:stop", "plugin:closed"]);
  if (process.argv.includes("--trace")) console.log(JSON.stringify({ trace: journal.snapshot() }));
});
await check("input validation rejects before the business body", async ctx => {
  await providers(ctx);
  await ctx.plugin(reviewPlugin()).await();
  await assert.rejects(ctx.bookTools.call("review_text", { text: 42 }), /TEXT_REQUIRED/);
  assert.deepEqual(kinds(ctx.bookJournal), ["plugin:load"]);
});
await check("policy veto blocks body and policy disposal restores the call", async ctx => {
  await providers(ctx);
  await ctx.plugin(reviewPlugin()).await();
  const records = [];
  const gate = ctx.plugin(policy({ reject: () => true, record: x => records.push(x) }));
  await gate.await();
  await assert.rejects(ctx.bookTools.call("review_text", { text: "x" }), /POLICY_DENIED/);
  assert.deepEqual(records, ["policy:before:1"]);
  assert.deepEqual(kinds(ctx.bookJournal), ["plugin:load"]);
  await gate.dispose();
  assert.equal((await ctx.bookTools.call("review_text", { text: "ok" })).characters, 2);
});
await check("initialization failure removes a tool already registered", async ctx => {
  await providers(ctx);
  const broken = ctx.plugin(reviewPlugin({ failAfterRegister: true }));
  await assert.rejects(broken.await(), /FAIL_AFTER_REGISTER/);
  assert.equal(broken.state, FiberState.FAILED);
  assert.equal(ctx.bookTools.definitions.size, 0);
  assert.deepEqual(kinds(ctx.bookJournal), ["plugin:load", "plugin:stop", "plugin:closed"]);
  ctx.emit("book/note", "late");
  assert.equal(ctx.bookJournal.entries.length, 3);
});
await check("unload cancels admitted work and awaits its delayed cleanup", async ctx => {
  await providers(ctx);
  const cleanupEntered = deferred();
  const allowCleanup = deferred();
  const plugin = ctx.plugin(reviewPlugin({ checkpoint: ({ signal }) => waitForAbort(signal),
    close: async () => { cleanupEntered.resolve(); await allowCleanup.promise; } }));
  await plugin.await();
  const call = ctx.bookTools.call("review_text", { text: "waiting" });
  const rejected = assert.rejects(call, /PLUGIN_UNLOADED/);
  let disposed = false;
  const stopping = plugin.dispose().then(() => { disposed = true; });
  await cleanupEntered.promise;
  assert.equal(disposed, false);
  assert.equal(ctx.bookTools.definitions.size, 0);
  assert.equal(kinds(ctx.bookJournal).includes("tool:result"), false);
  allowCleanup.resolve();
  await Promise.all([stopping, rejected]);
  assert.equal(disposed, true);
  assert.deepEqual(kinds(ctx.bookJournal).slice(-3), ["tool:error", "tool:settled", "plugin:closed"]);
});
await check("removing and replacing the tools provider reactivates the same plugin", async ctx => {
  const owners = await providers(ctx);
  const plugin = ctx.plugin(reviewPlugin());
  await plugin.await();
  const oldTools = ctx.bookTools;
  await owners.tools.dispose();
  await plugin.await();
  assert.equal(plugin.state, FiberState.PENDING);
  assert.equal(oldTools.definitions.size, 0);
  await ctx.plugin(ReviewTools).await();
  await plugin.await();
  assert.equal(plugin.state, FiberState.ACTIVE);
  assert.equal((await ctx.bookTools.call("review_text", { text: "new" })).characters, 3);
  assert.equal(kinds(ctx.bookJournal).filter(x => x === "plugin:load").length, 2);
});
await check("duplicate tool registration cannot remove the first owner's tool", async ctx => {
  await providers(ctx);
  const first = ctx.plugin(reviewPlugin());
  await first.await();
  const duplicate = ctx.plugin(reviewPlugin());
  await assert.rejects(duplicate.await(), /DUPLICATE_TOOL/);
  assert.equal(ctx.bookTools.definitions.size, 1);
  assert.equal((await ctx.bookTools.call("review_text", { text: "first" })).characters, 5);
});
await check("policy-delayed call cannot enter an unloaded owner", async ctx => {
  await providers(ctx);
  const plugin = ctx.plugin(reviewPlugin());
  await plugin.await();
  const entered = deferred();
  const release = deferred();
  await ctx.plugin(owner => {
    owner.on("book/execute", async (_request, next) => {
      entered.resolve();
      await release.promise;
      return next();
    });
  }).await();
  const call = ctx.bookTools.call("review_text", { text: "late" });
  const rejected = assert.rejects(call, /PLUGIN_UNLOADED/);
  await entered.promise;
  await plugin.dispose();
  release.resolve();
  await rejected;
  assert.deepEqual(kinds(ctx.bookJournal), ["plugin:load", "plugin:stop", "plugin:closed"]);
});
await check("same service isolation label intentionally shares a provider", async ctx => {
  const label = Symbol("shared-review");
  const left = ctx.isolate("bookJournal", label);
  const right = ctx.isolate("bookJournal", label);
  await left.plugin(ReviewJournal).await();
  left.bookJournal.append("left");
  right.bookJournal.append("right");
  assert.deepEqual(kinds(left.bookJournal), ["left", "right"]);
});
await check("once unregisters before recursive emission", async ctx => {
  let count = 0;
  ctx.once("book/once", () => { count++; ctx.emit("book/once"); });
  ctx.emit("book/once");
  assert.equal(count, 1);
});
await check("serial continues on false but stops on zero", async ctx => {
  const sequence = [];
  ctx.on("book/select", async () => { sequence.push("false"); return false; });
  ctx.on("book/select", async () => { sequence.push("zero"); return 0; });
  ctx.on("book/select", () => { sequence.push("unreachable"); return 7; });
  assert.equal(await ctx.serial("book/select"), 0);
  assert.deepEqual(sequence, ["false", "zero"]);
});
await check("parallel waits for all listeners and aggregates failures", async ctx => {
  const released = deferred();
  const entered = deferred();
  const failure = new Error("LISTENER_FAILED");
  let slowFinished = false;
  ctx.on("book/parallel", async () => { throw failure; });
  ctx.on("book/parallel", async () => { entered.resolve(); await released.promise; slowFinished = true; });
  let settled = false;
  const work = ctx.parallel("book/parallel").finally(() => { settled = true; });
  const observed = assert.rejects(work, error => error instanceof AggregateError && error.errors[0] === failure);
  await entered.promise;
  assert.equal(settled, false);
  released.resolve();
  await observed;
  assert.equal(slowFinished, true);
});
await check("unloaded context rejects new owned registrations", async ctx => {
  let owner;
  const plugin = ctx.plugin(context => { owner = context; });
  await plugin.await();
  await plugin.dispose();
  assert.throws(() => owner.on("book/late", () => {}), error => error.code === "INACTIVE_EFFECT");
});
console.log(JSON.stringify({ component: "Cordis with original book review services",
  commit: "fcc0ad462172522aaf5c93a7b2e01f6b9f0b0159", cases, passed: true,
  model_used: false, complete_dsh_host: false }));
