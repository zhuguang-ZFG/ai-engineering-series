import { readFileSync, writeFileSync, mkdirSync } from "node:fs";
import { resolve, join } from "node:path";
import { marked } from "marked";
import { validateData } from "./llm/validate-data.mjs";
import { principlesExperiment, principlesStatic } from "./llm/principles-templates.mjs";
import { applicationExperiment, applicationStatic } from "./llm/application-templates.mjs";
import { reviewTasks, reviewRubric, reviewRecord, reviewPaperRecord } from "./llm/review-templates.mjs";
import { legacyPrinciples } from "./llm/legacy-principles.mjs";
import { legacyApplications } from "./llm/legacy-applications.mjs";
import { legacyTransformer } from "./llm/legacy-transformer.mjs";
import { legacyReferences } from "./llm/legacy-references.mjs";
import { distillationExperiment } from "./llm/distillation-templates.mjs";
import { renderReading, readingContents } from "./llm/reading-outline.mjs";
import { mechanismLesson, mechanismFigures } from "./llm/mechanism-templates.mjs";
import { buildCurriculum } from "./llm/course-site.mjs";

const root = resolve(import.meta.dirname, "..");
const checking = process.argv.includes("--check");
const source = join(root, "book/llm");
const out = join(root, "exports/llm");
const read = (path) => readFileSync(join(source, path), "utf8");
const json = (path) => JSON.parse(read(path));
export const escapeHtml = (value) => String(value).replace(/[&<>"']/g, (ch) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[ch]);
const h = escapeHtml;
const course = json("course.json");
validateData(root, { allowPendingOutputs: !checking });
const sources = json("sources.json").sources;
const ready = course.lessons.filter((lesson) => lesson.status === "ready");
const fixtures = Object.fromEntries(["tokens", "generation", "vectors", "attention", "training", "assistant", "materials", "evidence", "retrieval", "tools", "approaches", "project"].map(name => { const data = json(`fixtures/${name}.json`); return [data.id, data]; }));
const models = json("models.json");
const distillation = json("fixtures/distillation.json");
const review = json("review/tasks.json");
const rubric = json("review/rubric.json");
const figures = JSON.parse(readFileSync(join(root, "book/assets/handdraw/llm/figures.json"), "utf8")).figures;
const legacyFigureCount = new Set([...ready.flatMap(lesson => [lesson.figure, ...(lesson.extraFigures ?? [])]), ...[...read("legacy-transformer.md").matchAll(/assets\/handdraw\/llm\/([^" ]+)/g)].map(match => match[1])]).size;
for (const expected of mechanismFigures) {
  const actual = figures.find(figure => figure.id === expected.id);
  if (!actual || Object.entries(expected).some(([key, value]) => actual[key] !== value)) throw new Error(`${expected.id}: storyboard metadata must match its computed explanation`);
  if (!course.lessons.find(lesson => lesson.id === expected.lesson)?.extraFigures?.includes(expected.file)) throw new Error(`${expected.id}: storyboard missing from course figures`);
}
const transformer = legacyTransformer(root, checking);
const legacy = legacyPrinciples(root, checking);
const applications = legacyApplications(root, checking);
const referenceChapters = legacyReferences(root, checking);
const landingPath = join(root, "exports/landing.html");
const landingSource = readFileSync(landingPath, "utf8");
let landingOutput = landingSource;
for (const [name, count] of [["lessons", ready.length], ["experiments", ready.reduce((total, lesson) => total + Number(/^X/.test(lesson.experiment)) + (lesson.extraExperiments?.length ?? 0), 0)]]) {
  const marker = new RegExp(`(<!-- llm:${name} -->)\\d+(<!-- /llm:${name} -->)`, "g");
  if ([...landingSource.matchAll(marker)].length !== 1) throw new Error(`Landing page requires one ${name} count marker`);
  landingOutput = landingOutput.replace(marker, (_, before, after) => `${before}${count}${after}`);
}
if (checking && landingOutput !== landingSource) throw new Error("Landing course counts are stale; run npm run build:llm");
if (!checking && landingOutput !== landingSource) writeFileSync(landingPath, landingOutput);
const write = (name, body) => {
  if (checking) {
    if (readFileSync(join(out, name), "utf8") !== body) throw new Error(`${name} is stale; run npm run build:llm`);
  } else writeFileSync(join(out, name), body);
};

function page(title, body, data = null) {
  const hasMechanism = mechanismFigures.some(figure => figure.lesson === data?.lesson?.id);
  body = body.replace(/<main\b([^>]*\bid="main"[^>]*)>/, '<main$1 tabindex="-1">');
  const encoded = data ? JSON.stringify(data).replaceAll("<", "\\u003c").replaceAll("\u2028", "\\u2028").replaceAll("\u2029", "\\u2029") : null;
  return `<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="description" content="${h(course.description)}"><title>${h(title)} · ${h(course.title)}</title><link rel="stylesheet" href="lab.css">${data?.lesson ? '<link rel="stylesheet" href="reader.css">' : ""}${hasMechanism ? '<link rel="stylesheet" href="mechanism.css">' : ""}</head>
<body${data?.lesson ? ` data-reading-lesson="${h(data.lesson.id)}" data-reading-title="${h(data.lesson.title)}" data-reading-version="${h(course.version)}"` : ""}><a class="skip" href="#main">跳到正文</a><header class="topbar"><a class="brand" href="index.html">${h(course.title)}</a><span>Vibe Coding 101 · 原理与应用</span><a href="../landing.html">返回课程</a></header>
${body}<footer>十二课 · 可离线阅读与操作 · 试读版<br><a href="../../deliverables/llm-explained-handdraw.pdf">阅读 PDF</a> · <a href="../../deliverables/llm-explained-handdraw.epub" download>下载 EPUB</a><br><a href="../../book/llm/README.md">课文与维护说明</a> · <a href="../../specs/llm-learning-redesign/ACCEPTANCE.md">验收记录</a></footer>
${encoded ? `<script id="lab-data" type="application/json">${encoded}</script><script src="core.js"></script><script src="principles.js"></script><script src="applications.js"></script><script src="client.js"></script><script src="application-client.js"></script>${data.lesson.id === "L05" ? '<script src="distillation.js"></script><script src="distillation-client.js"></script>' : ""}<script src="reader.js"></script>${hasMechanism ? '<script src="mechanism-player.js"></script>' : ""}` : ""}</body></html>\n`;
}

function staticExperiment(lesson, fixture) {
  let content;
  if (lesson.id === "L01") {
    const sample = fixture.encodings.cl100k_base.examples[0];
    content = `<p>示例：<code>${h(sample.text)}</code></p><p>cl100k_base 的编号：<code>${sample.tokens.map((t) => t.id).join(" · ")}</code></p><p>“Hello”与它前后的标点分开，空格可能和后面的文字一起编码。罕见字符还可能跨多个字节片段。</p>`;
  } else if (lesson.id === "L02") {
    content = `<p>当前输入：“${h(fixture.prompt)}”。教学分数：${fixture.states[fixture.prompt].map((item) => `${h(item.piece)} ${item.logit}`).join("、")}。</p><p>若选择“水”，输入变成“他端起杯子，喝了一口水”，下一轮候选变为句号或逗号。温度改变选择分布，不改变杯子里的真实内容。</p>`;
  } else if (lesson.id === "L07") {
    content = `<p>通知 A：${h(fixture.documents[0].text)}</p><p>预置回答说地点是“城市图书馆”，但 A 没有地点，应该标未知。通知 B 才提供“社区阅览室”；加入通知 C 后，周六与周日两种时间需要核对有效版本。</p>`;
  } else if (["L03", "L04", "L05", "L06"].includes(lesson.id)) content = principlesStatic(lesson, fixture, h);
  else content = applicationStatic(lesson, fixture, h);
  if (!content) throw new Error(`Missing static experiment ${lesson.id}`);
  return `<noscript><section class="lab"><h2>静态实验读法</h2><p>当前浏览器没有执行 JavaScript，可以按下面的步骤阅读结果。</p>${content}</section></noscript>`;
}

function experiment(lesson, fixture) {
  let body;
  if (lesson.id === "L01") {
    body = `<h2 id="experiment-title">拆开一段文字</h2><p>选同一句话，换一种编码。点片段查看 ID 与原始字节。</p>
<div class="control-grid"><label for="token-input">输入示例<select id="token-input">${fixture.encodings.cl100k_base.examples.map((e) => `<option value="${h(e.id)}">${h(e.label)}</option>`).join("")}</select></label>
<label for="encoding">编码<select id="encoding">${Object.keys(fixture.encodings).map((id) => `<option>${id}</option>`).join("")}</select></label></div>
<p class="sentence" id="token-text"></p><p class="token-counts" id="token-counts"></p><div class="token-pieces" id="token-pieces" role="group" aria-label="编码片段"></div>
<p class="byte-detail" id="token-detail" aria-live="polite"></p><p class="status" id="token-status" role="status"></p><p class="caption">␠ 表示空格，↵ 表示换行；连接符会标明名称，独立组合标记加 ◌ 帮助显示。这些提示符不改原始字节。不能独立组成字符的 token 显示为“字节片段”。</p>`;
  } else if (lesson.id === "L02") {
    body = `<h2 id="experiment-title">把一句话接下去</h2><p>先看候选，再生成一步。右侧百分比是当前这一步的计算结果。</p>
<p class="sentence" id="generated-text"></p><ul class="bars" id="candidate-bars" aria-label="当前候选的概率"></ul>
<label class="range-control" for="temperature">温度 <output id="temperature-value" for="temperature">1.0</output><input id="temperature" type="range" min="0" max="2" step="0.1" value="1"></label>
<div class="actions"><button class="primary" id="generate-step" type="button">生成一步</button><button id="sample-many" type="button">本步抽样 100 次</button></div>
<div class="actions"><label for="seed">重放种子 <input id="seed" type="number" min="0" max="4294967295" step="1" value="42"></label><button id="reset-generation" type="button">按种子重置</button></div>
<p class="status" id="generation-status" role="status">还没生成。改温度会改变概率，点按钮才会选择。</p><ol class="history" id="generation-history" aria-label="生成步骤记录"></ol><div id="sample-result" aria-live="polite"></div>`;
  } else if (lesson.id === "L07") {
    body = `<h2 id="experiment-title">这张待办表有依据吗？</h2><p>先选材料，勾出你认为需要核对的项，再看原句证据。</p>
<fieldset><legend>本次使用的通知</legend><div class="documents">${fixture.documents.map((doc, i) => `<div class="document" id="doc-${doc.id}"><label><input type="checkbox" name="document" value="${doc.id}" ${i === 0 ? "checked" : ""}>${h(doc.title)}</label><p>${h(doc.text)}</p></div>`).join("")}</div></fieldset>
<h3>${h(fixture.answerLabel)}</h3><p class="caption">下面这份回答故意留了问题，不是正在调用模型生成。</p><div id="claims">${fixture.claims.map((claim, i) => `<div class="claim"><b>${h(claim.field)}</b>${h(claim.value)}<label class="caption"><input type="checkbox" name="suspect" value="${i}">我认为这项需要核对</label><div id="verdict-${i}"></div></div>`).join("")}</div>
<div class="actions"><button class="primary" id="audit-materials" type="button">核对所选材料</button><button id="reset-materials" type="button">重新练习</button></div><p class="status" id="audit-status" role="status">只选通知 A 时，地点有依据吗？</p><div id="corrected-answer" hidden></div>`;
  } else if (["L03", "L04", "L05", "L06"].includes(lesson.id)) body = principlesExperiment(lesson, fixture, h);
  else body = applicationExperiment(lesson, fixture, h);
  if (!body) throw new Error(`Missing interactive experiment ${lesson.id}`);
  const label = fixture.kind === "recorded" ? "真实编码快照" : fixture.kind === "toy" ? "本地教学计算 · 非商用模型内部数据" : "课程人工示意 · 非模型实测";
  return `<section class="lab" aria-labelledby="experiment-title" data-experiment="${fixture.id}" hidden><span class="data-label">${h(label)}</span>${body}<p class="caption">${h(fixture.limitations)}</p></section>${staticExperiment(lesson, fixture)}`;
}

function quiz(lesson) {
  return `<section class="quiz"><h2 id="self-check" tabindex="-1">用自己的判断过一关</h2><form id="quiz-form" hidden><fieldset><legend>${h(lesson.question)}</legend>${lesson.options.map((option, i) => `<label><input type="radio" name="answer" value="${i}" required>${h(option)}</label>`).join("")}</fieldset><button class="primary" type="submit">检查答案</button><p class="explanation" id="quiz-feedback" role="status"></p></form>
<noscript><p>${h(lesson.question)}</p><details><summary>看答案与解释</summary><p>${h(lesson.options[lesson.correct])}</p><p>${h(lesson.feedback)}</p></details></noscript></section>`;
}

if (!checking) mkdirSync(out, { recursive: true });
write("lab.css", readFileSync(join(root, "scripts/llm/styles.css"), "utf8"));
write("reader.css", readFileSync(join(root, "scripts/llm/reader.css"), "utf8"));
write("reader.js", readFileSync(join(root, "scripts/llm/reader.js"), "utf8"));
write("mechanism.css", readFileSync(join(root, "scripts/llm/mechanism.css"), "utf8"));
write("mechanism-player.js", readFileSync(join(root, "scripts/llm/mechanism-player.js"), "utf8"));
write("core.js", readFileSync(join(root, "scripts/llm/core.cjs"), "utf8"));
write("client.js", readFileSync(join(root, "scripts/llm/client.js"), "utf8"));
write("distillation.js", readFileSync(join(root, "scripts/llm/distillation.cjs"), "utf8"));
write("distillation-client.js", readFileSync(join(root, "scripts/llm/distillation-client.js"), "utf8"));
write("principles.js", readFileSync(join(root, "scripts/llm/principles.js"), "utf8"));
write("applications.js", readFileSync(join(root, "scripts/llm/applications.cjs"), "utf8"));
write("application-client.js", readFileSync(join(root, "scripts/llm/application-client.js"), "utf8"));
const curriculumIntro = buildCurriculum({ root, course, write });
const legacyWebMarkdown = legacy.markdown.replace(/^### .+\n/, "").replace(/^#### /m, "# ").replace(/^##### /gm, "## ").replace(/^###### /gm, "### ");
const legacyHtml = marked.parse(legacyWebMarkdown).replace(/src="assets\//g, 'src="../../book/assets/').replace(/href="llm\//g, 'href="../../book/llm/').replace(/href="\.\.\/exports\/llm\//g, 'href="');
write("principles-reference.html", page("原理回查与技术修订", `<main class="shell review-page" id="main"><article>${legacyHtml}</article><nav class="lesson-nav"><a href="index.html">返回十二课</a><a href="advanced.html">只看缓存、专家与成本</a></nav></main>`));
write("advanced.html", page("缓存、专家与计算成本", `<main class="shell review-page" id="main"><article id="advanced-content">${marked.parse(legacy.advanced)}</article><nav class="lesson-nav"><a href="index.html">返回十二课</a><a href="principles-reference.html">完整原理回查</a></nav></main>`));
const applicationHtml = markdown => marked.parse(markdown)
  .replace(/src="assets\//g, 'src="../../book/assets/')
  .replace(/href="llm\//g, 'href="../../book/llm/')
  .replace(/href="\.\.\/exports\/llm\//g, 'href="');
for (const [name, title] of [["multimodal", "多模态输入回查"], ["embedding", "向量与检索回查"], ["protocols", "MCP 与 A2A 回查"]]) {
  const markdown = referenceChapters[name].replace(/^### .+\n/, "").replace(/^#### /m, "# ").replace(/^##### /gm, "## ").replace(/^###### /gm, "### ");
  write(`${name}-reference.html`, page(title, `<main class="shell review-page" id="main"><article>${applicationHtml(markdown)}</article><nav class="lesson-nav"><a href="index.html">返回十二课</a><a href="tools.html">工具执行实验</a></nav></main>`));
}
const studyViews = ready.map((lesson, index) => `<article class="study-sheet" id="${lesson.id}"><p class="eyebrow">${h(lesson.id)} / ${ready.length} · ${h(lesson.shortTitle)}</p><h2>${h(lesson.title)}</h2><div class="study-body"><img src="../../book/assets/handdraw/llm/${h(lesson.openerFigure ?? lesson.figure)}" alt="${h(figures.find(entry => entry.file === (lesson.openerFigure ?? lesson.figure)).alt)}"><div><p>${h(lesson.summary)}</p><h3>先判断</h3><p>${h(lesson.question)}</p><details><summary>核对自己的解释</summary><p>${h(lesson.options[lesson.correct])}</p><p>${h(lesson.feedback)}</p></details><p><a href="${h(lesson.slug)}.html">动手验证这一课 →</a></p><nav aria-label="图卡导航">${index ? `<a href="#${ready[index - 1].id}">上一张</a> · ` : ""}${ready[index + 1] ? `<a href="#${ready[index + 1].id}">下一张</a>` : '<a href="check-understanding.html">换材料再试一次</a>'}</nav></div></div></article>`).join("\n");
const viewStyle = `<style>.study-sheet{padding:32px;border-top:2px solid var(--ink,#1f2328);scroll-margin-top:1rem}.study-sheet h2{font-size:clamp(1.5rem,3vw,2.5rem)}.study-body{display:grid;grid-template-columns:minmax(180px,360px) 1fr;gap:36px;align-items:start}.study-body img{width:100%;height:auto}.study-body details{margin:24px 0;padding:16px;border:1px solid #57606a}.study-body p{line-height:1.8}.study-sheet nav{margin-top:32px}.cards-view{display:grid;grid-template-columns:1fr 1fr;gap:24px}.cards-view .study-sheet{padding:24px;border:1px solid #57606a}.cards-view .study-body{grid-template-columns:1fr}.cards-view img{max-height:440px;object-fit:contain}@media(max-width:760px){.study-body,.cards-view{grid-template-columns:1fr}.study-sheet{padding:20px 0}.study-body img{max-height:600px;object-fit:contain}}@media print{.topbar,footer,.skip,.view-intro{display:none}.study-sheet{break-after:page;break-inside:avoid}.study-sheet details> *{display:block}.cards-view{display:block}.shell{max-width:none}}</style>`;
for (const [name, title, className] of [["deck", "沿着十二张图讲清大模型", ""], ["cards", "十二张图，十二个判断", "cards-view"]]) {
  write(`${name}.html`, page(title, `${viewStyle}<main class="shell" id="main"><div class="view-intro"><p class="eyebrow">${h(course.title)} · ${h(course.version)}</p><h1>${title}</h1><p>先看图，再解释问题。每张图都能进入对应的本地实验；核对答案前，先用自己的话讲一遍。</p><p><a href="index.html">学习路线</a> · <a href="${name === "deck" ? "cards" : "deck"}.html">${name === "deck" ? "查看图卡" : "查看讲义"}</a> · <a href="../../deliverables/llm-explained-handdraw.pdf">PDF</a> · <a href="../../deliverables/llm-explained-handdraw.epub">EPUB</a></p></div><div class="${className}">${studyViews}</div></main>`));
}
const transformerMarkdown = transformer.markdown.replace(/^### .+\n/, "").replace(/^#### /m, "# ").replace(/^##### /gm, "## ").replace(/^###### /gm, "### ");
write("transformer-reference.html", page("Transformer 与注意力机制回查", `<main class="shell review-page" id="main"><article>${applicationHtml(transformerMarkdown)}</article><nav class="lesson-nav"><a href="index.html">返回十二课</a><a href="architecture-guide.html">结构回查精选</a></nav></main>`));
write("architecture-guide.html", page("注意力怎样拼成一层", `<main class="shell review-page" id="main"><article id="architecture-content">${applicationHtml(transformer.guide)}</article><nav class="lesson-nav"><a href="transformer-reference.html">完整 Transformer 回查</a><a href="attention.html">单头注意力实验</a></nav></main>`));
for (const [name, title] of [["prompt", "提示词工程回查"], ["rag", "RAG 架构回查"], ["context", "上下文工程回查"], ["agent", "Agent 与工具调用回查"]]) {
  const markdown = applications[name].replace(/^### .+\n/, "").replace(/^#### /m, "# ").replace(/^##### /gm, "## ").replace(/^###### /gm, "### ");
  write(`${name}-reference.html`, page(title, `<main class="shell review-page" id="main"><article>${applicationHtml(markdown)}</article><nav class="lesson-nav"><a href="index.html">返回十二课</a><a href="applications-guide.html">应用回查精选</a></nav></main>`));
}
write("applications-guide.html", page("提示、检索与核验", `<main class="shell review-page" id="main"><article id="applications-content">${applicationHtml(applications.guide)}</article><nav class="lesson-nav"><a href="prompt-reference.html">完整提示词回查</a><a href="rag-reference.html">完整 RAG 回查</a></nav></main>`));
write("execution-guide.html", page("上下文与工具执行", `<main class="shell review-page" id="main"><article id="execution-content">${applicationHtml(applications.executionGuide)}</article><nav class="lesson-nav"><a href="context-reference.html">完整上下文回查</a><a href="agent-reference.html">完整 Agent 回查</a></nav></main>`));
const reviewRecordText = JSON.stringify(reviewRecord(review, course), null, 2) + "\n";
write("review-record.json", reviewRecordText);
const reviewRecordDownload = "data:application/json;base64," + Buffer.from(reviewRecordText).toString("base64");
write("check-understanding.html", page("换一份材料练习", `<main class="shell review-page" id="main"><article id="review-content">${marked.parse(read("review/reader.md"))}<div class="actions no-print"><a class="button primary" href="../../deliverables/llm-reading-tasks.pdf" download>下载 A4 练习 PDF</a><a href="index.html">回看课程</a></div><p class="reader-code">匿名编号：________　日期：________</p>${reviewTasks(review, h)}</article><nav class="lesson-nav no-print" aria-label="练习后导航"><a href="review-guide.html">做完再看：核对依据与陪读记录</a><a href="index.html">返回学习路线</a></nav></main>`));
const guideMarkdown = read("review/facilitator.md");
if ((guideMarkdown.match(/<!-- rubric -->/g) || []).length !== 1) throw new Error("Review guide requires one rubric anchor");
write("review-guide.html", page("核对依据与陪读记录", `<main class="shell review-page" id="main"><article id="review-guide-content">${marked.parse(guideMarkdown).replace("<!-- rubric -->", reviewRubric(review, rubric, h))}${reviewPaperRecord(review, h)}</article><div class="actions no-print"><a class="button primary" href="../../deliverables/llm-reading-guide.pdf" download>下载陪读与记录 PDF</a><a class="button" href="${reviewRecordDownload}" download="llm-reading-record.json">下载空白 JSON 记录表</a></div><p class="caption no-print">也可<a href="review-record.json">直接打开空白模板</a>后另存。</p><nav class="lesson-nav no-print" aria-label="陪读导航"><a href="check-understanding.html">返回练习题目</a><a href="index.html">返回学习路线</a></nav></main>`));
const image = (lesson, file = lesson.figure) => {
  const figure = figures.find(item => item.lesson === lesson.id && item.file === file);
  if (!figure) throw new Error(`Missing figure metadata: ${file}`);
  const svg = readFileSync(join(root, "book/assets/handdraw/llm", file), "utf8");
  const [, width, height] = svg.match(/viewBox="0 0 (\d+) (\d+)"/);
  return `<figure class="concept-figure${figure.layout ? " story-figure" : ""}${file === lesson.openerFigure ? " story-opener" : ""}" id="figure-${h(figure.id)}"><img src="../../book/assets/handdraw/llm/${file}" width="${width}" height="${height}" alt="${h(figure.alt)}"><figcaption><span class="figure-number">${h(figure.id)}</span> ${h(figure.purpose)} ${h(figure.limitations)} <a class="figure-open" href="../../book/assets/handdraw/llm/${file}" aria-label="放大：${h(figure.purpose)}">看大图</a></figcaption></figure>`;
};
const modelPractice = () => `<section class="model-practice"><h2>在实际模型里复做</h2><p>使用同一份通知，分别试 ${models.models.map(model => h(model.name)).join(" 和 ")}，检查是否保留缺失项、每句依据是否正确。</p><pre>${h(models.task)}</pre><details><summary>模型入口、版本与记录方法</summary>${models.models.map(model => `<p><a href="${h(model.url)}">${h(model.name)} 官方资料</a><br>${h(model.note)}</p>`).join("")}<p>每次记录：${models.recordFields.map(h).join("、")}。一次回答不用于排名或准确率比较。</p><p class="caption">官方资料核验日期：${h(models.checkedOn)}。${h(models.limitations)}</p></details></section>`;
const route = (lessons) => `<div class="route">${lessons.map(lesson => `<a class="route-item" href="${lesson.slug}.html"><span class="route-id">${h(lesson.id)}</span><div><h3>${h(lesson.title)}</h3><p>${h(lesson.summary)}</p></div><span class="arrow" aria-hidden="true">↗</span></a>`).join("")}</div>`;

write("index.html", page("学习路线", `<main class="shell" id="main">${curriculumIntro}<section class="hero"><div><p class="eyebrow">已开放 ${ready.length} 课 · 从观察到应用</p><h1>把大模型<br><span class="underline">拆开看</span></h1><p class="intro">“他端起杯子，喝了一口……”你会接水，还是茶？从这个小问题开始，沿着手绘看模型怎样选词、怎样学习，再拿一份通知试试它会在哪里出错。</p><div class="actions"><a class="button primary" href="generation.html">先生成一句话</a><a href="training.html">训练一个小模型</a></div><p class="caption">本地实验无需账号。实际模型练习采用 DeepSeek V4.1 Flash 与 Kimi K3，附官方资料和复做记录方法。</p></div><figure><img src="../../book/assets/handdraw/llm/generation-fork.svg" width="480" height="640" alt="从水、茶、咖啡三条候选路径中选茶，把茶接回输入，再计算下一轮候选"><figcaption class="caption">重点看回环：新片段接上后，下一步的输入也变了。</figcaption></figure></section>
<section aria-labelledby="route-title"><h2 id="route-title">第一次来，先走通这三步</h2>${route(course.quickRoute.map(id => ready.find(lesson => lesson.id === id)))}</section>
<section><h2>继续追问：它里面发生了什么？</h2><p>按课号从头读，或从你关心的问题开始。每课都有操作、解释和自测。</p>${route(ready)}</section>
<section class="downloads"><h2>下载到本地阅读</h2><p>十二课、${legacyFigureCount} 张手绘图、纸上实验和自测答案，离线可读。书末附六道换材料练习。PDF 按 A5 排版；EPUB 可在阅读器中调整字号。</p><div class="actions"><a class="button primary" href="../../deliverables/llm-explained-handdraw.pdf" download>下载 PDF</a><a class="button" href="../../deliverables/llm-explained-handdraw.epub" download>下载 EPUB</a></div></section>
<section class="upcoming"><h2>合上书，换一份材料试试</h2><p>画一次生成循环，再整理一份没在课上出现过的通知。先留下自己的判断，做完再看核对依据；有人陪读时，可以记录卡点和提示。</p><div class="actions"><a class="button" href="check-understanding.html">做六道练习</a><a href="review-guide.html">核对依据与陪读记录</a></div><p><a href="../../deliverables/llm-reading-tasks.pdf" download>A4 练习 PDF</a> · <a href="../../deliverables/llm-reading-guide.pdf" download>陪读与空白记录 PDF</a></p><p><a href="training.html#distillation">蒸馏：教师的输出怎样变成学生的参数？</a></p><p>读完再追问：<a href="advanced.html">缓存、专家与计算成本</a> · <a href="principles-reference.html">完整原理回查与分词复算</a> · <a href="architecture-guide.html">注意力怎样拼成一层</a> · <a href="transformer-reference.html">完整 Transformer 回查</a></p><p>应用时回查：<a href="applications-guide.html">提示、检索与核验</a> · <a href="prompt-reference.html">完整提示词工程</a> · <a href="rag-reference.html">完整 RAG 架构</a></p><p>搭系统时回查：<a href="execution-guide.html">上下文与工具执行</a> · <a href="context-reference.html">完整上下文工程</a> · <a href="agent-reference.html">完整 Agent 与工具调用</a></p></section>
<section class="reading-index"><h2>换一种方式复习</h2><p><a href="deck.html">十二张讲义</a> · <a href="cards.html">手绘图卡</a> · <a href="multimodal-reference.html">多模态输入</a> · <a href="embedding-reference.html">向量检索</a> · <a href="protocols-reference.html">MCP 与 A2A</a></p></section>${modelPractice()}<section class="upcoming"><p class="eyebrow">十二课已开放 · 学习效果待真实试读</p><h2>把方法用到自己的资料</h2><p>读完原理，再到检索、工具与综合交付里检查结果。最后换一份未见通知，独立完成带证据的安排表。</p><p><a href="project.html">完成资料助手练习</a> · <a href="../../book/book.md">回到完整书籍与编程实战</a></p></section></main>`));

for (const [index, lesson] of ready.entries()) {
  const fixture = lesson.id === "L08" ? { ...fixtures[lesson.experiment], documents: fixtures.X06.documents } : fixtures[lesson.experiment];
  let markdown = read(`lessons/${lesson.file}`);
  const depth = read(`deepening/${lesson.file}`);
  if (lesson.id === "L05") markdown = markdown.replace("<!-- distillation -->", depth + "\n\n" + read("distillation.md"));
  else if (markdown.includes("## 再深一层")) markdown = markdown.replace("## 再深一层", depth + "\n\n## 再深一层");
  else markdown += "\n\n" + depth;
  if ((markdown.match(/<!-- experiment -->/g) || []).length !== 1) throw new Error(`${lesson.id}: expected exactly one experiment anchor`);
  const placedFigures = new Set();
  const illustratedMarkdown = markdown.replace(/<!-- figure: (G\d+) -->/g, (_, id) => {
    const figure = figures.find(entry => entry.id === id && entry.lesson === lesson.id);
    if (!figure || !(lesson.extraFigures ?? []).includes(figure.file)) throw new Error(`${lesson.id}: unregistered inline figure ${id}`);
    if (placedFigures.has(figure.file)) throw new Error(`${lesson.id}: duplicate inline figure ${id}`);
    placedFigures.add(figure.file);
    return image(lesson, figure.file);
  });
  if (/<!--\s*figure:/.test(illustratedMarkdown)) throw new Error(`${lesson.id}: invalid figure anchor`);
  if (lesson.openerFigure && !placedFigures.has(lesson.openerFigure)) throw new Error(`${lesson.id}: missing opening illustration`);
  const mechanismFigure = mechanismFigures.find(figure => figure.lesson === lesson.id);
  const mechanismMarkers = [...illustratedMarkdown.matchAll(/<!-- mechanism: ([a-z]+) -->/g)];
  if (mechanismMarkers.length !== Number(Boolean(mechanismFigure))) throw new Error(`${lesson.id}: incorrect mechanism anchor count`);
  const mechanismMarkdown = illustratedMarkdown.replace(/<!-- mechanism: ([a-z]+) -->/g, (_, id) => {
    if (!mechanismFigure || mechanismFigure.file !== `${id}-steps.svg`) throw new Error(`${lesson.id}: unexpected mechanism ${id}`);
    placedFigures.add(mechanismFigure.file);
    return mechanismLesson(id, h);
  });
  if (/<!--\s*mechanism:/.test(mechanismMarkdown)) throw new Error(`${lesson.id}: invalid mechanism anchor`);
  const reading = renderReading(mechanismMarkdown, lesson.id);
  const body = reading.html.replace("<!-- experiment -->", image(lesson) + experiment(lesson, fixture)).replace("<!-- distillation-figure -->", lesson.id === "L05" ? image(lesson, "distillation-flow.svg") : "").replace("<!-- distillation -->", lesson.id === "L05" ? distillationExperiment(distillation, h) : "").replace("<!-- depth-figure -->", lesson.depthFigure ? image(lesson, lesson.depthFigure) : "").replace('id="experiment-title"', 'id="experiment-title" tabindex="-1"');
  const contents = readingContents(reading.outline);
  const references = lesson.sources.map((id) => {
    const entry = sources.find((item) => item.id === id);
    if (!entry) throw new Error(`Unknown source ${id}`);
    return `<li>${entry.url ? `<a href="${h(entry.url)}">${h(entry.title)}</a>` : h(entry.title)}<p>${h(entry.scope)} ${h(entry.method)}</p></li>`;
  }).join("");
  write(`${lesson.slug}.html`, page(lesson.title, `<main class="shell lesson-layout" id="main"><aside class="sidebar" aria-label="阅读导航"><div class="reader-tools" hidden><label for="reader-size">正文字号<select id="reader-size"><option value="18">标准</option><option value="20">较大</option><option value="22">最大</option></select></label><a id="reader-resume" hidden>继续上次阅读</a></div><details class="course-menu"><summary>全部十二课</summary><nav aria-label="课程目录"><ol>${ready.map((entry) => `<li><a href="${entry.slug}.html" ${entry.id === lesson.id ? 'aria-current="page"' : ""}>${h(entry.id)} · ${h(entry.shortTitle)}</a></li>`).join("")}</ol><a href="index.html">查看学习路线</a></nav></details><details class="section-menu"><summary>本课目录</summary>${contents}</details></aside>
<article class="lesson"><p class="eyebrow">${h(lesson.id)} / ${ready.length} · ${h(lesson.shortTitle)}</p><div class="article-body">${body}</div>${(lesson.extraFigures ?? []).filter(file => file !== "distillation-flow.svg" && file !== lesson.depthFigure && !placedFigures.has(file)).map(file => `<details class="deeper-figure"><summary>${h(file === "transformer-block.svg" ? "深入图：注意力之外还有什么？" : file === "multihead-flow.svg" ? "深入图：两个头怎样汇合？" : file === "context-selection.svg" ? "深入图：外部保存与本次输入" : figures.find(entry => entry.file === file).purpose)}</summary>${image(lesson, file)}</details>`).join("")}${quiz(lesson)}<details class="model-practice-fold"><summary>换到实际模型再试一次</summary>${modelPractice()}</details><details class="sources"><summary>学习目标、来源与演示边界</summary><p>${h(lesson.objective)}</p><ul>${references}</ul><p>实际模型案例：<a href="${h(models.models[0].url)}">DeepSeek 官方资料</a> · <a href="${h(models.models[1].url)}">Kimi K3 官方资料</a>（${h(models.checkedOn)} 核验）。</p><a href="../../book/llm/sources.json">查看来源和纠错台账</a></details><nav class="lesson-nav" aria-label="课后导航">${ready[index - 1] ? `<a rel="prev" href="${ready[index - 1].slug}.html">上一课：${h(ready[index - 1].shortTitle)}</a>` : '<a href="index.html">返回学习路线</a>'}${ready[index + 1] ? `<a rel="next" href="${ready[index + 1].slug}.html">下一课：${h(ready[index + 1].shortTitle)}</a>` : '<a href="check-understanding.html">换一份材料，独立试试</a>'}</nav></article></main>`, { lesson, fixture, ...(lesson.id === "L05" ? { distillation } : {}) }));
}

console.log(`${checking ? "Verified" : "Built"} ${ready.length} lessons and learning route (offline scripts + pinned fixtures)`);
