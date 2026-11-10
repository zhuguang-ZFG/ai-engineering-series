"""Independent copies must retain the public contract and actual tool outcomes."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

EXAMPLE = Path(__file__).resolve().parents[1] / "prompt/examples/exercise.py"
SPEC = importlib.util.spec_from_file_location("prompt_exercise", EXAMPLE)
exercise = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(exercise)


class IndependentExercise(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.project = Path(self.temporary.name) / "exercise"
        exercise.prepare(self.project)

    def test_copy_is_independent_and_contains_no_reference_implementation(self):
        self.assertEqual({p.name for p in self.project.iterdir()},
                         {"registration.py", "check.py", "cases.json", "rules.md", "exercise-lock.json"})
        source = (self.project / "registration.py").read_text(encoding="utf-8")
        self.assertNotIn("reference", source)
        self.assertNotIn("faulty=", source)
        result = subprocess.run([sys.executable, "-X", "utf8", "-B", "check.py"],
                                cwd=self.project, capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(result.returncode, 1)
        self.assertEqual(json.loads(result.stdout)["passed"], 8)

    def test_initial_receipt_identifies_the_four_actual_failures(self):
        receipt = exercise.check(self.project)
        self.assertEqual(receipt["status"], "business_failed")
        self.assertEqual(receipt["returncode"], 1)
        self.assertEqual(receipt["business"], {"passed": 8, "total": 12})
        failures = {row["id"] for row in json.loads(receipt["stdout"])["results"] if not row["passed"]}
        self.assertEqual(failures, {"full", "zero", "duplicate-waiting", "cancel-promote"})
        self.assertTrue(receipt["candidate_unchanged_during_check"])

    def test_public_contract_accepts_a_repaired_candidate(self):
        candidate = self.project / "registration.py"
        source = candidate.read_text(encoding="utf-8")
        source = source.replace("if person in confirmed:", "if person in confirmed or person in waiting:", 1)
        source = source.replace("elif len(confirmed) <= capacity:", "elif len(confirmed) < capacity:")
        source = source.replace("        confirmed.remove(person)\n", "        confirmed.remove(person)\n        if waiting:\n            confirmed.append(waiting.pop(0))\n")
        candidate.write_text(source, encoding="utf-8")
        receipt = exercise.check(self.project)
        self.assertEqual(receipt["status"], "passed")
        self.assertEqual(receipt["returncode"], 0)
        self.assertEqual(receipt["business"], {"passed": 12, "total": 12})

    def test_existing_directory_is_not_overwritten(self):
        original = (self.project / "registration.py").read_bytes()
        with self.assertRaises(FileExistsError):
            exercise.prepare(self.project)
        self.assertEqual((self.project / "registration.py").read_bytes(), original)

    def test_changed_rules_cases_or_checker_do_not_run(self):
        for name in exercise.FROZEN_FILES:
            path = self.project / name
            original = path.read_bytes()
            path.write_bytes(original + b"\n")
            receipt = exercise.check(self.project)
            self.assertEqual(receipt["status"], "invalid_project")
            self.assertIsNone(receipt["returncode"])
            path.write_bytes(original)

    def test_missing_project_is_not_reported_as_business_failure(self):
        receipt = exercise.check(self.project / "absent")
        self.assertEqual(receipt["status"], "invalid_project")
        self.assertIsNone(receipt["returncode"])

    def test_syntax_error_is_reported_with_actual_stderr(self):
        (self.project / "registration.py").write_text("def broken(:\n", encoding="utf-8")
        receipt = exercise.check(self.project)
        self.assertEqual(receipt["status"], "execution_failed")
        self.assertIn("SyntaxError", receipt["stderr"])
        self.assertNotEqual(receipt["returncode"], 0)

    def test_timeout_is_distinct_and_preserves_the_attempt(self):
        (self.project / "registration.py").write_text("import time\ntime.sleep(5)\n", encoding="utf-8")
        receipt = exercise.check(self.project, timeout=0.1)
        self.assertEqual(receipt["status"], "timeout")
        self.assertIsNone(receipt["returncode"])

    def test_candidate_mutation_during_run_invalidates_result(self):
        candidate = self.project / "registration.py"
        source = candidate.read_text(encoding="utf-8")
        candidate.write_text(source + '\nfrom pathlib import Path\nPath(__file__).write_text("changed")\n', encoding="utf-8")
        receipt = exercise.check(self.project)
        self.assertEqual(receipt["status"], "input_changed_during_check")
        self.assertFalse(receipt["candidate_unchanged_during_check"])

    def test_bad_timeouts_are_rejected(self):
        for timeout in (0, -1, float("inf"), float("nan")):
            with self.assertRaises(ValueError):
                exercise.check(self.project, timeout)

    def test_cli_receipt_is_not_overwritten(self):
        receipt_path = Path(self.temporary.name) / "receipt.json"
        receipt_path.write_text("keep", encoding="utf-8")
        result = subprocess.run([sys.executable, str(EXAMPLE), "check", "--project", str(self.project),
                                 "--receipt", str(receipt_path)], capture_output=True)
        self.assertEqual(result.returncode, 2)
        self.assertEqual(receipt_path.read_text(encoding="utf-8"), "keep")


if __name__ == "__main__":
    unittest.main()
