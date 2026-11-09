#!/usr/bin/env python3
"""Classify every tracked file under video/ before the factory is rebuilt.

P0.4 asks for an identity list, not a deletion list: each tracked file gets one
of six roles so the later migration knows what may be regenerated and what is
authored material. The categories follow the transformation spec:

    source       authored input: scripts, scene HTML, design/plan docs, specs
    config       project or tool configuration, including lock files
    review       reports, audits and polish notes produced by a review pass
    generated    machine output that a pipeline step can rebuild
    cache        local cache, never a source of truth (none tracked today)
    third_party  credits/licences for assets from elsewhere

    python scripts/video_identity.py
    python scripts/video_identity.py --check

An unknown file fails the run instead of landing in a catch-all bucket; the
inventory is only useful if every row was decided.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "baseline" / "video-identity.json"
CATEGORIES = ("source", "config", "review", "generated", "cache",
              "third_party")

CONFIG_NAMES = {"package.json", "package-lock.json", "hyperframes.json",
                "hyperframes.lock.json", "meta.json", "tsconfig.json"}
SOURCE_NAMES = {"sample-short.txt", "sample-long.txt", "ch01-whiteboard.json"}
VO_CHUNK = re.compile(r"^c\d{3}\.txt$")
REVIEW = re.compile(r"(REPORT|AUDIT|POLISH|REVIEW)", re.I)
SOURCE_DOCS = re.compile(
    r"^(AGENTS|CLAUDE|DESIGN|STORYBOARD|SYNC-MAP|README|LONG-.*-PLAN)\.md$",
    re.I)


def classify(path: str) -> tuple[str, str] | None:
    """(category, reason) for one repo-relative path, or None if undecided."""
    pure = Path(path)
    name = pure.name
    suffix = pure.suffix.lower()
    parts = pure.as_posix().split("/")

    if name == "CREDITS.md":
        return "third_party", "asset credits/licence"
    if REVIEW.search(name):
        return "review", "review artefact"
    if name in CONFIG_NAMES or name.endswith(".lock.json"):
        return "config", "project/tool configuration"
    if parts[:2] == ["video", "chapters"]:
        if suffix in {".yaml", ".yml"}:
            return "source", "chapter pipeline config"
        if name in {"content-pack.json", "compat-report.json"}:
            return "generated", "pipeline output"
        if name.startswith("script-") and suffix in {".md", ".txt"}:
            return "source", "chapter narration script"
    if name in SOURCE_NAMES:
        return "source", "authored narration/visual spec"
    if "huashu-specs" in parts:
        return "source", "authored storyboard spec"
    if suffix == ".py":
        return "source", "authored build script"
    if suffix == ".html":
        return "source", "authored HyperFrames scene/composition"
    if suffix == ".md" and SOURCE_DOCS.match(name):
        return "source", "authored design/plan note"
    if suffix == ".md":
        return None
    if suffix == ".txt":
        if VO_CHUNK.match(name):
            return "source", "narration chunk kept as input (.gitignore)"
        return "generated", "narration slice / concat list"
    if suffix == ".json":
        if name in {"chunks.json", "timeline.json", "transcript.json",
                    "vo-manifest.json", "assemble-meta.json",
                    "sample-meta.json", "short-meta.json", "short-caps.json",
                    "short-sents.json", "short-words.json",
                    "short-scan.json", "voice-render-info.json"}:
            return "generated", "pipeline output"
        return None
    return None


def tracked() -> list[str]:
    out = subprocess.run(["git", "ls-files", "video"], cwd=ROOT, check=True,
                         capture_output=True, text=True).stdout.splitlines()
    return sorted(out)


def build() -> dict:
    files = []
    undecided = []
    for path in tracked():
        result = classify(path)
        if result is None:
            undecided.append(path)
            continue
        category, reason = result
        absolute = ROOT / path
        files.append({
            "path": path,
            "category": category,
            "reason": reason,
            "bytes": absolute.stat().st_size,
            "sha256": hashlib.sha256(absolute.read_bytes()).hexdigest(),
        })
    if undecided:
        print("undecided video files:", file=sys.stderr)
        for path in undecided:
            print("  " + path, file=sys.stderr)
        raise SystemExit(1)
    counts = Counter(row["category"] for row in files)
    return {
        "schema_version": 1,
        "source_commit": subprocess.run(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, check=True,
            capture_output=True, text=True).stdout.strip(),
        "tracked": len(files),
        "counts": {category: counts.get(category, 0) for category in CATEGORIES},
        "files": files,
    }


def dump(data: dict) -> str:
    return json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args(argv)
    data = build()
    text = dump(data)
    if args.check:
        current = json.loads(OUT.read_text(encoding="utf-8"))
        current.pop("source_commit", None)
        data.pop("source_commit", None)
        if dump(current) != dump(data):
            print(f"video identity drift: {OUT}", file=sys.stderr)
            return 1
        print(f"video identity matches {OUT}")
        return 0
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(text, encoding="utf-8", newline="\n")
    print(f"video identity: {data['tracked']} tracked files -> " +
          ", ".join(f"{k} {v}" for k, v in data["counts"].items()))
    return 0


if __name__ == "__main__":
    sys.exit(main())
