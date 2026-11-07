import { readFileSync, writeFileSync } from "node:fs";
import { resolve, join } from "node:path";

const out = resolve(import.meta.dirname, "../../book/assets/handdraw/llm");
const ink = "#1f2328", paper = "#fbfaf6", green = "#d3efd9";
const text = (x, y, label, size = 26) => `<text x="${x}" y="${y}" font-size="${size}">${label}</text>`;
const box = (x, y, w, h, fill = paper) => `<path d="M${x + 8} ${y} L${x + w - 4} ${y + 1} Q${x + w} ${y + 2} ${x + w} ${y + 8} L${x + w - 1} ${y + h - 4} Q${x + w - 2} ${y + h} ${x + w - 8} ${y + h} L${x + 4} ${y + h - 1} Q${x} ${y + h - 2} ${x} ${y + h - 8} L${x + 1} ${y + 6} Q${x + 2} ${y} ${x + 8} ${y} Z" fill="${fill}" stroke="${ink}" stroke-width="2.5"/>`;
const arrow = (x, y, endY) => `<path d="M${x} ${y} Q${x - 2} ${(y + endY) / 2} ${x} ${endY}" fill="none" stroke="${ink}" stroke-width="2.5" marker-end="url(#arrow)"/>`;
const items = [];
function figure(file, height, title, desc, body) {
  const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="480" height="${height}" viewBox="0 0 480 ${height}" role="img" aria-labelledby="title desc">
  <title id="title">${title}</title>
  <desc id="desc">${desc}</desc>
  <defs><marker id="arrow" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0 0 L6 3 L0 6" fill="none" stroke="${ink}" stroke-width="1.5"/></marker></defs>
  <rect width="480" height="${height}" fill="${paper}"/>
  <g font-family="'Microsoft YaHei',sans-serif" fill="${ink}">
    ${body.join("\n    ")}
  </g>
</svg>\n`;
  items.push({ file, svg });
}

figure("multihead-flow.svg", 660, "两个头先汇总，再拼接混合", "同一输入分到两组 Q/K/V 投影，每头使用因果掩码独立汇总；两头输出拼接后经过输出投影。没有预设语法头或情感头。", [
  text(24, 40, "同一输入，两组投影", 28),
  box(28, 70, 424, 64), text(48, 112, "输入 X：三个二维向量"),
  `<path d="M240 144 L240 163 L128 163 M240 163 L352 163" fill="none" stroke="${ink}" stroke-width="2.5"/>`,
  arrow(128, 163, 187), arrow(352, 163, 187),
  box(28, 200, 200, 128), box(252, 200, 200, 128, green),
  text(48, 239, "第 1 头"), text(48, 278, "投影 Q/K/V"), text(48, 316, "取第一维"),
  text(272, 239, "第 2 头"), text(272, 278, "投影 Q/K/V"), text(272, 316, "取第二维"),
  arrow(128, 338, 360), arrow(352, 338, 360),
  box(28, 372, 200, 62), box(252, 372, 200, 62, green),
  text(48, 412, "掩码后汇总"), text(272, 412, "掩码后汇总"),
  `<path d="M128 444 L128 465 L352 465 L352 444" fill="none" stroke="${ink}" stroke-width="2.5"/>`,
  arrow(240, 465, 486),
  box(28, 498, 424, 66), text(48, 540, "拼接 → 输出投影 Wᵒ"),
  text(28, 606, "各头不预设语言学职责"), text(28, 647, "人工小矩阵，不是完整模型")
]);
figure("claim-evidence.svg", 590, "结论与引用分两道检查", "预置回答说周日，通知原句写周六。先确认原文存在，再检查它是否支持结论。", [
  text(24, 40, "引用编号不能代替核对", 28),
  box(32, 74, 416, 100), text(52, 113, "预置主张：周日 14:00"), text(52, 150, "引用：通知 A"),
  arrow(240, 184, 218),
  `<path d="M52 238 L410 240 L430 260 L428 376 L50 374 Z M410 240 L410 263 L430 260" fill="${green}" stroke="${ink}" stroke-width="2.5"/>`,
  text(74, 285, "A 原句：周六 14:00 开始"), text(74, 333, "原文存在，结论却不符"),
  arrow(240, 386, 418),
  text(24, 463, "① 原文是否存在？"), text(24, 505, "② 是否支持这项主张？"), text(24, 558, "缺失、冲突和错引，分别留下")
]);
figure("retrieve-then-answer.svg", 688, "检索到的片段才进入输入", "资料先切块，查询决定取回哪些片段，命中片段连同问题进入上下文；无命中时停止，检索不改参数。", [
  text(24, 40, "从一叠文件，取回几段依据", 28),
  box(42, 70, 382, 56), box(34, 78, 382, 56), box(26, 86, 382, 56, green), text(46, 124, "文件 + 文档编号 + 版本"),
  arrow(240, 152, 180), box(26, 192, 426, 64), text(46, 234, "切成片段，保留原文位置"),
  arrow(240, 266, 294), box(26, 306, 426, 96, green), text(46, 344, "查询 → 检索 → 取回"), text(46, 382, "无命中：停止，不补零分项"),
  arrow(240, 412, 440), box(26, 452, 426, 86), text(46, 489, "本次输入：问题 + 命中片段"), text(46, 524, "没有取回的文件不在这里"),
  arrow(240, 548, 576), text(26, 616, "带出处回答；版本仍需核对"), text(26, 662, "检索没有把文件训练进参数")
]);
figure("tool-execution-loop.svg", 680, "工具请求与执行回执", "先提出请求，再由程序校验和执行，回传数值后结束；失败或取消进入终态。", [
  text(24, 40, "说要计算，到真的计算", 28),
  box(28, 70, 424, 66), text(48, 113, "请求：12.5 × 8"), arrow(240, 146, 170),
  box(28, 182, 424, 76, green), text(48, 225, "程序校验：工具、类型、范围"), arrow(240, 268, 292),
  box(28, 304, 424, 66), text(48, 347, "本地执行 → 数值 100"), arrow(240, 380, 404),
  box(28, 416, 424, 66, green), text(48, 459, "回传结果 → 才能汇报完成"),
  `<path d="M28 532 Q240 530 452 532" fill="none" stroke="${ink}" stroke-width="2" stroke-dasharray="7 6"/>`,
  text(28, 577, "失败 / 超时 / 取消 → 停止"), text(28, 619, "终态不继续，不显示成功"), text(28, 661, "本图请求预置，不是模型实测")
]);
figure("context-selection.svg", 700, "外部保存不等于本次可见", "外部原文、任务与历史经过权限、版本和相关性选择后进入本次输入；人工共享预算 4096 中输入至多 3584，输出预留 512。缓存复用计算，不增加窗口或参数。", [
  text(24, 40, "保存了，还要选进本次输入", 28),
  box(28, 76, 424, 96), text(48, 113, "外部保存：原文 / 任务 / 历史"), text(48, 153, "有来源，可更正，可重新读取"),
  arrow(240, 182, 208),
  box(28, 220, 424, 96, green), text(48, 257, "选取：权限 → 版本 → 相关性"), text(48, 297, "没有选入，不代表本次已读"),
  arrow(240, 326, 352),
  box(28, 364, 424, 96), text(48, 401, "本次输入：规则 / 目标 / 依据"), text(48, 441, "历史 / 回执 / 当前问题"),
  arrow(240, 470, 496),
  box(28, 508, 424, 96, green), text(48, 545, "人工预算：窗口 4096 token"), text(48, 585, "输入 3584 + 输出预留 512"),
  text(28, 650, "缓存复用计算，不扩大窗口"), text(28, 687, "示意数字，不是实际模型规格")
]);
figure("choose-an-approach.svg", 668, "按缺口选择方案", "全文够用先明确任务；缺相关新资料用检索；缺确定计算用受控工具；稳定行为问题经评测再考虑微调。", [
  text(24, 40, "先问：任务缺的是什么？", 28),
  ...[
    [76, "一页材料，做一次", "先写清任务与输出约定"],
    [210, "缺不断更新的依据", "检索 → 核对出处和版本"],
    [344, "缺可以复算的执行", "受控工具 → 检查回执"],
    [478, "固定行为仍反复失败", "有数据和评测，再考虑微调"]
  ].flatMap(([y, a, b]) => [box(28, y, 424, 102, y === 210 ? green : paper), text(48, y + 37, a), text(48, y + 77, b)]),
  text(28, 638, "可组合；先用任务样本检验")
]);
figure("materials-to-result.svg", 686, "有依据的资料助手交付", "任务约定与材料一起进入处理，结果逐项连接原句，缺失和冲突保留，人工回查后导出。", [
  text(24, 40, "把结果交给下一个人", 28),
  box(28, 74, 424, 78), text(48, 120, "任务约定 + 带编号的材料"), arrow(240, 162, 190),
  box(28, 202, 424, 102, green), text(48, 239, "按字段整理 → 连回原句"), text(48, 279, "活动 / 时间 / 地点 / 报名"), arrow(240, 314, 342),
  box(28, 354, 424, 102), text(48, 391, "缺失：留未知；冲突：待确认"), text(48, 431, "无依据 / 范围外：停止"), arrow(240, 466, 494),
  box(28, 506, 424, 78, green), text(48, 552, "人工回查 → 导出核验报告"),
  text(28, 628, "把材料里的命令当内容"), text(28, 670, "草稿不等于已经执行报名")
]);

for (const { file, svg } of items) {
  const path = join(out, file);
  if (process.argv.includes("--check")) {
    if (readFileSync(path, "utf8") !== svg) throw new Error(`Stale figure ${file}`);
  } else writeFileSync(path, svg);
}
console.log(`${process.argv.includes("--check") ? "Verified" : "Built"} ${items.length} application figures`);
