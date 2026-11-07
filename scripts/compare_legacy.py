#!/usr/bin/env python3
"""Compare the frozen legacy structure report with a fresh v2 build.

P3.7 of the total-transformation plan: a module split is only finished when the
assembled book still has the shape the pre-platform builder produced. The
legacy side is ``docs/baseline/baseline.json`` (the P0 capture of the tagged
builder); the v2 side is rebuilt from ``yuyu-book/dist``. Content edits after
the capture are allowlisted by path and delta in
``docs/baseline/legacy-v2-deltas.json``; any other difference fails the gate.

    python scripts/compare_legacy.py
    python scripts/compare_legacy.py --report docs/migrations/legacy-v2-structure.md

Exit codes: 0 all differences accounted for, 1 unexpected drift, 2 inputs
missing. The command reads artifacts; it does not build them.
"""
from __future__ import annotations

import argparse
import json
import math
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_BASELINE = ROOT / "docs" / "baseline" / "baseline.json"
DEFAULT_ALLOW = ROOT / "docs" / "baseline" / "legacy-v2-deltas.json"
DEFAULT_REPORT = ROOT / "docs" / "migrations" / "legacy-v2-structure.md"

sys.path.insert(0, str(ROOT / "scripts"))
import baseline  # noqa: E402


def load_rules(path: Path) -> list[dict]:
    """Load constrained delta/exact rules backed by locally available commits."""
    data = json.loads(path.read_text(encoding="utf-8"))
    if (not isinstance(data, dict)
            or type(data.get("schema_version")) is not int
            or data["schema_version"] != 1):
        raise ValueError(f"{path}: schema_version must be 1")
    rules = data.get("deltas")
    if not isinstance(rules, list) or not rules:
        raise ValueError(f"{path}: deltas must be a non-empty array")
    verified_commits = set()
    for index, rule in enumerate(rules):
        location = f"{path}: deltas[{index}]"
        if not isinstance(rule, dict):
            raise ValueError(f"{location}: rule must be an object")
        rule_path = rule.get("path")
        if not isinstance(rule_path, str) or not rule_path.startswith("/"):
            raise ValueError(f"{location}: path must start with /")
        reason = rule.get("reason")
        if not isinstance(reason, str) or not reason.strip():
            raise ValueError(f"{location}: reason must be non-empty")
        if rule.get("kind", "value") not in ("value", "len"):
            raise ValueError(f"{location}: kind must be value or len")
        if "delta" in rule:
            if "legacy" in rule or "fresh" in rule:
                raise ValueError(f"{location}: use either delta or an exact pair")
            delta = rule["delta"]
            if (type(delta) not in (int, float)
                    or isinstance(delta, float) and not math.isfinite(delta)):
                raise ValueError(f"{location}: delta must be a finite number")
        elif "legacy" not in rule or "fresh" not in rule:
            raise ValueError(f"{location}: exact rules need both legacy and fresh")
        commit = rule.get("commit")
        if not isinstance(commit, str) or not re.fullmatch(r"[0-9a-f]{7,40}", commit):
            raise ValueError(f"{location}: commit must be a 7-40 character SHA")
        if commit not in verified_commits:
            resolved = subprocess.run(
                ["git", "cat-file", "-e", f"{commit}^{{commit}}"], cwd=ROOT,
                capture_output=True, text=True)
            if resolved.returncode:
                raise ValueError(
                    f"{location}: commit {commit} is unavailable; fetch its history")
            verified_commits.add(commit)
    return rules


@dataclass(frozen=True)
class Diff:
    path: str
    kind: str          # value | len | added | removed
    legacy: object
    fresh: object

    def describe(self) -> str:
        if self.kind == "len":
            return f"length {self.legacy} -> {self.fresh}"
        if self.kind == "added":
            return f"added {short(self.fresh)}"
        if self.kind == "removed":
            return f"removed {short(self.legacy)}"
        return f"{short(self.legacy)} -> {short(self.fresh)}"


def short(value: object) -> str:
    text = repr(value)
    return text if len(text) <= 80 else text[:77] + "..."


def _pattern_regex(pattern: str) -> re.Pattern:
    parts = []
    for token in re.split(r"(\*|\[\*\])", pattern):
        if token == "*":
            parts.append("[^/]+")
        elif token == "[*]":
            parts.append(r"\[\d+\]")
        else:
            parts.append(re.escape(token))
    return re.compile("^" + "".join(parts) + "$")


def diff_reports(legacy: dict, fresh: dict, path: str = "") -> list[Diff]:
    """Every structural leaf that moved, with the path a rule can name."""
    if type(legacy) is not type(fresh):
        return [Diff(path, "value", type(legacy).__name__,
                     type(fresh).__name__)]
    if isinstance(legacy, dict):
        diffs = []
        for key in sorted(set(legacy) | set(fresh)):
            child = f"{path}/{key}"
            if key not in legacy:
                diffs.append(Diff(child, "added", None, fresh[key]))
            elif key not in fresh:
                diffs.append(Diff(child, "removed", legacy[key], None))
            else:
                diffs.extend(diff_reports(legacy[key], fresh[key], child))
        return diffs
    if isinstance(legacy, list):
        if len(legacy) != len(fresh):
            return [Diff(path, "len", len(legacy), len(fresh))]
        diffs = []
        for index, (old, new) in enumerate(zip(legacy, fresh)):
            diffs.extend(diff_reports(old, new, f"{path}[{index}]"))
        return diffs
    return [] if legacy == fresh else [Diff(path, "value", legacy, fresh)]


