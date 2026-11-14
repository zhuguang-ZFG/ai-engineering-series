"""The same gate with the three defects closed.

The comparison is numeric per component; the changelog must carry a section
for the version being released; the test log is accepted only when it both
ends with a success line and reports no failures.
"""
from __future__ import annotations

import re
from pathlib import Path

MINIMUM = (1, 10, 0)
SUCCESS = re.compile(r"^Ran \d+ tests? in .*$", re.M)


def parse_version(text: str) -> tuple[int, ...] | None:
    parts = text.strip().split(".")
    if not parts or any(not p.isdigit() for p in parts):
        return None
    return tuple(int(p) for p in parts)


def version_ok(package_version: str, minimum: tuple[int, ...] = MINIMUM) -> str | None:
    parsed = parse_version(package_version)
    if parsed is None:
        return f"package version {package_version!r} is not numeric"
    if parsed < minimum:
        want = ".".join(str(p) for p in minimum)
        return f"package version {package_version} is below {want}"
    return None


def changelog_ok(changelog: Path, version: str) -> str | None:
    if not changelog.exists():
        return "CHANGELOG.md is missing"
    headings = re.findall(r"^## \[?(\d+\.\d+\.\d+)\]?", changelog.read_text(encoding="utf-8"), re.M)
    if version not in headings:
        return f"CHANGELOG.md has no section for {version}"
    return None


def tests_ok(log: Path) -> str | None:
    if not log.exists():
        return "test log is missing"
    text = log.read_text(encoding="utf-8")
    if "FAILED" in text:
        return "test log reports FAILED"
    if not SUCCESS.search(text):
        return "test log has no summary line"
    return None


def gate(root: Path, version: str) -> list[str]:
    reasons = []
    for reason in (version_ok(version),
                   changelog_ok(root / "CHANGELOG.md", version),
                   tests_ok(root / "tests.log")):
        if reason:
            reasons.append(reason)
    return reasons
