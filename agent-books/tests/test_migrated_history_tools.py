"""History-dependent helpers must survive the move into agent-books/."""
from contextlib import redirect_stdout
import importlib.util
import io
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
sys.path.insert(0, str(ROOT / "scripts"))
from book_history import HistoryError, RevisionFiles  # noqa: E402
import repoint_omp_refs as repoint  # noqa: E402


def load_tool(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / "docs/yuyu-overhaul" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


markers = load_tool("check_block_markers")
pedagogy = load_tool("measure_pedagogy")


class MigratedHistoryTools(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="book-history-")
        self.addCleanup(self.temporary.cleanup)
        self.repository = Path(self.temporary.name).resolve()
        self.project = self.repository
        self.environment = {**os.environ, "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.devnull,
                            "GIT_AUTHOR_NAME": "History Test", "GIT_AUTHOR_EMAIL": "history@example.invalid",
                            "GIT_COMMITTER_NAME": "History Test", "GIT_COMMITTER_EMAIL": "history@example.invalid"}
        self.git("init", "-q")
        self.git("config", "core.autocrlf", "false")
        self.content = "<!-- block: retained -->\nanchor term\n```mermaid\nflowchart LR\n A --> B\n```\n"
        self.write("omp/ch01.md", self.content)
        self.write("omp/章节 [1].md", "literal Unicode path\n")
        self.write_metadata(2)
        self.legacy = self.commit("Standalone project")

    def git(self, *arguments):
        return subprocess.run(["git", *arguments], cwd=self.repository, env=self.environment,
                              capture_output=True, text=True, encoding="utf-8", check=True).stdout.strip()

    def commit(self, title):
        self.git("add", "-A")
        self.git("commit", "-qm", title)
        return self.git("rev-parse", "HEAD")

    def write(self, relative, content):
        path = self.project / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8", newline="\n")
        return path

    def write_metadata(self, line):
        text = json.dumps({"evidence": [f"omp/ch01.md:{line}"]}) + "\n"
        for name in ("glosses-omp.json", "manifest-omp.json"):
            self.write(f"yuyu-book/{name}", text)

    def migrate(self):
        self.project = self.repository / "agent-books"
        self.project.mkdir()
        for name in ("omp", "yuyu-book"):
            (self.repository / name).rename(self.project / name)
        self.write("omp/ch01.md", "New heading\n" + self.content)
        self.write_metadata(3)
        self.current = self.commit("Move project into series")

    def sources(self):
        return tuple(self.project / "yuyu-book" / name for name in ("glosses-omp.json", "manifest-omp.json"))

    def test_reads_standalone_and_prefixed_snapshots_without_mixing_them(self):
        self.assertEqual(RevisionFiles(self.project, "HEAD").read_text("omp/ch01.md"), self.content)
        self.migrate()
        current = RevisionFiles(self.project, "HEAD")
        legacy = RevisionFiles(self.project, self.legacy)
        self.assertEqual(current.read_text("omp/ch01.md"), "New heading\n" + self.content)
        self.assertEqual(legacy.read_text("omp/ch01.md"), self.content)
        self.assertEqual(current.read_text("omp/章节 [1].md"), "literal Unicode path\n")
        with patch.object(repoint, "ROOT", self.project), patch.object(repoint, "SOURCES", self.sources()):
            self.assertEqual(set(repoint.collect_refs("HEAD")), {("omp/ch01.md", 3)})
            self.assertEqual(set(repoint.collect_refs(self.legacy)), {("omp/ch01.md", 2)})

    def test_current_project_never_falls_back_to_an_unrelated_root_file(self):
        self.migrate()
        root_file = self.repository / "omp/ch01.md"
        root_file.parent.mkdir()
        root_file.write_text("unrelated root content", encoding="utf-8")
        (root_file.parent / "missing.md").write_text("not part of the project", encoding="utf-8")
        self.commit("Add unrelated root files")
        history = RevisionFiles(self.project, "HEAD")
        self.assertEqual(history.read_text("omp/ch01.md"), "New heading\n" + self.content)
        self.assertIsNone(history.read_text("omp/missing.md", missing_ok=True))
        with self.assertRaisesRegex(HistoryError, "file is absent"):
            history.read_text("omp/missing.md")

    def test_marker_guard_detects_removed_anchors_and_fences_after_migration(self):
        self.migrate()
        self.write("omp/ch01.md", "New heading\nanchor term\n")
        output = io.StringIO()
        with patch.object(markers, "ROOT", self.project), redirect_stdout(output):
            self.assertEqual(markers.check("omp/ch01.md", [], set()), 2)
        self.assertIn("retained", output.getvalue())
        self.assertNotIn("跳过锚点对比", output.getvalue())

    def test_pedagogy_uses_a_real_nonzero_head_baseline(self):
        self.migrate()
        before = "New heading\n" + self.content
        self.write("omp/ch01.md", before * 2)
        output = io.StringIO()
        with patch.object(pedagogy, "ROOT", self.project), \
                patch.object(pedagogy, "units", return_value=[("ch01", "zh", "omp/ch01.md")]), \
                redirect_stdout(output):
            self.assertEqual(pedagogy.git_head("omp/ch01.md"), before)
            self.assertEqual(pedagogy.report({"ch01"}), 1)
        self.assertIn("100.0", output.getvalue())

    def test_repointer_preserves_cli_and_rewrites_from_the_legacy_snapshot(self):
        self.migrate()
        self.write("omp/ch01.md", "Extra line\nNew heading\n" + self.content)
        output = io.StringIO()
        with patch.object(repoint, "ROOT", self.project), patch.object(repoint, "SOURCES", self.sources()), \
                patch.object(sys, "argv", ["repoint_omp_refs.py", "--base", self.legacy, "--write"]), \
                redirect_stdout(output):
            self.assertEqual(repoint.main(), 0)
        for source in self.sources():
            self.assertEqual(json.loads(source.read_text(encoding="utf-8"))["evidence"], ["omp/ch01.md:4"])
        self.assertIn("omp/ch01.md:2 -> :4", output.getvalue())

    def test_missing_revision_or_metadata_is_not_replaced_by_working_tree_data(self):
        self.migrate()
        with patch.object(repoint, "ROOT", self.project), patch.object(repoint, "SOURCES", self.sources()):
            with self.assertRaisesRegex(HistoryError, "rev-parse failed"):
                repoint.collect_refs("no-such-commit")
            self.git("rm", "agent-books/yuyu-book/manifest-omp.json")
            self.commit("Remove a historical registry")
            self.write_metadata(99)
            with self.assertRaisesRegex(HistoryError, "file is absent"):
                repoint.collect_refs("HEAD")
        with tempfile.TemporaryDirectory(prefix="not-a-repository-") as outside:
            with self.assertRaisesRegex(HistoryError, "rev-parse failed"):
                RevisionFiles(Path(outside), "HEAD")

    def test_cli_reports_git_failure_without_claiming_success(self):
        self.migrate()
        scripts = self.project / "scripts"
        scripts.mkdir()
        for name in ("repoint_omp_refs.py", "book_history.py"):
            shutil.copyfile(ROOT / "scripts" / name, scripts / name)
        result = subprocess.run([sys.executable, "-B", str(scripts / "repoint_omp_refs.py"),
                                 "--base", "no-such-commit"], cwd=self.repository, env=self.environment,
                                capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(result.returncode, 2)
        self.assertIn("rev-parse failed", result.stderr)
        self.assertNotIn("Traceback", result.stderr)
        self.assertNotIn("ok", result.stdout)


if __name__ == "__main__":
    unittest.main()
