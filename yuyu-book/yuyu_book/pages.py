"""Front/back-matter page builders: cover, imprint, revisions, reading
guide, compass cards, part dividers, TOC, source registry, subject index."""
from __future__ import annotations

import html
import re

from .plain import ANALOGY_TAG, WHY_TAG  # noqa: E402

_LABELS = {
    "cover_kicker": {"zh": "Agent Harness Engineering",
                     "en": "Agent Harness Engineering"},
    "imprint": {"zh": "版本与许可", "en": "Imprint"},
    "revisions": {"zh": "版本与修订", "en": "Revision history"},
    "how": {"zh": "阅读路线", "en": "How to read"},
    "toc": {"zh": "目录", "en": "Contents"},
    "author": {"zh": "著", "en": "Author"},
    "edition": {"zh": "版本", "en": "Edition"},
    "date": {"zh": "日期", "en": "Date"},
    "license": {"zh": "许可", "en": "License"},
    "notice": {"zh": "声明", "en": "Notice"},
    "notice_body": {
        "zh": "Claude Code 为 Anthropic 产品；本书是独立的技术分析作品，并非官方出版物。"
              "阅读时请区分源码可确认的行为、架构推演与教学示例；功能标志与工具可用性取决于构建和运行时配置。",
        "en": "Claude Code is an Anthropic product; this book is an independent technical "
             "analysis, not an official publication. Distinguish observed implementation, "
             "architectural interpretation, and teaching examples; flags and tool "
             "availability depend on build and runtime configuration."},
    "sources_page": {"zh": "来源与许可", "en": "Sources & Licenses"},
    "sources_note": {
        "zh": "本书不转载来源正文；GitHub 参考钉住 tag/commit，社区材料标注访问日期且非规范。",
        "en": "The book does not republish source texts; GitHub references are pinned to "
             "tags/commits, community material carries access dates and is non-normative."},
    "index_page": {"zh": "主题索引", "en": "Subject Index"},
    "principles_page": {"zh": "原理札记", "en": "Why It Works This Way"},
    "notes_page": {"zh": "按语集", "en": "The Keeper's Notes"},
    "notes_note": {
        "zh": "每一章都收在它自己的车辙上；车辙上方另有一句按语，出自一位"
              "赶了三十年驿路的老驿卒。他不解释术语，只回头看看刚走完的"
              "这段路。这一页把二十条按语照原路再走一遍，每条链回章末。",
        "en": "Every unit closes on its own wheel ruts, and above them stands "
             "one line by an old postman who has ridden this road for thirty "
             "years. He explains nothing; he only looks back over the leg "
             "just travelled. This page walks all twenty lines in order, each "
             "linked back to the ruts it sat on."},
    "principles_note": {
        "zh": "书里的核心术语各有一句白话定义和一个比方；这一页补上中间那层——"
              "它非这样不可的理由。理由一律取自正文自己的论证，条目排在提出它的那一章下面。",
        "en": "Every core term carries a plain definition and an everyday "
             "comparison; this page supplies the layer in between, the reason it "
             "has to be that way. Each reason is the book's own argument, filed "
             "under the chapter that makes it."},
    "why_tag": WHY_TAG,
    "analogy_tag": ANALOGY_TAG,
    "index_cn": {"zh": "中文", "en": "Chinese"},
    "index_cn_note": {
        "zh": "按译名首字的部首笔画排列；一个英文术语有多个译名时，每个译名单独立条。",
        "en": "Filed by the radical and stroke count of the first character; a "
              "term with several translations is filed under each of them."},
    "compass_q": {"zh": "本章问题", "en": "The question"},
    "compass_d": {"zh": "读完交付", "en": "What you get"},
    "compass_b": {"zh": "本章边界", "en": "Out of scope"},
    "compass_src": {"zh": "来源锚点", "en": "Source anchors"},
    "front": {"zh": "前言", "en": "Foreword"},
    "appendix": {"zh": "附录", "en": "Appendix"},
    "diagrams": {"zh": "全书图版", "en": "Plates in this book"},
    "plate_fallback": {"zh": "架构示意", "en": "Architecture sketch"},
    "plate_wide": {"zh": "可横向拖动", "en": "drag sideways"},
    "plate_motion": {"zh": "悬停播放", "en": "hover to play"},
    "lead_tag": {"zh": "一句话讲明白", "en": "In plain words"},
    "lead_analogy": {"zh": "打个比方：", "en": "Think of it as: "},
    "new_terms": {"zh": "本章新词", "en": "New terms in this chapter"},
    "new_terms_front": {"zh": "开篇新词", "en": "New terms in the foreword"},
    "new_terms_appendix": {"zh": "本附录新词",
                           "en": "New terms in this appendix"},
    "new_terms_note": {
        "zh": "正文里带虚线的词都收在这里；其余术语见附录 D 术语表。",
        "en": "Every dashed term in the text is listed here; Appendix D covers "
             "the rest."},
    "tier_legend": {"zh": "阅读层级", "en": "Reading tiers"},
    "tier_hint": {
        "zh": "每个二级小节右上角标了层级：起步可先读，主干要读，进阶可以跳。"
              "术语首次出现带虚线，鼠标悬停或点按出白话注释。",
        "en": "Every section carries a level at its right: read Start first, "
             "Core is required, Advanced can wait. Dashed terms reveal a "
             "plain-language note on hover or tap."},
    "route_map": {"zh": "全书线路图", "en": "The Book's Route"},
    "route_map_lead": {
        "zh": "把全书想成一条路：前言套车出发，十五章是路上依次排开的驿站，"
              "附录是停在路边的岔线，随时可以折过去取个东西再回来。",
        "en": "Think of the book as one road: the foreword harnesses the team, "
             "the fifteen chapters are the stations set out along it, and the "
             "appendices are a siding you can turn into whenever you need "
             "something and come back."},
    "rm_key_wheel": {"zh": "轮：前言发车", "en": "Wheel: the ride starts here"},
    "rm_key_ring": {"zh": "圈：一章一站", "en": "Ring: one chapter per stop"},
    "rm_key_siding": {"zh": "虚线：附录是岔线", "en": "Dashed: the appendices, a siding"},
    "rm_side": {"zh": "支线", "en": "Siding"},
    "rm_why_front": {"zh": "上车前先读：这本书在讲什么、怎么讲。",
                     "en": "Read before you set off: what this book covers and how."},
    "rm_why_apx": {"zh": "随时折回去查：源码地图、工具清单、功能标志、术语表。",
                   "en": "Turn back any time: the source map, the tool inventory, "
                        "the flag list, the glossary."},
}


