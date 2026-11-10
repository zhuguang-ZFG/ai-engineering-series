"""docs/knowledge-cards.html (+ .en.html) — one 3:4 deck per chapter.

Three cards per chapter: the door-opener quote, the core mechanism in the
author's plain layer, and the three sentences the chapter asks a reader to
carry away. Every sentence comes from the BookModel; every drawing is a
plate the book already ships. No scripts, no external assets.
"""
from __future__ import annotations

from pathlib import Path

from ..labels import esc
from ..paths import BOOK_DIR, REPO_ROOT
from . import tokens
from .chapter_copy import content_plate, hook, recap
from .loader import load_repo_model

OUT = {"zh": "knowledge-cards.html", "en": "knowledge-cards.en.html"}

LABELS = {
    "zh": {
        "title": "御舆 · 知识卡",
        "sub": "十五章，每章三张 3:4 卡：一句话钩子、核心机制、三句带走。",
        "hint": ("全部素材取自本书自有插图；手机可读，打印时每张卡独立成页。"
                 "没有脚本，离线打开也是这个样子。"),
        "kicker_hook": "章钩子",
        "kicker_core": "核心机制",
        "kicker_recap": "三句带走",
        "deck": "张",
        "footer": ("回到 <a href=\"portal.html\">站点导航</a> · "
                   "<a href=\"beginner-reader.html\">入门分册</a> · "
                   "<a href=\"illustration-gallery.html\">插画画廊</a> · "
                   "对应大书 v@@BASELINE@@"),
    },
    "en": {
        "title": "Yù Yú · Knowledge Cards",
        "sub": ("Fifteen chapters, three 3:4 cards each: the one-line hook, "
                "the core mechanism, the three sentences to keep."),
        "hint": ("Every card is drawn from the book's own plates; readable on "
                 "a phone, and each card keeps to its own page in print. No "
                 "scripts, so it looks the same offline."),
        "kicker_hook": "The hook",
        "kicker_core": "Core mechanism",
        "kicker_recap": "Three to keep",
        "deck": "cards",
        "footer": ("Back to the <a href=\"portal.html\">site index</a> · "
                   "<a href=\"beginner-reader.en.html\">beginner reader</a> · "
                   "<a href=\"illustration-gallery.html\">illustration gallery</a> · "
                   "baseline v@@BASELINE@@"),
    },
}

PAGE = """<!doctype html>
<html lang="@@LANG@@">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="color-scheme" content="light">
@@FAVICON@@
<title>@@TITLE@@</title>
<meta property="og:title" content="@@TITLE@@">
<meta property="og:description" content="@@SUB@@">
<meta property="og:type" content="website">
<meta property="og:image" content="cover.png">
<style>
body{margin:0;font:15px/1.75 @@SERIF@@;background:#F5F0E6;color:#26221B}
header{padding:34px 30px 8px;max-width:1040px;margin:0 auto;text-align:center}
h1{font-size:26px;margin:0 0 4px;font-weight:650}
.brush{width:200px;height:9px;color:#B4472F;display:block;margin:2px auto 8px}
.sub{color:#5C5448;font-size:13.5px;margin:0}
.hint{color:#6E6353;font-size:12.5px;margin:8px 0 0}
main{max-width:1040px;margin:0 auto;padding:10px 30px 50px}
.ch{margin:26px 0 0}
.ch-head{display:flex;align-items:baseline;gap:12px;border-bottom:1px dashed rgba(38,34,27,.25);
  padding:0 0 8px;margin:0 0 14px}
.ch-no{margin:0;font-size:12px;letter-spacing:.14em;color:#9C3A26;white-space:nowrap}
.ch-head h2{font-size:19px;margin:0;font-weight:650}
.deck{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:16px}
.kcard{position:relative;aspect-ratio:3/4;border:1.5px solid rgba(38,34,27,.3);
  border-radius:@@RADIUS_CARD@@;padding:22px 20px 16px;
  display:flex;flex-direction:column;gap:9px;overflow:hidden;
  box-shadow:2px 3px 0 rgba(38,34,27,.08)}
.kcard::after{content:"";position:absolute;inset:7px;pointer-events:none;
  border:1px dashed rgba(38,34,27,.18);
  border-radius:@@RADIUS_RESUME@@}
.k-hook{background:#FBF6EC}
.k-core{background:#F3EAD8}
.k-recap{background:#EADFC7}
.k-kicker{margin:0;font-size:11.5px;letter-spacing:.18em;color:#B4472F}
.k-mark{width:58px;height:58px;color:#9C3A26;flex:0 0 auto}
.k-mark svg{width:100%;height:100%}
.k-quote{margin:0;font-size:16.5px;line-height:1.62;color:#26221B}
.k-quote::before{content:"“";color:#B4472F}
.k-quote::after{content:"”";color:#B4472F}
.k-plain{margin:0;font-size:13.5px;line-height:1.65}
.k-ana{margin:0;font-size:12.5px;line-height:1.6;color:#5C5448}
.k-plate{width:100%;height:auto;color:#5A5040;margin:auto 0}
.k-list{margin:0;padding:0;list-style:none;display:flex;flex-direction:column;gap:8px}
.k-list li{font-size:12.5px;line-height:1.55;padding-left:20px;position:relative}
.k-list li::before{counter-increment:kcard;content:counter(kcard);position:absolute;
  left:0;top:1px;width:15px;height:15px;line-height:15px;text-align:center;
  font-size:10px;color:#FBF6EC;background:#B4472F;border-radius:50%}
.k-list{counter-reset:kcard}
.k-foot{margin:auto 0 0;font-size:11px;letter-spacing:.12em;color:#675F4F}
footer{max-width:1040px;margin:34px auto 0;padding:16px 30px 40px;
  border-top:1px dashed rgba(38,34,27,.25);font-size:12.5px;color:#5C5448;text-align:center}
footer a{color:#3A5A78;text-decoration:none;border-bottom:1px dashed rgba(76,112,147,.5)}
footer a:hover{color:#B4472F}
a:focus-visible{outline:2px solid #B4472F;outline-offset:3px}
@media (max-width:820px){.deck{grid-template-columns:1fr}
  .kcard{aspect-ratio:auto;min-height:360px}}
@media print{body{background:#FFFDF8}
  header .hint,footer{display:none}
  .ch{break-before:page}
  .kcard{box-shadow:none;break-inside:avoid}
  .deck{grid-template-columns:repeat(3,minmax(0,1fr))}}
@media screen and (prefers-reduced-motion: reduce){
  footer a{transition:none}}
</style>
</head>
<body>
<header>
  <h1>@@TITLE@@</h1>
  @@BRUSH@@
  <p class="sub">@@SUB@@</p>
  <p class="hint">@@HINT@@</p>
</header>
<main>
@@DECKS@@
</main>
<footer>@@FOOTER@@</footer>
</body>
</html>
"""


