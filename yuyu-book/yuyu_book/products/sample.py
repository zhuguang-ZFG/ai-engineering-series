"""docs/sample-chapter.html (+ .en.html) — chapter 2, the whole chapter.

The sample's promise is that a reader sees the real book, not a paraphrase:
the body is the chapter article as the book's own pipeline rendered it,
lifted from the built edition and rehosted in a standalone sheet. The hook
band and the recap card frame it; the book's stylesheet is embedded whole, so
the sheet keeps the ink system (including dark mode and print).

Chapter 2 is the chosen excerpt: the dialog loop is the book's heart, and it
is the chapter the reading paths put first.

Regenerate after a chapter edit (the book must be built first):

    python yuyu-book/build.py --lang both
    python scripts/build_sample_chapter.py
"""
from __future__ import annotations

import re
from pathlib import Path

from .. import style_css
from ..io import load_json
from ..labels import esc
from ..paths import BOOK_DIR, REPO_ROOT
from . import tokens
from .chapter_copy import hook, recap
from .loader import load_repo_model

CHAPTER = "ch02"
OUT = {"zh": "sample-chapter.html", "en": "sample-chapter.en.html"}
BOOK = {"zh": "yuyu-agent-harness-zh.html", "en": "yuyu-agent-harness-en.html"}

LABELS = {
    "zh": {
        "title": "样章 · 第 2 章 对话循环 —— 御舆",
        "kicker": "御舆 · 试读样章",
        "hint": "下文即完整版第 2 章原文，图版、表格与引文与正式版一致。",
        "recap": "三句话带走",
        "go": "在完整版继续读 →",
        "meta": ("完整版 v@@BASELINE@@ · "
                 "<a href=\"portal.html\">站点导航</a> · "
                 "<a href=\"knowledge-cards.html\">知识卡</a> · "
                 "<a href=\"beginner-reader.html\">入门分册</a>"),
        "foot": ("正文与插图取自《御舆：解码 Agent Harness》第 2 章，"
                 "由同一构建管线生成 · 大书内容 CC BY-NC-SA 4.0"),
    },
    "en": {
        "title": "Sample · Chapter 2 The Dialog Loop — Yù Yú",
        "kicker": "Yù Yú · Sample chapter",
        "hint": ("What follows is Chapter 2 exactly as the full edition ships "
                 "it — plates, tables and quotations included."),
        "recap": "Three sentences to keep",
        "go": "Continue in the full edition →",
        "meta": ("baseline v@@BASELINE@@ · "
                 "<a href=\"portal.html\">site index</a> · "
                 "<a href=\"knowledge-cards.en.html\">knowledge cards</a> · "
                 "<a href=\"beginner-reader.en.html\">beginner reader</a>"),
        "foot": ("Chapter 2 of Yù Yú: Decoding Agent Harness, rendered by the "
                 "same build pipeline · book text CC BY-NC-SA 4.0"),
    },
}

PAGE = """<!doctype html>
<html lang="@@HTML_LANG@@">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
@@FAVICON@@
<meta name="color-scheme" content="light dark">
<meta name="generator" content="yuyu-book">
<title>@@TITLE@@</title>
<meta property="og:title" content="@@TITLE@@">
<meta property="og:description" content="@@HINT@@">
<meta property="og:type" content="article">
<meta property="og:image" content="cover.png">
<style>
@@BOOK_CSS@@
/* ---- the sample sheet ------------------------------------------------
   The book's stylesheet is embedded above; everything below only frames
   one chapter and must paint from the same custom properties. */
body.sample{--measure:44rem}
.sp-hero{max-width:var(--furniture,56rem);margin:0 auto;
  padding:2.2rem 1.4rem 1.1rem;text-align:center}
.sp-kicker{font-family:var(--sans);font-size:.74rem;letter-spacing:.3em;
  color:var(--cinnabar);margin:0 0 .45rem}
.sp-mark{width:62px;height:62px;color:var(--bronze);margin:0 auto .2rem}
.sp-mark svg{width:100%;height:100%}
.sp-hero .brush{width:190px;height:10px;color:var(--cinnabar);
  display:block;margin:.35rem auto .85rem}
.sp-hook{max-width:34rem;margin:0 auto;font-size:1.02rem;line-height:1.85;
  color:var(--ink-2);border:0;padding:0;background:none}
.sp-hook::before{content:"“";color:var(--cinnabar)}
.sp-hook::after{content:"”";color:var(--cinnabar)}
.sp-hint{max-width:36rem;margin:.8rem auto 0;font-size:.8rem;
  color:var(--ink-3)}
.sp-meta{font-size:.78rem;color:var(--ink-3);margin:1rem 0 0}
.sp-meta a{color:var(--sky);text-decoration:none;
  border-bottom:1px dashed rgba(76,112,147,.5)}
.sample-main{max-width:64rem;margin:0 auto;padding:0 1.2rem 1rem}
.sample-main article.chapter{padding-top:1.2rem;break-before:auto}
.sp-recap{max-width:var(--measure);margin:2.2rem auto 3rem;
  padding:1.4rem 1.6rem 1.2rem;background:var(--paper-2);
  border:1.5px solid var(--line-2);
  border-radius:@@RADIUS_STATION@@;
  box-shadow:2px 3px 0 rgba(38,34,27,.08)}
.sp-recap h2{font-size:1.05rem;margin:0 0 .44rem;color:var(--ink)}
.sp-recap ol{margin:.3rem 0 1rem;padding-left:1.35rem}
.sp-recap li{margin:.34rem 0;font-size:.95rem;line-height:1.75}
.sp-go{display:inline-block;font-size:.88rem;color:var(--cinnabar);
  text-decoration:none;border-bottom:1.5px solid var(--cinnabar);
  padding-bottom:1px}
.sp-go:hover{color:var(--cinnabar-deep)}
.sp-foot{max-width:var(--furniture,56rem);margin:0 auto;
  padding:1.2rem 1.5rem 3rem;border-top:1px dashed var(--line-2);
  color:var(--ink-3);font-size:.8rem;text-align:center}
.sp-foot a{color:var(--sky);text-decoration:none;
  border-bottom:1px dashed rgba(76,112,147,.5)}
@media screen and (prefers-reduced-motion: reduce){
  .sp-go{transition:none}}
@media print{.sp-hero{padding-top:.6rem}.sp-recap{break-inside:avoid}}
</style>
</head>
<body class="lang-@@BODY_LANG@@ sample">
<header class="sp-hero">
  <p class="sp-kicker">@@KICKER@@</p>
  <div class="sp-mark" aria-hidden="true">@@MARK@@</div>
  @@BRUSH@@
  <blockquote class="sp-hook">@@HOOK@@</blockquote>
  <p class="sp-hint">@@HINT@@</p>
  <p class="sp-meta">@@META@@</p>
</header>
<main class="sample-main">
@@CHAPTER_HTML@@
<aside class="sp-recap" aria-labelledby="sp-recap-h">
  <h2 id="sp-recap-h">@@RECAP_LABEL@@</h2>
  <ol>
@@RECAP_ITEMS@@
  </ol>
  <a class="sp-go" href="@@BOOK@@#@@CHAPTER@@">@@GO@@</a>
</aside>
</main>
<footer class="sp-foot">@@FOOT@@</footer>
</body>
</html>
"""

