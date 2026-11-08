"""Chapter emblems — one small line drawing per unit, kept in the book's hand.

The rules below are what make a hand-drawn SVG safe to inline 20 times into a
single offline file: no ids (the audit fails on a duplicate), no scripts or
styles, no external references, and `currentColor` everywhere so one drawing
re-inks itself in dark mode and on paper without a second asset.
"""
from __future__ import annotations

import base64
import re
from pathlib import Path

from .core import BuildError

ART_DIR = Path(__file__).resolve().parent.parent / "illustrations"
# the companion volume's own tray: its ids all carry an `omp-` prefix, so the
# two directories can be searched in one pass without a product flag and a
# drawing can never cross-ink the wrong book
OMP_ART_DIR = Path(__file__).resolve().parent.parent / "illustrations-omp"
PI_ART_DIR = Path(__file__).resolve().parent.parent / "illustrations-pi"
MAX_BYTES = 6000
PLATE_BYTES = 20000
# one photograph the single-file edition can afford to carry: the offline
# guarantee means the bytes travel inside the HTML, not beside it
PHOTO_BYTES = 300_000
PHOTO_TYPES = {".png": "image/png", ".jpg": "image/jpeg",
               ".jpeg": "image/jpeg", ".webp": "image/webp"}

# the one rule that decides whether a drawing is a filmstrip: `seq` among the
# classes of its root element. render.py asks it, and the filmstrip frame-order
# test asks the same object instead of keeping a looser copy of its own
SEQ_ROOT = re.compile(r'<svg\b[^>]*class="[^"]*\bseq\b')

_BANNED = (
    (re.compile(r"<\s*script", re.I), "<script>"),
    (re.compile(r"<\s*style", re.I), "<style>"),
    (re.compile(r"<\s*iframe", re.I), "<iframe>"),
    (re.compile(r"\bid\s*=", re.I), "an id= attribute (20 inlined drawings would "
                                    "collide; the audit fails on a duplicate id)"),
    (re.compile(r"href\s*=", re.I), "an href= (external or #fragment reference)"),
    (re.compile(r"url\s*\(", re.I), "a url() (nothing may reach outside the file)"),
)


def _search_dirs() -> list[Path]:
    """Where a drawing may live, in the order `_read` looks.

    Read at call time: the tests point `ART_DIR` at a temporary folder.
    """
    return [d for d in (OMP_ART_DIR, PI_ART_DIR, ART_DIR) if d.is_dir()]


def _read(name: str, budget: int = MAX_BYTES) -> str | None:
    path = next((d / f"{name}.svg" for d in _search_dirs()
                 if (d / f"{name}.svg").exists()), None)
    if path is None:
        return None
    text = path.read_text(encoding="utf-8").strip()
    if len(text.encode("utf-8")) > budget:
        raise BuildError(f"{path.name}: {len(text)} bytes, over the "
                         f"{budget} budget for an inlined drawing")
    if not text.startswith("<svg") or "viewBox" not in text.split(">", 1)[0]:
        raise BuildError(f"{path.name}: an emblem must be one <svg> with a viewBox")
    for rx, why in _BANNED:
        if rx.search(text):
            raise BuildError(f"{path.name}: contains {why}")
    if "currentColor" not in text:
        raise BuildError(f"{path.name}: nothing is drawn in currentColor, so the "
                         "emblem cannot re-ink itself in dark mode or on paper")
    return text


def emblem(unit_id: str) -> str:
    """The unit's emblem as inline markup, or '' when the unit has none."""
    text = _read(unit_id)
    if not text:
        return ""
    return f'<span class="ch-emblem" aria-hidden="true">{text}</span>'


def keeper() -> str:
    """The old postman at the foot of each chapter, inlined 20 times: small
    by contract, because a mascot the file cannot afford is not a mascot."""
    text = _read("keeper")
    if not text:
        return ""
    return f'<span class="kp-art" aria-hidden="true">{text}</span>'


def headpiece(part_id: str) -> str:
    """The drawing a part divider opens with, or '' when there is none."""
    text = _read(f"part-{part_id}")
    if not text:
        return ""
    return f'<div class="pd-art" aria-hidden="true">{text}</div>'


def cover_plate() -> str:
    """The cover's four-horse chariot, drafted in the same hand as the
    emblems: an inline plate costs the file 11 KB and needs no crop, no
    filter and no bitmap."""
    text = _read("cover", PLATE_BYTES)
    if not text:
        return ""
    return f'<div class="cover-art" aria-hidden="true">{text}</div>'


def drawing(name: str) -> str:
    """A body-scale drawing an `ill` slot asked for.

    Same rules as an emblem, one size larger: the plate sits inside the prose
    column and re-inks itself, so it may run to `PLATE_BYTES` but no further.
    """
    text = _read(name, PLATE_BYTES)
    if not text:
        raise BuildError(f"illustrations/{name}.svg: an ill slot asks for a "
                         "drawing that is not there")
    return text


def photo(name: str) -> str:
    """A photograph as a data URI, for the few plates that need real light.

    Refusing to link out is the whole point: the reader gets one file, so the
    image has to live inside it, and a budget per picture keeps that file
    openable on a laptop with the book on a plane.
    """
    return photo_path(ART_DIR / name, label=f"illustrations/{name}")


def photo_path(path: Path, *, label: str | None = None) -> str:
    """Embed any on-disk bitmap under the same offline budget as `photo`."""
    label = label or path.name
    if not path.exists():
        raise BuildError(f"{label}: no such photograph")
    mime = PHOTO_TYPES.get(path.suffix.lower())
    if mime is None:
        raise BuildError(f"{label}: {path.suffix} is not a bitmap "
                         "type the book ships")
    raw = path.read_bytes()
    if len(raw) > PHOTO_BYTES:
        raise BuildError(f"{label}: {len(raw)} bytes, over the "
                         f"{PHOTO_BYTES} budget for one photograph")
    return f"data:{mime};base64,{base64.b64encode(raw).decode('ascii')}"


def missing(names: list[str]) -> list[str]:
    dirs = _search_dirs()
    return [n for n in names
            if not any((d / f"{n}.svg").exists() for d in dirs)]
