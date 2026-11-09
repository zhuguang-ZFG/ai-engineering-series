"""Every chapter ships one runnable case, and the page prints what it prints.

The cases are teaching models, not Claude Code source, so nothing else in the
suite executes them. Without this test an edit to a case could quietly stop
matching the "expected result" line two paragraphs above it, or one edition
could lose the block the other still carries.
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHAPTERS = [f"ch{number:02d}" for number in range(1, 16)]

LABELS = {
    "zh": ("**最小可运行案例：**", "**版本锁：**", "**预期结果：**",
           "**前置：**", "**回链：**"),
    "en": ("**Minimal runnable case:**", "**Version lock:**",
           "**Expected result:**", "**Prerequisite:**", "**Backlink:**"),
}
STDLIB = {"zh": ("Python 3.12", "标准库"), "en": ("Python 3.12", "standard library")}
FENCE = re.compile(r"^```python\n(.*?)^```$", re.M | re.S)
MARKER = "# exercise: "


def units() -> dict:
    manifest = json.loads((ROOT / "yuyu-book/manifest.json").read_text(encoding="utf-8"))
    found = {}
    for part in manifest["parts"]:
        for unit in part["units"]:
            if unit["id"] in CHAPTERS:
                found[unit["id"]] = {
                    lang: ROOT / unit[lang] for lang in ("zh", "en")
                }
    return found


def blocks(text: str) -> list:
    found = []
    for match in FENCE.finditer(text):
        code = match.group(1)
        if code.startswith(MARKER):
            found.append((code, text[:match.start()].count("\n")))
    return found


def expected(code: str) -> list:
    lines = code.splitlines()
    if not lines or not lines[0].startswith(MARKER):
        raise AssertionError("a case must open with its # exercise marker")
    for index, line in enumerate(lines):
        if not line.startswith("# expected:"):
            continue
        inline = line[len("# expected:"):].strip()
        if inline:
            return [inline]
        wanted = []
        for following in lines[index + 1:]:
            if not following.startswith("# "):
                break
            wanted.append(following[2:].strip())
        return wanted
    raise AssertionError("no # expected: comment above the code")


class Exercises(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.units = units()
        cls.texts = {
            unit: {lang: path.read_text(encoding="utf-8") for lang, path in paths.items()}
            for unit, paths in cls.units.items()
        }

    def test_every_chapter_has_exactly_one_case_in_both_editions(self):
        self.assertEqual(sorted(self.units), CHAPTERS)
        for unit, paths in self.units.items():
            for lang in ("zh", "en"):
                self.assertEqual(len(blocks(self.texts[unit][lang])), 1,
                                 f"{paths[lang].name}: {unit} needs exactly one case")

    def test_both_editions_carry_the_same_code(self):
        for unit in CHAPTERS:
            zh = blocks(self.texts[unit]["zh"])[0][0]
            en = blocks(self.texts[unit]["en"])[0][0]
            self.assertEqual(zh, en, f"{unit}: the two editions run different code")

    def test_the_labels_and_version_lock_sit_above_the_case(self):
        for unit in CHAPTERS:
            for lang in ("zh", "en"):
                text = self.texts[unit][lang]
                code, line = blocks(text)[0]
                above = "\n".join(text.splitlines()[max(0, line - 12):line])
                for label in LABELS[lang]:
                    self.assertIn(label, above,
                                  f"{unit} {lang}: missing {label} above the case")
                for token in STDLIB[lang]:
                    self.assertIn(token, above,
                                  f"{unit} {lang}: the version lock does not name {token}")
                self.assertRegex(above, r"\*\*回链：\*\* \S|\*\*Backlink:\*\* \S",
                                 f"{unit} {lang}: the backlink is empty")

    def test_the_printed_result_is_what_the_reader_is_promised(self):
        env = dict(os.environ, PYTHONIOENCODING="utf-8")
        for unit in CHAPTERS:
            code = blocks(self.texts[unit]["zh"])[0][0]
            want = expected(code)
            self.assertTrue(want, f"{unit}: no expected output")
            run = subprocess.run(
                [sys.executable, "-"], input=code, capture_output=True,
                text=True, encoding="utf-8", errors="replace", env=env, timeout=30,
            )
            self.assertEqual(run.returncode, 0,
                             f"{unit}: case failed\n{run.stderr}")
            self.assertEqual(run.stdout.splitlines(), want,
                             f"{unit}: output drifted from the # expected: comment")
