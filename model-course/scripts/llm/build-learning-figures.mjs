import { readFileSync, writeFileSync } from "node:fs";
import { resolve, join } from "node:path";
import assert from "node:assert/strict";

import { attentionRowArt, transformerBlockArt, gradientStepArt, stepTour } from "./mechanism-art.mjs";
import { artDefs, artPaper } from "./figure-frame.mjs";

const root = resolve(import.meta.dirname, "../..");
const checking = process.argv.includes("--check");
const folder = join(root, "book/assets/handdraw/llm");
const vector = JSON.parse(readFileSync(join(root, "book/llm/fixtures/vectors.json"), "utf8"));
const h = value => String(value).replace(/[&<>"']/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[c]);
const text = (x, y, value, size = 26, color = "#1f2328") => `<text x="${x}" y="${y}" font-size="${size}" fill="${color}">${h(value)}</text>`;
const path = (d, color = "#1f2328", dash = "") => `<path d="${d}" fill="none" stroke="${color}" stroke-width="2.8" stroke-linecap="round" stroke-linejoin="round"${dash ? ` stroke-dasharray="${dash}"` : ""}/>`;
const paper = (x, y, w, height, fill = "#fffdf8") => `<path d="M${x} ${y + 3} Q${x + w / 2} ${y - 3} ${x + w} ${y} L${x + w - 2} ${y + height} Q${x + w / 2} ${y + height + 4} ${x} ${y + height - 1}Z" fill="${fill}" stroke="#1f2328" stroke-width="2.5"/>`;
const down = (x, y, length) => path(`M${x} ${y} Q${x - 3} ${y + length / 2} ${x} ${y + length} M${x - 9} ${y + length - 11} L${x} ${y + length} L${x + 9} ${y + length - 11}`, "#B4472F");
const underline = (x, y, w) => path(`M${x} ${y} Q${x + w / 2} ${y - 5} ${x + w} ${y - 1}`, "#B4472F");
function svg(title, desc, body, height = 800) {
  return `<svg xmlns="http://www.w3.org/2000/svg" width="480" height="${height}" viewBox="0 0 480 ${height}" role="img" aria-labelledby="title desc"><title id="title">${h(title)}</title><desc id="desc">${h(desc)}</desc>${artDefs()}${artPaper(480, height)}<g font-family="'Noto Serif SC','Source Han Serif SC','Songti SC','SimSun',serif">${text(28, 48, title, 30)}${underline(28, 66, 420)}${body}</g></svg>\n`;
}
const figures = [
  ["contextual-word.svg", svg("同一个编号，两段上下文", "人工 ID 42 的苹果从同一个初始向量出发，在切成小块与开发软件的不同上下文中得到不同示意表示。", `${paper(100, 98, 280, 116)}${text(168, 137, `“${vector.token.text}”`)}${text(140, 176, `人工 ID ${vector.token.id}`)}${down(240, 221, 36)}${text(54, 297, `初始向量 [${vector.token.initial.join(", ")}]`)}${path("M240 316 L240 343 Q130 342 121 371 M111 360 L121 371 L131 360 M240 343 Q350 342 360 371 M350 360 L360 371 L370 360", "#B4472F")}${paper(28, 389, 195, 124)}${paper(256, 388, 195, 124)}${text(48, 430, "切成小块")}${text(276, 430, "开发软件")}${text(48, 478, "水果语境")}${text(276, 478, "公司语境")}${down(125, 522, 36)}${down(354, 522, 36)}${text(28, 604, "[0.9,0.1,0.1]")}${text(256, 604, "[0.1,0.3,0.95]", 24)}${underline(30, 618, 190)}${underline(258, 618, 190)}${text(40, 677, "查表起点相同，语境结果可不同")}${text(40, 739, "数字是人工表，不是网络实测", 26, "#57606a")}`)],
  ["gradient-step.svg", gradientStepArt()],
  ["transformer-block.svg", transformerBlockArt()],
  ["attention-row.svg", attentionRowArt()],
  ["training-signals.svg", svg("三种信号，分别在教什么？", "普通文本提供续写目标，任务示范提供回答样式，偏好对提供比较标准；消息角色模板另行组织本次输入。", `${path("M47 110 L47 615", "#e6e1d4")}${text(28, 117, "1")}${text(77, 117, "文本 → 续写目标", 28)}${paper(77, 140, 372, 102)}${text(94, 180, "周六 14 时开始……")}${text(94, 220, "比较下一个 token")}${text(28, 302, "2")}${text(77, 302, "示范 → 如何作答", 28)}${paper(77, 324, 372, 103)}${text(94, 365, "问地点 → 地点未知")}${text(94, 405, "学习条件下的示范")}${text(28, 487, "3")}${text(77, 487, "偏好 → 比较标准", 28)}${paper(77, 510, 372, 103, "#f0e9d8")}${text(94, 551, "有据的回答 > 编造")}${text(94, 591, "标准错，也会奖励错")}${path("M28 650 Q239 645 451 652")}${text(29, 698, "角色模板：组织输入消息")}${text(29, 746, "模板本身不执行一次训练", 26, "#57606a")}`)],
  ["retrieval-failures.svg", svg("答错了，资料在哪一步丢了？", "第一种失败是没取回含地点的通知，第二种是取回了通知B但答案仍写错地点；应分别检查检索和资料使用。", `${text(28, 112, "第一种：没拿到相关片段", 28)}${paper(28, 137, 422, 99)}${text(48, 178, "只取回 A：周六 14 时")}${text(48, 219, "A 没写地点")}${down(240, 249, 33)}${text(51, 325, "结果：本次没有地点依据")}${underline(49, 338, 366)}${text(52, 379, "先查查询、切块和取回内容")}${path("M28 417 Q240 423 451 416", "#e6e1d4")}${text(28, 467, "第二种：拿到了，仍然用错", 28)}${paper(28, 489, 422, 99, "#f0e9d8")}${text(48, 530, "取回 B：社区阅览室")}${underline(48, 544, 264)}${down(240, 600, 33)}${text(49, 677, "却回答：城市图书馆")}${path("M180 650 L371 685 M180 685 L371 650", "#57606a")}${text(49, 730, "查引用和主张是否真正对应")}${text(49, 777, "两种失败，需要不同的修正", 26, "#57606a")}`, 820)],
  ["timeout-receipt.svg", svg("超时，能断定没有执行吗？", "客户端发出job7，远端可能已经执行但回执丢失；客户端超时后应先按请求ID查状态，重试去重依赖服务端约定。", `${text(45, 113, "客户端", 28)}${text(307, 113, "服务端", 28)}${path("M99 134 L99 632 M358 134 L358 632", "#e6e1d4", "8 7")}${text(34, 177, "① 发出请求 job-7")}${path("M99 198 Q235 203 358 198 M347 189 L358 198 L347 207", "#B4472F")}${text(149, 260, "② 可能已经完成")}${paper(252, 281, 195, 74, "#f0e9d8")}${text(273, 330, "外部状态已变")}${text(130, 398, "③ 回执丢失")}${path("M358 420 L252 420 M199 420 L99 420 M110 411 L99 420 L110 429", "#57606a", "7 7")}${path("M212 405 L239 435 M212 435 L239 405")}${text(28, 485, "④ 客户端只知道：超时")}${text(28, 547, "⑤ 先按 job-7 查询状态")}${path("M99 572 Q234 577 358 572 M347 563 L358 572 L347 581", "#B4472F")}${text(28, 679, "重试是否去重，要看服务端约定")}${text(28, 731, "示意流程；本课没有远端副作用", 26, "#57606a")}`)],
  ["evaluation-split.svg", svg("先留一份没见过的材料", "开发材料用于修改提示和参数，验证材料用于选择方案，保留测试材料用于最后独立评估；图中没有真实试读成绩。", `${paper(28, 104, 422, 134)}${text(48, 146, "开发材料", 28)}${text(48, 191, "修改提示、流程或参数")}${text(48, 226, "反复查错，允许重做", 26, "#57606a")}${paper(63, 281, 387, 133)}${text(83, 325, "验证材料", 28)}${text(83, 370, "比较方法，选择方案")}${path("M55 360 Q15 357 15 265 Q15 215 27 200 M19 207 L27 200 L32 212", "#B4472F")}${text(93, 450, "最后才打开保留材料")}${down(240, 465, 35)}${paper(28, 514, 422, 151, "#f0e9d8")}${text(48, 558, "保留测试材料", 28)}${text(48, 603, "检查陌生输入与失败情况")}${text(48, 642, "记录样本数、范围与错误")}${text(28, 716, "反复看测试题再改，会影响评估")}${text(28, 768, "图中是流程，不是真人试读成绩", 26, "#57606a")}${stepTour([[24, 100, 430, 142], [59, 277, 395, 141], [24, 510, 430, 159]])}`)]
];
for (const [file, body] of figures) {
  const target = join(folder, file);
  if (checking) assert.equal(readFileSync(target, "utf8").replaceAll("\r\n", "\n"), body, `${file} is stale`);
  else writeFileSync(target, body);
}
console.log(`${checking ? "Verified" : "Built"} ${figures.length} causal teaching figures`);
