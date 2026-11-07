"""docs/portal.html — the front door of the 御舆 ecosystem: full book,
beginner readers, illustration gallery, prompt handbook. Ink style, bilingual
labels, hand-cut cards.

The second-volume card is a <div>, not an <a>: omp has no deployed page yet,
and a card that links to nothing on this site would be the dead link the
portal is supposed to have none of.
"""
from pathlib import Path

from . import tokens
from .reader import LANGS, PLATES

COVER = "cover.png"

PAGE = """<!doctype html>
<html lang="zh">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="color-scheme" content="light">
@@FAVICON@@
<title>御舆 · 站点导航 — 解码 Agent Harness</title>
<meta property="og:title" content="御舆 · 站点导航 — 解码 Agent Harness">
<meta property="og:description" content="一本书、一册入门、一廊插画、一套知识卡、一页样章、一份手册——大书、双语入门分册、插画画廊、知识卡、样章与再生提示词手册，全部离线自包含。本站只发布御舆；同仓第二分册《Omp 从入门到精通：原理与实战》仍在施工中。">
<meta property="og:type" content="website">
<meta property="og:image" content="cover.png">
<style>
body{margin:0;font:16px/1.9 "Noto Serif SC","Source Han Serif SC","思源宋体","Songti SC","SimSun",Georgia,serif;background:#F5F0E6;color:#26221B}
header{padding:44px 30px 8px;max-width:860px;margin:0 auto;text-align:center}
h1{font-size:28px;margin:0 0 4px;font-weight:650}
.brush{width:210px;height:9px;color:#B4472F;display:block;margin:4px auto 10px}
.sub{color:#5C5448;font-size:14px}
.hint{color:#6E6353;font-size:12.5px;margin:12px 0 0}
.cover{display:block;margin:26px auto 6px;width:min(360px,80%);
  border:1.5px solid rgba(38,34,27,.3);border-radius:10px 6px 12px 6px/6px 12px 6px 10px;
  box-shadow:3px 4px 0 rgba(38,34,27,.14)}
main{max-width:860px;margin:0 auto;padding:14px 30px 56px}
.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:18px}
.card{display:block;background:#FFFDF8;border:1.5px solid rgba(38,34,27,.3);
  border-radius:10px 6px 12px 6px/6px 12px 6px 10px;padding:20px 22px;
  text-decoration:none;color:#26221B;box-shadow:2px 3px 0 rgba(38,34,27,.1);
  transition:transform .18s cubic-bezier(.34,1.56,.64,1),box-shadow .18s ease,border-color .18s ease;
  animation:card-in .7s cubic-bezier(.22,.9,.3,1) both}
.card:nth-child(1){animation-delay:.1s}
.card:nth-child(2){animation-delay:.22s}
.card:nth-child(3){animation-delay:.34s}
.card:nth-child(4){animation-delay:.46s}
.card:nth-child(5){animation-delay:.58s}
.card:nth-child(6){animation-delay:.7s}
.card:nth-child(7){animation-delay:.82s}
@keyframes card-in{from{opacity:0;transform:translateY(18px) rotate(-.8deg)}}
@media screen and (prefers-reduced-motion: reduce){
  a.card{animation:none;transition:box-shadow .18s ease,border-color .18s ease}
  div.card{animation:none;transition:none}
  a.card:hover{transform:none}}
a.card:hover{transform:translateY(-3px) rotate(-.4deg);border-color:#B4472F;
  box-shadow:3px 5px 0 rgba(180,71,47,.22)}
.card div.soon{margin-top:10px;font-size:12px;color:#675F4F}
.card div.soon code,.card p code{font-family:ui-monospace,Menlo,Consolas,monospace;font-size:12.5px}
.card h2{font-size:17px;margin:0 0 6px}
.card h2 .ico{margin-right:6px}
.card p{margin:0;font-size:13px;color:#5C5448;line-height:1.7}
.card .go{display:inline-block;margin-top:10px;font-size:12px;color:#B4472F;
  border-bottom:1.5px solid #B4472F;padding-bottom:1px;text-decoration:none}
.card .alt{display:block;margin-top:8px;font-size:11.5px;color:#675F4F}
.card .alt a{color:#4C7093;text-decoration:none;border-bottom:1px dashed rgba(76,112,147,.5)}
footer{max-width:860px;margin:0 auto;padding:0 30px 46px;color:#675F4F;font-size:12px;text-align:center}
footer a{color:inherit}
a:focus-visible{outline:2px solid #B4472F;outline-offset:3px}
</style>
</head>
<body>
<header>
  <h1>御舆 · 站点导航</h1>
  @@BRUSH@@
  <p class="sub">解码 Agent Harness —— 一本书、一册入门、一廊插画、一套知识卡、一页样章、一份手册｜第二分册《Omp 从入门到精通》在仓库施工中</p>
  <p class="hint">全部页面离线自包含、无脚本依赖（入门分册与画廊内建的动效除外）；
  由 GitHub Actions 每次推送自动构建发布。</p>
  <img class="cover" src="cover.png" alt="御舆：解码 Agent Harness 封面">
</header>
<main>
  <div class="cards">
    <div class="card">
      <h2><span class="ico">📖</span>大书 · 御舆：解码 Agent Harness<span lang="en"></span></h2>
      <p>全书 15 章 + 4 附录：对话循环、工具、权限、记忆、上下文、钩子、子智能体、
      编排、技能、MCP、流式、Plan、亲手造一个 Harness。滚动阅读时，@@PLATES@@ 幅手绘插图
      与按书的配色预渲染的图版会随你前进。</p>
      <a class="go" href="book.html">开始阅读 →</a>
      <span class="alt">English edition: <a href="yuyu-agent-harness-en.html">Yù Yú (English)</a></span>
    </div>
    <div class="card">
      <h2><span class="ico">🧭</span>第二分册 · Omp 从入门到精通（施工中）</h2>
      <p>同仓第二本书：《Omp 从入门到精通：原理与实战》——开源终端 agent 的非官方教程，
      中文单语，与御舆共用构建器与图版管线，产物前缀 <code>yuyu-omp-*</code>。</p>
      <p>本站只发布御舆，这张卡因此不带链接——带了就是一条死链；omp 上线要等它的书稿进 main。</p>
      <div class="soon">本地构建：<code>make book-omp</code>（中文 HTML）／<code>make book-omp-pdf</code>（再加 A4 PDF）</div>
      <span class="alt">书稿与构建口径在仓库内的 <code>omp/</code> 目录。</span>
    </div>
    <a class="card" href="beginner-reader.html">
      <h2><span class="ico">🌱</span>入门分册 · 看图读懂<span lang="en"></span></h2>
      <p>人人可读的 @@STATIONS_ZH@@ 站看图入门：每站一幅手绘插图、一句白话、一个比方、
      一句记忆、一道自测、一段视频。由浅入深——底色一层比一层深。</p>
      <span class="go">15 分钟入门 →</span>
    </a>
    <a class="card" href="beginner-reader.en.html" hreflang="en">
      <h2><span class="ico">🌱</span>Beginner reader · illustrated<span lang="en"></span></h2>
      <p>The same @@STATIONS_EN@@-station picture walk in English — plain language,
      shallow to deep, every station with a sketch, a takeaway, a self-check
      and curated videos.</p>
      <span class="go">15-minute on-ramp →</span>
    </a>
    <a class="card" href="illustration-gallery.html">
      <h2><span class="ico">🎨</span>插画画廊 · 看图说话<span lang="en"></span></h2>
      <p>@@PLATES@@ 幅手绘插图的中英双语题注画廊：点击任意一幅，看墨线逐笔重演、
      悬停读白话、点击迸发墨点。</p>
      <span class="go">逛画廊 →</span>
    </a>
    <div class="card">
      <h2><span class="ico">🗂️</span>知识卡 · 一章三张<span lang="en"></span></h2>
      <p>十五章各三张 3:4 手绘卡：一句话钩子、核心机制、三句带走。
      手机一屏一张，打印时每张卡独立成页。</p>
      <a class="go" href="knowledge-cards.html">抽卡复习 →</a>
      <span class="alt">English: <a href="knowledge-cards.en.html">knowledge cards</a></span>
    </div>
    <div class="card">
      <h2><span class="ico">📜</span>样章 · 试读第 2 章<span lang="en"></span></h2>
      <p>从全书的心脏「对话循环」读起：完整一章正文、图版、表格与引文，
      由同一构建管线生成，单文件离线可开。</p>
      <a class="go" href="sample-chapter.html">免费试读 →</a>
      <span class="alt">English: <a href="sample-chapter.en.html">sample chapter</a></span>
    </div>
  </div>
</main>
<footer>
  画风体系来自 <a href="https://github.com/yang0/handraw-style">yang0/handraw-style</a>
  （MIT with Attribution）· 提示词手册见
  <a href="illustration-prompts.md">docs/illustration-prompts.md</a> ·
  大书内容 CC BY-NC-SA 4.0
</footer>
</body>
</html>
"""

# Counts come from the reader builder and the plates on disk, so the front door
# cannot quote a stale number.
PAGE = (PAGE.replace("@@STATIONS_ZH@@", str(LANGS["zh"]["total"]))
           .replace("@@STATIONS_EN@@", str(LANGS["en"]["total"]))
           .replace("@@PLATES@@", str(PLATES))
           .replace("@@FAVICON@@", tokens.FAVICON)
           .replace("@@BRUSH@@", tokens.BRUSH))


def write(out: Path) -> Path:
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(PAGE, encoding="utf-8")
    return out
