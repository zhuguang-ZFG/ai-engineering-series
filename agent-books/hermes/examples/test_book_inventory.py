"""Offline checks for original example only; does not load Hermes PluginManager."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

spec = importlib.util.spec_from_file_location(
    "book_inventory", Path(__file__).parent / "book-inventory" / "__init__.py"
)
plugin = importlib.util.module_from_spec(spec)
spec.loader.exec_module(plugin)


class InventoryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()

    def test_relative_markdown_inventory(self):
        (self.root / "sub").mkdir()
        (self.root / "sub" / "b.MD").write_text("B", encoding="utf-8")
        (self.root / "a.md").write_text("A", encoding="utf-8")
        (self.root / "secret.txt").write_text("excluded", encoding="utf-8")
        result = json.loads(plugin.make_inventory_handler(self.root)({}))
        self.assertEqual(result, {"files": ["a.md", "sub/b.MD"], "truncated": False})

    def test_missing_or_empty_root(self):
        for root in ("", self.root / "missing"):
            with self.subTest(root=str(root)), self.assertRaises(ValueError):
                plugin.make_inventory_handler(root)

    def test_result_limit_and_scan_budget(self):
        for name in ("a.md", "b.md", "c.md"):
            (self.root / name).write_text("", encoding="utf-8")
        result = json.loads(plugin.make_inventory_handler(self.root, limit=2)({}))
        self.assertEqual(result, {"files": ["a.md", "b.md"], "truncated": True})
        result = json.loads(plugin.make_inventory_handler(self.root, max_entries=2)({}))
        self.assertIn("error", result)

    def test_parameters_cannot_change_root(self):
        handler = plugin.make_inventory_handler(self.root)
        for params in ({"root": "elsewhere"}, [], None):
            with self.subTest(params=params):
                self.assertIn("error", json.loads(handler(params)))

    def test_disappeared_root_is_an_error(self):
        directory = self.root / "gone"
        directory.mkdir()
        handler = plugin.make_inventory_handler(directory)
        directory.rmdir()
        self.assertIn("error", json.loads(handler({})))

    def test_symlinks_are_excluded_and_root_is_rejected(self):
        external = self.root / "outside"
        external.mkdir()
        (external / "private.md").write_text("", encoding="utf-8")
        workspace = self.root / "workspace"
        workspace.mkdir()
        try:
            (workspace / "linked-dir").symlink_to(external, target_is_directory=True)
            (workspace / "linked-file.md").symlink_to(external / "private.md")
        except OSError as error:
            self.skipTest(f"OS did not allow symlink creation: {error.__class__.__name__}")
        result = json.loads(plugin.make_inventory_handler(workspace)({}))
        self.assertEqual(result["files"], [])
        with self.assertRaises(ValueError):
            plugin.make_inventory_handler(workspace / "linked-dir")

    def test_registration_contract_with_fake_context(self):
        class FakeContext:
            def get_config(inner, key, default):
                self.assertEqual(key, "root")
                return str(self.root)

            def register_tool(inner, **values):
                inner.values = values
                return object()

        ctx = FakeContext()
        plugin.register(ctx)
        self.assertEqual(ctx.values["name"], "book_inventory")
        self.assertEqual(ctx.values["toolset"], "book_inventory")
        self.assertEqual(ctx.values["schema"], plugin.SCHEMA)
        self.assertEqual(json.loads(ctx.values["handler"]({}))["files"], [])

    def test_rejected_registration_is_visible(self):
        class RejectingContext:
            def get_config(inner, key, default):
                return str(self.root)

            def register_tool(inner, **values):
                return None

        with self.assertRaisesRegex(RuntimeError, "not accepted"):
            plugin.register(RejectingContext())

    def test_missing_config_never_registers_a_tool(self):
        class MissingConfig:
            def get_config(inner, key, default):
                return default

            def register_tool(inner, **values):
                self.fail("Missing root must fail before tool registration")

        with self.assertRaises(ValueError):
            plugin.register(MissingConfig())


if __name__ == "__main__":
    unittest.main()
