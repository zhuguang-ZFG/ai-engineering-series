"""Deterministic scene/cover assembly from canonical chapter packs.

A scripted package is a renderable storyboard, not a claimed audio recording.
Existing built projects keep their exact composition paths and timing witnesses.
"""
from __future__ import annotations

import hashlib
from html import escape

from . import content, model


def scene_plan(episode: dict, scenes: dict, pack: dict) -> dict:
    result = {**scenes, "formats": dict(scenes.get("formats") or {})}
    sections = pack["sections"]
    for fmt, spec in episode["formats"].items():
        if result["formats"].get(fmt):
            continue
        selected = sections if fmt == "long" else sections[:3]
        cards = [{"title": pack["title"], "summary": " · ".join(
            term["zh"] for term in pack["core_terms"][:4])}] + selected
        if not cards:
            raise model.VideoError(f"{episode['id']}: no source content for scenes")
        step = spec["duration_s"] / len(cards)
        result["formats"][fmt] = [{
            "id": f"{fmt}-{index + 1:02d}",
            "start_s": round(index * step, 3),
            "duration_s": round((index + 1) * step, 3) - round(index * step, 3),
            "intent": "hook" if index == 0 else "section",
            "source": f"compositions/{fmt}-{index + 1:02d}.html",
            "title": card["title"], "summary": card["summary"],
        } for index, card in enumerate(cards)]
    return result


def write_compositions(out, episode: dict, scenes: dict) -> dict:
    files = {}
    for fmt, items in scenes["formats"].items():
        for scene in items:
            if "title" not in scene:
                continue
            spec = episode["formats"][fmt]
            path = out / scene["source"]
            path.parent.mkdir(parents=True, exist_ok=True)
            page = (f'<!doctype html><html lang="zh-CN"><meta charset="utf-8">'
                    f'<title>{escape(scene["title"])}</title><style>'
                    'body{margin:0;background:#FBF7EF;color:#26221B;font-family:serif;'
                    'display:flex;flex-direction:column;justify-content:center;box-sizing:border-box;'
                    f'width:{spec["width"]}px;height:{spec["height"]}px;padding:8%;}}'
                    'h1{font-size:64px;line-height:1.3}p{font-size:38px;line-height:1.7}'
                    '</style><main><h1>' + escape(scene["title"]) + '</h1><p>'
                    + escape(scene["summary"]) + '</p></main></html>')
            path.write_text(page, encoding="utf-8")
            files[path.relative_to(out).as_posix()] = hashlib.sha256(path.read_bytes()).hexdigest()
    return files


def cover(out, episode: dict, pack: dict) -> dict:
    title = escape(pack["title"])
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1280 720" '
           f'role="img" aria-label="{title}"><rect width="1280" height="720" fill="#FBF7EF"/>'
           '<path d="M90 100H1190M90 620H1190" stroke="#B4472F" stroke-width="5"/>'
           f'<text x="100" y="200" font-family="serif" font-size="36" fill="#5C5448">'
           f'御舆 · {episode["id"]}</text>')
    # Controlled wrapping keeps the composition inside the declared safe rectangle.
    for index, start in enumerate(range(0, len(pack["title"]), 17)):
        line = escape(pack["title"][start:start + 17])
        svg += f'<text x="100" y="{310 + index * 72}" font-family="serif" font-size="56" fill="#26221B">{line}</text>'
    svg += '</svg>'
    path = out / "cover.svg"
    path.write_text(svg, encoding="utf-8")
    return {"schema_version": 1, "chapter": episode["id"], "path": path.name,
            "width": 1280, "height": 720, "source": pack["source"],
            "rights": episode["rights"], "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}
