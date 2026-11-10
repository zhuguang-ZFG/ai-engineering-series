"""Scene timelines come from `scenes.yaml`; the legacy `index.html` is only a
witness. The compatibility report compares the two so ch01-ch05 can be reviewed
before the old projects are retired.

Legacy captions and rendered keyframes are compared through separate entry
points: no SRT/VTT or mp4 evidence is committed today, so `compat()` must not
store an unverified field that would make the committed reports stale.
"""
from __future__ import annotations

import hashlib
import math
import re
import subprocess
from pathlib import Path

from .model import VideoError, format_base
from .voice import normalized

ROOT_DIV = re.compile(
    r'<div id="root"[^>]*data-duration="([\d.]+)"[^>]*'
    r'data-width="(\d+)"[^>]*data-height="(\d+)"[^>]*data-fps="(\d+)"')
CLIP = re.compile(r"<div class=\"clip\"([^>]*)>")
ATTR = re.compile(r'data-([a-z-]+)="([^"]*)"')
AUDIO = re.compile(r"<audio[^>]*>")
TAG_ATTR = re.compile(r'([a-z-]+)="([^"]*)"')
CAPTION_TIME = re.compile(
    r"^\s*(?:(\d+):)?(\d{1,2}):(\d{1,2})[.,](\d{1,3})\s*-->\s*"
    r"(?:(\d+):)?(\d{1,2}):(\d{1,2})[.,](\d{1,3})")
CAPTION_SUFFIXES = (".srt", ".vtt")
CAPTION_TOLERANCE_S = 0.25
KEYFRAME_POINTS = (0.1, 0.5, 0.9)
VIDEO_DURATION_TOLERANCE_S = 0.1


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


def _seconds(hours, minutes, seconds, fraction) -> float:
    return round(int(hours or 0) * 3600 + int(minutes) * 60 + int(seconds)
                 + int(fraction.ljust(3, "0")) / 1000, 3)


def parse_captions(path: Path) -> list[dict]:
    """Read SRT or VTT cues. ASS is not parsed; callers stay unverified."""
    text = path.read_text(encoding="utf-8-sig", errors="replace")
    cues: list[dict] = []
    current = None
    body: list[str] = []

    def flush() -> None:
        nonlocal current, body
        if current is not None:
            cue_text = "\n".join(body).strip()
            if cue_text:
                current["text"] = cue_text
                cues.append(current)
        current = None
        body = []

    for line in text.splitlines():
        match = CAPTION_TIME.match(line)
        if match:
            flush()
            groups = match.groups()
            current = {"start": _seconds(*groups[:4]),
                       "end": _seconds(*groups[4:])}
        elif current is not None:
            if line.strip():
                body.append(line)
            else:
                flush()
    flush()
    return cues


def legacy_caption_path(episode: dict, chapter_dir: Path,
                        fmt: str) -> Path | None:
    base = format_base(chapter_dir, episode.get("legacy") or {}, fmt)
    if base is None or not base.is_dir():
        return None
    candidates = sorted(
        path for path in base.iterdir()
        if path.is_file() and path.suffix.lower() in CAPTION_SUFFIXES)
    if not candidates:
        return None
    preferred = [path for path in candidates if fmt in path.stem.lower()]
    return (preferred or candidates)[0]


