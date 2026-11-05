"""Regression checks for the Omp acceptance gates."""
from contextlib import redirect_stdout
import copy
import io
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from omp.overhaul import audit_delivery, audit_structure


class StructureGateTests(unittest.TestCase):
    def test_empty_manuscript_tree_fails_strict_mode(self):
        with tempfile.TemporaryDirectory() as directory:
            with patch.object(audit_structure, "ROOT", Path(directory)):
                with patch("sys.argv", ["audit_structure.py", "--check"]):
                    with redirect_stdout(io.StringIO()):
                        self.assertEqual(audit_structure.main(), 1)

    def test_csv_mode_still_fails_missing_elements(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for number in range(1, 34):
                (root / f"ch{number:02}.md").write_text("# Incomplete chapter\n", encoding="utf-8")
            with patch.object(audit_structure, "ROOT", root):
                with patch("sys.argv", ["audit_structure.py", "--check", "--csv"]):
                    with redirect_stdout(io.StringIO()):
                        self.assertEqual(audit_structure.main(), 1)

    def test_opening_audits_do_not_share_previous_chapters(self):
        self.assertEqual(audit_structure.prose_before_first_h2("# First\n\nOpening.\n\n## Next"), ["Opening."])
        self.assertEqual(audit_structure.prose_before_first_h2("# Second\n\n## Next"), [])


class DeliveryGateTests(unittest.TestCase):
    def run_with_registry_change(self, filename, change):
        original = audit_delivery.load_json

        def changed(root, name):
            data = copy.deepcopy(original(root, name))
            if name == filename:
                change(data)
            return data

        with patch.object(audit_delivery, "load_json", side_effect=changed):
            return audit_delivery.check()

    def test_shipped_delivery_passes(self):
        self.assertEqual(audit_delivery.check(), [])

    def test_one_part_without_diagrams_fails_even_when_total_is_sufficient(self):
        def remove_diagrams(manifest):
            manifest["parts"][0]["units"] = [{"id": "omp-ch02", "zh": "omp/ch02.md"}]
            manifest["parts"][1]["units"].extend([
                {"id": "omp-ch01", "zh": "omp/ch01.md"},
                {"id": "omp-ch03", "zh": "omp/ch03.md"},
            ])

        errors = self.run_with_registry_change("manifest-omp.json", remove_diagrams)
        self.assertTrue(any("omp-p1: no Mermaid" in error for error in errors))
        self.assertFalse(any("at least 12" in error for error in errors))

    def test_shared_term_cannot_point_to_unknown_book_term(self):
        errors = self.run_with_registry_change(
            "glosses-omp.json",
            lambda terms: terms["agent-harness"].update(shared_with="missing-term"),
        )
        self.assertTrue(any("unknown shared glossary ID" in error for error in errors))

    def test_book_implementation_cannot_leak_into_definition(self):
        errors = self.run_with_registry_change(
            "glosses-omp.json",
            lambda terms: terms["agent-harness"]["plain"].update(zh="QueryEngine"),
        )
        self.assertTrue(any("implementation leaked" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
