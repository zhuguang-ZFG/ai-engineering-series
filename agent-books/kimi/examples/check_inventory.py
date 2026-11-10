"""Run the same business cases against the faulty and reference implementations."""
from __future__ import annotations

import argparse
import json

import inventory
import inventory_fixed

CASES = (
    ("ordinary", 10, 3, 7),
    ("reserve_all", 10, 10, 0),
    ("over_stock", 10, 11, "ValueError"),
    ("negative_quantity", 10, -2, "ValueError"),
    ("zero_quantity", 10, 0, "ValueError"),
    ("negative_stock", -1, 1, "ValueError"),
    ("boolean_quantity", 10, True, "TypeError"),
    ("fractional_quantity", 10, 1.5, "TypeError"),
)


def check(fixed: bool = False) -> dict:
    function = inventory_fixed.reserve if fixed else inventory.reserve
    results = []
    for name, stock, quantity, expected in CASES:
        try:
            actual = function(stock, quantity)
        except (TypeError, ValueError) as error:
            actual = type(error).__name__
        results.append({"case": name, "stock": stock, "quantity": quantity,
                        "expected": expected, "actual": actual,
                        "passed": actual == expected})
    return {"implementation": "fixed" if fixed else "exercise", "cases": results,
            "passed": sum(case["passed"] for case in results), "total": len(results)}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fixed", action="store_true")
    args = parser.parse_args()
    report = check(args.fixed)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    raise SystemExit(0 if report["passed"] == report["total"] else 1)
