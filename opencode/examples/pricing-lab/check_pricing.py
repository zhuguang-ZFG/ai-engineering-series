"""Run the same behavioral cases against the broken and corrected function."""
from decimal import Decimal
import json

import pricing
import pricing_broken


VALUES = [
    (("19.99", 2), "39.98"),
    (("0.05", 1, "0.5"), "0.03"),
    (("2.50", 3, "0.1"), "6.75"),
    (("19.99", 0), "0.00"),
    (("19.99", 2, "1"), "0.00"),
    (("1000000", 1_000_000), "1000000000000.00"),
]
INVALID = [
    ("-1", 1), ("1", -1), ("1", True), ("1", 1.5),
    ("1", 1_000_001), ("1000001", 1), ("1", 1, "-0.1"),
    ("1", 1, "1.1"), ("NaN", 1), ("Infinity", 1),
    ("1", 1, "NaN"), (1.25, 1), ("invalid", 1),
]


def examine(function):
    failures = []
    for args, expected in VALUES:
        try:
            actual = function(*args)
            # Representation matters: invoice output must retain two decimals.
            if not isinstance(actual, Decimal) or str(actual) != expected:
                failures.append({"input": args, "expected": expected, "actual": str(actual)})
        except Exception as exc:
            failures.append({"input": args, "unexpected_error": type(exc).__name__})
    for args in INVALID:
        try:
            function(*args)
        except ValueError:
            continue
        except Exception as exc:
            failures.append({"input": args, "wrong_error": type(exc).__name__})
        else:
            failures.append({"input": args, "missing_error": "ValueError"})
    return failures


def main():
    broken = examine(pricing_broken.total)
    fixed = examine(pricing.total)
    report = {"cases": len(VALUES) + len(INVALID),
              "broken_failures": broken, "reference_failures": fixed,
              "external_model_used": False}
    print(json.dumps(report, ensure_ascii=False, indent=2))
    # This command succeeds only when the exercise starts red and ends green.
    return 0 if broken and not fixed else 1


if __name__ == "__main__":
    raise SystemExit(main())
