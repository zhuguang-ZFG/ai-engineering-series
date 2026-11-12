import { readFileSync, writeFileSync } from "node:fs";
import { resolve, join } from "node:path";

import { multiheadArt, stepTour } from "./mechanism-art.mjs";

const out = resolve(import.meta.dirname, "../../book/assets/handdraw/llm");
const ink = "#1f2328", paper = "#fbfaf6", wash = "#f0e9d8";
const text = (x, y, label, size = 26) => `<text x="${x}" y="${y}" font-size="${size}">${label}</text>`;
const box = (x, y, w, h, fill = paper) => `<path d="M${x - 2} ${y + 2} Q${x + w * .28} ${y - 2.6} ${x + w + 2} ${y + 1} L${x + w + .6} ${y + h + 1} Q${x + w * .62} ${y + h + 2.8} ${x - 3} ${y + h - .6} Q${x - 2.4} ${y + h * .5} ${x - 2} ${y + 2} Z" fill="${fill}" stroke="${ink}" stroke-width="2.5" stroke-linejoin="round"/>`;
const arrow = (x, y, endY) => `<path d="M${x} ${y} Q${x - 2} ${(y + endY) / 2} ${x} ${endY}" fill="none" stroke="${ink}" stroke-width="2.5" marker-end="url(#arrow)"/>`;
const items = [];
function figure(file, height, title, desc, body) {
  const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="480" height="${height}" viewBox="0 0 480 ${height}" role="img" aria-labelledby="title desc">
  <title id="title">${title}</title>
  <desc id="desc">${desc}</desc>
  <defs><marker id="arrow" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0 0 L6 3 L0 6" fill="none" stroke="${ink}" stroke-width="1.5"/></marker></defs>
  <g font-family="'Noto Serif SC','Source Han Serif SC','Songti SC','SimSun',serif" fill="${ink}">
    ${body.join("\n    ")}
  </g>
</svg>\n`;
  items.push({ file, svg });
}

items.push({ file: "multihead-flow.svg", svg: multiheadArt() });
figure("claim-evidence.svg", 590, "结论与引用分两道检查", "预置回答说周日，通知原句写周六。先确认原文存在，再检查它是否支持结论。", [
  text(24, 40, "引用编号不能代替核对", 28),
  box(32, 74, 416, 100), text(52, 113, "预置主张：周日 14:00"), text(52, 150, "引用：通知 A"),
  arrow(240, 184, 218),
  `<path d="M52 238 L410 240 L430 260 L428 376 L50 374 Z M410 240 L410 263 L430 260" fill="${wash}" stroke="${ink}" stroke-width="2.5"/>`,
  text(74, 285, "A 原句：周六 14:00 开始"), text(74, 333, "原文存在，结论却不符"),
  arrow(240, 386, 418),
  text(24, 463, "① 原文是否存在？"), text(24, 505, "② 是否支持这项主张？"), text(24, 558, "缺失、冲突和错引，分别留下")
]);
figure("retrieve-then-answer.svg", 688, "检索到的片段才进入输入", "资料先切块，查询决定取回哪些片段，命中片段连同问题进入上下文；无命中时停止，检索不改参数。", [
  text(24, 40, "从一叠文件，取回几段依据", 28),
  box(42, 70, 382, 56), box(34, 78, 382, 56), box(26, 86, 382, 56, wash), text(46, 124, "文件 + 文档编号 + 版本"),
  arrow(240, 152, 180), box(26, 192, 426, 64), text(46, 234, "切成片段，保留原文位置"),
  arrow(240, 266, 294), box(26, 306, 426, 96, wash), text(46, 344, "查询 → 检索 → 取回"), text(46, 382, "无命中：停止，不补零分项"),
  arrow(240, 412, 440), box(26, 452, 426, 86), text(46, 489, "本次输入：问题 + 命中片段"), text(46, 524, "没有取回的文件不在这里"),
  arrow(240, 548, 576), text(26, 616, "带出处回答；版本仍需核对"), text(26, 662, "检索没有把文件训练进参数"),
  stepTour([[22, 66, 432, 80], [22, 188, 434, 72], [22, 302, 434, 104], [22, 448, 434, 94]])
]);
figure("tool-execution-loop.svg", 680, "工具请求与执行回执", "先提出请求，再由程序校验和执行，回传数值后结束；失败或取消进入终态。", [
  text(24, 40, "说要计算，到真的计算", 28),
  box(28, 70, 424, 66), text(48, 113, "请求：12.5 × 8"), arrow(240, 146, 170),
  box(28, 182, 424, 76, wash), text(48, 225, "程序校验：工具、类型、范围"), arrow(240, 268, 292),
  box(28, 304, 424, 66), text(48, 347, "本地执行 → 数值 100"), arrow(240, 380, 404),
  box(28, 416, 424, 66, wash), text(48, 459, "回传结果 → 才能汇报完成"),
  stepTour([[24, 66, 432, 74], [24, 178, 432, 84], [24, 300, 432, 74], [24, 412, 432, 74]]),
  `<path d="M28 532 Q240 530 452 532" fill="none" stroke="${ink}" stroke-width="2" stroke-dasharray="7 6"/>`,
  text(28, 577, "失败 / 超时 / 取消 → 停止"), text(28, 619, "终态不继续，不显示成功"), text(28, 661, "本图请求预置，不是模型实测")
]);
figure("context-selection.svg", 700, "外部保存不等于本次可见", "外部原文、任务与历史经过权限、版本和相关性选择后进入本次输入；人工共享预算 4096 中输入至多 3584，输出预留 512。缓存复用计算，不增加窗口或参数。", [
  text(24, 40, "保存了，还要选进本次输入", 28),
  box(28, 76, 424, 96), text(48, 113, "外部保存：原文 / 任务 / 历史"), text(48, 153, "有来源，可更正，可重新读取"),
  arrow(240, 182, 208),
  box(28, 220, 424, 96, wash), text(48, 257, "选取：权限 → 版本 → 相关性"), text(48, 297, "没有选入，不代表本次已读"),
  arrow(240, 326, 352),
  box(28, 364, 424, 96), text(48, 401, "本次输入：规则 / 目标 / 依据"), text(48, 441, "历史 / 回执 / 当前问题"),
  arrow(240, 470, 496),
  box(28, 508, 424, 96, wash), text(48, 545, "人工预算：窗口 4096 token"), text(48, 585, "输入 3584 + 输出预留 512"),
  stepTour([[24, 72, 432, 104], [24, 216, 432, 104], [24, 360, 432, 104], [24, 504, 432, 104]]),
  text(28, 650, "缓存复用计算，不扩大窗口"), text(28, 687, "示意数字，不是实际模型规格")
]);
figure("choose-an-approach.svg", 668, "按缺口选择方案", "全文够用先明确任务；缺相关新资料用检索；缺确定计算用受控工具；稳定行为问题经评测再考虑微调。", [
  text(24, 40, "先问：任务缺的是什么？", 28),
  ...[
    [76, "一页材料，做一次", "先写清任务与输出约定"],
    [210, "缺不断更新的依据", "检索 → 核对出处和版本"],
    [344, "缺可以复算的执行", "受控工具 → 检查回执"],
    [478, "固定行为仍反复失败", "有数据和评测，再考虑微调"]
  ].flatMap(([y, a, b]) => [box(28, y, 424, 102, y === 210 ? wash : paper), text(48, y + 37, a), text(48, y + 77, b)]),
  text(28, 638, "可组合；先用任务样本检验"),
  stepTour([[24, 72, 432, 110], [24, 206, 432, 110], [24, 340, 432, 110], [24, 474, 432, 110]])
]);
figure("materials-to-result.svg", 686, "有依据的资料助手交付", "任务约定与材料一起进入处理，结果逐项连接原句，缺失和冲突保留，人工回查后导出。", [
  text(24, 40, "把结果交给下一个人", 28),
  box(28, 74, 424, 78), text(48, 120, "任务约定 + 带编号的材料"), arrow(240, 162, 190),
  box(28, 202, 424, 102, wash), text(48, 239, "按字段整理 → 连回原句"), text(48, 279, "活动 / 时间 / 地点 / 报名"), arrow(240, 314, 342),
  box(28, 354, 424, 102), text(48, 391, "缺失：留未知；冲突：待确认"), text(48, 431, "无依据 / 范围外：停止"), arrow(240, 466, 494),
  box(28, 506, 424, 78, wash), text(48, 552, "人工回查 → 导出核验报告"),
  stepTour([[24, 70, 432, 86], [24, 198, 432, 110], [24, 350, 432, 110], [24, 502, 432, 86]]),
  text(28, 628, "把材料里的命令当内容"), text(28, 670, "草稿不等于已经执行报名")
]);

for (const { file, svg } of items) {
  const path = join(out, file);
  if (process.argv.includes("--check")) {
    if (readFileSync(path, "utf8") !== svg) throw new Error(`Stale figure ${file}`);
  } else writeFileSync(path, svg);
}
console.log(`${process.argv.includes("--check") ? "Verified" : "Built"} ${items.length} application figures`);
