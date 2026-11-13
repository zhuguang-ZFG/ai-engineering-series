// Deterministic explainer source. Values come from the same course fixtures as the pages.
import { readFileSync, writeFileSync, mkdirSync } from "node:fs";
import { resolve, join } from "node:path";
import assert from "node:assert/strict";
import api from "./core.cjs";

const root = resolve(import.meta.dirname, "../..");
const checking = process.argv.includes("--check");
const json = file => JSON.parse(readFileSync(join(root, "book/llm", file), "utf8"));
const course = json("course.json");
// Prose and illustration revisions do not change the reviewed film edition.
const mediaVersion = course.mediaVersion ?? course.version;
const generation = json("fixtures/generation.json");
const materials = json("fixtures/materials.json");
const prices = json("fixtures/tools.json").scenarios[0].request.arguments;
const choices = api.candidates(generation, generation.prompt, 1);
const following = api.candidates(generation, generation.prompt + "水", 1);
const h = value => String(value).replace(/[&<>"']/g, char => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[char]);
const bar = (id, options) => `<div class="bars">${options.map((option, i) => `<div class="bar-row"><span>${h(option.piece)}</span><div class="bar-track"><div class="bar-fill" id="${id}-${i}" style="width:${option.probability * 100}%"></div></div><span>${(option.probability * 100).toFixed(1)}%</span></div>`).join("")}</div>`;
const arrow = id => `<svg class="draw-arrow" viewBox="0 0 1300 80" aria-hidden="true"><path id="${id}" d="M12 25 Q640 42 1270 25 M1240 5 L1270 25 L1240 48" fill="none" stroke="#1f883d" stroke-width="5" stroke-linecap="round"/></svg>`;
const style = `#root{width:1920px;height:1080px;background:#fbfaf6;color:#1f2328;font-family:'Noto Sans JP',sans-serif;overflow:hidden}.board{position:absolute;inset:110px 192px 100px}.eyebrow{font-size:34px;letter-spacing:2px;margin:0 0 24px}h1{font-size:84px;line-height:1.15;margin:0 0 50px;font-weight:800}.statement{font-size:66px;line-height:1.5;margin:22px 0}.paper{border:3px solid #1f2328;border-radius:3px 12px 4px 9px;padding:28px 34px;font-size:58px;line-height:1.5;background:#fffefb}.green{color:#1f6f35}.unknown{color:#a12c24}.note{font-size:46px;line-height:1.5;margin-top:26px}.footer{position:absolute;bottom:0;font-size:30px;color:#57606a}.draw-arrow{display:block;width:100%;height:72px;margin:12px 0}.bars{margin:12px 0}.bar-row{display:grid;grid-template-columns:170px 1fr 210px;align-items:center;gap:30px;font-size:64px;margin:26px 0}.bar-track{height:34px;border-bottom:2px solid #57606a}.bar-fill{height:34px;background:#1f883d;transform-origin:left}.result{font-size:72px;margin-top:24px;padding:22px 32px;border-left:6px solid #1f883d;background:#d3efd9}.split{display:grid;grid-template-columns:1fr 1fr;gap:50px}.split .paper{font-size:52px}.cross{font-size:60px;text-decoration:line-through;text-decoration-color:#a12c24;text-decoration-thickness:5px}.underline{display:inline-block;border-bottom:5px solid #1f883d}`;

const compactStyle = `.board{inset:100px 192px 100px}.eyebrow{margin-bottom:18px}h1{font-size:80px;margin-bottom:30px}.statement{font-size:62px;line-height:1.3;margin:18px 0}.paper{font-size:56px;padding:20px 28px}.note{font-size:42px;line-height:1.3;margin-top:18px;margin-bottom:18px}.draw-arrow{height:56px;margin:8px 0}.bar-row{font-size:60px;margin:18px 0}.result{font-size:66px;padding:18px 28px;margin-top:18px}.split .paper{font-size:48px}.footer{font-size:28px}.progress{position:absolute;left:0;right:0;bottom:24px;height:8px;background:#e3ded4}.progress i{position:absolute;left:0;top:0;height:100%;width:100%;background:#1f883d;transform:scaleX(0);transform-origin:left}.progress b{position:absolute;top:-7px;left:0;width:22px;height:22px;border-radius:50%;background:#1f883d}`;

// Narration is the film's spoken track: one line per scene, read by a local
// zh-CN voice and muxed as 48 kHz stereo AAC. Text stays on screen as well, so
// the film still reads with the sound off.
const narration = {
  "llm-principles": {
    candidates: "这句话还没有说完。先看三个候选，分数来自人工教学模型。",
    append: "选中水，把它接回输入，用新的整段文字再算一次。",
    boundary: "生成概率不等于核对事实。杯子里是不是水，这一段没有给出证据。"
  },
  "llm-applications": {
    missing: "通知里没有写地点。再通顺的补全，也补不出缺失的事实。",
    retrieve: "先找到通知B，再逐字核对原句，地点是社区阅览室。",
    receipt: "要计算，就检查真正的回执。失败或超时，就保留未完成。"
  }
};

const projects = [
  {
    name: "llm-principles", title: "选一个片段以后，发生了什么？", lessons: ["L02", "L05"],
    scenes: [
      { id: "candidates", title: "这句没说完的话，接什么？", body: `<div class="paper">${h(generation.prompt)}<span class="green">……</span></div>${bar("first", choices)}<p class="note" id="first-note">分数来自人工教学模型；温度为 1</p>`, animation: `tl.fromTo(".bar-fill",{scaleX:0},{scaleX:1,duration:.9,stagger:.2,ease:"power2.out"},2);tl.fromTo("#first-note",{opacity:0},{opacity:1,duration:.3},5);` },
      { id: "append", title: "选中的片段，接回输入", body: `<div class="paper">${h(generation.prompt)}<span id="water" class="green">水</span></div>${arrow("append-arrow")}<p class="statement" id="again">用新的整段输入，再计算一次</p>${bar("next", following)}<p class="note" id="next-note">本例演示选择“水”，不是某个实际模型的输出</p>`, animation: `tl.fromTo("#water",{opacity:0},{opacity:1,duration:.25},1);tl.fromTo("#append-arrow",{strokeDasharray:1400,strokeDashoffset:1400},{strokeDashoffset:0,duration:.7},2);tl.fromTo("#again",{opacity:0},{opacity:1,duration:.3},3);tl.fromTo(".bar-fill",{scaleX:0},{scaleX:1,duration:.8,stagger:.2},4.5);tl.fromTo("#next-note",{opacity:0},{opacity:1,duration:.3},7);` },
      { id: "boundary", title: "生成概率，不能替你核对事实", body: `<p class="statement">杯子里真的是水吗？</p><div class="paper" id="cup">这句话没有给出现场证据</div>${arrow("boundary-arrow")}<div class="split"><div class="paper" id="infer"><b>这次推理</b><br>使用已有参数<br>继续生成</div><div class="paper" id="train"><b>训练</b><br>对照目标算损失<br>再更新参数</div></div><p class="note" id="try">到 L02 换温度，再到 L05 看参数怎样更新</p>`, animation: `tl.fromTo("#cup",{opacity:0},{opacity:1,duration:.3},1);tl.fromTo("#boundary-arrow",{strokeDasharray:1400,strokeDashoffset:1400},{strokeDashoffset:0,duration:.7},2);tl.fromTo("#infer",{y:20,opacity:0},{y:0,opacity:1,duration:.4},3.5);tl.fromTo("#train",{y:20,opacity:0},{y:0,opacity:1,duration:.4},5.2);tl.fromTo("#try",{opacity:0},{opacity:1,duration:.3},7.5);` }
    ]
  },
  {
    name: "llm-applications", title: "一份安排表，怎样才有依据？", lessons: ["L07", "L09", "L10"],
    scenes: [
      { id: "missing", title: "通知没写地点，能补出来吗？", body: `<div class="paper">通知 A：${h(materials.documents[0].text)}</div><p class="statement" id="bad">预置练习回答：<span class="cross">城市图书馆</span></p>${arrow("missing-arrow")}<div class="result" id="missing-result">地点：未知</div><p class="note" id="missing-note">让提示更清楚，也不能补出缺失的事实</p>`, animation: `tl.fromTo("#bad",{opacity:0},{opacity:1,duration:.3},2);tl.fromTo("#missing-arrow",{strokeDasharray:1400,strokeDashoffset:1400},{strokeDashoffset:0,duration:.7},3.5);tl.fromTo("#missing-result",{opacity:0},{opacity:1,duration:.3},4.8);tl.fromTo("#missing-note",{opacity:0},{opacity:1,duration:.3},7);` },
      { id: "retrieve", title: "先找到资料，再核对原句", body: `<div class="paper" id="document-b">通知 B：${h(materials.documents[1].text)}</div>${arrow("retrieve-arrow")}<div class="result" id="place">地点：<span class="underline">社区阅览室</span>［B］</div><p class="statement" id="quote">证据：“地点为社区阅览室”</p><p class="note" id="retrieval-limit">检索让资料进入本次输入；引用仍要支持结论</p>`, animation: `tl.fromTo("#document-b",{y:25,opacity:0},{y:0,opacity:1,duration:.4},.5);tl.fromTo("#retrieve-arrow",{strokeDasharray:1400,strokeDashoffset:1400},{strokeDashoffset:0,duration:.7},2);tl.fromTo("#place",{opacity:0},{opacity:1,duration:.3},3.5);tl.fromTo("#quote",{opacity:0},{opacity:1,duration:.3},5);tl.fromTo("#retrieval-limit",{opacity:0},{opacity:1,duration:.3},7.5);` },
      { id: "receipt", title: "要计算，就检查真正的回执", body: `<div class="paper">人工请求：${prices.a} × ${prices.b}</div>${arrow("receipt-arrow")}<div class="result" id="total">本地乘法回执：${prices.a * prices.b}</div><p class="statement" id="failed">若失败或超时：保留未完成</p><p class="note" id="final-task">在 L07 / L09 / L10 亲手换材料、查证据、试失败</p><p class="note" id="models">实际模型复做：DeepSeek V4.1 Flash / Kimi K3</p>`, animation: `tl.fromTo("#receipt-arrow",{strokeDasharray:1400,strokeDashoffset:1400},{strokeDashoffset:0,duration:.7},1);tl.fromTo("#total",{opacity:0},{opacity:1,duration:.3},2.5);tl.fromTo("#failed",{opacity:0},{opacity:1,duration:.3},4.5);tl.fromTo("#final-task,#models",{opacity:0},{opacity:1,duration:.3,stagger:.8},6.5);` }
    ]
  }
];

for (const project of projects) {
  const folder = join(root, "videos", project.name);
  const put = (name, text) => {
    const path = join(folder, name);
    if (checking) assert.equal(readFileSync(path, "utf8").replaceAll("\r\n", "\n"), text, `${project.name}/${name} is stale`);
    else { mkdirSync(resolve(path, ".."), { recursive: true }); writeFileSync(path, text); }
  };
  put("package.json", JSON.stringify({ name: project.name, private: true, type: "module", scripts: { dev: "npx --yes hyperframes@0.8.210 preview", check: "npx --yes hyperframes@0.8.210 check", render: "npx --yes hyperframes@0.8.210 render" } }, null, 2) + "\n");
  put("hyperframes.json", JSON.stringify({ $schema: "https://hyperframes.heygen.com/schema/hyperframes.json", paths: { blocks: "compositions", assets: "assets" } }, null, 2) + "\n");
  put("STORYLINES.md", `# ${project.title}\n\n选用：纸上追踪。一个例子逐步改变，箭头只连接实际发生的变化，沿用课程纸色与墨绿。\n\n另案一：从完整答案倒查证据，适合复习；本片先顺着例子建立顺序。\n\n另案二：双画面对照有无证据的回答，信息量较大，留给熟悉例子的读者。\n\n用户已要求完成计划并交付，采用第一案连续制作。配音图解版：每场一句中文解说（本地合成音轨），文字同时保留，关掉声音仍可读。\n`);
  put("SPEC.md", `# ${project.title}\n\nGOAL: 沿一个人工例子分清输入、处理和可验证结果。\nOUTPUT: 1920×1080, 30fps, 32.4 秒（972 帧），含音轨。\nLOOK: #fbfaf6 纸色，#1f2328 墨色，#1f883d 仅标变化；标题 84px，正文 58–72px，边线 3–5px，无阴影和装饰颗粒。\nMOTION: power2.out；箭头绘制 21 帧，数值条增长 24–27 帧；全片进度条与游标连续移动，任何 0.5 秒窗口都有位移。\nSOUND: 中文解说音轨（本地 zh-CN 语音合成，48 kHz 立体声 AAC），每场一句；不使用第三方音乐素材。\nSOURCE: 课程 ${mediaVersion}；${project.lessons.join('/')}；fixture 及本地公式，不代表实际模型输出。\nREGISTRY: 搜索 bar chart draw path，参考 animated-bar-chart 的 scaleX 确定性增长；按课程实际概率重建，未复制第三方资产。\nBANNED: 整页列表、装饰机器人、每字弹跳、霓虹渐变、凭空数字、把计划画成执行成功。\nQA: 各场景 0.3s/5.4s/9.5s、切点前后 0.2s、末帧；必须无空白、证据可读。\n\n${project.scenes.map((scene, i) => `- 帧 ${i * 324}–${(i + 1) * 324 - 1}：${scene.title}。先展示输入，再按时间线展开变化。`).join("\n")}\n`);
  const narrationEntries = project.scenes.map(scene => {
    const line = narration[project.name]?.[scene.id];
    if (!line) throw new Error(`${project.name}/${scene.id} has no narration line; add one to the narration map so the delivery never renders silent`);
    return { id: scene.id, text: line };
  });
  put("narration.json", JSON.stringify(narrationEntries, null, 2) + "\n");
  const hosts = project.scenes.map((scene, i) => `<div id="scene-${scene.id}" class="clip" data-composition-id="${scene.id}" data-composition-src="compositions/${scene.id}.html" data-start="${(i * 10.8).toFixed(1)}" data-duration="10.8" data-track-index="${i + 1}" data-track-kind="graphics" data-width="1920" data-height="1080" data-hold="true"></div>`).join("\n");
  put("index.html", `<!doctype html>\n<html lang="zh-CN"><head><meta charset="utf-8"><title>${h(project.title)}</title><script src="assets/gsap.min.js"></script><style>*{box-sizing:border-box}html,body{margin:0;width:1920px;height:1080px;overflow:hidden;background:#fbfaf6}#root{position:relative;width:1920px;height:1080px}</style></head><body><div id="root" data-composition-id="main" data-start="0" data-duration="32.4" data-width="1920" data-height="1080">${hosts}</div><script>window.__timelines=window.__timelines||{};window.__timelines["main"]=gsap.timeline({paused:true});</script></body></html>\n`);
  for (const [i, scene] of project.scenes.entries()) {
    put(`compositions/${scene.id}.html`, `<template>\n<style>${style}${compactStyle}</style>\n<div id="root" data-composition-id="${scene.id}" data-width="1920" data-height="1080"><div class="board clip" id="board-${scene.id}" data-start="0" data-duration="10.8" data-hold="true"><p class="eyebrow">${h(project.name === "llm-principles" ? "把一句话接下去" : "把通知变成安排")} · ${i + 1}/3 · 配音图解</p><h1>${h(scene.title)}</h1>${scene.body}<p class="footer">课程 ${h(mediaVersion)} · 人工例子 / 本地计算 · ${project.lessons.join(" / ")}</p><div class="progress"><i id="prog"></i><b id="dot"></b></div></div></div>\n<script>const tl=gsap.timeline({paused:true});tl.fromTo("#board-${scene.id}",{scale:1.0},{scale:1.035,transformOrigin:"50% 50%",duration:10.8,ease:"none"},0);tl.fromTo("#prog",{scaleX:0},{scaleX:1,duration:10.8,ease:"none"},0);tl.fromTo("#dot",{x:0},{x:1514,duration:10.8,ease:"none"},0);${scene.animation}window.__timelines=window.__timelines||{};window.__timelines["${scene.id}"]=tl;</script>\n</template>\n`);
  }
}
console.log(`${checking ? "Verified" : "Built"} two source-driven explainer projects`);
