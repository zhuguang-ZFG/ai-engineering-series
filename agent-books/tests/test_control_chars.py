from __future__ import annotations

import re
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TEXT_SUFFIXES = {".md", ".txt", ".json", ".py", ".mjs", ".js", ".html", ".css", ".yml", ".yaml"}
# Tab (09), LF (0a) and CR (0d) are layout, not damage; the rest are bytes a
# shell or a Python string literal dropped on the way in.
CONTROL = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f]")


def tracked_text_files():
    listing = subprocess.run(["git", "ls-files"], cwd=ROOT, capture_output=True,
                             text=True, check=True).stdout.splitlines()
    return [rel for rel in listing
            if Path(rel).suffix in TEXT_SUFFIXES and (ROOT / rel).is_file()]


class ControlCharacters(unittest.TestCase):
    def test_the_pattern_catches_the_byte_that_ate_a_letter(self):
        # "\video/ch01" through a shell that honours escapes comes out as
        # 0x0b + "ideo/ch01": the path loses its first letter and stays quiet.
        self.assertEqual(CONTROL.findall("see \x0bideo/ch01/out.ah\x07ssets"),
                         ["\x0b", "\x07"])
        self.assertEqual(CONTROL.findall("plain 文本\tindent\rcrlf"), [])

    def test_no_tracked_text_file_hides_a_control_character(self):
        offenders = []
        for rel in tracked_text_files():
            hits = sorted({hex(ord(c)) for c in CONTROL.findall(
                (ROOT / rel).read_bytes().decode("utf-8", "replace"))})
            if hits:
                offenders.append(f"{rel}: {hits}")
        self.assertEqual(offenders, [],
                         "these bytes break the paths and hashes they sit in")


if __name__ == "__main__":
    unittest.main()
