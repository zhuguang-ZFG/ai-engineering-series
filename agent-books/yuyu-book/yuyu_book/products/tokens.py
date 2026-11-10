"""Design tokens shared by every generated page.

The book's own custom properties live in ``style_tokens``. This module is the
product-side mirror: the inks, papers, surfaces and accents that the portal,
the two beginner readers and the illustration gallery may paint with, plus the
three font stacks, the hand-cut corner radii and the two marks those pages
reuse. A product may not introduce a colour of its own — the palette gate in
``tests/test_product_tokens.py`` scans every shipped page and fails on a hex or
``rgba()`` triplet that is not listed here.

Values are the book's tokens wherever the book has one. ``BOOK_MIRROR`` names
the custom property each shared value must match; the same test parses
``style_tokens`` and compares them, so the two stylesheets cannot drift.
"""
from __future__ import annotations

# --------------------------------------------------------------------------
# palette
# --------------------------------------------------------------------------
# The book's palette (mirrored by name into TOKENS; kept as literals here so a
# product page can be generated without importing the whole builder).
PALETTE: dict[str, str] = {
    # paper and cards
    "paper-0": "#FBF6EC",       # the lightest station / hero band
    "paper": "#F5F0E6",         # the product sheet
    "paper-2": "#F3EAD8",
    "paper-3": "#EADFC7",
    "paper-4": "#E0D4B8",
    "paper-5": "#DDD2B8",
    "book-paper": "#FBF7EF",    # the book's own sheet, quoted on badges
    "card": "#FFFDF8",
    "line-2": "#D2C4A6",
    # inks
    "ink": "#26221B",
    "ink-2": "#5C5448",
    "ink-3": "#675F4F",
    "hint": "#6E6353",
    "bronze": "#43392B",        # 浓墨
    "bronze-2": "#8A7D68",      # 次墨
    "bronze-3": "#5A5040",      # 淡墨
    # accents
    "cinnabar": "#B4472F",      # 朱砂
    "cinnabar-deep": "#9C3A26",
    "cinnabar-warm": "#8A4A34",
    "jade-deep": "#3E5A4C",
    "sky": "#4C7093",
    "sky-deep": "#3A5A78",
    # dark mode
    "dark-paper": "#1E1D18",
    "dark-card": "#26241D",
    "dark-ink": "#E9E4D8",
    "dark-ink-2": "#BDB4A2",
    "dark-ink-3": "#A59C8A",
    "dark-bronze": "#9C9484",
    "dark-plain": "#B3AA99",
    "dark-cinnabar": "#E07B5F",
}

# name in this module -> custom property in style_tokens.TOKENS_CSS
BOOK_MIRROR: dict[str, str] = {
    "paper-2": "--paper-2",
    "paper-3": "--paper-3",
    "book-paper": "--paper",
    "card": "--card",
    "line-2": "--line-2",
    "ink": "--ink",
    "ink-2": "--ink-2",
    "ink-3": "--ink-3",
    "bronze": "--bronze",
    "bronze-2": "--bronze-2",
    "bronze-3": "--bronze-3",
    "cinnabar": "--cinnabar",
    "sky": "--sky",
}

PALETTE_VALUES = frozenset(PALETTE.values())


# --------------------------------------------------------------------------
# type and corners
# --------------------------------------------------------------------------
SERIF_ZH = ('"Noto Serif SC","Source Han Serif SC","思源宋体","Songti SC",'
            '"SimSun",Georgia,serif')
SERIF_EN = '"Iowan Old Style",Palatino,Georgia,"Noto Serif SC",serif'
SANS = 'system-ui,"Microsoft YaHei",sans-serif'
MONO = "ui-monospace,Menlo,Consolas,monospace"

RADIUS_CARD = "10px 6px 12px 6px/6px 12px 6px 10px"
RADIUS_STATION = "12px 7px 11px 8px/8px 11px 7px 12px"
RADIUS_CHIP = "6px 4px 7px 3px/3px 7px 4px 5px"
RADIUS_RESUME = "6px 3px 7px 4px/4px 7px 3px 6px"


# --------------------------------------------------------------------------
# components
# --------------------------------------------------------------------------
# The seal favicon: one cinnabar ring, one solid dot. Kept as the finished
# <link> so no page can drift on the URL encoding.
FAVICON = ('<link rel="icon" href="data:image/svg+xml,%3Csvg '
           "xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E"
           "%3Ccircle cx='16' cy='16' r='12' fill='none' stroke='%23B4472F' "
           "stroke-width='3'/%3E%3Ccircle cx='16' cy='16' r='4' "
           "fill='%23B4472F'/%3E%3C/svg%3E\">")

# The brush rule under a page title: two dry-brush strokes and a drop of ink.
BRUSH = ('<svg class="brush" viewBox="0 0 190 10" aria-hidden="true">'
         '<path d="M4 6q30-4.5 62-2.5t72-1q24 .2 46 1.8" fill="none" '
         'stroke="currentColor" stroke-width="2.4" stroke-linecap="round" '
         'opacity=".85"/><path d="M152 5.6q10-.6 20-.2" fill="none" '
         'stroke="currentColor" stroke-width="1.3" stroke-linecap="round" '
         'opacity=".45"/><circle cx="178" cy="5.8" r="1.5" '
         'fill="currentColor" stroke="none"/></svg>')


# --------------------------------------------------------------------------
# the gate
# --------------------------------------------------------------------------
import re  # noqa: E402 - kept below the data so the module reads as a table

_HEX = re.compile(r"#[0-9A-Fa-f]{6}\b")
_RGBA = re.compile(r"rgba?\(\s*(\d{1,3})\s*,\s*(\d{1,3})\s*,\s*(\d{1,3})")


def hexes(text: str) -> set[str]:
    """Every #RRGGBB in a page, normalised to upper case."""
    return {m.group(0).upper() for m in _HEX.finditer(text)}


def _rgb_hex(match: re.Match) -> str:
    return "#" + "".join(f"{int(match.group(i)):02X}" for i in (1, 2, 3))


def unregistered(text: str, extra: set[str] | None = None) -> set[str]:
    """Colours a page paints that are not in the shared palette.

    ``extra`` admits a page-local value only when the caller spells it out;
    the three shipped pages pass nothing, so their palette is exactly this
    module's. ``rgba()`` is checked by its triplet, which is why the book can
    keep translucent inks without opening a second colour.
    """
    allowed = PALETTE_VALUES | {value.upper() for value in (extra or set())}
    found = hexes(text) | {_rgb_hex(m) for m in _RGBA.finditer(text)}
    return {value for value in found if value not in allowed}
