"""The `ill` fence: the prose names a drawing, the shelf supplies it.

A ```ill fence is neither code nor diagram — it is a hole cut in the prose for
one file in `illustrations/`. Two bugs were found the hard way while wiring it
up, and both are pinned here: a closing fence that left the buffer open
swallowed the *next* fence's body and tried to read it as a drawing name, and a
placeholder line measured before the blank-line pass pointed the caption lookup
a row or two above where the slot really sits. The rest of the module is what
the reader ends up seeing: a figure numbered with the diagrams, captioned by
the heading above it, and animated only if the drawing says it is a sequence.
"""
import re
import sys
import tempfile
import unittest
from pathlib import Path

if not __package__:  # direct run: see tests/__init__.py for the real bootstrap
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from yuyu_book import art, render  # noqa: E402
from yuyu_book.core import (REPO_ROOT, BuildError, IllusBlock, Unit,  # noqa: E402
                            expected_ids, extract_illustrations, extract_mermaid,
                            load_configs, load_unit, normalize_h1, unit_stream)

ILL_PH = re.compile(r"@@ILL:([0-9a-f]{12})@@")
LINE_SVG = ('<svg viewBox="0 0 340 156" fill="none" stroke="currentColor">'
            '<path d="M8 130h300"/></svg>')
SEQ_SVG = ('<svg class="a-strip seq" viewBox="0 0 348 106" fill="none" '
           'stroke="currentColor"><g class="frame"><rect x="8" y="18" '
           'width="80" height="52"/></g><g class="frame"><rect x="96" y="18" '
           'width="80" height="52"/></g></svg>')

CH03 = "第一部分-基础篇/03-工具系统-Agent的双手.md"


def slot_texts(text: str, file: str = "t.md"):
    """Both fence passes, the way load_unit runs them."""
    return extract_illustrations(extract_mermaid(text, file)[0], file)


def fixture_unit(uid: str, name: str, body: str, lang="zh",
                 unit_id="ch03", no="第 3 章") -> Unit:
    line = next(i for i, row in enumerate(body.split("\n"), 1)
                if f"@@ILL:{uid}@@" in row)
    return Unit(id=unit_id, kind="chapter", lang=lang, no=no, title="工具系统",
                md=body, ills=[IllusBlock(uid, name, "t.md", line)])


class FencePass(unittest.TestCase):
    def test_an_ill_fence_becomes_one_placeholder_and_no_fence(self):
        text = ("正文。\n\n```ill\nch03-tool-bench\n```\n\n"
                "## 3.2 工具注册\n\n清单如下。\n")
        body, ills = slot_texts(text)
        self.assertEqual(len(ills), 1)
        self.assertEqual(ills[0].name, "ch03-tool-bench")
        self.assertEqual(ILL_PH.findall(body), [ills[0].uid])
        self.assertNotIn("ch03-tool-bench", body)
        self.assertNotIn("```", body)

    def test_a_plain_fence_after_an_ill_fence_stays_a_plain_fence(self):
        # the first version left `buf` open past the ill fence, so this bash
        # body was collected as a drawing name and its ``` read as an ill close
        text = ("```ill\nbench\n```\n\n"
                "```bash\nls -la\n# a comment\n```\n\n尾部。\n")
        body, ills = slot_texts(text)
        self.assertEqual([b.name for b in ills], ["bench"])
        self.assertIn("```bash", body)
        self.assertIn("ls -la", body)
        self.assertIn("# a comment", body)

    def test_an_ill_fence_holding_prose_is_rejected(self):
        for bad in ("```ill\nbench\nmore\n```", "```ill\n```",
                    "```ill\nBench Tool.svg\n```"):
            with self.subTest(bad=bad):
                with self.assertRaises(BuildError):
                    slot_texts(bad + "\n")

    def test_an_unclosed_ill_fence_is_reported_with_its_line(self):
        with self.assertRaises(BuildError) as ctx:
            slot_texts("正文。\n\n```ill\nbench\n")
        self.assertIn("unclosed", str(ctx.exception))

    def test_a_slot_reports_the_line_its_placeholder_sits_on(self):
        # the pass that guarantees a blank line under a placeholder pushes every
        # later row down; a caption looked up on the pre-pass line lands wrong
        text = ("## 3.2 上\n\n```ill\nfirst\n```\n"
                "紧贴的正文。\n\n## 3.4 下\n\n```ill\nsecond\n```\n")
        body, ills = slot_texts(text)
        by_uid = {b.uid: b for b in ills}
        for match in ILL_PH.finditer(body):
            block = by_uid[match.group(1)]
            real = body[:match.start()].count("\n") + 1
            self.assertEqual(block.line, real, block.name)

    def test_the_same_drawing_asked_for_twice_is_two_slots(self):
        text = ("```ill\nbench\n```\n\n```ill\nbench\n```\n")
        _body, ills = slot_texts(text)
        self.assertEqual(len({b.uid for b in ills}), 2)
        self.assertEqual({b.name for b in ills}, {"bench"})


