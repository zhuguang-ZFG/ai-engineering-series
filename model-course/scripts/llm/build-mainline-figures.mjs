import { readFileSync, writeFileSync } from "node:fs";
import { join, resolve } from "node:path";
import assert from "node:assert/strict";
import { mainlineArtworks } from "./mainline-art.mjs";

const checking = process.argv.includes("--check");
const folder = resolve(import.meta.dirname, "../../book/assets/handdraw/llm");
for (const [file, svg] of mainlineArtworks) {
  const target = join(folder, file);
  if (checking) assert.equal(readFileSync(target, "utf8").replaceAll("\r\n", "\n"), svg, `${file} is stale`);
  else writeFileSync(target, svg);
}
console.log(`${checking ? "Verified" : "Built"} ${mainlineArtworks.length} running-example figures`);
