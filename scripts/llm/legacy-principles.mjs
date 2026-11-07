import { readFileSync, writeFileSync } from "node:fs";
import { join } from "node:path";
import assert from "node:assert/strict";

export function legacyPrinciples(root, checking) {
  const read = path => readFileSync(join(root, path), "utf8");
  const fixture = JSON.parse(read("book/llm/fixtures/legacy-tokenization.json"));
  const visible = raw => {
    try { return JSON.stringify(new TextDecoder("utf-8", { fatal: true }).decode(Uint8Array.from(raw))).replaceAll("|", "\\|"); }
    catch { return "（部分 UTF-8 字节）"; }
  };
  const rows = fixture.encodings.cl100k_base.tokens.map(token => `| ${token.id} | ${token.bytes.map(byte => byte.toString(16).padStart(2, "0")).join(" ")} | ${visible(token.bytes)} |`);
  const table = ["```text", JSON.stringify(fixture.text), "```", "", "| token ID | UTF-8 字节（十六进制） | 可独立解码时的片段（JSON 转义） |", "| --- | --- | --- |", ...rows, ""].join("\n");
  const path = "book/llm/legacy-principles.md";
  const before = read(path);
  const marker = /(?<=<!-- llm:legacy-tokens -->\n)[\s\S]*?(?=<!-- \/llm:legacy-tokens -->)/g;
  assert.equal([...before.matchAll(marker)].length, 1);
  const markdown = before.replace(marker, table);
  if (checking) assert.equal(before, markdown, "Legacy token table is stale; run npm run build:llm");
  else if (before !== markdown) writeFileSync(join(root, path), markdown);
  const bookPath = join(root, "book/book.md");
  const book = readFileSync(bookPath, "utf8");
  const start = /^### 大语言模型的工作原理\r?$/m.exec(book)?.index ?? -1;
  const boundary = /\r?\n---\r?\n\r?\n### 提示词工程/.exec(book.slice(start));
  const end = boundary ? start + boundary.index : -1;
  assert.ok(start >= 0 && end > start, "Legacy chapter boundaries changed");
  const previous = book.slice(start, end);
  const headings = text => text.replaceAll("\r\n", "\n").match(/^#{3,6} .+$/gm);
  assert.deepEqual(headings(previous), headings(markdown), "Legacy heading text/order changed; preserve existing anchors");
  const newline = book.includes("\r\n") ? "\r\n" : "\n";
  const assembled = book.slice(0, start) + (markdown.trimEnd() + "\n").replaceAll("\n", newline) + book.slice(end);
  if (checking) assert.equal(book, assembled, "Assembled legacy chapter is stale; run npm run build:llm");
  else if (book !== assembled) writeFileSync(bookPath, assembled);
  // Keep the old graphic path working while removing the obsolete claims.
  const diagram = read("book/assets/handdraw/llm/generation-loop.svg");
  if (checking) assert.equal(read("book/assets/handdraw/llm-work.svg"), diagram, "Legacy diagram alias is stale");
  else if (read("book/assets/handdraw/llm-work.svg") !== diagram) writeFileSync(join(root, "book/assets/handdraw/llm-work.svg"), diagram);
  const section = title => {
    const start = markdown.indexOf(title + "\n");
    assert.ok(start >= 0, `Missing legacy section ${title}`);
    const end = markdown.indexOf("\n#", start + title.length + 1);
    return markdown.slice(start, end < 0 ? undefined : end).trim();
  };
  const advanced = [
    "# 进阶回查：缓存、专家与计算成本",
    "读完十二课后，遇到长上下文、专家路由或显存问题，可以回到这里。以下说明来自同一份旧章修订稿，固定网络规模和维度后再讨论长度项，不用于给实际模型排速度名次。",
    ...[
      ["###### 4.3 效率黑科技：KV 缓存 (KV Cache)", "KV 缓存存了什么？"],
      ["###### 7.5 架构进化：从“全能”到“专家团” (Dense vs MoE)", "MoE 专家由什么决定？"],
      ["###### 7.6 效率革命：突破长度极限 (Linear Attention)", "长度怎样影响计算成本？"],
      ["###### 一个是“网状”，一个是“线性”的原理", "逐位置缓存与递归状态"],
      ["###### 7.7 架构大比拼：RNN vs Transformer vs RWKV", "比较之前，先固定条件"]
    ].map(([title, short]) => section(title).replace(title, "## " + short)),
    "## 自己检查一次",
    "1. KV Cache 增长时，模型参数一定增长了吗？缓存以外还有哪些显存开销？\n2. 路由选中一个专家，能只凭 token 的字面含义为它命名吗？\n3. 为什么不能把输入预填充、带缓存的单步解码与模型全部计算都写成 N² 次？",
    "这里只补充计算与结构边界。产品是否支持某个模式、窗口或工具，仍按实际版本文档和任务测试判断。"
  ].join("\n\n") + "\n";
  return { markdown, advanced };
}
