"""One-time migration from five hand-built projects to fifteen chapter configs.

Chapter one keeps its Markdown parser; chapters two to five keep the plain
narration file their voice scripts already split. Chapters six to fifteen get a
draft script cut from the content pack until a producer reviews it.
"""
from __future__ import annotations

import shutil
from pathlib import Path

from . import content, timeline, voice
from .model import (
    CHAPTER_IDS, CHAPTERS, DEFAULT_CAPTIONS, DEFAULT_QUALITY, ROOT, VIDEO,
    VideoError, format_base, write_json, write_yaml,
)

DOCS = ROOT / "docs" / "video"
VOICE = {"engine": "edge-tts", "voice_id": "zh-CN-YunyangNeural",
         "rate": "-10%", "pitch": "-5Hz"}
RIGHTS = {"owner": "小电讲电路 (original)", "music": "none", "footage": "none"}


def _legacy(chapter_id: str) -> Path:
    return VIDEO / chapter_id / "hf-remake"


def _intent(scene_id: str, index: int, total: int) -> str:
    low = scene_id.lower()
    if any(word in low for word in ("outro", "end", "close")):
        return "outro"
    if any(word in low for word in ("quiz", "guess")):
        return "quiz"
    if any(word in low for word in ("practice", "demo", "doctor", "crud")):
        return "demo"
    if index == 0:
        return "hook"
    if index == total - 1:
        return "outro"
    return "section"


def _scenes_from_index(path: Path) -> dict:
    parsed = timeline.parse_index(path)
    total = len(parsed["scenes"])
    scenes = []
    for index, scene in enumerate(parsed["scenes"]):
        scenes.append({
            "id": scene["id"],
            "start_s": scene["start_s"],
            "duration_s": scene["duration_s"],
            "source": scene["source"],
            "intent": _intent(scene["id"], index, total),
        })
    return {"parsed": parsed, "scenes": scenes}


def _format(index: dict | None, fallback: float, width: int, height: int,
            status: str) -> dict:
    duration = round(index["duration_s"], 3) if index else round(fallback, 3)
    return {"width": width, "height": height,
            "fps": index["fps"] if index else 30,
            "duration_s": duration, "status": status}


def _script(source: Path, target: Path, mode: str) -> dict:
    if not source.is_file():
        raise VideoError(f"{source}: script is missing")
    target.write_text(source.read_text(encoding="utf-8"), encoding="utf-8")
    return {"path": target.name, "mode": mode}


def _spoken_script(chapter_id: str, target: Path) -> dict:
    """The rendered voice slices are the narration that actually shipped."""
    vo = VIDEO / chapter_id / "assets" / "vo"
    lines = [path.read_text(encoding="utf-8").strip()
             for path in sorted(vo.glob("c[0-9][0-9][0-9].txt"))]
    lines = [line for line in lines if line]
    if not lines:
        raise VideoError(f"{vo}: no spoken text to migrate")
    target.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return {"path": target.name, "mode": "paragraph"}


def migrate_published(chapter_id: str) -> dict:
    chapter_dir = CHAPTERS / chapter_id
    chapter_dir.mkdir(parents=True, exist_ok=True)
    legacy = _legacy(chapter_id)
    docs = DOCS / chapter_id

    if chapter_id == "ch01":
        spoken = sorted((VIDEO / chapter_id / "assets" / "vo").glob("c[0-9][0-9][0-9].txt"))
        if spoken:
            scripts = {"long": _spoken_script(
                chapter_id, chapter_dir / "script-long.txt")}
        else:
            scripts = {"long": _script(docs / "long-script.md",
                                       chapter_dir / "script-long.md",
                                       "markdown")}
    else:
        scripts = {
            "long": _script(VIDEO / chapter_id / "assets" / "vo" /
                            "full-script.txt",
                            chapter_dir / "script-long.txt", "plain"),
        }
    if (docs / "short-script.md").is_file():
        scripts["short"] = _script(docs / "short-script.md",
                                   chapter_dir / "script-short.md",
                                   "narration")

    long_index_path = legacy / "index.html"
    short_index_path = legacy / "short" / "index.html"
    long_index = timeline.parse_index(long_index_path) if long_index_path.is_file() else None
    short_index = timeline.parse_index(short_index_path) if short_index_path.is_file() else None

    legacy_spec = {
        "dir": f"../../{chapter_id}/hf-remake",
        "long_index": "index.html" if long_index else "",
        "short_index": "short/index.html" if short_index else "",
    }
    scenes = {"schema_version": 1, "episode": chapter_id, "formats": {},
              "audio": {}, "flashes": {}}
    for fmt, path in (("long", long_index_path), ("short", short_index_path)):
        if not path.is_file():
            continue
        extracted = _scenes_from_index(path)
        scenes["formats"][fmt] = extracted["scenes"]
        audio = extracted["parsed"]["audio"]
        if audio["path"] and audio["duration_s"]:
            scenes["audio"][fmt] = audio

    def audio_file(fmt: str):
        entry = (scenes.get("audio") or {}).get(fmt)
        base = format_base(chapter_dir, legacy_spec, fmt)
        return base / entry["path"] if entry and base else None

    # The published voice tracks predate the loudness floor; measure them,
    # but only gate a render this pipeline normalizes itself.
    legacy_quality = dict(DEFAULT_QUALITY, normalize=False)
    draft = {
        "voice": VOICE,
        "captions": DEFAULT_CAPTIONS,
        "quality": legacy_quality,
        "scripts": scripts,
    }
    long_manifest = voice.manifest(draft, chapter_dir, "long",
                                   audio_file("long"))
    short_manifest = voice.manifest(draft, chapter_dir, "short",
                                    audio_file("short"))
    long_fallback = long_manifest["total_duration_s"]
    short_fallback = short_manifest["total_duration_s"]

    formats = {
        "long": _format(long_index, long_fallback, 1920, 1080,
                        "built" if long_index else "scripted"),
        "short": _format(short_index, short_fallback, 1080, 1920,
                         "built" if short_index else "scripted"),
    }
    episode = {
        "schema_version": 1,
        "id": chapter_id,
        "title": content.build_pack(chapter_id)["title"],
        "status": "published",
        "content_pack": "content-pack.json",
        "scripts": scripts,
        "formats": formats,
        "voice": VOICE,
        "captions": DEFAULT_CAPTIONS,
        "quality": legacy_quality,
        "rights": RIGHTS,
        "sources": [],
        "legacy": legacy_spec,
    }
    content.write_pack(chapter_id, chapter_dir)
    write_yaml(chapter_dir / "episode.yaml", episode)
    write_yaml(chapter_dir / "scenes.yaml", scenes)
    stale = chapter_dir / "script-long.md"
    if scripts["long"]["path"] == "script-long.txt" and stale.is_file():
        stale.unlink()
    report = timeline.compat(episode, chapter_dir, scenes)
    write_json(chapter_dir / "compat-report.json", report)
    return report


