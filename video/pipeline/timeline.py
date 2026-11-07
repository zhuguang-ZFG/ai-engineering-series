"""Scene timelines come from `scenes.yaml`; the legacy `index.html` is only a
witness. The compatibility report compares the two so ch01-ch05 can be reviewed
before the old projects are retired.
"""
from __future__ import annotations

import re
from pathlib import Path

from .model import VideoError

ROOT_DIV = re.compile(
    r'<div id="root"[^>]*data-duration="([\d.]+)"[^>]*'
    r'data-width="(\d+)"[^>]*data-height="(\d+)"[^>]*data-fps="(\d+)"')
CLIP = re.compile(r"<div class=\"clip\"([^>]*)>")
ATTR = re.compile(r'data-([a-z-]+)="([^"]*)"')
AUDIO = re.compile(r"<audio[^>]*>")
TAG_ATTR = re.compile(r'([a-z-]+)="([^"]*)"')


def parse_index(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    root = ROOT_DIV.search(text)
    if not root:
        raise VideoError(f"{path}: cannot read the composition root")
    duration, width, height, fps = root.groups()
    scenes = []
    for match in CLIP.finditer(text):
        attrs = dict(ATTR.findall(match.group(1)))
        if attrs.get("track-index") != "1":
            continue
        scenes.append({
            "id": attrs.get("composition-id", ""),
            "source": attrs.get("composition-src", ""),
            "start_s": round(float(attrs.get("start", 0)), 3),
            "duration_s": round(float(attrs.get("duration", 0)), 3),
        })
    scenes.sort(key=lambda scene: scene["start_s"])
    audio = {"path": "", "duration_s": 0.0}
    for match in AUDIO.finditer(text):
        attrs = dict(TAG_ATTR.findall(match.group(0)))
        if attrs.get("data-duration"):
            audio = {
                "path": attrs.get("src", ""),
                "duration_s": round(float(attrs["data-duration"]), 3),
            }
            break
    return {
        "width": int(width),
        "height": int(height),
        "fps": int(fps),
        "duration_s": round(float(duration), 3),
        "scenes": scenes,
        "audio": audio,
    }


def compat(episode: dict, chapter_dir: Path, scenes: dict) -> dict:
    legacy = episode.get("legacy") or {}
    if not legacy.get("dir"):
        return {"chapter": chapter_dir.name, "formats": {}}
    base = chapter_dir / legacy["dir"]
    report = {"chapter": chapter_dir.name, "formats": {}}
    for fmt in ("long", "short"):
        name = legacy.get(f"{fmt}_index")
        if not name:
            continue
        path = base / name
        if not path.is_file():
            report["formats"][fmt] = {
                "index": str(path.relative_to(chapter_dir)).replace("\\", "/"),
                "match": False,
                "mismatches": ["legacy index is missing"],
            }
            continue
        old = parse_index(path)
        spec = episode["formats"][fmt]
        new_scenes = (scenes.get("formats") or {}).get(fmt) or []
        mismatches = []
        if (old["width"], old["height"]) != (spec["width"], spec["height"]):
            mismatches.append(
                f"size {old['width']}x{old['height']} != "
                f"{spec['width']}x{spec['height']}")
        if old["fps"] != spec["fps"]:
            mismatches.append(f"fps {old['fps']} != {spec['fps']}")
        if abs(old["duration_s"] - spec["duration_s"]) > 0.1:
            mismatches.append(
                f"duration {old['duration_s']} != {spec['duration_s']}")
        if len(old["scenes"]) != len(new_scenes):
            mismatches.append(
                f"{len(old['scenes'])} legacy scenes != {len(new_scenes)}")
        for index, (before, after) in enumerate(zip(old["scenes"],
                                                     new_scenes)):
            if before["id"] != after["id"]:
                mismatches.append(
                    f"scene {index}: id {before['id']} != {after['id']}")
            for field in ("start_s", "duration_s"):
                if abs(before[field] - after.get(field, 0)) > 0.01:
                    mismatches.append(
                        f"scene {index}: {field} {before[field]} != "
                        f"{after.get(field)}")
            if before["source"] != after.get("source"):
                mismatches.append(
                    f"scene {index}: source {before['source']} != "
                    f"{after.get('source')}")
        old_audio = (scenes.get("audio") or {}).get(fmt) or {}
        if old["audio"]["path"] and old_audio.get("path"):
            if Path(old["audio"]["path"]).name != Path(
                    old_audio["path"]).name:
                mismatches.append(
                    f"audio {old['audio']['path']} != {old_audio['path']}")
            if abs(old["audio"]["duration_s"]
                   - old_audio.get("duration_s", 0)) > 0.01:
                mismatches.append(
                    f"audio duration {old['audio']['duration_s']} != "
                    f"{old_audio.get('duration_s')}")
        report["formats"][fmt] = {
            "index": str(path.relative_to(chapter_dir)).replace("\\", "/"),
            "match": not mismatches,
            "mismatches": mismatches,
        }
    return report


def build(episode: dict, scenes: dict, cues: dict) -> dict:
    formats = {}
    for fmt, spec in episode["formats"].items():
        items = (scenes.get("formats") or {}).get(fmt) or []
        track = cues.get(fmt) or []
        formats[fmt] = {
            "status": spec["status"],
            "width": spec["width"],
            "height": spec["height"],
            "fps": spec["fps"],
            "duration_s": spec["duration_s"],
            "audio": (scenes.get("audio") or {}).get(fmt),
            "scenes": items,
            "captions": {
                "count": len(track),
                "first_start": track[0]["start"] if track else None,
                "last_end": track[-1]["end"] if track else None,
            },
        }
    return {
        "schema_version": 1,
        "chapter": episode["id"],
        "formats": formats,
    }
