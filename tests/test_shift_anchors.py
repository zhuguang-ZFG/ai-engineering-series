"""Anchor arithmetic for a six-line plate: move the pointer, not the prose.

A shift is the one edit that can silently break the plain-language layer, so
the script that does it is pinned here four ways: which refs move, which do
not, that nothing on disk escapes the regex, and that the bytes outside the
digits are untouched.
"""
from __future__ import annotations

import contextlib
import io
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import shift_anchors  # noqa: E402

ZH02 = "第一部分-基础篇/02-对话循环-Agent的心跳.md"
EN02 = "en/Part-1-Foundations/02-The-Dialog-Loop-Heartbeat-of-an-Agent.md"
OTHER = "第一部分-基础篇/03-工具系统-Agent的双手.md"


def doc(*refs: str) -> str:
    return '{\n "a": [\n' + "".join(f'  "{r}",\n' for r in refs) + " ]\n}\r\n"


class ShiftSemantics(unittest.TestCase):
    def test_only_refs_after_the_insert_move(self):
        text = doc(f"{ZH02}:100", f"{ZH02}:289", f"{ZH02}:290", f"{ZH02}:445")
        out, hits = shift_anchors.shift(text, frozenset({ZH02}), 289, 6)
        self.assertEqual([(ZH02, 290, 296), (ZH02, 445, 451)], hits)
        self.assertIn(f'"{ZH02}:100"', out)
        self.assertIn(f'"{ZH02}:289"', out)
        self.assertIn(f'"{ZH02}:296"', out)
        self.assertIn(f'"{ZH02}:451"', out)

    def test_other_files_are_left_alone(self):
        text = doc(f"{OTHER}:400", f"{EN02}:400")
        out, hits = shift_anchors.shift(text, frozenset({ZH02}), 289, 6)
        self.assertEqual([], hits)
        self.assertEqual(text, out)

    def test_both_languages_move_on_the_same_line(self):
        text = doc(f"{ZH02}:300", f"{EN02}:300")
        out, hits = shift_anchors.shift(
            text, frozenset({ZH02, EN02}), 289, 6)
        self.assertEqual(2, len(hits), out)

    def test_every_anchor_on_disk_is_matched(self):
        """If a registry ever stores a pointer the regex cannot see, the
        shift would silently leave it behind."""
        for name in shift_anchors.REGISTRY_NAMES:
            text = (ROOT / "yuyu-book" / name).read_text(encoding="utf-8")
            self.assertEqual(
                text.count(".md:"), len(shift_anchors.REF.findall(text)),
                f"{name}: an anchor the script cannot move")


class PreserveFormatting(unittest.TestCase):
    def test_a_zero_delta_rewrite_is_byte_identical(self):
        for name in shift_anchors.REGISTRY_NAMES:
            text = (ROOT / "yuyu-book" / name).read_text(
                encoding="utf-8", newline="")
            out, hits = shift_anchors.shift(text, frozenset({ZH02}), 0, 0)
            # Delta 0 still routes every anchor past line 0 through the
            # substitution, so this compares real rewritten bytes rather than
            # an untouched string; an empty hits list would mean a no-op test.
            self.assertEqual(text.count(f'"{ZH02}:'), len(hits),
                             f"{name}: an anchor the shift did not route")
            self.assertEqual(text, out, f"{name}: formatting drifted")

    def test_crlf_survives_a_write(self):
        src = ROOT / "yuyu-book" / shift_anchors.REGISTRY_NAMES[0]
        text = src.read_text(encoding="utf-8", newline="")
        self.assertIn("\r\n", text, "the fixture assumed CRLF registries")

    def test_the_cli_without_write_leaves_the_bytes_alone(self):
        """The default is a plan, not an edit; Task 3 leans on that before it
        is ever pointed at --write. Run it against a scratch copy, so being
        wrong about the default costs a test rather than the registries."""
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            book = root / "yuyu-book"
            book.mkdir()
            blobs = {name: (ROOT / "yuyu-book" / name).read_bytes()
                     for name in shift_anchors.REGISTRY_NAMES}
            for name, blob in blobs.items():
                (book / name).write_bytes(blob)
            for rel in (ZH02, EN02):
                prose = root / rel
                prose.parent.mkdir(parents=True, exist_ok=True)
                prose.write_text("x\n", encoding="utf-8")

            saved = shift_anchors.ROOT
            shift_anchors.ROOT = root
            out = io.StringIO()
            try:
                with contextlib.redirect_stdout(out):
                    code = shift_anchors.main(
                        ["--after", "289", "--delta", "6", ZH02, EN02])
            finally:
                shift_anchors.ROOT = saved

            self.assertEqual(0, code, out.getvalue())
            plan = out.getvalue().splitlines()
            self.assertNotIn("written:", "\n".join(plan))
            self.assertEqual(
                f"planned: {sum(' -> ' in ln for ln in plan)} anchors",
                plan[-1], "the summary line disagrees with the plan it prints")
            for name, blob in blobs.items():
                self.assertEqual(
                    blob, (book / name).read_bytes(),
                    f"{name}: a dry run wrote to disk")
