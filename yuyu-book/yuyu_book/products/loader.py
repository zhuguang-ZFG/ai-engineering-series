"""Assemble the BookModel every product reads.

The builder renders from `units.load_unit` and the registries directly. A
product page only needs the model, so this loader is the one place that turns
manifest + guides + notes + glosses + manuscripts into `BookModel`. Products
call `load_model()` and never parse a rendered HTML file — that reverse
extraction is exactly what P4 removes.

The loader is deliberately read-only: no HTML, no browser, no output. Passing
`langs=["zh"]` loads one edition; the parts and terms are language-neutral and
come along once.
"""
from __future__ import annotations

from .. import blocks as block_markers
from .. import units
from ..config import unit_stream
from ..io import load_json, read_text
from ..model import Block, BookModel, Edition, Guide, Part, Section, Term, Unit
from ..paths import BOOK_DIR, REPO_ROOT


def _sections(parsed: list[Block], fallback_title: str) -> list[Section]:
    """Group spans under the heading that opened them.

    A unit may open with prose before its first H2 (the foreword does), so an
    implicit level-1 section named after the unit collects that lead-in. The
    heading span itself stays in its section's block list: it is citable, and
    dropping it would make `Section.title` the only copy of that text.
    """
    sections: list[Section] = []
    lead: list[Block] = []
    current: Section | None = None
    for block in parsed:
        if block.kind == "heading":
            stripped = block.text.lstrip()
            level = len(stripped) - len(stripped.lstrip("#"))
            current = Section(level, stripped[level:].strip(), block.line,
                              [block])
            sections.append(current)
        elif current is None:
            lead.append(block)
        else:
            current.blocks.append(block)
    if lead:
        sections.insert(0, Section(1, fallback_title, lead[0].line, lead))
    return sections


def _plain_fields(raw: dict | None) -> Guide:
    raw = raw or {}

    def field(name: str) -> dict[str, str]:
        value = raw.get(name) or {}
        return {lang: str(text) for lang, text in value.items()
                if isinstance(text, str)}

    return Guide(question=field("question"), deliverable=field("deliverable"),
                 boundary=field("boundary"), plain=field("plain"),
                 analogy=field("analogy"),
                 sources=[str(sid) for sid in raw.get("sources") or []])


def _terms(glosses: dict | None) -> list[Term]:
    out: list[Term] = []
    for gid, raw in (glosses or {}).items():
        if not isinstance(raw, dict) or "term" not in raw:
            continue
        out.append(Term(
            id=gid,
            term=dict(raw.get("term") or {}),
            forms={lang: list(forms)
                   for lang, forms in (raw.get("forms") or {}).items()},
            plain={lang: str(text)
                   for lang, text in (raw.get("plain") or {}).items()},
            priority=str(raw.get("priority") or ""),
            evidence=list(raw.get("evidence") or []),
            analogy={lang: str(text)
                     for lang, text in (raw.get("analogy") or {}).items()},
            why={lang: str(text)
                 for lang, text in (raw.get("why") or {}).items()},
        ))
    return out


def load_model(manifest: dict, notes: dict | None = None,
               glosses: dict | None = None, langs: list[str] | None = None,
               repo_root=REPO_ROOT) -> BookModel:
    langs = list(langs or manifest.get("langs") or ("zh", "en"))
    notes = notes or {}
    guides = manifest.get("guides") or {}
    model = BookModel(version=str(manifest.get("version") or ""))
    model.terms = _terms(glosses)

    part_of: dict[str, str] = {}
    for raw in manifest.get("parts") or []:
        unit_ids = [u["id"] for u in raw.get("units") or []]
        for uid in unit_ids:
            part_of[uid] = raw["id"]
        model.parts.append(Part(
            raw["id"], unit_ids,
            no=dict(raw.get("no") or {}),
            title=dict(raw.get("title") or {}),
            motto=dict(raw.get("motto") or {}),
            goal=dict(raw.get("goal") or {})))

    for lang in langs:
        edition = Edition(lang)
        for unit_def, kind, _part in unit_stream(manifest):
            rel = unit_def[lang]
            raw = read_text(repo_root / rel)
            block_markers.validate_markers(raw, rel, unit_def["id"])
            no, title, _body = units.normalize_h1(raw, lang, rel)
            parsed = block_markers.parse_blocks(raw, unit_def["id"], lang)
            keep = (notes.get(unit_def["id"]) or {}).get(lang) or ""
            edition.units.append(Unit(
                id=unit_def["id"], kind=kind, lang=lang, path=rel,
                title=title, sections=_sections(parsed, title),
                no=no, anchor=unit_def["id"],
                part_id=part_of.get(unit_def["id"], ""),
                guide=_plain_fields(guides.get(unit_def["id"])),
                keeper=str(keep)))
        model.editions[lang] = edition
    return model


def load_repo_model(langs: list[str] | None = None) -> BookModel:
    """Load the book this repository ships, registries included."""
    return load_model(
        load_json(BOOK_DIR / "manifest.json"),
        load_json(BOOK_DIR / "notes.json"),
        load_json(BOOK_DIR / "glosses.json"),
        langs=langs)
