"""Narration is the spine: chunks, their timings, and the cue text derived from
them. Captions never retype a sentence -- they are cuts of the chunk text, so a
caption and the voice track cannot drift apart.
"""
from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

from .model import DEFAULT_CAPTIONS, VideoError, read_json

CJK = re.compile(r"[\u4e00-\u9fff]")
SECTION_RE = re.compile(r"^##\s+")
MARKER_RE = re.compile(r"^\[(ANIM|CODE):([a-z0-9\-]+)\]\s*$")
BOLD_RE = re.compile(r"\*\*(.+?)\*\*")
CODE_RE = re.compile(r"`([^`]+)`")
SENTENCE_END = "。！？；.!?;"


def chunk_plain(text: str) -> list[str]:
    text = re.sub(r"\n[^\S\n]*\n\s*", "", text)
    parts: list[str] = []
    buf = ""
    for char in text.strip():
        buf += char
        if char in "。！？；" and len(buf) >= 90:
            parts.append(buf.strip())
            buf = ""
    if buf.strip():
        parts.append(buf.strip())
    merged: list[str] = []
    for part in parts:
        if merged and len(part) < 40:
            merged[-1] += part
        else:
            merged.append(part)
    return merged


def _clean(line: str) -> str:
    line = BOLD_RE.sub(r"\1", line)
    line = CODE_RE.sub(r"\1", line)
    return line.strip()


def _skip(line: str) -> bool:
    stripped = line.strip()
    return (not stripped or stripped.startswith(("#", ">", "---", "```"))
            or (stripped.startswith("|") and "|" in stripped[1:]))


def chunk_markdown(text: str) -> list[str]:
    """Port of the chapter-one parser: headings and stage markers break chunks."""
    chunks: list[str] = []
    buf: list[str] = []
    in_code = False

    def flush() -> None:
        nonlocal buf
        body = "".join(buf).strip()
        buf = []
        if not body:
            return
        if len(CJK.findall(body)) < 8 and len(body) < 20:
            return
        chunks.append(body)

    for raw in text.splitlines():
        if raw.strip().startswith("```"):
            in_code = not in_code
            continue
        if in_code:
            continue
        if SECTION_RE.match(raw) or MARKER_RE.match(raw.strip()):
            flush()
            continue
        if _skip(raw):
            continue
        buf.append(_clean(raw))
    flush()
    return chunks


def chunk_paragraph(text: str) -> list[str]:
    return [line.strip() for line in text.splitlines() if line.strip()]


HEADING_RE = re.compile(r"^(#{1,6})\s+(.*)$")


def narration_section(text: str) -> str:
    """A short script is a storyboard; its 口播 heading is the spoken part.

    Chapter one names the block 口播连贯稿; chapters two to five use 口播.
    """
    lines = text.splitlines()
    chosen = None
    for index, line in enumerate(lines):
        match = HEADING_RE.match(line)
        if not match or "口播" not in match.group(2):
            continue
        if "连贯" in match.group(2):
            chosen = index
            break
        if chosen is None:
            chosen = index
    if chosen is None:
        return text
    body = []
    for line in lines[chosen + 1:]:
        if HEADING_RE.match(line):
            break
        body.append(line)
    return "\n".join(body)


def _script(episode: dict, fmt: str) -> tuple[str, str]:
    raw = (episode.get("scripts") or {}).get(fmt)
    if isinstance(raw, dict):
        return raw.get("path", ""), raw.get("mode", "plain")
    if isinstance(raw, str):
        return raw, "plain"
    return "", "plain"


def chunks(episode: dict, chapter_dir: Path, fmt: str = "long") -> list[str]:
    name, mode = _script(episode, fmt)
    if not name:
        return []
    text = (chapter_dir / name).read_text(encoding="utf-8")
    if mode == "markdown":
        return chunk_markdown(text)
    if mode == "paragraph":
        return chunk_paragraph(text)
    if mode == "narration":
        return chunk_plain(narration_section(text))
    return chunk_plain(text)


def _vo_dir(episode: dict, chapter_dir: Path,
            fmt: str = "long") -> Path | None:
    legacy = episode.get("legacy") or {}
    if not legacy.get("dir"):
        return None
    base = (chapter_dir / legacy["dir"]).resolve()
    folder = "vo" if fmt == "long" else "vo-short"
    return base.parent / "assets" / folder


def _duration(path: Path) -> float | None:
    if not path.is_file():
        return None
    try:
        run = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration",
             "-of", "default=noprint_wrappers=1:nokey=1", str(path)],
            capture_output=True, text=True, timeout=30, encoding="utf-8",
        )
    except (OSError, subprocess.SubprocessError):
        return None
    try:
        return round(float(run.stdout.strip()), 3)
    except ValueError:
        return None


def _srt_end(path: Path) -> float | None:
    if not path.is_file():
        return None
    stamps = re.findall(r"--> (\d+):(\d+):(\d+),(\d+)", path.read_text(
        encoding="utf-8", errors="replace"))
    if not stamps:
        return None
    h, m, s, ms = (int(part) for part in stamps[-1])
    return round(h * 3600 + m * 60 + s + ms / 1000, 3)


