"""The media review command must not turn missing evidence into a pass."""
import contextlib
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "video"))
from pipeline import cli, timeline


class MediaComparisonCLI(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.directory = Path(temporary.name)
        self.legacy = self.directory / "legacy.srt"
        self.legacy.write_text("1\n00:00:00,000 --> 00:00:02,000\n你好世界\n",
                               encoding="utf-8")
        self.current = self.directory / "transcript-long.json"
        self.document = {"schema_version": 1, "chapter": "ch01", "format": "long",
                         "segments": [{"start": 0., "end": 2., "text": "你好世界"}]}
        self.report = self.directory / "comparison.json"

    def compare(self, *extra):
        self.current.write_text(json.dumps(self.document), encoding="utf-8")
        output = io.StringIO()
        with contextlib.redirect_stdout(output), contextlib.redirect_stderr(output):
            code = cli.main(["compare", "--chapter", "ch01", "--format", "long",
                             "--legacy-captions", str(self.legacy),
                             "--current-captions", str(self.current),
                             "--report", str(self.report), *extra])
        return code, output.getvalue()

    def test_matching_captions_without_rendered_videos_stay_unverified(self):
        code, output = self.compare()
        self.assertEqual(code, 1, output)
        report = json.loads(self.report.read_text(encoding="utf-8"))
        self.assertEqual(report["status"], "unverified")
        self.assertEqual(report["captions"]["status"], "match")
        self.assertEqual(report["keyframes"]["status"], "unverified")
        self.assertRegex(report["inputs"]["current_captions"]["sha256"], r"^[a-f0-9]{64}$")

    def test_caption_mismatch_is_reported_even_when_video_is_missing(self):
        self.document["segments"][0]["text"] = "另外一句"
        code, output = self.compare()
        self.assertEqual(code, 1, output)
        report = json.loads(self.report.read_text(encoding="utf-8"))
        self.assertEqual(report["status"], "mismatch")
        self.assertIn("cue 0: text differs", report["captions"]["mismatches"])

    def test_a_transcript_from_another_chapter_is_refused(self):
        self.document["chapter"] = "ch02"
        code, output = self.compare()
        self.assertEqual(code, 1, output)
        self.assertIn("chapter", output)
        self.assertFalse(self.report.exists())

    def test_nonfinite_cue_time_is_refused(self):
        self.document["segments"][0]["start"] = float("nan")
        code, output = self.compare()
        self.assertEqual(code, 1, output)
        self.assertIn("cue 0", output)
        self.assertFalse(self.report.exists())

    def test_report_cannot_overwrite_caption_evidence(self):
        self.report = self.legacy
        before = self.legacy.read_bytes()
        code, output = self.compare()
        self.assertEqual(code, 1, output)
        self.assertIn("overwrite", output)
        self.assertEqual(self.legacy.read_bytes(), before)

    def test_complete_matching_evidence_passes_and_records_both_inputs(self):
        old, new = self.directory / "old.mp4", self.directory / "new.mp4"
        old.write_bytes(b"legacy render")
        new.write_bytes(b"current render")
        with mock.patch.object(timeline, "_probe_duration", return_value=1148.352), \
                mock.patch.object(timeline, "_frame_sha", return_value="a" * 64):
            code, output = self.compare("--legacy-video", str(old),
                                        "--current-video", str(new))
        self.assertEqual(code, 0, output)
        report = json.loads(self.report.read_text(encoding="utf-8"))
        self.assertEqual(report["status"], "match")
        self.assertTrue(report["duration_matches_episode"])
        self.assertNotEqual(report["inputs"]["legacy_video"]["sha256"],
                            report["inputs"]["current_video"]["sha256"])

    def test_identical_videos_with_the_wrong_episode_duration_fail(self):
        old, new = self.directory / "old.mp4", self.directory / "new.mp4"
        old.touch()
        new.touch()
        with mock.patch.object(timeline, "_probe_duration", return_value=10.), \
                mock.patch.object(timeline, "_frame_sha", return_value="a" * 64):
            code, output = self.compare("--legacy-video", str(old),
                                        "--current-video", str(new))
        self.assertEqual(code, 1, output)
        report = json.loads(self.report.read_text(encoding="utf-8"))
        self.assertEqual(report["status"], "mismatch")
        self.assertFalse(report["duration_matches_episode"])

    def test_missing_legacy_caption_file_stays_unverified(self):
        self.legacy.unlink()
        code, output = self.compare()
        self.assertEqual(code, 1, output)
        report = json.loads(self.report.read_text(encoding="utf-8"))
        self.assertEqual(report["captions"]["status"], "unverified")
        self.assertIsNone(report["inputs"]["legacy_captions"]["sha256"])


if __name__ == "__main__":
    unittest.main()
