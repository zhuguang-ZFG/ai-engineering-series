"""Stable block markers carried by the manuscript itself.

A citable block gets one HTML comment on its own line directly above it:

    <!-- block: ch03.tool-contract -->

The comment is invisible in the book, survives reflow and insertion, and keeps
the ID next to the prose it names. IDs are unit-scoped (`<unit-id>.<slug>`),
unique per unit, and shared by the Chinese and English editions so a registry
entry can name one block in both languages. A marker inside a code fence is an
example, not a marker; only prose counts.

This module validates the markers now. The line-ref → block-ref migration and
the block-boundary parser arrive in P2.4; both use `validate_markers()` to find
the IDs that already exist.
"""
from __future__ import annotations

import re

from .core import FENCE_RE, BuildError
from .model import Diagnostic

MARKER = re.compile(
    r"^\s*<!--\s*block:\s*(?P<id>[a-z0-9][a-z0-9.-]*)\s*-->\s*$")
LOOSE = re.compile(r"<!--\s*block\b", re.I)
ID_RE = re.compile(r"^[a-z][a-z0-9]*\.[a-z0-9]+(?:-[a-z0-9]+)*$")


def _fail(code: str, file: str, block_id: str, message: str,
          hint: str = "") -> None:
    raise BuildError(str(Diagnostic("error", code, file, block_id, message,
                                    hint)))


def _fence_token(line: str):
    match = FENCE_RE.match(line)
    if not match:
        return None
    token, info = match.group(1), match.group(2).strip()
    return token, info


def validate_markers(text: str, file: str, unit_id: str) -> dict[str, int]:
    """Return {block_id: marker line} and fail on a malformed or dangling one."""
    lines = text.split("\n")
    found: dict[str, int] = {}
    fence = None
    for number, line in enumerate(lines, 1):
        token = _fence_token(line)
        if token:
            mark, info = token
            if fence is None:
                fence = mark
            elif mark[0] == fence[0] and len(mark) >= len(fence) and not info:
                fence = None
            continue
        if fence is not None or not LOOSE.search(line):
            continue
        match = MARKER.match(line)
        if not match:
            _fail("block-marker", file, "",
                  f"malformed block marker on line {number}",
                  "use <!-- block: <unit-id>.<slug> --> on a line of its own")
        block_id = match.group("id")
        if not block_id.startswith(f"{unit_id}.") or not ID_RE.match(block_id):
            _fail("block-id", file, block_id,
                  f"block id on line {number} does not belong to {unit_id}",
                  f"expected {unit_id}.<lowercase-slug>")
        if block_id in found:
            _fail("block-id", file, block_id,
                  f"duplicate block id (lines {found[block_id]} and {number})")
        next_line = number
        while next_line < len(lines) and not lines[next_line].strip():
            next_line += 1
        if next_line >= len(lines):
            _fail("block-marker", file, block_id,
                  "block marker is not followed by a block")
        if LOOSE.search(lines[next_line]):
            _fail("block-marker", file, block_id,
                  "two block markers point at the same block")
        found[block_id] = number
    return found
