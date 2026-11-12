// Seven drawings for the shared running example (周六 下午 两点 在 图书馆 报名).
// Every number below is copied from specs/llm-running-example.md; the art test
// re-reads that file so a silent drift fails the suite instead of the reader.
// Drawing language follows the series volumes: one warm ink scale, hairline
// rules, cinnabar reserved for the single highlighted relation, no plate.
const ink = "#26221B", soft = "#5C5448", rule = "#E3D8C1", wash = "#F3EAD8", accent = "#B4472F", card = "#FFFDF8";
const esc = value => String(value).replace(/[&<>"']/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[c]);

const t = (x, y, label, size = 24, anchor = "start", color = ink, weight = 400) =>
  `<text x="${x}" y="${y}" font-size="${size}" text-anchor="${anchor}" fill="${color}" font-weight="${weight}">${esc(label)}</text>`;
const line = (d, color = ink, width = 1.6, dash = "") =>
  `<path d="${d}" fill="none" stroke="${color}" stroke-width="${width}" stroke-linecap="round" stroke-linejoin="round"${dash ? ` stroke-dasharray="${dash}"` : ""}/>`;
const solid = (d, color = rule) => `<path d="${d}" fill="${color}" stroke="none"/>`;
const down = (x, y1, y2) => line(`M${x} ${y1}V${y2}M${x - 5} ${y2 - 7}L${x} ${y2}L${x + 5} ${y2 - 7}`, accent, 1.8);
const minus = value => String(value).replace("-", "−");
const num = (value, digits = 4) => minus(Number(value).toFixed(digits));
const vec = (values, digits = 4) => `[${values.map(value => num(value, digits)).join(", ")}]`;

function canvas(title, desc, height, body) {
  return `<svg xmlns="http://www.w3.org/2000/svg" width="480" height="${height}" viewBox="0 0 480 ${height}" role="img" aria-labelledby="title desc"><title id="title">${esc(title)}</title><desc id="desc">${esc(desc)}</desc><g font-family="'Noto Serif SC','Source Han Serif SC','Songti SC','SimSun',serif" fill="${ink}">${t(26, 42, title, 28, "start", ink, 600)}${line("M26 56Q140 53 250 56", accent, 3)}${body}</g></svg>\n`;
}

// ---------- G01 一条主线，六个问题 ----------
const chain = [
  ["C05", "六片文字，先查成六个编号", "4102 2871 5530 2701 6984 3650"],
  ["C06", "编号查表，变成四维向量", "[0.6, −0.2, 0.2, 0.2] 等六条"],
  ["C07", "每个位置算一行注意力权重", "0.2766 0.1184 0.0288 0.4870 0.0892"],
  ["C08", "汇总后归一化，再过前馈", "y = [−1.3285, 3.1419, 0.4850, −0.4850]"],
  ["C08", "输出头给出三个候选的分数", "1.9336 / −0.0126 / 0.3268"],
  ["C10", "softmax 与采样选出下一片", "0.7444 / 0.1063 / 0.1493 → 报名"]
];
export function mainlineChainArt() {
  const rows = chain.map(([tag, claim, value], index) => {
    const y = 96 + index * 122;
    return line(`M26 ${y}H454`, rule, 1.2) +
      t(26, y + 30, tag, 21, "start", accent, 600) +
      t(82, y + 30, claim, 23) +
      t(82, y + 70, value, 21, "start", soft) +
      (index < chain.length - 1 ? down(240, y + 82, y + 108) : "");
  }).join("");
  return canvas("一条主线，六个问题",
    "同一句话走完六步：编号、向量、注意力权重、归一化与前馈、三个候选分数、softmax 采样；每一步的输出就是下一步的输入，图上的数字全部来自同一组人工算例。",
    860, rows +
    line("M26 828H454", rule, 1.2) +
    t(26, 852, "换掉的只有问题，数字一直是同一组", 21, "start", soft));
}

// ---------- G02 温度只改形状，不改排序 ----------
const temperature = [
  ["T = 2", { "报名": 0.5477, "两点": 0.2453, "签到": 0.2070 }],
  ["T = 1", { "报名": 0.7444, "两点": 0.1493, "签到": 0.1063 }],
  ["T = 0.5", { "报名": 0.9429, "两点": 0.0379, "签到": 0.0192 }],
  ["T = 0.2", { "报名": 0.999617, "两点": 0.000324, "签到": 0.000059 }]
];
export function temperatureLadderArt() {
  const rows = temperature.map(([label, distribution], index) => {
    const y = 92 + index * 152;
    const bars = ["报名", "两点", "签到"].map((name, order) => {
      const value = distribution[name];
      const width = Math.max(2, value * 268);
      const by = y + 22 + order * 30;
      const color = name === "报名" ? accent : name === "两点" ? ink : soft;
      const digits = value < 0.001 ? 6 : 4;
      return solid(`M118 ${by}H${118 + width}V${by + 20}H118Z`, color) +
        t(126 + width, by + 17, num(value, digits), 20, "start", soft);
    }).join("");
    return t(26, y + 16, label, 25, "start", ink, 600) +
      t(26, y + 46, "报名", 19, "start", soft) + t(26, y + 76, "两点", 19, "start", soft) + t(26, y + 106, "签到", 19, "start", soft) +
      bars;
  }).join("");
  return canvas("温度只改形状，不改排序",
    "同一组三个候选分数在四个温度下的概率：报名始终第一，两点第二，签到第三；温度越低分布越尖，越高越平。条形长度按概率比例绘制，数值取四位或六位小数。",
    748, rows +
    line("M26 706H454", rule, 1.2) +
    t(26, 730, "名次四次都相同；温度只改差距，不改排序", 21, "start", soft));
}

// ---------- G03 余弦只回答方向像不像 ----------
const angles = [
  ["图书馆 · 报名", 0.3273, 70.9, 12],
  ["下午 · 两点", 0.0000, 90.0, 20],
  ["周六 · 图书馆", -0.3333, 109.5, 8]
];
export function cosineAnglesArt() {
  const rows = angles.map(([pair, cosine, degrees, start], index) => {
    const cx = 96, cy = 132 + index * 176, r = 54;
    const point = degree => [cx + r * Math.cos(degree * Math.PI / 180), cy - r * Math.sin(degree * Math.PI / 180)];
    const [ax, ay] = point(start), [bx, by] = point(start + degrees);
    const arc = line(`M${cx + 20 * Math.cos(start * Math.PI / 180)} ${cy - 20 * Math.sin(start * Math.PI / 180)}A20 20 0 ${degrees > 180 ? 1 : 0} 0 ${cx + 20 * Math.cos((start + degrees) * Math.PI / 180)} ${cy - 20 * Math.sin((start + degrees) * Math.PI / 180)}`, soft, 1.2);
    return line(`M${cx - r - 10} ${cy}a${r + 10} ${r + 10} 0 1 1 ${(r + 10) * 2} 0a${r + 10} ${r + 10} 0 1 1 ${-(r + 10) * 2} 0`, rule, 1.2) +
      line(`M${cx} ${cy}L${ax} ${ay}M${cx} ${cy}L${bx} ${by}`, ink, 2) +
      line(`M${ax - 6} ${ay - 2}L${ax} ${ay}L${ax - 1} ${ay + 7}`, ink, 2) +
      line(`M${bx - 6} ${by - 2}L${bx} ${by}L${bx - 1} ${by + 7}`, accent, 2) +
      line(`M${cx} ${cy}L${bx} ${by}`, accent, 2) +
      arc + `<circle cx="${cx}" cy="${cy}" r="2.5" fill="${ink}"/>` +
      t(196, cy - 30, pair, 23, "start", ink, 600) +
      t(196, cy + 2, `cos = ${num(cosine, 4)}`, 23, "start", accent) +
      t(196, cy + 34, `夹角 ≈ ${num(degrees, 1)}°`, 21, "start", soft);
  }).join("");
  return canvas("余弦只回答方向像不像",
    "三对四维向量的夹角与余弦：图书馆与报名约 70.9 度、余弦 0.3273；下午与两点正交、余弦 0；周六与图书馆钝角、余弦 −0.3333。余弦把长度除了出去，只比较方向。",
    704, rows +
    line("M26 662H454", rule, 1.2) +
    t(26, 686, "长度差别在点积里，不在余弦里", 21, "start", soft));
}

// ---------- G04 五行权重，一行一算 ----------
const weightRows = [
  ["周六", [1.0, null, null, null, null]],
  ["下午", [0.5702, 0.4298, null, null, null]],
  ["两点", [0.4085, 0.3167, 0.2749, null, null]],
  ["在", [0.2612, 0.1860, 0.1860, 0.3668, null]],
  ["图书馆", [0.2766, 0.1184, 0.0288, 0.4870, 0.0892]]
];
export function attentionMatrixArt() {
  const names = ["周六", "下午", "两点", "在", "图书馆"];
  const cell = 56, x0 = 124, y0 = 116;
  const headers = names.map((name, index) => t(x0 + index * cell + cell / 2, y0 - 12, name, 19, "middle", soft)).join("");
  const labels = weightRows.map(([name], index) => t(x0 - 14, y0 + index * cell + cell / 2 + 7, name, 20, "end")).join("");
  const cells = weightRows.map(([, weights], row) => weights.map((weight, column) => {
    const x = x0 + column * cell, y = y0 + row * cell;
    if (weight === null) {
      return solid(`M${x} ${y}H${x + cell}V${y + cell}H${x}Z`, card) +
        line(`M${x} ${y}H${x + cell}V${y + cell}H${x}Z`, rule, 1) +
        line(`M${x + 5} ${y + cell - 5}L${x + cell - 5} ${y + 5}`, rule, 1.2);
    }
    return solid(`M${x} ${y}H${x + cell}V${y + cell}H${x}Z`, card) +
      solid(`M${x} ${y}H${x + cell}V${y + cell}H${x}Z`, accent).replace("/>", ` fill-opacity="${(0.08 + weight * 0.62).toFixed(2)}"/>`) +
      line(`M${x} ${y}H${x + cell}V${y + cell}H${x}Z`, weight >= 0.4870 ? accent : rule, weight >= 0.4870 ? 1.8 : 1);
  }).join("")).join("");
  const last = weightRows[4][1];
  return canvas("五行权重，一行一算",
    "五个位置的因果注意力权重矩阵：行是计算位置，列是被看位置，斜线格表示未来被遮住。最后一行图书馆的五个权重是 0.2766、0.1184、0.0288、0.4870、0.0892，和为一。颜色越深权重越大。",
    764, headers + labels + cells +
    line(`M${x0} ${y0}H${x0 + 5 * cell}V${y0 + 5 * cell}H${x0}Z`, ink, 1.6) +
    t(26, 486, "图书馆那一行", 23, "start", ink, 600) +
    names.map((name, index) => t(26, 522 + index * 30, `${name}  ${num(last[index], 4)}`, 21, "start", index === 3 ? accent : soft)).join("") +
    t(26, 522 + 5 * 30 + 8, "五项之和 = 1.0000", 21, "start", accent) +
    line("M26 714H454", rule, 1.2) +
    t(26, 738, "斜线格不是零权重，是没有这个位置可看", 21, "start", soft));
}

// ---------- G05 一个位置走完一个块 ----------
const block = [
  ["h", "注意力输出加残差", vec([0.1723, 0.7584, 0.5723, 0.3584])],
  ["LayerNorm", "mean 0.4654 · sd 0.2206", vec([-1.3285, 1.3285, 0.4850, -0.4850])],
  ["W1 → ReLU", "两个负项被门掉", vec([0, 1.8134, 0, 0])],
  ["W2 + 残差", "前馈只动本位置", vec([-1.3285, 3.1419, 0.4850, -0.4850])],
  ["W_U → softmax", "三个候选的分数", "0.7444 / 0.1063 / 0.1493"]
];
export function blockNumericFlowArt() {
  const rows = block.map(([stage, note, value], index) => {
    const y = 92 + index * 128;
    return solid(`M26 ${y}H454V${y + 104}H26Z`, index === 4 ? wash : card) +
      line(`M26 ${y}H454V${y + 104}H26Z`, rule, 1) +
      t(40, y + 32, stage, 22, "start", index === 4 ? accent : ink, 600) +
      t(40, y + 60, note, 19, "start", soft) +
      t(40, y + 90, value, 20) +
      (index < block.length - 1 ? down(240, y + 108, y + 124) : "");
  }).join("");
  return canvas("一个位置走完一个块",
    "图书馆位置的完整数值流水：h 经 LayerNorm 到 ln，经 W1 与 ReLU 只剩第二维，加残差得到 y，再由输出头得到三个分数。去掉 LayerNorm 时 y 变成 0.1723、1.1584、1.5031、1.2891，概率转为 0.3501、0.3803、0.2696，签到反超。",
    852, rows +
    line("M26 772H454", rule, 1.2) +
    t(26, 796, "去掉 LayerNorm", 21, "start", accent, 600) +
    t(26, 824, "0.3501 / 0.3803 / 0.2696，第一名从报名换成签到", 20, "start", soft));
}

// ---------- G06 一步更新，损失降一点 ----------
// lr = 0.05 has all four steps published; the two larger rates only publish
// step 1 and step 4, so they stay dots — no line may imply an interpolation.
const descent = {
  "0.05": [0.2952, 0.2578, 0.2282, 0.2042, 0.1845],
  "0.2": { 1: 0.1697, 4: 0.0751 },
  "0.5": { 1: 0.0705, 4: 0.0291 }
};
export function lossDescentArt() {
  const left = 104, right = 386, base = 508, top = 148, span = 0.32;
  const x = step => left + (right - left) * step / 4;
  const y = value => base - (base - top) * value / span;
  const grid = [0.30, 0.20, 0.10, 0.00].map(value =>
    line(`M${left} ${y(value)}H${right}`, value === 0 ? ink : rule, value === 0 ? 1.4 : 1) +
    t(left - 10, y(value) + 6, value.toFixed(2), 19, "end", soft)).join("");
  const steps = [0, 1, 2, 3, 4].map(step =>
    t(x(step), base + 26, String(step), 19, "middle", soft)).join("");
  const main = descent["0.05"].map((value, step) => `${x(step)} ${y(value)}`).join(" L");
  const mainLine = line(`M${main}`, ink, 2.2) +
    descent["0.05"].map((value, step) => `<circle cx="${x(step)}" cy="${y(value)}" r="3.6" fill="${ink}"/>`).join("") +
    [0, 2, 4].map(step => t(x(step) + 6, y(descent["0.05"][step]) + (step === 4 ? -12 : 20), num(descent["0.05"][step], 4), 19, "start", ink)).join("");
  const dots = Object.entries(descent).slice(1).map(([rate, points]) => Object.entries(points).map(([step, value]) =>
    `<circle cx="${x(Number(step))}" cy="${y(value)}" r="4.2" fill="${card}" stroke="${rate === "0.2" ? accent : soft}" stroke-width="2"/>` +
    t(x(Number(step)) + 8, y(value) + 6, num(value, 4), 18, "start", rate === "0.2" ? accent : soft)).join("")).join("");
  return canvas("一步更新，损失降一点",
    "起点损失 0.2952。学习率 0.05 的四个步骤全部有数，连成一条线：0.2578、0.2282、0.2042、0.1845。学习率 0.2 与 0.5 只公布第 1 步和第 4 步，因此画成孤立的点，不连线。",
    660, grid + steps +
    line(`M${left} 132V${base}`, ink, 1.4) +
    t(left - 10, 124, "损失", 19, "end", soft) + t(454, 124, "步数", 19, "end", soft) +
    mainLine + dots +
    t(26, 574, "实线 lr = 0.05：四步都有数", 20, "start", ink) +
    t(26, 604, "圆点 lr = 0.2（朱）与 lr = 0.5（灰）：只标第 1、4 步", 19, "start", soft) +
    t(26, 634, "两点之间不连线，中间步未列出", 19, "start", soft));
}

// ---------- G07 四种手段，四种持久性 ----------
const levers = [
  ["改输入", "换提示词、贴资料、改聊天模板", "本次有效，重开就没了"],
  ["改参数", "训练一步、微调一批数据", "写进权重，换设备还在"],
  ["改解码", "调温度、改 top-p、换采样", "分布不变，只改怎么选"],
  ["加外部状态", "检索、缓存、工具返回", "不改参数，资料换了答案跟着换"]
];
export function fourLeversArt() {
  const rows = levers.map(([name, example, verdict], index) => {
    const y = 92 + index * 148;
    return line(`M26 ${y}H454`, rule, 1.2) +
      t(26, y + 34, name, 24, "start", index === 1 ? accent : ink, 600) +
      t(26, y + 68, example, 20, "start", soft) +
      t(26, y + 102, verdict, 20, "start", index === 1 ? accent : ink);
  }).join("");
  return canvas("四种手段，四种持久性",
    "同一个效果的四种来源：改输入只在本次生效，改参数写进权重，改解码只改选择方式，加外部状态不碰参数。判据是关掉哪一层之后效果还在不在。",
    716, rows +
    line("M26 676H454", rule, 1.2) +
    t(26, 700, "四种可叠加；看关掉哪一个后还剩什么", 20, "start", soft));
}

export const mainlineArtworks = [
  ["guide-mainline-chain.svg", mainlineChainArt()],
  ["c05-temperature-ladder.svg", temperatureLadderArt()],
  ["c06-cosine-angles.svg", cosineAnglesArt()],
  ["c07-attention-matrix.svg", attentionMatrixArt()],
  ["c08-block-numeric-flow.svg", blockNumericFlowArt()],
  ["c09-loss-descent.svg", lossDescentArt()],
  ["c10-four-levers.svg", fourLeversArt()]
];