def estimate(text: str) -> float:
    """Fallback pace for a chapter whose audio has not been synthesized."""
    return round(len(text) / 4.5 + 0.25, 3)


def manifest(episode: dict, chapter_dir: Path, fmt: str = "long",
             audio_path: Path | None = None) -> dict:
    texts = chunks(episode, chapter_dir, fmt)
    vo_dir = _vo_dir(episode, chapter_dir, fmt)
    voice = episode["voice"]
    segments = []
    for index, text in enumerate(texts):
        mp3 = vo_dir / f"c{index:03d}.mp3" if vo_dir else None
        srt = vo_dir / f"c{index:03d}.srt" if vo_dir else None
        duration = (_duration(mp3) if mp3 else None) or (
            _srt_end(srt) if srt else None)
        segments.append({
            "i": index,
            "text": text,
            "chars": len(text),
            "mp3": mp3.name if mp3 and mp3.is_file() else "",
            "duration_s": duration,
        })
    missing = [segment for segment in segments
               if segment["duration_s"] is None]
    total_audio = _duration(audio_path) if audio_path else None
    if missing and total_audio and not any(s["mp3"] for s in segments):
        chars = sum(segment["chars"] for segment in segments) or 1
        for segment in missing:
            segment["duration_s"] = round(
                total_audio * segment["chars"] / chars, 3)
    for segment in segments:
        if segment["duration_s"] is None:
            segment["duration_s"] = estimate(segment["text"])
    return {
        "schema_version": 1,
        "chapter": chapter_dir.name,
        "format": fmt,
        "voice": voice["voice_id"],
        "rate": voice["rate"],
        "pitch": voice["pitch"],
        "count": len(segments),
        "total_duration_s": round(sum(s["duration_s"] for s in segments), 3),
        "segments": segments,
    }


def _split(text: str, limit: int) -> list[str]:
    pieces: list[str] = []
    buf = ""
    for char in text:
        buf += char
        if len(buf) >= limit:
            cut = max(buf.rfind(mark) for mark in SENTENCE_END)
            if cut >= limit // 2:
                pieces.append(buf[:cut + 1])
                buf = buf[cut + 1:]
            else:
                pieces.append(buf)
                buf = ""
    if buf:
        if pieces and len(buf) < limit // 3:
            pieces[-1] += buf
        else:
            pieces.append(buf)
    return [piece for piece in pieces if piece.strip()]


def cues(episode: dict, chapter_dir: Path, fmt: str = "long",
         total_s: float | None = None,
         audio_path: Path | None = None) -> list[dict]:
    captions = episode.get("captions") or DEFAULT_CAPTIONS
    limit = int(captions.get("max_chars", 16))
    minimum = float(captions.get("min_dwell_s", 1.2))
    prepared = []
    for segment in manifest(episode, chapter_dir, fmt,
                            audio_path)["segments"]:
        pieces = _split(segment["text"], limit)
        weights = [max(1, len(piece)) for piece in pieces]
        total = sum(weights)
        local = []
        for piece, weight in zip(pieces, weights):
            local.append((piece, max(segment["duration_s"] * weight / total,
                                     minimum)))
        prepared.append(local)
    raw_total = sum(duration for segment in prepared
                    for _, duration in segment)
    count = sum(len(segment) for segment in prepared)
    floor = minimum * count
    extra_scale = 1.0
    if total_s and raw_total > total_s and raw_total > floor:
        extra_scale = max(0.0, (total_s - floor) / (raw_total - floor))
    built = []
    clock = 0.0
    for segment in prepared:
        for piece, duration in segment:
            duration = minimum + (duration - minimum) * extra_scale
            built.append({
                "start": round(clock, 3),
                "end": round(clock + duration, 3),
                "text": piece,
            })
            clock += duration
    return built


def caption_html(captions: list[dict], width: int, height: int,
                 style: dict) -> str:
    font = style.get("min_font_px", 32)
    safe = style.get("safe_pct", 5)
    rows = "\n".join(
        f'<div class="cue" data-start="{cue["start"]:.3f}" '
        f'data-duration="{cue["end"] - cue["start"]:.3f}">'
        f'{_escape(cue["text"])}</div>'
        for cue in captions
    )
    return f"""<!doctype html>
<html lang="zh">
<meta charset="utf-8">
<style>
  body {{ margin: 0; background: transparent; }}
  #captions {{ position: absolute; left: {safe}%; right: {safe}%;
               bottom: {safe}%; text-align: center; }}
  .cue {{ display: none; font: {font}px/1.4 sans-serif;
          color: {style.get("foreground", "#ffffff")};
          background: {style.get("background", "#101010")};
          padding: 0.2em 0.4em; }}
</style>
<div id="captions" data-width="{width}" data-height="{height}">
{rows}
</div>
</html>
"""


def _escape(text: str) -> str:
    return (text.replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;"))


def normalized(text: str) -> str:
    return re.sub(r"[\s，。！？；：、,.!?;:'\"“”‘’（）()\[\]【】…—-]", "", text)
