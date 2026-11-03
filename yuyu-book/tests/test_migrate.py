"""The migration report must be conservative: map what is certain, refuse
to rewrite a marker, and say plainly where a human has to choose."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from yuyu_book.migrate import build_report  # noqa: E402

ZH = "zh/00.md"
EN = "en/00.md"

ZH_TEXT = """# 标题

<!-- block: front.intro -->

Intro body

Same

Same
"""

EN_TEXT = """# Title

<!-- block: front.intro -->

Intro body

Same

Same
"""


def manifest(refs, extra=None):
    front = {"id": "front", "zh": ZH, "en": EN}
    guides = {"front": {"plain_evidence": list(refs)}}
    guides.update(extra or {})
    return {"front": front, "parts": [], "appendices": [], "guides": guides}


class Report(unittest.TestCase):
    def build(self, refs, files=None, glosses=None):
        files = files if files is not None else {
            ZH: ZH_TEXT, EN: EN_TEXT}
        return build_report(manifest(refs), glosses or {}, files=files)

    def row(self, report, field):
        return next(r for r in report["refs"] if r["field"] == field)

    def test_marked_block_is_mapped_and_keeps_its_id(self):
        report = self.build([f"{ZH}:5"])
        row = self.row(report, "manifest.guides.front.plain_evidence[0]")
        self.assertEqual((row["status"], row["block_id"]),
                         ("mapped", "front.intro"))
        self.assertTrue(next(b for b in report["files"][ZH]["blocks"]
                             if b["start"] == 5)["has_marker"])

    def test_two_editions_may_share_one_marker(self):
        report = self.build([f"{ZH}:5", f"{EN}:5"])
        self.assertEqual(report["summary"]["ambiguous"], 0)
        self.assertEqual({r["block_id"] for r in report["refs"]},
                         {"front.intro"})

    def test_identical_blocks_get_a_suffix_and_an_ambiguity(self):
        report = self.build([f"{ZH}:7", f"{ZH}:9"])
        first, second = report["refs"]
        self.assertEqual(first["status"], "mapped")
        self.assertTrue(first["block_id"].startswith("front.b-"))
        self.assertEqual(second["status"], "ambiguous")
        self.assertTrue(second["block_id"].endswith("-2"))
        self.assertIn("choose a semantic slug", second["reason"])

    def test_blank_line_is_missing(self):
        row = self.row(self.build([f"{ZH}:4"]),
                       "manifest.guides.front.plain_evidence[0]")
        self.assertEqual(row["status"], "missing")
        self.assertIn("blank", row["reason"])

    def test_past_the_end_is_missing(self):
        row = self.row(self.build([f"{ZH}:99"]),
                       "manifest.guides.front.plain_evidence[0]")
        self.assertEqual(row["status"], "missing")

    def test_unknown_file_is_missing(self):
        row = self.row(self.build(["nope/missing.md:1"]),
                       "manifest.guides.front.plain_evidence[0]")
        self.assertEqual(row["status"], "missing")
        self.assertIn("not a manifest unit", row["reason"])

    def test_heading_is_a_mapped_block(self):
        row = self.row(self.build([f"{ZH}:1"]),
                       "manifest.guides.front.plain_evidence[0]")
        self.assertEqual(row["status"], "mapped")
        self.assertTrue(row["block_id"].startswith("front.b-"))

    def test_gloss_evidence_is_collected(self):
        glosses = {"term": {"evidence": [f"{EN}:5"]}}
        report = self.build([], glosses=glosses)
        self.assertEqual(report["refs"][0]["field"], "glosses.term.evidence[0]")

    def test_summary_counts_every_pointer(self):
        glosses = {"term": {"evidence": [f"{EN}:5"]}}
        report = self.build([f"{ZH}:5"], glosses=glosses)
        self.assertEqual(report["summary"]["refs"], 2)
        self.assertEqual(report["summary"]["unique_refs"], 2)
        self.assertEqual(report["summary"]["mapped"], 2)


if __name__ == "__main__":
    unittest.main()
