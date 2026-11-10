"""Plate geometry, print caps and figure markup."""
from __future__ import annotations

import re

from . import mermaid, pages
from .core import Unit

# one pass over both kinds of plate, so a drawing that sits above a diagram
# cannot inherit the diagram's number
_PLATE_PH_RE = re.compile(
    r"<p>@@(MM:[0-9a-f]{12}|ILL:[0-9a-f]{12})@@</p>"
    r"|@@(MM:[0-9a-f]{12}|ILL:[0-9a-f]{12})@@")

_FLOOR_FROM = 1150.0
_FLOOR_RATIO = 0.85
_FLOOR_CAP = 2600.0
_VIEWBOX_RE = re.compile(r'viewBox="0 0 ([0-9.]+) ([0-9.]+)"')
_SVG_ROOT_RE = re.compile(r"<svg\b[^>]*>")


def floor_wide_svg(svg: str) -> tuple[str, str | None]:
    """Return (svg with a min-width floor, that floor in px or None).

    Only rendered plates are floored: --mermaid=source hands over a <pre>,
    which already wraps.
    """
    tag = _SVG_ROOT_RE.match(svg)
    if not tag:
        return svg, None
    head = tag.group(0)
    vb = _VIEWBOX_RE.search(head)
    if not vb:
        return svg, None
    vw = float(vb.group(1))
    if vw < _FLOOR_FROM:
        return svg, None
    floor = f"{round(min(vw * _FLOOR_RATIO, _FLOOR_CAP))}px"
    if " style=" in head:
        new = head.replace('style="', f'style="min-width:{floor};', 1)
    else:
        new = head[:4] + f' style="min-width:{floor};"' + head[4:]
    return svg[:tag.start()] + new + svg[tag.end():], floor


_PRINT_COL_PX = 665.0
_PRINT_CAP_PX = 567.0        # 150mm, style.py's default
_PRINT_MAX_PX = 926.0        # 245mm
_LAND_COL_PX = 993.0         # A4 landscape text block: 297mm - 2x17mm
_LAND_MAX_PX = 567.0         # 150mm — the sheet's own cap, see mermaid_figure
_MIN_PLATE_PT = 6.0          # what a plate must reach to stay portrait
_LAND_MIN_PLATE_PT = 5.0     # a turned sheet is held to a slightly lower bar
_PX_PER_MM = 96 / 25.4


def _plate_metrics(svg: str) -> tuple[float, float, float] | None:
    tag = _SVG_ROOT_RE.match(svg)
    if not tag:
        return None
    vb = _VIEWBOX_RE.search(tag.group(0))
    if not vb:
        return None
    fonts = [float(x) for x in re.findall(r"font-size:\s*([0-9.]+)px", svg)]
    return (float(vb.group(1)), float(vb.group(2)),
            max(fonts) if fonts else 16.0)


def plate_cap(svg: str) -> str | None:
    """Print height cap in mm for this plate, or None for the default."""
    m = _plate_metrics(svg)
    if not m:
        return None
    w, h, base = m
    need = _MIN_PLATE_PT / (base * 0.75)      # 1px = 0.75pt
    if w * need <= _PRINT_COL_PX and _PRINT_CAP_PX < h * need <= _PRINT_MAX_PX:
        return f"{h * need / _PX_PER_MM:.0f}mm"
    return None


def plate_landscape(svg: str) -> bool:
    """True when turning the sheet is what makes the plate readable."""
    m = _plate_metrics(svg)
    if not m:
        return False
    w, h, base = m
    here = base * min(_PRINT_COL_PX / w, _PRINT_CAP_PX / h) * 0.75
    turned = base * min(_LAND_COL_PX / w, _LAND_MAX_PX / h) * 0.75
    return here < _MIN_PLATE_PT and turned >= _LAND_MIN_PLATE_PT \
        and turned > here * 1.25


def mermaid_figure(uid: str, svg: str, fig_no: str, caption: str,
                   lang: str) -> str:
    cap_word = "图" if lang == "zh" else "Figure"
    svg, floor = floor_wide_svg(svg)
    classes = ["diagram"]
    if floor:
        classes.append("wide")
    land = plate_landscape(svg)
    if land:
        classes.append("landscape")
    hint = (f'<span class="fig-hint">{pages.ui("plate_wide", lang)}</span>'
            if floor else "")
    # A turned plate takes the sheet's default cap: the landscape block is
    # 170mm tall, so a cap of its own would push the caption onto a second sheet.
    cap = None if land else plate_cap(svg)
    style = f' style="--plate-cap:{cap}"' if cap else ""
    return (f'<figure class="{" ".join(classes)}" id="fig-{uid}"{style}>'
            f'<div class="diagram-frame">{svg}</div>'
            f'<figcaption><span class="fig-no">{cap_word} {fig_no}</span>'
            f'<span class="fig-cap">{caption}</span>{hint}</figcaption></figure>')


def drawing_slots(unit: Unit) -> dict[str, tuple[str, str]]:
    """The drawing each `ill` slot asks for, and the caption it earns.

    A plate borrows its caption from the section above it, the same rule a
    Mermaid plate follows, so the prose names a picture without describing it.
    """
    caps = mermaid.captions_for(unit.md, unit.ills,
                                fallback=pages.ui("plate_fallback", unit.lang))
    return {b.uid: (b.name, caps.get(b.uid, "")) for b in unit.ills}


def illu_figure(uid: str, svg: str, fig_no: str, caption: str,
                lang: str, kind: str = "line") -> str:
    """A hand-drawn plate inside the prose column.

    It borrows the diagram's caption furniture so the two read as one series,
    but not its scroll: a drawing is meant to be looked at, not scrolled
    sideways."""
    cap_word = "图" if lang == "zh" else "Figure"
    hint = (f'<span class="fig-hint">{pages.ui("plate_motion", lang)}</span>'
            if kind == "seq" else "")
    return (f'<figure class="illu illu-{kind}" id="fig-{uid}">'
            f'<div class="illu-frame">{svg}</div>'
            f'<figcaption><span class="fig-no">{cap_word} {fig_no}</span>'
            f'<span class="fig-cap">{caption}</span>{hint}</figcaption></figure>')
