"""The two products in this repository must not be able to write each other's files.

`product` is a bookctl-level concept: `build.py` takes `--manifest/--sources` names and
reads `product`, `output_prefix`, `langs`, `subject_index_registry` out of the manifest.
That is the whole isolation mechanism, and every piece of it can rot silently. A shared
registry name would let an omp edit rewrite the book's glosses; a shared output prefix
would make the second build overwrite the first artifact; an inherited subject index
would let omp's build stamp page numbers into the book's `subject-index.json`.

These assertions are wired to the same functions the builder calls, so a rename that
would break isolation breaks a test first. The counts (20 / 39 units) are the ones
`docs/YUYU-OVERHAUL-SPEC.md` pins: 御舆's contract is 1 front + 15 chapters + 4
appendices, omp's is 1 front + 33 chapters + 5 appendices. The last class extends the
same reasoning to the drawing layer, because `illustrations-omp/` is searched by the
same loader as `illustrations/`.
"""
import sys
import unittest
from pathlib import Path
from typing import Any, cast

if not __package__:  # direct run: see tests/__init__.py for the real bootstrap
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from yuyu_book import art, plain, registry
from yuyu_book.core import expected_ids, load_configs

BOOK = "manifest.json"
OMP = "manifest-omp.json"
BOOK_UNITS = 20
OMP_UNITS = 39
BOOK_PREFIX = "yuyu-agent-harness"  # build.py's fallback when a manifest declares none


def _load(name: str) -> dict[str, Any]:
    return cast(dict[str, Any], registry.load(name))