def _draft_script(pack: dict) -> str:
    lines = [
        f"# {pack['title']}",
        "",
        f"大家好，这里是小电讲电路。今天讲{pack['title']}。",
    ]
    lines += pack["takeaways"]
    for section in pack["sections"]:
        lines.append(f"{section['title']}。{section['summary']}")
    lines.append("这一讲就到这里，下一讲见。")
    return "\n\n".join(lines) + "\n"


def _draft_short(pack: dict) -> str:
    hook = pack["takeaways"][0] if pack["takeaways"] else pack["title"]
    second = pack["takeaways"][1] if len(pack["takeaways"]) > 1 else ""
    body = [hook]
    if second:
        body.append(second)
    topic = pack["sections"][0]["title"] if pack["sections"] else pack["title"]
    body.append(f"留个问题：{topic}，你会怎么设计？")
    body.append("小电讲电路，下一讲见。")
    return "# 短讲（草稿）\n\n" + "\n\n".join(body) + "\n"


def migrate_draft(chapter_id: str) -> dict:
    chapter_dir = CHAPTERS / chapter_id
    chapter_dir.mkdir(parents=True, exist_ok=True)
    pack = content.write_pack(chapter_id, chapter_dir)
    (chapter_dir / "script-long.md").write_text(
        _draft_script(pack), encoding="utf-8")
    (chapter_dir / "script-short.md").write_text(
        _draft_short(pack), encoding="utf-8")
    draft = {"voice": VOICE, "scripts": {
        "long": {"path": "script-long.md", "mode": "markdown"},
        "short": {"path": "script-short.md", "mode": "markdown"},
    }}
    long_manifest = voice.manifest(draft, chapter_dir, "long")
    short_manifest = voice.manifest(draft, chapter_dir, "short")
    episode = {
        "schema_version": 1,
        "id": chapter_id,
        "title": pack["title"],
        "status": "draft",
        "content_pack": "content-pack.json",
        "scripts": draft["scripts"],
        "formats": {
            "long": {"width": 1920, "height": 1080, "fps": 30,
                     "duration_s": max(120.0, long_manifest["total_duration_s"]),
                     "status": "scripted"},
            "short": {"width": 1080, "height": 1920, "fps": 30,
                      "duration_s": max(15.0, short_manifest["total_duration_s"]),
                      "status": "scripted"},
        },
        "voice": VOICE,
        "captions": DEFAULT_CAPTIONS,
        "quality": DEFAULT_QUALITY,
        "rights": RIGHTS,
        "sources": [],
    }
    scenes = {"schema_version": 1, "episode": chapter_id, "formats": {},
              "audio": {}, "flashes": {}}
    write_yaml(chapter_dir / "episode.yaml", episode)
    write_yaml(chapter_dir / "scenes.yaml", scenes)
    return {"chapter": chapter_id, "status": "draft"}


def create_all() -> list[dict]:
    reports = []
    for chapter_id in CHAPTER_IDS:
        if int(chapter_id[2:]) <= 5:
            reports.append(migrate_published(chapter_id))
        else:
            reports.append(migrate_draft(chapter_id))
    return reports