def _svg(name: str) -> str:
    return (BOOK_DIR / "illustrations" / f"{name}.svg").read_text(
        encoding="utf-8").strip()


def cards_for(model, lang: str) -> list[dict]:
    labels = LABELS[lang]
    parts = {part.id: part for part in model.parts}
    out: list[dict] = []
    for unit in model.editions[lang].units:
        if unit.kind != "chapter":
            continue
        part = parts.get(unit.part_id)
        plate = content_plate(unit.id)
        out.append({
            "id": unit.id,
            "no": esc(unit.no),
            "title": esc(unit.title),
            "part": esc(f"{part.no[lang]} · {part.title[lang]}") if part else "",
            "hook": esc(hook(unit, lang)),
            "plain": esc(unit.guide.plain.get(lang, "")),
            "analogy": esc(unit.guide.analogy.get(lang, "")),
            "recap": [esc(item) for item in recap(unit, lang)],
            "emblem": _svg(unit.id),
            "plate": plate.read_text(encoding="utf-8").strip() if plate else "",
        })
    return out


def _deck(card: dict, labels: dict) -> str:
    recap_items = "".join(f"<li>{item}</li>" for item in card["recap"])
    plate = (f'<div class="k-plate" aria-hidden="true">{card["plate"]}</div>'
             if card["plate"] else "")
    return f"""<section class="ch" id="{card["id"]}" aria-labelledby="{card["id"]}-h">
  <div class="ch-head">
    <p class="ch-no">{card["part"]}</p>
    <h2 id="{card["id"]}-h">{card["no"]}　{card["title"]}</h2>
  </div>
  <div class="deck">
    <article class="kcard k-hook">
      <div class="k-mark" aria-hidden="true">{card["emblem"]}</div>
      <p class="k-kicker">{labels["kicker_hook"]}</p>
      <blockquote class="k-quote">{card["hook"]}</blockquote>
      <p class="k-foot">{card["no"]}</p>
    </article>
    <article class="kcard k-core">
      <p class="k-kicker">{labels["kicker_core"]}</p>
      {plate}
      <p class="k-plain">{card["plain"]}</p>
      <p class="k-ana">✦ {card["analogy"]}</p>
      <p class="k-foot">{card["no"]}</p>
    </article>
    <article class="kcard k-recap">
      <p class="k-kicker">{labels["kicker_recap"]}</p>
      <ol class="k-list">{recap_items}</ol>
      <p class="k-foot">{card["no"]}</p>
    </article>
  </div>
</section>"""


def page_for(model, lang: str) -> str:
    labels = LABELS[lang]
    decks = "\n".join(_deck(card, labels) for card in cards_for(model, lang))
    return (PAGE.replace("@@LANG@@", lang)
                .replace("@@TITLE@@", esc(labels["title"]))
                .replace("@@SUB@@", esc(labels["sub"]))
                .replace("@@HINT@@", esc(labels["hint"]))
                .replace("@@SERIF@@", tokens.SERIF_ZH if lang == "zh"
                         else tokens.SERIF_EN)
                .replace("@@BASELINE@@", model.version)
                .replace("@@FOOTER@@", labels["footer"].replace(
                    "@@BASELINE@@", model.version))
                .replace("@@DECKS@@", decks)
                .replace("@@RADIUS_CARD@@", tokens.RADIUS_CARD)
                .replace("@@RADIUS_RESUME@@", tokens.RADIUS_RESUME)
                .replace("@@FAVICON@@", tokens.FAVICON)
                .replace("@@BRUSH@@", tokens.BRUSH))


def build(lang: str) -> tuple[Path, int]:
    model = load_repo_model([lang])
    page = page_for(model, lang)
    out = REPO_ROOT / "docs" / OUT[lang]
    out.write_text(page, encoding="utf-8")
    return out, len(cards_for(model, lang))


def main() -> None:
    for lang in ("zh", "en"):
        out, count = build(lang)
        print(f"{out} ({count} decks)")
