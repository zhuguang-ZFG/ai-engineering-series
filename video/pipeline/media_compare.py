"""Review explicit caption/render evidence without changing episode status."""
from __future__ import annotations

import hashlib
import math
from pathlib import Path

from . import model, timeline


def transcript(path: Path, chapter: str, fmt: str) -> list[dict]:
    data = model.read_json(path)
    expected = {"schema_version": 1, "chapter": chapter, "format": fmt}
    if not isinstance(data, dict):
        raise model.VideoError(f"{path}: transcript must be an object")
    for key, value in expected.items():
        if type(data.get(key)) is not type(value) or data[key] != value:
            raise model.VideoError(f"{path}: transcript {key} must be {value!r}")
    cues = data.get("segments")
    if not isinstance(cues, list) or not cues:
        raise model.VideoError(f"{path}: transcript segments must be non-empty")
    previous_start = -1.
    for index, cue in enumerate(cues):
        if not isinstance(cue, dict):
            raise model.VideoError(f"{path}: cue {index} must be an object")
        times = [cue.get(key) for key in ("start", "end")]
        if (any(type(value) not in (int, float) or not math.isfinite(value)
                for value in times) or not 0 <= times[0] < times[1]
                or times[0] < previous_start):
            raise model.VideoError(f"{path}: cue {index} needs ordered finite times")
        if not isinstance(cue.get("text"), str) or not cue["text"].strip():
            raise model.VideoError(f"{path}: cue {index} needs text")
        previous_start = times[0]
    return cues


def evidence(path: Path | None) -> dict:
    if path is None:
        return {"path": None, "sha256": None}
    digest = None
    if path.is_file():
        with path.open("rb") as source:
            digest = hashlib.file_digest(source, "sha256").hexdigest()
    return {"path": path.resolve().as_posix(), "sha256": digest}


def compare(args) -> int:
    inputs = {"legacy_captions": args.legacy_captions,
              "current_captions": args.current_captions,
              "legacy_video": args.legacy_video, "current_video": args.current_video}
    target = args.report.resolve()
    for path in inputs.values():
        if path is not None and (target == path.resolve() or
                target.exists() and path.exists() and target.samefile(path)):
            raise model.VideoError("comparison report must not overwrite input evidence")
    episode, scenes = model.load_episode(args.chapter, check_assets=False)
    chapter_dir = model.CHAPTERS / args.chapter
    cues = transcript(args.current_captions, args.chapter, args.format)
    captions = timeline.caption_report(episode, chapter_dir, {args.format: cues},
                                       args.format, legacy_path=args.legacy_captions)
    structure = timeline.compat(episode, chapter_dir, scenes)["formats"].get(args.format)
    if args.legacy_video is None or args.current_video is None:
        frames = {"status": "unverified",
                  "reason": "both legacy and independently rendered current videos are required"}
    else:
        frames = timeline.keyframe_report(args.legacy_video, args.current_video)
    expected_duration = episode["formats"][args.format]["duration_s"]
    duration_match = all(abs(frames[key] - expected_duration) <=
                         timeline.VIDEO_DURATION_TOLERANCE_S
                         for key in ("old_duration_s", "new_duration_s")
                         if key in frames)
    if (captions["status"] == "mismatch" or frames["status"] == "different"
            or not duration_match or structure is not None and not structure["match"]):
        status = "mismatch"
    elif (captions["status"] == "match" and frames["status"] == "identical"
          and structure is not None and structure["match"]):
        status = "match"
    else:
        status = "unverified"
    report = {"schema_version": 1, "chapter": args.chapter, "format": args.format,
              "status": status, "inputs": {key: evidence(path) for key, path in inputs.items()},
              "timeline": structure, "captions": captions, "keyframes": frames,
              "expected_duration_s": expected_duration,
              "duration_matches_episode": duration_match if "frames" in frames else None,
              "scope": "sampled decoded frames only; audio quality requires check --audio"}
    model.write_json(target, report)
    print(f"{args.chapter} {args.format}: {status}; report: {target}")
    return 0 if status == "match" else 1
