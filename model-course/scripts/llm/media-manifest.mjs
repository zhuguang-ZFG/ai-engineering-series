import { createHash } from "node:crypto";
import { readFileSync, writeFileSync, readdirSync } from "node:fs";
import { resolve, join, relative, extname } from "node:path";
import assert from "node:assert/strict";

const root = resolve(import.meta.dirname, "../..");
const digest = bytes => createHash("sha256").update(bytes).digest("hex");
const projects = [
  ["landscape", "vibe-coding-101-landscape.mp4"],
  ["vertical", "vibe-coding-101-vertical.mp4"],
  ["llm-principles", "llm-principles.mp4"],
  ["llm-applications", "llm-applications.mp4"]
];
function sourceHash(name) {
  const folder = join(root, "videos", name);
  const collect = dir => readdirSync(dir, { withFileTypes: true }).sort((a, b) => a.name < b.name ? -1 : 1).flatMap(entry => {
    if ([".hyperframes", ".thumbnails", "renders", "node_modules", "tools"].includes(entry.name)) return [];
    const path = join(dir, entry.name);
    if (entry.isDirectory()) return collect(path);
    return [".html", ".json", ".js", ".wav", ".mp3", ".png", ".jpg", ".svg", ".txt"].includes(extname(path)) ? [path] : [];
  });
  const hasher = createHash("sha256");
  for (const path of collect(folder)) {
    hasher.update(relative(folder, path).replaceAll("\\", "/"));
    const bytes = readFileSync(path);
    hasher.update([".html", ".json", ".js", ".svg", ".txt"].includes(extname(path)) ? bytes.toString("utf8").replaceAll("\r\n", "\n") : bytes);
  }
  return hasher.digest("hex");
}
const path = join(root, "media-status.json");
const records = projects.map(([project, filename]) => ({ project, delivery: "deliverables/" + filename, status: "rendered-and-reviewed", sourceHash: sourceHash(project), deliverySha256: digest(readFileSync(join(root, "deliverables", filename))), review: `videos/${project}/REVIEW.md` }));
if (process.argv.includes("--update")) {
  writeFileSync(path, JSON.stringify({ reviewedOn: "2026-11-07", drafts: [], deliveries: records }, null, 2) + "\n");
} else {
  const manifest = JSON.parse(readFileSync(path, "utf8"));
  assert.deepEqual(manifest.drafts, [], "Draft media remain unrendered");
  assert.deepEqual(manifest.deliveries, records, "Video source or delivery changed after review; rebuild and review the affected video");
  console.log("Four delivered videos match their reviewed source and file hashes");
}
