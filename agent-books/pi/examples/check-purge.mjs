// Offline checks for the book's pinned pi-purge case study. No model requests.
// Usage: node pi/examples/check-purge.mjs <pi-purge checkout> <Pi package directory>
import assert from "node:assert/strict";
import { mkdtempSync, readFileSync, readdirSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join, resolve } from "node:path";
import { pathToFileURL } from "node:url";

const [purgePath, corePath] = process.argv.slice(2);
if (!purgePath || !corePath) {
    throw new Error("Usage: node check-purge.mjs <pi-purge checkout> <Pi package directory>");
}
const version = (path) => JSON.parse(readFileSync(join(path, "package.json"), "utf8")).version;
assert.equal(version(purgePath), "0.2.1");
assert.equal(version(corePath), "1.5.0");
const fixtureDir = mkdtempSync(join(tmpdir(), "pi-book-purge-"));
const events = new Map();
const commands = new Map();
const notes = [];
const statuses = [];
const ctx = { ui: {
    notify: (text, level) => notes.push({ text, level }),
    setStatus: (key, text) => statuses.push({ key, text }),
} };
const load = (path) => import(pathToFileURL(resolve(path)).href);
const { default: extension } = await load(join(purgePath, "extensions/pi-purge.ts"));
const { buildSystemPrompt } = await load(join(corePath, "dist/core/system-prompt.js"));
extension({ on: (name, handler) => events.set(name, handler),
    registerCommand: (name, spec) => commands.set(name, spec) });
const command = (args) => commands.get("purge").handler(args, ctx);
const host = buildSystemPrompt({
    cwd: "C:/pi-book-fixture",
    selectedTools: ["read"],
    toolSnippets: { read: "Read a file" },
    contextFiles: [{ path: "C:/pi-book-fixture/AGENTS.md", content: "PROJECT_SENTINEL" }],
});
const run = (systemPrompt = host, cwd = "C:\\pi-book-fixture") =>
    events.get("before_agent_start")({ systemPrompt, systemPromptOptions: { cwd } }, ctx);
const lastNote = () => notes.at(-1).text;
let checks = 0;
const check = async (name, fn) => { await fn(); checks++; console.log(`ok ${checks} - ${name}`); };

try {
    const promptPath = join(fixtureDir, "review prompt.md");
    writeFileSync(promptPath, "REVIEW_FIXTURE", "utf8");
    const beforeFiles = readdirSync(fixtureDir);
    await events.get("session_start")({ reason: "startup" }, ctx);
    await check("disabled hook returns no replacement", async () => assert.equal(await run(), undefined));
    await command(`source "${promptPath}"`);
    await command("on");
    await check("strict keeps custom prompt and normalized cwd only", async () => {
        assert.equal((await run()).systemPrompt, "REVIEW_FIXTURE\n\nCurrent working directory: C:/pi-book-fixture");
    });
    await command("mode append");
    await check("append places custom text before the complete host prompt", async () => {
        assert.equal((await run()).systemPrompt, `REVIEW_FIXTURE\n\n${host}`);
    });
    await command("mode replace");
    await check("Pi 1.5.0 default wording does not match either old marker", async () => {
        assert.equal((await run()).systemPrompt, `REVIEW_FIXTURE\n\n${host}`);
        await command("status");
        assert.match(lastNote(), /身份段 未匹配 \/ pi 文档段 未匹配/);
    });
    const legacy = "You are an expert coding assistant operating inside pi, a coding agent harness. Tail.\n\n" +
        "Available tools:\n- read\n\n" +
        "Pi documentation (read only when the user asks about pi itself, its SDK):\n" +
        "- Always read docs (e.g., tui.md for TUI API details)\n\nPROJECT_SENTINEL";
    await check("legacy markers cut both blocks and preserve project text", async () => {
        const text = (await run(legacy)).systemPrompt;
        assert.ok(!text.includes("expert coding assistant"));
        assert.ok(!text.includes("Pi documentation"));
        assert.ok(text.includes("Available tools:"));
        assert.ok(text.includes("PROJECT_SENTINEL"));
    });
    await check("partial match cuts identity even when docs end marker is absent", async () => {
        const text = (await run(legacy.replace("(e.g., tui.md for TUI API details)", "changed"))).systemPrompt;
        assert.ok(!text.includes("expert coding assistant"));
        assert.ok(text.includes("Pi documentation"));
    });
    await check("invalid source restores the previous readable source", async () => {
        await command(`source ${join(fixtureDir, "missing.md")}`);
        assert.equal(notes.at(-1).level, "error");
        assert.ok((await run()).systemPrompt.startsWith("REVIEW_FIXTURE\n\n"));
    });
    await check("file edits need an explicit reload through source or on", async () => {
        writeFileSync(promptPath, "REVISED_FIXTURE", "utf8");
        assert.ok((await run()).systemPrompt.startsWith("REVIEW_FIXTURE\n\n"));
        await command("reload");
        assert.match(lastNote(), /未知子命令: reload/);
        await command("on");
        assert.ok((await run()).systemPrompt.startsWith("REVISED_FIXTURE\n\n"));
    });
    await check("append retains prior cut diagnostics rather than updating them", async () => {
        await run(legacy);
        await command("mode append");
        await run();
        await command("status");
        assert.match(lastNote(), /身份段 已切除 \/ pi 文档段 已切除/);
    });
    await check("strict without structured cwd returns only custom text", async () => {
        await command("mode strict");
        assert.equal((await run(host, null)).systemPrompt, "REVISED_FIXTURE");
    });
    await check("off and session_start disable future replacements", async () => {
        await command("off");
        assert.equal(await run(), undefined);
        await command("on");
        await events.get("session_start")({ reason: "resume" }, ctx);
        assert.equal(await run(), undefined);
        assert.equal(statuses.at(-1).text, undefined);
    });
    await check("extension creates no extra files in the fixture directory", async () => {
        assert.deepEqual(readdirSync(fixtureDir), beforeFiles);
    });
    console.log(`PASS: ${checks} offline checks; Pi ${version(corePath)}, pi-purge ${version(purgePath)}`);
} finally {
    // Only the directory returned by mkdtempSync above is removed.
    rmSync(fixtureDir, { recursive: true, force: true });
}
