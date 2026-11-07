"""Source and asset drift must not silently ship a stale reviewed sample plate."""
import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'yuyu-book'))
from yuyu_book.core import BuildError
from yuyu_book.products import sample_diagrams


class ReviewedPlates(unittest.TestCase):
    def test_changed_source_cannot_reuse_a_reviewed_plate(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            svg = '<svg viewBox="0 0 1 1"/>'
            (root/'plate.svg').write_text(svg, encoding='utf-8')
            (root/'manifest.json').write_text(json.dumps({'diagrams':{'plate':{
                'source_sha256': hashlib.sha256(b'old source').hexdigest(),
                'svg_sha256': hashlib.sha256(svg.encode()).hexdigest()}}}), encoding='utf-8')
            with self.assertRaisesRegex(BuildError, 'source changed'):
                sample_diagrams.load([SimpleNamespace(uid='plate',src='new source')], {'plate':'caption'}, root)

    def test_tampered_reviewed_plate_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            block = SimpleNamespace(uid='plate',src='source')
            (root/'plate.svg').write_text('<svg>tampered</svg>', encoding='utf-8')
            (root/'manifest.json').write_text(json.dumps({'diagrams':{'plate':{
                'source_sha256':sample_diagrams.source_digest(block), 'svg_sha256':'0'*64}}}), encoding='utf-8')
            with self.assertRaisesRegex(BuildError, 'digest mismatch'):
                sample_diagrams.load([block], {'plate':'caption'}, root)
