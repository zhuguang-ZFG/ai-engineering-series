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


def marker_line(block_id: str) -> str:
    return f"<!-- block: {block_id} -->"


def insert_markers(text: str, inserts: list[tuple[int, str]]) -> str:
    """Put marker lines above 1-based block starts, preserving CRLF/LF."""
    newline = "\r\n" if "\r\n" in text else "\n"
    lines = text.split(newline)
    for start, block_id in sorted(inserts, reverse=True):
        lines.insert(start - 1, marker_line(block_id))
    return newline.join(lines)


def _replace_refs(node, mapping: dict[str, str]):
    if isinstance(node, dict):
        return {key: _replace_refs(value, mapping)
                for key, value in node.items()}
    if isinstance(node, list):
        return [_replace_refs(value, mapping) for value in node]
    if isinstance(node, str):
        return mapping.get(node, node)
    return node


def stage_migration(root, manifest: dict, glosses: dict,
                    report: dict) -> tuple[dict, dict]:
    """Copy the manuscript to `root` and write the fully migrated variant."""
    from pathlib import Path
    from .core import read_text

    root = Path(root)
    for unit, _kind, _part in unit_stream(manifest):
        for lang in ("zh", "en"):
            rel = unit[lang].replace("\\", "/")
            target = root / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(read_text(REPO_ROOT / rel), encoding="utf-8",
                              newline="")

    mapping: dict[str, str] = {}
    for row in report["refs"]:
        if row["status"] == "mapped":
            mapping[row["ref"]] = row["block_id"]
    for rel, info in report["files"].items():
        wanted = {row["block_id"] for row in report["refs"]
                  if row["file"] == rel and row["status"] == "mapped"}
        inserts = [(block["start"], block["block_id"])
                   for block in info["blocks"]
                   if block["block_id"] in wanted and not block["has_marker"]]
        if not inserts:
            continue
        target = root / rel
        target.write_text(
            insert_markers(target.read_text(encoding="utf-8"), inserts),
            encoding="utf-8", newline="")
    return (_replace_refs(manifest, mapping),
            _replace_refs(glosses, mapping))


def verify_dual(manifest: dict, glosses: dict, paths: dict | None = None,
                report: dict | None = None) -> dict:
    """Validate legacy refs and their staged block ids, then compare reach.

    Both runs go through `plain.validate_plain`; the only difference is the
    pointer vocabulary and, for blocks, a temporary manuscript carrying the
    markers. A block is consistent when the markers it resolves to reach
    every language its line refs reached; a shared marker may also reach the
    other edition, which is why the check is a projection, not set equality.
    """
    import tempfile
    from pathlib import Path
    from . import plain

    report = report or build_report(manifest, glosses)
    mapping = {row["ref"]: row["block_id"] for row in report["refs"]
               if row["status"] == "mapped"}
    with tempfile.TemporaryDirectory() as tmp:
        staged_manifest, staged_glosses = stage_migration(
            Path(tmp), manifest, glosses, report)
        line_reached: dict[str, set[str]] = {}
        plain.validate_plain(glosses, paths or {}, manifest,
                             reached=line_reached)
        block_reached: dict[str, set[str]] = {}
        plain.validate_plain(staged_glosses, paths or {}, staged_manifest,
                             root=Path(tmp), reached=block_reached)

    mismatches = []
    claims: dict[str, set[str]] = {}
    block_of: dict[str, str] = {}
    for ref, block_id in mapping.items():
        before = line_reached.get(ref, set())
        block_of[block_id] = ref
        claims.setdefault(block_id, set()).update(before)
    for block_id, claimed in sorted(claims.items()):
        after = block_reached.get(block_id, set())
        if not claimed or not claimed <= after:
            mismatches.append({"ref": block_of[block_id],
                               "block_id": block_id,
                               "line_reaches": sorted(claimed),
                               "block_reaches": sorted(after)})
    return {
        "schema_version": 1,
        "blocks": len(claims),
        "consistent": len(claims) - len(mismatches),
        "mismatches": mismatches,
    }


def rewrite_registry_text(text: str, mapping: dict[str, str]) -> str:
    """Swap quoted `file:line` values for block ids without reformatting JSON."""
    import json
    for ref, block_id in mapping.items():
        text = text.replace(json.dumps(ref, ensure_ascii=False),
                            json.dumps(block_id, ensure_ascii=False))
    return text


def apply_migration(manifest: dict, glosses: dict, report: dict,
                    root=None, registry_dir=None) -> dict:
    """Write the staged plan to the real manuscript and registries.

    Refuses an ambiguous or incomplete plan: inserting a marker for a line
    that maps to two blocks would silently pick one. Registry edits are string
    replacements, so the files keep their existing formatting and diff.
    """
    import json
    from pathlib import Path
    from .core import BOOK_DIR

    root = Path(root or REPO_ROOT)
    registry_dir = Path(registry_dir or BOOK_DIR)
    summary = report["summary"]
    if summary["ambiguous"] or summary["missing"]:
        raise ValueError("refusing to write an incomplete migration plan")

    mapping: dict[str, str] = {}
    for row in report["refs"]:
        if row["status"] == "mapped":
            mapping[row["ref"]] = row["block_id"]

    paths = {"manifest.json": registry_dir / "manifest.json",
             "glosses.json": registry_dir / "glosses.json"}
    pending = {}
    for name, path in paths.items():
        text = path.read_text(encoding="utf-8", newline="")
        pending[name] = rewrite_registry_text(text, mapping)
    for ref in mapping:
        quoted = json.dumps(ref, ensure_ascii=False)
        if any(quoted in text for text in pending.values()):
            raise ValueError(f"ref did not rewrite cleanly: {ref}")

    inserted = 0
    for rel, info in report["files"].items():
        wanted = {row["block_id"] for row in report["refs"]
                  if row["file"] == rel and row["status"] == "mapped"}
        inserts = [(block["start"], block["block_id"])
                   for block in info["blocks"]
                   if block["block_id"] in wanted and not block["has_marker"]]
        if not inserts:
            continue
        target = root / rel
        original = target.read_text(encoding="utf-8", newline="")
        target.write_text(insert_markers(original, inserts),
                          encoding="utf-8", newline="")
        inserted += len(inserts)

    for name, text in pending.items():
        paths[name].write_text(text, encoding="utf-8", newline="")
    return {"refs": len(mapping), "markers": inserted,
            "registries": sorted(pending)}
