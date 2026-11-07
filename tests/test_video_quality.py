"""Static quality gates and legacy evidence comparators for the video factory.

The fixtures are synthetic: they prove gate logic, not rendered media. Audio
tests either stop before ffmpeg or replace `audio_report`, so a machine without
ffmpeg can still run the suite. Keyframe tests patch the extractor for the same
reason; the missing-video path is exercised for real.
"""
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "video"))
from pipeline import model, quality, timeline


def episode(*, formats=None, captions=None, rules=None, rights=None,
            legacy=None):
    data = {
        "id": "ch06",
        "formats": formats if formats is not None else {
            "long": {"status": "scripted", "width": 1920, "height": 1080,
                     "fps": 30, "duration_s": 60.0},
            "short": {"status": "scripted", "width": 1080, "height": 1920,
                      "fps": 30, "duration_s": 20.0},
        },
        "captions": dict(model.DEFAULT_CAPTIONS, **(captions or {})),
        "quality": dict(model.DEFAULT_QUALITY, **(rules or {})),
        "rights": rights or {"owner": "original", "music": "none",
                             "footage": "none"},
    }
    if legacy is not None:
        data["legacy"] = legacy
    return data


def short_format(**overrides):
    spec = {"status": "scripted", "width": 1080, "height": 1920,
            "fps": 30, "duration_s": 20.0}
    spec.update(overrides)
    return {"short": spec}


