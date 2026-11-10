#!/usr/bin/env python3
"""Scan book/book.md for hand-drawn illustration points (Phase C step 1).

Applies the red-line rules from design/handdraw/README.md:
- prefer sections with 0 local images and a long prose-only run;
- a new figure needs >=400-500 chars of prose on both sides of its anchor;
- code, tables and existing figures are untouchable, they only push spacing.

    python design/handdraw/scan_illustration_points.py [--min-gap 1000]

Prints one candidate per line: chapter | section | line | imgs | maxgap | code-ratio.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BOOK = ROOT / "book" / "book.md"

FENCE = re.compile(r"^(```|~~~)")
IMG = re.compile(r"!\[[^\]]*\]\(|<img\s|<figure")
HEAD3 = re.compile(r"^###\s+(?!#)")
HEAD2 = re.compile(r"^##\s+(?!#)")
HEAD_ANY = re.compile(r"^(#{2,6})\s+")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--min-gap", type=int, default=1000)
    ap.add_argument("--top", type=int, default=0, help="print at most N candidates (0 = all)")
    args = ap.parse_args()

    lines = BOOK.read_text(encoding="utf-8-sig").splitlines()

    sections: list[dict] = []
    cur_chapter = "(preamble)"
    cur: dict | None = None
    in_fence = False
    for idx, line in enumerate(lines, start=1):
        if FENCE.match(line.strip()):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        if HEAD2.match(line):
            cur_chapter = line[3:].strip()
            continue
        if HEAD3.match(line):
            if cur:
                sections.append(cur)
            cur = {
                "chapter": cur_chapter,
                "title": line[4:].strip(),
                "start": idx,
                "code_lines": 0,
                "prose_chars": 0,
                "img_lines": [],
                "in_fence": False,
            }
            continue
        if cur is None:
            continue
        if line.lstrip().startswith("|") or re.match(r"^\s*[-*]\s", line):
            pass
        if IMG.search(line):
            cur["img_lines"].append(idx)
        stripped = line.strip()
        if stripped.startswith("```") or stripped.startswith("~~~"):
            cur["in_fence"] = not cur["in_fence"]
            continue
        if cur["in_fence"]:
            cur["code_lines"] += 1
            continue
        if HEAD_ANY.match(line):
            continue
        cur["prose_chars"] += len(re.sub(r"\s", "", line))

    if cur:
        sections.append(cur)

    # second pass needs fence state per section; recompute code ratio by slicing
    results = []
    for i, sec in enumerate(sections):
        start = sec["start"]
        end = sections[i + 1]["start"] - 1 if i + 1 < len(sections) else len(lines)
        body = lines[start:end]
        code = prose = 0
        fence = False
        runs: list[tuple[int, int]] = []  # (line, prose_chars) per line for gap math
        for off, ln in enumerate(body):
            if FENCE.match(ln.strip()):
                fence = not fence
                continue
            if fence:
                code += 1
                runs.append((start + off, -1))
                continue
            n = len(re.sub(r"\s", "", ln))
            prose += n
            runs.append((start + off, n))
        img_offsets = [l for l in sec["img_lines"] if start <= l <= end]
        # longest prose-only run between images / section bounds
        bounds = [start] + img_offsets + [end + 1]
        best_gap, best_mid = 0, start
        for lo, hi in zip(bounds, bounds[1:]):
            acc = 0
            first = last = None
            for ln, n in runs:
                if lo <= ln < hi and n > 0:
                    acc += n
                    if first is None:
                        first = ln
                    last = ln
            if acc > best_gap and first is not None:
                best_gap, best_mid = acc, (first + last) // 2
        total = prose + code
        results.append({
            **sec,
            "end": end,
            "prose": prose,
            "code_ratio": code / total if total else 0.0,
            "imgs": len(img_offsets),
            "gap": best_gap,
            "gap_line": best_mid,
        })

    cands = [r for r in results if r["gap"] >= args.min_gap and r["code_ratio"] < 0.5]
    cands.sort(key=lambda r: -r["gap"])
    if args.top:
        cands = cands[: args.top]
    print(f"sections={len(results)} candidates={len(cands)} min_gap={args.min_gap}")
    for r in cands:
        print(
            f"{r['chapter'][:24]:24} | {r['title'][:30]:30} | line {r['gap_line']:6} "
            f"| imgs {r['imgs']:2} | gap {r['gap']:5} | code {r['code_ratio']:.2f}"
        )


if __name__ == "__main__":
    sys.exit(main())
