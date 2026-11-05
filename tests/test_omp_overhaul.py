"""Regression checks for the Omp acceptance gates."""
from contextlib import redirect_stderr, redirect_stdout
import copy
import io
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from omp.overhaul import audit_delivery, audit_structure, markdown_scan


class StructureGateTests(unittest.TestCase):
    def audit_text(self, text):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "ch01.md"
            path.write_text(text, encoding="utf-8")
            return audit_structure.audit(path)

    def test_empty_manuscript_tree_fails_strict_mode(self):
        with tempfile.TemporaryDirectory() as directory:
            with patch.object(audit_structure, "ROOT", Path(directory)):
                with patch("sys.argv", ["audit_structure.py", "--check"]):
                    with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
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

    def test_markdown_example_cannot_supply_chapter_requirements(self):
        row = self.audit_text(
            "# Chapter\n\nA concrete opening scenario with enough words to pass the opening check.\n\n"
            "````markdown\n## 跟做实验\n```sh\nomp --version\n```\n"
            "## 翻车对照\n| 问题 | 结果 |\n| --- | --- |\n| 错误 | 重试 |\n"
            "![示例](images/example.jpg)\n御舆\n版本核对：本机已验\n````\n"
        )
        for element in ("e2_principle_figure", "e3_runnable_experiment", "e4_pit_table",
                        "e5_yuyu_isomorphism", "e6_pin_checklist", "mark_verified"):
            self.assertEqual(row[element], "n", element)

    def test_commented_out_content_cannot_supply_chapter_requirements(self):
        row = self.audit_text(
            "# Chapter\n\nA concrete opening scenario with enough words to pass the opening check.\n\n"
            "<!--\n## 跟做实验\n```sh\nomp --version\n```\n"
            "## 翻车对照\n| 问题 | 结果 |\n| --- | --- |\n| 错误 | 重试 |\n"
            "![示例](images/example.jpg)\n御舆\n版本核对：本机已验\n-->\n"
        )
        for element in ("e2_principle_figure", "e3_runnable_experiment", "e4_pit_table",
                        "e5_yuyu_isomorphism", "e6_pin_checklist", "mark_verified"):
            self.assertEqual(row[element], "n", element)

    def test_tilde_mermaid_counts_as_a_real_figure(self):
        row = self.audit_text("# Chapter\n\n~~~mermaid\nflowchart LR\n  FIRST --> SECOND\n~~~\n")
        self.assertEqual(row["e2_principle_figure"], "Y")
        self.assertEqual(row["mermaid"], 1)

    def test_versioned_binary_observation_is_a_verification_marker(self):
        row = self.audit_text("# Chapter\n\n本机 18.16.0 回「在线」且 exit 0（facts/print-mode-online.txt）。\n")
        self.assertEqual(row["mark_verified"], "Y")

    def test_mermaid_info_must_match_the_builder(self):
        for info in ("Mermaid", "mermaid example"):
            with self.subTest(info=info):
                row = self.audit_text(f"# Chapter\n\n```{info}\nflowchart LR\n  FIRST --> SECOND\n```\n")
                self.assertEqual(row["e2_principle_figure"], "n")
                self.assertEqual(row["mermaid"], 0)

    def test_missing_chapter_cannot_be_replaced_by_an_extra_filename(self):
        valid_row = {key: "Y" for key in (
            "e1_opening_scene", "e2_principle_figure", "e3_runnable_experiment",
            "e4_pit_table", "e5_yuyu_isomorphism", "e6_pin_checklist", "mark_verified")}
        valid_row.update(unit="chapter", e3_cmd_blocks=1, han=0, chars=0)
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for number in (*range(1, 33), 99):
                (root / f"ch{number:02}.md").touch()
            with patch.object(audit_structure, "ROOT", root):
                with patch.object(audit_structure, "audit", return_value=valid_row):
                    with patch("sys.argv", ["audit_structure.py", "--check"]):
                        with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
                            self.assertEqual(audit_structure.main(), 1)

    def test_pipe_in_prose_does_not_count_as_a_failure_table(self):
        row = self.audit_text("# Chapter\n\n## 翻车\n| 这里只是一行示例 | 不是表格 |\n")
        self.assertEqual(row["e4_pit_table"], "n")

    def test_unclosed_fence_fails_even_when_all_other_requirements_pass(self):
        valid_row = {key: "Y" for key in (
            "e1_opening_scene", "e2_principle_figure", "e3_runnable_experiment",
            "e4_pit_table", "e5_yuyu_isomorphism", "e6_pin_checklist", "mark_verified")}
        valid_row.update(unit="chapter", e3_cmd_blocks=1, han=0, chars=0,
                         errors=["line 3: unclosed code fence"])
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for number in range(1, 34):
                (root / f"ch{number:02}.md").touch()
            with patch.object(audit_structure, "ROOT", root):
                with patch.object(audit_structure, "audit", return_value=valid_row):
                    with patch("sys.argv", ["audit_structure.py", "--check", "--csv"]):
                        with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
                            self.assertEqual(audit_structure.main(), 1)


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

    def test_missing_front_and_appendix_are_reported(self):
        for location in ("front", "appendices"):
            def remove_manuscript(manifest):
                unit = manifest["front"] if location == "front" else manifest["appendices"][0]
                unit["zh"] = "omp/missing-manuscript.md"

            with self.subTest(location=location):
                errors = self.run_with_registry_change("manifest-omp.json", remove_manuscript)
                self.assertTrue(any("missing-manuscript.md" in error for error in errors))

    def test_reference_image_in_appendix_is_checked(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "appendix.md"
            path.write_text('![Caption][drawing]\n\n[drawing]: images/missing.jpg "Caption"\n', encoding="utf-8")
            errors = self.run_with_registry_change(
                "manifest-omp.json",
                lambda manifest: manifest["appendices"][0].update(zh=str(path)),
            )
        self.assertTrue(any("images/missing.jpg" in error for error in errors))

    def test_malformed_shared_term_has_a_diagnostic(self):
        errors = self.run_with_registry_change(
            "glosses-omp.json",
            lambda terms: terms["agent-harness"].update(shared_with=["agent-harness"]),
        )
        self.assertTrue(any("shared_with" in error for error in errors))

    def test_invalid_registry_is_reported_without_a_traceback(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "yuyu-book").mkdir()
            (root / "yuyu-book/manifest-omp.json").write_text("{", encoding="utf-8")
            errors = audit_delivery.check(root)
        self.assertTrue(any("manifest-omp.json" in error for error in errors))

    def test_nested_mermaid_example_cannot_supply_part_coverage(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "example.md"
            path.write_text("````markdown\n```mermaid\nflowchart LR\n  FIRST --> SECOND\n```\n````\n", encoding="utf-8")
            errors = self.run_with_registry_change(
                "manifest-omp.json",
                lambda manifest: manifest["parts"][0].update(units=[{"id": "omp-ch01", "zh": str(path)}]),
            )
        self.assertTrue(any("omp-p1: no Mermaid diagram" in error for error in errors))


class MarkdownScanTests(unittest.TestCase):
    def test_nested_example_keeps_the_outer_fence(self):
        content = markdown_scan.scan_markdown(
            "Before\n````markdown\n```mermaid\nflowchart LR\n  FIRST --> SECOND\n```\n````\nAfter"
        )
        self.assertEqual([language for language, _ in content.blocks], ["markdown"])
        self.assertEqual(content.prose.splitlines(), ["Before", "", "", "", "", "", "", "After"])
        self.assertEqual(content.errors, [])

    def test_comment_can_close_before_visible_content_on_the_same_line(self):
        content = markdown_scan.scan_markdown("Before <!-- hidden\n```mermaid\n--> After")
        self.assertEqual(content.prose, "Before \n\n After")
        self.assertEqual(content.blocks, [])
        self.assertEqual(content.errors, [])

    def test_unclosed_markdown_reports_its_location(self):
        content = markdown_scan.scan_markdown("Before\n~~~mermaid\nflowchart LR")
        self.assertEqual(content.blocks, [])
        self.assertEqual(content.errors, ["line 2: unclosed code fence"])

    def test_only_rendered_images_are_collected(self):
        prose = (
            '`![Example](images/code.jpg)`\n\n'
            '![Actual][picture]\n\n[picture]: <images/my%20image.jpg> "Caption"\n\n'
            '<img src="images/html.jpg">'
        )
        self.assertEqual(markdown_scan.image_sources(prose), ["images/my%20image.jpg", "images/html.jpg"])

    def test_literal_comment_marker_in_inline_code_does_not_hide_prose(self):
        text = "Use `<!--` in an example.\n\n## Still visible\n"
        content = markdown_scan.scan_markdown(text)
        self.assertEqual(content.prose, text.rstrip("\n"))
        self.assertEqual(content.errors, [])


if __name__ == "__main__":
    unittest.main()