class StaticCaptionGates(unittest.TestCase):
    def test_a_resolved_configuration_has_no_static_errors(self):
        manifests = {"long": {"segments": [{"text": "你好世界"}]}}
        cues = {"long": [{"start": 0.0, "end": 2.0, "text": "你好世界"}]}
        self.assertEqual(
            quality.check(episode(), {}, manifests, cues, Path(".")), [])

    def test_contrast_below_four_point_five_is_rejected(self):
        # #777777 on white is 4.47:1.
        errors = quality.check(
            episode(captions={"foreground": "#777777",
                              "background": "#ffffff"}),
            {}, {}, {}, Path("."))
        self.assertEqual(len(errors), 1, errors)
        self.assertIn("caption contrast", errors[0])
        self.assertIn("below 4.5:1", errors[0])

    def test_contrast_is_not_rounded_up_to_the_threshold(self):
        # #008769 on white is 4.4972:1; two-decimal rounding would hide it.
        self.assertLess(quality.contrast("#008769", "#ffffff"), 4.5)
        errors = quality.check(
            episode(captions={"foreground": "#008769",
                              "background": "#ffffff"}),
            {}, {}, {}, Path("."))
        self.assertEqual(len(errors), 1, errors)
        self.assertIn("below 4.5:1", errors[0])

    def test_caption_box_wider_than_the_safe_area_is_rejected(self):
        # 40 chars at 96 px on 1080 px width overflows the inner area.
        errors = quality.check(
            episode(captions={"max_chars": 40, "max_lines": 3,
                              "min_font_px": 96, "safe_pct": 8}),
            {}, {}, {}, Path("."))
        self.assertTrue(any("long caption box is wider" in item
                            for item in errors), errors)
        self.assertTrue(any("short caption box is wider" in item
                            for item in errors), errors)

    def test_caption_box_taller_than_the_safe_area_is_rejected(self):
        # 3 lines at 96 px (403 px) cannot fit a 400 px tall frame.
        errors = quality.check(
            episode(formats={"short": {"status": "scripted", "width": 1080,
                                       "height": 400, "fps": 30,
                                       "duration_s": 20.0}},
                    captions={"max_chars": 6, "max_lines": 3,
                              "min_font_px": 96, "safe_pct": 8}),
            {}, {}, {}, Path("."))
        self.assertEqual(len(errors), 1, errors)
        self.assertIn("short caption box is taller", errors[0])

    def test_a_cue_below_the_minimum_dwell_is_rejected(self):
        manifests = {"short": {"segments": [{"text": "你好世界"}]}}
        cues = {"short": [{"start": 0.0, "end": 1.0, "text": "你好世界"}]}
        errors = quality.check(episode(), {}, manifests, cues, Path("."))
        self.assertEqual(len(errors), 1, errors)
        self.assertIn("dwells less than 1.2s", errors[0])

    def test_a_cue_over_the_character_budget_is_rejected(self):
        text = "字" * 33  # default budget is 16 chars x 2 lines
        manifests = {"short": {"segments": [{"text": text}]}}
        cues = {"short": [{"start": 0.0, "end": 2.0, "text": text}]}
        errors = quality.check(episode(), {}, manifests, cues, Path("."))
        self.assertEqual(len(errors), 1, errors)
        self.assertIn("character budget", errors[0])

    def test_caption_text_must_match_the_narration(self):
        manifests = {"short": {"segments": [{"text": "你好世界"}]}}
        punctuation_only = {"short": [
            {"start": 0.0, "end": 2.0, "text": "你好，世界！"}]}
        self.assertEqual(quality.check(episode(), {}, manifests,
                                       punctuation_only, Path(".")), [])
        drifted = {"short": [{"start": 0.0, "end": 2.0, "text": "别的句子"}]}
        errors = quality.check(episode(), {}, manifests, drifted, Path("."))
        self.assertEqual(len(errors), 1, errors)
        self.assertIn("captions do not match the narration", errors[0])

    def test_declared_narration_without_captions_is_a_mismatch(self):
        manifests = {"short": {"segments": [{"text": "你好世界"}]}}
        errors = quality.check(episode(), {}, manifests, {"short": []},
                               Path("."))
        self.assertEqual(len(errors), 1, errors)
        self.assertIn("captions do not match the narration", errors[0])

    def test_captions_past_the_format_duration_are_rejected(self):
        # The out-of-order track hides the overflow from a last-cue check.
        manifests = {"short": {"segments": [{"text": "甲乙"},
                                            {"text": "丙丁"}]}}
        cues = {"short": [{"start": 19.0, "end": 22.0, "text": "甲乙"},
                          {"start": 0.0, "end": 2.0, "text": "丙丁"}]}
        errors = quality.check(episode(), {}, manifests, cues, Path("."))
        self.assertEqual(len(errors), 1, errors)
        self.assertIn("captions run past the format duration", errors[0])

    def test_flashes_outside_the_format_are_rejected(self):
        scenes = {"flashes": {"short": [{"at_s": -1.0}, {"at_s": 25.0}]}}
        errors = quality.check(episode(), scenes, {}, {}, Path("."))
        self.assertEqual(len(errors), 2, errors)
        self.assertTrue(all("is outside the format" in item
                            for item in errors), errors)

    def test_flash_rate_limit(self):
        dense = {"flashes": {"short": [{"at_s": at}
                                       for at in (0.0, 0.2, 0.4, 0.6)]}}
        errors = quality.check(episode(), dense, {}, {}, Path("."))
        self.assertEqual(len(errors), 1, errors)
        self.assertIn("flashes more than 3 times per second", errors[0])
        spread = {"flashes": {"short": [{"at_s": at}
                                        for at in (0.0, 0.6, 1.2, 1.8)]}}
        self.assertEqual(quality.check(episode(), spread, {}, {}, Path(".")),
                         [])

    def test_unresolved_rights_are_rejected(self):
        errors = quality.check(
            episode(rights={"owner": "original", "music": "TBD",
                            "footage": "Unlicensed"}),
            {}, {}, {}, Path("."))
        self.assertEqual(len(errors), 2, errors)
        self.assertIn("rights.music is not resolved", errors[0])
        self.assertIn("rights.footage is not resolved", errors[1])


