"""CI tiering is a contract: triggers, jobs and release wiring are pinned.

Comments and line numbers churn; job keys, guards and step commands do not.
These tests read the workflow YAML instead of grepping raw lines so that
formatting changes cannot silently move a job back onto every pull request.
"""
from __future__ import annotations

import unittest
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
WORKFLOWS = ROOT / ".github" / "workflows"


def load(name: str) -> dict:
    return yaml.safe_load((WORKFLOWS / name).read_text(encoding="utf-8"))


def triggers(workflow: dict) -> dict:
    # PyYAML resolves the unquoted ``on`` key to True under YAML 1.1 rules.
    return workflow.get("on") or workflow.get(True) or {}


def run_commands(job: dict) -> str:
    return "\n".join(step["run"] for step in job.get("steps", []) if "run" in step)


def upload_steps(workflow: dict):
    for job_name, job in workflow["jobs"].items():
        for step in job.get("steps", []):
            if str(step.get("uses", "")).startswith("actions/upload-artifact"):
                yield job_name, step


class BookWorkflow(unittest.TestCase):
    def test_the_legacy_check_book_workflow_stays_gone(self):
        self.assertFalse((WORKFLOWS / "check-book.yml").exists())

    def test_book_ci_declares_fast_full_omp_bootstrap(self):
        jobs = load("book.yml")["jobs"]
        self.assertLessEqual({"fast", "full", "omp", "bootstrap"}, set(jobs))
        self.assertEqual(jobs["fast"]["name"], "Fast")
        self.assertEqual(jobs["full"]["name"], "Full")
        self.assertEqual(jobs["omp"]["name"], "Omp")
        self.assertTrue(jobs["bootstrap"]["name"].startswith("Bootstrap"))
        self.assertEqual(jobs["full"].get("needs"), "fast")

    def test_pull_requests_pay_only_for_the_fast_layer(self):
        workflow = load("book.yml")
        trigger = triggers(workflow)
        self.assertTrue(trigger["pull_request"]["paths"])
        self.assertIn("workflow_dispatch", trigger)
        self.assertIn("main", trigger["push"]["branches"])

        jobs = workflow["jobs"]
        self.assertNotIn("if", jobs["fast"])
        for name in ("full", "omp", "bootstrap"):
            guard = jobs[name].get("if")
            self.assertIsInstance(guard, str, name)
            self.assertIn("github.event_name", guard, name)
            self.assertIn("pull_request", guard, name)
            self.assertNotIn("== 'pull_request'", guard, name)

    def test_each_tier_runs_its_bookctl_layer(self):
        jobs = load("book.yml")["jobs"]
        self.assertIn("bookctl.py check --fast", run_commands(jobs["fast"]))
        self.assertIn("bookctl.py check --full", run_commands(jobs["full"]))
        self.assertIn("build --product omp", run_commands(jobs["omp"]))
        self.assertIn("bookctl.py doctor", run_commands(jobs["bootstrap"]))
        self.assertIn("build --check", run_commands(jobs["bootstrap"]))

    def test_every_upload_step_fails_when_artifacts_are_missing(self):
        for name in ("book.yml", "release.yml"):
            uploads = list(upload_steps(load(name)))
            self.assertTrue(uploads, name)
            for job_name, step in uploads:
                self.assertEqual(
                    step.get("with", {}).get("if-no-files-found"), "error",
                    f"{name}:{job_name}:{step.get('name', step.get('uses'))}")


class ReleaseWorkflow(unittest.TestCase):
    def test_release_is_tag_or_manual_only(self):
        trigger = triggers(load("release.yml"))
        self.assertEqual(trigger["push"]["tags"], ["v*"])
        version = trigger["workflow_dispatch"]["inputs"]["version"]
        self.assertTrue(version["required"])

    def test_release_uses_the_shared_setup_and_release_script(self):
        job = load("release.yml")["jobs"]["release"]
        uses = [step.get("uses") for step in job["steps"] if "uses" in step]
        self.assertIn("./.github/actions/book-setup", uses)
        commands = run_commands(job)
        self.assertIn("scripts/release.py", commands)
        self.assertIn("--version", commands)
        self.assertIn("--epub", commands)
        self.assertIn("bookctl.py check --full", commands)

    def test_release_verifies_checksums_before_upload(self):
        job = load("release.yml")["jobs"]["release"]
        commands = [step.get("run", "") for step in job["steps"]]
        self.assertTrue(any("sha256sum --check SHA256SUMS" in command
                            for command in commands))

    def test_shared_setup_action_is_a_composite_with_both_toolchains(self):
        action = yaml.safe_load(
            (ROOT / ".github/actions/book-setup/action.yml")
            .read_text(encoding="utf-8"))
        self.assertEqual(action["runs"]["using"], "composite")
        uses = [step.get("uses") for step in action["runs"]["steps"]
                if "uses" in step]
        self.assertTrue(any(str(use).startswith("actions/setup-node") for use in uses))
        self.assertTrue(any(str(use).startswith("actions/setup-python") for use in uses))


if __name__ == "__main__":
    unittest.main()
