"""Published entry points are aliases, and every local link must resolve."""
from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import check_site_redirects  # noqa: E402


class SiteEntryPoints(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="site-check-")
        self.addCleanup(temporary.cleanup)
        self.site = Path(temporary.name)
        portal = ('<a href="beginner-reader.html">read</a>'
                  '<a href="https://example.com/x">outside</a>')
        for name in check_site_redirects.REQUIRED:
            (self.site / name).write_text(
                f'<main id="{name}">{portal}</main>', encoding="utf-8")
        for alias, target in check_site_redirects.ALIASES.items():
            (self.site / alias).write_bytes((self.site / target).read_bytes())

    def test_complete_alias_site_passes(self):
        self.assertEqual(check_site_redirects.check(self.site), [])

    def test_alias_must_keep_identical_bytes(self):
        (self.site / "book.html").write_text("<h1>stale</h1>", encoding="utf-8")
        failures = check_site_redirects.check(self.site)
        self.assertTrue(any("book.html" in item and "differs" in item
                            for item in failures), failures)

    def test_missing_target_is_named(self):
        page = self.site / "beginner-reader.html"
        page.write_text('<a href="missing.html">gone</a>', encoding="utf-8")
        failures = check_site_redirects.check(self.site)
        self.assertTrue(any("missing.html" in item for item in failures),
                        failures)

    def test_missing_fragment_is_named(self):
        page = self.site / "beginner-reader.html"
        page.write_text('<a href="portal.html#nope">bad anchor</a>',
                        encoding="utf-8")
        failures = check_site_redirects.check(self.site)
        self.assertTrue(any("nope" in item for item in failures), failures)

    def test_path_escaping_the_site_is_rejected(self):
        page = self.site / "beginner-reader.html"
        page.write_text('<img src="../secret.png">', encoding="utf-8")
        failures = check_site_redirects.check(self.site)
        self.assertTrue(any("escapes site" in item for item in failures),
                        failures)

    def test_missing_entry_point_is_named(self):
        (self.site / "portal.html").unlink()
        failures = check_site_redirects.check(self.site)
        self.assertTrue(any("portal.html" in item for item in failures),
                        failures)


if __name__ == "__main__":
    unittest.main()
