import hashlib
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

SCRIPT = Path(__file__).resolve().parents[1] / "book/llm/examples/delivery/check_package.py"
spec = importlib.util.spec_from_file_location("delivery", SCRIPT)
delivery = importlib.util.module_from_spec(spec)
spec.loader.exec_module(delivery)


class DeliveryTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name) / "release"
        self.root.mkdir()
        self.manifest = dict(release="1", created="2026-11-08", scope="local", start="python app.py", health="GET /health", files={})
        for name in ("requirements.lock", "runbook.md", "user-guide.md", "app.py"):
            content = f"fixture: {name}".encode()
            (self.root / name).write_bytes(content)
            self.manifest["files"][name] = hashlib.sha256(content).hexdigest()

    def check(self):
        (self.root / "release.json").write_text(json.dumps(self.manifest), encoding="utf-8")
        return delivery.check_package(self.root)

    def test_valid_package_and_tampering(self):
        self.assertEqual(self.check()["status"], "ok")
        (self.root / "app.py").write_text("changed", encoding="utf-8")
        result = self.check()
        self.assertEqual(result["status"], "failed")
        self.assertIn("hash mismatch: app.py", result["problems"])

    def test_missing_or_invalid_hash_list_fails(self):
        for files in (None, [], {}, "files"):
            with self.subTest(files=files):
                self.manifest["files"] = files
                self.assertEqual(self.check()["status"], "failed")

    def test_required_unlisted_file_and_invalid_digest_fail(self):
        del self.manifest["files"]["runbook.md"]
        self.manifest["files"]["app.py"] = "not-a-hash"
        result = self.check()
        self.assertEqual(result["status"], "failed")
        self.assertTrue(any("runbook.md" in p for p in result["problems"]))
        self.assertTrue(any("SHA-256" in p for p in result["problems"]))

    def test_external_paths_never_reach_hash_reader(self):
        for name in ("../private.txt", "/private.txt", "C:/private.txt", "C:private.txt", "..\\private.txt", "file:stream"):
            with self.subTest(name=name):
                self.manifest["files"] = {name: "0" * 64}
                with patch.object(delivery, "sha256", side_effect=AssertionError("must not read outside file")):
                    self.assertEqual(self.check()["status"], "failed")

    def test_symlink_outside_is_rejected_before_reading(self):
        outside = self.root.parent / "outside.txt"
        outside.write_text("private", encoding="utf-8")
        try:
            (self.root / "escape.txt").symlink_to(outside)
        except OSError:
            self.skipTest("symlink creation unavailable")
        self.manifest["files"] = {"escape.txt": "0" * 64}
        with patch.object(delivery, "sha256", side_effect=AssertionError("outside read")):
            self.assertEqual(self.check()["status"], "failed")

    def test_malformed_root_missing_file_and_self_hash_fail(self):
        self.manifest = []
        self.assertEqual(self.check()["status"], "failed")
        (self.root / "release.json").write_text("{", encoding="utf-8")
        self.assertEqual(delivery.check_package(self.root)["status"], "failed")
        self.set_manifest_for_self_hash()
        self.assertEqual(self.check()["status"], "failed")

    def set_manifest_for_self_hash(self):
        self.manifest = dict(release="1", created="today", scope="local", start="run", health="health", files={"release.json": "0" * 64})


if __name__ == "__main__":
    unittest.main()