def rule_matches(rule: dict, diff: Diff) -> bool:
    if rule.get("kind", "value") != diff.kind:
        return False
    if not _pattern_regex(rule["path"]).match(diff.path):
        return False
    if "delta" in rule:
        if not isinstance(diff.legacy, (int, float)):
            return False
        return diff.fresh - diff.legacy == rule["delta"]
    if "legacy" in rule and rule["legacy"] != diff.legacy:
        return False
    if "fresh" in rule and rule["fresh"] != diff.fresh:
        return False
    return True


def classify(diffs: list[Diff], rules: list[dict]) -> tuple[list, list]:
    matched, unmatched = [], []
    for diff in diffs:
        rule = next((r for r in rules if rule_matches(r, diff)), None)
        (matched if rule else unmatched).append((diff, rule))
    return matched, unmatched


def git_head() -> str:
    try:
        return subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=ROOT,
                              check=True, capture_output=True, text=True).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return "unknown"


def render_report(legacy_meta: dict, matched: list, unmatched: list,
                  allow_path: Path) -> str:
    lines = [
        "# Legacy / v2 structural comparison (P3.7)",
        "",
        f"- Legacy report: `docs/baseline/baseline.json` "
        f"(source commit `{legacy_meta.get('source_commit')}`)",
        f"- v2 report: fresh from `yuyu-book/dist` at `{git_head()}`",
        f"- Allowlist: `{allow_path.relative_to(ROOT).as_posix()}`",
        "",
        "Only structural leaves are compared: bytes, hashes, source line "
        "counts and figure hash values are provenance, not shape.",
        "",
        "## Allowlisted content deltas",
        "",
    ]
    if matched:
        lines += ["| Path pattern | Delta | Reason | Commit |", "|---|---:|---|---|"]
        seen = set()
        for _diff, rule in matched:
            key = (rule["path"], rule.get("delta"), rule.get("reason"))
            if key in seen:
                continue
            seen.add(key)
            delta = rule.get("delta")
            lines.append(
                f"| `{rule['path']}` | {delta if delta is not None else '-'} | "
                f"{rule.get('reason', '')} | `{rule.get('commit', '-')}` |")
    else:
        lines.append("None.")
    lines += ["", "## Unexpected drift", ""]
    if unmatched:
        lines += ["| Path | Change |", "|---|---|"]
        for diff, _rule in unmatched:
            lines.append(f"| `{diff.path}` | {diff.describe()} |")
    else:
        lines.append("None.")
    lines += [
        "",
        "## Verdict",
        "",
        ("GREEN: every structural difference is a declared content delta; the "
         "P3 module split changed no structure."
         if not unmatched else
         f"RED: {len(unmatched)} structural difference(s) are not accounted for."),
        "",
    ]
    return "\n".join(lines)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--baseline", type=Path, default=DEFAULT_BASELINE)
    ap.add_argument("--dist", type=Path, default=baseline.DEFAULT_DIST)
    ap.add_argument("--allow", type=Path, default=DEFAULT_ALLOW)
    ap.add_argument("--report", type=Path, default=None,
                    help=f"write the Markdown report (suggested: {DEFAULT_REPORT})")
    args = ap.parse_args(argv)

    for path in (args.baseline, args.allow):
        if not path.exists():
            print(f"missing {path}", file=sys.stderr)
            return 2
    try:
        rules = load_rules(args.allow)
    except (OSError, ValueError) as exc:
        print(f"invalid comparison rules: {exc}", file=sys.stderr)
        return 2
    html = args.dist / "yuyu-agent-harness-zh.html"
    if not html.exists():
        print(f"missing build artifacts under {args.dist}; build first",
              file=sys.stderr)
        return 2

    legacy_raw = json.loads(args.baseline.read_text(encoding="utf-8"))
    fresh_raw = baseline.build_baseline(args.dist)
    legacy = baseline.normalized(legacy_raw)
    fresh = baseline.normalized(fresh_raw)
    diffs = diff_reports(legacy, fresh)
    matched, unmatched = classify(diffs, rules)

    print(f"structural differences: {len(diffs)} "
          f"({len(matched)} allowlisted, {len(unmatched)} unexpected)")
    for diff, rule in unmatched:
        print(f"  DRIFT {diff.path}: {diff.describe()}", file=sys.stderr)

    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(
            render_report(legacy_raw, matched, unmatched, args.allow),
            encoding="utf-8", newline="\n")
        print(f"report: {args.report}")

    if unmatched:
        return 1
    print("legacy/v2 structure: GREEN")
    return 0


if __name__ == "__main__":
    sys.exit(main())
