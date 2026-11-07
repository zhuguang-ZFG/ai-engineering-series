"""Static and audio gates. Static checks always run; loudness, peak and silence
run when the narration file is on disk, so a clean clone still checks the
configuration.
"""
from __future__ import annotations

import re
import subprocess
from pathlib import Path

from .model import format_base
from .voice import normalized

LUFS = re.compile(r"I:\s*(-?\d+(?:\.\d+)?)\s*LUFS")
PEAK = re.compile(r"Peak:\s*(-?\d+(?:\.\d+)?)\s*dBFS")
SILENCE_START = re.compile(r"silence_start:\s*(-?\d+(?:\.\d+)?)")
SILENCE_END = re.compile(r"silence_end:\s*(-?\d+(?:\.\d+)?)")


def _rgb(color: str) -> tuple[float, float, float]:
    return tuple(int(color[index:index + 2], 16) / 255
                 for index in (1, 3, 5))


def _luminance(color: str) -> float:
    def channel(value: float) -> float:
        return value / 12.92 if value <= 0.04045 else (
            (value + 0.055) / 1.055) ** 2.4
    red, green, blue = (channel(value) for value in _rgb(color))
    return 0.2126 * red + 0.7152 * green + 0.0722 * blue


def contrast(foreground: str, background: str) -> float:
    one, two = sorted((_luminance(foreground), _luminance(background)),
                      reverse=True)
    return round((one + 0.05) / (two + 0.05), 2)


def _duration(path: Path) -> float:
    run = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", str(path)],
        capture_output=True, text=True, timeout=30, encoding="utf-8")
    return round(float(run.stdout.strip()), 3)


def audio_report(path: Path) -> dict:
    duration = _duration(path)
    loud = subprocess.run(
        ["ffmpeg", "-hide_banner", "-nostats", "-i", str(path),
         "-af", "ebur128=peak=true", "-f", "null", "-"],
        capture_output=True, text=True, timeout=300, encoding="utf-8",
        errors="replace")
    summary = loud.stderr.rsplit("Summary:", 1)[-1]
    lufs = LUFS.search(summary) or LUFS.search(loud.stderr)
    peak = PEAK.search(summary) or PEAK.search(loud.stderr)
    silence = subprocess.run(
        ["ffmpeg", "-hide_banner", "-nostats", "-i", str(path),
         "-af", "silencedetect=noise=-40dB:d=0.5", "-f", "null", "-"],
        capture_output=True, text=True, timeout=300, encoding="utf-8",
        errors="replace")
    starts = [float(value) for value in SILENCE_START.findall(silence.stderr)]
    ends = [float(value) for value in SILENCE_END.findall(silence.stderr)]
    gaps = list(zip(starts, ends))
    trailing = 0.0
    if starts and (not ends or ends[-1] < starts[-1]):
        trailing = round(duration - starts[-1], 3)
    elif starts and duration - ends[-1] < 0.15:
        trailing = round(duration - starts[-1], 3)
    leading = round(ends[0], 3) if starts and starts[0] < 0.05 and ends else 0.0
    inside = [end - start for start, end in gaps
              if start >= leading - 0.01 and duration - end > 0.15]
    return {
        "duration_s": duration,
        "loudness_lufs": float(lufs.group(1)) if lufs else None,
        "peak_dbfs": float(peak.group(1)) if peak else None,
        "silences": [{"start_s": start, "end_s": end} for start, end in gaps],
        "leading_silence_s": leading,
        "trailing_silence_s": trailing,
        "inside_silence_s": max(inside or [0.0]),
    }