_INTERNAL = re.compile(r'href="#((?:ch|apx|source)[\w-]*)"')


def _dist(lang: str) -> Path:
    prefix = (load_json(BOOK_DIR / "manifest.json").get("output_prefix")
              or "yuyu-agent-harness")
    return REPO_ROOT / "yuyu-book" / "dist" / f"{prefix}-{lang}.html"


def chapter_article(lang: str, unit_id: str = CHAPTER) -> str:
    """The rendered chapter, rehosted with its internal jumps retargeted."""
    dist = _dist(lang)
    if not dist.exists():
        raise SystemExit(f"sample chapter: {dist} is missing — build the book "
                         "first (python yuyu-book/build.py --lang both)")
    text = dist.read_text(encoding="utf-8")
    start = text.find(f'<article class="chapter" id="{unit_id}">')
    if start < 0:
        raise SystemExit(f"sample chapter: no <article id=\"{unit_id}\"> in "
                         f"{dist.name} — rebuild the book after the chapter "
                         "edit")
    end = text.find("<article class=", start + 10)
    if end < 0:
        end = text.find("</main>", start)
    if end < 0:
        end = len(text)
    chunk = text[start:end].rstrip()
    return _INTERNAL.sub(rf'href="{BOOK[lang]}#\1"', chunk)


def page_for(model, lang: str, body: str | None = None) -> str:
    labels = LABELS[lang]
    unit = model.unit(lang, CHAPTER)
    html_lang = "zh-CN" if lang == "zh" else "en"
    mark = (BOOK_DIR / "illustrations" / f"{CHAPTER}.svg").read_text(
        encoding="utf-8").strip()
    recap_items = "\n".join(f"    <li>{esc(item)}</li>"
                            for item in recap(unit, lang))
    return (PAGE.replace("@@HTML_LANG@@", html_lang)
                .replace("@@BODY_LANG@@", lang)
                .replace("@@BOOK_CSS@@", style_css.CSS)
                .replace("@@TITLE@@", esc(labels["title"]))
                .replace("@@KICKER@@", esc(labels["kicker"]))
                .replace("@@HOOK@@", esc(hook(unit, lang)))
                .replace("@@HINT@@", esc(labels["hint"]))
                .replace("@@MARK@@", mark)
                .replace("@@META@@", labels["meta"].replace(
                    "@@BASELINE@@", model.version))
                .replace("@@CHAPTER_HTML@@",
                         body if body is not None else chapter_article(lang))
                .replace("@@RECAP_LABEL@@", esc(labels["recap"]))
                .replace("@@RECAP_ITEMS@@", recap_items)
                .replace("@@BOOK@@", BOOK[lang])
                .replace("@@CHAPTER@@", CHAPTER)
                .replace("@@GO@@", esc(labels["go"]))
                .replace("@@FOOT@@", labels["foot"])
                .replace("@@RADIUS_STATION@@", tokens.RADIUS_STATION)
                .replace("@@FAVICON@@", tokens.FAVICON)
                .replace("@@BRUSH@@", tokens.BRUSH))


def build(lang: str) -> Path:
    model = load_repo_model([lang])
    page = page_for(model, lang)
    out = REPO_ROOT / "docs" / OUT[lang]
    out.write_text(page, encoding="utf-8")
    return out


def main() -> None:
    for lang in ("zh", "en"):
        out = build(lang)
        print(f"{out} ({out.stat().st_size} bytes)")
