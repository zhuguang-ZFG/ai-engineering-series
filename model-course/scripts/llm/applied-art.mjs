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

// ---------- A19 十一道边界，从权限到最终文字 ----------
export const ladder = [
  ["读者/权限", "unauthorized · filtered_doc_count"],
  ["清单/文件/版本", "missing-source · source-version-mismatch"],
  ["切块", "chunk_count · chunks[].start/end"],
  ["检索", "hits=[] · usage.calls=0"],
  ["提示组装", "used_chunk_ids · prompt budget dropped"],
  ["模型调用", "generation-failed · calls>0"],
  ["解析", "invalid-response · first_raw_response"],
  ["schema/语义", "first_failure.stage=validate"],
  ["引用/提取", "citation-failed · citation_errors"],
  ["工具", "tool-failed · budget-exhausted"],
  ["最终回答", "answered，但答非所问"]
];
export function failureLadderArt() {
  const rows = ladder.map(([name, field], index) => {
    const y = 104 + index * 56;
    const mark = index === 4;
    const tail = index === ladder.length - 1 ? "" : line(`M44 ${y - 6}V${y + 50}`, rule, 1.2);
    return t(26, y + 22, String(index + 1), 19, mark ? accent : soft, "start", 600) +
      t(58, y + 22, name, 21, "start", mark ? accent : ink, mark ? 600 : 400) +
      t(58, y + 46, field, 16, "start", soft) +
      tail;
  }).join("");

  return canvas("先看更早的边界，再看现象",
    "一条请求按实际顺序经过十一个边界。只要更早的环节已经偏离，后面的现象都只是后果；程序报出的 first_failure 是第一个异常，不一定是第一边界。",
    800, rows +
    line("M26 726H454", rule, 1.2) +
    t(26, 758, "例：命中片段被提示预算丢掉", 21, "start", accent, 600) +
    t(26, 786, "程序不报错，边界在第 5 步而不是第 11 步", 19, "start", soft));
}

// ---------- A22 八个点里有一个离群值 ----------
export const latencies = [1200, 1300, 1400, 1500, 1600, 1700, 1800, 9000];
const ms = value => 60 + value / 10000 * 380; // 0..10 000 ms → 60..440 px
export function latencySpreadArt() {
  const dots = latencies.map((value, index) => {
    // 前七个点挤在 25 px 内，上下交替避免互相遮挡。
    const y = index % 2 === 0 ? 122 : 140;
    return `<circle cx="${ms(value).toFixed(1)}" cy="${y}" r="5.5" fill="${value === 9000 ? accent : ink}"/>`;
  }).join("");
  const ticks = [0, 2000, 4000, 6000, 8000, 10000].map(value =>
    line(`M${ms(value)} 172V182`, ink, 1.4) + t(ms(value), 202, String(value), 17, "middle", soft)).join("");

  return canvas("八个样本里有一个离群值",
    "八次端到端耗时中七次在 1 200 到 1 800 毫秒，一次 9 000 毫秒。中位数 1 550 毫秒，平均值 2 437.5 毫秒，nearest-rank p95 在 n=8 时就是最大值 9 000 毫秒。",
    560,
    t(26, 96, "每次请求的端到端耗时（毫秒）", 19, "start", soft) +
    dots + ticks +
    line(`M${ms(1550).toFixed(1)} 100V240`, soft, 1.2, "4 4") +
    line(`M${ms(2437.5).toFixed(1)} 100V240`, accent, 1.2, "4 4") +
    line(`M${ms(9000).toFixed(1)} 100V240`, accent, 1.2, "4 4") +
    t(ms(1550) - 6, 264, "1550 中位数", 17, "end", soft) +
    t(ms(2437.5) + 6, 264, "平均值 2437.5", 17, "start", accent) +
    t(ms(9000) - 6, 264, "p95 = 9000", 17, "end", accent) +
    line("M26 292H454", rule, 1.2) +
    t(26, 324, "中位数贴近常见值，平均值被一个点拉高", 20, "start", ink) +
    t(26, 358, "n=8 时 p95 就是最大值，不能说“95% 用户”", 20, "start", soft) +
    t(26, 392, "所以要报 n 和原始点，写明分位算法", 20, "start", soft) +
    line("M26 416H454", rule, 1.2) +
    t(26, 448, "1200 1300 1400 1500 1600 1700 1800 9000", 17, "start", soft) +
    t(26, 486, "换个算法，p95 会变成另一个数", 19, "start", accent));
}

