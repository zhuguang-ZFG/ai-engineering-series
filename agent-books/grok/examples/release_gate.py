"""A release gate that looks finished and is not.

Three defects, each visible from a different input:

1. `version_ok` compares version strings by prefix, so 1.10.0 sorts below 1.9.0.
2. `changelog_ok` accepts the file as long as it exists.
3. `tests_ok` looks for "OK" anywhere in the log, including the failure summary.

Every function returns a reason string, so a failing gate can be read the same
way a passing one is.
"""
from __future__ import annotations

from pathlib import Path

REQUIRED_VERSION = "1.10.0"


def version_ok(package_version: str) -> str | None:
    if not package_version:
        return "package version is missing"
    if package_version < REQUIRED_VERSION:
        return f"package version {package_version} is below {REQUIRED_VERSION}"
    return None


def changelog_ok(changelog: Path, version: str) -> str | None:
    if not changelog.exists():
        return "CHANGELOG.md is missing"
    return None


def tests_ok(log: Path) -> str | None:
    if not log.exists():
        return "test log is missing"
    if "OK" not in log.read_text(encoding="utf-8"):
        return "test log does not report OK"
    return None


def gate(root: Path, version: str) -> list[str]:
    reasons = []
    for reason in (version_ok(version),
                   changelog_ok(root / "CHANGELOG.md", version),
                   tests_ok(root / "tests.log")):
        if reason:
            reasons.append(reason)
    return reasons
