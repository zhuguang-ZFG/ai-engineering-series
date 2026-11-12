import { readFileSync, writeFileSync } from "node:fs";
import { join, resolve } from "node:path";
import assert from "node:assert/strict";

// Ten early figures are hand-authored rather than generated. Figures sit
// directly on the page paper (ink, no plate), so this pass removes the
// generator-era plate — paper fill, grain, hairline frame and corner marks —
// without touching labels or geometry.
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

const platePart = (width, height) => [
  new RegExp(`<rect width="${width}" height="${height}"(?: rx="\\d+")? fill="#fbfaf6"/>`),
  new RegExp(`<rect width="${width}" height="${height}" fill="url\\(#figure-grain\\)" opacity="\\.34"/>`),
  new RegExp(`<rect x="9" y="9" width="${width - 18}" height="${height - 18}" fill="none" stroke="#1f2328" stroke-width="\\.8" opacity="\\.22"/>`),
  new RegExp(`<path d="M9 30 V9 H30 M${width - 30} 9 H${width - 9} V30 M9 ${height - 30} V${height - 9} H30 M${width - 30} ${height - 9} H${width - 9} V${height - 30}" fill="none" stroke="#1f2328" stroke-width="1\\.2" opacity="\\.38"/>`),
  /<defs><pattern id="figure-grain" width="18" height="18" patternUnits="userSpaceOnUse"><circle cx="2" cy="3" r="\.7" fill="#1f2328" opacity="\.16"\/><circle cx="12" cy="13" r="\.55" fill="#1f2328" opacity="\.11"\/><\/pattern><\/defs>/,
];

for (const file of files) {
  const target = join(folder, file);
  const source = readFileSync(target, "utf8").replaceAll("\r\n", "\n");
  let text = source;
  const size = /<svg[^>]*\bwidth="(\d+)"[^>]*\bheight="(\d+)"/.exec(text);
  assert.ok(size, `${file}: missing canvas size`);
  const [, width, height] = size;
  const parts = platePart(Number(width), Number(height));
  const hadPlate = parts.some((p) => p.test(text));
  for (const part of parts) text = text.replace(part, "");
  assert.ok(!hadPlate || text !== source, `${file}: plate not stripped`);
  assert.ok(!text.includes("figure-grain"), `${file}: plate grain remains`);
  if (checking) assert.equal(source, text, `${file} is stale`);
  else if (text !== source) writeFileSync(target, text);
}
console.log(`${checking ? "Verified" : "Stripped"} plate from ${files.length} authored figures`);
