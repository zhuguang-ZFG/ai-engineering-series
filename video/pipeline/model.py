"""The video pipeline reads one config per chapter and refuses to guess.

Every episode declares its formats, voice, caption box, quality floor and
rights; every scene declares a start, a duration and an intent. The legacy
HyperFrames projects remain the renderer, but they are no longer the source of
truth -- `episode.yaml` and `scenes.yaml` are.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
VIDEO = ROOT / "video"
CHAPTERS = VIDEO / "chapters"
BOOK = ROOT / "yuyu-book"
CHAPTER_IDS = tuple(f"ch{number:02d}" for number in range(1, 16))

SCHEMA_VERSION = 1
FORMAT_SIZE = {"long": (1920, 1080), "short": (1080, 1920)}
FORMAT_MIN_S = {"long": 120.0, "short": 10.0}
FORMAT_MAX_S = {"long": 1800.0, "short": 90.0}
EPISODE_STATUSES = {"draft", "scripted", "published"}
FORMAT_STATUSES = {"draft", "scripted", "built"}
INTENTS = {"hook", "section", "demo", "quiz", "recap", "outro", "transition"}
ENGINES = {"edge-tts"}
HEX = re.compile(r"^#[0-9a-fA-F]{6}$")
ID_RE = re.compile(r"^[a-z0-9][a-z0-9_-]*$")

DEFAULT_CAPTIONS = {
    "max_chars": 16,
    "max_lines": 2,
    "min_dwell_s": 1.2,
    "min_font_px": 32,
    "safe_pct": 5,
    "foreground": "#ffffff",
    "background": "#101010",
}
DEFAULT_QUALITY = {
    "normalize": True,
    "max_flash_hz": 3,
    "peak_dbfs": -1.0,
    "loudness_lufs": -16.0,
    "loudness_tolerance": 2.0,
    "end_margin_s": 0.5,
}


class VideoError(Exception):
    """A chapter cannot be checked; the message names the file and field."""


def read_yaml(path: Path) -> dict:
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as exc:
        raise VideoError(f"{path}: cannot read YAML: {exc}") from exc
    if not isinstance(data, dict):
        raise VideoError(f"{path}: expected a mapping at the top level")
    return data


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2, sort_keys=False) + "\n",
        encoding="utf-8",
    )


def write_yaml(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        yaml.safe_dump(data, allow_unicode=True, sort_keys=False,
                       default_flow_style=False),
        encoding="utf-8",
    )


def source_ids() -> set:
    path = BOOK / "sources.json"
    if not path.exists():
        return set()
    return {entry["id"] for entry in read_json(path).get("sources", [])
            if isinstance(entry, dict) and "id" in entry}


def _number(errors: list, where: str, field: str, value, minimum=None,
            maximum=None) -> None:
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        errors.append(f"{where}.{field}: expected a number")
        return
    if minimum is not None and value < minimum:
        errors.append(f"{where}.{field}: {value} is below {minimum}")
    if maximum is not None and value > maximum:
        errors.append(f"{where}.{field}: {value} is above {maximum}")


def _text(errors: list, where: str, field: str, value, required=True) -> None:
    if not isinstance(value, str) or (required and not value.strip()):
        errors.append(f"{where}.{field}: expected a non-empty string")


def validate_episode(episode: dict, chapter_dir: Path) -> list[str]:
    errors: list[str] = []
    where = chapter_dir.name
    if episode.get("schema_version") != SCHEMA_VERSION:
        errors.append(f"{where}: schema_version must be {SCHEMA_VERSION}")
    if episode.get("id") != chapter_dir.name:
        errors.append(f"{where}: id must match the directory name")
    _text(errors, where, "title", episode.get("title"))
    if episode.get("status") not in EPISODE_STATUSES:
        errors.append(f"{where}: status must be one of {sorted(EPISODE_STATUSES)}")

    pack = episode.get("content_pack")
    _text(errors, where, "content_pack", pack)
    if isinstance(pack, str) and not (chapter_dir / pack).is_file():
        errors.append(f"{where}: content pack {pack} is missing")

    scripts = episode.get("scripts") or {}
    if not isinstance(scripts, dict):
        errors.append(f"{where}.scripts: expected a mapping")
    else:
        for name in ("long", "short"):
            if name not in scripts:
                continue
            spec = scripts[name]
            if isinstance(spec, dict):
                _text(errors, where, f"scripts.{name}.path", spec.get("path"))
                if spec.get("mode") not in {"plain", "markdown", "paragraph",
                                            "narration"}:
                    errors.append(
                        f"{where}.scripts.{name}.mode: plain, markdown, "
                        "paragraph or narration")
                path = spec.get("path")
            else:
                _text(errors, where, f"scripts.{name}", spec)
                path = spec
            if isinstance(path, str) and not (chapter_dir / path).is_file():
                errors.append(f"{where}: script {path} is missing")

    formats = episode.get("formats")
    if not isinstance(formats, dict):
        errors.append(f"{where}.formats: expected a mapping")
    else:
        for name, (width, height) in FORMAT_SIZE.items():
            spec = formats.get(name)
            if not isinstance(spec, dict):
                errors.append(f"{where}.formats.{name}: expected a mapping")
                continue
            if spec.get("width") != width or spec.get("height") != height:
                errors.append(
                    f"{where}.formats.{name}: must be {width}x{height}")
            _number(errors, f"{where}.formats.{name}", "fps", spec.get("fps"),
                    1, 120)
            _number(errors, f"{where}.formats.{name}", "duration_s",
                    spec.get("duration_s"), FORMAT_MIN_S[name],
                    FORMAT_MAX_S[name])
            if spec.get("status") not in FORMAT_STATUSES:
                errors.append(
                    f"{where}.formats.{name}.status: "
                    f"one of {sorted(FORMAT_STATUSES)}")

    voice = episode.get("voice") or {}
    if voice.get("engine") not in ENGINES:
        errors.append(f"{where}.voice.engine: one of {sorted(ENGINES)}")
    _text(errors, where, "voice.voice_id", voice.get("voice_id"))
    for field in ("rate", "pitch"):
        _text(errors, where, f"voice.{field}", voice.get(field))

    captions = episode.get("captions") or {}
    _number(errors, f"{where}.captions", "max_chars",
            captions.get("max_chars"), 6, 40)
    _number(errors, f"{where}.captions", "max_lines",
            captions.get("max_lines"), 1, 3)
    _number(errors, f"{where}.captions", "min_dwell_s",
            captions.get("min_dwell_s"), 0.8, 5.0)
    _number(errors, f"{where}.captions", "min_font_px",
            captions.get("min_font_px"), 24, 96)
    _number(errors, f"{where}.captions", "safe_pct",
            captions.get("safe_pct"), 0, 8)
    for field in ("foreground", "background"):
        value = captions.get(field)
        if not isinstance(value, str) or not HEX.match(value):
            errors.append(f"{where}.captions.{field}: expected #rrggbb")

    quality = episode.get("quality") or {}
    if not isinstance(quality.get("normalize", True), bool):
        errors.append(f"{where}.quality.normalize: expected true or false")
    _number(errors, f"{where}.quality", "max_flash_hz",
            quality.get("max_flash_hz"), 0, 10)
    _number(errors, f"{where}.quality", "peak_dbfs",
            quality.get("peak_dbfs"), -30.0, 0.0)
    _number(errors, f"{where}.quality", "loudness_lufs",
            quality.get("loudness_lufs"), -40.0, -5.0)
    _number(errors, f"{where}.quality", "loudness_tolerance",
            quality.get("loudness_tolerance"), 0.1, 10.0)
    _number(errors, f"{where}.quality", "end_margin_s",
            quality.get("end_margin_s"), 0.0, 10.0)

    rights = episode.get("rights") or {}
    _text(errors, where, "rights.owner", rights.get("owner"))
    for field in ("music", "footage"):
        _text(errors, where, f"rights.{field}", rights.get(field))

    known = source_ids()
    sources = episode.get("sources") or []
    if not isinstance(sources, list):
        errors.append(f"{where}.sources: expected a list")
    else:
        for source in sources:
            if source not in known:
                errors.append(f"{where}.sources: {source!r} is not registered")

    legacy = episode.get("legacy")
    if legacy is not None:
        if not isinstance(legacy, dict):
            errors.append(f"{where}.legacy: expected a mapping")
        else:
            _text(errors, where, "legacy.dir", legacy.get("dir"))
            base = chapter_dir / str(legacy.get("dir", ""))
            if not base.is_dir():
                errors.append(f"{where}: legacy dir {base} is missing")
            for field in ("long_index", "short_index"):
                value = legacy.get(field)
                if value and not (base / value).is_file():
                    errors.append(f"{where}: legacy {field} {value} is missing")
    return errors


def format_base(chapter_dir: Path, legacy: dict | None,
                name: str) -> Path | None:
    """Scene sources and audio are relative to the index that renders them."""
    if not legacy or not legacy.get("dir"):
        return None
    base = chapter_dir / legacy["dir"]
    index = legacy.get("long_index" if name == "long" else "short_index")
    if index:
        base = base / Path(index).parent
    return base


def validate_scenes(scenes: dict, episode: dict, chapter_dir: Path, *,
                    check_assets: bool = True) -> list[str]:
    errors: list[str] = []
    where = f"{chapter_dir.name}.scenes"
    if scenes.get("schema_version") != SCHEMA_VERSION:
        errors.append(f"{where}: schema_version must be {SCHEMA_VERSION}")
    if scenes.get("episode") != chapter_dir.name:
        errors.append(f"{where}: episode must match the directory name")

    formats = scenes.get("formats")
    episode_formats = episode.get("formats") or {}
    if not isinstance(formats, dict):
        errors.append(f"{where}.formats: expected a mapping")
        return errors

    legacy = episode.get("legacy") or {}
    for name, spec in episode_formats.items():
        if spec.get("status") != "built":
            continue
        items = formats.get(name)
        if not isinstance(items, list) or not items:
            errors.append(f"{where}.formats.{name}: a built format needs scenes")
            continue
        base = format_base(chapter_dir, legacy, name) if check_assets else None
        _validate_scene_list(errors, f"{where}.{name}", items, spec, base)
        audio = (scenes.get("audio") or {}).get(name)
        if audio is not None:
            _validate_audio(errors, f"{where}.audio.{name}", audio, spec, base)
    for name in formats:
        if name not in FORMAT_SIZE:
            errors.append(f"{where}.formats.{name}: unknown format")
    return errors


def _validate_scene_list(errors: list, where: str, items: list, spec: dict,
                         legacy_base: Path | None) -> None:
    seen = set()
    expected_start = 0.0
    for index, scene in enumerate(items):
        label = f"{where}[{index}]"
        if not isinstance(scene, dict):
            errors.append(f"{label}: expected a mapping")
            continue
        scene_id = scene.get("id")
        if not isinstance(scene_id, str) or not ID_RE.match(scene_id):
            errors.append(f"{label}.id: lowercase slug, got {scene_id!r}")
        elif scene_id in seen:
            errors.append(f"{label}.id: duplicate {scene_id}")
        else:
            seen.add(scene_id)
        start = scene.get("start_s")
        duration = scene.get("duration_s")
        _number(errors, label, "start_s", start, 0.0, spec.get("duration_s"))
        _number(errors, label, "duration_s", duration, 2.0, 1800.0)
        if isinstance(start, (int, float)) and abs(start - expected_start) > 0.05:
            errors.append(
                f"{label}: starts at {start}, previous scene ends at "
                f"{expected_start:.3f}")
        if isinstance(start, (int, float)) and isinstance(duration, (int, float)):
            expected_start = start + duration
        if scene.get("intent") not in INTENTS:
            errors.append(f"{label}.intent: one of {sorted(INTENTS)}")
        source = scene.get("source")
        if not source:
            errors.append(f"{label}.source: a built scene needs a composition")
        elif legacy_base is not None and not (legacy_base / source).is_file():
            errors.append(f"{label}: composition {source} is missing")
    end = expected_start
    want = spec.get("duration_s")
    if isinstance(want, (int, float)) and abs(end - want) > 0.1:
        errors.append(f"{where}: scenes end at {end:.3f}, declared {want}")


def _validate_audio(errors: list, where: str, audio: dict, spec: dict,
                    legacy_base: Path | None) -> None:
    if not isinstance(audio, dict):
        errors.append(f"{where}: expected a mapping")
        return
    _text(errors, where, "path", audio.get("path"))
    _number(errors, where, "duration_s", audio.get("duration_s"),
            FORMAT_MIN_S["short"], FORMAT_MAX_S["long"])
    want = spec.get("duration_s")
    got = audio.get("duration_s")
    if isinstance(want, (int, float)) and isinstance(got, (int, float)):
        if abs(want - got) > 0.5:
            errors.append(f"{where}: audio {got}s does not match format {want}s")
    path = audio.get("path")
    if legacy_base is not None and isinstance(path, str):
        if not (legacy_base / path).exists():
            errors.append(f"{where}: audio {path} is missing")


def load_episode(chapter_id: str, *, check_assets: bool = True
                 ) -> tuple[dict, dict]:
    chapter_dir = CHAPTERS / chapter_id
    episode = read_yaml(chapter_dir / "episode.yaml")
    scenes = read_yaml(chapter_dir / "scenes.yaml")
    errors = validate_episode(episode, chapter_dir)
    errors += validate_scenes(scenes, episode, chapter_dir,
                              check_assets=check_assets)
    if errors:
        raise VideoError("\n".join(errors))
    return episode, scenes
