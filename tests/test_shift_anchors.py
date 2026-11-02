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


def eol_of(text: str) -> str | None:
    """The one line terminator a file uses, or None when it mixes them.

    Counting CRLF against LF is not enough: a write without newline="" turns
    every CRLF into CR-CRLF, which still has one LF and one CRLF per line yet
    is exactly the whole-file byte change the module docstring warns about.
    """
    crlf, lf, cr = text.count("\r\n"), text.count("\n"), text.count("\r")
    if crlf and crlf == lf == cr:
        return "\r\n"
    if lf and not crlf and not cr:
        return "\n"
    return None


def stage_scratch_repo(root: Path) -> dict[str, bytes]:
    """Copy the real registries into a scratch repo and stand up the prose
    files the CLI insists on, returning the pristine bytes. Both CLI tests
    write through this, so being wrong costs a tempfile, never the checkout."""
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
    return blobs


def run_cli(root: Path, argv: list[str]) -> tuple[int, list[str]]:
    """main() with the module's repo root pointed at `root` and its stdout
    captured; ROOT is restored even when the call raises."""
    saved = shift_anchors.ROOT
    shift_anchors.ROOT = root
    out = io.StringIO()
    try:
        with contextlib.redirect_stdout(out):
            code = shift_anchors.main(argv)
    finally:
        shift_anchors.ROOT = saved
    return code, out.getvalue().splitlines()


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

    def test_line_endings_on_disk_are_consistent(self):
        """These registries are CRLF in a Windows working copy and LF in a
        Linux checkout (the blobs are LF; autocrlf does the rest). Either way
        the splice must not mix them, or "only the digits change" is a lie."""
        for name in shift_anchors.REGISTRY_NAMES:
            text = (ROOT / "yuyu-book" / name).read_text(
                encoding="utf-8", newline="")
            crlf = text.count("\r\n")
            self.assertTrue(crlf == 0 or crlf == text.count("\n"),
                            f"{name}: mixed line endings on disk")

    def test_the_cli_without_write_leaves_the_bytes_alone(self):
        """The default is a plan, not an edit; Task 3 leans on that before it
        is ever pointed at --write. Run it against a scratch copy, so being
        wrong about the default costs a test rather than the registries."""
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            blobs = stage_scratch_repo(root)
            code, plan = run_cli(
                root, ["--after", "289", "--delta", "6", ZH02, EN02])

            self.assertEqual(0, code, "\n".join(plan))
            self.assertNotIn("written:", "\n".join(plan))
            # The printed total is not evidence on its own: counted from the
            # very lines it summarizes it reads 0 == 0 once the path filter
            # matches nothing, so the floor and both registry prefixes are
            # pinned against the plan lines instead.
            self.assertGreater(len(plan), 1, f"just a summary line: {plan}")
            moved = [ln for ln in plan if " -> " in ln]
            self.assertGreater(len(moved), 0, f"no anchor in the plan: {plan}")
            for name in shift_anchors.REGISTRY_NAMES:
                self.assertTrue(
                    any(ln.startswith(f"{name}: ") for ln in moved),
                    f"{name}: nothing of it planned")
            self.assertEqual(
                f"planned: {len(moved)} anchors", plan[-1],
                "the summary line disagrees with the plan it prints")
            for name, blob in blobs.items():
                self.assertEqual(
                    blob, (root / "yuyu-book" / name).read_bytes(),
                    f"{name}: a dry run wrote to disk")

    def test_the_cli_with_write_moves_only_the_digits(self):
        """--write is the half a dry run cannot reach: what lands on disk has
        to keep the registry's own line endings and change nothing but the
        anchored numbers, or a six-line plate arrives as a whole-file diff.
        Scratch copy again, so a wrong write costs a tempfile."""
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            blobs = stage_scratch_repo(root)
            code, plan = run_cli(
                root, ["--after", "289", "--delta", "6", "--write",
                       ZH02, EN02])

            self.assertEqual(0, code, "\n".join(plan))
            self.assertRegex(plan[-1], r"^written: [1-9]\d* anchors$",
                             f"--write reported {plan[-3:]}")
            moved = [ln for ln in plan if " -> " in ln]
            self.assertEqual(
                int(plan[-1].split(": ")[1].split()[0]), len(moved),
                "the summary line disagrees with the plan it printed")

            for name, blob in blobs.items():
                old = blob.decode("utf-8")
                new = (root / "yuyu-book" / name).read_text(
                    encoding="utf-8", newline="")
                self.assertIsNotNone(
                    eol_of(new), f"{name}: --write mixed the line endings")
                self.assertEqual(
                    eol_of(old), eol_of(new),
                    f"{name}: --write swapped the line endings, so every "
                    "line reads as changed")
                self.assertEqual(
                    len(old.split("\n")), len(new.split("\n")),
                    f"{name}: --write added or dropped lines")

                touched = [ln for ln in moved if ln.startswith(f"{name}: ")]
                self.assertGreater(
                    len(touched), 0, f"{name}: --write left its anchors alone")
                diff = [(a, b) for a, b in zip(old.split("\n"),
                                               new.split("\n")) if a != b]
                self.assertEqual(
                    len(touched), len(diff),
                    f"{name}: {len(diff)} lines moved but {len(touched)} "
                    "were planned")
                for (before, after), entry in zip(diff, touched):
                    src, dst = entry.split(": ", 1)[1].split(" -> ")
                    rel, frm = src.rsplit(":", 1)
                    expect = before.replace(f'"{rel}:{frm}"', f'"{rel}:{dst}"')
                    self.assertEqual(
                        after, expect, f"{name}: an edit outside the digits "
                        f"of {rel}:{frm}")
