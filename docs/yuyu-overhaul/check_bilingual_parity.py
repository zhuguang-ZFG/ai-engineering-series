#!/usr/bin/env python3
"""M8 Step 1: zh/en structural parity for the 20 units of the 御舆 product.

The bilingual contract has always been asserted in prose («中英文逐章同步») and
never measured, so a chapter could gain a section or a diagram in one language
and the other edition would simply not notice. This script turns that sentence
into three numbers per unit:

    1. both files exist
    2. H2 count differs by at most --max-h2-diff (default 2, the threshold
       registered in BI-AUDIT.md)
    3. Mermaid diagram count is exactly equal

Fence handling is the same scan check_book.check() uses: an opening
````` fence records its info string, so ```mermaid counts once per block and a
line inside a fence can never be read as a heading.

    python docs/yuyu-overhaul/check_bilingual_parity.py
    python docs/yuyu-overhaul/check_bilingual_parity.py --json
    python docs/yuyu-overhaul/check_bilingual_parity.py --max-h2-diff=1

Exit code is the number of failing units (0 = parity holds), so CI can use it
directly. Only the 御舆 product is covered: omp is a zh-only edition, and the
omp unit contract is checked by yuyu-book/tests/test_product_isolation.py.
"""
import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
BOOK = ROOT / "yuyu-book"
sys.path.insert(0, str(BOOK))

H2 = re.compile(r"^##\s+\S")


def unit_pairs():
    from yuyu_book.core import load_configs, unit_stream
    manifest, _sources = load_configs()
    return [(u["id"], u["zh"], u["en"]) for u, _kind, _part in unit_stream(manifest)]


def structure(path: Path):
    """(h2 count, mermaid count) for one markdown file, fence-aware."""
    fence = None
    mermaid = False
    h2 = diagrams = 0
    for line in path.read_text(encoding="utf-8").splitlines():
        marker = re.match(r"^\s*(`{3,}|~{3,})(.*)$", line)
        if marker:
            token, info = marker.groups()
            if fence is None:
                fence = token
                mermaid = info.strip() == "mermaid"
                diagrams += int(mermaid)
            elif (token[0] == fence[0] and len(token) >= len(fence)
                    and not info.strip()):
                fence = None
                mermaid = False
            continue
        if fence:
            continue
        if H2.match(line):
            h2 += 1
    return h2, diagrams


def audit(max_h2_diff: int = 2):
    rows, failures = [], []
    for uid, zh_rel, en_rel in unit_pairs():
        row = {"unit": uid, "zh": zh_rel, "en": en_rel}
        missing = [rel for rel in (zh_rel, en_rel) if not (ROOT / rel).is_file()]
        row["missing"] = missing
        if missing:
            row.update(zh_h2=None, en_h2=None, zh_mermaid=None, en_mermaid=None)
            row["ok"] = False
            failures.append(f"{uid}: missing {', '.join(missing)}")
            rows.append(row)
            continue
        zh_h2, zh_m = structure(ROOT / zh_rel)
        en_h2, en_m = structure(ROOT / en_rel)
        row.update(zh_h2=zh_h2, en_h2=en_h2, zh_mermaid=zh_m, en_mermaid=en_m)
        problems = []
        if abs(zh_h2 - en_h2) > max_h2_diff:
            problems.append(f"{uid}: H2 zh={zh_h2} en={en_h2} diff="
                            f"{abs(zh_h2 - en_h2)} > {max_h2_diff}")
        if zh_m != en_m:
            problems.append(f"{uid}: mermaid zh={zh_m} en={en_m} not equal")
        row["ok"] = not problems
        failures += problems
        rows.append(row)
    return rows, failures


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--max-h2-diff", type=int, default=2, metavar="N",
                    help="accepted H2 count difference between the two editions")
    ap.add_argument("--json", action="store_true", help="machine-readable rows")
    args = ap.parse_args(argv)

    rows, failures = audit(args.max_h2_diff)
    if args.json:
        print(json.dumps(rows, ensure_ascii=False, indent=1))
    else:
        print(f"units={len(rows)}  H2 threshold={args.max_h2_diff}  "
              f"failures={len(failures)}")
        print(f"{'unit':8} {'zh H2':>6} {'en H2':>6} {'Δ':>3} "
              f"{'zh mm':>6} {'en mm':>6}")
        for r in rows:
            if r["missing"]:
                print(f"{r['unit']:8} {'-':>6} {'-':>6} {'-':>3} {'-':>6} {'-':>6}")
                continue
            print(f"{r['unit']:8} {r['zh_h2']:6} {r['en_h2']:6} "
                  f"{r['zh_h2'] - r['en_h2']:3} "
                  f"{r['zh_mermaid']:6} {r['en_mermaid']:6}")
        for f in failures:
            print("FAIL " + f)
        if not failures:
            print("bilingual parity OK")
    return len(failures)


if __name__ == "__main__":
    raise SystemExit(main())
