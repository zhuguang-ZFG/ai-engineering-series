"""One content pack per chapter, cut from the book rather than retyped.

Long, short and knowledge-card scripts all point at the same pack. The pack
holds the chapter title, its domain sections (a heading plus the first
paragraph), the key-takeaway sentences and the core glossary terms that
actually appear in the chapter.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

from .model import BOOK, ROOT, VideoError, write_json

MANIFEST = BOOK / "manifest.json"
GLOSSES = BOOK / "glosses.json"
SKIP_SECTIONS = {"学习目标", "关键要点", "实战练习", "本章小结", "小结"}
TAKEAWAY_HEADINGS = {"关键要点", "Key Takeaways"}


def unit_paths() -> dict:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    found = {}
    for part in manifest["parts"]:
        for unit in part["units"]:
            found[unit["id"]] = unit
    return found


def plain(text: str) -> str:
    text = re.sub(r"<!--.*?-->", "", text)
    text = re.sub(r"!\[[^\]]*\]\([^)]*\)", "", text)
    text = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", text)
    text = re.sub(r"`([^`]*)`", r"\1", text)
    text = re.sub(r"\*\*(.+?)\*\*", r"\1", text)
    text = re.sub(r"__(.+?)__", r"\1", text)
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


def _sections(text: str) -> list[dict]:
    lines = text.splitlines()
    sections: list[dict] = []
    in_fence = False
    current = None
    paragraph: list[str] = []

    def flush() -> None:
        nonlocal current, paragraph
        if current is None:
            paragraph = []
            return
        body = plain(" ".join(paragraph))
        if body:
            current["summary"] = _trim(body, 180)
            sections.append(current)
        current = None
        paragraph = []

    for line in lines:
        if line.strip().startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        heading = re.match(r"^##\s+(.+?)\s*$", line)
        if heading:
            flush()
            title = plain(heading.group(1))
            if title and title not in SKIP_SECTIONS:
                current = {"index": len(sections) + 1, "title": title}
            continue
        if line.startswith("###"):
            continue
        if line.startswith("#"):
            flush()
            continue
        if current is None:
            continue
        stripped = line.strip()
        if not stripped:
            if paragraph:
                flush()
            continue
        if stripped.startswith((">", "|", "<!--")):
            continue
        paragraph.append(stripped)
    flush()
    return [s for s in sections if s.get("summary")]


def _takeaways(text: str) -> list[str]:
    lines = text.splitlines()
    found: list[str] = []
    active = False
    in_fence = False
    for line in lines:
        if line.strip().startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        heading = re.match(r"^##\s+(.+?)\s*$", line)
        if heading:
            title = plain(heading.group(1))
            active = title in TAKEAWAY_HEADINGS or title.startswith("关键要点")
            continue
        if not active:
            continue
        item = re.match(r"^\d+\.\s+(.+)$", line)
        if item:
            body = plain(item.group(1))
            if body:
                found.append(_trim(body, 240))
    return found


def _core_terms(text: str, limit: int = 8) -> list[dict]:
    if not GLOSSES.exists():
        return []
    entries = json.loads(GLOSSES.read_text(encoding="utf-8"))
    terms = []
    for key, entry in entries.items():
        if key == "schema_version" or entry.get("priority") != "core":
            continue
        forms = entry.get("forms", {}).get("zh", [])
        if any(form and form in text for form in forms):
            terms.append({
                "zh": entry.get("term", {}).get("zh", ""),
                "en": entry.get("term", {}).get("en", ""),
            })
        if len(terms) == limit:
            break
    return terms


def build_pack(chapter_id: str) -> dict:
    units = unit_paths()
    if chapter_id not in units:
        raise VideoError(f"{chapter_id}: not registered in manifest.json")
    path = ROOT / units[chapter_id]["zh"]
    text = path.read_text(encoding="utf-8")
    title_line = next((line for line in text.splitlines() if line.startswith("# ")), "")
    title = plain(title_line.lstrip("#").strip()) or chapter_id
    return {
        "schema_version": 1,
        "id": chapter_id,
        "title": title,
        "source": str(path.relative_to(ROOT)).replace("\\", "/"),
        "sections": _sections(text),
        "takeaways": _takeaways(text),
        "core_terms": _core_terms(text),
    }


def write_pack(chapter_id: str, chapter_dir: Path) -> dict:
    pack = build_pack(chapter_id)
    write_json(chapter_dir / "content-pack.json", pack)
    return pack
