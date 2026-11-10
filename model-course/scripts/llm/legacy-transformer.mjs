import { readFileSync, writeFileSync } from "node:fs";
import { join } from "node:path";
import assert from "node:assert/strict";
import { multihead } from "../../book/llm/examples/multihead.mjs";
import { assembleLegacyApplications } from "./legacy-applications.mjs";

export function legacyTransformer(root, checking) {
  const read = path => readFileSync(join(root, path), "utf8");
  const path = "book/llm/legacy-transformer.md";
  const before = read(path).replaceAll("\r\n", "\n");
  const fixture = JSON.parse(read("book/llm/fixtures/multihead.json"));
  const result = multihead(fixture.input, fixture.heads, fixture.WO, fixture.position);
  const vector = values => `[${values.map(value => value.toFixed(6)).join(", ")}]`;
  const table = [
    `人工输入 \`X=${JSON.stringify(fixture.input)}\`，当前为第 ${fixture.position + 1} 个位置。各头投影矩阵见同源 fixture；本例两头 \`d_k=1\`，缩放因子为 1。`,
    "",
    "| 本地计算 | 第 1 头 | 第 2 头 |",
    "| --- | --- | --- |",
    `| 掩码后权重 | ${vector(result.heads[0].weights)} | ${vector(result.heads[1].weights)} |`,
    `| 加权 V 输出 | ${vector(result.heads[0].output)} | ${vector(result.heads[1].output)} |`,
    "",
    `拼接结果为 \`${vector(result.concatenated)}\`，经过人工输出矩阵后得到 \`${vector(result.output)}\`。表中数值由源码计算后保留六位小数。`, ""
  ].join("\n");
  const marker = /(?<=<!-- llm:multihead-result -->\n)[\s\S]*?(?=<!-- \/llm:multihead-result -->)/g;
  assert.equal([...before.matchAll(marker)].length, 1, "Missing multihead result marker");
  const markdown = before.replace(marker, table);
  if (checking) assert.equal(before, markdown, "Multihead results are stale; run npm run build:llm");
  else if (before !== markdown) writeFileSync(join(root, path), markdown);
  const expected = JSON.parse(read("book/llm/legacy-transformer-headings.json")).transformer;
  const bookPath = join(root, "book/book.md");
  const previous = readFileSync(bookPath, "utf8");
  const assembled = assembleLegacyApplications(previous, { transformer: markdown }, { transformer: expected });
  if (checking) assert.equal(previous, assembled, "Legacy transformer chapter is stale; run npm run build:llm");
  else if (previous !== assembled) writeFileSync(bookPath, assembled);
  const section = (title, replacement) => {
    const start = markdown.indexOf(title + "\n");
    assert.ok(start >= 0, `Missing transformer section ${title}`);
    const next = /^#{1,6} .+$/m.exec(markdown.slice(start + title.length + 1));
    return markdown.slice(start, next ? start + title.length + 1 + next.index : undefined).trim().replace(title, "## " + replacement);
  };
  const guide = [
    "# 结构回查：注意力怎样拼成一层",
    "先追踪几个向量怎样汇总，再看这一步怎样放进网络。以下来自同源 Transformer 修订章；数值是可复算的人工例子，不是实际模型内部读数。",
    section("###### 2.1 编码器（Encoder）", "注意力之外，还有什么？"),
    section("###### 2.2 注意力的计算过程", "先分清可见位置与目标"),
    section("###### 4.1 多头的工作机制", "各头汇总后，还要怎样混合？"),
    "在仓库根目录运行 `node book/llm/examples/multihead.mjs` 查看完整 Q/K/V、权重与输出；改变未来输入、当前可见输入或输出矩阵，再检查哪一步变化。",
    section("###### 5.3 现代变体：仅编码器 vs 仅解码器", "三条架构路线"),
    section("###### 6.3 现代位置编码方案", "位置怎样进入计算？"),
    section("###### 7.4 未来的挑战与方向", "精确计算与计算成本"),
    "## 自己检查一次",
    "1. 第二位置可见的输入能否包含未来第三位置？它在预测哪个位置？\n2. 把 W^O 换为单位矩阵，输出还会是两头的和与差吗？\n3. encoder-decoder 的交叉注意力，在 decoder-only 中也必然存在吗？\n4. 采用 FlashAttention 或 RoPE，能否推出任意长文本均能处理？",
    "核对依据：本例第二输入位置只看前两项，用来预测下一项；单位矩阵保留拼接值；decoder-only 省略编码器交叉注意力；内存优化与位置关系均不保证无限窗口或可靠外推。",
    "## 来源与范围",
    "原始结构、公式与 post-norm 见 [Transformer 论文](https://arxiv.org/html/1706.03762v7)；[RoFormer](https://arxiv.org/abs/2104.09864)和 [FlashAttention](https://arxiv.org/abs/2205.14135)按其论文范围解释。实际模型练习继续用 DeepSeek V4.1 Flash 与 Kimi K3，未采集内部状态、输出或性能。"
  ].join("\n\n") + "\n";
  return { markdown, guide };
}