def ui(key: str, lang: str) -> str:
    return _LABELS[key][lang]


# the full-width colon is ours to choose, and the English book should not wear it
COLON = {"zh": "：", "en": ":"}

# the foreword is the one unit with no chapter number, so the book gives it the
# gutter number 00 -- the contents row and the route map's wheel both wear it
FRONT_NO = "00"


def esc(s: str) -> str:
    return html.escape(s, quote=False)


_NOTE_CODE = re.compile(r"`([^`]+)`")


def note(s: str) -> str:
    """A revision note, marked up: the notes quote the builder's own names, and
    a row of raw backticks around one reads as a typo in a typeset book."""
    out, prev = [], 0
    for m in _NOTE_CODE.finditer(s):
        out.append(esc(s[prev:m.start()]))
        out.append(f"<code>{esc(m.group(1))}</code>")
        prev = m.end()
    out.append(esc(s[prev:]))
    return "".join(out)


def tier_legend(paths: dict | None, lang: str) -> str:
    """How many sections sit at each level, so a reader can size the shortcut."""
    if not paths:
        return ""
    from .plain import TIER_DESC, TIER_LABELS, TIER_ORDER

    counts = {t: sum(1 for tiers in paths.values()
                     for x in tiers if x == t) for t in TIER_ORDER}
    rows = "".join(
        f'<li class="tl-row"><span class="tier-chip t-{t}">'
        f'{esc(TIER_LABELS[t][lang])}</span>'
        f'<span class="tl-desc">{esc(TIER_DESC[t][lang])}</span>'
        f'<span class="tl-n tl-n-{t}">{counts[t]}</span></li>'
        for t in TIER_ORDER)
    return (f'<div class="tier-legend"><h2 class="page-sub">'
            f'{esc(ui("tier_legend", lang))}</h2>'
            f'<p class="tl-hint">{esc(ui("tier_hint", lang))}</p>'
            f'<ul class="tl-list">{rows}</ul></div>')


