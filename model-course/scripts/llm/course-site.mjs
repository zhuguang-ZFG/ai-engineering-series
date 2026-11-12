import { readFileSync, existsSync } from "node:fs";
import { join, resolve, relative, dirname } from "node:path";
import { renderReading, readingContents } from "./reading-outline.mjs";

const escape = value => String(value).replace(/[&<>"']/g, character => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[character]);

// Pair an authored standalone image with its immediately following caption.
// The site and both book formats retain this semantic group when they reflow.
const groupFigures = html => html.replace(/<p>(<img\b[^>]*>)<\/p>\s*<p><em>([\s\S]*?)<\/em><\/p>/g,
  (_, image, caption) => `<figure class="curriculum-figure">${image}<figcaption>${caption}</figcaption></figure>`);

// Authored chapter/answer pairs share one manifest across the site and books.
// The original L URLs are learning assets, not aliases for the new C chapters.
export function buildCurriculum({ root, course, write }) {
  const curriculum = course.curriculum;
  if (!curriculum) return "";
  const source = join(root, "book/llm");
  const chapters = curriculum.chapters;
  const stageSource = JSON.parse(readFileSync(join(source, "stages.json"), "utf8"));
  const stageNotes = new Map(stageSource.stages.map(stage => [stage.id, stage]));
  if (chapters.length !== 30 || chapters.some((chapter, index) => chapter.id !== `C${String(index + 1).padStart(2, "0")}`)) {
    throw new Error("Curriculum requires ordered C01–C30");
  }
  const ids = new Set(chapters.map(chapter => chapter.id));
  for (const [index, chapter] of chapters.entries()) {
    if (!curriculum.stages.some(stage => stage.id === chapter.stage)) throw new Error(`${chapter.id}: unknown stage`);
    if (typeof chapter.abstract !== "string" || chapter.abstract.length < 18) throw new Error(`${chapter.id}: missing chapter abstract`);
    for (const prerequisite of chapter.prerequisites) {
      if (!ids.has(prerequisite) || chapters.findIndex(item => item.id === prerequisite) >= index) throw new Error(`${chapter.id}: forward/unknown prerequisite`);
    }
    for (const file of [chapter.file, chapter.answer]) {
      const path = resolve(source, file);
      if (relative(source, path).startsWith("..") || !existsSync(path)) throw new Error(`${chapter.id}: missing source ${file}`);
    }
  }
  for (const stage of curriculum.stages) {
    const note = stageNotes.get(stage.id);
    if (!note || !note.thesis || !Array.isArray(note.intro) || note.intro.length < 2) throw new Error(`${stage.id}: missing stage introduction`);
    const plate = resolve(source, "..", "assets/handdraw/llm", note.plate);
    if (!existsSync(plate)) throw new Error(`${stage.id}: missing stage plate ${note.plate}`);
  }
  for (const appendix of [stageSource.guide, stageSource.deepReading, stageSource.glossary]) {
    if (!appendix || !existsSync(join(source, appendix.file))) throw new Error(`Missing appendix source ${appendix?.file}`);
  }
  if (!stageSource.map || !existsSync(join(source, "..", "assets/handdraw/llm", stageSource.map.file))) throw new Error("Missing book map asset");
  const stagePage = stage => `stage-${stage.id.toLowerCase()}.html`;
  const navigation = current => curriculum.stages.map(stage => `<details${chapters.find(chapter => chapter.id === current)?.stage === stage.id ? " open" : ""}><summary>${escape(stage.id)} · ${escape(stage.title)} / ${escape(stage.gate)}</summary><p class="stage-nav-link"><a href="${stagePage(stage)}">阶段导言</a></p><ol>${chapters.filter(chapter => chapter.stage === stage.id).map(chapter => `<li><a href="${chapter.id.toLowerCase()}.html"${chapter.id === current ? ' aria-current="page"' : ""}>${escape(chapter.id)} ${escape(chapter.title)}</a></li>`).join("")}</ol></details>`).join("");
  const shell = (title, body) => `<!doctype html>\n<html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><meta name="description" content="五阶段三十章：从证据报告、模型原理到真实应用、评测、训练与交付。"><title>${escape(title)} · 大模型学习路线</title><link rel="stylesheet" href="lab.css"><link rel="stylesheet" href="course.css"></head><body><a class="skip" href="#main">跳到正文</a><header class="topbar"><a class="brand" href="course.html">五阶段学习路线</a><a href="index.html">旧实验与回查</a></header>${body}<footer>实施试读版 ${escape(curriculum.version)} · 真实读者学习效果尚待验收<br><a href="../../specs/llm-learning-redesign/ACCEPTANCE.md">分层验收与未验证项</a> · <a href="../../book/llm/README.md">维护说明</a></footer></body></html>\n`;
  const readingMarkdown = file => readFileSync(join(source, file), "utf8").replace("<!-- DELIVERY-CHECK -->", () => "```python\n" + readFileSync(join(source, "examples/delivery/check_package.py"), "utf8").trimEnd() + "\n```").replace(/^(\s*[-*+] )\[([ xX])\] /gm, (_, prefix, checked) => `${prefix}${checked === " " ? "□" : "☑"} `);
  const rewriteLinks = (html, from) => html.replace(/\b(href|src)="([^"#]+)(#[^"]*)?"/g, (match, attribute, target, fragment = "") => {
    if (/^(?:[a-z]+:|\/\/)/i.test(target)) return match;
    const path = resolve(dirname(join(source, from)), target);
    const chapter = chapters.find(entry => resolve(source, entry.file) === path || resolve(source, entry.answer) === path);
    if (chapter) return `${attribute}="${chapter.id.toLowerCase()}${resolve(source, chapter.answer) === path ? "-answer" : ""}.html${fragment}"`;
    const web = join(root, "exports/llm");
    return `${attribute}="${escape(relative(web, path).replaceAll("\\", "/"))}${fragment}"`;
  });
  write("course.css", readFileSync(join(root, "scripts/llm/course.css"), "utf8"));

  for (const [index, chapter] of chapters.entries()) {
    const rendered = renderReading(readingMarkdown(chapter.file), chapter.id);
    let html = groupFigures(rewriteLinks(rendered.html, chapter.file));
    const titleMatch = html.match(/<h1[^>]*>([\s\S]*?)<\/h1>/);
    if (!titleMatch) throw new Error(`${chapter.id}: expected one chapter title`);
    html = html.replace(titleMatch[0], "").trimStart();
    const stage = curriculum.stages.find(item => item.id === chapter.stage);
    const previous = chapters[index - 1];
    const next = chapters[index + 1];
    const prerequisites = chapter.prerequisites.length ? chapter.prerequisites.map(id => `<a href="${id.toLowerCase()}.html">${id}</a>`).join("、") : "不需要代码、账号或 GPU";
    write(`${chapter.id.toLowerCase()}.html`, shell(`${chapter.id} ${chapter.title}`, `<main class="shell curriculum-layout" id="main" tabindex="-1"><aside class="curriculum-nav" aria-label="全书与本章目录"><details open><summary>全书目录</summary><nav>${navigation(chapter.id)}</nav></details><details><summary>本章目录</summary>${readingContents(rendered.outline)}</details><a href="#main">回到章首</a></aside><article class="curriculum-chapter" id="${chapter.id}"><header class="chapter-opener"><p class="chapter-number">${escape(chapter.id)}</p><p class="chapter-kicker">${escape(stage.id)} · ${escape(stage.title)} / ${escape(stage.gate)}</p><h1>${escape(chapter.title)}</h1><p class="chapter-abstract">${escape(chapter.abstract)}</p></header><p class="chapter-meta">先修：${prerequisites} · <a href="${stagePage(stage)}">${escape(stage.id)} 阶段导言</a></p><div class="article-body">${html}</div><nav class="lesson-nav" aria-label="阅读顺序">${previous ? `<a href="${previous.id.toLowerCase()}.html">上一章 ${previous.id}</a>` : '<a href="course.html">学习路线</a>'}<a href="${chapter.id.toLowerCase()}-answer.html">独立作答后核对</a>${next ? `<a href="${next.id.toLowerCase()}.html">下一章 ${next.id}</a>` : '<a href="course.html">返回全书目录</a>'}</nav></article></main>`));
    const answer = renderReading(readingMarkdown(chapter.answer), `${chapter.id}-answer`);
    if ((answer.html.match(/<h1[\s>]/g) ?? []).length !== 1) throw new Error(`${chapter.id}: expected one answer title`);
    write(`${chapter.id.toLowerCase()}-answer.html`, shell(`${chapter.id} 核对依据`, `<main class="shell curriculum-answer" id="main" tabindex="-1"><article class="article-body">${rewriteLinks(answer.html, chapter.answer)}</article><nav class="lesson-nav"><a href="${chapter.id.toLowerCase()}.html">返回 ${chapter.id} 题目</a><a href="course.html">全书目录</a></nav></main>`));
  }

  for (const stage of curriculum.stages) {
    const note = stageNotes.get(stage.id);
    const stageChapters = chapters.filter(chapter => chapter.stage === stage.id);
    const stageIndex = curriculum.stages.indexOf(stage);
    const nextStage = curriculum.stages[stageIndex + 1];
    write(stagePage(stage), shell(`${stage.id} ${stage.title} · 阶段导言`, `<main class="shell stage-page" id="main" tabindex="-1"><figure class="stage-figure"><img src="../../book/assets/handdraw/llm/${escape(note.plate)}" alt="${escape(stage.id)} ${escape(stage.title)} 阶段插画"><figcaption>${escape(stage.id)} / ${escape(stage.gate)} · ${escape(note.thesis)}</figcaption></figure><header class="stage-header"><p class="stage-label">阶段 ${escape(stage.id.slice(1))} / ${escape(stage.gate)}</p><h1>${escape(stage.id)} ${escape(stage.title)}</h1><p class="stage-thesis">${escape(note.thesis)}</p><p class="stage-outcome">${escape(stage.outcome)}</p></header><div class="stage-prose">${note.intro.map(paragraph => `<p>${escape(paragraph)}</p>`).join("")}</div><section class="stage-chapters" aria-labelledby="stage-chapters"><h2 id="stage-chapters">本阶段章节</h2><ol>${stageChapters.map(chapter => `<li><a href="${chapter.id.toLowerCase()}.html"><span class="chapter-id">${escape(chapter.id)}</span>${escape(chapter.title)}</a><p>${escape(chapter.abstract)}</p></li>`).join("")}</ol></section><p class="stage-next">${nextStage ? `<a href="${stagePage(nextStage)}">下一阶段 ${escape(nextStage.id)} →</a>` : '<a href="course.html">回到学习路线 →</a>'} · <a href="deep-reading.html">阶段深读</a></p></main>`));
  }

  const guide = renderReading(readingMarkdown(stageSource.guide.file), "guide");
  write("guide.html", shell(stageSource.guide.title, `<main class="shell deep-reading-page" id="main" tabindex="-1"><article class="article-body">${groupFigures(rewriteLinks(guide.html, stageSource.guide.file))}</article><nav class="lesson-nav"><a href="map.html">全书地图</a><a href="c05.html">从 C05 开始</a><a href="course.html">学习路线</a></nav></main>`));

  const deep = renderReading(readingMarkdown(stageSource.deepReading.file), "deep-reading");
  write("deep-reading.html", shell(stageSource.deepReading.title, `<main class="shell deep-reading-page" id="main" tabindex="-1"><article class="article-body">${groupFigures(rewriteLinks(deep.html, stageSource.deepReading.file))}</article><nav class="lesson-nav"><a href="course.html">学习路线</a><a href="glossary.html">术语、符号与能力门</a><a href="c01.html">从 C01 开始</a></nav></main>`));

  const glossary = renderReading(readingMarkdown(stageSource.glossary.file), "glossary");
  write("glossary.html", shell(stageSource.glossary.title, `<main class="shell glossary-page" id="main" tabindex="-1"><article class="article-body">${groupFigures(rewriteLinks(glossary.html, stageSource.glossary.file))}</article><nav class="lesson-nav"><a href="course.html">学习路线</a><a href="deep-reading.html">五个深读问题</a><a href="c01.html">从 C01 开始</a></nav></main>`));

  const mapList = curriculum.stages.map(stage => `<li><strong>${escape(stage.id)} ${escape(stage.title)}</strong> · ${escape(stage.gate)}<span>${chapters.filter(chapter => chapter.stage === stage.id).map(chapter => `${chapter.id} ${chapter.title}`).join("；")}</span></li>`).join("");
  write("map.html", shell(stageSource.map.title, `<main class="shell book-map-page" id="main" tabindex="-1"><header class="map-header"><p class="eyebrow">五阶段 · 三十章 · 五道能力门</p><h1>全书地图</h1><p>横线是阶段，圆点是章号，右侧菱形是能力门。地图只给位置；每一章的判断仍回到正文、图注和失败记录。</p></header><figure class="map-figure"><img src="../../book/assets/handdraw/llm/${escape(stageSource.map.file)}" alt="全书地图：S1 会使用 C01–C04，S2 懂原理 C05–C10，S3 能实现 C11–C17，S4 会改进 C18–C26，S5 独立交付 C27–C30；每段右侧是能力门 K1–K5。"><figcaption>${escape(stageSource.map.description)}</figcaption></figure><section class="map-list" aria-labelledby="map-list"><h2 id="map-list">按阶段读</h2><ol>${mapList}</ol></section><nav class="lesson-nav"><a href="course.html">学习路线</a><a href="stage-s1.html">从 S1 阶段页开始</a><a href="glossary.html">术语与能力门</a></nav></main>`));

  const stageList = curriculum.stages.map(stage => {
    const note = stageNotes.get(stage.id);
    return `<section class="stage-card" aria-labelledby="${stage.id}"><p class="stage-card-label">${escape(stage.id)} / ${escape(stage.gate)}</p><h2 id="${stage.id}"><a href="${stagePage(stage)}">${escape(stage.id)} ${escape(stage.title)}</a></h2><p class="stage-thesis">${escape(note.thesis)}</p><p>${escape(stage.outcome)}</p><ol>${chapters.filter(chapter => chapter.stage === stage.id).map(chapter => `<li><a href="${chapter.id.toLowerCase()}.html">${escape(chapter.id)} ${escape(chapter.title)}</a></li>`).join("")}</ol></section>`;
  }).join("");
  write("course.html", shell(curriculum.title, `<main class="shell curriculum-home" id="main" tabindex="-1"><p class="eyebrow">五阶段 · 三十章 · 五道能力门</p><h1>${escape(curriculum.title)}</h1><p>先完成任务，再解释机制、补编程、接真实模型，最后用评测与新题检验。手工核验、本地教学运算、预训练模型与真人验收各自记证据，不互相替代。</p><p><strong>当前为实施试读版，尚无真实初学者全程验收记录。</strong>S1 无需账号，S3 起需合法可用模型和相应环境；资源不可用就停下并报告，不返回预置成功答案。</p><div class="actions"><a class="button primary" href="c01.html">从 C01 开始</a><a href="../../deliverables/llm-course.pdf">新版 PDF</a><a href="../../deliverables/llm-course.epub">新版 EPUB</a><a href="../../deliverables/llm-course-answers.pdf">单独答案 PDF</a><a href="guide.html">第零章 导读</a><a href="map.html">全书地图</a><a href="deep-reading.html">五个深读问题</a><a href="glossary.html">术语与能力门</a></div>${stageList}<section><h2>实验、来源与旧入口</h2><p>原 L01–L12 的交互实验、图解和回查入口保留；它们不是新工程章节已经接入模型的证据。</p><p><a href="index.html">十二课实验与回查</a> · <a href="../../book/llm/examples/assistant/README.md">真实助手运行说明</a> · <a href="../../book/llm/examples/tiny_decoder/README.md">微型模型运行说明</a> · <a href="../../specs/llm-learning-redesign/REFERENCE-BOOKS.md">参考与许可边界</a></p></section></main>`));
  return `<section class="downloads" aria-labelledby="curriculum-title"><h2 id="curriculum-title">新版：五阶段三十章，从任务到独立交付</h2><p>先完成资料报告，再学机制、真实应用、受控评测、小模型训练与换题交付。实施试读版，真人学习效果仍待验收。</p><div class="actions"><a class="button primary" href="course.html">进入新版学习路线</a><a href="c01.html">从 C01 开始</a><a href="map.html">全书地图</a><a href="deep-reading.html">五个深读问题</a><a href="glossary.html">术语与能力门</a></div></section>`;
}
