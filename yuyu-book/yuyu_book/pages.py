"""Body page components; reader-facing labels live in labels.py."""
from __future__ import annotations

import html

from .labels import COLON, FRONT_NO, _LABELS, esc, note, ui

__all__ = ["COLON", "FRONT_NO", "_LABELS", "esc", "note", "ui"]

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
