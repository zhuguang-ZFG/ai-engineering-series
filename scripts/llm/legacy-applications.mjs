import { readFileSync, writeFileSync } from "node:fs";
import { join } from "node:path";
import assert from "node:assert/strict";
import { runPriceWorkflow } from "../../book/llm/examples/tool-workflow.mjs";

const headings = text => text.replaceAll("\r\n", "\n").match(/^#{3,6} .+$/gm);

// Work on exact chapter boundaries; content between targets stays intact.
export function assembleLegacyApplications(book, chapters, expected) {
  const newline = book.includes("\r\n") ? "\r\n" : "\n";
  for (const [name, markdown] of Object.entries(chapters)) {
    const title = markdown.split("\n")[0];
    const starts = [...book.matchAll(/^### .+\r?$/gm)].filter(match => match[0].trimEnd() === title);
    assert.equal(starts.length, 1, `Expected exactly one legacy chapter ${title}`);
    const start = starts[0].index;
    const boundary = /\r?\n---\r?\n\r?\n### /.exec(book.slice(start));
    assert.ok(boundary, `Missing end boundary for ${title}`);
    const end = start + boundary.index;
    assert.deepEqual(headings(markdown), expected[name], `Canonical ${name} heading anchors changed`);
    assert.deepEqual(headings(book.slice(start, end)), expected[name], `Assembled ${name} heading anchors changed`);
    book = book.slice(0, start) + (markdown.trimEnd() + "\n").replaceAll("\n", newline) + book.slice(end);
  }
  return book;
}

function section(markdown, title, replacement) {
  const level = title.match(/^#+/)[0].length;
  const start = markdown.indexOf(title + "\n");
  assert.ok(start >= 0, `Missing practical section: ${title}`);
  const remaining = markdown.slice(start + title.length + 1);
  const next = new RegExp(`^#{1,${level}} .+$`, "m").exec(remaining);
  return (title + "\n" + remaining.slice(0, next?.index)).trim().replace(title, "## " + replacement)
    .replace(/^###### /gm, "### ");
}

export function legacyApplications(root, checking) {
  const read = path => readFileSync(join(root, path), "utf8");
  const chapters = Object.fromEntries(["prompt", "rag", "context", "agent"].map(name => [name, read(`book/llm/legacy-${name}.md`).replaceAll("\r\n", "\n")]));
  const example = read("book/llm/examples/tool-workflow.mjs").replaceAll("\r\n", "\n");
  const fixture = JSON.parse(read("book/llm/fixtures/tool-workflow.json"));
  const snippets = {
    "single-tool-code": `const fixture = ${JSON.stringify({ catalog: fixture.catalog }, null, 2)};\n\n` + example.slice(example.indexOf("export function executeTool"), example.indexOf("export function runPriceWorkflow")).trim(),
    "workflow-code": example.slice(example.indexOf("export function runPriceWorkflow"), example.indexOf("\nif (process.argv[1]")).trim()
  };
  for (const [name, code] of Object.entries(snippets)) {
    const marker = new RegExp(`(?<=<!-- llm:${name} -->\\n)[\\s\\S]*?(?=<!-- /llm:${name} -->)`, "g");
    assert.equal([...chapters.agent.matchAll(marker)].length, 1, `Missing code marker ${name}`);
    chapters.agent = chapters.agent.replace(marker, "```javascript\n" + code + "\n```\n");
  }
  const canonicalPath = join(root, "book/llm/legacy-agent.md");
  const canonical = readFileSync(canonicalPath, "utf8");
  const normalized = chapters.agent.replaceAll("\n", canonical.includes("\r\n") ? "\r\n" : "\n");
  if (checking) assert.equal(canonical, normalized, "Agent code excerpts are stale; run npm run build:llm");
  else if (canonical !== normalized) writeFileSync(canonicalPath, normalized);
  const expected = JSON.parse(read("book/llm/legacy-application-headings.json"));
  const bookPath = join(root, "book/book.md");
  const previous = readFileSync(bookPath, "utf8");
  const assembled = assembleLegacyApplications(previous, chapters, expected);
  if (checking) assert.equal(previous, assembled, "Legacy applications are stale; run npm run build:llm");
  else if (previous !== assembled) writeFileSync(bookPath, assembled);
  for (const [alias, file] of [["context-engineering.svg", "context-selection.svg"], ["agent-loop.svg", "tool-execution-loop.svg"]]) {
    const diagram = read(`book/assets/handdraw/llm/${file}`);
    const path = join(root, "book/assets/handdraw", alias);
    if (checking) assert.equal(readFileSync(path, "utf8"), diagram, `Legacy figure ${alias} is stale`);
    else if (readFileSync(path, "utf8") !== diagram) writeFileSync(path, diagram);
  }
  const guide = [
    "# 应用回查：提示、检索与核验",
    "同一句提示更清楚了，回答为什么仍可能错？先看材料是否齐全，再分别检查检索、事实、计算与执行。以下选自本书同源修订章；完整提示词与 RAG 回查页还保留更多模板、分块方法和实际模型挑战。",
    section(chapters.prompt, "###### 最小模板（记住就够用）", "先把任务交代清楚"),
    section(chapters.prompt, "##### 4. 第四步：用“示例”锁定风格（Few-shot）", "示例放在输入里，参数是否更新？"),
    section(chapters.prompt, "###### 核心技巧 2：要求自检 (Self-Correction)", "自检之后，谁来检查？"),
    section(chapters.rag, "##### 1. RAG 基础流程：索引、检索、生成", "资料怎样进入本次回答？"),
    section(chapters.prompt, "##### 8. 安全防御：防止“指令注入”", "资料中的命令能改变任务吗？"),
    section(chapters.rag, "##### 5. RAG vs 微调：该选哪个", "缺哪一层，再补哪一层"),
    "## 自己检查一次",
    "1. 通知没有写地点，提示词加上“务必准确”后能否补出地点？\n2. 文档改了，线上检索却仍返回旧通知，先查哪一步？\n3. JSON 可解析，且引用编号存在，能否证明地点正确？\n4. 在对话里给两条例子，与用样本微调有什么不同？",
    "核对依据：地点仍应标未知；查文档处理、有效版本与索引刷新；还需对照原句能否支持地点；上下文示例改变本次输入，微调更新参数。这些判断来自人工练习，不是 DeepSeek V4.1 Flash 或 Kimi K3 的实测回答。",
    "## 来源与范围",
    "上下文示例：[GPT-3 论文](https://arxiv.org/abs/2005.14165)。间接注入：[公开研究](https://arxiv.org/abs/2302.12173)。RAG：[原始论文](https://arxiv.org/abs/2005.11401)、[综述](https://arxiv.org/abs/2312.10997)与[当前框架资料检索文档](https://docs.langchain.com/oss/python/langchain/knowledge-base)。公开研究仅支持所述模型、方法与任务范围；本地教学实验边界见各课来源说明。"
  ].join("\n\n") + "\n";
  const outcome = runPriceWorkflow(fixture.task.sku, fixture.task.quantity);
  assert.equal(outcome.status, "done");
  assert.equal(outcome.total, fixture.expectedTotal);
  const executionGuide = [
    "# 系统回查：上下文与工具执行",
    "文件存下来了，本次模型就看见了吗？模型说要计算，工具就执行了吗？这两类问题都需要沿数据和回执往回查。下面从同源旧章选取关键机制与可运行例子，完整回查页另有缓存、框架和场景说明。",
    section(chapters.context, '###### 2.2 AI 的"记性"到底像什么', "参数、输入、缓存与外部记录"),
    section(chapters.context, "###### 5.1 给信息分等级的动机", "保存之后，还要选择"),
    section(chapters.context, "###### 8.1 像盖房子一样组装上下文", "先留出输出预算"),
    section(chapters.context, '###### 7.2 "缩写"的三种境界', "压缩后，条件还在吗？"),
    section(chapters.agent, "###### 1.2 解决方案：Tool Calling（工具调用）", "请求到回执，中间发生什么？"),
    section(chapters.agent, "##### 4. Agent 的核心循环", "完成之外，还有哪些停止条件？"),
    "## 在本地运行两步工作流",
    "在仓库根目录运行 `node book/llm/examples/tool-workflow.mjs`。程序先查人工目录里的练习册单价，再把真实查价结果交给乘法；它是固定工作流，没有模型自主规划、联网或下单。源码中的工具白名单和类型检查先于运算，不执行输入里的代码。",
    "```text\n" + outcome.receipts.map(item => `${item.request.id}: ${item.request.name} → ${item.receipt.status}, ${item.receipt.result}`).join("\n") + `\n最终状态: ${outcome.status}, 总价: ${outcome.total}\n` + "```",
    "纸上追踪：单价 12.5，数量 8，乘法得到 100；改成人工目录里不存在的商品，查价失败，总价为空，乘法不执行。把实际查到的价格改成 7.25，8 件应得到 58，检查流程有没有把 100 写死。数值为教学材料，使用浮点数，不代表现实报价。",
    section(chapters.agent, "###### 10.1 技术挑战", "超时与取消之后，能否重试？"),
    "## 自己检查一次",
    "1. 文件已保存但没有进入这次输入，能否据此说模型已读到？\n2. 缓存命中是否让资料不再占窗口，或等于模型参数已更新？\n3. 共享上限 4096、输出预留 512，输入预算是多少？这是不是两个实际模型的规格？\n4. 请求 JSON 合法，是否就能汇报工具完成？取消会撤销过去的操作吗？",
    "核对依据：保存不等于本次提供；缓存复用计算，不增加窗口或训练参数；例子输入预算为 3584 token，仅是人工设定；还要校验、执行和成功回执，取消也不自动回滚已发生的步骤。",
    "## 来源与范围",
    "缓存机制见 [Transformers 文档](https://huggingface.co/docs/transformers/cache_explanation)，跨请求规则以[具体服务文档](https://api-docs.deepseek.com/guides/kv_cache)为准；上下文位置效应见 [Lost in the Middle](https://arxiv.org/abs/2307.03172)。[Manus 原文](https://manus.im/blog/Context-Engineering-for-AI-Agents-Lessons-from-Building-Manus)是团队经验，不是本课测评。[ReAct](https://arxiv.org/abs/2210.03629)研究交错的推理与动作。实际模型练习仍采用 DeepSeek V4.1 Flash 与 Kimi K3，未采集本章模型输出或费用实测。"
  ].join("\n\n") + "\n";
  return { ...chapters, guide, executionGuide };
}
