import { readFileSync, writeFileSync } from "node:fs";
import { join } from "node:path";
import assert from "node:assert/strict";
import { assembleLegacyApplications } from "./legacy-applications.mjs";

export function legacyReferences(root, checking) {
  const read = path => readFileSync(join(root, path), "utf8");
  const chapters = Object.fromEntries(["multimodal", "embedding", "protocols"].map(name => [name, read(`book/llm/legacy-${name}.md`).replaceAll("\r\n", "\n")]));
  const bookPath = join(root, "book/book.md");
  const previous = readFileSync(bookPath, "utf8");
  const expected = JSON.parse(read("book/llm/legacy-reference-headings.json"));
  const assembled = assembleLegacyApplications(previous, chapters, expected);
  if (checking) assert.equal(previous, assembled, "Reference chapters are stale; run npm run build:llm");
  else if (previous !== assembled) writeFileSync(bookPath, assembled);
  return chapters;
}
