"""Consumer boundaries for the shared chapter video factory."""
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "video"))
from pipeline import model, quality, timeline


class TrackedVideoInventory(unittest.TestCase):
    def test_only_authored_sources_and_pipeline_code_are_tracked(self):
        result = subprocess.run(["git", "ls-files", "video"], cwd=ROOT,
                                capture_output=True, text=True, encoding="utf-8")
        if result.returncode:
            self.skipTest("git metadata is unavailable")
        tracked = [line for line in result.stdout.splitlines() if line]
        media = {".mp3", ".mp4", ".mov", ".webm", ".wav", ".m4a", ".aac",
                 ".png", ".jpg", ".jpeg", ".webp"}
        generated_names = ("vo-concat.txt", "short-meta.json", "chunks.json",
                           "vo-manifest", "transcript", "captions-")
        problems = []
        for path in tracked:
            suffix = Path(path).suffix.lower()
            name = Path(path).name
            if suffix in media:
                problems.append(f"media: {path}")
            elif suffix in {".srt", ".vtt"}:
                problems.append(f"captions: {path}")
            elif suffix == ".py" and not path.startswith("video/pipeline/"):
                problems.append(f"legacy script: {path}")
            elif name in generated_names or any(
                    name.startswith(prefix) for prefix in generated_names):
                problems.append(f"generated: {path}")
            elif "/assets/" in path and path.split("/assets/", 1)[0].split(
                    "/")[-1] in {"ch01", "ch02", "ch03", "ch04", "ch05"}:
                allowed = {
                    "video/ch01/assets/huashu/ch01-whiteboard.json",
                    "video/ch01/assets/sample-long.txt",
                    "video/ch01/assets/sample-short.txt",
                    "video/ch02/assets/sample-short.txt",
                    "video/ch03/assets/sample-short.txt",
                    "video/ch04/assets/sample-short.txt",
                    "video/ch05/assets/sample-short.txt",
                }
                if path not in allowed:
                    problems.append(f"intermediate: {path}")
        self.assertEqual(problems, [])


class ConfigurationBoundary(unittest.TestCase):
    def test_audio_gate_rejects_a_configuration_without_recordings(self):
        episode = {"id": "ch06", "formats": {
            name: {"status": "scripted", "width": width, "height": height,
                   "duration_s": 20}
            for name, (width, height) in model.FORMAT_SIZE.items()},
            "captions": dict(model.DEFAULT_CAPTIONS),
            "quality": dict(model.DEFAULT_QUALITY),
            "rights": {"owner": "original", "music": "none", "footage": "none"}}
        with tempfile.TemporaryDirectory() as directory:
            chapter = Path(directory) / "ch06"
            chapter.mkdir()
            self.assertEqual(quality.check(episode, {}, {}, {}, chapter), [])
            errors = quality.check(episode, {}, {}, {}, chapter, check_audio=True)
        self.assertEqual(errors, [
            "ch06: long narration is not declared; audio verification requires a real recording",
            "ch06: short narration is not declared; audio verification requires a real recording"])

    def test_audio_gate_rejects_an_unresolvable_recording_base(self):
        episode = {"id": "ch06", "formats": {"short": {
            "status": "scripted", "width": 1080, "height": 1920, "duration_s": 20}},
            "captions": dict(model.DEFAULT_CAPTIONS),
            "quality": dict(model.DEFAULT_QUALITY),
            "rights": {"owner": "original", "music": "none", "footage": "none"}}
        with tempfile.TemporaryDirectory() as directory:
            chapter = Path(directory) / "ch06"
            chapter.mkdir()
            errors = quality.check(episode, {"audio": {"short": {
                "path": "voice.mp3", "duration_s": 20}}}, {}, {}, chapter,
                check_audio=True)
        self.assertEqual(errors, [
            "ch06: short narration base cannot be resolved for voice.mp3"])

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
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            chapter = root / "ch01"
            shutil.copytree(model.CHAPTERS / "ch01", chapter)
            episode = model.read_yaml(chapter / "episode.yaml")
            episode["legacy"]["dir"] = "../legacy"
            model.write_yaml(chapter / "episode.yaml", episode)
            for name in ("index.html", "short/index.html"):
                index = root / "legacy" / name
                index.parent.mkdir(parents=True, exist_ok=True)
                index.write_text("<!doctype html>", encoding="utf-8")
            bootstrap = (
                "import sys; from pathlib import Path; "
                "sys.path.insert(0, str(Path(sys.argv[1]) / 'video')); "
                "from pipeline import model, cli; "
                "model.CHAPTERS=Path(sys.argv[2]); "
                "raise SystemExit(cli.main(['check','--chapter','ch01']))")
            result = subprocess.run(
                [sys.executable, "-c", bootstrap, str(ROOT), str(root)],
                cwd=ROOT, capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(result.returncode, 1)
        self.assertIn("VIDEO FAILED:", result.stderr)
        self.assertNotIn("Traceback", result.stderr)
        self.assertIn("audio full.mp3 is missing", result.stderr)


if __name__ == "__main__":
    unittest.main()
