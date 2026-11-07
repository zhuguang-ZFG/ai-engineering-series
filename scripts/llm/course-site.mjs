import { readFileSync, existsSync } from "node:fs";
import { join, resolve, relative, dirname } from "node:path";
import { renderReading, readingContents } from "./reading-outline.mjs";

const escape = value => String(value).replace(/[&<>"']/g, character => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[character]);

// Authored chapter/answer pairs share one manifest across the site and books.
// The original L URLs are learning assets, not aliases for the new C chapters.
export function buildCurriculum({ root, course, write }) {
  const curriculum = course.curriculum;
  if (!curriculum) return "";
  const source = join(root, "book/llm");
  const chapters = curriculum.chapters;
  if (chapters.length !== 30 || chapters.some((chapter, index) => chapter.id !== `C${String(index + 1).padStart(2, "0")}`)) {
    throw new Error("Curriculum requires ordered C01–C30");
  }
  const ids = new Set(chapters.map(chapter => chapter.id));
  for (const [index, chapter] of chapters.entries()) {
    if (!curriculum.stages.some(stage => stage.id === chapter.stage)) throw new Error(`${chapter.id}: unknown stage`);
    for (const prerequisite of chapter.prerequisites) {
      if (!ids.has(prerequisite) || chapters.findIndex(item => item.id === prerequisite) >= index) throw new Error(`${chapter.id}: forward/unknown prerequisite`);
    }
    for (const file of [chapter.file, chapter.answer]) {
      const path = resolve(source, file);
      if (relative(source, path).startsWith("..") || !existsSync(path)) throw new Error(`${chapter.id}: missing source ${file}`);
    }
  }
  const navigation = current => curriculum.stages.map(stage => `<details${chapters.find(chapter => chapter.id === current)?.stage === stage.id ? " open" : ""}><summary>${escape(stage.id)} · ${escape(stage.title)} / ${escape(stage.gate)}</summary><ol>${chapters.filter(chapter => chapter.stage === stage.id).map(chapter => `<li><a href="${chapter.id.toLowerCase()}.html"${chapter.id === current ? ' aria-current="page"' : ""}>${escape(chapter.id)} ${escape(chapter.title)}</a></li>`).join("")}</ol></details>`).join("");
  const shell = (title, body) => `<!doctype html>\n<html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><meta name="description" content="五阶段三十章：从证据报告、模型原理到真实应用、评测、训练与交付。"><title>${escape(title)} · 把大模型拆开看</title><link rel="stylesheet" href="lab.css"><link rel="stylesheet" href="course.css"></head><body><a class="skip" href="#main">跳到正文</a><header class="topbar"><a class="brand" href="course.html">五阶段学习路线</a><a href="index.html">旧实验与回查</a></header>${body}<footer>实施试读版 ${escape(curriculum.version)} · 真实读者学习效果尚待验收<br><a href="../../specs/llm-learning-redesign/ACCEPTANCE.md">分层验收与未验证项</a> · <a href="../../book/llm/README.md">维护说明</a></footer></body></html>\n`;
  const readingMarkdown = file => readFileSync(join(source, file), "utf8").replace(/^(\s*[-*+] )\[([ xX])\] /gm, (_, prefix, checked) => `${prefix}${checked === " " ? "□" : "☑"} `);
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
    const html = rewriteLinks(rendered.html, chapter.file);
    if ((html.match(/<h1[\s>]/g) ?? []).length !== 1) throw new Error(`${chapter.id}: expected one chapter title`);
    const previous = chapters[index - 1];
    const next = chapters[index + 1];
    const prerequisites = chapter.prerequisites.length ? chapter.prerequisites.map(id => `<a href="${id.toLowerCase()}.html">${id}</a>`).join("、") : "不需要代码、账号或 GPU";
    write(`${chapter.id.toLowerCase()}.html`, shell(`${chapter.id} ${chapter.title}`, `<main class="shell curriculum-layout" id="main" tabindex="-1"><aside class="curriculum-nav" aria-label="全书与本章目录"><details open><summary>全书目录</summary><nav>${navigation(chapter.id)}</nav></details><details><summary>本章目录</summary>${readingContents(rendered.outline)}</details><a href="#main">回到章首</a></aside><article class="curriculum-chapter" id="${chapter.id}"><p class="eyebrow">${escape(chapter.stage)} / ${escape(chapter.id)} · ${escape(curriculum.status)}</p><p class="caption">先修：${prerequisites}</p><div class="article-body">${html}</div><nav class="lesson-nav" aria-label="阅读顺序">${previous ? `<a href="${previous.id.toLowerCase()}.html">上一章 ${previous.id}</a>` : '<a href="course.html">学习路线</a>'}<a href="${chapter.id.toLowerCase()}-answer.html">独立作答后核对</a>${next ? `<a href="${next.id.toLowerCase()}.html">下一章 ${next.id}</a>` : '<a href="course.html">返回全书目录</a>'}</nav></article></main>`));
    const answer = renderReading(readingMarkdown(chapter.answer), `${chapter.id}-answer`);
    if ((answer.html.match(/<h1[\s>]/g) ?? []).length !== 1) throw new Error(`${chapter.id}: expected one answer title`);
    write(`${chapter.id.toLowerCase()}-answer.html`, shell(`${chapter.id} 核对依据`, `<main class="shell curriculum-answer" id="main" tabindex="-1"><article class="article-body">${rewriteLinks(answer.html, chapter.answer)}</article><nav class="lesson-nav"><a href="${chapter.id.toLowerCase()}.html">返回 ${chapter.id} 题目</a><a href="course.html">全书目录</a></nav></main>`));
  }
  const stageList = curriculum.stages.map(stage => `<section aria-labelledby="${stage.id}"><h2 id="${stage.id}">${escape(stage.id)} ${escape(stage.title)} / ${escape(stage.gate)}</h2><p>${escape(stage.outcome)}</p><ol>${chapters.filter(chapter => chapter.stage === stage.id).map(chapter => `<li><a href="${chapter.id.toLowerCase()}.html">${escape(chapter.id)} ${escape(chapter.title)}</a></li>`).join("")}</ol></section>`).join("");
  write("course.html", shell("从入门到独立交付", `<main class="shell curriculum-home" id="main" tabindex="-1"><p class="eyebrow">五阶段 · 三十章 · 五道能力门</p><h1>从一份能核对的报告，到独立交付大模型应用</h1><p>先完成任务，再解释机制、补编程、接真实模型，最后用评测与新题检验。手工核验、本地教学运算、预训练模型与真人验收各自记证据，不互相替代。</p><p><strong>当前为实施试读版，尚无真实初学者全程验收记录。</strong>S1 无需账号，S3 起需合法可用模型和相应环境；资源不可用就停下并报告，不返回预置成功答案。</p><div class="actions"><a class="button primary" href="c01.html">从 C01 开始</a><a href="../../deliverables/llm-course.pdf">新版 PDF</a><a href="../../deliverables/llm-course.epub">新版 EPUB</a><a href="../../deliverables/llm-course-answers.pdf">单独答案 PDF</a></div>${stageList}<section><h2>实验、来源与旧入口</h2><p>原 L01–L12 的交互实验、图解和回查入口保留；它们不是新工程章节已经接入模型的证据。</p><p><a href="index.html">十二课实验与回查</a> · <a href="../../book/llm/examples/assistant/README.md">真实助手运行说明</a> · <a href="../../book/llm/examples/tiny_decoder/README.md">微型模型运行说明</a> · <a href="../../specs/llm-learning-redesign/REFERENCE-BOOKS.md">参考与许可边界</a></p></section></main>`));
  return `<section class="downloads" aria-labelledby="curriculum-title"><h2 id="curriculum-title">新版：五阶段三十章，从任务到独立交付</h2><p>先完成资料报告，再学机制、真实应用、受控评测、小模型训练与换题交付。实施试读版，真人学习效果仍待验收。</p><div class="actions"><a class="button primary" href="course.html">进入新版学习路线</a><a href="c01.html">从 C01 开始</a></div></section>`;
}
