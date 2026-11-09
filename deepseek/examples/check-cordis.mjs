/** Run with Node + tsx; --source points to the pinned, unmodified Cordis source. */
import assert from "node:assert/strict";
import { pathToFileURL } from "node:url";
import { resolve } from "node:path";
import { reviewObserver, reviewWrapper } from "./review-observer.mjs";

const source = process.argv[process.argv.indexOf("--source") + 1];
if (!process.argv.includes("--source") || !source) throw new Error("Provide --source <pinned Cordis src/index.ts>");
const { Context, Service, FiberState } = await import(pathToFileURL(resolve(source)).href);
const cases = [];
async function check(name, test) {
  await test();
  cases.push({ name, passed: true });
  console.log(`PASS ${name}`);
}
class Counter extends Service {
  value = 0;
  constructor(ctx) { super(ctx, "bookCounter"); }
  next() { return ++this.value; }
}
await check("required injection waits, activates and cleans up", async () => {
  const root = new Context();
  const records = [];
  try {
    const observer = root.plugin(reviewObserver(x => records.push(x)));
    await observer.await();
    assert.equal(observer.state, FiberState.PENDING);
    assert.deepEqual(records, []);
    const provider = root.plugin(Counter);
    await provider.await();
    await observer.await();
    assert.equal(observer.state, FiberState.ACTIVE);
    root.emit("book/review", "a.ts");
    assert.deepEqual(records, ["observer:load", "resource:open", "review:1:a.ts"]);
    await observer.dispose();
    assert.equal(records.at(-1), "resource:closed");
    root.emit("book/review", "b.ts");
    assert.equal(records.length, 4);
  } finally { await root.fiber.dispose(); }
});
await check("provider removal deactivates dependent; replacement reactivates", async () => {
  const root = new Context();
  const records = [];
  try {
    const provider = root.plugin(Counter);
    await provider.await();
    const observer = root.plugin(reviewObserver(x => records.push(x)));
    await observer.await();
    root.emit("book/review", "first.ts");
    await provider.dispose();
    await observer.await();
    assert.equal(observer.state, FiberState.PENDING);
    assert.equal(records.at(-1), "resource:closed");
    const replacement = root.plugin(Counter);
    await replacement.await();
    await observer.await();
    root.emit("book/review", "second.ts");
    assert.equal(records.at(-1), "review:1:second.ts");
  } finally { await root.fiber.dispose(); }
});
await check("failed initialization rolls back managed effects, not raw writes", async () => {
  const root = new Context();
  const records = [];
  try {
    const broken = root.plugin(function broken(ctx) {
      records.push("unmanaged:written");
      ctx.effect(() => { records.push("managed:open"); return () => records.push("managed:closed"); });
      ctx.on("book/probe", () => records.push("unexpected:listener"));
      throw new Error("BOOK_INIT_FAILURE");
    });
    await assert.rejects(broken.await(), /BOOK_INIT_FAILURE/);
    assert.equal(broken.state, FiberState.FAILED);
    root.emit("book/probe");
    assert.deepEqual(records, ["unmanaged:written", "managed:open", "managed:closed"]);
    const healthy = root.plugin(ctx => ctx.on("book/probe", () => records.push("healthy")));
    await healthy.await();
    root.emit("book/probe");
    assert.equal(records.at(-1), "healthy");
  } finally { await root.fiber.dispose(); }
});
await check("waterfall preserves nested order and result", async () => {
  const root = new Context();
  const records = [];
  try {
    await root.plugin(reviewWrapper("A", x => records.push(x))).await();
    await root.plugin(reviewWrapper("B", x => records.push(x))).await();
    const result = await root.waterfall("book/dispatch", { file: "x.ts" }, () => {
      records.push("body"); return "read-result";
    });
    assert.equal(result, "read-result");
    assert.deepEqual(records, ["A:before:x.ts", "B:before:x.ts", "body", "B:after", "A:after"]);
  } finally { await root.fiber.dispose(); }
});
await check("waterfall veto skips body and duplicate next is rejected", async () => {
  const root = new Context();
  let executed = false;
  try {
    const veto = root.plugin(ctx => ctx.on("book/veto", () => "blocked"));
    await veto.await();
    assert.equal(root.waterfall("book/veto", () => { executed = true; }), "blocked");
    assert.equal(executed, false);
    await root.plugin(ctx => ctx.on("book/twice", (next) => { next(); return next(); })).await();
    assert.throws(() => root.waterfall("book/twice", () => 1), /multiple times/);
  } finally { await root.fiber.dispose(); }
});
await check("parent disposal awaits asynchronous child cleanup", async () => {
  const root = new Context();
  const records = [];
  try {
    let child;
    const parent = root.plugin(ctx => {
      child = ctx.plugin(childCtx => childCtx.effect(() => async () => {
        await Promise.resolve(); records.push("child:closed");
      }));
    });
    await parent.await();
    await child.await();
    await parent.dispose();
    assert.deepEqual(records, ["child:closed"]);
    await parent.dispose();
    assert.equal(records.length, 1);
  } finally { await root.fiber.dispose(); }
});
await check("isolated service realms keep counters separate", async () => {
  const root = new Context();
  try {
    const a = root.isolate("bookCounter");
    const b = root.isolate("bookCounter");
    await a.plugin(Counter).await();
    await b.plugin(Counter).await();
    assert.equal(a.bookCounter.next(), 1);
    assert.equal(a.bookCounter.next(), 2);
    assert.equal(b.bookCounter.next(), 1);
  } finally { await root.fiber.dispose(); }
});
console.log(JSON.stringify({ component: "Cordis", commit: "fcc0ad462172522aaf5c93a7b2e01f6b9f0b0159", cases, passed: true, model_used: false }));
