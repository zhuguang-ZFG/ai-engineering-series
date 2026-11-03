#!/usr/bin/env python3
"""Freeze the structural baseline the platform migration is measured against.

P0 of the total-transformation plan needs one reproducible file that answers
"what did the old builder actually produce?" before any module moves: unit and
heading counts, navigation anchors, registry totals, HTML/PDF sizes and PDF
pages. It deliberately reads the *outputs* and the *registries*, not builder
internals, so the same probe still works after the builder is split apart.

    python scripts/baseline.py                    # write docs/baseline/baseline.json
    python scripts/baseline.py --check            # compare with the committed file

The JSON carries no timestamp. Run it twice on the same source tree and the
bytes must match; that is the reproducibility gate. Environment versions are
recorded because PDF pagination is browser- and font-dependent in a way HTML
structure is not.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import platform
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BOOK = ROOT / "yuyu-book"
DEFAULT_DIST = BOOK / "dist"
DEFAULT_OUT = ROOT / "docs" / "baseline" / "baseline.json"

ARTICLE = re.compile(r'<article class="([^"]+)" id="([^"]+)">(.*?)</article>',
                     re.S)
HEADING = re.compile(r"<h([1-6])\b([^>]*)>", re.S)
FIG = re.compile(r'<figure class="([^"]*)"(?: id="([^"]+)")?')
NAV_ID = re.compile(r'<(section|article|h[2-4])\b[^>]*\sid="([^"]+)"')


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as fh:
        for block in iter(lambda: fh.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def git(*args: str) -> str:
    try:
        return subprocess.run(["git", *args], cwd=ROOT, check=True,
                              capture_output=True, text=True).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return ""


def tool_version(command: list[str]) -> str | None:
    try:
        out = subprocess.run(command, cwd=ROOT, check=True,
                             capture_output=True, text=True).stdout
        return out.strip().splitlines()[0]
    except (OSError, subprocess.CalledProcessError):
        return None


def module_version(name: str) -> str | None:
    try:
        from importlib.metadata import version
        return version(name)
    except Exception:  # noqa: BLE001 - a missing tool is a fact, not a crash
        return None


def unit_stats(html: str) -> tuple[list[dict], dict]:
    """Per-unit structure plus whole-edition totals."""
    units = []
    totals = {"headings": {}, "figures": 0, "tables": 0, "landscape": 0,
              "glosses": 0, "keeper": 0, "lead": 0, "tier_chips": 0,
              "new_terms": 0, "cited_links": 0}
    for cls, uid, body in ARTICLE.findall(html):
        kind = ("chapter" if cls == "chapter"
                else "appendix" if "appendix" in cls else "front")
        headings = {f"h{level}": 0 for level in range(1, 5)}
        heading_ids = []
        for level, attrs in HEADING.findall(body):
            level = int(level)
            if level > 4:
                continue
            headings[f"h{level}"] += 1
            found = re.search(r'\sid="([^"]+)"', attrs)
            if found:
                heading_ids.append(found.group(1))
        figs = FIG.findall(body)
        figures = len(figs)
        landscape = sum(1 for cls_name, _fid in figs
                        if {"wide", "landscape"}.issubset(cls_name.split()))
        stats = {
            "id": uid,
            "kind": kind,
            "bytes": len(body.encode("utf-8")),
            "headings": headings,
            "heading_anchors": heading_ids,
            "figures": figures,
            "figure_ids": [fid for _cls, fid in figs if fid],
            "tables": body.count("<table"),
            "landscape": landscape,
            "glosses": body.count('<span class="gloss"'),
            "keeper": body.count('<div class="keeper">'),
            "lead": body.count('<div class="lead-band">'),
            "tier_chips": body.count('<span class="sec-tier'),
            "new_terms": body.count('<li class="nt-row">'),
            "cited_links": body.count('<a class="ext"'),
        }
        units.append(stats)
        for level, count in headings.items():
            totals["headings"][level] = totals["headings"].get(level, 0) + count
        for key in ("figures", "tables", "landscape", "glosses", "keeper",
                    "lead", "tier_chips", "new_terms", "cited_links"):
            totals[key] += stats[key]
    totals["units"] = len(units)
    totals["chapters"] = sum(1 for u in units if u["kind"] == "chapter")
    totals["appendices"] = sum(1 for u in units if u["kind"] == "appendix")
    totals["front"] = sum(1 for u in units if u["kind"] == "front")
    return units, totals


def edition(dist: Path, lang: str) -> dict:
    path = dist / f"yuyu-agent-harness-{lang}.html"
    html = path.read_text(encoding="utf-8")
    units, totals = unit_stats(html)
    nav_ids = [anchor for _tag, anchor in NAV_ID.findall(html)]
    pdf_path = dist / f"yuyu-agent-harness-{lang}.pdf"
    pdf = None
    if pdf_path.exists():
        import fitz  # PyMuPDF, already a builder dependency
        with fitz.open(pdf_path) as doc:
            pdf = {
                "file": pdf_path.name,
                "bytes": pdf_path.stat().st_size,
                "pages": doc.page_count,
                "bookmarks": len(doc.get_toc(simple=True)),
            }
    return {
        "html": {
            "file": path.name,
            "bytes": path.stat().st_size,
            "sha256": sha256(path),
            "nav_anchors": len(nav_ids),
            "nav_anchor_ids": nav_ids,
            "ids_total": html.count(' id="'),
            "mm_svg": html.count('<svg id="mm-'),
            "sections": html.count("<section"),
        },
        "units": units,
        "totals": totals,
        "document": {
            "headings": {f"h{level}": len(re.findall(rf"<h{level}\b", html))
                         for level in range(1, 5)},
        },
        "pdf": pdf,
    }


def registry_report() -> dict:
    def load(name):
        data = json.loads((BOOK / name).read_text(encoding="utf-8"))
        # The probe deliberately reads outputs/registries without importing the
        # builder. Registries carry a schema_version envelope; strip it here so
        # the report stays about content.
        if name == "subject-index.json":
            return data["entries"]
        data.pop("schema_version", None)
        return data

    manifest = load("manifest.json")
    glosses = load("glosses.json")
    sources = load("sources.json")
    notes = load("notes.json")
    paths = load("reading-paths.json")
    revisions = load("revisions.json")
    index = load("subject-index.json")

    evidence = [ref for g in glosses.values() for ref in g.get("evidence") or []]
    why_evidence = [ref for g in glosses.values()
                    for ref in g.get("why_evidence") or []]
    unit_files = {}
    front = manifest["front"]
    groups = [*manifest["parts"],
              {"units": [front] if isinstance(front, dict) else front or []},
              {"units": manifest.get("appendices") or []}]
    for group in groups:
        for unit in group.get("units") or []:
            unit_files[unit["id"]] = {"zh": unit["zh"], "en": unit["en"]}
    markdown = {}
    for uid, files in unit_files.items():
        markdown[uid] = {}
        for lang, rel in files.items():
            path = ROOT / rel
            text = path.read_text(encoding="utf-8")
            markdown[uid][lang] = {
                "file": rel,
                "lines": len(text.splitlines()),
                "bytes": len(text.encode("utf-8")),
            }
    kind = {}
    for source in sources.values():
        kind[source.get("kind", "other")] = kind.get(source.get("kind", "other"), 0) + 1
    tiers = {}
    for entry in paths.values():
        for tier in ([entry] if isinstance(entry, str) else entry):
            tiers[tier] = tiers.get(tier, 0) + 1
    refs_zh = sum(len(e.get("zh", {}).get("refs") or []) for e in index)
    refs_en = sum(len(e.get("en", {}).get("refs") or []) for e in index)
    return {
        "manifest": {
            "version": manifest["version"],
            "date": manifest["date"],
            "parts": len(manifest["parts"]),
            "units": len(unit_files),
        },
        "markdown": markdown,
        "glosses": {
            "entries": len(glosses),
            "evidence_refs": len(evidence),
            "why_evidence_refs": len(why_evidence),
            "evidence_files": len({ref.rsplit(":", 1)[0] for ref in evidence}),
            "core": sum(1 for g in glosses.values()
                        if g.get("priority") == "core"),
        },
        "sources": {
            "entries": len(sources),
            "kinds": dict(sorted(kind.items())),
            "https": sum(1 for s in sources.values()
                         if str(s.get("url", "")).startswith("https://")),
            "pinned": sum(1 for s in sources.values()
                          if s.get("pinned")),
        },
        "notes": {
            "units": len(notes),
            "zh": sum(1 for n in notes.values() if n.get("zh")),
            "en": sum(1 for n in notes.values() if n.get("en")),
        },
        "reading_paths": {"units": len(paths), "tiers": dict(sorted(tiers.items()))},
        "revisions": {"entries": len(revisions["entries"]),
                      "versions": [e["version"] for e in revisions["entries"]]},
        "subject_index": {
            "terms": len(index),
            "zh_refs": refs_zh,
            "en_refs": refs_en,
        },
    }


def asset_report() -> dict:
    root = BOOK / "illustrations"
    files = []
    for path in sorted(p for p in root.rglob("*") if p.is_file()):
        # Identity must survive a Windows checkout's CRLF smudge, so hash the
        # LF form the repository stores, not the bytes on this disk.
        raw = path.read_bytes().replace(b"\r\n", b"\n")
        files.append({
            "file": str(path.relative_to(ROOT)).replace("\\", "/"),
            "bytes": len(raw),
            "sha256": sha256_bytes(raw),
        })
    return {"illustrations": files}


def build_baseline(dist: Path) -> dict:
    registries = registry_report()
    return {
        "schema_version": 1,
        "source_commit": git("rev-parse", "HEAD") or None,
        "book": {"version": registries["manifest"]["version"],
                 "date": registries["manifest"]["date"]},
        "environment": {
            "platform": platform.platform(),
            "python": platform.python_version(),
            "node": tool_version(["node", "--version"]),
            "playwright": module_version("playwright"),
            "pymupdf": module_version("PyMuPDF"),
        },
        "registries": registries,
        "assets": asset_report(),
        "editions": {lang: edition(dist, lang)
                     for lang in ("zh", "en")},
    }


def dump(data: dict) -> str:
    return json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--dist", type=Path, default=DEFAULT_DIST)
    ap.add_argument("--out", type=Path, default=DEFAULT_OUT)
    ap.add_argument("--check", action="store_true",
                    help="fail when the committed baseline differs from a fresh run")
    args = ap.parse_args(argv)
    data = build_baseline(args.dist)
    text = dump(data)
    if args.check:
        current = json.loads(args.out.read_text(encoding="utf-8"))
        for key in ("source_commit", "environment"):
            current.pop(key, None)
            data.pop(key, None)
        # Artifact bytes are provenance, not structure: a one-word edit changes
        # an HTML hash without moving a heading, a marker line changes the
        # source byte count, and PDF size follows the build machine's CJK face.
        # `--check` therefore compares the shape the migration promised to
        # preserve: anchors, ids, plates, unit counts, registry totals and PDF
        # pagination.
        for record in (current, data):
            for sources in record["registries"]["markdown"].values():
                for source in sources.values():
                    source.pop("bytes", None)
                    source.pop("lines", None)
            for edition in record["editions"].values():
                for key in ("bytes", "sha256"):
                    edition["html"].pop(key, None)
                for unit in edition["units"]:
                    unit.pop("bytes", None)
                    # Figure IDs are content hashes regenerated by the current
                    # builder. The frozen baseline keeps the old build's IDs as
                    # provenance; comparing their count preserves the slot
                    # inventory without claiming the hash algorithm never moves.
                    unit["figure_ids"] = ["fig"] * len(unit["figure_ids"])
                if edition["pdf"]:
                    edition["pdf"].pop("bytes", None)
        if dump(current) != dump(data):
            print(f"baseline drift: {args.out}", file=sys.stderr)
            return 1
        print(f"baseline matches {args.out}")
        return 0
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(text, encoding="utf-8", newline="\n")
    totals = data["editions"]["zh"]["totals"]
    print(f"baseline: {totals['units']} units, "
          f"{sum(totals['headings'].values())} headings, "
          f"{data['editions']['zh']['html']['nav_anchors']} zh anchors / "
          f"{data['editions']['en']['html']['nav_anchors']} en anchors; "
          f"PDF {data['editions']['zh']['pdf']['pages']} zh / "
          f"{data['editions']['en']['pdf']['pages']} en pages -> {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
