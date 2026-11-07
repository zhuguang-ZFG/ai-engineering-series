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
    from pipeline import composition, content, migrate, model, proof, quality, timeline, voice
else:
    from . import composition, content, migrate, model, proof, quality, timeline, voice

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
            f"{chapter_id}: content pack is stale; rerun cli.py refresh")

    scenes = composition.scene_plan(episode, scenes, generated_pack)
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


def _write_build(report: dict, root: Path = BUILD) -> Path:
    chapter_id = report["chapter"]
    out = root / chapter_id
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
    hashes.update(composition.write_compositions(out, episode, report["scenes"]))
    cover = composition.cover(out, episode, pack)
    model.write_json(out / "cover-manifest.json", cover)
    hashes["cover.svg"] = cover["sha256"]
    hashes["cover-manifest.json"] = _sha(out / "cover-manifest.json")
    path = out / "timeline.json"
    model.write_json(path, timeline.build(episode, report["scenes"],
                                           report["cues"]))
    hashes[path.name] = _sha(path)
    if report["compat"]["formats"]:
        path = out / "compat-report.json"
        model.write_json(path, report["compat"])
        hashes[path.name] = _sha(path)
    model.write_json(out / "manifest.json",
                     {"schema_version": 1, "chapter": chapter_id,
                      "version": content._model().version,
                      "media_verification": "unverified; use check --audio with real assets",
                      "sha256": hashes})
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
    level = "configuration" if args.config_only else "asset"
    print(f"video {level} check: {len(ids) - failures}/{len(ids)} chapters clean")
    if args.config_only:
        print("media: UNVERIFIED (audio, frames and render quality not exercised)")
    return 1 if failures else 0


def build(args) -> int:
    ids = [args.chapter] if args.chapter else list(model.CHAPTER_IDS)
    for chapter_id in ids:
        report = _report(chapter_id, config_only=not args.assets)
        if report["errors"]:
            for error in report["errors"]:
                print(f"error: {error}", file=sys.stderr)
            return 1
        out = _write_build(report, Path(args.out_dir) if args.out_dir else BUILD)
        print(f"{chapter_id}: wrote {out}")
    return 0


def refresh(args) -> int:
    ids = [args.chapter] if args.chapter else list(model.CHAPTER_IDS)
    for chapter_id in ids:
        content.write_pack(chapter_id, model.CHAPTERS / chapter_id)
        print(f"{chapter_id}: refreshed source content pack")
    return 0


def migrate_cmd(args) -> int:
    reports = migrate.create_all()
    for report in reports:
        print(json.dumps(report, ensure_ascii=False))
    return 0




def prove(args) -> int:
    ids = [args.chapter] if args.chapter else [
        cid for cid in model.CHAPTER_IDS if int(cid[2:]) <= 5]
    results = [{"chapter": chapter_id,
                "rebuild": proof.rebuild(chapter_id, config_only=args.config_only)}
               for chapter_id in ids]
    target = Path(args.out_dir) if args.out_dir else BUILD / "proof"
    target.mkdir(parents=True, exist_ok=True)
    model.write_json(target / "video-rebuild-proof.json", results)
    for row in results:
        print(json.dumps(row, ensure_ascii=False))
    return 0 if all(row["rebuild"]["status"] == "identical" for row in results) else 1


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    for name, handler in (("check", check), ("build", build),
                          ("prove", prove), ("refresh", refresh)):
        cmd = sub.add_parser(name)
        cmd.add_argument("--chapter", choices=model.CHAPTER_IDS)
        if name in ("build", "prove"):
            cmd.add_argument("--out-dir", help="write derived products outside source directories")
        if name == "prove":
            cmd.add_argument("--config-only", action="store_true",
                             help="rebuild source products; do not claim media verification")
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
