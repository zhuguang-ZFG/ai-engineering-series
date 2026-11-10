"""Independent video rebuilds must compare files, not trust their manifests."""
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "video"))
from pipeline import proof


class RebuildBoundary(unittest.TestCase):
    def test_identical_manifests_cannot_hide_changed_caption_bytes(self):
        with tempfile.TemporaryDirectory() as directory:
            first, second = (Path(directory) / name for name in ("first", "second"))
            for target in (first, second):
                target.mkdir()
                (target / "manifest.json").write_text(json.dumps({"sha256": {"captions.html": "unchanged"}}), encoding="utf-8")
            (first / "captions.html").write_text("<p>请求并非执行完成</p>", encoding="utf-8")
            (second / "captions.html").write_text("<p>请求就是执行完成</p>", encoding="utf-8")
            result = proof.compare_outputs(first, second)
            self.assertEqual(result["status"], "different")
            self.assertEqual(result["changed"], ["captions.html"])

    def test_lost_transcript_is_not_a_successful_rebuild(self):
        with tempfile.TemporaryDirectory() as directory:
            first, second = (Path(directory) / name for name in ("first", "second"))
            first.mkdir()
            second.mkdir()
            for target in (first, second):
                (target / "timeline.json").write_text('{"end":20}', encoding="utf-8")
            (first / "transcript.json").write_text('{"text":"读取真实结果"}', encoding="utf-8")
            result = proof.compare_outputs(first, second)
            self.assertEqual(result["status"], "different")
            self.assertEqual(result["missing_second"], ["transcript.json"])


if __name__ == "__main__":
    unittest.main()
