import test from "node:test";
import assert from "node:assert/strict";
import { mkdtempSync, mkdirSync, copyFileSync, writeFileSync, readFileSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { spawnSync } from "node:child_process";

test("media fingerprints ignore generated thumbnails but reject changed composition sources", () => {
  const fixture = mkdtempSync(join(tmpdir(), "llm-media-manifest-"));
  try {
    const script = join(fixture, "scripts/llm/media-manifest.mjs");
    mkdirSync(join(fixture, "scripts/llm"), { recursive: true });
    mkdirSync(join(fixture, "deliverables"));
    copyFileSync(new URL("./media-manifest.mjs", import.meta.url), script);
    for (const [project, file] of [
      ["landscape", "vibe-coding-101-landscape.mp4"],
      ["vertical", "vibe-coding-101-vertical.mp4"],
      ["llm-principles", "llm-principles.mp4"],
      ["llm-applications", "llm-applications.mp4"]
    ]) {
      mkdirSync(join(fixture, "videos", project, "compositions"), { recursive: true });
      writeFileSync(join(fixture, "videos", project, "compositions/scene.html"), "<p>source</p>\n");
      writeFileSync(join(fixture, "deliverables", file), "fixture delivery");
    }
    const run = (...args) => spawnSync(process.execPath, [script, ...args], { encoding: "utf8" });
    assert.equal(run("--update").status, 0);
    const manifest = readFileSync(join(fixture, "media-status.json"), "utf8");
    const project = join(fixture, "videos/llm-principles");
    mkdirSync(join(project, ".thumbnails"));
    writeFileSync(join(project, ".thumbnails/preview.jpg"), "generated thumbnail");
    assert.equal(run().status, 0, "Local thumbnail cache must not invalidate a reviewed source");
    assert.equal(run("--update").status, 0);
    assert.equal(readFileSync(join(fixture, "media-status.json"), "utf8"), manifest);
    writeFileSync(join(project, "compositions/scene.html"), "<p>source</p>\r\n");
    assert.equal(run().status, 0, "Platform line endings must not alter source hashes");
    writeFileSync(join(project, "compositions/scene.html"), "<p>changed source</p>\n");
    const changed = run();
    assert.notEqual(changed.status, 0);
    assert.match(changed.stderr, /Video source or delivery changed/);
  } finally {
    rmSync(fixture, { recursive: true, force: true });
  }
});