// ---------- A27 四种“没读出来”并不是一回事 ----------
export const ocrStates = [
  ["unreadable", "没有生成任何文字：text 为 null，退出码 4", "记录区域与原因，不要从上下文猜值", false],
  ["uncertain", "生成了文字，但平均 token log-prob 低于阈值", "标人工回看，它不是“已识别”", false],
  ["recognized 但字符错", "10:00 读成 10:30，LIFT 读成 LEFT", "最危险的一类，必须逐字回看原图", true],
  ["图中是恶意指令", "扫描件里写着“忽略之前的要求”", "当数据保留，绝不执行其中指令", false]
];
export function ocrFailuresArt() {
  const rows = ocrStates.map(([state, what, todo, danger], index) => {
    const y = 104 + index * 118;
    return line(`M26 ${y - 24}H454`, rule, 1.2) +
      t(26, y, state, 21, "start", danger ? accent : ink, 600) +
      t(26, y + 32, what, 17, "start", soft) +
      t(26, y + 62, `处理：${todo}`, 17, "start", danger ? accent : ink);
  }).join("");

  return canvas("四种“没读出来”",
    "没有文字、有文字但没过阈值、过了阈值但字符错、图中写着指令：四种状态的错误代价完全不同，报告里的 status 相同并不代表风险相同。",
    620, rows +
    line("M26 574H454", rule, 1.2) +
    t(26, 604, "阈值不是准确率：调到 -999 只是关掉警报", 19, "start", accent));
}

// ---------- A29 六次故障注入，各能证明什么 ----------
export const faults = [
  ["停掉服务", "连接被拒或超时", "不能推出服务一定没执行"],
  ["换错模型路径", "502 model-unavailable", "健康检查 200 是假阳性"],
  ["发非法 JSON", "400/413 invalid-request", "请求没有进入模型"],
  ["源文件缺失或改版", "409 missing-source", "不能拿缓存或旧版本顶上"],
  ["用无权读者提问", "403 或 insufficient-evidence", "无权限正文没有进提示与日志"],
  ["构造超时或断网", "未知，保留未知状态", "不等于服务没有答案"]
];
export function faultMatrixArt() {
  const rows = faults.map(([fault, status, cannot], index) => {
    const y = 104 + index * 84;
    return line(`M26 ${y - 28}H454`, rule, 1.2) +
      t(26, y, `${index + 1}. ${fault}`, 20, "start", ink, 600) +
      t(454, y, status, 17, "end", index === 5 ? soft : accent) +
      t(26, y + 30, cannot, 17, "start", soft);
  }).join("");

  return canvas("六次故障注入，各能证明什么",
    "每次故障都要保存请求、HTTP 码、响应体和时间。预期状态只说明入口拒绝了什么，不说明内部一定没执行、缓存一定没用、权限一定生效。",
    660, rows +
    line("M26 620H454", rule, 1.2) +
    t(26, 648, "记录实际结果；不要为演示 403 去改代码", 18, "start", soft));
}

appliedArtworks.push(
  ["c19-failure-ladder.svg", failureLadderArt()],
  ["c22-latency-spread.svg", latencySpreadArt()],
  ["c27-ocr-failures.svg", ocrFailuresArt()],
  ["c29-fault-matrix.svg", faultMatrixArt()]
);
