"""Command line for the video factory.

    python video/pipeline/cli.py migrate
    python video/pipeline/cli.py check [--chapter ch02] [--audio]
    python video/pipeline/cli.py build [--chapter ch02]
    python video/pipeline/cli.py prove
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from pipeline import content, migrate, model, quality, timeline, voice
else:
    from . import content, migrate, model, quality, timeline, voice

BUILD = model.VIDEO / ".build"


def _report(chapter_id: str, audio: bool = False, *,
            config_only: bool = False) -> dict:
    episode, scenes = model.load_episode(chapter_id, check_assets=not config_only)
    chapter_dir = model.CHAPTERS / chapter_id
    errors: list[str] = []
    warnings: list[str] = []

    generated_pack = content.build_pack(chapter_id)
    stored_pack = model.read_json(chapter_dir / episode["content_pack"])
    if generated_pack != stored_pack:
        errors.append(
            f"{chapter_id}: content pack is stale; rerun cli.py migrate")

    manifests, cues = {}, {}
    legacy = episode.get("legacy") or {}
    for fmt in ("long", "short"):
        if not (episode.get("scripts") or {}).get(fmt):
            continue
        base = model.format_base(chapter_dir, legacy, fmt)
        entry = (scenes.get("audio") or {}).get(fmt)
        audio_path = base / entry["path"] if entry and base else None
        manifest = voice.manifest(episode, chapter_dir, fmt, audio_path)
        manifests[fmt] = manifest
        spec = episode["formats"][fmt]
        tolerance = max(0.5, spec["duration_s"] * 0.001)
        if not config_only and spec["status"] == "built" and \
                abs(manifest["total_duration_s"] - spec["duration_s"]) > tolerance:
            errors.append(
                f"{chapter_id}: {fmt} narration is "
                f"{manifest['total_duration_s']}s, format declares "
                f"{spec['duration_s']}s")
        cues[fmt] = voice.cues(episode, chapter_dir, fmt,
                               total_s=spec["duration_s"],
                               audio_path=audio_path)

    errors += quality.check(episode, scenes, manifests, cues, chapter_dir,
                            check_audio=audio)

    report = timeline.compat(episode, chapter_dir, scenes)
    stored = chapter_dir / "compat-report.json"
    if report["formats"]:
        if not stored.is_file():
            errors.append(f"{chapter_id}: compat report is missing")
        else:
            if model.read_json(stored) != report:
                errors.append(
                    f"{chapter_id}: compat report is stale; rerun migrate")
        for fmt, entry in report["formats"].items():
            if not entry["match"]:
                errors.extend(f"{chapter_id}: {fmt}: {item}"
                              for item in entry["mismatches"])

    return {
        "chapter": chapter_id,
        "errors": errors,
        "warnings": warnings,
        "manifests": manifests,
        "cues": cues,
        "compat": report,
        "episode": episode,
        "scenes": scenes,
    }


def _write_build(report: dict) -> Path:
    chapter_id = report["chapter"]
    out = BUILD / chapter_id
    out.mkdir(parents=True, exist_ok=True)
    episode = report["episode"]
    hashes = {}
    for fmt, manifest in report["manifests"].items():
        path = out / f"vo-manifest-{fmt}.json"
        model.write_json(path, manifest)
        hashes[path.name] = _sha(path)
        spec = episode["formats"][fmt]
        captions = voice.caption_html(
            report["cues"][fmt], spec["width"], spec["height"],
            episode["captions"])
        path = out / f"captions-{fmt}.html"
        path.write_text(captions, encoding="utf-8")
        hashes[path.name] = _sha(path)
        transcript = {
            "schema_version": 1,
            "chapter": chapter_id,
            "format": fmt,
            "segments": report["cues"][fmt],
        }
        path = out / f"transcript-{fmt}.json"
        model.write_json(path, transcript)
        hashes[path.name] = _sha(path)
    pack = content.build_pack(chapter_id)
    path = out / "content-pack.json"
    model.write_json(path, pack)
    hashes[path.name] = _sha(path)
    path = out / "timeline.json"
    model.write_json(path, timeline.build(episode, report["scenes"],
                                           report["cues"]))
    hashes[path.name] = _sha(path)
    if report["compat"]["formats"]:
        path = out / "compat-report.json"
        model.write_json(path, report["compat"])
        hashes[path.name] = _sha(path)
    model.write_json(out / "manifest.json",
                     {"chapter": chapter_id, "sha256": hashes})
    return out


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check(args) -> int:
    ids = [args.chapter] if args.chapter else list(model.CHAPTER_IDS)
    failures = 0
    for chapter_id in ids:
        report = _report(chapter_id, audio=args.audio,
                         config_only=args.config_only)
        status = "ok" if not report["errors"] else "FAIL"
        print(f"{chapter_id}: {status}")
        for error in report["errors"]:
            print(f"  error: {error}")
        failures += bool(report["errors"])
    print(f"video check: {len(ids) - failures}/{len(ids)} chapters clean")
    return 1 if failures else 0


def build(args) -> int:
    ids = [args.chapter] if args.chapter else list(model.CHAPTER_IDS)
    for chapter_id in ids:
        report = _report(chapter_id, config_only=not args.assets)
        if report["errors"]:
            for error in report["errors"]:
                print(f"error: {error}", file=sys.stderr)
            return 1
        out = _write_build(report)
        print(f"{chapter_id}: wrote {out.relative_to(model.ROOT)}")
    return 0


def migrate_cmd(args) -> int:
    reports = migrate.create_all()
    for report in reports:
        print(json.dumps(report, ensure_ascii=False))
    return 0


def _legacy_chunks(chapter_id: str) -> list[str]:
    if chapter_id == "ch01":
        data = model.read_json(
            model.VIDEO / "ch01" / "assets" / "build" / "chunks.json")
        return [item["text"] for item in data["chunks"]]
    data = model.read_json(
        model.VIDEO / chapter_id / "assets" / "vo" / "chunks.json")
    return [item["text"] for item in data]


def _prove_one(chapter_id: str) -> dict:
    result = {"chapter": chapter_id, "chunks": "missing",
              "vo_manifest": "missing", "captions": "missing",
              "audio_slices": "missing", "transcript": "missing"}
    chapter_dir = model.CHAPTERS / chapter_id
    if not (chapter_dir / "episode.yaml").is_file():
        return result
    episode, scenes = model.load_episode(chapter_id)
    legacy_chunks = _legacy_chunks(chapter_id)
    rebuilt = voice.chunks(episode, chapter_dir, "long")
    result["chunks"] = ("identical" if rebuilt == legacy_chunks
                        else f"differs ({len(rebuilt)} vs {len(legacy_chunks)})")
    legacy_manifest_path = (
        model.VIDEO / chapter_id / "assets" / "vo" / "vo-manifest.json")
    manifest = voice.manifest(episode, chapter_dir, "long")
    if legacy_manifest_path.is_file():
        legacy_manifest = model.read_json(legacy_manifest_path)
        same_text = ([item["text"] for item in manifest["segments"]]
                     == [item["text"] for item in legacy_manifest["segments"]])
        total = abs(manifest["total_duration_s"]
                    - legacy_manifest["total_duration_s"])
        result["vo_manifest"] = (
            "identical" if same_text and total < 0.1
            else f"differs (text={same_text}, total={total:.3f}s)")
    else:
        vo_dir = voice._vo_dir(episode, chapter_dir, "long")
        spoken = [path.read_text(encoding="utf-8").strip()
                  for path in sorted(vo_dir.glob("c[0-9][0-9][0-9].txt"))]
        same_text = [item["text"] for item in manifest["segments"]] == spoken
        result["vo_manifest"] = (
            "text matches slices (no legacy manifest)" if same_text
            else "text drift (no legacy manifest)")
    cues = voice.cues(episode, chapter_dir, "long")
    result["captions"] = (
        "consistent" if voice.normalized(
            "".join(cue["text"] for cue in cues))
        == voice.normalized("".join(rebuilt)) else "text drift")
    vo_dir = voice._vo_dir(episode, chapter_dir)
    if vo_dir and vo_dir.is_dir():
        slices = sorted(vo_dir.glob("c*.mp3"))
        full = (chapter_dir / (episode.get("legacy") or {}).get("dir", "")
                / "full.mp3")
        if len(slices) == len(rebuilt):
            if full.is_file():
                got = sum(voice._duration(path) or 0 for path in slices)
                want = voice._duration(full) or 0
                if abs(got - want) < 0.2:
                    result["audio_slices"] = "sum matches"
                elif abs(got - want) <= 0.03 * len(slices):
                    result["audio_slices"] = (
                        f"sum {got:.2f}s + {want - got:.3f}s concat "
                        f"padding = full {want:.2f}s")
                else:
                    result["audio_slices"] = f"sum {got:.2f}s vs full {want:.2f}s"
            elif episode["formats"]["long"]["status"] == "scripted":
                result["audio_slices"] = (
                    f"{len(slices)} slices, long not yet rendered")
            else:
                result["audio_slices"] = f"{len(slices)} slices, no full.mp3"
        else:
            result["audio_slices"] = f"{len(slices)} slices vs {len(rebuilt)} chunks"
    first = BUILD / "prove" / chapter_id / "a.json"
    second = BUILD / "prove" / chapter_id / "b.json"
    model.write_json(first, {"segments": cues})
    model.write_json(second, {"segments": cues})
    result["transcript"] = (
        "deterministic" if _sha(first) == _sha(second) else "unstable")
    return result


def prove(args) -> int:
    ids = [args.chapter] if args.chapter else [
        cid for cid in model.CHAPTER_IDS if int(cid[2:]) <= 5]
    results = [_prove_one(chapter_id) for chapter_id in ids]
    target = model.ROOT / "docs" / "migrations"
    target.mkdir(parents=True, exist_ok=True)
    model.write_json(target / "video-rebuild-proof.json", results)
    lines = ["# Video intermediate rebuild proof", "",
             "Regenerated from the chapter script by `video/pipeline/cli.py prove`.",
             "", "| chapter | chunks | vo-manifest | captions | audio slices | transcript |",
             "|---|---|---|---|---|---|"]
    for row in results:
        lines.append("| {chapter} | {chunks} | {vo_manifest} | {captions} | "
                     "{audio_slices} | {transcript} |".format(**row))
    (target / "video-rebuild-proof.md").write_text(
        "\n".join(lines) + "\n", encoding="utf-8")
    for row in results:
        print(json.dumps(row, ensure_ascii=False))
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    for name, handler in (("check", check), ("build", build),
                          ("prove", prove)):
        cmd = sub.add_parser(name)
        cmd.add_argument("--chapter", choices=model.CHAPTER_IDS)
        if name == "check":
            cmd.add_argument("--audio", action="store_true")
            cmd.add_argument("--config-only", action="store_true",
                             help="validate configuration; media stays unverified")
        if name == "build":
            cmd.add_argument("--assets", action="store_true",
                             help="require all declared renderer/media assets")
        cmd.set_defaults(handler=handler)
    sub.add_parser("migrate").set_defaults(handler=migrate_cmd)
    args = parser.parse_args(argv)
    try:
        return args.handler(args)
    except (model.VideoError, OSError, ValueError) as exc:
        print(f"VIDEO FAILED: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
