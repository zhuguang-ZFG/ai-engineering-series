"""Front-matter page builders: cover, imprint, revisions, routes, TOC."""
from __future__ import annotations

from .pages import FRONT_NO, esc, note, tier_legend, ui

def cover(manifest: dict, lang: str) -> str:
    from .art import cover_plate
    from .style import wheel
    title = manifest["title"][lang]
    main, _, tail = title.partition("：")
    if main == title:
        main, _, tail = title.partition(":")
        tail = tail.strip()
    epigraph = manifest["epigraph"][lang]
    epi, _, epi_src = epigraph.rpartition("——")
    if not epi:
        epi, epi_src = epigraph, ""
    lic = manifest["license"]
    product = manifest.get("product", "book")
    is_agent = product in {"opencode", "deepseek", "hermes", "codex", "kimi", "prompt"}
    plate = cover_plate(lang, product)
    # the plate carries a 30-spoke wheel of its own; a second one under the
    # title would be the same motif twice within a hand's width
    mark = "" if plate else wheel(26)
    src_line = (f'<span class="epi-src">——{esc(epi_src.strip())}</span>'
                if epi_src else "")
    seal = (f'<span class="cover-seal" aria-hidden="true">{esc(main.strip()[:2])}</span>'
            if lang == "zh" and main.strip() and not is_agent else "")
    kicker = (manifest.get("kicker") or {}).get(lang) or ui("cover_kicker", lang)
    volume_class = f" agent-volume av-{product}" if is_agent else ""
    return (f'<section class="front-page cover{volume_class}" id="cover">'
            f'<div class="cover-inner">{seal}'
            f'<p class="cover-kicker">{esc(kicker)}</p>'
            f'<h1 class="book-title"><span class="bt-main">{esc(main.strip())}</span>'
            f'<span class="bt-tail">{esc(tail.strip())}</span></h1>'
            f'<div class="cover-rule"><i></i>{mark}<i></i></div>'
            f'{plate}'
            f'<p class="book-sub">{esc(manifest["subtitle"][lang])}</p>'
            f'<p class="book-epi">{esc(epi.strip())}{src_line}</p>'
            f'<div class="cover-foot">'
            f'<span class="book-author">{esc(manifest["author"])}</span>'
            f'<span class="cover-ver">v{esc(manifest["version"])} · '
            f'{esc(manifest["date"])} · <b>{esc(lic["name"])}</b></span>'
            f'</div></div></section>')


def imprint(manifest: dict, lang: str) -> str:
    lic = manifest["license"]
    rows = [
        (ui("author", lang), esc(manifest["author"])),
        (ui("edition", lang), f'v{esc(manifest["version"])}'),
        (ui("date", lang), esc(manifest["date"])),
        (ui("license", lang),
         f'<a class="ext" href="{lic["url"]}" rel="noopener">{esc(lic["name"])}</a>'),
    ]
    dl = "".join(f'<div class="ip-row"><dt>{k}</dt><dd>{v}</dd></div>'
                 for k, v in rows)
    notice = (manifest.get("notice") or {}).get(lang) or ui("notice_body", lang)
    return (f'<section class="front-page" id="imprint">'
            f'<h1 class="page-title">{esc(ui("imprint", lang))}</h1>'
            f'<dl class="imprint-list">{dl}</dl>'
            f'<h2 class="ip-notice-t">{esc(ui("notice", lang))}</h2>'
            f'<p class="ip-notice">{esc(notice)}</p></section>')


def revisions_page(entries: list[dict], lang: str) -> str:
    items = []
    for e in entries:
        lis = "".join(f"<li>{note(x)}</li>" for x in e.get(lang, []))
        items.append(f'<h2 class="rev-v">v{esc(e["version"])}'
                     f'<span class="rev-d">{esc(e["date"])}</span></h2><ul>{lis}</ul>')
    return (f'<section class="front-page" id="revisions">'
            f'<h1 class="page-title">{esc(ui("revisions", lang))}</h1>'
            f'{"".join(items)}</section>')


def how_to_read(manifest: dict, lang: str, paths: dict | None = None) -> str:
    cards = "".join(
        f'<div class="route-card"><h3>{esc(r["label"][lang])}</h3>'
        f'<p>{esc(r["body"][lang])}</p></div>'
        for r in manifest["start_reading"])
    parts = "".join(
        f'<li><a class="xref" href="#{p["units"][0]["id"]}">'
        f'{esc(p["no"][lang])} · {esc(p["title"][lang])}</a>'
        f'<span class="route-goal">{esc(p["goal"][lang])}</span></li>'
        for p in manifest["parts"])
    return (f'<section class="front-page" id="how-to-read">'
            f'<h1 class="page-title">{esc(ui("how", lang))}</h1>'
            f'<div class="route-grid">{cards}</div>'
            f'<ul class="route-parts">{parts}</ul>{tier_legend(paths, lang)}</section>')


