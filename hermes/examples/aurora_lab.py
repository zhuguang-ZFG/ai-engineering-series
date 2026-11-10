"""Original offline project used throughout the Hermes book.

This is a deliberately small Markdown checker, not a Hermes host emulator.
It supports inline Markdown links and fenced examples, not all CommonMark.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import tempfile
from urllib.parse import unquote, urlsplit

FIXTURE = {
    "docs/index.md": "# Aurora handbook\n\n[Setup](setup.md)\n[Release notes](release-notes.md)\n",
    "docs/setup.md": "# Setup\n\nUse Python and unittest.\n\n```text\nhttps://example.invalid/demo\n```\n",
    "docs/release-notes.md": "# Release notes\n\nThe current runner is unittest.\n",
    "archive/old-plan.md": "# Old plan\n\n[Former setup](removed.md)\nThe old runner was pytest.\n",
}
RULES = {"schema_version": 1, "include_archive": False, "scan_examples": False}
LINK = re.compile(r"\[[^\]\n]*\]\(([^)\s]+)\)")
URL = re.compile(r"https?://[^\s<>`]+")


def atomic_json(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=".aurora-", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(value, stream, ensure_ascii=False, indent=2)
            stream.write("\n")
        os.replace(temporary, path)
    finally:
        Path(temporary).unlink(missing_ok=True)


def initialize(root: Path) -> None:
    if root.exists():
        raise ValueError("Use a new directory; init never overwrites an existing project.")
    root.mkdir(parents=True)
    for name, body in FIXTURE.items():
        path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(body, encoding="utf-8", newline="\n")
    atomic_json(root / "rules.json", RULES)


def linked(path: Path) -> bool:
    return path.is_symlink() or (hasattr(path, "is_junction") and path.is_junction())


def collect(root: Path, include_archive: bool) -> list[Path]:
    paths = []
    for name in ["docs", *(["archive"] if include_archive else [])]:
        directory = root / name
        if linked(directory) or not directory.is_dir():
            raise ValueError(f"Expected a real directory: {name}")
        for current, directories, files in os.walk(directory, followlinks=False):
            directories[:] = sorted(item for item in directories if not linked(Path(current) / item))
            for item in sorted(files):
                path = Path(current) / item
                if path.suffix.lower() == ".md" and not linked(path):
                    paths.append(path)
    return sorted(paths)


def inspect(root: Path) -> dict:
    root = root.absolute()
    if any(linked(path) for path in (root, *root.parents)):
        raise ValueError("Use a root without symlinks or junctions.")
    root = root.resolve(strict=True)
    rules_path = root / "rules.json"
    if linked(rules_path):
        raise ValueError("rules.json must be a regular project file.")
    rules_bytes = rules_path.read_bytes()
    rules = json.loads(rules_bytes)
    if rules.get("schema_version") != 1:
        raise ValueError("Unsupported rules schema.")
    for field in ("include_archive", "scan_examples"):
        if type(rules.get(field)) is not bool:
            raise ValueError(f"{field} must be a JSON boolean.")
    inventory, issues, observations = [], [], []
    for path in collect(root, rules["include_archive"]):
        raw = path.read_bytes()
        relative = path.relative_to(root).as_posix()
        inventory.append({"path": relative, "sha256": hashlib.sha256(raw).hexdigest()})
        fence = None
        for line_number, line in enumerate(raw.decode("utf-8-sig").splitlines(), 1):
            stripped = line.lstrip()
            marker = re.match(r"(`{3,}|~{3,})", stripped)
            if marker:
                token = marker.group(1)
                if fence is None:
                    fence = token
                elif token[0] == fence[0] and len(token) >= len(fence):
                    fence = None
                continue
            if fence:
                if rules["scan_examples"]:
                    for url in URL.findall(line):
                        observations.append({"path": relative, "line": line_number,
                            "kind": "example-url", "value": url,
                            "placeholder": urlsplit(url).hostname == "example.invalid"})
                continue
            for target in LINK.findall(line):
                parsed = urlsplit(target)
                if parsed.scheme or parsed.netloc or not parsed.path:
                    continue
                candidate = path.parent / unquote(parsed.path)
                resolved = candidate.resolve()
                if not resolved.is_relative_to(root):
                    kind = "outside-root"
                elif any(linked(part) for part in (candidate, *candidate.parents)):
                    kind = "linked-target"
                elif not resolved.is_file():
                    kind = "missing-target"
                else:
                    continue
                issues.append({"path": relative, "line": line_number, "kind": kind, "target": target})
    snapshot = {"rules_sha256": hashlib.sha256(rules_bytes).hexdigest(), "files": inventory}
    digest = hashlib.sha256(json.dumps(snapshot, sort_keys=True).encode()).hexdigest()
    return {"schema_version": 1, "input_digest": digest, "snapshot": snapshot,
            "status": "needs-review" if issues else "checked", "issues": issues,
            "observations": observations, "scope": rules}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=["init", "check"])
    parser.add_argument("root", type=Path)
    args = parser.parse_args()
    try:
        if args.action == "init":
            initialize(args.root)
            print("Initialized Aurora fixture")
            return 0
        report = inspect(args.root)
        report_dir = args.root / "reports"
        if linked(report_dir):
            raise ValueError("reports must not be a link.")
        atomic_json(report_dir / "latest.json", report)
        print(json.dumps({key: report[key] for key in ("input_digest", "status", "issues", "observations")},
                         ensure_ascii=False))
        return 1 if report["issues"] else 0
    except (OSError, ValueError) as error:
        print(json.dumps({"error": str(error)}, ensure_ascii=False))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
