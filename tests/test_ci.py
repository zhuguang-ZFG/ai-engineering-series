"""The effective root CI must validate both projects without publishing."""
from pathlib import Path
import re
import unittest

import yaml


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github/workflows/series.yml"


def commands(job):
    return "\n".join(step["run"] for step in job["steps"] if "run" in step)


def actions(job, prefix):
    return [step for step in job["steps"]
            if str(step.get("uses", "")).startswith(prefix)]


class SeriesWorkflow(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.workflow = yaml.safe_load(WORKFLOW.read_text(encoding="utf-8"))
        cls.jobs = cls.workflow["jobs"]

    def test_root_workflow_runs_for_changes_and_manual_requests(self):
        triggers = self.workflow.get("on") or self.workflow.get(True)
        self.assertIn("main", triggers["push"]["branches"])
        self.assertIn("feat/**", triggers["push"]["branches"])
        self.assertIn("fix/**", triggers["push"]["branches"])
        self.assertIn("pull_request", triggers)
        self.assertIn("workflow_dispatch", triggers)
        self.assertFalse(triggers["workflow_dispatch"]["inputs"]["build_books"]["default"])
        self.assertEqual(self.workflow["permissions"], {"contents": "read"})

    def test_root_and_both_project_checks_are_independent_jobs(self):
        for name in ("root", "agent-books", "model-course"):
            self.assertIn(name, self.jobs)
            self.assertNotIn("needs", self.jobs[name])
            self.assertNotIn("if", self.jobs[name])
        self.assertIn("series.py check --project all --structure-only", commands(self.jobs["root"]))
        self.assertIn("unittest discover -s tests", commands(self.jobs["root"]))
        for project in ("agent-books", "model-course"):
            self.assertIn(f"series.py check --project {project}", commands(self.jobs[project]))

    def test_effective_ci_does_not_depend_on_nested_workflows(self):
        self.assertEqual(WORKFLOW.parent, ROOT / ".github/workflows")
        for name, job in self.jobs.items():
            self.assertNotIn("uses", job, name)
            self.assertIn("steps", job, name)
            for step in job["steps"]:
                use = str(step.get("uses", ""))
                for project in ("agent-books", "model-course"):
                    self.assertNotIn(f"{project}/.github/workflows/", use)
                if "python series.py " in step.get("run", ""):
                    self.assertNotIn("working-directory", step)
                    self.assertNotIn("working-directory", job.get("defaults", {}).get("run", {}))
                    self.assertNotIn("working-directory", self.workflow.get("defaults", {}).get("run", {}))

    def test_dependency_caches_are_scoped_to_the_project_locks(self):
        expected = {
            "agent-books": ("3.12", "agent-books/yuyu-book/requirements.txt"),
            "model-course": ("3.13", "model-course/scripts/llm/requirements-books.txt"),
        }
        for project, (version, requirements) in expected.items():
            node = actions(self.jobs[project], "actions/setup-node@")[0]["with"]
            python = actions(self.jobs[project], "actions/setup-python@")[0]["with"]
            self.assertEqual(str(node["node-version"]), "22")
            self.assertEqual(node["cache-dependency-path"], f"{project}/package-lock.json")
            self.assertEqual(python["python-version"], version)
            self.assertEqual(python["cache-dependency-path"], requirements)
            installs = [step for step in self.jobs[project]["steps"] if "npm ci" in step.get("run", "")]
            self.assertEqual(len(installs), 1)
            self.assertEqual(installs[0]["working-directory"], project)

    def test_agent_checks_keep_companion_exercises_and_render_dependencies(self):
        run = commands(self.jobs["agent-books"])
        for required in ("check_bilingual_parity.py", "check-review-trace.mjs",
                         "-s hermes/examples", "check_aurora_workflow.py",
                         "codex/examples/check_workshop.py", "-s kimi/examples",
                         "pricing-lab/check_pricing.py", "fonts-noto-cjk",
                         "playwright install --with-deps chromium"):
            self.assertIn(required, run)
        example = next(step for step in self.jobs["agent-books"]["steps"]
                       if "check_bilingual_parity.py" in step.get("run", ""))
        self.assertEqual(example["working-directory"], "agent-books")
        cache = actions(self.jobs["agent-books"], "actions/cache@")
        self.assertTrue(any(step["with"]["path"] == "agent-books/yuyu-book/.cache" for step in cache))
        for step in cache:
            self.assertIn("agent-books/", step["with"]["key"])

    def test_course_keeps_lfs_media_and_browser_checks(self):
        job = self.jobs["model-course"]
        checkout = actions(job, "actions/checkout@")[0]["with"]
        self.assertTrue(checkout["lfs"])
        run = commands(job)
        for required in ("git lfs fsck", "model-course/book/assets/images",
                         "git-lfs.github.com/spec/v1", "ffmpeg", "fonts-noto-cjk",
                         "check:accessibility:llm", "check:reading:llm", "check:mechanisms:llm"):
            self.assertIn(required, run)
        self.assertEqual(job["env"]["COURSE_BROWSER_CHANNEL"], "chromium")
        for step in job["steps"]:
            if "npm run check:" in step.get("run", ""):
                self.assertEqual(step["working-directory"], "model-course")
        reports = actions(job, "actions/upload-artifact@")[0]["with"]["path"]
        self.assertIn("model-course/tmp/llm-review/accessibility-report.json", reports)
        self.assertIn("model-course/tmp/reading-review/*.json", reports)
        self.assertIn("model-course/tmp/mechanism-review/*.json", reports)

    def test_book_build_is_opt_in_and_uses_unified_entry_point(self):
        job = self.jobs["build"]
        self.assertIn("github.event_name == 'workflow_dispatch'", job["if"])
        self.assertIn("inputs.build_books", job["if"])
        self.assertEqual(set(job["needs"]), {"root", "agent-books", "model-course"})
        matrix = job["strategy"]["matrix"]["include"]
        self.assertEqual({entry["product"] for entry in matrix}, {"prompt", "llm"})
        for entry in matrix:
            self.assertTrue(entry["requirements"].startswith(entry["project"] + "/"))
        run = commands(job)
        self.assertIn('series.py build --product "${{ matrix.product }}" --lang zh --pdf --epub', run)
        self.assertIn('series.py collect --project "${{ matrix.project }}"', run)
        upload = actions(job, "actions/upload-artifact@")[0]
        self.assertEqual(upload["with"]["path"], "dist/")
        collect = next(step for step in job["steps"] if "series.py collect" in step.get("run", ""))
        self.assertLess(job["steps"].index(collect), job["steps"].index(upload))
        chrome = next(step for step in job["steps"] if "install --with-deps chrome" in step.get("run", ""))
        self.assertEqual(chrome["if"], "matrix.product == 'llm'")
        package = next(step for step in job["steps"] if "package_prompt.py" in step.get("run", ""))
        self.assertEqual(package["if"], "matrix.product == 'prompt'")
        self.assertIn("--output agent-books/yuyu-book/dist/yuyu-prompt-zh-examples.zip", package["run"])
        self.assertLess(job["steps"].index(package), job["steps"].index(collect))
        verification = next(step for step in job["steps"] if "paths.append(Path('agent-books" in step.get("run", ""))
        self.assertIn("agent-books/yuyu-book/dist/yuyu-prompt-zh-examples.zip", verification["run"])
        self.assertIn("path.is_file() and path.stat().st_size", run)

    def test_optional_build_uses_the_original_epubcheck_pin(self):
        job = self.jobs["build"]
        java = actions(job, "actions/setup-java@")[0]["with"]
        self.assertEqual(java, {"distribution": "temurin", "java-version": "17"})
        installer = next(step for step in job["steps"] if "sha256sum -c" in step.get("run", ""))
        original = (ROOT / "model-course/.github/workflows/ci.yml").read_text(encoding="utf-8")
        url = "https://github.com/w3c/epubcheck/releases/download/v5.3.0/epubcheck-5.3.0.zip"
        checksum = "6c07e68584b2e2ce2f89fe06e1246dfead3eb36b46b340e7d93524f29dcff6c5"
        for expected in (url, checksum):
            self.assertIn(expected, original)
            self.assertIn(expected, installer["run"])
        self.assertLess(installer["run"].index("sha256sum -c"), installer["run"].index("unzip -q"))
        self.assertEqual(installer["shell"], "bash")
        for name in ("root", "agent-books", "model-course"):
            self.assertFalse(actions(self.jobs[name], "actions/setup-java@"))
            self.assertNotIn("releases/download/v5.3.0", commands(self.jobs[name]))

    def test_fresh_epub_reports_and_course_checks_precede_collection(self):
        steps = self.jobs["build"]["steps"]
        build = next(step for step in steps if "series.py build" in step.get("run", ""))
        installer = next(step for step in steps if "sha256sum -c" in step.get("run", ""))
        collect = next(step for step in steps if "series.py collect" in step.get("run", ""))
        validators = [step for step in steps if "check_epub.py" in step.get("run", "")]
        self.assertEqual(len(validators), 2)
        for step in validators:
            self.assertLess(steps.index(build), steps.index(step))
            self.assertLess(steps.index(installer), steps.index(step))
            self.assertLess(steps.index(step), steps.index(collect))
            self.assertNotIn("continue-on-error", step)
        course = next(step for step in validators if step["if"] == "matrix.product == 'llm'")
        self.assertEqual(course["working-directory"], "model-course")
        for stem, report in (("llm-explained-handdraw", "llm-epubcheck"),
                             ("llm-course", "llm-course-epubcheck"),
                             ("llm-course-answers", "llm-course-answers-epubcheck")):
            self.assertIn(f"--epub deliverables/{stem}.epub --report deliverables/{report}.json", course["run"])
        for command in ("npm run check:books:llm", "npm run check:course:llm"):
            self.assertGreater(course["run"].index(command), course["run"].rindex("check_epub.py"))
        prompt = next(step for step in validators if step["if"] == "matrix.product == 'prompt'")
        report = "agent-books/yuyu-book/dist/yuyu-prompt-zh-epubcheck.json"
        self.assertIn(f"--epub agent-books/yuyu-book/dist/yuyu-prompt-zh.epub --report {report}", prompt["run"])
        self.assertNotIn("working-directory", prompt)
        uploads = actions(self.jobs["build"], "actions/upload-artifact@")
        prompt_report = next(step for step in uploads if step["with"]["path"] == report)
        self.assertEqual(prompt_report["if"], "matrix.product == 'prompt'")
        self.assertLess(steps.index(prompt), steps.index(prompt_report))

    def test_all_artifacts_use_root_relative_paths_and_fail_if_missing(self):
        uploads = []
        for name, job in self.jobs.items():
            for step in actions(job, "actions/upload-artifact@"):
                uploads.append(step)
                self.assertEqual(step["with"]["if-no-files-found"], "error", name)
                for path in step["with"]["path"].splitlines():
                    self.assertTrue(path.startswith(("agent-books/", "model-course/", "dist/")), path)
        self.assertGreaterEqual(len(uploads), 3)

    def test_ci_neither_publishes_nor_uses_write_permissions(self):
        for name, job in self.jobs.items():
            self.assertNotIn("environment", job, name)
            self.assertNotIn("permissions", job, name)
            for step in job["steps"]:
                use = str(step.get("uses", ""))
                self.assertNotIn("deploy-pages", use)
                self.assertNotIn("upload-pages", use)
                run = step.get("run", "")
                self.assertIsNone(re.search(r"\bgit\s+(push|commit)\b|\bgh\s+release\s+create\b", run), name)
            for step in actions(job, "actions/checkout@"):
                self.assertFalse(step["with"]["persist-credentials"], name)


if __name__ == "__main__":
    unittest.main()
