"""The four Agent volumes must build complete books without sharing metadata.

These are source-only checks against the same loaders used by publication.
Browser/PDF/EPUB rendering is exercised separately by the per-volume CI jobs.
"""
from __future__ import annotations

import json
import re
import sys
import unittest
from pathlib import Path

if not __package__:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from yuyu_book import plain, registry
from yuyu_book.core import REPO_ROOT, expected_ids, load_configs, load_unit, unit_stream


PRODUCTS = ("opencode", "deepseek", "hermes", "codex")


class AgentProducts(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.books = {}
        cls.sources = {}
        for product in PRODUCTS:
            cls.books[product], cls.sources[product] = load_configs(
                f"manifest-{product}.json", f"sources-{product}.json")
        source_lock = json.loads(
            (REPO_ROOT / "docs/agent-series/sources.lock.json").read_text(encoding="utf-8"))
        cls.baselines = {entry["id"]: entry for entry in source_lock["repositories"]}

    def test_each_volume_has_its_foreword_eighteen_chapters_and_four_appendices(self):
        for product, manifest in self.books.items():
            with self.subTest(product=product):
                want = ([f"{product}-front"]
                        + [f"{product}-ch{i:02d}" for i in range(1, 19)]
                        + [f"{product}-apx{letter}" for letter in "abcd"])
                self.assertEqual(expected_ids(manifest), want)
                self.assertEqual(len(set(want)), 23)
                self.assertEqual(manifest["product"], product)
                self.assertEqual(plain.manifest_langs(manifest), ("zh",))

    def test_each_registered_unit_is_a_parsable_manuscript_in_its_own_directory(self):
        for product, manifest in self.books.items():
            registered = set()
            for definition, kind, _part in unit_stream(manifest):
                with self.subTest(product=product, unit=definition["id"]):
                    relative = Path(definition["zh"])
                    self.assertEqual(relative.parts[0], product)
                    path = (REPO_ROOT / relative).resolve()
                    self.assertTrue(path.is_relative_to((REPO_ROOT / product).resolve()))
                    self.assertNotIn(path, registered, "two units read the same manuscript")
                    registered.add(path)
                    unit = load_unit(definition, kind, "zh", REPO_ROOT)
                    self.assertEqual(unit.id, definition["id"])
                    self.assertTrue(unit.title)
                    self.assertTrue(unit.md.strip())
                    if kind == "chapter":
                        self.assertEqual(unit.no_plain, definition["id"].rsplit("ch", 1)[1])
                    elif kind == "appendix":
                        self.assertEqual(unit.no_plain, definition["id"][-1].upper())

    def test_no_chapter_on_disk_is_omitted_from_the_book(self):
        for product, manifest in self.books.items():
            with self.subTest(product=product):
                registered = {(REPO_ROOT / definition["zh"]).resolve()
                              for definition, _kind, _part in unit_stream(manifest)}
                folder = REPO_ROOT / product
                manuscripts = {path.resolve() for pattern in
                               ("00-*.md", "ch[0-9][0-9].md", "appendix-*.md")
                               for path in folder.glob(pattern)}
                self.assertEqual(registered, manuscripts)

    def test_artifact_names_are_unique_across_registered_books(self):
        owners = {}
        for name in registry.FILES:
            if name != "manifest.json" and not name.startswith("manifest-"):
                continue
            manifest = registry.load(name)
            prefix = manifest.get("output_prefix") or "yuyu-agent-harness"
            for lang in plain.manifest_langs(manifest):
                for extension in ("html", "pdf", "epub"):
                    artifact = f"{prefix}-{lang}.{extension}"
                    self.assertNotIn(artifact, owners,
                                     f"{name} overwrites {owners.get(artifact)}")
                    owners[artifact] = name
        for product, manifest in self.books.items():
            self.assertEqual(manifest["output_prefix"], f"yuyu-{product}")

    def test_plain_revisions_and_indexes_use_separate_registered_files(self):
        claimed = set()
        for product, manifest in self.books.items():
            names = plain.registry_names(manifest)
            names.update({"sources": f"sources-{product}.json",
                          "revisions": manifest["revisions_registry"],
                          "index": manifest["subject_index_registry"]})
            for role, name in names.items():
                with self.subTest(product=product, role=role):
                    self.assertTrue(name.endswith(f"-{product}.json"), name)
                    self.assertNotIn(name, claimed, "metadata shared across volumes")
                    claimed.add(name)
                    self.assertIn(name, registry.FILES)
                    registry.load(name)

    def test_reading_paths_cover_real_headings_and_leads_have_prose_evidence(self):
        for product, manifest in self.books.items():
            with self.subTest(product=product):
                glosses, paths = plain.load_plain(manifest)
                self.assertFalse(manifest.get("plain_optional"))
                plain.validate_plain(glosses, paths, manifest)
                chapters = {definition["id"] for definition, kind, _part
                            in unit_stream(manifest) if kind == "chapter"}
                self.assertTrue(chapters.issubset(paths))
                for definition, kind, _part in unit_stream(manifest):
                    if kind != "chapter":
                        continue
                    prose = plain.prose_lines(
                        (REPO_ROOT / definition["zh"]).read_text(encoding="utf-8"))
                    headings = sum(bool(re.match(r"^##\s+\S", line)) for line in prose.values())
                    self.assertEqual(len(paths[definition["id"]]), headings, definition["id"])

    def test_source_baselines_match_the_shared_full_commit_lock(self):
        for product, sources in self.sources.items():
            baseline = self.baselines[product]
            with self.subTest(product=product):
                self.assertRegex(baseline["commit"], r"^[0-9a-f]{40}$")
                matching = [source for source in sources.values()
                            if source["kind"] == "github"
                            and source["url"].startswith("https://github.com/" + baseline["repo"])]
                self.assertTrue(matching, "the volume has no registered upstream source")
                for source in matching:
                    self.assertEqual(source["pinned"]["commit"], baseline["commit"])
                    self.assertEqual(source["license"], baseline["license"])
                for source in sources.values():
                    if source["kind"] == "github":
                        self.assertRegex(source["pinned"].get("commit", ""), r"^[0-9a-f]{40}$")

    def test_index_references_and_guide_sources_stay_in_their_own_book(self):
        for product, manifest in self.books.items():
            ids = set(expected_ids(manifest))
            with self.subTest(product=product):
                index = registry.load(manifest["subject_index_registry"])
                self.assertTrue(index)
                for entry in index:
                    for lang in plain.manifest_langs(manifest):
                        self.assertTrue(entry[lang]["refs"], entry["key"])
                        for reference in entry[lang]["refs"]:
                            self.assertIn(reference["anchor"], ids, entry["key"])
                for uid, guide in manifest["guides"].items():
                    self.assertIn(uid, ids)
                    self.assertTrue(guide.get("sources"), uid)
                    self.assertTrue(set(guide["sources"]).issubset(self.sources[product]), uid)


if __name__ == "__main__":
    unittest.main()
