"""P3.7's gate: the legacy/v2 structural comparison must name every delta."""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import compare_legacy as cl  # noqa: E402

ALLOW = ROOT / "docs" / "baseline" / "legacy-v2-deltas.json"


class DiffWalk(unittest.TestCase):
    def test_scalar_change_is_one_value_diff(self):
        diffs = cl.diff_reports({"a": 1}, {"a": 2})
        self.assertEqual(len(diffs), 1)
        self.assertEqual((diffs[0].path, diffs[0].kind), ("/a", "value"))
        self.assertEqual((diffs[0].legacy, diffs[0].fresh), (1, 2))

    def test_list_length_change_is_a_len_diff_not_element_noise(self):
        diffs = cl.diff_reports({"xs": [1, 2]}, {"xs": [1, 2, 3]})
        self.assertEqual([(d.path, d.kind, d.legacy, d.fresh) for d in diffs],
                         [("/xs", "len", 2, 3)])

    def test_same_length_list_recurses_to_the_moved_element(self):
        diffs = cl.diff_reports({"xs": [{"n": 1}]}, {"xs": [{"n": 2}]})
        self.assertEqual([(d.path, d.kind) for d in diffs], [("/xs[0]/n", "value")])

    def test_added_and_removed_keys_are_reported(self):
        diffs = cl.diff_reports({"a": 1}, {"b": 2})
        kinds = {(d.path, d.kind) for d in diffs}
        self.assertEqual(kinds, {("/a", "removed"), ("/b", "added")})

    def test_equal_reports_have_no_diff(self):
        self.assertEqual(cl.diff_reports({"a": [1, {"b": "c"}]},
                                         {"a": [1, {"b": "c"}]}), [])


class AllowlistMatching(unittest.TestCase):
    def rule(self, **overrides):
        base = dict(path="/editions/*/units[*]/tables", delta=1)
        base.update(overrides)
        return base

    def test_wildcards_cover_language_and_unit_index(self):
        diff = cl.Diff("/editions/zh/units[13]/tables", "value", 7, 8)
        self.assertTrue(cl.rule_matches(self.rule(), diff))
        diff = cl.Diff("/editions/zh/units[13]/headings/h2", "value", 7, 8)
        self.assertFalse(cl.rule_matches(self.rule(), diff))

    def test_delta_must_match_exactly(self):
        diff = cl.Diff("/editions/zh/units[13]/tables", "value", 7, 9)
        self.assertFalse(cl.rule_matches(self.rule(), diff))

    def test_len_diffs_need_the_len_kind(self):
        diff = cl.Diff("/editions/zh/units[13]/heading_anchors", "len", 31, 32)
        rule = self.rule(path="/editions/*/units[*]/heading_anchors", kind="len")
        self.assertTrue(cl.rule_matches(rule, diff))
        self.assertFalse(cl.rule_matches({**rule, "kind": "value"}, diff))

    def test_classify_separates_declared_from_unexpected(self):
        diffs = [cl.Diff("/editions/zh/units[1]/tables", "value", 1, 2),
                 cl.Diff("/editions/zh/units[1]/figures", "value", 4, 3)]
        matched, unmatched = cl.classify(diffs, [self.rule()])
        self.assertEqual(len(matched), 1)
        self.assertEqual([d.path for d, _r in unmatched],
                         ["/editions/zh/units[1]/figures"])


