"""Validate a release's declared files without executing its startup command."""
import argparse
import hashlib
import json
import re
from pathlib import Path, PurePosixPath, PureWindowsPath

REQUIRED = ("release.json", "requirements.lock", "runbook.md", "user-guide.md")


def contained_path(root, relative):
    if not isinstance(relative, str) or not relative or "\\" in relative:
        raise ValueError("use a non-empty relative path with / separators")
    path = PurePosixPath(relative)
    if path.is_absolute() or PureWindowsPath(relative).drive or ".." in path.parts or ":" in relative:
        raise ValueError("path must stay inside the release directory")
    target = (root / relative).resolve()
    if not target.is_relative_to(root) or target == root:
        raise ValueError("path or symbolic link leaves the release directory")
    return target


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def check_package(directory, manifest_name="release.json"):
    root = Path(directory).resolve()
    problems = []
    checked = 0
    try:
        manifest_path = contained_path(root, manifest_name)
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, ValueError, RuntimeError) as error:
        return {"status": "failed", "files_checked": 0, "problems": [f"cannot read manifest: {error}"]}
    if not isinstance(manifest, dict):
        return {"status": "failed", "files_checked": 0, "problems": ["manifest must be an object"]}
    for name in REQUIRED:
        try:
            if not contained_path(root, name).is_file():
                problems.append(f"missing required file: {name}")
        except (OSError, ValueError, RuntimeError) as error:
            problems.append(f"invalid required file {name}: {error}")
    for key in ("release", "created", "scope", "start", "health"):
        value = manifest.get(key)
        if not isinstance(value, str) or not value.strip():
            problems.append(f"manifest requires non-empty string: {key}")
    files = manifest.get("files")
    if not isinstance(files, dict) or not files:
        problems.append("files must be a non-empty object of relative paths and SHA-256 digests")
        files = {}
    for name in REQUIRED[1:]:
        if name not in files:
            problems.append(f"required file missing from hash list: {name}")
    for name, expected in files.items():
        try:
            target = contained_path(root, name)
            if target == manifest_path:
                raise ValueError("manifest cannot contain its own hash")
            if not isinstance(expected, str) or not re.fullmatch(r"[0-9a-fA-F]{64}", expected):
                raise ValueError("expected a 64-character SHA-256 digest")
            actual = sha256(target)
            checked += 1
            if actual != expected.lower():
                problems.append(f"hash mismatch: {name}")
        except (OSError, ValueError, RuntimeError) as error:
            problems.append(f"cannot verify {name}: {error}")
    return {"status": "failed" if problems else "ok", "files_checked": checked, "problems": problems}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("package", help="release directory")
    parser.add_argument("--manifest", default="release.json")
    args = parser.parse_args()
    result = check_package(args.package, args.manifest)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["status"] == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())