def caption_report(episode: dict, chapter_dir: Path, cues: dict,
                   fmt: str, *, legacy_path: Path | None = None) -> dict:
    """Compare a legacy SRT/VTT with the current cue track.

    Returns `{"status": "unverified", "reason": ...}` when no legacy caption
    file exists. This is intentionally not part of `compat()`: storing an
    unverified field would make the committed compat reports stale.
    """
    path = legacy_path or legacy_caption_path(episode, chapter_dir, fmt)
    if path is None:
        return {"status": "unverified",
                "reason": f"{episode['id']} {fmt}: no legacy SRT/VTT "
                          "captions under the legacy base"}
    if not path.is_file():
        return {"status": "unverified", "reason": f"captions are missing: {path}"}
    legacy = parse_captions(path)
    if not legacy:
        return {"status": "unverified",
                "reason": f"{path.name} has no readable caption cues"}
    current = cues.get(fmt) or []
    mismatches: list[str] = []
    if len(legacy) != len(current):
        mismatches.append(f"{len(legacy)} legacy cues != {len(current)}")
    if normalized("".join(cue["text"] for cue in legacy)) != normalized(
            "".join(cue["text"] for cue in current)):
        mismatches.append("caption text differs")
    for index, (before, after) in enumerate(zip(legacy, current)):
        if normalized(before["text"]) != normalized(after["text"]):
            mismatches.append(f"cue {index}: text differs")
        for field in ("start", "end"):
            if abs(before[field] - after[field]) > CAPTION_TOLERANCE_S:
                mismatches.append(
                    f"cue {index}: {field} {before[field]} != {after[field]}")
    return {
        "status": "match" if not mismatches else "mismatch",
        "captions": (path.relative_to(chapter_dir).as_posix()
                     if path.is_relative_to(chapter_dir) else path.as_posix()),
        "legacy_count": len(legacy),
        "current_count": len(current),
        "mismatches": mismatches,
    }


def _probe_duration(path: Path) -> float | None:
    try:
        run = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration",
             "-of", "default=noprint_wrappers=1:nokey=1", str(path)],
            capture_output=True, text=True, timeout=30, encoding="utf-8")
        if run.returncode:
            return None
        return round(float(run.stdout.strip()), 3)
    except (OSError, subprocess.SubprocessError, ValueError):
        return None


def _frame_sha(path: Path, at_s: float) -> str | None:
    try:
        run = subprocess.run(
            ["ffmpeg", "-hide_banner", "-v", "error", "-i", str(path),
             "-ss", f"{at_s:.3f}", "-frames:v", "1", "-map", "0:v:0",
             "-f", "image2pipe", "-vcodec", "png", "-"],
            capture_output=True, timeout=120)
    except (OSError, subprocess.SubprocessError):
        return None
    if run.returncode or not run.stdout:
        return None
    return hashlib.sha256(run.stdout).hexdigest()


def keyframe_report(old_video: Path, new_video: Path, *,
                    points: tuple = KEYFRAME_POINTS) -> dict:
    """Compare evenly spaced decoded frames by SHA-256.

    Missing videos or unavailable ffmpeg/ffprobe yield an explicit
    `unverified` result instead of a fabricated match.
    """
    if not points or any(type(point) not in (int, float)
                         or not math.isfinite(point) or not 0 <= point < 1
                         for point in points):
        raise VideoError("keyframe points must be non-empty finite fractions in [0, 1)")
    old, new = Path(old_video), Path(new_video)
    missing = [str(path) for path in (old, new) if not path.is_file()]
    if missing:
        return {"status": "unverified",
                "reason": "video is missing: " + ", ".join(missing)}
    if old.samefile(new):
        return {"status": "unverified",
                "reason": "old and new video refer to the same file"}
    old_duration = _probe_duration(old)
    new_duration = _probe_duration(new)
    if any(duration is None or not math.isfinite(duration) or duration <= 0
           for duration in (old_duration, new_duration)):
        return {"status": "unverified",
                "reason": f"ffprobe could not read a video duration: "
                          f"{old} or {new}"}
    frames = []
    for fraction in points:
        old_at = round(min(old_duration, new_duration) * fraction, 3)
        new_at = old_at
        old_sha = _frame_sha(old, old_at)
        new_sha = _frame_sha(new, new_at)
        frames.append({
            "fraction": fraction,
            "old_at_s": old_at,
            "new_at_s": new_at,
            "old_sha256": old_sha,
            "new_sha256": new_sha,
            "match": old_sha is not None and old_sha == new_sha,
        })
    report = {
        "old": str(old),
        "new": str(new),
        "old_duration_s": old_duration,
        "new_duration_s": new_duration,
        "duration_match": abs(old_duration - new_duration) <= VIDEO_DURATION_TOLERANCE_S,
        "frames": frames,
    }
    if any(frame["old_sha256"] is None or frame["new_sha256"] is None
           for frame in frames):
        report["status"] = "unverified"
        report["reason"] = "ffmpeg could not extract every comparison frame"
    elif report["duration_match"] and all(frame["match"] for frame in frames):
        report["status"] = "identical"
    else:
        report["status"] = "different"
    return report


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