class ProductIsolation(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.book = _load(BOOK)
        cls.omp = _load(OMP)

    def test_book_is_twenty_units(self):
        ids = expected_ids(self.book)
        self.assertEqual(len(ids), BOOK_UNITS)
        self.assertEqual(len(set(ids)), BOOK_UNITS, "duplicate unit id")

    def test_omp_is_thirty_nine_units(self):
        ids = expected_ids(self.omp)
        self.assertEqual(len(ids), OMP_UNITS)
        self.assertEqual(len(set(ids)), OMP_UNITS, "duplicate unit id")

    def test_plain_registries_are_disjoint(self):
        book_names = plain.registry_names(self.book)
        omp_names = plain.registry_names(self.omp)
        for key in ("glosses", "notes", "paths"):
            self.assertNotEqual(book_names[key], omp_names[key], key)
            self.assertIn(book_names[key], registry.FILES, key)
            self.assertIn(omp_names[key], registry.FILES, key)
            for name in (book_names[key], omp_names[key]):
                self.assertTrue((Path(registry.BOOK_DIR) / name).exists(),
                                f"{name} declared but not on disk")

    def test_default_loader_still_returns_the_book(self):
        """`build.py` with no `--manifest` is the book path. If a default ever started
        resolving to omp, every book-only test below would silently be about omp."""
        manifest, _ = load_configs()
        self.assertEqual(cast(dict[str, Any], manifest).get("product") or "book", "book")
        self.assertEqual(len(expected_ids(cast(dict[str, Any], manifest))), BOOK_UNITS)

    def test_omp_manifest_passes_the_same_validator(self):
        """Isolation must not be paid for with a weaker check: omp goes through
        `core.validate_configs()` too, including the guides-cover-every-unit rule."""
        manifest, _ = load_configs(OMP, "sources-omp.json")
        self.assertEqual(plain.manifest_langs(cast(dict[str, Any], manifest)), ("zh",))

    def test_output_artifacts_cannot_collide(self):
        book_prefix = self.book.get("output_prefix") or BOOK_PREFIX
        omp_prefix = self.omp.get("output_prefix")
        self.assertEqual(book_prefix, BOOK_PREFIX, "御舆's prefix is what README and CI quote")
        self.assertTrue(omp_prefix, "omp must declare its own prefix")
        self.assertNotEqual(book_prefix, omp_prefix)
        book_files = {f"{book_prefix}-{lang}.{kind}"
                      for lang in plain.manifest_langs(self.book) for kind in ("html", "pdf")}
        omp_files = {f"{omp_prefix}-{lang}.{kind}"
                     for lang in plain.manifest_langs(self.omp) for kind in ("html", "pdf")}
        self.assertEqual(book_files & omp_files, set())

    def test_omp_cannot_stamp_the_books_subject_index(self):
        """`build.py` reads `subject_index_registry` with a default of
        `subject-index.json`; omp declares the key as null, which is the only thing
        keeping its build from measuring and writing the book's index."""
        self.assertEqual(self.book.get("subject_index_registry", "subject-index.json"),
                         "subject-index.json")
        self.assertIn("subject_index_registry", self.omp,
                      "omp must declare the key explicitly, or the default reappears")
        self.assertIsNone(self.omp["subject_index_registry"])

    def test_omp_declares_no_english_edition(self):
        """omp's units carry only a `zh` path key, so asking it for English prose is a
        KeyError inside the builder, not a missing file. `langs` is the guard."""
        self.assertEqual(self.omp.get("langs"), ["zh"])
        self.assertNotIn("langs", self.book, "御舆 keeps the implicit both-language default")

    def test_no_other_test_loads_the_omp_manifest(self):
        """The book-only suites are the 20-unit contract's second line of defence. An
        omp manifest sneaking into one of them would widen or blur that number."""
        here = Path(__file__).name
        hits = sorted(p.name for p in Path(__file__).parent.glob("test_*.py")
                      if p.name not in (here, "test_pi_product.py")
                      and "manifest-omp" in p.read_text(encoding="utf-8"))
        self.assertEqual(hits, [], f"{hits} load omp's manifest from a book-only suite")


class OmpArtTray(unittest.TestCase):
    """omp's own drawings live in `illustrations-omp/`.

    `art.py` searches the volume's tray first and falls back to the shared one,
    which is what lets `keeper.svg` stay a single file for both books. That
    single pass is only safe while the two namespaces do not overlap, so the
    overlap itself is policed here rather than assumed.
    """

    @classmethod
    def setUpClass(cls):
        cls.omp = _load(OMP)
        cls.book = _load(BOOK)

    def test_every_omp_part_opens_with_its_own_drawing(self):
        want = [f'part-{p["id"]}' for p in self.omp["parts"]]
        self.assertEqual(art.missing(want), [],
                         f"omp part dividers with no drawing: {want}")

    def test_every_omp_unit_opens_with_its_own_emblem(self):
        """`build.py` only compares the emblems that reached the page against the
        ones the loader found, so an empty tray balances (0/0) and a whole layer can
        go missing without the build objecting. This is the absolute half of that."""
        ids = expected_ids(self.omp)
        self.assertEqual(len(ids), OMP_UNITS)
        self.assertEqual(art.missing(ids), [],
                         "omp units opening without a drawing")

    def test_every_shipped_omp_drawing_passes_the_loader(self):
        # budget, viewBox, currentColor and the no-id rule all live in `_read`
        for path in sorted(art.OMP_ART_DIR.glob("*.svg")):
            self.assertTrue(art._read(path.stem), path.name)

    def test_the_two_trays_declare_no_drawing_of_the_same_name(self):
        """A shared name would let the omp tray shadow the book's drawing, and
        the build guard counts would still balance."""
        shared = ({p.stem for p in art.ART_DIR.glob("*.svg")}
                  & {p.stem for p in art.OMP_ART_DIR.glob("*.svg")})
        self.assertEqual(shared, set(), f"{sorted(shared)} in both trays")

    def test_the_two_volumes_name_no_unit_or_part_alike(self):
        self.assertEqual(set(expected_ids(self.omp)) & set(expected_ids(self.book)),
                         set(), "a unit id shared by both volumes")
        self.assertEqual({p["id"] for p in self.omp["parts"]}
                         & {p["id"] for p in self.book["parts"]},
                         set(), "a part id shared by both volumes")


if __name__ == "__main__":
    unittest.main()
