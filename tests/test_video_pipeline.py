"""Consumer boundaries for the shared chapter video factory."""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "video"))
from pipeline import model, timeline


class ConfigurationBoundary(unittest.TestCase):
    def test_missing_media_is_explicitly_separate_from_config_validation(self):
        with tempfile.TemporaryDirectory() as directory:
            chapter = Path(directory) / "ch01"
            chapter.mkdir()
            episode = {"formats": {"short": {"status": "built", "duration_s": 20}}}
            scenes = {"schema_version": 1, "episode": "ch01", "formats": {
                "short": [{"id": "opening", "start_s": 0, "duration_s": 20,
                           "source": "missing.html", "intent": "hook"}]},
                "audio": {"short": {"path": "missing.mp3", "duration_s": 20}}}
            episode["legacy"] = {"dir": ".", "short_index": "index.html"}
            self.assertEqual(model.validate_scenes(
                scenes, episode, chapter, check_assets=False), [])
            errors = model.validate_scenes(scenes, episode, chapter)
            self.assertTrue(any("composition missing.html is missing" in item
                                for item in errors), errors)
            self.assertTrue(any("audio missing.mp3 is missing" in item
                                for item in errors), errors)

    def test_scripted_timeline_contains_scenes_and_render_state(self):
        episode = {"id": "ch06", "formats": {"short": {
            "status": "scripted", "width": 1080, "height": 1920,
            "fps": 30, "duration_s": 20}}}
        scene = {"id": "hook", "start_s": 0, "duration_s": 20,
                 "source": "compositions/hook.html", "intent": "hook"}
        result = timeline.build(episode, {"formats": {"short": [scene]}}, {})
        self.assertEqual(result["formats"]["short"]["scenes"], [scene])
        self.assertEqual(result["formats"]["short"]["status"], "scripted")

    def test_asset_failure_is_a_named_cli_error_not_traceback(self):
        result = subprocess.run(
            [sys.executable, "video/pipeline/cli.py", "check", "--chapter", "ch01"],
            cwd=ROOT, capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(result.returncode, 1)
        self.assertIn("VIDEO FAILED:", result.stderr)
        self.assertNotIn("Traceback", result.stderr)


if __name__ == "__main__":
    unittest.main()