class AudioGates(unittest.TestCase):
    def test_declared_recording_must_exist(self):
        with tempfile.TemporaryDirectory() as directory:
            chapter = Path(directory) / "ch06"
            (chapter / "legacy").mkdir(parents=True)
            scenes = {"audio": {"short": {"path": "voice.mp3",
                                          "duration_s": 20.0}}}
            errors = quality.check(
                episode(formats=short_format(), legacy={"dir": "legacy"}),
                scenes, {}, {}, chapter, check_audio=True)
        self.assertEqual(len(errors), 1, errors)
        self.assertIn("voice.mp3 is missing", errors[0])

    def test_audio_report_metrics_are_gated(self):
        with tempfile.TemporaryDirectory() as directory:
            chapter = Path(directory) / "ch06"
            (chapter / "legacy").mkdir(parents=True)
            (chapter / "legacy" / "voice.mp3").write_bytes(b"")
            scenes = {"audio": {"short": {"path": "voice.mp3",
                                          "duration_s": 20.0}}}
            report = {"duration_s": 22.0, "loudness_lufs": -10.0,
                      "peak_dbfs": 0.5, "silences": [],
                      "leading_silence_s": 0.0, "trailing_silence_s": 0.1,
                      "inside_silence_s": 3.0}
            with mock.patch.object(quality, "audio_report",
                                   return_value=report):
                errors = quality.check(
                    episode(formats=short_format(),
                            legacy={"dir": "legacy"}),
                    scenes, {}, {}, chapter, check_audio=True)
        self.assertEqual(len(errors), 5, errors)
        self.assertIn("audio is 22.0s, configured 20.0s", errors[0])
        self.assertIn("peak 0.5 dBFS", errors[1])
        self.assertIn("loudness -10.0 LUFS", errors[2])
        self.assertIn("3.0s silence", errors[3])
        self.assertIn("leaves only 0.1s", errors[4])


class LegacyCaptionComparison(unittest.TestCase):
    def _chapter(self, directory):
        chapter = Path(directory) / "ch06"
        (chapter / "legacy").mkdir(parents=True)
        return chapter

    def test_missing_legacy_captions_are_explicitly_unverified(self):
        with tempfile.TemporaryDirectory() as directory:
            chapter = self._chapter(directory)
            result = timeline.caption_report(
                episode(legacy={"dir": "legacy"}), chapter,
                {"long": [{"start": 0.0, "end": 2.0, "text": "你好世界"}]},
                "long")
        self.assertEqual(result["status"], "unverified")
        self.assertIn("no legacy SRT/VTT captions", result["reason"])
        self.assertNotIn("captions", result)

    def test_srt_captions_match_with_normalized_text_and_tolerance(self):
        srt = (
            "1\n"
            "00:00:00,100 --> 00:00:02,000\n"
            "你好，世界\n"
            "\n"
            "2\n"
            "00:00:02,000 --> 00:00:04,300\n"
            "第二句。\n")
        with tempfile.TemporaryDirectory() as directory:
            chapter = self._chapter(directory)
            (chapter / "legacy" / "captions.srt").write_text(
                srt, encoding="utf-8")
            result = timeline.caption_report(
                episode(legacy={"dir": "legacy"}), chapter,
                {"long": [{"start": 0.0, "end": 2.1, "text": "你好世界"},
                          {"start": 2.0, "end": 4.2, "text": "第二句"}]},
                "long")
        self.assertEqual(result["status"], "match", result)
        self.assertEqual(result["mismatches"], [])
        self.assertEqual(result["captions"], "legacy/captions.srt")

    def test_vtt_caption_text_and_timing_drift_is_reported(self):
        vtt = (
            "WEBVTT\n"
            "\n"
            "00:00:00.000 --> 00:00:02.000\n"
            "第一句\n")
        with tempfile.TemporaryDirectory() as directory:
            chapter = self._chapter(directory)
            (chapter / "legacy" / "captions.vtt").write_text(
                vtt, encoding="utf-8")
            result = timeline.caption_report(
                episode(legacy={"dir": "legacy"}), chapter,
                {"long": [{"start": 0.5, "end": 2.5, "text": "另外一句"}]},
                "long")
        self.assertEqual(result["status"], "mismatch", result)
        self.assertIn("caption text differs", result["mismatches"])
        self.assertIn("cue 0: start 0.0 != 0.5", result["mismatches"])
        self.assertIn("cue 0: end 2.0 != 2.5", result["mismatches"])

    def test_compat_report_does_not_store_unverified_captions(self):
        index = (
            '<div id="root" data-duration="20" data-width="1080" '
            'data-height="1920" data-fps="30">'
            '<div class="clip" data-composition-id="hook" '
            'data-composition-src="hook.html" data-start="0" '
            'data-duration="20" data-track-index="1"></div></div>')
        spec = {"short": {"status": "built", "width": 1080, "height": 1920,
                          "fps": 30, "duration_s": 20.0}}
        scenes = {"formats": {"short": [
            {"id": "hook", "start_s": 0.0, "duration_s": 20.0,
             "source": "hook.html"}]}}
        with tempfile.TemporaryDirectory() as directory:
            chapter = self._chapter(directory)
            (chapter / "legacy" / "index.html").write_text(
                index, encoding="utf-8")
            data = episode(formats=spec,
                           legacy={"dir": "legacy",
                                   "short_index": "index.html"})
            report = timeline.compat(data, chapter, scenes)
        entry = report["formats"]["short"]
        self.assertTrue(entry["match"], entry)
        self.assertEqual(set(entry), {"index", "match", "mismatches"})


