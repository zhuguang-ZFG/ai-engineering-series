"""Back-matter page builders: sources, index, principles, keeper notes."""
from __future__ import annotations

import re

from .core import BuildError, INDEX_CN_LETTER
from .pages import esc, src_field, ui

KIND_GROUP = {
    "zh": {"github": "GitHub 仓库与发布", "docs": "官方文档", "blog": "工程博客",
           "spec": "协议规范", "npm": "npm 包", "community": "社区材料（非规范）"},
    "en": {"github": "GitHub repositories & releases", "docs": "Official docs",
           "blog": "Engineering blog", "spec": "Protocol specs",
           "npm": "npm packages", "community": "Community (non-normative)"},
}


def source_registry(sources: dict, lang: str) -> str:
    order = ["github", "npm", "docs", "blog", "spec", "community"]
    groups: dict[str, list] = {k: [] for k in order}
    for sid, src in sources.items():
        groups.setdefault(src.get("kind", "docs"), []).append((sid, src))
    parts = [
        f'<section class="front-page sources" id="sources">'
        f'<h1 class="page-title">{esc(ui("sources_page", lang))}</h1>'
        f'<p class="reg-note">{esc(ui("sources_note", lang))}</p>']
    for kind in order:
        items = groups.get(kind) or []
        if not items:
            continue
        parts.append(f'<h2 class="reg-kind"><span class="rk-tx">{esc(KIND_GROUP[lang][kind])}</span>'
                     f'<span class="rk-n">{len(items)}</span></h2><ul class="reg-list">')
        for num, (sid, src) in enumerate(items, 1):
            pinned = src.get("pinned") or {}
            pin = ""
            if pinned.get("tag"):
                pin += f' · tag <code>{esc(pinned["tag"])}</code>'
            if pinned.get("commit"):
                pin += f' · commit <code>{esc(pinned["commit"][:10])}</code>'
            if pinned.get("version"):
                pin += f' · v<code>{esc(pinned["version"])}</code>'
            scope = src_field(src, "scope", lang)
            parts.append(
                f'<li id="source-{sid}"><div class="reg-head">'
                f'<span class="reg-no">{num:02d}</span>'
                f'<a class="ext" href="{esc(src["url"])}" rel="noopener">'
                f'{esc(src_field(src, "title", lang))}</a>'
                f'<span class="reg-auth">{esc(src_field(src, "authority", lang))}</span>'
                f'<span class="reg-pin">{pin}</span></div>'
                f'<div class="reg-meta">{esc(src_field(src, "snapshot", lang))} · '
                f'{esc(src_field(src, "license", lang))}</div>'
                f'<div class="reg-scope">{esc(scope)}</div></li>')
        parts.append("</ul>")
    parts.append("</section>")
    return "".join(parts)


def subject_index_page(entries: list[dict], lang: str) -> str:
    letters: dict[str, list] = {}
    for e in entries:
        if not e[lang]["refs"]:
            continue  # a headword this edition has no rows for
        letters.setdefault(e["letter"], []).append(e)
    parts = [f'<section class="front-page back-index" id="subject-index">'
             f'<h1 class="page-title">{esc(ui("index_page", lang))}</h1>'
             f'<div class="idx-cols">']
    for letter in sorted(letters):
        cn = letter == INDEX_CN_LETTER
        head = ui("index_cn", lang) if cn else esc(letter)
        parts.append(f'<div class="idx-block"><h2 class="idx-letter">{head}</h2>'
                     + (f'<p class="idx-note">{esc(ui("index_cn_note", lang))}</p>'
                        if cn else '')
                     + '<ul class="idx-list">')
        for e in letters[letter]:
            # a 23-character feature flag has no space to break at, and the row
            # would spend its dotted leader to fit it; `<wbr>` after each
            # underscore gives the name a place to end instead, and is used only
            # when the entry genuinely cannot fit on one line
            term = esc(e[lang]["term"]).replace("_", "_<wbr>")
            refs = "".join(
                f'<a class="xref" href="#{r["anchor"]}">{esc(r["label"])}</a>'
                for r in e[lang]["refs"])
            parts.append(f'<li class="idx-row"><span class="idx-term">{term}</span>'
                         f'<span class="leader"></span>'
                         f'<span class="idx-refs">{refs}</span>'
                         f'<span class="page-ref idx-ref" '
                         f'data-ref="{e[lang]["refs"][0]["anchor"] if e[lang]["refs"] else ""}"></span></li>')
        parts.append("</ul></div>")
    parts.append("</div></section>")
    return "".join(parts)


