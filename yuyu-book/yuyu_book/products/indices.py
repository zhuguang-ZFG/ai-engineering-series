"""docs/search-index.json, language-map.json, concept-map.json.

Three static tables the site can serve and a future client can search without
a server:

* `search-index.json` — every prose span of both editions, in reading order,
  with its unit, section anchor and stable block id (when the author gave one).
* `language-map.json` — the same section in the two editions. The two
  editions keep the same unit list, section counts and heading levels; this
  module fails the build if that stops being true, so a reader can always jump
  from a Chinese paragraph's heading to its English twin.
* `concept-map.json` — every registered term with the units its evidence
  names, and the terms that share the most units with it.

The tables are deterministic: models in, JSON out, nothing read from dist.
"""
from __future__ import annotations

import json
from pathlib import Path

from ..model import BookModel, Unit
from ..paths import REPO_ROOT
from ..render import book_slug
from .loader import load_repo_model

OUT = {
    "search": "search-index.json",
    "language": "language-map.json",
    "concept": "concept-map.json",
}
SCHEMA_VERSION = 1


class IndexDrift(RuntimeError):
    """The two editions no longer line up section for section."""


def _section_anchor(unit: Unit, title: str) -> str:
    return f"{unit.id}-{book_slug(title)}"


def _plain(block) -> str:
    if block.kind == "heading":
        return block.text.lstrip("#").strip()
    if block.kind == "fence":
        lines = block.text.splitlines()
        body = lines[1:-1] if len(lines) >= 2 else []
        return "\n".join(body)
    if block.kind == "quote":
        return " ".join(line.lstrip("> ").strip()
                        for line in block.text.splitlines())
    return block.text


def _anchors(unit: Unit) -> list[tuple[int, str, str]]:
    """(level, title, anchor) per section, unit title included."""
    out = []
    for section in unit.sections:
        anchor = (unit.anchor if section.level == 1
                  else _section_anchor(unit, section.title))
        out.append((section.level, section.title, anchor))
    return out


def search_index(model: BookModel) -> dict:
    entries = []
    for lang, edition in model.editions.items():
        for unit in edition.units:
            for section in unit.sections:
                current = (unit.anchor if section.level == 1
                           else _section_anchor(unit, section.title))
                for block in section.blocks:
                    text = _plain(block)
                    if not text.strip():
                        continue
                    entry = {
                        "lang": lang,
                        "unit": unit.id,
                        "section": current,
                        "kind": block.kind,
                        "text": text,
                    }
                    if block.block_id:
                        entry["block"] = block.block_id
                    entries.append(entry)
    return {
        "schema_version": SCHEMA_VERSION,
        "baseline": model.version,
        "entries": entries,
    }


def language_map(model: BookModel) -> dict:
    zh = model.editions.get("zh")
    en = model.editions.get("en")
    if zh is None or en is None:
        raise IndexDrift("the language map needs both editions loaded")
    if [u.id for u in zh.units] != [u.id for u in en.units]:
        raise IndexDrift("the editions no longer list the same units")
    units = []
    for zu, eu in zip(zh.units, en.units):
        za, ea = _anchors(zu), _anchors(eu)
        if len(za) != len(ea) or [x[0] for x in za] != [x[0] for x in ea]:
            raise IndexDrift(
                f"{zu.id}: section structure drifted between editions "
                f"({len(za)} zh vs {len(ea)} en)")
        sections = [{
            "level": z[0],
            "zh": {"title": z[1], "anchor": z[2]},
            "en": {"title": e[1], "anchor": e[2]},
        } for z, e in zip(za, ea)]
        units.append({
            "id": zu.id,
            "zh": {"no": zu.no, "title": zu.title, "anchor": zu.anchor},
            "en": {"no": eu.no, "title": eu.title, "anchor": eu.anchor},
            "sections": sections,
        })
    return {
        "schema_version": SCHEMA_VERSION,
        "baseline": model.version,
        "units": units,
    }


def concept_map(model: BookModel, glosses: dict) -> dict:
    known = {unit.id for edition in model.editions.values()
             for unit in edition.units}
    terms, units_of = [], {}
    for gid in sorted(glosses):
        raw = glosses[gid]
        if not isinstance(raw, dict) or "term" not in raw:
            continue
        units: list[str] = []
        for evidence in raw.get("evidence") or []:
            uid = str(evidence).split(".", 1)[0]
            if uid in known and uid not in units:
                units.append(uid)
        units_of[gid] = units
        terms.append({
            "id": gid,
            "term": dict(raw.get("term") or {}),
            "forms": {lang: list(forms) for lang, forms
                      in (raw.get("forms") or {}).items()},
            "priority": str(raw.get("priority") or ""),
            "plain": dict(raw.get("plain") or {}),
            "units": units,
        })
    related = {}
    for gid in units_of:
        shared = []
        for other, other_units in units_of.items():
            if other == gid:
                continue
            count = len(set(units_of[gid]) & set(other_units))
            if count:
                shared.append((-count, other))
        related[gid] = [{"id": other, "shared": -count}
                        for count, other in sorted(shared)[:5]]
    for term in terms:
        term["related"] = related.get(term["id"], [])
    return {
        "schema_version": SCHEMA_VERSION,
        "baseline": model.version,
        "terms": terms,
    }


def _write(name: str, data: dict) -> Path:
    out = REPO_ROOT / "docs" / name
    out.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n",
                   encoding="utf-8")
    return out


def build() -> list[Path]:
    from ..io import load_json
    from ..paths import BOOK_DIR
    model = load_repo_model(["zh", "en"])
    glosses = load_json(BOOK_DIR / "glosses.json")
    return [
        _write(OUT["search"], search_index(model)),
        _write(OUT["language"], language_map(model)),
        _write(OUT["concept"], concept_map(model, glosses)),
    ]


def main() -> None:
    for out in build():
        print(f"{out} ({out.stat().st_size} bytes)")
