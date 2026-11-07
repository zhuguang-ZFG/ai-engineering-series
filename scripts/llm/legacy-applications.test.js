import test from "node:test";
import assert from "node:assert/strict";
import { assembleLegacyApplications } from "./legacy-applications.mjs";

test("legacy assembly preserves intervening chapters, suffix and CRLF", () => {
  const book = "prefix\r\n### Prompt\r\n#### Intro\r\nold\r\n\r\n---\r\n\r\n### Between\r\nkeep this exactly\r\n\r\n---\r\n\r\n### RAG\r\n#### Flow\r\nold rag\r\n\r\n---\r\n\r\n### Next\r\nsuffix";
  const chapters = { prompt: "### Prompt\n#### Intro\nnew\n", rag: "### RAG\n#### Flow\nnew rag\n" };
  const expected = { prompt: ["### Prompt", "#### Intro"], rag: ["### RAG", "#### Flow"] };
  const result = assembleLegacyApplications(book, chapters, expected);
  assert.equal(result, book.replace("old\r\n", "new\r\n").replace("old rag\r\n", "new rag\r\n"));
  assert.equal(assembleLegacyApplications(result, chapters, expected), result);
  assert.throws(() => assembleLegacyApplications(book, { ...chapters, rag: "### RAG\n#### Renamed\nnew\n" }, expected), /anchors changed/);
  assert.throws(() => assembleLegacyApplications(book.replace("#### Intro", "#### Changed"), chapters, expected), /anchors changed/);
  assert.throws(() => assembleLegacyApplications(book + "\r\n### Prompt\r\n", chapters, expected), /exactly one/);
  assert.throws(() => assembleLegacyApplications(book.replace("\r\n---\r\n\r\n### Next", "\r\n### Next"), chapters, expected), /end boundary/);
});
