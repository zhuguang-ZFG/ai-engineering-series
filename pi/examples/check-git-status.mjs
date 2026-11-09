// Real Git and Pi exec, a temporary repository, no model or user session.
// Usage: node pi/examples/check-git-status.mjs <Pi package directory>
import assert from "node:assert/strict";
import { spawnSync } from "node:child_process";
import { mkdtempSync, mkdirSync, readFileSync, rmSync, writeFileSync } from "node:fs";
import { createRequire } from "node:module";
import { tmpdir } from "node:os";
import { join, resolve } from "node:path";
import { pathToFileURL } from "node:url";

const corePath = process.argv[2];
if (!corePath) throw new Error("Usage: node check-git-status.mjs <Pi package directory>");
const root = mkdtempSync(join(tmpdir(), "pi-book-tool-"));
const repo = join(root, "repo");
mkdirSync(repo);
const hostRequire = createRequire(pathToFileURL(resolve(corePath, "package.json")));
const typeboxUrl = pathToFileURL(hostRequire.resolve("typebox")).href;
const { execCommand } = await import(pathToFileURL(resolve(corePath, "dist/core/exec.js")).href);
// Map the host-supplied TypeBox import for standalone Node, as Pi does on load.
const source = readFileSync(new URL("./git-status.ts", import.meta.url), "utf8")
    .replace('from "typebox"', `from ${JSON.stringify(typeboxUrl)}`);
const extensionPath = join(root, "git-status.ts");
writeFileSync(extensionPath, source);
const { default: extension } = await import(pathToFileURL(extensionPath).href);
let tool;
const registered = [];
extension({
    registerTool: (value) => { tool = value; registered.push(value.name); },
    exec: (command, args, options) => execCommand(command, args, repo, options),
});
assert.deepEqual(registered, ["book_git_status"]);
const git = (...args) => {
    const result = spawnSync("git", ["-C", repo, ...args], { encoding: "utf8" });
    assert.equal(result.status, 0, result.stderr);
};
const execute = (cwd = repo, signal = new AbortController().signal) =>
    tool.execute("fixture-call", {}, signal, undefined, { cwd });
let checks = 0;
const check = async (name, fn) => { await fn(); checks++; console.log(`ok ${checks} - ${name}`); };
try {
    git("init", "--quiet");
    writeFileSync(join(repo, "tracked.txt"), "before\n");
    git("add", "tracked.txt");
    git("-c", "user.name=Book Fixture", "-c", "user.email=fixture@example.invalid",
        "-c", "commit.gpgsign=false", "commit", "--quiet", "-m", "fixture");
    await check("clean tracked files have an explicitly limited description", async () => {
        assert.match((await execute()).content[0].text, /没有已跟踪文件的改动/);
    });
    await check("untracked files are not called tracked modifications", async () => {
        writeFileSync(join(repo, "untracked.txt"), "fixture\n");
        assert.match((await execute()).content[0].text, /未列出未跟踪文件/);
    });
    await check("modified tracked files reach model-facing content", async () => {
        writeFileSync(join(repo, "tracked.txt"), "after\n");
        assert.match((await execute()).content[0].text, /M tracked\.txt/);
    });
    await check("non-repository errors reject instead of returning clean status", async () => {
        await assert.rejects(execute(root), /退出码/);
    });
    await check("pre-aborted execution rejects", async () => {
        const controller = new AbortController();
        controller.abort();
        await assert.rejects(execute(repo, controller.signal), { name: "AbortError" });
    });
    await check("large status output is marked as truncated", async () => {
        for (let i = 0; i < 240; i++) {
            writeFileSync(join(repo, `fixture-long-name-${String(i).padStart(4, "0")}.txt`), "fixture\n");
        }
        git("add", ".");
        const result = await execute();
        assert.equal(result.details.truncated, true);
        assert.ok(result.content[0].text.endsWith("[输出已截断]"));
        assert.ok(result.content[0].text.length < 6100);
    });
    console.log(`PASS: ${checks} offline tool checks`);
} finally {
    // Only this script's mkdtempSync directory is removed.
    rmSync(root, { recursive: true, force: true });
}