class KeyframeComparison(unittest.TestCase):
    def test_missing_videos_are_explicitly_unverified(self):
        with tempfile.TemporaryDirectory() as directory:
            old = Path(directory) / "old.mp4"
            new = Path(directory) / "new.mp4"
            result = timeline.keyframe_report(old, new)
        self.assertEqual(result["status"], "unverified")
        self.assertIn("old.mp4", result["reason"])
        self.assertIn("new.mp4", result["reason"])
        self.assertNotIn("frames", result)

    def test_identical_frame_hashes_are_reported(self):
        with tempfile.TemporaryDirectory() as directory:
            old = Path(directory) / "old.mp4"
            new = Path(directory) / "new.mp4"
            old.write_bytes(b"")
            new.write_bytes(b"")
            with mock.patch.object(timeline, "_probe_duration",
                                   return_value=10.0), \
                    mock.patch.object(timeline, "_frame_sha",
                                      return_value="a" * 64):
                result = timeline.keyframe_report(old, new)
        self.assertEqual(result["status"], "identical", result)
        self.assertEqual(len(result["frames"]), 3)
        self.assertTrue(all(frame["match"] for frame in result["frames"]))

    def test_different_frame_hashes_are_reported(self):
        with tempfile.TemporaryDirectory() as directory:
            old = Path(directory) / "old.mp4"
            new = Path(directory) / "new.mp4"
            old.write_bytes(b"")
            new.write_bytes(b"")
            with mock.patch.object(timeline, "_probe_duration",
                                   return_value=10.0), \
                    mock.patch.object(timeline, "_frame_sha",
                                      side_effect=lambda path, at:
                                      f"{path.name}:{at}"):
                result = timeline.keyframe_report(old, new)
        self.assertEqual(result["status"], "different", result)
        self.assertFalse(any(frame["match"] for frame in result["frames"]))
        self.assertNotEqual(result["frames"][0]["old_sha256"],
                            result["frames"][0]["new_sha256"])

    def test_unreadable_duration_is_unverified(self):
        with tempfile.TemporaryDirectory() as directory:
            old = Path(directory) / "old.mp4"
            new = Path(directory) / "new.mp4"
            old.write_bytes(b"")
            new.write_bytes(b"")
            with mock.patch.object(timeline, "_probe_duration",
                                   return_value=None):
                result = timeline.keyframe_report(old, new)
        self.assertEqual(result["status"], "unverified")
        self.assertIn("ffprobe", result["reason"])


if __name__ == "__main__":
    unittest.main()