class RuleLoading(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.commit = subprocess.run(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, check=True,
            capture_output=True, text=True).stdout.strip()

    def rule(self, **overrides):
        rule = dict(path="/book/version", legacy="0.3.5", fresh="0.3.6",
                    reason="A versioned content release", commit=self.commit)
        rule.update(overrides)
        return rule

    def load(self, *rules):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "deltas.json"
            path.write_text(json.dumps({"schema_version": 1,
                                        "deltas": list(rules)}), encoding="utf-8")
            return cl.load_rules(path)

    def test_exact_rule_requires_both_before_and_after_values(self):
        rules = self.load(self.rule())
        diffs = [cl.Diff("/book/version", "value", "0.3.5", "0.3.6"),
                 cl.Diff("/book/version", "value", "0.3.4", "0.3.6"),
                 cl.Diff("/book/version", "value", "0.3.5", "0.3.7")]
        matched, unmatched = cl.classify(diffs, rules)
        self.assertEqual([diff for diff, _ in matched], diffs[:1])
        self.assertEqual([diff for diff, _ in unmatched], diffs[1:])

    def test_numeric_rule_does_not_allow_a_different_delta(self):
        rule = dict(path="/editions/*/pdf/pages", delta=7,
                    reason="Added exercises", commit=self.commit)
        rules = self.load(rule)
        expected = cl.Diff("/editions/zh/pdf/pages", "value", 518, 525)
        drift = cl.Diff("/editions/en/pdf/pages", "value", 569, 577)
        matched, unmatched = cl.classify([expected, drift], rules)
        self.assertEqual([diff for diff, _ in matched], [expected])
        self.assertEqual([diff for diff, _ in unmatched], [drift])

    def test_value_less_or_one_sided_exact_rules_are_rejected(self):
        for missing in (("legacy",), ("fresh",), ("legacy", "fresh")):
            rule = self.rule()
            for name in missing:
                rule.pop(name)
            with self.subTest(missing=missing):
                with self.assertRaisesRegex(ValueError, "legacy.*fresh"):
                    self.load(rule)

    def test_delta_cannot_override_an_exact_pair(self):
        with self.assertRaisesRegex(ValueError, "either.*delta"):
            self.load(self.rule(delta=1))

    def test_delta_must_be_a_finite_number_not_a_boolean(self):
        for delta in (True, "7", None, float("inf"), float("nan")):
            with self.subTest(delta=delta):
                with self.assertRaisesRegex(ValueError, "finite number"):
                    self.load(dict(path="/count", delta=delta,
                                   reason="Content count", commit=self.commit))

    def test_provenance_must_name_an_existing_commit(self):
        for commit in ("working tree (P5.5)", "0" * 40):
            with self.subTest(commit=commit):
                with self.assertRaisesRegex(ValueError, "commit"):
                    self.load(self.rule(commit=commit))

    def test_rules_without_a_path_reason_or_supported_kind_are_rejected(self):
        for field, value in (("path", "book/version"), ("reason", ""),
                             ("kind", "added")):
            with self.subTest(field=field):
                with self.assertRaisesRegex(ValueError, field):
                    self.load(self.rule(**{field: value}))

    def test_invalid_rule_documents_are_named_before_comparison(self):
        for document in ({"schema_version": 2, "deltas": [self.rule()]},
                         {"schema_version": 1, "deltas": []},
                         {"schema_version": 1, "deltas": [None]}):
            with tempfile.TemporaryDirectory() as directory:
                path = Path(directory) / "invalid.json"
                path.write_text(json.dumps(document), encoding="utf-8")
                with self.subTest(document=document):
                    with self.assertRaisesRegex(ValueError, "invalid.json"):
                        cl.load_rules(path)

    def test_invalid_provenance_stops_the_cli_before_artifact_comparison(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "invalid.json"
            path.write_text(json.dumps({"schema_version": 1, "deltas": [
                self.rule(commit="working tree (P5.5)")]}), encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(ROOT / "scripts/compare_legacy.py"),
                 "--allow", str(path), "--dist", directory], cwd=ROOT,
                capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(result.returncode, 2)
        self.assertIn("invalid comparison rules:", result.stderr)
        self.assertIn("commit", result.stderr)
        self.assertNotIn("missing build artifacts", result.stderr)
        self.assertNotIn("GREEN", result.stdout)


class ShippedRules(unittest.TestCase):
    def test_version_release_is_accounted_for_without_hiding_a_different_release(self):
        rules = cl.load_rules(ALLOW)
        baseline = json.loads((ROOT / "docs/baseline/baseline.json").read_text(
            encoding="utf-8"))
        current = json.loads((ROOT / "yuyu-book/manifest.json").read_text(
            encoding="utf-8"))
        release = cl.Diff("/book/version", "value", baseline["book"]["version"],
                          current["version"])
        unknown = cl.Diff("/book/version", "value", baseline["book"]["version"],
                          "99.0.0")
        matched, unmatched = cl.classify([release, unknown], rules)
        self.assertEqual([diff for diff, _ in matched], [release])
        self.assertEqual([diff for diff, _ in unmatched], [unknown])


if __name__ == "__main__":
    unittest.main()
