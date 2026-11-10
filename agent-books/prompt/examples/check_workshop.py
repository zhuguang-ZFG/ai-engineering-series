"""Compare implementation outputs with literal expectations frozen from R01-v1."""
from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path

from workshop import transition


def run(mode):
    cases = json.loads((Path(__file__).resolve().parents[1]
                        / "evaluation/business-cases.json").read_text(encoding="utf-8"))
    results = []
    for case in cases:
        request = copy.deepcopy(case["input"])
        actual = transition(**request, faulty=mode == "faulty")
        unchanged = request == case["input"]
        results.append({"id": case["id"], "passed": actual == case["expected"] and unchanged,
                        "input_unchanged": unchanged, "actual": actual,
                        "expected": case["expected"]})
    return {"kind": "offline_business_check", "mode": mode,
            "passed": sum(item["passed"] for item in results),
            "total": len(results), "results": results}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=("faulty", "reference"), required=True)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    report = run(args.mode)
    encoded = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(encoded, encoding="utf-8")
    print(encoded)
    return 0 if report["passed"] == report["total"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
