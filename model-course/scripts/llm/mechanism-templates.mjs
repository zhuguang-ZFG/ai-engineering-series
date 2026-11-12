import { readFileSync } from "node:fs";
import snapshots from "./mechanism-frames.cjs";

const fixture = name => {
  const data = JSON.parse(readFileSync(new URL(`../../book/llm/fixtures/${name}.json`, import.meta.url), "utf8"));
  snapshots.assertStoryboardFixture(name, data);
  return data;
};
const g = snapshots.generationFrames(fixture("generation"));
const a = snapshots.attentionFrames(fixture("attention"));
const d = snapshots.distillationFrames(fixture("distillation"));
const ink = "#26221B", paper = "#FFFDF8", soft = "#5C5448", accent = "#B4472F", wash = "#F3EAD8", rule = "#E3D8C1";
const esc = value => String(value).replace(/[&<>"']/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[c]);
const number = value => value.toFixed(4);
const percent = value => `${(value * 100).toFixed(2)}%`;
const vector = values => `[${values.map(number).join(", ")}]`;
const t = (x, y, value, size = 28, anchor = "start", color = ink) => `<text x="${x}" y="${y}" font-size="${size}" text-anchor="${anchor}" fill="${color}">${esc(value)}</text>`;
const path = (shape, color = ink, fill = "none", extra = "") => `<path d="${shape}" stroke="${color}" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" fill="${fill}" ${extra}/>`;
const box = (x, y, w, h, fill = paper) => path(`M${x + 3} ${y} Q${x + w / 2} ${y - 3} ${x + w} ${y + 2} L${x + w - 2} ${y + h} Q${x + w / 2} ${y + h + 2} ${x} ${y + h - 2}Z`, ink, fill);
const arrow = (x1, y1, x2, y2) => path(`M${x1} ${y1} Q${(x1 + x2) / 2 + 4} ${(y1 + y2) / 2 - 3} ${x2} ${y2}`, accent, "none", 'class="mechanism-flow"') + path(`M${x2 - 10} ${y2 - 8} L${x2} ${y2} L${x2 - 10} ${y2 + 8}`, accent);
const down = (x, y1, y2) => path(`M${x} ${y1} Q${x + 4} ${(y1 + y2) / 2} ${x} ${y2} M${x - 8} ${y2 - 10} L${x} ${y2} L${x + 8} ${y2 - 10}`, accent, "none", 'class="mechanism-flow"');
const circle = (x, y, r, fill = paper) => `<circle cx="${x}" cy="${y}" r="${r}" fill="${fill}" stroke="${ink}" stroke-width="2.5"/>`;
const change = body => `<g class="mechanism-change">${body}</g>`;
const bars = (items, x, y, width = 205, gap = 61, chosen = null) => items.map((item, i) => {
  const py = y + i * gap;
  return t(x, py + 25, item.piece, 27) + path(`M${x + 77} ${py + 7} L${x + 77 + width} ${py + 7}`, rule, "none", 'stroke-dasharray="4 5"') + box(x + 77, py, width * item.probability, 31, wash) + t(x + 77 + width + 12, py + 24, percent(item.probability), 24) + (chosen === item.piece ? path(`M${x - 15} ${py + 13} l6 7 l11 -15`, accent) : "");
}).join("");
const tape = (x, y, width, text, fill = paper) => box(x, y, width, 57, fill) + t(x + 15, y + 38, text, 28);
const svg = (title, description, body, id, height = 330) => `<svg xmlns="http://www.w3.org/2000/svg" width="480" height="${height}" viewBox="0 0 480 ${height}" role="img" aria-labelledby="${id}-title ${id}-desc"><title id="${id}-title">${esc(title)}</title><desc id="${id}-desc">${esc(description)}</desc><rect width="480" height="${height}" fill="${paper}"/><g font-family="'Noto Serif SC','Source Han Serif SC','Songti SC','SimSun',serif">${body}</g></svg>`;

function generationDrawing(step, compact = false) {
  if (compact) {
    if (step === 0) return bars(g.before, 34, 3, 195, 49);
    if (step === 1) return t(32, 40, "固定种子 42，抽中") + change(circle(370, 30, 37, wash) + t(370, 40, g.selected.piece, 30, "middle")) + t(32, 111, `本步概率 ${percent(g.selected.probability)}`, 28) + t(32, 154, "概率高，也不能证明杯里是水。", 24);
    if (step === 2) return tape(29, 4, 421, "他端起杯子，喝了一口") + down(240, 66, 96) + change(tape(29, 105, 421, g.text, wash));
    return t(32, 30, "新输入：……一口水", 28) + bars(g.next, 34, 58, 195, 53);
  }
  if (step === 0) return t(26, 38, "他端起杯子，喝了一口", 30) + path("M27 54 Q240 59 453 53", accent) + t(27, 95, "先把分数变成这一轮的概率", 26) + bars(g.before, 35, 122, 195, 61) + t(27, 316, "温度固定为 1", 24, "start", soft);
  if (step === 1) return t(26, 38, "这一轮，只取出一个片段", 30) + bars(g.before, 38, 73, 190, 57, g.selected.piece) + change(circle(94, 284, 31, wash) + t(94, 294, g.selected.piece, 30, "middle")) + arrow(145, 283, 212, 283) + t(230, 293, "等待追加", 29);
  if (step === 2) return t(26, 40, "刚选的片段，接到输入末尾", 29) + tape(28, 72, 424, g.prompt) + down(240, 142, 180) + change(tape(28, 194, 424, g.text, wash)) + t(27, 299, "下一轮要读到这个“水”", 27);
  return t(26, 40, "多了一个“水”，候选也变了", 29) + tape(28, 72, 424, "新输入：……一口水", wash) + bars(g.next, 35, 160, 195, 63) + t(27, 310, "下一轮再选择，再追加。", 27);
}

function attentionDrawing(step, compact = false) {
  const weights = a.tokens.map((piece, i) => ({ piece, probability: a.weights[i] }));
  if (compact) {
    if (step === 0) return a.tokens.map((word, i) => box(24 + i * 114, 6, 92, 56, i < 2 ? wash : rule) + t(70 + i * 114, 44, word, 26, "middle") + (i > 1 ? path(`M${27 + i * 114} 11 l84 46`, soft) : "")).join("") + t(30, 113, "当前在“把”：只看我、把。", 26) + t(30, 157, "苹果、切开：未来位置先挡住。", 24);
    if (step === 1) return t(30, 34, "Q = [0.2, 1]", 28) + t(30, 92, `我：0.2 / √2 = ${number(a.scores[0])}`, 25) + t(30, 148, `把：1.04 / √2 = ${number(a.scores[1])}`, 25);
    if (step === 2) return bars(weights.slice(0, 2), 34, 4, 195, 58) + t(30, 158, "未来权重为 0；可见权重和为 1。", 24);
    return t(30, 36, `${number(a.weights[0])} × [1, 0]`, 28) + t(30, 88, `+ ${number(a.weights[1])} × [0, 2]`, 28) + change(t(30, 148, `= ${vector(a.output)}`, 29));
  }
  if (step === 0) return t(25, 39, "让“把”向前找可用的信息", 29) + a.tokens.map((word, i) => box(23 + i * 114, 78, 92, 67, i < 2 ? wash : rule) + t(69 + i * 114, 121, word, 28, "middle") + t(69 + i * 114, 182, i < 2 ? "可见" : "屏蔽", 25, "middle") + (i > 1 ? path(`M${27 + i * 114} 84 l82 54`, soft) : "")).join("") + down(184, 199, 230) + tape(76, 248, 329, "本步 Q = [0.2, 1]", wash);
  if (step === 1) return t(26, 39, "Q 与可见 K 比一比", 30) + t(27, 93, "我：K = [1, 0]", 28) + t(47, 137, `0.2 / √2 = ${number(a.scores[0])}`, 28) + t(27, 206, "把：K = [0.2, 1]", 28) + t(47, 250, `1.04 / √2 = ${number(a.scores[1])}`, 28) + t(27, 311, "未来项不进入这一步的 softmax。", 25);
  if (step === 2) return t(26, 39, "softmax：把分数换成份额", 29) + bars(weights.slice(0, 2), 35, 85, 195, 69) + tape(28, 241, 424, "苹果 0%　　切开 0%", rule) + t(27, 319, "可见两项的权重加起来是 1。", 24);
  return t(26, 39, "按份额取 V，再逐维相加", 29) + t(27, 92, `${number(a.weights[0])} × [1, 0]`, 30) + t(27, 144, `+ ${number(a.weights[1])} × [0, 2]`, 30) + down(239, 163, 199) + change(tape(28, 211, 424, `输出 ${vector(a.output)}`, wash)) + t(27, 316, "输出仍是向量，接着交给后续计算。", 24);
}

function pairBars(compact = false, values = d.before) {
  const top = compact ? 42 : 115;
  const gap = compact ? 42 : 58;
  return t(80, top - 15, "教师", 27, "middle") + t(338, top - 15, "学生", 27, "middle") + d.labels.map((label, i) => {
    const y = top + i * gap;
    const student = t(266, y + 28, label, 24) + box(324, y + 6, 120 * values.student[i], 25, wash) + t(478, y + 27, percent(values.student[i]), 24, "end");
    return t(10, y + 28, label, 24) + box(67, y + 6, 120 * values.teacher[i], 25, wash) + t(238, y + 27, percent(values.teacher[i]), 24, "end") + (values === d.after ? change(student) : student);
  }).join("");
}

function distillationDrawing(step, compact = false) {
  if (compact) {
    if (step === 0) return pairBars(true);
    if (step === 1) return t(30, 32, "先算差多少，再算往哪边调", 27) + t(30, 88, "梯度（水、茶、咖啡）：", 25) + t(30, 141, vector(d.before.gradient), 28);
    if (step === 2) return d.labels.map((label, i) => t(30, 35 + i * 55, label, 27) + t(119, 35 + i * 55, "0", 29) + arrow(158, 26 + i * 55, 227, 26 + i * 55) + change(t(251, 35 + i * 55, number(d.logits[i]), 29))).join("");
    return pairBars(true, d.after);
  }
  if (step === 0) return t(26, 39, "同一温度 T = 2，对齐候选", 29) + pairBars() + t(27, 319, "学生起步三项同分；教师提供软目标。", 24);
  if (step === 1) return t(26, 39, "把两种训练信号合在一起", 29) + box(28, 69, 424, 57) + t(43, 107, "0.7 × T² × KL + 0.3 × CE", 26) + t(27, 179, "损失对学生三项分数的梯度：", 26) + change(t(27, 229, vector(d.before.gradient), 30)) + t(27, 284, "梯度为负的项，分数会升高。", 26) + t(27, 321, "本题硬标签是已核实的“水”。", 24);
  if (step === 2) return t(26, 39, "只更新学生的三项分数", 30) + t(27, 85, "新分数 = 旧分数 − 0.4 × 梯度", 26) + d.labels.map((label, i) => t(30, 146 + i * 67, label, 28) + t(130, 146 + i * 67, "0", 30) + arrow(169, 137 + i * 67, 247, 137 + i * 67) + change(t(273, 146 + i * 67, number(d.logits[i]), 30))).join("");
  return t(26, 39, "仍用 T = 2，再看学生变了多少", 28) + pairBars(false, d.after) + t(27, 319, `混合损失 ${number(d.before.loss)} → ${number(d.after.loss)}`, 27);
}

const stories = [
  {
    id: "G49", lesson: "L02", kind: "generation", file: "generation-steps.svg", title: "慢放一次：候选怎样变成下一轮输入",
    shortTitle: "一句话，接着往下写", drawing: generationDrawing,
    boundary: "沿用 X02 的人工教学模型，固定温度 1、种子 42；数字是本地计算，不是商用模型的内部概率。",
    frames: [
      { title: "先列本轮候选", text: `输入停在“${g.prompt}”。三个候选按分数计算后，“水”的概率是 ${percent(g.before[0].probability)}。此时还没有选词。` },
      { title: "从分布中选一个", text: `固定种子 42 的这次抽样选中“${g.selected.piece}”。抽中后先停一下：它只是本轮选出的片段，概率并不证明杯子里装着什么。` },
      { title: "追加到输入末尾", text: `把“${g.selected.piece}”接到句尾，输入变成“${g.text}”。刚才的输出，现在也成了下一轮能读到的内容。` },
      { title: "用新输入重算", text: `新上下文的候选变成了句号 ${percent(g.next[0].probability)}、逗号 ${percent(g.next[1].probability)}。上一轮的水、茶、咖啡已经不是这一步的候选；接下来重复选择和追加，直到停止。` },
    ],
  },
  {
    id: "G50", lesson: "L04", kind: "attention", file: "attention-steps.svg", title: "慢放一次：注意力怎样算出一个向量",
    shortTitle: "先挡未来，再汇总", drawing: attentionDrawing,
    boundary: "使用 X04 的同一组人工 Q/K/V，当前位置固定在“把”。这是单头因果注意力的一次计算；后文 0.75/0.25 是另一道手算例。",
    frames: [
      { title: "先确定哪些位置可见", text: "当前位置是“把”，可见“我”和“把”；“苹果”“切开”在未来，要先屏蔽。后面的文字即使已经画在纸上，也不能参与当前位置的汇总。" },
      { title: "比较 Q 与可见的 K", text: `Q = [0.2, 1]。和“我”的 K 点积得 0.2，和“把”的 K 点积得 1.04；除以 √2，分数分别是 ${number(a.scores[0])} 和 ${number(a.scores[1])}。` },
      { title: "把分数变成汇总份额", text: `只对可见分数做 softmax，得到“我” ${percent(a.weights[0])}、“把” ${percent(a.weights[1])}。未来两项是 0，可见权重加起来是 1。权重用于决定从各个 V 取多少。` },
      { title: "各取一份，再逐维相加", text: `${number(a.weights[0])} × [1, 0] + ${number(a.weights[1])} × [0, 2] = ${vector(a.output)}。图上保留四位小数，计算使用未舍入值。这个结果仍是向量，后面还要继续计算，不能直接当成完整推理的解释。` },
    ],
  },
  {
    id: "G51", lesson: "L05", kind: "distillation", file: "distillation-steps.svg", title: "慢放一次：学生怎样跟着训练信号改一步",
    shortTitle: "教师不动，学生改一步", drawing: distillationDrawing,
    boundary: "沿用 X09 的默认设置：温度 2、软目标权重 0.7、学习率 0.4，只优化当前上下文的三个学生 logits，没有完整语言网络或泛化测试。",
    frames: [
      { title: "让两个分布对齐", text: `教师与学生都用温度 2，候选顺序同为水、茶、咖啡。教师给“水” ${percent(d.before.teacher[0])}，学生起步给每项 ${percent(d.before.student[0])}；先对齐，才能逐项比较。` },
      { title: "算差距，也算调整方向", text: `训练同时使用软目标和已核实的硬标签“水”：软项为 0.7 × T² × KL，硬项为 0.3 × CE。混合损失是 ${number(d.before.loss)}，对学生三个 logits 的梯度为 ${vector(d.before.gradient)}。下一步按梯度的反方向更新，不是把教师的参数抄过来。` },
      { title: "沿反方向更新学生", text: `按“新分数 = 旧分数 − 学习率 × 梯度”，学生从 [0, 0, 0] 变为 ${vector(d.logits)}。学习率是 0.4；教师的 [3, 2, 0] 保持不变。` },
      { title: "再算一次，检查有没有变好", text: `仍用温度 2，学生给水、茶、咖啡的概率变为 ${d.after.student.map(percent).join("、")}，教师三项仍是 ${d.after.teacher.map(percent).join("、")}。用更新后的学生分数重算同一道题，混合损失从 ${number(d.before.loss)} 降到 ${number(d.after.loss)}。这里只能说明这次更新改善了当前训练目标；教师可能出错，学生在新题上的表现仍要单独测。` },
    ],
  },
];

export const mechanismFigures = stories.map(story => ({
  id: story.id, lesson: story.lesson, file: story.file, purpose: story.shortTitle,
  alt: story.frames.map((frame, i) => `${i + 1}．${frame.title}：${frame.text}`).join(" "),
  source: `课程原创手绘；与 ${story.kind === "generation" ? "X02" : story.kind === "attention" ? "X04" : "X09"} 共用 fixture 和计算函数；数值为教学计算。`,
  limitations: story.boundary, layout: "four-step-storyboard",
  mobile: "480×990 可编辑四步分镜；最小 24px。网页可逐帧观看 480×330 大图，正文保留逐步解释；打印版单图最大高 150mm。",
}));

export const mechanismAssets = stories.map(story => {
  const body = t(24, 39, story.shortTitle, 30) + path("M26 57 Q240 61 454 56", accent) + story.frames.map((frame, i) => `<g transform="translate(0 ${72 + i * 228})">${circle(43, 20, 18, wash)}${t(43, 29, i + 1, 24, "middle")}${t(74, 29, frame.title, 27)}<g transform="translate(0 49)">${story.drawing(i, true)}</g>${i < 3 ? path("M27 222 L452 222", rule) : ""}</g>`).join("");
  return { file: story.file, svg: svg(story.shortTitle, mechanismFigures.find(figure => figure.id === story.id).alt, body, story.id.toLowerCase(), 990) + "\n" };
});

export function mechanismLesson(id, h = esc) {
  const story = stories.find(entry => entry.lesson === id || entry.kind === id);
  if (!story) return "";
  const base = `mechanism-${story.kind}`;
  const figure = mechanismFigures.find(entry => entry.id === story.id);
  const buttons = [["previous", "上一步"], ["next", "下一步"], ["play", "播放一次"], ["reset", "从头看"], ["all", "看完整分镜"]].map(([action, label]) => `<button type="button" data-action="${action}" aria-controls="${base}-stage${action === "all" ? ` ${base}-static` : ""}">${label}</button>`).join("");
  return `<section class="mechanism" data-mechanism="${story.kind}" aria-labelledby="${base}-title"><h3 id="${base}-title">${h(story.title)}</h3><p class="mechanism-boundary">${h(story.boundary)}</p><div class="mechanism-controls" hidden>${buttons}</div><p class="mechanism-status" id="${base}-status" role="status" aria-live="polite"></p><div class="mechanism-stage" id="${base}-stage" hidden>${story.frames.map((frame, i) => `<div class="mechanism-frame" data-frame="${i}" data-title="${h(frame.title)}" hidden>${svg(frame.title, frame.text, story.drawing(i), `${base}-${i}`)}<p>${h(frame.text)}</p></div>`).join("")}</div><div class="mechanism-static" id="${base}-static"><figure class="mechanism-figure"><img src="../../book/assets/handdraw/llm/${story.file}" alt="${h(figure.alt)}" width="480" height="990"><figcaption>${story.id} · ${h(story.shortTitle)}。四步使用同一组教学数据。</figcaption></figure><ol>${story.frames.map(frame => `<li><strong>${h(frame.title)}</strong>。${h(frame.text)}</li>`).join("")}</ol></div></section>`;
}
