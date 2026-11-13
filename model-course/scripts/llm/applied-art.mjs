// Three drawings for the applied chapters (C18 evaluation, C28 system choice,
// C30 capstone rubric). Every number is copied from the chapter that hosts the
// picture; applied-art.test.js re-reads those chapters so a silent drift fails
// the suite instead of the reader. Language matches the rest of the series:
// one warm ink scale, hairline rules, cinnabar only for the highlighted relation.
const ink = "#26221B", soft = "#5C5448", rule = "#E3D8C1", wash = "#F3EAD8", accent = "#B4472F", card = "#FFFDF8";
const esc = value => String(value).replace(/[&<>"']/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[c]);

const t = (x, y, label, size = 22, anchor = "start", color = ink, weight = 400) =>
  `<text x="${x}" y="${y}" font-size="${size}" text-anchor="${anchor}" fill="${color}" font-weight="${weight}">${esc(label)}</text>`;
const line = (d, color = ink, width = 1.6, dash = "") =>
  `<path d="${d}" fill="none" stroke="${color}" stroke-width="${width}" stroke-linecap="round" stroke-linejoin="round"${dash ? ` stroke-dasharray="${dash}"` : ""}/>`;
const band = (x, y, width, height, fill, stroke = "none", strokeWidth = 0, dash = "") =>
  `<rect x="${x}" y="${y}" width="${width}" height="${height}" fill="${fill}" stroke="${stroke}" stroke-width="${strokeWidth}"${dash ? ` stroke-dasharray="${dash}"` : ""}/>`;

function canvas(title, desc, height, body) {
  return `<svg xmlns="http://www.w3.org/2000/svg" width="480" height="${height}" viewBox="0 0 480 ${height}" role="img" aria-labelledby="title desc"><title id="title">${esc(title)}</title><desc id="desc">${esc(desc)}</desc><g font-family="'Noto Serif SC','Source Han Serif SC','Songti SC','SimSun',serif" fill="${ink}">${t(26, 42, title, 26, "start", ink, 600)}${line("M26 56Q140 53 250 56", accent, 3)}${body}</g></svg>\n`;
}

// ---------- A18 命中率 100%，召回却只有三分之一 ----------
const queries = [
  ["查询 Q1", "相关 A, B, C", "取回 A, D, E", "1/3", "1/3", "1"],
  ["查询 Q2", "相关 D, E", "取回 D, E", "1", "1", "1"]
];
export function retrievalDenominatorsArt() {
  const columns = queries.map(([name, relevant, taken, precision, recall, hit], index) => {
    const x = index === 0 ? 26 : 248;
    const base = 108;
    return t(x, base, name, 22, "start", ink, 600) +
      line(`M${x} ${base + 12}H${x + 204}`, rule, 1.2) +
      t(x, base + 46, relevant, 20, "start", soft) +
      t(x, base + 80, taken, 20, "start", soft) +
      t(x, base + 122, `精确率 ${precision}`, 20, "start", ink) +
      t(x, base + 156, `召回率 ${recall}`, 20, "start", ink) +
      t(x, base + 190, `命中 ${hit}`, 20, "start", index === 0 ? accent : ink);
  }).join("");

  return canvas("命中率 100%，召回却只有三分之一",
    "两个查询都至少取回一个相关片段，所以命中率是 1.0；但 Q1 只取回三块相关片段中的一块，精确率与召回率都是 1/3。微平均先把两列合计再相除，宏平均先算每列再平均，两者给出不同的数。",
    700, columns +
    line("M26 322H454", rule, 1.2) +
    t(26, 360, "微平均：合计数再相除", 22, "start", ink, 600) +
    t(26, 392, "精确率 3/5 = 0.600　召回率 3/5 = 0.600", 21, "start", soft) +
    line("M26 418H454", rule, 1.2) +
    t(26, 456, "宏平均：先算每列再平均", 22, "start", ink, 600) +
    t(26, 488, "精确率 (1/3 + 1)/2 ≈ 0.667", 21, "start", soft) +
    t(26, 520, "召回率 (1/3 + 1)/2 ≈ 0.667", 21, "start", soft) +
    line("M26 546H454", rule, 1.2) +
    t(26, 584, "命中率 2/2 = 1.000，但 Q1 只取回三分之一", 21, "start", accent) +
    t(26, 616, "缺页仍是失败，只是命中了别的片段", 20, "start", soft) +
    t(26, 672, "三个数一起给，并写明是微平均还是宏平均", 20, "start", soft));
}

// ---------- A28 整本手册放不放进 32k 窗口 ----------
const scale = value => 60 + value / 60000 * 380; // 0..60 000 → 60..440 px
export function contextBudgetArt() {
  const windowRight = scale(32768);
  const wholeLow = scale(28800), wholeHigh = scale(57600);
  const reserveLow = scale(32768 - 4000), reserveHigh = scale(32768 - 2000);
  const ticks = [0, 20000, 40000, 60000].map(value =>
    line(`M${scale(value)} 286V296`, ink, 1.4) + t(scale(value), 320, String(value).replace(/(\d)(\d{3})$/, "$1 $2"), 19, "middle", soft)).join("");

  return canvas("整本手册，塞不进 32k 窗口",
    "96 页、每页约 500 字符，合计约 48 000 字符；按 0.6 到 1.2 token/字符估，整本约 28 800 到 57 600 token。上界已越过 32 768 的上下文窗口，还要留 2 000 到 4 000 给问题与输出。",
    620,
    t(26, 96, "整本手册放进提示", 22, "start", ink, 600) +
    band(wholeLow, 112, wholeHigh - wholeLow, 40, "none", accent, 1.8) +
    band(windowRight, 112, wholeHigh - windowRight, 40, accent, "none", 0) +
    t(wholeLow + 6, 106, "28 800", 19, "start", accent) +
    t(wholeHigh, 106, "57 600", 19, "end", accent) +
    t((windowRight + wholeHigh) / 2, 176, "超出部分被截断", 19, "middle", accent) +

    t(26, 214, "上下文窗口", 22, "start", ink, 600) +
    band(60, 226, windowRight - 60, 38, wash, rule, 1.2) +
    t(66, 252, "32 768", 20, "start", ink, 600) +
    line(`M${windowRight} 218V272`, accent, 1.6, "5 5") +
    t(windowRight + 6, 218, "上界", 18, "start", accent) +

    line("M60 286H440", rule, 1.2) +
    ticks +

    t(26, 358, "其中留给问题与输出", 22, "start", ink, 600) +
    band(reserveLow, 372, Math.max(3, reserveHigh - reserveLow), 24, accent, "none", 0) +
    t(reserveLow - 8, 390, "2 000–4 000", 19, "end", accent) +

    line("M26 418H454", rule, 1.2) +
    t(26, 448, "96 页 × 500 字符 ≈ 48 000 字符", 21, "start", ink) +
    t(26, 480, "0.6–1.2 token/字符 → 28 800–57 600 token", 21, "start", soft) +
    t(26, 512, "窗口 32 768，余量 2 000–4 000", 21, "start", soft) +
    line("M26 536H454", rule, 1.2) +
    t(26, 572, "20 页、约 8 000 字符的小手册", 21, "start", accent) +
    t(26, 602, "此时整本提示更小更稳，上检索是过度设计", 20, "start", soft));
}

// ---------- A30 七项任务，一共 100 分 ----------
const rubric = [
  ["A", "材料档案与授权", 10],
  ["B", "需求与范围", 10],
  ["C", "架构决定", 15],
  ["D", "实现", 20],
  ["E", "评测", 20],
  ["F", "交付", 15],
  ["G", "答辩", 10]
];
const groups = [
  ["材料与需求", "A + B", 20, "先能解释你为什么有权处理，再谈做多少"],
  ["架构选择", "C", 15, "方案要由材料数据支持，不是列技术名词"],
  ["实现与评测", "D + E", 40, "六类路径至少四类有实际结果；评测先冻结"],
  ["交付与答辩", "F + G", 25, "可复建、可回退、能解释首个失败边界"]
];
export function rubricWeightsArt() {
  let cursor = 26;
  const segments = rubric.map(([letter, , points]) => {
    const width = points / 100 * 428;
    const x = cursor;
    cursor += width;
    return band(x, 96, width, 52, points === 20 ? wash : card, ink, 1.2) +
      t(x + width / 2, 130, letter, 22, "middle", ink, 600) +
      t(x + width / 2, 176, String(points), 19, "middle", points === 20 ? accent : soft, 600);
  }).join("");

  const legend = rubric.map(([letter, name, points], index) => {
    const x = index < 4 ? 26 : 248;
    const y = 272 + (index < 4 ? index : index - 4) * 32;
    return t(x, y, `${letter}　${name}`, 18, "start", points === 20 ? accent : ink) +
      t(x + 206, y, `${points} 分`, 18, "end", soft);
  }).join("");

  const rows = groups.map(([label, parts, points, note], index) => {
    const y = 436 + index * 76;
    return line(`M26 ${y - 26}H454`, rule, 1.2) +
      t(26, y, label, 22, "start", ink, 600) +
      t(454, y, `${points} 分`, 22, "end", index === 2 ? accent : ink, 600) +
      t(26, y + 28, `${parts}　${note}`, 19, "start", soft);
  }).join("");

  return canvas("七项任务，一共 100 分",
    "材料档案与授权各 10 分，架构决定 15 分，实现与评测各 20 分，交付 15 分，答辩 10 分，合计 100 分。实现与评测合计 40 分，材料与需求合计 20 分：分数压在能被别人复查的部分上。",
    772, segments +
    t(26, 214, "条形长度按分值比例，合计 100 分", 19, "start", soft) +
    line("M26 236H454", rule, 1.2) +
    legend +
    line("M26 400H454", rule, 1.2) +
    rows +
    line("M26 712H454", rule, 1.2) +
    t(26, 746, "先完成再对照，不要按分数倒推答案", 20, "start", accent));
}

export const appliedArtworks = [
  ["c18-retrieval-scores.svg", retrievalDenominatorsArt()],
  ["c28-context-budget.svg", contextBudgetArt()],
  ["c30-rubric-weights.svg", rubricWeightsArt()]
];
