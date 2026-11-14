"""Run the same release fixture against both gates and print a diffable report.

    python grok/examples/check_release.py            # faulty build
    python grok/examples/check_release.py --fixed    # reference build

Exit code 1 means at least one case disagreed with its expected verdict, which
is the intended result for the faulty build. `--fixed` exits 0.
"""
from __future__ import annotations

import argparse
import json
import sys
import tempfile
from pathlib import Path

import release_gate
import release_gate_fixed

CASES = (
    # name, version, changelog body, test log, expected number of reasons
    ("clean", "1.10.0", "## [1.10.0]\n- first\n", "Ran 4 tests in 0.01s\n\nOK\n", 0),
    ("numeric_order", "1.9.0", "## [1.9.0]\n- old\n", "Ran 4 tests in 0.01s\n\nOK\n", 1),
    ("missing_section", "1.10.0", "## [1.9.0]\n- old\n", "Ran 4 tests in 0.01s\n\nOK\n", 1),
    ("failed_suite", "1.10.0", "## [1.10.0]\n- first\n",
     "FAILED (failures=1)\nRan 4 tests in 0.01s\n\nOK\n", 1),
    ("no_changelog", "1.10.0", None, "Ran 4 tests in 0.01s\n\nOK\n", 1),
)


def run(fixed: bool) -> list[dict]:
    gate = release_gate_fixed.gate if fixed else release_gate.gate
    rows = []
    for name, version, changelog, log, expected in CASES:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            if changelog is not None:
                (root / "CHANGELOG.md").write_text(changelog, encoding="utf-8")
            (root / "tests.log").write_text(log, encoding="utf-8")
            reasons = gate(root, version)
        rows.append({"case": name, "expected": expected, "actual": len(reasons),
                     "reasons": reasons})
    return rows


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fixed", action="store_true")
    args = parser.parse_args()
    rows = run(args.fixed)
    failures = [r for r in rows if r["actual"] != r["expected"]]
    print(json.dumps({"build": "fixed" if args.fixed else "faulty",
                      "cases": rows, "disagreements": len(failures)},
                     ensure_ascii=False, indent=2))
    return 0 if not failures else 1


if __name__ == "__main__":
    sys.exit(main())
