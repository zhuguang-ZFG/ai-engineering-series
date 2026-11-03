"""Read-only migration plan for line-number evidence.

The registries still name evidence as `file:line`. This module resolves every
pointer against the manuscript's actual block spans and proposes a stable ID
for each referenced block, without writing anything. P2.5 adds the dual reader
and P2.6 runs the approved plan; until then this is a report, not an edit.

Classification is deliberately conservative:

* `mapped`   - the line sits inside exactly one prose span;
* `ambiguous`- the proposed ID collides with another block (usually identical
               paragraphs), so a human has to choose a semantic slug;
* `missing`  - the file, line, or block does not exist.

No timestamp is recorded: the same manuscript must produce the same report.
"""
from __future__ import annotations

import hashlib
import re

from . import blocks
from .core import REPO_ROOT, read_text, unit_stream

REF_RE = re.compile(r"^(.+):(\d+)$")


def collect_refs(manifest: dict, glosses: dict) -> list[tuple[str, str]]:
    """Every `file:line` value with a dotted path to the field holding it."""
    found: list[tuple[str, str]] = []

    def walk(node, path: str) -> None:
        if isinstance(node, dict):
            for key, value in node.items():
                walk(value, f"{path}.{key}")
        elif isinstance(node, list):
            for index, value in enumerate(node):
                walk(value, f"{path}[{index}]")
        elif isinstance(node, str) and REF_RE.match(node) \
                and "://" not in node:
            found.append((path, node))

    walk(manifest, "manifest")
    walk(glosses, "glosses")
    return found


def proposal_id(unit_id: str, body: str) -> str:
    """A content-derived ID: survives insertion, changes if the block is edited."""
    flat = re.sub(r"\s+", " ", body).strip().encode("utf-8")
    return f"{unit_id}.b-{hashlib.sha1(flat).hexdigest()[:8]}"


def build_report(manifest: dict, glosses: dict,
                 files: dict[str, str] | None = None) -> dict:
    """Resolve refs to spans and return the deterministic migration report."""
    unit_of: dict[str, tuple[str, str]] = {}
    for unit, kind, _part in unit_stream(manifest):
        for lang in ("zh", "en"):
            unit_of[unit[lang].replace("\\", "/")] = (unit["id"], lang)

    source = files if files is not None else {}

    def text_for(rel: str) -> str | None:
        if rel in source:
            return source[rel]
        path = REPO_ROOT / rel
        return read_text(path) if path.exists() else None

    spans: dict[str, list] = {}
    lines_of: dict[str, list[str]] = {}
    refs = collect_refs(manifest, glosses)
    for _field, ref in refs:
        rel = ref.rsplit(":", 1)[0].replace("\\", "/")
        if rel not in spans and rel in unit_of:
            body = text_for(rel)
            lines_of[rel] = body.split("\n") if body is not None else []
            spans[rel] = (blocks.parse_blocks(body, unit_of[rel][0],
                                              unit_of[rel][1])
                          if body is not None else [])

    owners: dict[tuple[str, str, str], tuple[str, int]] = {}
    block_reports: dict[str, list] = {}
    for rel, (unit_id, _lang) in unit_of.items():
        for block in spans.get(rel, []):
            marked = bool(block.block_id)
            block.block_id = block.block_id or proposal_id(unit_id, block.text)
            key = (unit_id, block.lang, block.block_id)
            status, reason = "mapped", ""
            if key in owners:
                status = "ambiguous"
                reason = ("identical block text already claimed this id "
                          f"at line {owners[key][1]}; choose a semantic slug")
                if not marked:
                    suffix = 2
                    while (unit_id, block.lang,
                           f"{block.block_id}-{suffix}") in owners:
                        suffix += 1
                    block.block_id = f"{block.block_id}-{suffix}"
                key = (unit_id, block.lang, block.block_id)
            owners[key] = (rel, block.line)
            block_reports.setdefault(rel, []).append({
                "start": block.line,
                "end": block.end_line,
                "kind": block.kind,
                "block_id": block.block_id,
                "has_marker": marked,
                "status": status,
                "reason": reason,
            })

    details = []
    counts = {"mapped": 0, "ambiguous": 0, "missing": 0}
    for field, ref in refs:
        rel, lineno = ref.rsplit(":", 1)
        rel = rel.replace("\\", "/")
        lineno = int(lineno)
        unit_id, lang = unit_of.get(rel, ("", ""))
        row = {"field": field, "ref": ref, "file": rel, "line": lineno,
               "unit": unit_id, "lang": lang, "block_id": "",
               "status": "missing", "reason": ""}
        if not unit_id:
            row["reason"] = "file is not a manifest unit"
        else:
            hit = next((block for block in spans.get(rel, [])
                        if block.line <= lineno <= block.end_line), None)
            record = None
            if hit is not None:
                record = next(r for r in block_reports[rel]
                              if r["start"] == hit.line)
            if hit is None:
                row["reason"] = "line is blank, a marker, or past the end"
            elif record["status"] == "ambiguous":
                row["status"] = "ambiguous"
                row["block_id"] = hit.block_id
                row["reason"] = record["reason"]
            else:
                row["status"] = "mapped"
                row["block_id"] = hit.block_id
            if hit is not None:
                line_text = lines_of[rel][lineno - 1].strip()
                row["text_equal"] = line_text in [
                    part.strip() for part in hit.text.split("\n")]
        counts[row["status"]] += 1
        details.append(row)

    matched = sum(1 for row in details if row.get("text_equal"))
    mismatched = sum(1 for row in details
                     if row["status"] == "mapped"
                     and not row.get("text_equal"))
    return {
        "schema_version": 1,
        "summary": {
            "refs": len(refs),
            "unique_refs": len({ref for _field, ref in refs}),
            **counts,
            "text_equal": matched,
            "text_mismatch": mismatched,
            "blocks": sum(len(records) for records in block_reports.values()),
        },
        "files": {rel: {"unit": unit_of[rel][0], "lang": unit_of[rel][1],
                        "blocks": records}
                  for rel, records in sorted(block_reports.items())},
        "refs": details,
    }
