"""Chapter video content is an adapter over the shared read-only BookModel."""
from __future__ import annotations

import re
import sys
from functools import lru_cache

from .model import BOOK, VideoError, write_json

sys.path.insert(0, str(BOOK))
from yuyu_book.products.loader import load_repo_model

SKIP_SECTIONS = {"学习目标", "关键要点", "实战练习", "本章小结", "小结"}


def plain(text: str) -> str:
    text = re.sub(r"<!--.*?-->", "", text)
    text = re.sub(r"!\[[^\]]*\]\([^)]*\)", "", text)
    text = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", text)
    text = re.sub(r"`([^`]*)`", r"\1", text)
    text = re.sub(r"\*\*(.+?)\*\*|__(.+?)__", lambda m: m[1] or m[2], text)
    text = re.sub(r"<[^>]+>", "", text)
    text = re.sub(r"^\s*(?:[-*>+]|\d+\.)\s+", "", text)
    return re.sub(r"\s+", " ", text).strip()


def _trim(text: str, limit: int) -> str:
    if len(text) <= limit:
        return text
    cut = text[:limit]
    for index in range(len(cut) - 1, max(0, limit - 40), -1):
        if cut[index] in "。！？；.!?;":
            return cut[:index + 1]
    return cut.rstrip() + "…"


@lru_cache(maxsize=1)
def _model():
    return load_repo_model(["zh"])


def build_pack(chapter_id: str) -> dict:
    model = _model()
    unit = model.unit("zh", chapter_id)
    if unit is None or unit.kind != "chapter":
        raise VideoError(f"{chapter_id}: not a chapter in BookModel")
    sections, takeaways = [], []
    for section in unit.sections:
        if section.level != 2:
            continue
        title = plain(section.title)
        if title in {"关键要点", "Key Takeaways"} or title.startswith("关键要点"):
            for block in section.blocks:
                if block.kind == "list":
                    for line in block.text.splitlines():
                        if re.match(r"^\d+\.\s+", line):
                            takeaways.append(_trim(plain(line), 240))
        if title in SKIP_SECTIONS:
            continue
        first = next((plain(block.text) for block in section.blocks
                      if block.kind == "paragraph" and plain(block.text)), "")
        if first:
            sections.append({"index": len(sections) + 1, "title": title,
                             "summary": _trim(first, 180)})
    text = "\n".join(block.text for section in unit.sections for block in section.blocks)
    terms = []
    for term in model.terms:
        if term.priority == "core" and any(form and form in text
                                          for form in term.forms.get("zh", [])):
            terms.append({"zh": term.term.get("zh", ""),
                          "en": term.term.get("en", "")})
            if len(terms) == 8:
                break
    return {"schema_version": 1, "id": chapter_id, "title": unit.display,
            "source": unit.path.replace("\\", "/"), "sections": sections,
            "takeaways": takeaways, "core_terms": terms}


def write_pack(chapter_id: str, chapter_dir) -> dict:
    pack = build_pack(chapter_id)
    write_json(chapter_dir / "content-pack.json", pack)
    return pack