def route_map_page(manifest: dict, lang: str, nos: dict[str, str]) -> str:
    """The whole book as one road, for the reader who wants to know how far it
    goes before opening it. The drawing is the ornament; the list under it is
    the thing itself, because the numbers written inside an `aria-hidden`
    picture are unreachable to a screen reader and carry no link."""
    from .style import itinerary, key_mark

    front = manifest["front"]["id"]
    front_stop = (front, nos.get(front, ""))
    side = [(a["id"], nos.get(a["id"], "")) for a in manifest["appendices"]]
    siding = f'{ui("appendix", lang)} · {ui("rm_side", lang)}'
    legs = [(f'{p["no"][lang]} · {p["title"][lang]}',
             [(u["id"], nos.get(u["id"], "")) for u in p["units"]])
            for p in manifest["parts"]]
    # the foreword is the wheel at the head of the road rather than a ring on
    # it: it is where the team harnesses up, not a station you travel to
    rows = [(front, ui("front", lang), [front_stop], ui("rm_why_front", lang))]
    rows += [(p["id"], head, stops, p["goal"][lang])
             for p, (head, stops) in zip(manifest["parts"], legs)]
    rows.append((side[0][0], siding, side, ui("rm_why_apx", lang)))

    def li(anchor: str, head: str, stops: list[tuple[str, str]], why: str) -> str:
        numbers = " ".join(n for _a, n in stops if n)
        return (f'<li><p class="rm-head"><a class="xref" href="#{anchor}">'
                f'{esc(head)}</a><span class="rm-nos">{esc(numbers)}</span></p>'
                f'<p class="rm-why">{esc(why)}</p></li>')

    keys = "".join(f'<li>{key_mark(kind)}{esc(ui(label, lang))}</li>'
                   for kind, label in (("wheel", "rm_key_wheel"),
                                       ("ring", "rm_key_ring"),
                                       ("siding", "rm_key_siding")))
    map_svg = itinerary("route",
                        [(esc(head), stops) for head, stops in legs]
                        + [(esc(siding), side)],
                        start_label=esc(nos.get(front, "")))
    lead = ui("route_map_lead", lang).format(
        chapters=sum(len(part["units"]) for part in manifest["parts"]))
    return (f'<section class="front-page route-map" id="route-map">'
            f'<h1 class="page-title">{esc(ui("route_map", lang))}</h1>'
            f'<p class="rm-lead">{esc(lead)}</p>'
            f'{map_svg}'
            f'<ul class="rm-key">{keys}</ul>'
            f'<ul class="rm-legs">{"".join(li(*r) for r in rows)}</ul></section>')


def part_divider(part: dict, lang: str, idx: int,
                 rows: list[tuple[str, str, str]]) -> str:
    from .style import route_map, wheel
    from . import art
    items = "".join(
        f'<li><a class="xref" href="#{anchor}" data-no="{esc(no)}">'
        f'{esc(label)}</a></li>'
        for anchor, no, label in rows)
    return (f'<section class="part-divider" id="{part["id"]}">'
            f'<span class="pd-ghost" aria-hidden="true">{wheel(360)}</span>'
            f'<div class="pd-inner">{art.headpiece(part["id"], lang)}'
            f'<p class="pd-no">{esc(part["no"][lang])}</p>'
            f'<h1 class="pd-title">{esc(part["title"][lang])}</h1>'
            f'<div class="cover-rule"><i></i>{wheel(24)}<i></i></div>'
            f'<p class="pd-motto">{esc(part["motto"][lang])}</p>'
            f'<p class="pd-goal">{esc(part["goal"][lang])}</p>'
            f'{route_map(part["id"], len(rows))}'
            f'<ol class="pd-list">{items}</ol>'
            f'</div></section>')


_ROMAN = ["", "Ⅰ", "Ⅱ", "Ⅲ", "Ⅳ", "Ⅴ", "Ⅵ", "Ⅶ", "Ⅷ"]


def toc_html(entries: list[dict], lang: str) -> str:
    """entries: {'kind': 'part'|'row'|'hr', 'anchor', 'no', 'title'}.
    Parts link to their divider page; rows carry a page-ref placeholder
    that the PDF pass stamps with the printed folio. Each part and its rows
    form one group, so a heading never strands itself on the previous page."""
    chunks: list[list[str]] = [[]]

    def close() -> None:
        if any(c.strip() for c in chunks[-1]):
            chunks.append([])

    for e in entries:
        kind = e["kind"]
        if kind in ("part", "hr"):
            close()
        if kind == "part":
            no = (f'<span class="tp-no">{esc(e["no"])}</span>'
                  if e["no"] else "")
            chunks[-1].append(
                f'<a class="toc-part" href="#{e["anchor"]}">{no}'
                f'<span class="tp-tx">{esc(e["title"])}</span>'
                f'<span class="page-ref" data-ref="{e["anchor"]}"></span></a>')
        elif kind == "hr":
            chunks[-1].append('<hr class="toc-hr">')
        else:
            chunks[-1].append(
                f'<a class="toc-row" href="#{e["anchor"]}">'
                f'<span class="toc-n">{esc(e["no"])}</span>'
                f'<span class="toc-t">{esc(e["title"])}</span>'
                f'<span class="leader"></span>'
                f'<span class="page-ref" data-ref="{e["anchor"]}"></span></a>')
    groups = "".join(f'<div class="toc-group">{"".join(c)}</div>'
                     for c in chunks if any(x.strip() for x in c))
    return (f'<section class="front-page toc" id="toc">'
            f'<h1 class="page-title">{esc(ui("toc", lang))}</h1>'
            f'{groups}</section>')


