"""The migration report must be conservative: map what is certain, refuse
to rewrite a marker, and say plainly where a human has to choose."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from yuyu_book import plain  # noqa: E402
from yuyu_book.core import BuildError  # noqa: E402
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
        self.assertTrue(row["text_equal"])
        self.assertEqual(report["summary"]["text_mismatch"], 0)
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


class DualPaths(unittest.TestCase):
    """The shipped registries must survive the vocabulary swap unchanged."""

    @classmethod
    def setUpClass(cls):
        from yuyu_book import migrate, registry
        cls.migrate = migrate
        cls.manifest = registry.load("manifest.json")
        cls.glosses = registry.load("glosses.json")
        cls.paths = registry.load("reading-paths.json")

    def test_block_markers_never_reach_the_rendered_book(self):
        from yuyu_book import render
        from yuyu_book.core import (REPO_ROOT, load_configs, load_unit,
                                    unit_stream)
        unit_def = next(u for u, _k, _p in unit_stream(load_configs()[0])
                        if u["id"] == "ch02")
        unit = load_unit(unit_def, "chapter", "zh", REPO_ROOT)
        out = render.render_unit(unit, {}, diagrams={}, autolink=False)
        self.assertNotIn("<!-- block", out["html"])

    def test_shipped_registry_has_no_line_refs_left(self):
        report = self.migrate.build_report(self.manifest, self.glosses)
        self.assertEqual(report["summary"]["refs"], 0)

    def test_shipped_registry_survives_fifty_inserted_lines(self):
        import tempfile
        from yuyu_book import plain
        from yuyu_book.core import REPO_ROOT, read_text, unit_stream

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for unit, _kind, _part in unit_stream(self.manifest):
                for lang in ("zh", "en"):
                    rel = unit[lang].replace("\\", "/")
                    target = root / rel
                    target.parent.mkdir(parents=True, exist_ok=True)
                    target.write_text("\n" * 50 + read_text(REPO_ROOT / rel),
                                      encoding="utf-8", newline="")
            plain.validate_plain(self.glosses, self.paths, self.manifest,
                                 root=root)

    def test_cli_exits_nonzero_when_the_dual_check_disagrees(self):
        import importlib.util
        import json
        import tempfile
        from unittest import mock

        script = (Path(__file__).resolve().parents[2] / "scripts" /
                  "migrate_line_refs.py")
        spec = importlib.util.spec_from_file_location("migrate_cli", script)
        cli = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cli)
        broken = {"mismatches": [{"ref": "x", "block_id": "y"}]}
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "report.json"
            eq = Path(tmp) / "equivalence.json"
            with mock.patch.object(cli.migrate, "verify_dual",
                                   return_value=broken):
                code = cli.main(["--out", str(out),
                                 "--equivalence", str(eq)])
            self.assertEqual(code, 1)
            self.assertEqual(json.loads(eq.read_text(encoding="utf-8"))
                             ["dual"]["mismatches"], broken["mismatches"])


class ResolverScope(unittest.TestCase):
    """An id proves only the editions whose files carry that marker."""

    def setUp(self):
        import tempfile
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        files = {
            "zh/front.md": "# 前言\n\n<!-- block: front.intro -->\n\n"
                           "前言正文 Agent Harness\n",
            "en/front.md": "# Front\n\n<!-- block: front.intro -->\n\n"
                           "front body Agent Harness\n",
            "zh/ch01.md": "# 标题\n\n<!-- block: ch01.zh-only -->\n\n"
                          "Agent Harness 中文段落\n\n"
                          "<!-- block: ch01.shared -->\n\n"
                          "Agent Harness 共享段落\n",
            "en/ch01.md": "# Title\n\n<!-- block: ch01.en-only -->\n\n"
                          "Agent Harness english paragraph\n\n"
                          "<!-- block: ch01.shared -->\n\n"
                          "Agent Harness shared paragraph\n",
        }
        for rel, text in files.items():
            path = self.root / rel
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding="utf-8")
        self.manifest = {
            "front": {"id": "front", "zh": "zh/front.md",
                      "en": "en/front.md"},
            "parts": [{"id": "p1", "units": [
                {"id": "ch01", "zh": "zh/ch01.md", "en": "en/ch01.md"}]}],
            "appendices": [],
            "guides": {
                "front": {"plain": {"zh": "前", "en": "front"},
                          "plain_evidence": ["front.intro"]},
                "ch01": {"plain": {"zh": "章", "en": "chapter"},
                         "plain_evidence": ["ch01.shared"]},
            },
        }
        self.paths = {"ch01": ["start"]}

    def tearDown(self):
        self.tmp.cleanup()

    def validate(self, evidence):
        g = {"harness": {
            "term": {"zh": "线束", "en": "Agent Harness"},
            "forms": {"zh": ["Agent Harness"], "en": ["Agent Harness"]},
            "plain": {"zh": "一根线", "en": "one harness"},
            "why": {"zh": "因为要接线", "en": "because it wires things"},
            "why_evidence": ["ch01.shared"],
            "priority": "core",
            "evidence": evidence,
        }}
        plain.validate_plain(g, self.paths, self.manifest, root=self.root)

    def test_zh_only_id_cannot_prove_the_english_edition(self):
        with self.assertRaises(BuildError) as ctx:
            self.validate(["ch01.zh-only"])
        self.assertIn("core glosses need evidence in both languages", str(ctx.exception))
        self.assertIn("['zh']", str(ctx.exception))

    def test_en_only_id_cannot_prove_the_chinese_edition(self):
        with self.assertRaises(BuildError) as ctx:
            self.validate(["ch01.en-only"])
        self.assertIn("['en']", str(ctx.exception))

    def test_a_shared_id_proves_both_editions(self):
        self.validate(["ch01.shared"])

    def test_two_scoped_ids_union_into_both_editions(self):
        self.validate(["ch01.zh-only", "ch01.en-only"])


class WritePlan(unittest.TestCase):
    def test_markers_go_above_blocks_and_keep_crlf(self):
        from yuyu_book.migrate import insert_markers
        out = insert_markers("a\r\nb\r\nc\r\n", [(2, "u.one"), (3, "u.two")])
        self.assertEqual(out, "a\r\n<!-- block: u.one -->\r\nb\r\n"
                              "<!-- block: u.two -->\r\nc\r\n")

    def test_registry_rewrite_is_quoted_and_leaves_other_text_alone(self):
        from yuyu_book.migrate import rewrite_registry_text
        text = '{"a": "x.md:5", "b": ["x.md:5"], "note": "x.md:5?"}'
        out = rewrite_registry_text(text, {"x.md:5": "u.b-1234"})
        self.assertEqual(out.count('"u.b-1234"'), 2)
        self.assertIn('"note": "x.md:5?"', out)


if __name__ == "__main__":
    unittest.main()
