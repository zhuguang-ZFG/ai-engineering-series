"""Chapter copy shared by the knowledge cards and the sample chapter.

The hook and the three-sentence recap are authored as blockquotes whose bold
lead-in names them. Both editions use the same pattern, so one parser feeds
both products; a missing label is a build failure, not an empty card.
"""
from __future__ import annotations

import re
from pathlib import Path

from ..paths import BOOK_DIR

HOOK = {"zh": "开门一句话", "en": "In one line"}
RECAP = {"zh": "三句话带走", "en": "Three sentences to keep"}

_CIRCLED = re.compile(r"[①②③④⑤]")


def _quote_block(unit, marker: str) -> str:
    for section in unit.sections:
        for block in section.blocks:
            if block.kind == "quote" and marker in block.text:
                return block.text
    return ""


def _after_label(text: str, label: str) -> str:
    flat = " ".join(line.lstrip("> ").strip() for line in text.splitlines())
    flat = flat.replace("**", "")
    index = flat.find(label)
    if index < 0:
        return ""
    rest = re.sub(r"^\s*[：:]\s*", "", flat[index + len(label):])
    return rest.strip()


def hook(unit, lang: str) -> str:
    """The one-line door opener that starts the chapter."""
    label = HOOK[lang]
    text = _after_label(_quote_block(unit, label), label)
    if not text:
        raise ValueError(f"{unit.id}: no '{label}' quote in {lang}")
    return text


def recap(unit, lang: str) -> list[str]:
    """The three sentences the chapter asks the reader to carry away."""
    label = RECAP[lang]
    text = _after_label(_quote_block(unit, label), label)
    items = [part.strip() for part in _CIRCLED.split(text) if part.strip()]
    if len(items) != 3:
        raise ValueError(f"{unit.id}: expected 3 '{label}' items in {lang}, "
                         f"found {len(items)}")
    return items


def content_plate(unit_id: str) -> Path | None:
    """The chapter's own content plate, when the drawing shelf has one."""
    plates = sorted(BOOK_DIR.joinpath("illustrations").glob(f"{unit_id}-*.svg"))
    return plates[0] if plates else None
