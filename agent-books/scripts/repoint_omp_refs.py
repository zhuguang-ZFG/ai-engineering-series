"""Relocate the book's file:line evidence pointers after prose edits.

Every anchor in ``yuyu-book/glosses-omp.json`` and ``yuyu-book/manifest-omp.json``
names a chapter line. Editing prose above that line moves it, and the assembly
check then fails on a pointer that no longer contains a registered form.

Recomputing the numbers by hand is error-prone, so this tool remaps them by
content: for each pointer it reads the line it used to name at ``--base``, looks
for that same line in the current file, and reports the new number.

Usage::

    python scripts/repoint_omp_refs.py --base HEAD        # report only
    python scripts/repoint_omp_refs.py --base HEAD --write # update the JSON

Statuses:

``ok``        the pointer still names the same line
``moved``     the line exists once at a new number (rewritten with --write)
``ambiguous`` the line now appears more than once; pick by hand
``missing``   the line was edited away; re-aim by hand

``--write`` only touches ``moved`` pointers, so an ambiguous or missing line can
never be silently repointed at the wrong place.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

from book_history import HistoryError, RevisionFiles

ROOT = Path(__file__).resolve().parents[1]
SOURCES = (
    ROOT / "yuyu-book" / "glosses-omp.json",
    ROOT / "yuyu-book" / "manifest-omp.json",
)
REF = re.compile(r"^(?P<path>[^:]+):(?P<line>\d+)$")


def base_text(ref: str, path: str, history: RevisionFiles | None = None) -> str:
    return (history or RevisionFiles(ROOT, ref)).read_text(path)


def collect_refs(ref: str, history: RevisionFiles | None = None) -> dict[tuple[str, int], list[Path]]:
    """Map every (chapter, line) pointer recorded at ``ref`` to its sources.

    The pointers are read from the JSON *at that revision* so the numbers and
    the chapter text they describe come from the same snapshot; mixing a
    working-tree JSON with a base chapter pairs the wrong lines.
    """
    history = history or RevisionFiles(ROOT, ref)
    refs: dict[tuple[str, int], list[Path]] = {}
    for source in SOURCES:
        rel = source.relative_to(ROOT).as_posix()
        text = base_text(ref, rel, history)
        for raw in re.findall(r'"((?:omp/)?[^"\n]+\.md:\d+)"', text):
            match = REF.match(raw)
            if not match:
                continue
            key = (match.group("path"), int(match.group("line")))
            refs.setdefault(key, []).append(source)
    return refs


def base_lines(ref: str, path: str, history: RevisionFiles | None = None) -> list[str]:
    return base_text(ref, path, history).splitlines()


def locate(lines: list[str], wanted: str, hint: int) -> tuple[str, int | None]:
    if 0 < hint <= len(lines) and lines[hint - 1].strip() == wanted:
        return "ok", hint
    hits = [index + 1 for index, line in enumerate(lines) if line.strip() == wanted]
    if len(hits) == 1:
        return "moved", hits[0]
    if len(hits) > 1:
        return "ambiguous", min(hits, key=lambda n: abs(n - hint))
    return "missing", None


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", default="HEAD", help="git revision holding the old line numbers")
    parser.add_argument("--write", action="store_true", help="rewrite moved pointers in place")
    args = parser.parse_args()

    history = RevisionFiles(ROOT, args.base)
    refs = collect_refs(args.base, history)
    if not refs:
        print("no file:line pointers found")
        return 1

    cache: dict[str, tuple[list[str], list[str]]] = {}
    report: dict[str, list[tuple[str, int, int | None]]] = {
        "ok": [], "moved": [], "ambiguous": [], "missing": [],
    }
    replacements: dict[tuple[Path, str, int], int] = {}

    for (path, line), sources in sorted(refs.items()):
        if path not in cache:
            old = base_lines(args.base, path, history)
            current = (ROOT / path).read_text(encoding="utf-8").splitlines()
            cache[path] = (old, current)
        old, current = cache[path]
        if line > len(old):
            report["missing"].append((path, line, None))
            continue
        status, new_line = locate(current, old[line - 1].strip(), line)
        report[status].append((path, line, new_line))
        if status == "moved" and new_line is not None:
            for source in sources:
                replacements[(source, path, line)] = new_line

    for status in ("ok", "moved", "ambiguous", "missing"):
        entries = report[status]
        print(f"{status:9} {len(entries):3}")
        for path, old_line, new_line in entries:
            arrow = f" -> :{new_line}" if new_line else ""
            if status != "ok":
                print(f"          {path}:{old_line}{arrow}")

    if args.write and replacements:
        for source in SOURCES:
            # The mapping was derived from the JSON *at* --base, so the output
            # must start from that same snapshot; starting from a JSON that was
            # already half-rewritten would mix two numbering systems.
            text = base_text(args.base, source.relative_to(ROOT).as_posix(), history)
            changed = 0
            for (target, path, old_line), new_line in replacements.items():
                if target != source:
                    continue
                needle = f'"{path}:{old_line}"'
                if needle in text:
                    text = text.replace(needle, f'"{path}:{new_line}"')
                    changed += 1
            if changed:
                json.loads(text)  # never write a broken file
                source.write_text(text, encoding="utf-8", newline="\n")
                print(f"rewrote {changed} pointer(s) in {source.relative_to(ROOT)}")

    unresolved = len(report["ambiguous"]) + len(report["missing"])
    return 1 if unresolved else 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except HistoryError as exc:
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(2)
