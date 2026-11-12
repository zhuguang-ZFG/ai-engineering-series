import { readFileSync, writeFileSync } from "node:fs";
import { join, resolve } from "node:path";
import assert from "node:assert/strict";

// Course-edition art: one cover and five stage plates. Every mark is drawn
// from the same small set of paper, ink, pine and clay rules so the printed
// book, the EPUB and the website share one visual language.
const root = resolve(import.meta.dirname, "../..");
const folder = join(root, "book/assets/handdraw/llm");
const checking = process.argv.includes("--check");

const ink = "#26221B";
const soft = "#5C5448";
const paper = "#FBF7EF";
const card = "#FFFDF8";
const pine = "#26221B";
const sage = "#F3EAD8";
const clay = "#B4472F";
const sand = "#E3D8C1";
const esc = value => String(value).replace(/[&<>"']/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[c]);
const text = (x, y, value, size = 22, color = ink, anchor = "start", family = "'Noto Serif SC','Songti SC','SimSun',serif", weight = 400, spacing = 0) =>
  `<text x="${x}" y="${y}" font-family="${family}" font-size="${size}" font-weight="${weight}" fill="${color}" text-anchor="${anchor}"${spacing ? ` letter-spacing="${spacing}"` : ""}>${esc(value)}</text>`;
const line = (x1, y1, x2, y2, color = ink, width = 2, dash = "") =>
  `<path d="M${x1} ${y1} L${x2} ${y2}" fill="none" stroke="${color}" stroke-width="${width}" stroke-linecap="round"${dash ? ` stroke-dasharray="${dash}"` : ""}/>`;
const path = (d, color = ink, width = 2, fill = "none", dash = "") =>
  `<path d="${d}" fill="${fill}" stroke="${color}" stroke-width="${width}" stroke-linecap="round" stroke-linejoin="round"${dash ? ` stroke-dasharray="${dash}"` : ""}/>`;
const grain = (width, height) => `<pattern id="grain" width="22" height="22" patternUnits="userSpaceOnUse"><circle cx="2" cy="3" r=".8" fill="${ink}" opacity=".16"/><circle cx="14" cy="15" r=".7" fill="${ink}" opacity=".12"/></pattern><rect width="${width}" height="${height}" fill="url(#grain)" opacity=".28"/>`;
const frame = (width, height, inset = 26) => `<rect x="${inset}" y="${inset}" width="${width - inset * 2}" height="${height - inset * 2}" fill="none" stroke="${ink}" stroke-width="1" opacity=".22"/><path d="M${inset - 6} ${inset + 26} V${inset - 6} H${inset + 26} M${width - inset - 26} ${inset - 6} H${width - inset + 6} V${inset + 26} M${inset - 6} ${height - inset - 26} V${height - inset + 6} H${inset + 26} M${width - inset - 26} ${height - inset + 6} H${width - inset + 6} V${height - inset - 26}" fill="none" stroke="${ink}" stroke-width="1.6" opacity=".5"/>`;
const plate = (title, desc, body) => `<svg xmlns="http://www.w3.org/2000/svg" width="480" height="640" viewBox="0 0 480 640" role="img" aria-labelledby="title desc"><title id="title">${esc(title)}</title><desc id="desc">${esc(desc)}</desc><rect width="480" height="640" fill="${paper}"/>${grain(480, 640)}${frame(480, 640)}<g>${body}</g></svg>\n`;

// A thin isometric plate: top diamond plus two side faces.
function slab(cx, cy, w, h, t, fill, stroke = ink, opacity = 1) {
  const top = `M${cx - w / 2} ${cy} L${cx} ${cy - h / 2} L${cx + w / 2} ${cy} L${cx} ${cy + h / 2} Z`;
  const left = `M${cx - w / 2} ${cy} L${cx} ${cy + h / 2} L${cx} ${cy + h / 2 + t} L${cx - w / 2} ${cy + t} Z`;
  const right = `M${cx + w / 2} ${cy} L${cx} ${cy + h / 2} L${cx} ${cy + h / 2 + t} L${cx + w / 2} ${cy + t} Z`;
  return `<g opacity="${opacity}">${path(left, stroke, 1.6, fill)}${path(right, stroke, 1.6, fill)}${path(top, stroke, 1.8, fill)}</g>`;
}

function stagePlate(n, gate, title, desc, motif) {
  const label = String(n).padStart(2, "0");
  return plate(title, desc,
    `<text x="46" y="118" font-family="'Noto Serif SC','Songti SC','SimSun',serif" font-size="112" font-weight="600" fill="none" stroke="${pine}" stroke-width="1.7" letter-spacing="2">${label}</text>` +
    text(432, 74, `STAGE ${label}`, 13, soft, "end", "'Noto Serif SC','Songti SC','SimSun',serif", 500, 3) +
    text(432, 96, `K${n}`, 13, soft, "end", "ui-monospace,monospace", 500, 2) +
    line(44, 150, 436, 150, ink, 1, "2 6") +
    motif +
    text(44, 596, "五阶段 · 三十章", 15, soft, "start", "'Noto Serif SC','Songti SC','SimSun',serif", 400, 2) +
    text(436, 596, "把大模型拆开看", 15, soft, "end", "'Noto Serif SC','Songti SC','SimSun',serif", 400, 1));
}

// S1: three offset sheets, one checked claim, and a return arrow.
const s1 = stagePlate(1, "K1", "S1 · 会使用", "三张错开的纸页代表材料、报告与核对；朱砂勾只落在能回到原句的一格上，虚线箭头表示回到原文。",
  `${[0, 1, 2].map(i => `<g transform="translate(${i * 18} ${i * 26}) rotate(${i * 1.4} 200 260)"><rect x="112" y="186" width="224" height="188" rx="6" fill="${i === 2 ? card : sand}" stroke="${ink}" stroke-width="1.8" opacity="${0.66 + i * 0.17}"/>${i === 2 ? [0, 1, 2].map(r => line(140, 244 + r * 30, 300 - r * 22, 244 + r * 30, ink, 1.2, "1 7")).join("") : ""}</g>`).join("")}` +
  `<path d="M148 258 q34 10 58 -2" fill="none" stroke="${pine}" stroke-width="10" stroke-linecap="round" opacity=".55"/>` +
  path("M300 296 l16 17 l34 -44", pine, 4) +
  path("M348 356 q34 36 2 72 q-30 34 -98 18", pine, 2, "none", "6 6") +
  path("M258 442 l-10 6 l12 5", pine, 2) +
  line(50, 390, 50, 492, ink, 1, "2 6") +
  text(58, 410, "原文", 17, soft, "start", "'Noto Serif SC','Songti SC','SimSun',serif", 400, 1) +
  text(58, 446, "报告", 17, soft, "start", "'Noto Serif SC','Songti SC','SimSun',serif", 400, 1) +
  text(58, 482, "核对", 17, soft, "start", "'Noto Serif SC','Songti SC','SimSun',serif", 400, 1) +
  text(58, 530, "每一格都能回到原句", 18, ink, "start", "'Noto Serif SC','Songti SC','SimSun',serif", 500) +
  text(58, 558, "找不到，就写未知", 16, soft));

// S2: one query looking at three keys, weights as a small bar row.
const s2 = stagePlate(2, "K2", "S2 · 懂原理", "一个查询点向三个位置发出细线，线的粗细表示混合权重；右侧三条柱高按同一组权重绘制，未来位置被斜线遮住。",
  `<circle cx="116" cy="306" r="10" fill="${pine}"/>` +
  [0, 1, 2].map(i => `<g><circle cx="${282 + i * 54}" cy="306" r="9" fill="${i === 2 ? card : sage}" stroke="${ink}" stroke-width="1.8"/>${i === 2 ? path(`M${274 + i * 54} ${298} l${16} ${16} M${290 + i * 54} ${298} l-16 ${16}`, clay, 2) : ""}</g>`).join("") +
  [0.62, 0.88, 0].map((w, i) => path(`M126 300 Q${(126 + 282 + i * 54) / 2} ${268 - i * 8} ${272 + i * 54} 302`, i === 2 ? soft : pine, 1 + w * 5, "none", i === 2 ? "4 6" : "")).join("") +
  text(282, 356, "可见位置", 14, soft, "start", "'Noto Serif SC','Songti SC','SimSun',serif") +
  text(116, 356, "当前位置", 14, soft, "end", "'Noto Serif SC','Songti SC','SimSun',serif") +
  [0.33, 0.67].map((v, i) => `<rect x="${282 + i * 54}" y="${436 - v * 70}" width="26" height="${v * 70}" fill="${i === 1 ? pine : sage}" stroke="${ink}" stroke-width="1.2" opacity=".9"/>`).join("") +
  `<rect x="390" y="366" width="26" height="70" fill="${card}" stroke="${ink}" stroke-width="1.2" stroke-dasharray="4 5"/>` +
  line(272, 438, 428, 438, ink, 1.4) +
  text(295, 462, "0.33", 16, soft, "middle") + text(349, 462, "0.67", 16, soft, "middle") + text(403, 462, "0", 16, soft, "middle") +
  text(58, 500, "权重是混合比例", 18, ink, "start", "'Noto Serif SC','Songti SC','SimSun',serif", 500) +
  text(58, 528, "不是事实置信度", 16, soft));

// S3: request → checked execution → receipt, with a failure branch.
const s3 = stagePlate(3, "K3", "S3 · 能实现", "三层节点由箭头相连：模型提出请求，程序校验后执行，回执返回才允许汇报；向下的一支停在失败终态，不画成成功。",
  [0, 1, 2].map(i => `<rect x="74" y="${210 + i * 92}" width="332" height="58" rx="8" fill="${i === 1 ? sage : card}" stroke="${ink}" stroke-width="1.6"/>` +
    text(96, 245 + i * 92, ["请求：参数与意图", "校验：类型、范围、权限", "回执：结果、终态、时间"][i], 17, ink, "start", "'Noto Serif SC','Songti SC','SimSun',serif", 500)).join("") +
  [0, 1].map(i => path(`M240 ${268 + i * 92} v34 m-7 -8 l7 8 l7 -8`, pine, 2)).join("") +
  path("M406 394 q28 0 28 28 q0 26 -30 26", clay, 2) +
  path("M404 448 l10 -4 l-4 11", clay, 2) +
  text(368, 490, "失败也留终态", 15, clay, "start", "'Noto Serif SC','Songti SC','SimSun',serif", 500) +
  line(74, 528, 406, 528, ink, 1, "2 7") +
  text(74, 562, "程序接受什么，才叫完成", 18, ink, "start", "'Noto Serif SC','Songti SC','SimSun',serif", 500));

// S4: a measurement loop with a rising line and a wide interval band.
const s4 = stagePlate(4, "K4", "S4 · 会改进", "一个闭环包住前后对照：基线、改动、复测；折线只上升一小段，外面的一圈浅色带表示小样本的置信区间。",
  path("M118 350 a102 102 0 1 1 102 102", soft, 2, "none", "6 7") +
  path("M218 452 l-14 2 l8 11", soft, 2) +
  `<path d="M142 352 L316 314 L316 266 L142 304 Z" fill="${sage}" fill-opacity=".45"/>` +
  [0, 1, 2, 3].map(i => `<circle cx="${142 + i * 58}" cy="${352 - [0, 18, 14, 38][i]}" r="6" fill="${i === 3 ? pine : card}" stroke="${ink}" stroke-width="1.6"/>`).join("") +
  path("M142 352 L200 334 L258 338 L316 314", pine, 2.6) +
  line(132, 372, 340, 372, ink, 1.2) +
  text(142, 402, "基线", 14, soft) + text(300, 402, "改动", 14, soft) +
  text(58, 500, "先有同一把尺子", 18, ink, "start", "'Noto Serif SC','Songti SC','SimSun',serif", 500) +
  text(58, 528, "再谈变好", 16, soft));

// S5: a sealed package above a server, plus a rollback path to the previous seal.
const s5 = stagePlate(5, "K5", "S5 · 独立交付", "上方封好的交付包带哈希封条，下方一台服务接住它；旁边一条弧线退回上一个封条完好的包，表示回退的是整包，不是单个文件。",
  `<g transform="translate(0 -18)">${slab(236, 250, 250, 118, 17, sand)}${slab(236, 314, 250, 118, 17, sage)}${path("M114 314 l122 59 l122 -59", ink, 1.2, "none", "5 6")}</g>` +
  text(184, 274, "hash ✓", 16, pine, "start", "ui-monospace,monospace", 500) +
  text(184, 340, "manifest", 16, ink, "start", "ui-monospace,monospace", 500) +
  path("M236 414 v44 m-8 -9 l8 9 l8 -9", ink, 2) +
  `<rect x="158" y="464" width="156" height="62" rx="5" fill="${card}" stroke="${ink}" stroke-width="1.6"/>` +
  [0, 1, 2].map(i => line(178 + i * 44, 484, 202 + i * 44, 484, soft, 1.4)).join("") +
  line(178, 502, 294, 502, soft, 1.4) +
  path("M330 490 q46 8 46 -44 q0 -36 -34 -36", clay, 2, "none", "6 6") +
  path("M348 402 l-8 8 l10 6", clay, 2) +
  text(118, 572, "回退整包，不是单个文件", 18, ink, "start", "'Noto Serif SC','Songti SC','SimSun',serif", 500));

const stageFiles = [
  ["stage-1.svg", s1],
  ["stage-2.svg", s2],
  ["stage-3.svg", s3],
  ["stage-4.svg", s4],
  ["stage-5.svg", s5]
];

// Full-page reading map: five horizontal stage lines, 30 chapter dots and one
// gate diamond per stage. It is a navigation plate, not a replacement for the
// chapter list or the stage introductions.
function mapArt() {
  const stages = [
    { id: "S1", title: "会使用", gate: "K1", chapters: [1, 4], y: 310, note: "带原文依据的报告" },
    { id: "S2", title: "懂原理", gate: "K2", chapters: [5, 10], y: 550, note: "能手算的生成与注意力" },
    { id: "S3", title: "能实现", gate: "K3", chapters: [11, 17], y: 790, note: "真实模型、检索与工具" },
    { id: "S4", title: "会改进", gate: "K4", chapters: [18, 26], y: 1030, note: "冻结评测与训练证据" },
    { id: "S5", title: "独立交付", gate: "K5", chapters: [27, 30], y: 1270, note: "别人能启动、能回退" }
  ];
  const body = stages.map(stage => {
    const count = stage.chapters[1] - stage.chapters[0] + 1;
    const startX = 348, endX = 1010, step = (endX - startX) / count;
    const chips = Array.from({ length: count }, (_, i) => {
      const number = stage.chapters[0] + i;
      const x = startX + step * (i + 0.5);
      return `<circle cx="${x}" cy="${stage.y}" r="31" fill="${card}" stroke="${ink}" stroke-width="1.8"/>` +
        text(x, stage.y + 8, `C${String(number).padStart(2, "0")}`, 25, ink, "middle", "ui-monospace,monospace", 500);
    }).join("");
    return `<g>` +
      line(340, stage.y, 1046, stage.y, ink, 1.6) +
      chips +
      line(1010, stage.y, 1046, stage.y, pine, 2.2) +
      `<path d="M1080 ${stage.y} l24 -24 l24 24 l-24 24 Z" fill="${pine}" stroke="${ink}" stroke-width="1.5"/>` +
      text(1080, stage.y + 7, stage.gate, 21, paper, "middle", "ui-monospace,monospace", 600) +
      text(96, stage.y - 34, stage.id, 30, pine, "start", "'Noto Serif SC','Songti SC','SimSun',serif", 600, 2) +
      text(156, stage.y - 30, stage.title, 38, ink, "start", "'Noto Serif SC','Songti SC','SimSun',serif", 600) +
      text(96, stage.y + 38, `阶段门 ${stage.gate}`, 19, soft, "start", "'Noto Serif SC','Songti SC','SimSun',serif", 400, 1) +
      text(96, stage.y + 70, stage.note, 24, ink, "start", "'Noto Serif SC','Songti SC','SimSun',serif", 400, 1) +
      `</g>`;
  }).join("");
  return `<svg xmlns="http://www.w3.org/2000/svg" width="1240" height="1754" viewBox="0 0 1240 1754" role="img" aria-labelledby="title desc">
<title id="title">全书地图：五阶段三十章</title><desc id="desc">五条水平阶段线，从 S1 会使用到 S5 独立交付；每条线上的圆点是一章，右侧菱形是能力门。S1 含 C01 至 C04，S2 含 C05 至 C10，S3 含 C11 至 C17，S4 含 C18 至 C26，S5 含 C27 至 C30。</desc>
<rect width="1240" height="1754" fill="${paper}"/>${grain(1240, 1754)}${frame(1240, 1754, 54)}
${text(96, 120, "五阶段 · 三十章 · 五道能力门", 24, soft, "start", "'Noto Serif SC','Songti SC','SimSun',serif", 400, 3)}
${line(96, 156, 1144, 156, ink, 1, "2 7")}
${path("M1140 310 V1270", pine, 1.6, "none", "5 8")}
${body}
${line(96, 1440, 1144, 1440, ink, 1, "2 7")}
${text(96, 1500, "圆点：章号　菱形：能力门　虚线：阶段顺序", 24, soft, "start", "'Noto Serif SC','Songti SC','SimSun',serif", 400, 1)}
${text(96, 1556, "每一阶段的产出，是下一阶段的输入；地图只给位置，判断仍回到章节。", 26, ink, "start", "'Noto Serif SC','Songti SC','SimSun',serif", 400, 1)}
${text(1144, 1612, "实施试读版 · 2026.11", 20, soft, "end", "'Noto Serif SC','Songti SC','SimSun',serif", 400, 1)}
</svg>\n`;
}

// Cover: A5 at 150 dpi. The same isometric stack appears at a larger scale,
// with one stage lifted out of the pile to carry the "take it apart" idea.
const coverWidth = 1240;
const coverHeight = 1754;
const coverStack = [0, 1, 2, 3, 4].map(i => {
  const y = 1300 - i * 100;
  const active = i === 3;
  return slab(620, y, 600, 250, 26, active ? pine : (i % 2 ? sage : sand), ink, active ? 1 : 0.9) +
    text(430, y + 8, `${i + 1}`, 20, active ? paper : soft, "start", "ui-monospace,monospace", 500, 2) +
    text(476, y + 8, ["会使用", "懂原理", "能实现", "会改进", "独立交付"][i], 22, active ? paper : ink, "start", "'Noto Serif SC','Songti SC','SimSun',serif", active ? 600 : 400, 1);
}).join("");
const cover = `<svg xmlns="http://www.w3.org/2000/svg" width="${coverWidth}" height="${coverHeight}" viewBox="0 0 ${coverWidth} ${coverHeight}" role="img" aria-labelledby="title desc">
<title id="title">大模型：从入门到精通</title><desc id="desc">课程书封面。五阶段三十章，从一份通知到一次能复现的交付；五块薄板叠成阶梯，其中一块被抽出。</desc>
<rect width="${coverWidth}" height="${coverHeight}" fill="${paper}"/>${grain(coverWidth, coverHeight)}${frame(coverWidth, coverHeight, 54)}
${text(112, 176, "VIBE CODING 101 · 五阶段三十章", 24, soft, "start", "'Noto Serif SC','Songti SC','SimSun',serif", 400, 4)}
${text(104, 424, "大模型", 118, ink, "start", "'Noto Serif SC','Songti SC','SimSun',serif", 600, 6)}
${text(108, 556, "从入门到精通", 78, ink, "start", "'Noto Serif SC','Songti SC','SimSun',serif", 500, 6)}
<path d="M112 602 q210 -22 452 2 q152 8 258 -2" fill="none" stroke="${pine}" stroke-width="10" stroke-linecap="round" opacity=".82"/>
${text(112, 676, "把模型拆开，把结果交给别人核对", 30, soft, "start", "'Noto Serif SC','Songti SC','SimSun',serif", 400, 1)}
${path("M112 738 H1128", ink, 1, "none", "2 8")}
${coverStack}
${text(112, 1510, "会使用 · 懂原理 · 能实现 · 会改进 · 独立交付", 24, ink, "start", "'Noto Serif SC','Songti SC','SimSun',serif", 400, 2)}
${path("M112 1560 H1128", ink, 1, "none", "2 8")}
${text(112, 1632, "实施试读版 1.1.2 · 2026.11", 21, soft, "start", "'Noto Serif SC','Songti SC','SimSun',serif", 400, 1)}
${text(1128, 1632, "课程原创图解", 21, soft, "end", "'Noto Serif SC','Songti SC','SimSun',serif", 400, 1)}
</svg>\n`;

for (const [file, body] of [...stageFiles, ["cover-course.svg", cover], ["book-map.svg", mapArt()]]) {
  const target = join(folder, file);
  if (checking) assert.equal(readFileSync(target, "utf8").replaceAll("\r\n", "\n"), body, `${file} is stale`);
  else writeFileSync(target, body);
}
console.log(`${checking ? "Verified" : "Built"} cover, ${stageFiles.length} stage plates and the book map`);