def lead_band(guide: dict, lang: str) -> str:
    """The one plain-language device that reads the same on paper and screen."""
    plain = (guide.get("plain") or {}).get(lang) or ""
    if not plain:
        return ""
    analogy = (guide.get("analogy") or {}).get(lang) or ""
    a = (f'<p class="lb-analogy"><span class="lb-a-tag">'
         f'{esc(ui("lead_analogy", lang))}</span>{esc(analogy)}</p>'
         if analogy else "")
    return (f'<div class="lead-band"><p class="lb-tag">'
            f'{esc(ui("lead_tag", lang))}</p>'
            f'<p class="lb-plain">{esc(plain)}</p>{a}</div>')


def new_terms_panel(hits: list[dict], lang: str, kind: str = "") -> str:
    """Paper has no hover, so the dashed terms a reader meets in this unit are
    restated here in document order — the marks and this list are the same
    set, which the build asserts."""
    if not hits:
        return ""
    title = ui("new_terms" if kind in ("", "chapter") else f"new_terms_{kind}",
               lang)
    rows = "".join(
        f'<li class="nt-row"><span class="nt-term">{esc(h["term"])}</span>'
        f'<span class="nt-plain">{esc(h["plain"])}</span></li>'
        for h in hits)
    return (f'<aside class="new-terms"><h4 class="nt-title">'
            f'{esc(title)}'
            f'<span class="nt-n">{len(hits)}</span></h4>'
            f'<p class="nt-note">{esc(ui("new_terms_note", lang))}</p>'
            f'<ul class="nt-list">{rows}</ul></aside>')


def compass(unit, guide: dict, sources: dict, lang: str) -> str:
    # the labels say 本章, which is true of a chapter only: the foreword opens
    # the whole book and the appendices are not chapters
    scope = {"front": "全书", "appendix": "本附录"}.get(getattr(unit, "kind", ""), "")

    def tag(label: str) -> str:
        text = ui(label, lang)
        return scope + text[2:] if scope and text.startswith("本章") else text

    cards = "".join(
        f'<div class="compass-card {key}">'
        f'<h4 class="cc-tag">{esc(tag(label))}</h4>'
        f'<p>{esc(guide[key][lang])}</p></div>'
        for key, label in (("question", "compass_q"),
                           ("deliverable", "compass_d"),
                           ("boundary", "compass_b")))
    chips = ""
    if guide.get("sources"):
        names = {sid: src_field(sources.get(sid, {}), "title", lang) or sid
                 for sid in guide["sources"]}
        chips = ('<p class="cc-src"><span class="cc-src-t">'
                 f'{esc(ui("compass_src", lang))}{COLON[lang]}</span>' +
                 "".join(
                     f'<a class="source-chip" href="#source-{sid}" '
                     f'title="{html.escape(names[sid], True)}">'
                     f'{esc(names[sid])}</a>'
                     for sid in guide["sources"]) + "</p>")
    return (f'<div class="compass" role="complementary">{cards}{chips}</div>')


def src_field(src: dict, key: str, lang: str) -> str:
    """Registry text in the reader's language. Anything annotated by us carries
    a `_<key>_en` mirror when the base text is Chinese; third-party names are as
    published, so a Chinese forum thread keeps the title it was posted under."""
    return str(src.get(f"{key}_{lang}") or src.get(key, ""))


# Re-export the split page builders so callers keep importing `pages`.
from .backmatter import (KIND_GROUP, IDX_SLOT, fill_index_folios,  # noqa: E402
                         notes_page, principles_page, source_registry,
                         subject_index_page)
from .frontmatter import (FRONT_NO, _ROMAN, cover, how_to_read,  # noqa: E402
                          imprint, part_divider, revisions_page,
                          route_map_page, toc_html)
