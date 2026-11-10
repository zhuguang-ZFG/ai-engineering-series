"""Behavior checks for the book's deterministic project; no model or Hermes."""
import json
from pathlib import Path
import tempfile
import unittest

from aurora_lab import initialize, inspect


class AuroraTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve() / "project"
        initialize(self.root)

    def rules(self, **updates):
        path = self.root / "rules.json"
        value = json.loads(path.read_text(encoding="utf-8"))
        value.update(updates)
        path.write_text(json.dumps(value), encoding="utf-8")

    def test_initial_state_is_stable_and_archive_excluded(self):
        result = inspect(self.root)
        self.assertEqual(result, inspect(self.root))
        self.assertEqual(result["status"], "checked")
        self.assertEqual(len(result["snapshot"]["files"]), 3)

    def test_change_and_recovery_have_distinct_input_digest(self):
        initial = inspect(self.root)
        original = self.root / "docs/setup.md"
        original.rename(self.root / "docs/install.md")
        broken = inspect(self.root)
        self.assertEqual(broken["issues"][0]["target"], "setup.md")
        index = self.root / "docs/index.md"
        index.write_text(index.read_text(encoding="utf-8").replace("setup.md", "install.md"), encoding="utf-8")
        fixed = inspect(self.root)
        self.assertEqual(fixed["status"], "checked")
        self.assertEqual(len({r["input_digest"] for r in (initial, broken, fixed)}), 3)

    def test_example_url_is_an_observation_not_a_broken_link(self):
        self.assertEqual(inspect(self.root)["observations"], [])
        self.rules(scan_examples=True)
        result = inspect(self.root)
        self.assertEqual(result["issues"], [])
        self.assertTrue(result["observations"][0]["placeholder"])

    def test_archive_policy_is_explicit(self):
        self.rules(include_archive=True)
        result = inspect(self.root)
        self.assertEqual(result["issues"][0]["path"], "archive/old-plan.md")

    def test_external_path_is_rejected(self):
        (self.root / "docs/index.md").write_text("[Outside](../../private.md)", encoding="utf-8")
        self.assertEqual(inspect(self.root)["issues"][0]["kind"], "outside-root")

    def test_bad_policy_and_reinitialization_fail(self):
        with self.assertRaises(ValueError):
            initialize(self.root)
        self.rules(scan_examples="false")
        with self.assertRaises(ValueError):
            inspect(self.root)


if __name__ == "__main__":
    unittest.main()
