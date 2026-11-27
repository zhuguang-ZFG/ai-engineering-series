import assert from "node:assert/strict";
import { readFileSync, writeFileSync } from "node:fs";
import { mechanismAssets } from "./mechanism-templates.mjs";
import { inkifySvg } from "./ink.mjs";
const checking = process.argv.includes("--check");
for (const { file, svg } of mechanismAssets) {
  const destination = new URL(`../../book/assets/handdraw/llm/${file}`, import.meta.url);
  const inked = inkifySvg(svg);
  if (checking) assert.equal(readFileSync(destination, "utf8").replaceAll("\r\n", "\n"), inked, `${file} is stale`);
  else writeFileSync(destination, inked);
}
console.log(`${checking ? "Verified" : "Built"} 3 computed hand-drawn storyboards (G49–G51)`);