class SlotCaptions(unittest.TestCase):
    def test_a_plate_borrows_the_heading_above_it(self):
        text = ("## 3.2 工具注册与动态发现\n\n```ill\nbench\n```\n\n正文。\n")
        body, ills = slot_texts(text)
        unit = Unit(id="ch03", kind="chapter", lang="zh", no="第 3 章",
                    title="工具系统", md=body, ills=ills)
        name, cap = render.drawing_slots(unit)[ills[0].uid]
        self.assertEqual((name, cap), ("bench", "3.2 工具注册与动态发现"))

    def test_a_slot_under_no_heading_at_all_falls_back(self):
        body, ills = slot_texts("```ill\nbench\n```\n")
        unit = Unit(id="ch03", kind="chapter", lang="zh", no="第 3 章",
                    title="工具系统", md=body, ills=ills)
        self.assertEqual(render.drawing_slots(unit)[ills[0].uid][1], "架构示意")

    def test_an_ill_fence_is_never_counted_as_a_code_language(self):
        manifest, _sources = load_configs()
        unit_def, kind = next((u, k) for u, k, _p in unit_stream(manifest)
                              if u["id"] == "ch03")
        unit = load_unit(unit_def, kind, "zh", REPO_ROOT)
        self.assertNotIn("ill", unit.code_langs)
        self.assertEqual([b.name for b in unit.ills],
                         ["ch03-tool-bench", "ch03-tool-pipeline"])


class RenderedPlates(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest, _sources = load_configs()
        cls.mapping = {i: i for i in expected_ids(cls.manifest)}

    def setUp(self):
        self._dir = art.ART_DIR
        art.ART_DIR = Path(tempfile.mkdtemp())
        (art.ART_DIR / "bench.svg").write_text(LINE_SVG, encoding="utf-8")
        (art.ART_DIR / "strip.svg").write_text(SEQ_SVG, encoding="utf-8")

    def tearDown(self):
        art.ART_DIR = self._dir

    def render(self, body: str, uid: str, name: str, lang="zh") -> str:
        unit = fixture_unit(uid, name, body, lang=lang)
        return render.render_unit(unit, self.mapping, diagrams={})["html"]

    def test_a_drawing_becomes_a_figure_numbered_with_the_diagrams(self):
        body = "## 3.2 工具注册\n\n@@ILL:aaaaaaaaaaaa@@\n"
        html = self.render(body, "aaaaaaaaaaaa", "bench")
        self.assertIn('<figure class="illu illu-line" id="fig-aaaaaaaaaaaa">',
                      html)
        self.assertIn("图 3-1", html)
        self.assertIn("3.2 工具注册", html)
        self.assertIn("<path", html)
        self.assertNotIn("@@ILL:", html)

    def test_a_sequential_drawing_announces_itself_and_offers_the_play(self):
        html = self.render("@@ILL:bbbbbbbbbbbb@@\n", "bbbbbbbbbbbb", "strip")
        self.assertIn('class="illu illu-seq"', html)
        self.assertIn("悬停播放", html)
        self.assertNotIn("悬停播放",
                         self.render("@@ILL:aaaaaaaaaaaa@@\n", "aaaaaaaaaaaa",
                                     "bench"))

    def test_the_english_plate_says_figure_and_hover(self):
        html = self.render("@@ILL:bbbbbbbbbbbb@@\n", "bbbbbbbbbbbb", "strip",
                           lang="en")
        self.assertIn("Figure 3-1", html)
        self.assertIn("hover to play", html)

    def test_a_slot_asking_for_a_missing_drawing_fails_the_build(self):
        with self.assertRaises(BuildError):
            self.render("@@ILL:cccccccccccc@@\n", "cccccccccccc", "nope")

    def test_a_placeholder_with_no_fence_behind_it_fails_the_build(self):
        unit = Unit(id="ch03", kind="chapter", lang="zh", no="第 3 章",
                    title="工具系统", md="@@ILL:dddddddddddd@@\n", ills=[])
        with self.assertRaises(BuildError):
            render.render_unit(unit, self.mapping, diagrams={})


class ShippedPlates(unittest.TestCase):
    """The real chapters, so a renamed file or a stray fence fails here first."""

    @classmethod
    def setUpClass(cls):
        cls.manifest, _sources = load_configs()
        cls.slots = {}
        for lang in ("zh", "en"):
            for unit_def, kind, _part in unit_stream(cls.manifest):
                u = load_unit(unit_def, kind, lang, REPO_ROOT)
                if u.ills:
                    cls.slots[(lang, u.id)] = u

    def test_every_slot_hangs_a_drawing_that_passes_the_loader(self):
        self.assertTrue(self.slots, "no chapter asks for a drawing")
        for (lang, uid), unit in self.slots.items():
            for block in unit.ills:
                with self.subTest(lang=lang, unit=uid, drawing=block.name):
                    self.assertTrue(art._read(block.name, art.PLATE_BYTES))

    def test_the_two_languages_ask_for_the_same_drawings_in_order(self):
        for uid in {u for _l, u in self.slots}:
            self.assertEqual([b.name for b in self.slots[("zh", uid)].ills],
                             [b.name for b in self.slots[("en", uid)].ills], uid)

    def test_the_tool_chapter_hangs_a_bench_and_a_filmstrip(self):
        names = [b.name for b in self.slots[("zh", "ch03")].ills]
        self.assertEqual(names, ["ch03-tool-bench", "ch03-tool-pipeline"])
        # the strip is the one plate that must animate: it is a sequence of
        # frames, and it says so on its own root rather than in the prose
        self.assertIn("seq", art.drawing("ch03-tool-pipeline").split(">", 1)[0])
        self.assertNotIn("seq", art.drawing("ch03-tool-bench").split(">", 1)[0])

    def test_an_unresolved_drawing_placeholder_is_an_error(self):
        from yuyu_book import audit
        article = ('<article class="chapter" id="ch03"><div class="compass">'
                   '<h4 class="cc-tag">问题</h4></div><h2 id="ch03-s">节</h2>'
                   '<p>@@ILL:0123456789ab@@</p></article>')
        with self.assertRaises(BuildError) as ctx:
            audit.audit(f"<html><body>{article}</body></html>",
                        n_units=1, expect_svgs=None)
        self.assertIn("unresolved drawing placeholders", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
