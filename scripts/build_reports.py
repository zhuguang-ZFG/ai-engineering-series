"""Machine-readable build evidence; unavailable measurements stay explicit."""
from __future__ import annotations

import hashlib
import json
import os
import platform
import shutil
import subprocess
import sys
from importlib.metadata import distributions
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def digest(path: Path) -> str:
    checksum = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            checksum.update(block)
    return checksum.hexdigest()


def command(args: list[str]) -> str | None:
    try:
        result = subprocess.run(args, cwd=ROOT, capture_output=True,
                                text=True, encoding="utf-8", errors="replace",
                                timeout=30, check=True)
        return result.stdout.strip()
    except (OSError, subprocess.SubprocessError):
        return None


def write_reports(out: Path, steps: list[dict], artifacts=(), *,
                  warnings: list[str] | None = None) -> dict:
    out.mkdir(parents=True, exist_ok=True)
    dependencies = {dist.metadata["Name"]: dist.version for dist in distributions()
                    if dist.metadata["Name"]}
    locks = {name: digest(ROOT / name) for name in
             ("uv.lock", "package-lock.json", "video/package-lock.json")
             if (ROOT / name).is_file()}
    font = None
    browser = None
    try:
        sys.path.insert(0, str(ROOT / "yuyu-book"))
        from yuyu_book.pdf import CJK_FONTS, _launch
        for candidate in CJK_FONTS:
            path = Path(candidate)
            if path.is_file():
                font = {"path": str(path), "sha256": digest(path)}
                break
        from playwright.sync_api import sync_playwright
        with sync_playwright() as playwright:
            launched = _launch(playwright, None)
            browser = launched.version
            launched.close()
    except Exception as exc:
        browser = {"status": "unverified", "reason": str(exc)}
    files = []
    for path in sorted({Path(path).resolve() for path in artifacts}):
        if not path.is_file() or path.name in {"build-report.json", "artifact-manifest.json"}:
            continue
        name = path.relative_to(out.resolve()).as_posix() if path.is_relative_to(out.resolve()) else str(path)
        files.append({"path": name, "bytes": path.stat().st_size, "sha256": digest(path)})
    version = json.loads((ROOT / "yuyu-book/manifest.json").read_text(encoding="utf-8"))["version"]
    identity = {"schema_version": 1, "version": version,
                "commit": command(["git", "rev-parse", "HEAD"]),
                "working_tree": command(["git", "status", "--porcelain=v1", "--untracked-files=normal"]),
                "platform": platform.platform(), "python": platform.python_version(),
                "node": command([shutil.which("node") or "node", "--version"]),
                "browser": browser, "font": font, "dependencies": dependencies,
                "locks_sha256": locks,
                "cache_observations": {key: os.environ.get(key) for key in
                                       ("YUYU_NPM_CACHE_HIT", "YUYU_PYTHON_CACHE_HIT",
                                        "YUYU_BROWSER_CACHE_HIT", "YUYU_FONT_CACHE_HIT")}}
    manifest = {**identity, "artifacts": files}
    report = {"schema_version": 1, "version": version, "commit": identity["commit"],
              "status": "passed" if steps and all(step["returncode"] == 0 for step in steps) else "failed",
              "steps": steps, "warnings": warnings or [],
              "elapsed_seconds": round(sum(step.get("seconds", 0) for step in steps), 3),
              "unverified": ["operator-configured verification is reported separately",
                             "cache hits not supplied by the operator are unmeasured"]}
    for name, payload in (("build-report.json", report), ("artifact-manifest.json", manifest)):
        (out / name).write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return report
