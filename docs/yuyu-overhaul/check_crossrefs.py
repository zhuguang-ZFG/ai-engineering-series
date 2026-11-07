#!/usr/bin/env python3
"""Check that every book <-> omp cross-reference points at a real chapter.

Each side writes "第 N 章《标题》", and the title is reproducible from the target's
H1: book -> omp must match omp/chN.md exactly, omp -> book may abbreviate (so
"《Plan 模式》" passes for H1 "第14章：Plan 模式与结构化工作流"). A literal
"第 M 章" is a leftover placeholder from the SPEC's notation and is reported as
an error. Chapter numbers, not prose, are the contract here. The English book
translates omp chapter titles itself and omp has no English edition, so those
strings stay a hand check.

    python docs/yuyu-overhaul/check_crossrefs.py

Exit 0 prints a per-direction count; exit 1 prints one line per bad reference.
Without omp/ in the checkout there is nothing to check against, so it exits 1
rather than reporting a pass.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from omp.overhaul.markdown_scan import scan_markdown

BOOK_FILES = ["00-前言.md"] + sorted(
    p for d in ROOT.glob("第*篇*") for p in d.glob("*.md")
)
OMP_FILES = sorted(
    list(ROOT.glob("omp/ch*.md"))
    + list(ROOT.glob("omp/appendix-*.md"))
    + list(ROOT.glob("omp/00-前言.md"))
)

H1_CHAPTER = re.compile(r"#\s*第\s*(\d+)\s*章[:：]?\s*(.*)")
H1_APPENDIX = re.compile(r"#\s*附\s*录\s*([A-E])[:：]?\s*(.*)")
REF = re.compile(r"第\s*(\d+)\s*章《([^》]+)》")
REF_APP = re.compile(r"附\s*录\s*([A-E])《([^》]+)》")
PLACEHOLDER = re.compile(r"第\s*M\s*章|chapter\s+M\b", re.IGNORECASE)


def titles(files: list[Path]) -> dict:
    out: dict = {}
    for path in files:
        prose = scan_markdown(path.read_text(encoding="utf-8")).prose
        for line in prose.splitlines():
            for pattern, key in ((H1_CHAPTER, "ch"), (H1_APPENDIX, "app")):
                m = pattern.match(line.strip())
                if m:
                    out[(key, m.group(1).zfill(2) if key == "ch" else m.group(1))] = (
                        m.group(2).strip()
                    )
    return out


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def check_book_to_omp(omp: dict) -> tuple[list[str], int]:
    bad, n = [], 0
    for name in BOOK_FILES:
        path = ROOT / name
        if not path.exists():
            continue
        for ln, line in enumerate(
            path.read_text(encoding="utf-8").splitlines(), 1
        ):
            if "omp 分册" not in line:
                continue
            if PLACEHOLDER.search(line):
                bad.append(f"{rel(path)}:{ln} 占位未填（「第 M 章」）")
            for num, title in REF.findall(line):
                n += 1
                want = omp.get(("ch", num.zfill(2)))
                if want is None:
                    bad.append(f"{rel(path)}:{ln} omp 无第 {num} 章")
                elif want != title:
                    bad.append(
                        f"{rel(path)}:{ln} 第{num}章《{title}》 实为《{want}》"
                    )
    return bad, n


def check_omp_to_book(book: dict) -> tuple[list[str], int]:
    bad, n = [], 0
    for path in OMP_FILES:
        if not path.exists():
            continue
        for ln, line in enumerate(
            path.read_text(encoding="utf-8").splitlines(), 1
        ):
            if "御舆" not in line:
                continue
            # only what follows the marker belongs to the referenced volume
            segment = line[line.index("御舆"):]
            if PLACEHOLDER.search(segment):
                bad.append(f"{rel(path)}:{ln} 占位未填（「第 M 章」）")
            for num, title in REF.findall(segment):
                n += 1
                want = book.get(("ch", num.zfill(2)))
                if want is None:
                    bad.append(f"{rel(path)}:{ln} 御舆无第 {num} 章")
                elif title not in want:
                    bad.append(
                        f"{rel(path)}:{ln} 御舆第{num}章《{title}》 实为《{want}》"
                    )
            for letter, title in REF_APP.findall(segment):
                n += 1
                want = book.get(("app", letter))
                if want is None:
                    bad.append(f"{rel(path)}:{ln} 御舆无附录 {letter}")
                elif title not in want:
                    bad.append(
                        f"{rel(path)}:{ln} 附录{letter}《{title}》 实为《{want}》"
                    )
    return bad, n


def main() -> int:
    if not (ROOT / "omp").is_dir():
        print("omp/ not in this checkout — nothing to check against")
        return 1
    omp = titles(OMP_FILES)
    book = titles([ROOT / n for n in BOOK_FILES] + list(ROOT.glob("附录/*.md")))
    zh_bad, zh_n = check_book_to_omp(omp)
    back_bad, back_n = check_omp_to_book(book)
    print(
        f"book -> omp: {zh_n} refs checked, {len(zh_bad)} bad\n"
        f"omp -> book: {back_n} refs checked, {len(back_bad)} bad"
    )
    for line in zh_bad + back_bad:
        print(" ", line)
    if zh_bad or back_bad:
        return 1
    print("cross-references resolve to real chapters in both directions")
    return 0


if __name__ == "__main__":
    sys.exit(main())