IDX_SLOT = re.compile(r'<span class="page-ref idx-ref" data-ref="([^"]*)"></span>')


def fill_index_folios(html_text: str, folios: dict[str, int]) -> str:
    """Write each index row's printed page number into the slot it reserves.

    The row is keyed by the anchor it links to, never by the headword: `Session`
    and `SessionStart` print almost the same line, so any pass that looked for
    the term in the printed sheet could hand `SessionStart` the other's number.
    A slot with no folio, or a folio whose anchor never reached the page, is a
    build failure rather than an index that quietly stops mid-column.
    """
    hit: list[str] = []

    def ink(m: re.Match) -> str:
        anchor = m.group(1)
        hit.append(anchor)
        if anchor not in folios:
            raise BuildError(
                f"index: no page number for {anchor!r} — the sheet would print "
                "an empty folio slot")
        return (f'<span class="page-ref idx-ref" data-ref="{anchor}">'
                f"{folios[anchor]}</span>")

    filled = IDX_SLOT.sub(ink, html_text)
    unknown = sorted(set(folios) - set(hit))
    if unknown:
        raise BuildError(
            f"index: {len(unknown)} folio(s) with no row to fill "
            f"({unknown[:8]}) — the index and the page disagree")
    return filled


def principles_page(groups: list[dict], lang: str) -> str:
    """The mechanism layer, on paper.

    A hover card cannot reach the printed book, so the reasons a term exists
    would otherwise live only in the HTML. Each row is one term: the reason,
    then the picture the book uses for it.
    """
    parts = [f'<section class="front-page back-why" id="principles">'
             f'<h1 class="page-title">{esc(ui("principles_page", lang))}</h1>'
             f'<p class="pr-note">{esc(ui("principles_note", lang))}</p>']
    why_tag, ana_tag = ui("why_tag", lang), ui("analogy_tag", lang)
    for g in groups:
        rows = []
        for t in g["terms"]:
            row = (f'<li class="pr-row"><b class="pr-term">{esc(t["term"])}</b>'
                   f'<span class="pr-why"><i class="pr-t">{esc(why_tag)}</i>'
                   f'{esc(t["why"])}</span>')
            if t["analogy"]:
                row += (f'<span class="pr-ana"><i class="pr-t">{esc(ana_tag)}</i>'
                        f'{esc(t["analogy"])}</span>')
            rows.append(row + "</li>")
        parts.append(
            f'<div class="pr-unit"><h2 class="pr-head">'
            f'<a class="xref" href="#{esc(g["anchor"])}">{esc(g["head"])}</a>'
            f'<span class="pr-n">{len(g["terms"])}</span></h2>'
            f'<ul class="pr-list">{"".join(rows)}</ul></div>')
    parts.append("</section>")
    return "".join(parts)


def notes_page(notes: dict, units, lang: str) -> str:
    """The twenty lines of the old postman, walked once more in order.

    One row per unit in reading order; the head links back to the chapter's
    own ruts, because a note taken out of its ending loses its timing."""
    parts = [f'<section class="front-page back-notes" id="keeper-notes">'
             f'<h1 class="page-title">{esc(ui("notes_page", lang))}</h1>'
             f'<p class="pr-note">{esc(ui("notes_note", lang))}</p>'
             f'<ul class="kn-list">']
    for u in units:
        body = (notes.get(u.id) or {}).get(lang)
        if not body:
            continue
        # the gutter label, not the full title: a row whose head wraps to three
        # lines stops being an index and becomes a table of contents
        label = getattr(u, "eyebrow", None) or u.display
        parts.append(
            f'<li class="kn-row"><b class="kn-head">'
            f'<a class="xref" href="#{esc(u.anchor)}" title="{esc(u.display)}">'
            f'{esc(label)}</a>'
            f'</b><span class="kn-note">{esc(body)}</span></li>')
    parts.append("</ul></section>")
    return "".join(parts)
