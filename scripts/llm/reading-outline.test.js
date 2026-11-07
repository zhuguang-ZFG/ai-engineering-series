import test from "node:test";
import assert from "node:assert/strict";
import { renderReading, readingContents } from "./reading-outline.mjs";

test("reading anchors survive earlier insertions and disambiguate repeated headings", () => {
  const original = renderReading("# 开始\n\n## 一个问题\n\n文字\n\n### 为什么？\n\n## 一个问题", "L02");
  const changed = renderReading("# 开始\n\n## 新增内容\n\n## 一个问题\n\n文字\n\n### 为什么？\n\n## 一个问题", "L02");
  assert.deepEqual(changed.outline.slice(1), original.outline);
  assert.equal(new Set(original.outline.map(item => item.id)).size, 3);
  assert.match(readingContents(original.outline), /toc-level-3/);
  for (const item of original.outline) assert.ok(original.html.includes(`id="${item.id}" tabindex="-1"`));
  assert.notEqual(renderReading("## 一个问题", "L03").outline[0].id, original.outline[0].id);
});

test("distillation keeps its published link while inline markup and code blocks retain meaning", () => {
  const result = renderReading("# 训练\n\n## 蒸馏：教师与学生\n\n### 比较 `q(T)` 与 **q(1)**\n\n```text\n## 不是标题\n```", "L05");
  assert.equal(result.outline.length, 2);
  assert.equal(result.outline[0].id, "distillation");
  assert.match(result.outline[1].content, /<code>q\(T\)<\/code>/);
  assert.match(result.html, /## 不是标题/);
});
