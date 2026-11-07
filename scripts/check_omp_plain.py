"""Measure the omp volume's prose against a plain-language budget.

The book targets readers new to agents, so the prose has its own budget the
same way each plate has a byte budget:

``sent``   a sentence longer than 60 Chinese characters is one thought too long
``open``   every unit should open with a one-line "开门一句话" summary
``lead``   a section that starts with a table or list skips its explanation

Run it to see what a rewrite should target; ``--strict`` exits non-zero when
any rule is over budget, which is how the batch passes were gated.

Usage::

    python scripts/check_omp_plain.py
    python scripts/check_omp_plain.py --strict
    python scripts/check_omp_plain.py --file omp/ch15.md
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
UNIT = re.compile(r"^(ch\d+|appendix-[A-E]|00-前言)$")
SENTENCE_LIMIT = 60
CJK = re.compile(r"[\u4e00-\u9fff]")


def units(only: str | None = None) -> list[Path]:
    if only:
        return [ROOT / only]
    return sorted(
        p for p in (ROOT / "omp").glob("*.md") if UNIT.match(p.stem)
    )


def prose(text: str) -> list[tuple[int, str]]:
    """Lines outside code fences, with their 1-based numbers."""
    out, fence = [], None
    for number, line in enumerate(text.splitlines(), 1):
        if line.startswith("```"):
            fence = None if fence else "```"
            continue
        if fence is None:
            out.append((number, line))
    return out


def check(path: Path) -> list[str]:
    lines = prose(path.read_text(encoding="utf-8"))
    problems: list[str] = []

    if not any("开门一句话" in line for _, line in lines[:6]):
        problems.append("open    no 开门一句话 one-liner after the title")

    for number, line in lines:
        stripped = line.strip()
        if not stripped or stripped.startswith(("|", "#", "!", "```")):
            continue
        body = re.sub(r"`[^`]*`", "`x`", stripped)
        for sentence in re.split(r"(?<=[。！？])", body):
            length = len(CJK.findall(sentence))
            if length > SENTENCE_LIMIT:
                problems.append(
                    f"sent    :{number} {length} chars — {sentence.strip()[:28]}…"
                )

    for index, (number, line) in enumerate(lines):
        if not line.startswith("## "):
            continue
        for _, follow in lines[index + 1:]:
            candidate = follow.strip()
            if not candidate or candidate.startswith(("<!--", "```")):
                continue
            if candidate.startswith(("|", "- ", "* ")):
                problems.append(f"lead    :{number} section opens with a table or list")
            break
    return problems


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--strict", action="store_true", help="fail when over budget")
    parser.add_argument("--file", help="check one unit, e.g. omp/ch15.md")
    args = parser.parse_args()

    total = 0
    for path in units(args.file):
        problems = check(path)
        total += len(problems)
        if problems:
            print(f"{path.relative_to(ROOT).as_posix()}: {len(problems)}")
            for problem in problems:
                print(f"  {problem}")
    print(f"plain-language budget: {total} finding(s)")
    if args.strict and total:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
