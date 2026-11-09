"""The third volume's own manifest, prefix and drawing tray.

Kept apart from `test_product_isolation.py` so the two-volume contract file
stays exactly as its authors left it; this module only asserts the pi
product's own edges.
"""
import sys
import unittest
from pathlib import Path
from typing import Any, cast

if not __package__:  # direct run: see tests/__init__.py for the real bootstrap
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from yuyu_book import art, registry
from yuyu_book.core import expected_ids, load_configs

PI = "manifest-pi.json"
PI_UNITS = 31


def load(name: str) -> dict[str, Any]:
    return cast(dict[str, Any], registry.load(name))


class PiProduct(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pi = load(PI)
        cls.book = load("manifest.json")
        cls.omp = load("manifest-omp.json")

    def test_pi_is_thirty_one_units(self):
        ids = expected_ids(self.pi)
        self.assertEqual(len(ids), PI_UNITS)
        self.assertEqual(len(set(ids)), PI_UNITS, "duplicate unit id")

    def test_pi_manifest_passes_the_same_validator(self):
        manifest, _ = load_configs(PI, "sources-pi.json")
        self.assertEqual(cast(dict[str, Any], manifest).get("product"), "pi")

    def test_pi_prefix_is_its_own(self):
        prefixes = {self.book.get("output_prefix"),
                    self.omp.get("output_prefix"),
                    self.pi.get("output_prefix")}
        self.assertEqual(len(prefixes), 3)
        self.assertEqual(self.pi.get("output_prefix"), "yuyu-pi")

    def test_pi_is_zh_only(self):
        self.assertEqual(self.pi.get("langs"), ["zh"])


class PiArtTray(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pi = load(PI)

    def test_every_pi_unit_opens_with_its_own_emblem(self):
        self.assertEqual(art.missing(expected_ids(self.pi)), [])

    def test_every_pi_part_opens_with_its_own_plate(self):
        want = [f'part-{p["id"]}' for p in self.pi["parts"]]
        self.assertEqual(art.missing(want), [])

    def test_every_shipped_pi_drawing_passes_the_loader(self):
        for path in sorted(art.PI_ART_DIR.glob("*.svg")):
            self.assertTrue(art._read(path.stem), path.name)

    def test_body_plates_are_drawn_as_well(self):
        self.assertGreaterEqual(len(list(art.PI_ART_DIR.glob("pi-plate-*.svg"))), 11)
