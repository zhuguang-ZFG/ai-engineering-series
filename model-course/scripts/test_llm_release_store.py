import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path

DIRECTORY = Path(__file__).resolve().parents[1] / "book/llm/examples/delivery"
spec = importlib.util.spec_from_file_location("release_store", DIRECTORY / "release_store.py")
release_store = importlib.util.module_from_spec(spec)
sys.path.insert(0, str(DIRECTORY))
try:
    spec.loader.exec_module(release_store)
finally:
    sys.path.pop(0)


class ReleaseStoreTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.payload = self.root / "payload"
        self.payload.mkdir()
        self.store = self.root / "store"
        for name in ("requirements.lock", "runbook.md", "user-guide.md", "app.py"):
            (self.payload / name).write_text("original " + name, encoding="utf-8")

    def build(self, name):
        return release_store.build(self.payload, self.store, name, created="2026-11-09",
                                   scope="test", start="python app.py", health="GET /health")

    def test_build_select_and_rollback_keep_previous_bytes(self):
        self.build("v1")
        release_store.select(self.store, "v1")
        original = (self.store / "releases/v1/app.py").read_bytes()
        (self.payload / "app.py").write_text("version 2", encoding="utf-8")
        self.build("v2")
        release_store.select(self.store, "v2")
        self.assertEqual(release_store.current(self.store)["release"], "v2")
        release_store.select(self.store, "v1")
        self.assertEqual(release_store.current(self.store)["release"], "v1")
        self.assertEqual((self.store / "releases/v1/app.py").read_bytes(), original)
        with self.assertRaises(ValueError):
            self.build("v1")

    def test_failed_candidate_cannot_replace_current(self):
        self.build("v1")
        self.build("v2")
        release_store.select(self.store, "v1")
        pointer = (self.store / "current.json").read_bytes()
        (self.store / "releases/v2/app.py").write_text("tampered", encoding="utf-8")
        with self.assertRaises(ValueError):
            release_store.select(self.store, "v2")
        self.assertEqual((self.store / "current.json").read_bytes(), pointer)
        self.assertEqual(release_store.current(self.store)["release"], "v1")

    def test_unlisted_file_and_changed_manifest_are_rejected(self):
        self.build("v1")
        release_store.select(self.store, "v1")
        extra = self.store / "releases/v1/extra.py"
        extra.write_text("unlisted", encoding="utf-8")
        with self.assertRaises(ValueError):
            release_store.current(self.store)
        extra.unlink()
        manifest = self.store / "releases/v1/release.json"
        data = json.loads(manifest.read_text(encoding="utf-8"))
        data["start"] = "changed"
        manifest.write_text(json.dumps(data), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "manifest changed"):
            release_store.current(self.store)

    def test_bad_payload_and_paths_do_not_publish(self):
        for name in ("../escape", "/absolute", "C:drive", "two/names", ""):
            with self.subTest(name=name), self.assertRaises(ValueError):
                self.build(name)
        (self.payload / "runbook.md").unlink()
        with self.assertRaises(ValueError):
            self.build("missing")
        self.assertFalse((self.store / "releases/missing").exists())
        self.assertEqual(list((self.store / "releases").iterdir()), [])


if __name__ == "__main__":
    unittest.main()
