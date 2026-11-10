import { readFileSync, writeFileSync } from "node:fs";
import { join, resolve } from "node:path";
import assert from "node:assert/strict";
import { artDefs, artPaper } from "./figure-frame.mjs";

// Ten early figures are hand-authored rather than generated. This pass gives
// them the same paper, hairline and registration marks as the generated set,
// without touching their labels or geometry.
const root = resolve(import.meta.dirname, "../..");
const folder = join(root, "book/assets/handdraw/llm");
const checking = process.argv.includes("--check");
const files = [
  "token-pieces.svg",
  "generation-loop.svg",
  "context-workbench.svg",
  "embedding-view.svg",
  "attention-mask.svg",
  "training-versus-inference.svg",
  "assistant-training.svg",
  "multimodal-flow.svg",
  "protocol-boundaries.svg",
  "distillation-flow.svg"
];

for (const file of files) {
  const target = join(folder, file);
  let text = readFileSync(target, "utf8").replaceAll("\r\n", "\n");
  if (!text.includes("figure-grain")) {
    const size = /<svg[^>]*\bwidth="(\d+)"[^>]*\bheight="(\d+)"/.exec(text);
    assert.ok(size, `${file}: missing canvas size`);
    const [, width, height] = size;
    const background = new RegExp(`<rect width="${width}" height="${height}"(?: rx="\\d+")? fill="#fbfaf6"/>`);
    assert.ok(background.test(text), `${file}: missing paper background`);
    text = text.replace(background, artPaper(Number(width), Number(height)));
    text = text.replace("</desc>", `</desc>${artDefs()}`);
  }
  if (checking) assert.equal(readFileSync(target, "utf8").replaceAll("\r\n", "\n"), text, `${file} is stale`);
  else writeFileSync(target, text);
}
console.log(`${checking ? "Verified" : "Applied"} shared paper frame to ${files.length} authored figures`);
