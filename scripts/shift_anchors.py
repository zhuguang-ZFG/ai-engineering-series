#!/usr/bin/env python3
"""Move every `file:line` anchor when the prose it points at moves down.

A plate costs the prose six lines. The two registries that quote prose by line
number have to follow, or the plain-language layer's evidence pointers land on
a separator line — and `plain.validate_plain()` fails the build for it, which
is the loud version of a reader being shown the wrong sentence.

Only the digits are touched: glosses.json is written with one-space indent and
manifest.json with two, both with CRLF, and re-dumping either would bury a
six-line change under 500 lines of reformatting.

    python scripts/shift_anchors.py --after 289 --delta 6 <file> [<file> …]
    python scripts/shift_anchors.py --after 289 --delta 6 --write <file> …

Refs on the insert line itself and above it stay; the six new lines start at
after+1. Pass both language files together: they are line-for-line aligned, so
one number serves both.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REGISTRY_NAMES = ("glosses.json", "manifest.json")
REF = re.compile(r'"(?P<path>[^"\n]+\.md):(?P<line>\d+)"')


def shift(text: str, files: frozenset[str], after: int,
          delta: int) -> tuple[str, list[tuple[str, int, int]]]:
    """Rewrite the refs that point into `files` past `after`; report them."""
    hits: list[tuple[str, int, int]] = []

    def repl(m: re.Match[str]) -> str:
        rel, line = m.group("path"), int(m.group("line"))
        if rel.replace("\\", "/") not in files or line <= after:
            return m.group(0)
        hits.append((rel, line, line + delta))
        return f'"{rel}:{line + delta}"'

    return REF.sub(repl, text), hits


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("files", nargs="+", help="prose file(s), repo-relative")
    ap.add_argument("--after", type=int, required=True,
                    help="the blank line the block goes under")
    ap.add_argument("--delta", type=int, default=6)
    ap.add_argument("--write", action="store_true",
                    help="save the registries (default: print the plan)")
    args = ap.parse_args(argv)

    targets = frozenset(f.replace("\\", "/") for f in args.files)
    missing = [f for f in targets if not (ROOT / f).exists()]
    if missing:
        print(f"no such prose file: {', '.join(missing)}", file=sys.stderr)
        return 2

    moved = 0
    for name in REGISTRY_NAMES:
        path = ROOT / "yuyu-book" / name
        # read_bytes()/write_bytes(): no newline translation. The newline=
        # kwarg of Path.read_text/write_text needs 3.13 and CI runs 3.12.
        text = path.read_bytes().decode("utf-8")
        out, hits = shift(text, targets, args.after, args.delta)
        for rel, frm, to in hits:
            print(f"{name}: {rel}:{frm} -> {to}")
        moved += len(hits)
        if out != text and args.write:
            path.write_bytes(out.encode("utf-8"))
    print(f"{'written' if args.write else 'planned'}: {moved} anchors")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