def check(episode: dict, scenes: dict, manifests: dict, cues: dict,
          chapter_dir: Path, *, check_audio: bool = False) -> list[str]:
    errors: list[str] = []
    style = episode["captions"]
    quality = episode["quality"]
    ratio = contrast(style["foreground"], style["background"])
    if ratio < 4.5:
        errors.append(
            f"{episode['id']}: caption contrast {ratio}:1 is below 4.5:1")
    for fmt, spec in episode["formats"].items():
        width, height = spec["width"], spec["height"]
        safe = style["safe_pct"] / 100
        text_width = style["max_chars"] * style["min_font_px"] * 1.2
        if text_width + 2 * safe * width > width:
            errors.append(
                f"{episode['id']}: {fmt} caption box is wider than the safe area")
        text_height = style["max_lines"] * style["min_font_px"] * 1.4
        if text_height + 2 * safe * height > height:
            errors.append(
                f"{episode['id']}: {fmt} caption box is taller than the safe area")
        track = cues.get(fmt) or []
        for cue in track:
            if cue["end"] - cue["start"] + 0.001 < style["min_dwell_s"]:
                errors.append(
                    f"{episode['id']}: {fmt} cue at {cue['start']}s dwells "
                    f"less than {style['min_dwell_s']}s")
            if len(cue["text"]) > style["max_chars"] * style["max_lines"]:
                errors.append(
                    f"{episode['id']}: {fmt} cue at {cue['start']}s exceeds "
                    "the character budget")
        wanted = normalized("".join(
            segment["text"]
            for segment in (manifests.get(fmt) or {}).get("segments", [])))
        shown = normalized("".join(cue["text"] for cue in track))
        if track and wanted != shown:
            errors.append(
                f"{episode['id']}: {fmt} captions do not match the narration")
        if track and track[-1]["end"] > spec["duration_s"] + 0.1:
            errors.append(
                f"{episode['id']}: {fmt} captions run past the format duration")
        for flash in (scenes.get("flashes") or {}).get(fmt, []):
            at = flash.get("at_s")
            if not isinstance(at, (int, float)) or at < 0 or at > spec["duration_s"]:
                errors.append(
                    f"{episode['id']}: {fmt} flash at {at!r} is outside the format")
        flashes = sorted(
            flash["at_s"] for flash in (scenes.get("flashes") or {}).get(fmt, [])
            if isinstance(flash.get("at_s"), (int, float)))
        for start in flashes:
            if sum(1 for at in flashes if start <= at < start + 1.0) > \
                    quality["max_flash_hz"]:
                errors.append(
                    f"{episode['id']}: {fmt} flashes more than "
                    f"{quality['max_flash_hz']} times per second at {start}s")

    rights = episode["rights"]
    for field in ("owner", "music", "footage"):
        if rights[field].strip().lower() in {"unknown", "unlicensed", "tbd"}:
            errors.append(f"{episode['id']}: rights.{field} is not resolved")

    if check_audio:
        legacy = episode.get("legacy") or {}
        for fmt, audio in (scenes.get("audio") or {}).items():
            base = format_base(chapter_dir, legacy, fmt)
            if not audio or base is None:
                continue
            path = base / audio["path"]
            if not path.is_file():
                errors.append(f"{episode['id']}: audio {path} is missing")
                continue
            report = audio_report(path)
            if abs(report["duration_s"] - audio["duration_s"]) > 0.5:
                errors.append(
                    f"{episode['id']}: {fmt} audio is {report['duration_s']}s, "
                    f"configured {audio['duration_s']}s")
            if report["peak_dbfs"] is not None and \
                    report["peak_dbfs"] > quality["peak_dbfs"]:
                errors.append(
                    f"{episode['id']}: {fmt} peak {report['peak_dbfs']} dBFS "
                    f"exceeds {quality['peak_dbfs']}")
            if report["loudness_lufs"] is not None and \
                    quality.get("normalize", True):
                delta = abs(report["loudness_lufs"] - quality["loudness_lufs"])
                if delta > quality["loudness_tolerance"]:
                    errors.append(
                        f"{episode['id']}: {fmt} loudness "
                        f"{report['loudness_lufs']} LUFS is outside "
                        f"{quality['loudness_lufs']}±{quality['loudness_tolerance']}")
            if report["inside_silence_s"] > 2.0:
                errors.append(
                    f"{episode['id']}: {fmt} has a {report['inside_silence_s']}s "
                    "silence inside the narration")
            if report["trailing_silence_s"] + 0.01 < quality["end_margin_s"]:
                errors.append(
                    f"{episode['id']}: {fmt} leaves only "
                    f"{report['trailing_silence_s']}s after the last word")
    return errors
