"""Hold the two gates to the case table, so the book's output stays true.

    python -m unittest discover -s grok/examples -p "test_*.py" -v
"""
from __future__ import annotations

import unittest

import check_release


class GateDisagrees(unittest.TestCase):
    def test_the_faulty_build_misses_three_cases(self):
        rows = check_release.run(fixed=False)
        missed = sorted(r["case"] for r in rows if r["actual"] != r["expected"])
        self.assertEqual(missed, ["failed_suite", "missing_section", "numeric_order"])

    def test_the_reference_build_matches_every_case(self):
        rows = check_release.run(fixed=True)
        self.assertEqual([r["case"] for r in rows if r["actual"] != r["expected"]], [])

    def test_version_order_is_numeric_not_lexical(self):
        rows = {r["case"]: r for r in check_release.run(fixed=True)}
        self.assertEqual(rows["numeric_order"]["actual"], 1)
        self.assertIn("below 1.10.0", rows["numeric_order"]["reasons"][0])


if __name__ == "__main__":
    unittest.main()
