"""Root routing and collection must preserve project boundaries and failures."""
from __future__ import annotations

import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("series_router", ROOT / "series.py")
series = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(series)


class SeriesTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name).resolve()
        shutil.copyfile(ROOT / "series.json", self.root / "series.json")
        self.catalog = series.load_catalog(self.root)
        self.put("README.md", "# Series\n[Read](index.html)\n")
        self.put("index.html", '<a href="agent-books/README.md">Books</a>')
        self.put("series.py", "# fixture")
        self.put("scripts/build_index.py", "# fixture")
        for name, project in self.catalog["projects"].items():
            for relative in project["required"]:
                if "." in Path(relative).name:
                    self.put(f"{name}/{relative}", "fixture")
                else:
                    (self.root / name / relative).mkdir(parents=True, exist_ok=True)
        for book in self.catalog["books"]:
            self.put(f"{book['project']}/{book['source_entry']}", "# Source")

    def put(self, relative, text="fixture"):
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        return path

    def test_catalog_rejects_duplicate_books_and_project_escape(self):
        for mutate in (lambda d: d["books"].append(d["books"][0]),
                       lambda d: d["projects"]["agent-books"].update(path="../outside"),
                       lambda d: d["books"][0].update(source_entry="../outside")):
            data = json.loads((ROOT / "series.json").read_text(encoding="utf-8"))
            mutate(data)
            (self.root / "series.json").write_text(json.dumps(data), encoding="utf-8")
            with self.assertRaises(ValueError):
                series.load_catalog(self.root)

    def test_structure_only_only_refreshes_local_index_without_project_checks(self):
        with patch.object(series, "run", return_value=0) as runner:
            self.assertEqual(series.check_projects(self.root, self.catalog, structure_only=True), 0)
        runner.assert_called_once_with([sys.executable, "scripts/build_index.py"], self.root)

    def test_clean_checkout_refreshes_stale_index_without_build_artifacts(self):
        shutil.copyfile(ROOT / "scripts/build_index.py", self.root / "scripts/build_index.py")
        (self.root / "assets").mkdir()
        shutil.copyfile(ROOT / "assets/series-map.svg", self.root / "assets/series-map.svg")
        stale_link = "agent-books/yuyu-book/dist/yuyu-prompt-zh.html"
        self.put("index.html", f'<a href="{stale_link}">Stale local build</a>')
        self.assertFalse((self.root / "agent-books/yuyu-book/dist").exists())
        self.assertTrue(series.structure(self.root, self.catalog))
        with patch.object(series, "run", wraps=series.run) as runner:
            self.assertEqual(series.check_projects(self.root, self.catalog, structure_only=True), 0)
        runner.assert_called_once_with([sys.executable, "scripts/build_index.py"], self.root)
        self.assertNotIn(stale_link, (self.root / "index.html").read_text(encoding="utf-8"))
        self.assertFalse((self.root / "agent-books/yuyu-book/dist").exists())
        self.assertEqual(series.structure(self.root, self.catalog), [])

    def test_index_refresh_failure_stops_before_project_checks(self):
        with patch.object(series, "run", return_value=17) as runner:
            self.assertEqual(series.check_projects(self.root, self.catalog), 17)
        runner.assert_called_once_with([sys.executable, "scripts/build_index.py"], self.root)

    def test_missing_or_escaping_local_root_link_fails_structure(self):
        for link in ("missing.html", "../outside.html", "/absolute.html"):
            self.put("index.html", f'<a href="{link}">Broken</a>')
            self.assertTrue(series.structure(self.root, self.catalog))

    def test_check_stops_and_returns_exact_child_error(self):
        with patch.object(series, "run", side_effect=[0, 7]) as runner:
            self.assertEqual(series.check_projects(self.root, self.catalog), 7)
        self.assertEqual(runner.call_count, 2)
        self.assertEqual(runner.call_args.args, ([sys.executable, "scripts/bookctl.py", "check", "--fast"], self.root / "agent-books"))

    def test_model_check_uses_npm_in_its_own_directory(self):
        with patch.object(series, "run", side_effect=[0, 9]) as runner, patch.object(series, "npm_command", return_value="npm-test"):
            self.assertEqual(series.check_projects(self.root, self.catalog, "model-course"), 9)
        self.assertEqual(runner.call_count, 2)
        self.assertEqual(runner.call_args.args, (["npm-test", "test"], self.root / "model-course"))

    def test_build_is_independent_of_callers_working_directory(self):
        original = Path.cwd()
        try:
            os.chdir(self.root.parent)
            with patch.object(series, "run", return_value=0) as runner:
                self.assertEqual(series.build(self.root, self.catalog, "prompt", "zh", True, True), 0)
            runner.assert_called_once_with([sys.executable, "scripts/bookctl.py", "build", "--product", "prompt",
                                            "--lang", "zh", "--pdf", "--epub"], self.root / "agent-books")
        finally:
            os.chdir(original)

    def test_llm_export_uses_real_parameterless_interface_and_stops_on_build_failure(self):
        with patch.object(series, "run", side_effect=[0, 0]) as runner, patch.object(series, "npm_command", return_value="npm-test"):
            self.assertEqual(series.build(self.root, self.catalog, "llm", pdf=True), 0)
        self.assertEqual(runner.call_args_list[1].args, ([sys.executable, "scripts/llm/export_books.py"], self.root / "model-course"))
        with patch.object(series, "run", return_value=11) as runner, patch.object(series, "npm_command", return_value="npm-test"):
            self.assertEqual(series.build(self.root, self.catalog, "llm", epub=True), 11)
            self.assertEqual(runner.call_count, 1)

    def test_unsupported_language_never_starts_a_build(self):
        with patch.object(series, "run") as runner:
            self.assertEqual(series.build(self.root, self.catalog, "llm", "en"), 2)
        runner.assert_not_called()

    def test_collected_route_passes_language_and_date_without_shell(self):
        with patch.object(series, "run", return_value=0) as runner:
            self.assertEqual(series.main(["collected", "--lang", "zh",
                                          "--date", "2026-11-12"], root=self.root), 0)
        runner.assert_called_once_with([sys.executable, "scripts/collected.py",
                                        "--lang", "zh", "--date", "2026-11-12"], self.root)
        with patch.object(series, "run", return_value=7):
            self.assertEqual(series.main(["collected"], root=self.root), 7)

    def test_run_preserves_exit_code_without_shell(self):
        completed = subprocess.CompletedProcess(["command"], 23)
        with patch.dict(os.environ, {"PATH": "original-path", "PYTHONUTF8": "0", "SERIES_TEST_MARKER": "inherited"}):
            with patch.object(series.subprocess, "run", return_value=completed) as runner:
                self.assertEqual(series.run(["command"], self.root), 23)
            environment = runner.call_args.kwargs["env"]
            self.assertEqual(environment["PATH"], str(Path(sys.executable).parent) + os.pathsep + "original-path")
            self.assertEqual(environment["PYTHONUTF8"], "1")
            self.assertEqual(environment["SERIES_TEST_MARKER"], "inherited")
            self.assertEqual(os.environ["PATH"], "original-path")
            self.assertEqual(os.environ["PYTHONUTF8"], "0")
        runner.assert_called_once_with(["command"], cwd=self.root, env=environment, shell=False, check=False)

    def test_collection_selects_only_book_artifacts_and_flattens_agent_outputs(self):
        for name in ("yuyu-prompt-zh.html", "yuyu-prompt-zh.pdf", "yuyu-prompt-examples.zip", "secret.zip", "yuyu-prompt-demo.mp4", "yuyu-prompt-state.json"):
            self.put("agent-books/yuyu-book/dist/" + name)
        with patch.object(series, "run", return_value=0) as runner:
            report = series.collect(self.root, self.catalog, "agent-books")
        self.assertEqual({row["path"] for row in report["files"]},
                         {"agent-books/yuyu-prompt-zh.html", "agent-books/yuyu-prompt-zh.pdf", "agent-books/yuyu-prompt-examples.zip"})
        runner.assert_called_once_with([sys.executable, "scripts/build_index.py", "--dist"], self.root)
        for row in report["files"]:
            self.assertEqual(row["sha256"], series.sha256(self.root / "dist" / row["path"]))

    def test_course_collection_keeps_relative_assets_and_excludes_media_and_cache(self):
        self.put("model-course/exports/llm/course.html", '<img src="../../book/assets/diagram.svg">')
        self.put("model-course/book/assets/diagram.svg", "<svg/>")
        self.put("model-course/deliverables/llm-course.pdf")
        self.put("model-course/deliverables/llm-course-epubcheck.json", "{}")
        for path in ("deliverables/movie.mp4", "book/assets/audio.mp3", "exports/cards/output/cache.html", "book/llm/__pycache__/code.py"):
            self.put("model-course/" + path)
        with patch.object(series, "run", return_value=0):
            report = series.collect(self.root, self.catalog, "model-course")
        names = {row["path"] for row in report["files"]}
        self.assertIn("model-course/book/assets/diagram.svg", names)
        self.assertIn("model-course/deliverables/llm-course.pdf", names)
        self.assertFalse(any("movie" in name or "audio" in name or "cache" in name for name in names))
        entry = self.root / "dist/model-course/exports/llm/course.html"
        self.assertTrue((entry.parent / "../../book/assets/diagram.svg").resolve().is_file())

    def test_agent_collection_keeps_license_credits_and_source_registry_paths(self):
        self.put("agent-books/yuyu-book/dist/yuyu-prompt-zh.html")
        self.put("agent-books/LICENSE", "Original author and license")
        self.put("agent-books/CREDITS.md", "[Registry](yuyu-book/sources.json)")
        self.put("agent-books/yuyu-book/sources.json", "{}")
        self.put("agent-books/yuyu-book/sources-prompt.json", "{}")
        self.put("agent-books/docs/agent-series/sources.lock.json", "{}")
        with patch.object(series, "run", return_value=0):
            report = series.collect(self.root, self.catalog, "agent-books")
        names = {row["path"] for row in report["files"]}
        for relative in ("LICENSE", "CREDITS.md", "yuyu-book/sources.json", "yuyu-book/sources-prompt.json", "docs/agent-series/sources.lock.json"):
            self.assertIn("agent-books/" + relative, names)
        self.assertEqual(series.entry_links(self.root / "dist", self.root / "dist/agent-books/CREDITS.md"), [])
        self.assertEqual((self.root / "dist/agent-books/LICENSE").read_text(encoding="utf-8"), "Original author and license")

    def test_course_collection_preserves_exercises_licenses_and_linked_support_files(self):
        self.put("model-course/README.md", "[Checker](scripts/llm/check.py)\n[Gallery](design/handdraw/book-figures.html)")
        self.put("model-course/scripts/llm/check.py", "print('offline')")
        self.put("model-course/design/handdraw/book-figures.html", '<img src="renders/figure.png">')
        self.put("model-course/design/handdraw/renders/figure.png")
        for name in ("model.py", "train.py", "corpus.jsonl", "sft.jsonl", "LICENSE-CORPUS", ".gitignore"):
            self.put("model-course/book/llm/examples/tiny_decoder/" + name)
        self.put("model-course/book/llm/fixtures/js-tiktoken-LICENSE", "MIT license fixture")
        self.put("model-course/book/llm/examples/tiny_decoder/renders/temporary.png")
        self.put("model-course/design/handdraw/renders/recording.mp4")
        with patch.object(series, "run", return_value=0):
            report = series.collect(self.root, self.catalog, "model-course")
        names = {row["path"] for row in report["files"]}
        for name in ("model.py", "train.py", "corpus.jsonl", "sft.jsonl", "LICENSE-CORPUS", ".gitignore"):
            self.assertIn("model-course/book/llm/examples/tiny_decoder/" + name, names)
        self.assertIn("model-course/book/llm/fixtures/js-tiktoken-LICENSE", names)
        self.assertIn("model-course/design/handdraw/renders/figure.png", names)
        self.assertFalse(any("temporary" in name or "recording" in name for name in names))
        for entry in ("README.md", "design/handdraw/book-figures.html"):
            self.assertEqual(series.entry_links(self.root / "dist", self.root / "dist/model-course" / entry), [])

    def test_empty_artifact_selection_and_unknown_project_are_rejected(self):
        with self.assertRaises(ValueError):
            series.collect(self.root, self.catalog, "agent-books")
        with self.assertRaises(ValueError):
            series.selected_projects("../other")

    def test_collection_rejects_destination_escape_before_copy(self):
        self.put("agent-books/yuyu-book/dist/yuyu-prompt-zh.pdf")
        outside = self.root.parent / (self.root.name + "-outside")
        outside.mkdir()
        self.addCleanup(lambda: outside.rmdir())
        try:
            (self.root / "dist").symlink_to(outside, target_is_directory=True)
        except OSError:
            self.skipTest("directory symlinks unavailable")
        with self.assertRaises(ValueError):
            series.collect(self.root, self.catalog, "agent-books")
        self.assertEqual(list(outside.iterdir()), [])

    def test_index_failure_is_propagated_by_main(self):
        self.put("agent-books/yuyu-book/dist/yuyu-prompt-zh.pdf")
        with patch.object(series, "run", return_value=13):
            self.assertEqual(series.main(["collect", "--project", "agent-books"], root=self.root), 13)


if __name__ == "__main__":
    unittest.main()
