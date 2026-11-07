"""The source-rendered sample stays complete, offline and current.

Freshness is checked on every run; no dist directory or skipped build check
can conceal stale sample prose.
"""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "yuyu-book"))
from yuyu_book.labels import esc  # noqa: E402
from yuyu_book.products import sample  # noqa: E402
from yuyu_book.products.chapter_copy import hook, recap  # noqa: E402
from yuyu_book.products.loader import load_repo_model  # noqa: E402

OUT = {lang: ROOT / "docs" / name for lang, name in sample.OUT.items()}


class Sampler(unittest.TestCase):
    def test_the_page_holds_one_complete_chapter(self):
        for lang, out in OUT.items():
            page = out.read_text(encoding="utf-8")
            self.assertEqual(page.count('<article class="chapter"'), 1, out)
            self.assertIn(f'<article class="chapter" id="{sample.CHAPTER}">',
                          page, out)
            self.assertIn(f'<body class="lang-{lang} sample">', page, out)

    def test_cross_chapter_jumps_point_at_the_full_edition(self):
        for lang, out in OUT.items():
            page = out.read_text(encoding="utf-8")
            self.assertNotIn('href="#ch', page, out)
            self.assertNotIn('href="#source-', page, out)
            self.assertIn(f'href="{sample.BOOK[lang]}#{sample.CHAPTER}"', page,
                          out)

    def test_the_frame_quotes_the_models_hook_and_recap(self):
        for lang, out in OUT.items():
            model = load_repo_model([lang])
            unit = model.unit(lang, sample.CHAPTER)
            page = out.read_text(encoding="utf-8")
            self.assertIn(esc(hook(unit, lang)), page, out)
            for item in recap(unit, lang):
                self.assertIn(f"<li>{esc(item)}</li>", page, out)

    def test_the_sample_stays_offline_and_scriptless(self):
        for lang, out in OUT.items():
            page = out.read_text(encoding="utf-8")
            self.assertNotIn("<script", page, out)
            self.assertNotIn('src="http', page, out)
            self.assertNotIn("<img", page, out)
            self.assertIn("@media print", page, out)

    def test_the_sample_is_current_without_a_built_edition(self):
        """The shared source pipeline, not dist HTML, supplies the excerpt."""
        for lang, out in OUT.items():
            model = load_repo_model([lang])
            fresh = sample.page_for(model, lang)
            self.assertEqual(fresh, out.read_text(encoding="utf-8"),
                             f"{out}: regenerate the source-rendered sample")


if __name__ == "__main__":
    unittest.main()
