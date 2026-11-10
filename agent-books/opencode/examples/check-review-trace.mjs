import assert from "node:assert/strict";
import { test } from "node:test";
import { ReviewTrace } from "./review-trace.ts";

// Calls the real example, but provides a fake SDK client.
// Does not load OpenCode, start a server, call a model or enforce permissions.
async function fixture(log = async () => {}) {
  const hooks = await ReviewTrace({ client: { app: { log } } });
  return hooks;
}
const call = (sessionID = "s1", callID = "c1") => ({
  tool: "read", sessionID, callID,
});
const result = () => ({
  title: "read", output: "fixture content", metadata: { original: true },
});

test("appends one instruction and preserves the host's existing sections", async () => {
  const hooks = await fixture();
  const output = { system: ["HOST", "PROJECT"] };
  await hooks["experimental.chat.system.transform"]({}, output);
  await hooks["experimental.chat.system.transform"]({}, output);
  assert.deepEqual(output.system.slice(0, 2), ["HOST", "PROJECT"]);
  assert.equal(output.system.length, 3);
});

test("an async observer can log without changing tool arguments or text", async () => {
  const logs = [];
  const hooks = await fixture(async (entry) => { logs.push(entry); });
  const args = { filePath: "example.txt", sensitiveMarker: "DO_NOT_LOG" };
  const before = structuredClone(args);
  await hooks["tool.execute.before"](call(), { args });
  const output = result();
  await hooks["tool.execute.after"]({ ...call(), args }, output);
  assert.deepEqual(args, before);
  assert.equal(output.output, "fixture content");
  assert.equal(output.metadata.original, true);
  assert.equal(output.metadata.reviewTrace.correlated, true);
  assert.ok(output.metadata.reviewTrace.durationMs >= 0);
  assert.equal(logs.length, 1);
  assert.ok(!JSON.stringify(logs).includes("DO_NOT_LOG"));
  assert.ok(!JSON.stringify(logs).includes("fixture content"));
});

test("identical call IDs in different sessions do not consume each other's state", async () => {
  const hooks = await fixture();
  await Promise.all(["s1", "s2"].map((s) =>
    hooks["tool.execute.before"](call(s), { args: {} })));
  for (const session of ["s2", "s1"]) {
    const output = result();
    await hooks["tool.execute.after"]({ ...call(session), args: {} }, output);
    assert.equal(output.metadata.reviewTrace.correlated, true);
  }
  const duplicate = result();
  await hooks["tool.execute.after"]({ ...call(), args: {} }, duplicate);
  assert.deepEqual(duplicate.metadata.reviewTrace, { correlated: false, durationMs: null });
});

test("missing completion hooks cannot grow pending state without a bound", async () => {
  const hooks = await fixture();
  for (let i = 0; i < 129; i++) {
    await hooks["tool.execute.before"](call("s", String(i)), { args: {} });
  }
  const evicted = result();
  await hooks["tool.execute.after"]({ ...call("s", "0"), args: {} }, evicted);
  assert.equal(evicted.metadata.reviewTrace.correlated, false);
  const retained = result();
  await hooks["tool.execute.after"]({ ...call("s", "128"), args: {} }, retained);
  assert.equal(retained.metadata.reviewTrace.correlated, true);
});

test("a rejected log write preserves the already completed result", async () => {
  const hooks = await fixture(async () => { throw new Error("log unavailable"); });
  const output = result();
  await hooks["tool.execute.after"]({ ...call(), args: {} }, output);
  assert.equal(output.output, "fixture content");
  assert.equal(output.metadata.reviewTrace.correlated, false);
});

test("the pinned subtask failure shape can omit output without causing another failure", async () => {
  const logs = [];
  const hooks = await fixture(async (entry) => { logs.push(entry); });
  await hooks["tool.execute.before"](call(), { args: {} });
  await hooks["tool.execute.after"]({ ...call(), args: {} }, undefined);
  assert.equal(logs[0].body.level, "warn");
  assert.equal(logs[0].body.message, "Tool callback has no result");
  const late = result();
  await hooks["tool.execute.after"]({ ...call(), args: {} }, late);
  assert.equal(late.metadata.reviewTrace.correlated, false);
});

test("disposal stops all later observations and remains safe when repeated", async () => {
  const logs = [];
  const hooks = await fixture(async (entry) => { logs.push(entry); });
  await hooks["tool.execute.before"](call(), { args: {} });
  await hooks.dispose();
  await hooks.dispose();
  const system = { system: ["HOST"] };
  const output = result();
  await hooks["experimental.chat.system.transform"]({}, system);
  await hooks["tool.execute.before"](call(), { args: {} });
  await hooks["tool.execute.after"]({ ...call(), args: {} }, output);
  assert.deepEqual(system.system, ["HOST"]);
  assert.deepEqual(output.metadata, { original: true });
  assert.equal(logs.length, 0);
});

test("a teaching dispatcher demonstrates shared-output order and ignored return values", async () => {
  // Deliberately not the upstream dispatcher. Its semantics were read in
  // packages/opencode/src/plugin/index.ts at the locked commit.
  const dispatch = async (handlers, output) => {
    for (const handler of handlers) await handler({}, output);
    return output;
  };
  const output = { system: ["HOST"] };
  const hooks = await fixture();
  await dispatch([
    async () => ({ system: ["RETURNED_BUT_IGNORED"] }),
    hooks["experimental.chat.system.transform"],
    async (_input, state) => { state.system.push("SECOND_PLUGIN"); },
  ], output);
  assert.equal(output.system[0], "HOST");
  assert.equal(output.system[2], "SECOND_PLUGIN");
  assert.ok(!output.system.includes("RETURNED_BUT_IGNORED"));
});
