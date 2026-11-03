"""Registry envelopes: one schema_version per JSON file, one migration path.

The builder must read version 0 files (the shape before this phase) without a
compatibility branch at every call site, and must refuse a file written by a
newer builder instead of guessing. These tests own that contract; the shipped
files are checked against the real book.
"""
import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from yuyu_book import registry  # noqa: E402
from yuyu_book.core import BOOK_DIR, BuildError  # noqa: E402


class ShippedRegistries(unittest.TestCase):
    def test_every_registry_declares_the_current_version(self):
        for name in registry.FILES:
            data = json.loads((BOOK_DIR / name).read_text(encoding="utf-8"))
            self.assertEqual(data.get("schema_version"), registry.CURRENT,
                             name)
            if name == registry.SUBJECT_INDEX:
                self.assertIsInstance(data.get("entries"), list, name)

    def test_load_strips_the_version_key(self):
        manifest = registry.load("manifest.json")
        self.assertNotIn("schema_version", manifest)
        self.assertTrue(manifest["parts"])

    def test_subject_index_loads_as_a_list(self):
        entries = registry.load("subject-index.json")
        self.assertIsInstance(entries, list)
        self.assertTrue(entries)
        self.assertIn("key", entries[0])


class Migration(unittest.TestCase):
    def test_missing_version_is_read_as_v0(self):
        self.assertEqual(
            registry.migrate("notes.json", {"front": "one line"}),
            {"front": "one line"})

    def test_legacy_subject_index_list_is_wrapped(self):
        entries = [{"key": "ablation"}]
        self.assertEqual(
            registry.migrate("subject-index.json", entries), entries)

    def test_newer_version_is_refused(self):
        with self.assertRaises(BuildError) as raised:
            registry.migrate(
                "manifest.json",
                {"schema_version": registry.CURRENT + 1, "parts": []})
        self.assertIn("newer", str(raised.exception))

    def test_subject_index_without_entries_is_refused(self):
        with self.assertRaises(BuildError):
            registry.migrate("subject-index.json",
                             {"schema_version": registry.CURRENT})

    def test_wrap_round_trips(self):
        payload = {"front": "one line"}
        wrapped = registry.wrap("notes.json", payload)
        self.assertEqual(wrapped["schema_version"], registry.CURRENT)
        self.assertEqual(registry.migrate("notes.json", wrapped), payload)

    def test_unknown_registry_is_refused(self):
        with self.assertRaises(BuildError):
            registry.load("nope.json")


if __name__ == "__main__":
    unittest.main()
