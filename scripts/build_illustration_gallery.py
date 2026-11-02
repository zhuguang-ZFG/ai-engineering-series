#!/usr/bin/env python3
"""Regenerate docs/illustration-gallery.html — the "看图说话" showcase of every
hand-inked illustration the book ships.

Every figure carries a plain-language caption so a reader who opens nothing
else can still tell what each drawing says. The page is self-contained
(inline SVG, no external assets) and replays the ink drawing with character
loops — the same verbs the book itself ships, guarded the same way.

Regenerate after touching yuyu-book/illustrations/:

    python scripts/build_illustration_gallery.py

Style system: yang0/handraw-style (FD-001 ink editorial, C-32 charcoal,
C-15 cinnabar) — see CREDITS.md and docs/illustration-prompts.md.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ART = ROOT / "yuyu-book" / "illustrations"
OUT = ROOT / "docs" / "illustration-gallery.html"

ORDER = ["front", "ch01", "ch01-five-pillars", "ch02", "ch02-turn-loop",
         "ch03", "ch03-tool-bench", "ch03-tool-pipeline",
         "ch04", "ch04-gate-steps", "ch05", "ch05-trust-ladder",
         "ch06", "ch06-memory-funnel", "ch07", "ch07-four-levels",
         "ch08", "ch08-hook-line", "ch09", "ch09-fork-pipeline",
         "ch10", "ch10-coordinator-fork", "ch11", "ch11-skill-stairs",
         "ch12", "ch12-mcp-state-dial", "ch13", "ch13-concurrency-gate",
         "ch14", "ch14-plan-gate", "ch15", "ch15-harness-wheel",
         "apxa", "apxb", "apxc", "apxd", "keeper",
         "part-p1", "part-p2", "part-p3", "part-p4", "cover"]
BIG = {"part-p1", "part-p2", "part-p3", "part-p4", "cover"}
# the plates drawn for the prose column are wide landscapes, not badges
WIDE = {"ch03-tool-bench": 300, "ch03-tool-pipeline": 330,
        "ch02-turn-loop": 330, "ch01-five-pillars": 300,
        "ch04-gate-steps": 330, "ch08-hook-line": 330,
        "ch07-four-levels": 330, "ch05-trust-ladder": 330,
        "ch06-memory-funnel": 330, "ch09-fork-pipeline": 330,
        "ch10-coordinator-fork": 330, "ch11-skill-stairs": 330,
        "ch12-mcp-state-dial": 330, "ch13-concurrency-gate": 330,
        "ch14-plan-gate": 330, "ch15-harness-wheel": 330}
WIDTH = {n: (420 if n == "cover" else WIDE.get(n) or (300 if n in BIG else 120))
         for n in ORDER}

# 看图说话：每幅图配一句说人话的白话题注，让不看正文的读者也能懂
PLAIN = {
    "front": "一张古地图：整本书就是一条路",
    "ch01": "罗盘：从「陪聊」到「干活」，换一种瞄准方式",
    "ch01-five-pillars": "一道门廊：五条原则顶着同一根横梁",
    "ch02": "心跳：一句话进、一句话出的对话循环",
    "ch02-turn-loop": "四格胶片：问一句、点工具、跑完、填回去再问",
    "ch03": "螺母：Agent 的双手——工具越多，本事越大",
    "ch03-tool-bench": "一张工具台：每件家伙什只管一件事",
    "ch03-tool-pipeline": "四格胶片：排队、切批、同时开工、按序交回",
    "ch04": "闸门：危险操作先过一道勾选的护栏",
    "ch04-gate-steps": "四格胶片：验格式、比规则、看上下文、最后问人",
    "ch05": "千层饼：配置像基因，一层层定性格",
    "ch06": "折角笔记本：Agent 的长期记忆记在这里",
    "ch07": "仪表盘：脑子里工作台还剩多少位置",
    "ch07-four-levels": "四格胶片：剪一刀、压一压、折三层、整段重写",
    "ch08": "挂钩：在人生节点上，给它装上小动作",
    "ch08-hook-line": "四格胶片：铃响、挂住、跑脚本、一路放行一路截住",
    "ch09": "分叉路：派几个小助手分头去办",
    "ch10": "指挥家：一个主编排，四方小队听调",
    "ch11": "技能卡：把说明书装进兜里，随取随用",
    "ch12": "外接线：一根线，用上全世界的工具",
    "ch13": "漏斗：回答像水一样，一边流一边看",
    "ch14": "小红旗：先画路线再出发，插旗为证",
    "ch15": "辘轳：亲手摇一架，你也造一个 Agent",
    "ch05-trust-ladder": "六级台阶：越外层越不可信，三星闸门划出安全线",
    "ch06-memory-funnel": "双层漏斗：先按行滤、再按字节滤，只留一张索引卡",
    "ch09-fork-pipeline": "四格胶片：留消息、收调用、换占位、发分身，省下六成字",
    "ch10-coordinator-fork": "两种带队法：工地上听指挥，侦察队各带干粮",
    "ch11-skill-stairs": "五级台阶：官越大说了算，官缺了往下补",
    "ch12-mcp-state-dial": "一座钟面：五个状态绕环走，卡住就退避重试",
    "ch13-concurrency-gate": "一扇闸门：只读的齐头并进，动手的排队独占",
    "ch14-plan-gate": "一间带门的作坊：先在左屋画图，再进右屋动工",
    "ch15-harness-wheel": "一只车轮：对话循环是毂，五根辐条撑起整车",
    "apxa": "藏宝图：源码去哪儿翻，一图定位",
    "apxb": "工具清单：所有家当，逐项打勾",
    "apxc": "开关排：哪些功能开着，一眼看清",
    "apxd": "小词典：生词太多？翻这一册",
    "keeper": "老驿卒：每章结尾替你守夜总结的人",
    "part-p1": "大罗盘：基础篇，先把方向找准",
    "part-p2": "百宝箱：核心系统锁在这只匣子里",
    "part-p3": "山径：高级模式，是翻山的近道",
    "part-p4": "牌坊：工程实践，出了镇子的大路",
    "cover": "四马古车：书名「御舆」——驾驭一辆车，也驾驭一个 Agent",
}


PLAIN_EN = {
    "front": "An old map: the whole book is one road",
    "ch01": "Compass: from chatbot to co-worker — a new way to aim",
    "ch01-five-pillars": "A portico: five principles under one lintel",
    "ch02": "Heartbeat: one message in, one out",
    "ch02-turn-loop": "A filmstrip: ask, pick a tool, run it, put the "
                      "result back and ask again",
    "ch03": "Nut: the agent's hands — more tools, more skill",
    "ch03-tool-bench": "A tool bench: every tool on the wall does one job",
    "ch03-tool-pipeline": "A filmstrip: queue up, split, work at once, "
                          "report in order",
    "ch04": "Gate: risky actions pass a checked guardrail",
    "ch04-gate-steps": "A filmstrip: check the shape, match a rule, "
                       "weigh the context, then ask",
    "ch05": "Layer cake: settings are genes, layer by layer",
    "ch06": "Folded notebook: where long-term memory lives",
    "ch07": "Gauge: how much working memory is left",
    "ch07-four-levels": "A filmstrip: snip a tail, squeeze, fold in "
                        "three, rewrite the whole span",
    "ch08": "Hooks: small actions at life's milestones",
    "ch08-hook-line": "A filmstrip: the event rings, a hook catches it, "
                      "the script runs, one road goes on and one is cut",
    "ch09": "Fork: small helpers in parallel",
    "ch10": "Conductor: one orchestrator, four squads",
    "ch11": "Skill cards: the manual in your pocket",
    "ch12": "One line to the world's tools",
    "ch13": "Funnel: answers flow like water",
    "ch14": "Flag: draw the route first, plant the flag",
    "ch15": "Windlass: crank one yourself",
    "ch05-trust-ladder": "Six steps: the outer layers trust less; a "
                         "three-star gate draws the line",
    "ch06-memory-funnel": "A two-gate funnel: rows first, then bytes -- "
                          "one index card survives",
    "ch09-fork-pipeline": "A filmstrip: keep the messages, gather the "
                          "calls, swap a placeholder, fork -- two-thirds "
                          "the tokens",
    "ch10-coordinator-fork": "Two ways to lead: a foreman's yard, or "
                             "scouts who carry their own rations",
    "ch11-skill-stairs": "Five steps: policy outranks all; when it is "
                         "absent, the next level speaks",
    "ch12-mcp-state-dial": "A clock face: five states around the ring, "
                           "back off and retry when stuck",
    "ch13-concurrency-gate": "One gate: read-only tools run in step; "
                             "anything that writes queues alone",
    "ch14-plan-gate": "A workshop with a door: sketch in the read-only "
                      "room, build in the other",
    "ch15-harness-wheel": "A wheel: the dialog loop is the hub; five "
                          "spokes carry the cart",
    "apxa": "Treasure map: where the source lives",
    "apxb": "Tool inventory: tick every box",
    "apxc": "Switch bank: what's on, at a glance",
    "apxd": "Pocket dictionary for new words",
    "keeper": "The old courier, summing up each chapter",
    "part-p1": "The great compass: foundations",
    "part-p2": "The chest: core systems inside",
    "part-p3": "Mountain path: the hill shortcut",
    "part-p4": "Gateway: the road out of town",
    "cover": "The four-horse chariot: drive a chariot, drive an agent",
}

def main():
    on_disk = {p.stem for p in ART.glob("*.svg")}
    if on_disk != set(ORDER):
        raise SystemExit(
            "the gallery and the drawing shelf disagree: "
            f"only in ORDER {sorted(set(ORDER) - on_disk)}, "
            f"never hung {sorted(on_disk - set(ORDER))}")
    svgs = {n: (ART / f"{n}.svg").read_text(encoding="utf-8").strip()
            for n in ORDER}
    cells = "".join(
        f'<figure class="c" data-name="{n}" tabindex="0" role="button"'
        f' aria-label="重播 {n}：{PLAIN[n]}"'
        f' style="width:{WIDTH[n]+18}px">'
        f'<div class="art" style="width:{WIDTH[n]}px">{svgs[n]}</div>'
        f'<figcaption>{n}</figcaption>'
        f'<div class="plain">{PLAIN[n]}</div>'
        f'<div class="plain-en">{PLAIN_EN[n]}</div></figure>'
        for n in ORDER)
    grid_light = f'<div class="grid" id="light">{cells}</div>'
    grid_dark = f'<div class="grid" id="dark">{cells}</div>'
    page = build_page(grid_light, grid_dark).replace(
        "@@PLATES@@", str(len(ORDER)))
    OUT.write_text(page, encoding="utf-8")
    print(f"{OUT} ({len(page)} bytes, {len(ORDER)} figures)")


def build_page(grid_light: str, grid_dark: str) -> str:
    # the dark sheet re-uses the same markup: currentColor re-inks everything
    return PAGE_HEAD + grid_light + PAGE_DARK_OPEN + grid_dark + PAGE_TAIL


PAGE_HEAD = """<!doctype html>
<html lang="zh">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E%3Ccircle cx='16' cy='16' r='12' fill='none' stroke='%23B4472F' stroke-width='3'/%3E%3Ccircle cx='16' cy='16' r='4' fill='%23B4472F'/%3E%3C/svg%3E">
<title>御舆插图 · 看图说话 — 手绘逐笔回放</title>
<meta property="og:title" content="御舆插图 · 看图说话">
<meta property="og:description" content="@@PLATES@@ 幅手绘插图的中英双语题注画廊：点击任意一幅，看墨线逐笔重演。">
<meta property="og:type" content="website">
<meta property="og:image" content="cover.png">
<style>
body{margin:0;font:14px/1.6 system-ui,"Microsoft YaHei",sans-serif;background:#F5F0E6;color:#26221B}
header{padding:22px 28px 6px;display:flex;flex-wrap:wrap;gap:12px;align-items:baseline}
h1{font-size:18px;margin:0;font-weight:650}
.brush{width:150px;height:9px;color:#B4472F;flex:0 0 100%;margin:-4px 0 0 2px}
.ttl-c{display:inline-block;will-change:transform,opacity}
.sub{color:#675F4F;font-size:12.5px}
.bar{padding:0 28px 14px;display:flex;gap:10px;align-items:center;flex-wrap:wrap}
button{font:13.5px/1 inherit;padding:8px 16px;border-radius:6px 4px 7px 3px/3px 7px 4px 5px;
       border:1.5px solid #26221B;background:#FFFDF8;color:#26221B;cursor:pointer;
       transition:transform .14s ease, box-shadow .14s ease, color .14s ease, border-color .14s ease}
button:hover{transform:translateY(-1px) rotate(-.6deg);color:#B4472F;border-color:#B4472F;
             box-shadow:2px 3px 0 rgba(38,34,27,.16)}
button:active{transform:translateY(0) rotate(0deg);box-shadow:none}
.palette{display:inline-flex;gap:6px;vertical-align:middle}
.palette i{width:18px;height:18px;border-radius:4px 3px 5px 2px/3px 5px 3px 4px;display:inline-block}
.hint{font-size:12px;color:#675F4F}
section{padding:6px 28px 30px}
h2{font-size:13px;color:#675F4F;margin:16px 0 10px;font-weight:600;letter-spacing:.04em}
.grid{display:flex;flex-wrap:wrap;gap:16px;align-items:flex-end}
.c{margin:0;text-align:center;cursor:pointer}
.c:focus-visible{outline:2px solid #B4472F;outline-offset:3px}
.c figcaption{margin-top:6px;font-size:11px;color:#675F4F;letter-spacing:.03em}
.c .plain{margin-top:2px;font-size:11px;line-height:1.5;color:#6E6353;
          max-width:150px;margin-inline:auto}
.c .plain-en{font-size:10px;line-height:1.4;color:#8A7D68;
             max-width:150px;margin-inline:auto}
.c:hover .art svg{transform:scale(1.05)}
.c .art svg{transition:transform .25s cubic-bezier(.34,1.56,.64,1)}
.c:hover figcaption{color:#B4472F}
.art svg{display:block;width:100%;height:auto}
.dark-wrap{background:#1E1D18;margin:6px 28px 34px;
           border-radius:14px 8px 13px 9px/9px 13px 8px 14px;
           padding:14px 0 22px;color:#E9E4D8}
.dark-wrap h2{color:#BDB4A2;padding-left:16px}
.dark-wrap .c figcaption{color:#A59C8A}
.dark-wrap .c .plain-en{color:#9C9484}
.dark-wrap .c:hover figcaption{color:#E07B5F}
.dark-wrap .c .plain{color:#B3AA99}
.dark-wrap button{background:#26241D;border-color:#BDB4A2;color:#E9E4D8}
.replay-badge{position:fixed;right:18px;bottom:16px;background:#B4472F;color:#FBF7EF;
              font-size:11.5px;padding:7px 13px;border-radius:6px 3px 7px 4px/4px 7px 3px 6px;
              transform:rotate(-1.2deg);box-shadow:2px 3px 0 rgba(38,34,27,.2)}
/* character loops: the same verbs the book inks, but always on once a
   drawing has finished drawing itself */
.alive .swing{transform-origin:45.2px 39.3px;transform-box:view-box;
  animation:ink-swing 1.5s ease-in-out infinite alternate}
.alive .spin{transform-origin:32px 32px;transform-box:view-box;
  animation:ink-spin 9s linear infinite}
.alive .wiggle{transform-origin:32px 32px;transform-box:view-box;
  animation:ink-wiggle 1s cubic-bezier(.36,.07,.19,.97) infinite alternate}
.alive .sweep{transform-origin:32px 44px;transform-box:view-box;
  animation:ink-sweep 1.5s ease-in-out infinite alternate}
.alive .nudge{animation:ink-nudge .7s cubic-bezier(.36,.07,.19,.97) infinite alternate}
.alive .pulse{transform-box:fill-box;transform-origin:center;
  animation:ink-pulse 1.1s cubic-bezier(.34,1.56,.64,1) infinite}
.alive .sway{transform-origin:32px 14px;transform-box:view-box;
  animation:ink-sway 1.7s ease-in-out infinite alternate}
.alive .drip{animation:ink-drip 1s cubic-bezier(.55,0,1,.45) infinite}
.alive .wave{transform-origin:47px 12px;transform-box:view-box;
  animation:ink-wave 1.3s ease-in-out infinite alternate}
.alive .knob{animation:ink-toggle 1.6s cubic-bezier(.34,1.56,.64,1) infinite alternate}
.alive .roll{transform-origin:668px 336px;transform-box:view-box;
  animation:ink-roll 5.5s linear infinite}
.alive .bob{animation:ink-bob 1.1s ease-in-out infinite alternate}
.alive .turn{transform-origin:100px 64px;transform-box:view-box;
  animation:ink-turn 13s linear infinite}
.alive .m75{animation:ink-march-75 1s linear infinite}
.alive .m92{animation:ink-march-92 1.1s linear infinite}
.alive .m80{animation:ink-march-80 1.05s linear infinite}
.alive .m110{animation:ink-march-110 1.3s linear infinite}
.alive .redraw,.alive .write,.alive .tick{stroke-dasharray:100 100;
  animation:ink-redraw 1.2s ease-out infinite}
.alive .t2{animation-delay:.15s}
.alive .t3{animation-delay:.3s}
.alive .d1{animation:ink-ripple .9s ease-out infinite}
.alive .d2{animation:ink-ripple .9s ease-out .15s infinite}
.alive .blink{animation:ink-blink 1.1s linear infinite}
.alive .b2{animation-delay:.55s}
.alive .f1{animation:ink-flutter .8s ease-in-out infinite alternate}
.alive .f2{animation:ink-flutter .8s ease-in-out .2s infinite alternate}
.alive .ripple{transform-box:fill-box;transform-origin:center}
.alive .flutter{transform-box:fill-box;transform-origin:50% 0%}
.spark{position:fixed;width:7px;height:7px;border-radius:60% 40% 55% 45%;
  pointer-events:none;z-index:99}
@keyframes ink-spin{to{transform:rotate(360deg)}}
@keyframes ink-wiggle{from{transform:rotate(-7deg)}to{transform:rotate(7deg)}}
@keyframes ink-sweep{from{transform:rotate(-12deg)}to{transform:rotate(14deg)}}
@keyframes ink-nudge{from{transform:translateX(0)}to{transform:translateX(3px)}}
@keyframes ink-pulse{0%{transform:scale(1)}45%{transform:scale(1.3)}100%{transform:scale(1)}}
@keyframes ink-sway{from{transform:rotate(-1.4deg)}to{transform:rotate(1.4deg)}}
@keyframes ink-drip{0%{transform:translateY(0);opacity:.55}
  70%{opacity:.55}100%{transform:translateY(6px);opacity:0}}
@keyframes ink-wave{from{transform:rotate(-4deg)}to{transform:rotate(5deg)}}
@keyframes ink-toggle{0%{transform:translateX(0)}55%{transform:translateX(-25px)}
  75%{transform:translateX(-19px)}100%{transform:translateX(-21px)}}
@keyframes ink-swing{from{transform:rotate(-10deg)}to{transform:rotate(10deg)}}
@keyframes ink-roll{to{transform:rotate(360deg)}}
@keyframes ink-bob{0%,100%{transform:translateY(0)}50%{transform:translateY(-2.5px)}}
@keyframes ink-turn{to{transform:rotate(360deg)}}
@keyframes ink-march-75{to{stroke-dashoffset:-7.5}}
@keyframes ink-march-92{to{stroke-dashoffset:-9.2}}
@keyframes ink-march-80{to{stroke-dashoffset:-8}}
@keyframes ink-march-110{to{stroke-dashoffset:-11}}
@keyframes ink-redraw{from{stroke-dashoffset:100}to{stroke-dashoffset:0}}
@keyframes ink-ripple{0%{transform:translateY(0)}
  55%{transform:translateY(2.5px)}100%{transform:translateY(0)}}
@keyframes ink-blink{0%,45%{opacity:1}50%,95%{opacity:.12}100%{opacity:1}}
@keyframes ink-flutter{from{transform:rotate(-5deg)}to{transform:rotate(6deg)}}
</style>
</head>
<body>
<header>
  <h1>御舆插图 · 看图说话</h1>
  <svg class="brush" viewBox="0 0 190 10" aria-hidden="true"><path d="M4 6q30-4.5 62-2.5t72-1q24 .2 46 1.8" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" opacity=".85"/><path d="M152 5.6q10-.6 20-.2" fill="none" stroke="currentColor" stroke-width="1.3" stroke-linecap="round" opacity=".45"/><circle cx="178" cy="5.8" r="1.5" fill="currentColor" stroke="none"/></svg>
  <span class="sub">FD-001 东方墨线 Editorial · C-32 炭黑 / C-15 朱砂 · yang0/handraw-style 体系 · 点击任意图重播该张</span>
</header>
<div class="bar">
  <button id="replay">▶ 重播全部</button>
  <button id="speed">速度 ×1</button>
  <span class="palette">
    <i style="background:#43392B" title="浓墨 C-32"></i>
    <i style="background:#8A7D68" title="次墨"></i>
    <i style="background:#5A5040" title="淡墨"></i>
    <i style="background:#B4472F" title="朱砂 C-15"></i>
    <i style="background:#F3EAD8;border:1px solid #D2C4A6" title="纸"></i>
  </span>
  <span class="hint" id="motion-hint"></span>
</div>
<section>
  <h2>PAPER · 纸面</h2>
  """

PAGE_DARK_OPEN = """</section>
<div class="dark-wrap">
  <h2>DARK · 夜读</h2>
  """

PAGE_TAIL = """</div>
<div class="replay-badge" id="badge">正在起笔……</div>
<script>
const SPEEDS = [1, 1.6, 2.6];
let speedIdx = 0;
/* spring curve precompiled to linear() — zero runtime, hardware accelerated
   (technique: joshwcomeau.com/animation/linear-timing-function) */
const SPRING = "linear(0,0.09,0.24,0.42,0.55,0.66,0.74,0.81,0.87,0.91,0.95,0.97,0.99,1,1.008,1.012,1.012,1.01,1.006,1.003,1)";

function prep(svg, baseDelay, factor) {
  const els = Array.from(svg.querySelectorAll("path, circle"));
  let t = baseDelay;
  const jobs = [];
  for (const el of els) {
    const fill = el.getAttribute("fill");
    const dashed = el.hasAttribute("stroke-dasharray");
    if (fill && fill !== "none") {
      jobs.push({el, kind:"dot", at:t});
      t += 90 * factor;
      continue;
    }
    if (dashed) {
      jobs.push({el, kind:"dashed", at:t});
      t += 160 * factor;
      continue;
    }
    let L = 60;
    try { L = el.getTotalLength(); } catch (e) {}
    const dur = Math.min(900, Math.max(180, L * 2.4)) * factor;
    jobs.push({el, kind:"stroke", at:t, dur, L});
    t += dur * 0.42;
  }
  return {jobs, end:t};
}

function playFigure(figure, baseDelay, factor) {
  const svg = figure.querySelector("svg");
  const {jobs} = prep(svg, 0, 1);
  const cap = 4200, est = jobs.length ? jobs[jobs.length-1].at + 400 : 0;
  /* compress, never stretch: a long plate fits the cap by DIVIDING its
     durations — multiplying them is how a 10s cover becomes 26s */
  const f = factor * Math.min(1, est / cap);
  svg.querySelectorAll("path, circle").forEach(el => el.getAnimations().forEach(a => a.cancel()));
  const {jobs: jobs2} = prep(svg, baseDelay, f);
  for (const j of jobs2) {
    if (j.kind === "dot") {
      j.el.style.transformBox = "fill-box";
      j.el.style.transformOrigin = "center";
      j.el.animate([
        {transform:"scale(0)"},
        {transform:"scale(1.35,.72)",offset:.55},
        {transform:"scale(.9,1.14)",offset:.78},
        {transform:"scale(1)"}],
        {duration:430, delay:j.at, fill:"both", easing:"ease-out"});
    } else if (j.kind === "dashed") {
      j.el.animate([{opacity:0},{opacity:j.el.getAttribute("opacity") ?? 1}],
        {duration:450, delay:j.at, fill:"both", easing:"ease-out"});
    } else {
      /* pathLength="100" normalizes dashing: use 100/100 + offset 100->0,
         while j.L (true length) only paces the duration */
      j.el.style.strokeDasharray = "100 100";
      j.el.animate([{strokeDashoffset:"100"},{strokeDashoffset:"0"}],
        {duration:j.dur, delay:j.at, fill:"both", easing:"ease-out"});
    }
  }
  return jobs2.length ? jobs2[jobs2.length-1].at : 0;
}

function playAll(factor, ambient) {
  const figures = document.querySelectorAll("figure.c");
  const perSection = {};
  let longestEnd = 0;
  document.querySelectorAll(".grid svg").forEach(s => s.classList.remove("alive"));
  figures.forEach(fig => {
    const section = fig.closest(".grid").id;
    const start = (perSection[section] ?? 0);
    perSection[section] = start + 130;
    const end = playFigure(fig, start, factor);
    longestEnd = Math.max(longestEnd, end);
  });
  const badge = document.getElementById("badge");
  badge.textContent = "运笔中……";
  clearTimeout(badge._t);
  badge._t = setTimeout(() => {
    badge.textContent = "墨迹已干 · 点图重播";
    /* auto-load honours the system's reduced-motion choice; an explicit
       replay click is the user asking to watch, so the loops wake up */
    if (ambient) document.querySelectorAll(".grid svg").forEach(s => s.classList.add("alive"));
  }, longestEnd + 400);
}

/* the ink bursts where you click — a dozen droplets ride one spring curve */
function burst(x, y) {
  const colors = ["#26221B", "#26221B", "#43392B", "#B4472F"];
  for (let i = 0; i < 12; i++) {
    const s = document.createElement("i");
    s.className = "spark";
    const a = (i / 12) * Math.PI * 2 + Math.random() * .5;
    const d = 22 + Math.random() * 30;
    s.style.left = x + "px"; s.style.top = y + "px";
    s.style.background = colors[i % colors.length];
    document.body.appendChild(s);
    const dx = Math.cos(a) * d, dy = Math.sin(a) * d - 8;
    const anim = s.animate([
      {transform:"translate(0,0) scale(1)",opacity:1},
      {transform:`translate(${dx}px,${dy + 14}px) scale(.25)`,opacity:0}],
      {duration:520 + Math.random() * 240, delay:i * 12,
       easing:SPRING, fill:"both"});
    anim.onfinish = () => s.remove();
  }
}

document.getElementById("replay").addEventListener("click", () => playAll(SPEEDS[speedIdx], true));
document.getElementById("speed").addEventListener("click", e => {
  speedIdx = (speedIdx + 1) % SPEEDS.length;
  e.target.textContent = "速度 ×" + SPEEDS[speedIdx];
});
function replayFigure(fig, cx, cy) {
  burst(cx, cy);
  fig.querySelector("svg").classList.add("alive");
  playFigure(fig, 0, SPEEDS[speedIdx] * 0.8);
}
document.querySelectorAll("figure.c").forEach(fig => {
  fig.addEventListener("click", e => replayFigure(fig, e.clientX, e.clientY));
  /* keyboard parity: Enter or Space replays from the card's own center */
  fig.addEventListener("keydown", e => {
    if (e.key !== "Enter" && e.key !== " ") return;
    e.preventDefault();
    const r = fig.getBoundingClientRect();
    replayFigure(fig, r.left + r.width / 2, r.top + r.height / 2);
  });
});

/* the title lands one character at a time, like a brush that cannot wait */
(function typeTitle() {
  const h1 = document.querySelector("header h1");
  const text = h1.textContent;
  h1.textContent = "";
  const reduce = matchMedia("(prefers-reduced-motion: reduce)").matches;
  [...text].forEach((ch, i) => {
    if (ch === " ") { h1.appendChild(document.createTextNode(" ")); return; }
    const c = document.createElement("span");
    c.className = "ttl-c";
    c.textContent = ch;
    h1.appendChild(c);
    if (reduce) return;
    c.animate(
      [{opacity:0, transform:"translateY(16px) rotate(4deg) scale(1.15)"},
       {opacity:1, transform:"translateY(0) rotate(0deg) scale(1)"}],
      {duration:520, delay:120 + i * 55, fill:"both",
       easing:"cubic-bezier(.34,1.56,.64,1)"});
  });
})();

if (matchMedia("(prefers-reduced-motion: reduce)").matches) {
  document.getElementById("motion-hint").textContent =
    "检测到系统减少动效：已静置为成品图；点「重播全部」或任意一张图，即观看运笔与角色循环。";
  document.getElementById("badge").textContent = "墨迹已干 · 点图重播";
} else {
  playAll(1, true);
}
</script>
</body>
</html>
"""

if __name__ == "__main__":
    main()
