import { readFileSync } from "node:fs";
import api from "./core.cjs";
import { multihead } from "../../book/llm/examples/multihead.mjs";

// Publication drawings: exact data geometry, restrained hand-drawn contours.
// Labels stay editable; all four compositions fit the existing 480 × 640 page.
const ink = "#1f2328", soft = "#57606a", paper = "#fbfaf6";
const green = "#1f883d", wash = "#d3efd9", rule = "#e6e1d4";
const esc = value => String(value).replace(/[&<>"']/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[c]);
const t = (x, y, label, size = 26, anchor = "start", color = ink) => `<text x="${x}" y="${y}" font-size="${size}" text-anchor="${anchor}" fill="${color}">${esc(label)}</text>`;
const p = (d, color = ink, width = 2.5, fill = "none", dash = "") => `<path d="${d}" fill="${fill}" stroke="${color}" stroke-width="${width}" stroke-linecap="round" stroke-linejoin="round"${dash ? ` stroke-dasharray="${dash}"` : ""}/>`;
const rect = (x, y, w, h, fill) => `<rect x="${x}" y="${y}" width="${w}" height="${h}" fill="${fill}"/>`;
const panel = (x, y, w, h, fill = paper) => p(`M${x + 3} ${y + 1} Q${x + w / 2} ${y - 2} ${x + w} ${y + 2} L${x + w - 1} ${y + h - 1} Q${x + w / 2} ${y + h + 2} ${x} ${y + h - 2}Z`, ink, 2, fill);
const arrow = (d, color = green) => p(d, color, 2.8);
const down = (x, y1, y2, color = green) => arrow(`M${x} ${y1} Q${x - 1.5} ${(y1 + y2) / 2} ${x} ${y2} M${x - 6} ${y2 - 8} L${x} ${y2} L${x + 6} ${y2 - 8}`, color);
const plus = (x, y) => `<circle cx="${x}" cy="${y}" r="17" fill="${paper}" stroke="${ink}" stroke-width="2.5"/>` + p(`M${x - 7} ${y} H${x + 7} M${x} ${y - 7} V${y + 7}`, ink, 2.5);
const f = value => value.toFixed(4).replace("-", "−");
// Teaching animation: a green outline tours the steps in a loop. The base
// drawing stays fully visible (SMIL only adds the highlight), so print, EPUB
// and SMIL-less readers keep the complete static figure.
export function stepTour(steps, stepDur = 2.6) {
  const dur = steps.length * stepDur;
  return `<g pointer-events="none">${steps.map(([x, y, w, h], i) =>
    `<rect x="${x}" y="${y}" width="${w}" height="${h}" rx="10" fill="none" stroke="${green}" stroke-width="4" opacity="0"><animate attributeName="opacity" values="0;0.85;0.85;0" keyTimes="0;0.12;0.8;1" dur="${dur}s" begin="${(i * stepDur).toFixed(2)}s" repeatCount="indefinite"/></rect>`
  ).join("")}</g>`;
}
function frame(title, desc, body) {
  return `<svg xmlns="http://www.w3.org/2000/svg" width="480" height="640" viewBox="0 0 480 640" role="img" aria-labelledby="title desc"><title id="title">${esc(title)}</title><desc id="desc">${esc(desc)}</desc><rect width="480" height="640" fill="${paper}"/><g font-family="Microsoft YaHei,sans-serif">${t(28, 43, title, 30)}${p("M28 59 Q132 55 226 59", green, 4)}${body}${p("M28 583 Q240 581 452 583", rule, 1.5)}</g></svg>\n`;
}

// Same unit-projection example as C07, distinct from the legacy L04 fixture.
const X = [[1, 0], [0, 1], [1, 1]];
const attention = api.attention(X, X, X, 1);
export function attentionRowArt() {
  const columns = [92, 240, 388];
  return frame("一行注意力，算到输出", "C07人工单位投影：当前位置1，q=[0,1]，d_k=2。缩放后分数0与0.7071，未来位置被遮住。权重0.3302、0.6698、0，乘V后输出[0.3302,0.6698]。条高按未舍入权重绘制。",
    t(28, 96, "位置 1：q = [0, 1]，dₖ = 2", 26) +
    columns.map((x, i) => t(x, 143, `位置 ${i}`, 25, "middle") + t(x, 181, `[${X[i].join(", ")}]`, 26, "middle")).join("") +
    t(28, 218, "q·k / √2", 24, "start", soft) +
    panel(326, 231, 124, 49, rule) +
    t(92, 265, "0", 30, "middle") + t(240, 265, f(attention.scores[1]), 30, "middle") + t(388, 265, "−∞", 30, "middle") +
    t(240, 306, "先遮未来，再 softmax", 27, "middle") +
    columns.map((x, i) => {
      const height = attention.weights[i] * 80;
      return rect(x - 48, 415 - height, 96, height, i === 1 ? wash : rule) +
        p(`M${x - 49} 415 H${x + 49}`, ink, 2) +
        t(x, 405 - height, i === 2 ? "0" : f(attention.weights[i]), 28, "middle");
    }).join("") +
    t(92, 451, "× [1, 0]", 25, "middle") + t(240, 451, "× [0, 1]", 25, "middle") + t(388, 451, "× [1, 1]", 25, "middle") +
    p("M92 465 V482 H240 M388 465 V482 H240", ink, 2) + down(240, 482, 502) +
    panel(44, 517, 392, 46, wash) + t(240, 549, `= [${attention.output.map(f).join(", ")}]`, 30, "middle") +
    t(28, 618, "权重是混合比例，不是事实置信度", 24));
}

export function multiheadArt() {
  const fixture = JSON.parse(readFileSync(new URL("../../book/llm/fixtures/multihead.json", import.meta.url), "utf8"));
  const result = multihead(fixture.input, fixture.heads, fixture.WO, fixture.position);
  return frame("两条支路，拼接后再混合", "D14人工双头矩阵：位置1只看位置0与1。头1取第一维，权重0.5/0.5，输出0.5；头2取第二维，权重0.2689/0.7311，输出0.7311。拼接后乘WO，输出[1.2311,-0.2311]。条长按实际权重绘制。",
    t(240, 99, "X → 两组独立的 Q / K / V", 27, "middle") +
    p("M240 113 V130 M120 148 V130 H360 V148", ink, 2.3) +
    result.heads.map((head, i) => {
      const x = 120 + i * 240;
      const left = x - 90, first = head.weights[0] * 180;
      return t(x, 184, `头 ${i + 1}`, 28, "middle") +
        t(x, 221, `投影取第${i === 0 ? "一" : "二"}维`, 25, "middle") +
        rect(left, 240, first, 25, rule) + rect(left + first, 240, 180 - first, 25, wash) +
        t(x, 299, head.weights.slice(0, 2).map(value => value.toFixed(3)).join(" / "), 25, "middle") +
        down(x, 313, 337) + t(x, 373, f(head.output[0]), 34, "middle") +
        down(x, 386, 408, ink);
    }).join("") +
    panel(28, 421, 212, 48, rule) + panel(240, 421, 212, 48, wash) +
    t(134, 455, f(result.concatenated[0]), 29, "middle") + t(346, 455, f(result.concatenated[1]), 29, "middle") +
    t(240, 510, "拼接 1×2 → 乘 Wᴼ（2×2）", 25, "middle") +
    t(240, 555, `[${result.output.map(f).join(", ")}]`, 31, "middle") +
    t(28, 618, "未来位置 2 遮住；仅演示两个头", 24));
}

export function transformerBlockArt() {
  const block = (y, label) => panel(176, y, 270, 38, wash) + t(311, y + 28, label, 26, "middle");
  return frame("残差：保留一路，再相加", "一种pre-norm块。输入x先分出旁路，再归一化并经过因果多头注意力，输出与x相加得到h。h再分出旁路，经归一化与逐位置前馈后，与h相加得到块输出。位置机制依架构接入，本图未展开。",
    t(28, 96, "一种 pre-norm 块 · 先归一化", 25) +
    t(311, 132, "输入 x", 27, "middle") +
    p("M311 147 H105 V310 H290 M282 304 L290 310 L282 316", ink, 2.5) +
    down(311, 145, 161) + block(171, "归一化") + down(311, 216, 235) +
    block(245, "因果多头注意力") + down(311, 286, 292) + plus(311, 310) +
    t(30, 231, "保留 x", 25) +
    down(311, 329, 366) + t(350, 353, "h", 27) +
    p("M311 344 H105 V517 H290 M282 511 L290 517 L282 523", ink, 2.5) +
    block(376, "归一化") + down(311, 420, 439) + block(449, "逐位置前馈") +
    down(311, 490, 499) + plus(311, 517) +
    t(30, 436, "保留 h", 25) + down(311, 537, 550) + t(311, 576, "块输出", 27, "middle") +
    t(28, 618, "旁路带回的是子层输入的向量", 24));
}

export function gradientStepArt() {
  const initial = api.probabilities([0, 0], 1);
  const gradients = initial.map((value, i) => value - (i === 0 ? 1 : 0));
  const scores = gradients.map(value => -0.4 * value);
  const after = api.probabilities(scores, 1);
  const distribution = (y, values) => {
    const first = values[0] * 424;
    return rect(28, y, first, 36, wash) + rect(28 + first, y, 424 - first, 36, rule) +
      p(`M28 ${y + 37} H452 M${28 + first} ${y - 3} V${y + 40}`, ink, 2) +
      t(28, y + 70, `水 ${(values[0] * 100).toFixed(1)}%`, 27) +
      t(452, y + 70, `茶 ${(values[1] * 100).toFixed(1)}%`, 27, "end");
  };
  return frame("减去梯度，分数怎样移动", "人工两候选例子：目标水，学习率0.4。初始概率各50%；梯度为-0.5与+0.5；新分数0.2与-0.2，概率59.9%与40.1%，交叉熵从0.693降到0.513。前后条长使用相同总宽度与实际概率。",
    t(28, 96, "目标：水（1）/ 茶（0）", 26) +
    t(28, 139, "更新前 · 分数 [0, 0]", 26) + distribution(156, initial) +
    t(240, 276, "梯度 = 概率 − 目标", 27, "middle") +
    t(120, 322, "−0.5", 34, "middle") + t(360, 322, "+0.5", 34, "middle") +
    down(120, 338, 363) + down(360, 338, 363) +
    t(240, 399, "新分数 = 0 − 0.4 × 梯度", 27, "middle") +
    t(28, 444, "更新后 · 分数 [0.2, −0.2]", 26) + distribution(461, after) +
    t(240, 571, `损失 ${(-Math.log(initial[0])).toFixed(3)} → ${(-Math.log(after[0])).toFixed(3)}`, 29, "middle") +
    t(28, 618, "一步更像训练目标，仍需留出评测", 24) +
    stepTour([[24, 129, 432, 101], [24, 264, 432, 106], [24, 434, 432, 101], [24, 553, 432, 43]], 2.2));
}
