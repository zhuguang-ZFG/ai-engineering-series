"""PrintManifest: the typed hand-off from the HTML build to the PDF pass.

The PDF pass used to receive a plain dict assembled in `app.pdf_meta()`. A
missing key then surfaced as a `KeyError` deep inside PyMuPDF work, after the
expensive Chromium print, and a mistyped anchor surfaced as "no destination"
with no hint which list it came from. This module gives that hand-off a shape:
three frozen records, each validated where it is built, so a bad outline is
rejected before the browser launches.

The contract is positional on purpose. Bookmarks and running heads are read
left to right from `outline`, the contents pages number `toc_rows` in the
order the page prints them, and the subject index stamps `index_rows` by
anchor. A list that is silently reordered moves numbers to somebody else's
section, so every anchor must be unique and every row must point at a
bookmarked section.
"""
from __future__ import annotations

from dataclasses import dataclass

from .diagnostics import BuildError

LANGS = ("zh", "en")


@dataclass(frozen=True)
class OutlineEntry:
    """One bookmark: level 1 for parts/appendices, 2 for chapters."""
    level: int
    label: str
    anchor: str

    def __post_init__(self) -> None:
        if self.level not in (1, 2):
            raise BuildError(f"print manifest: outline level must be 1 or 2, "
                             f"got {self.level} for {self.anchor or '?'}")
        if not self.label.strip():
            raise BuildError(f"print manifest: empty bookmark label at "
                             f"{self.anchor or '?'}")
        if not self.anchor.strip():
            raise BuildError("print manifest: empty bookmark anchor")


@dataclass(frozen=True)
class IndexRow:
    """One printed index row and the anchor whose folio it carries."""
    term: str
    anchor: str

    def __post_init__(self) -> None:
        if not self.term.strip():
            raise BuildError(f"print manifest: empty index term for "
                             f"{self.anchor or '?'}")
        if not self.anchor.strip():
            raise BuildError(f"print manifest: index term {self.term!r} has no "
                             "anchor")


@dataclass(frozen=True)
class PrintManifest:
    outline: tuple[OutlineEntry, ...]
    toc_title: str
    title: str
    subtitle: str
    author: str
    keywords: str
    lang: str
    front_anchor: str
    toc_rows: tuple[str, ...]
    index_rows: tuple[IndexRow, ...]

    def __post_init__(self) -> None:
        if self.lang not in LANGS:
            raise BuildError(f"print manifest: unknown language {self.lang!r}")
        if not self.outline:
            raise BuildError("print manifest: outline is empty")
        if not self.title.strip():
            raise BuildError("print manifest: title is empty")
        if not self.toc_title.strip():
            raise BuildError("print manifest: contents heading is empty")
        if not self.front_anchor.strip():
            raise BuildError("print manifest: front anchor is empty")

        seen: set[str] = set()
        for entry in self.outline:
            if entry.anchor in seen:
                raise BuildError(
                    f"print manifest: duplicate outline anchor "
                    f"{entry.anchor!r} — two bookmarks would share one running "
                    "head slot")
            seen.add(entry.anchor)

        if self.front_anchor not in seen:
            raise BuildError(
                f"print manifest: front anchor {self.front_anchor!r} is not in "
                "the outline, so no destination can be resolved for it")

        for anchor in self.toc_rows:
            if anchor not in seen:
                raise BuildError(
                    f"print manifest: contents row {anchor!r} is not a "
                    "bookmarked section — its folio could never be stamped")

        for row in self.index_rows:
            if row.anchor not in seen:
                raise BuildError(
                    f"print manifest: index row {row.term!r} points at "
                    f"{row.anchor!r}, which is not a bookmarked section")

    @property
    def heads(self) -> tuple[tuple[str, str], ...]:
        """(anchor, label) in bookmark order — the running-head source."""
        return tuple((entry.anchor, entry.label) for entry in self.outline)
