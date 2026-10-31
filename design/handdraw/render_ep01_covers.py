#!/usr/bin/env python3
"""Re-snapshot the EP.01 landscape / vertical covers.

`videos/{landscape,vertical}/compositions/cover.html` are HyperFrames template
fragments that no project index mounts, so `hyperframes snapshot` cannot reach
them. Their timeline is a paused Ken Burns (scale 1 -> 1.03 at t=0), so the
static markup *is* the cover frame: lift the <template> body into a plain page
and screenshot it.

The two shipped webp files lagged the compositions (missing EP numeral,
subtitle, dark card and CTA), which is why this script exists.

    python design/handdraw/render_ep01_covers.py
"""

from __future__ import annotations

import os
import re
import subprocess
import tempfile
from pathlib import Path

from PIL import Image

CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
ROOT = Path(__file__).resolve().parents[2]
STILLS = ROOT / "design" / "handdraw" / "renders"

# (composition, width, height, still name, webp deliverable)
JOBS = [
    ("videos/landscape/compositions/cover.html", 1920, 1080, "ep01-landscape-16x9.png",
     "deliverables/landscape-cover.webp"),
    ("videos/vertical/compositions/cover.html", 1080, 1920, "ep01-vertical-9x16.png",
     "deliverables/vertical-cover.webp"),
]


def standalone(src: Path, width: int, height: int, out: Path) -> Path:
    html = src.read_text(encoding="utf-8")
    match = re.search(r"<template>(.*?)</template>", html, re.S)
    if not match:
        raise SystemExit(f"{src}: no <template> block")
    body = re.sub(r"<script>.*?</script>", "", match.group(1), flags=re.S)
    out.write_text(
        "<!doctype html><html><head><meta charset='utf-8'>"
        f"<style>html,body{{margin:0;padding:0;width:{width}px;height:{height}px;overflow:hidden}}</style>"
        f"</head><body>{body}</body></html>",
        encoding="utf-8",
    )
    return out


def capture(page: Path, width: int, height: int, png: Path, attempts: int = 3) -> Path:
    """Screenshot with a throwaway profile: a shared --user-data-dir makes Chrome's
    singleton lock drop the second capture silently."""
    for attempt in range(1, attempts + 1):
        if png.exists():
            png.unlink()
        profile = tempfile.mkdtemp(prefix="cover-chrome-")
        subprocess.run(
            [
                CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars",
                "--disable-extensions", "--no-first-run", "--no-default-browser-check",
                "--force-device-scale-factor=1", f"--user-data-dir={profile}",
                f"--window-size={width},{height}", f"--screenshot={png}",
                "file:///" + str(page).replace(os.sep, "/"),
            ],
            capture_output=True,
            timeout=90,
        )
        if png.exists() and png.stat().st_size > 10_000:
            return png
        print(f"  attempt {attempt} produced nothing, retrying")
    raise SystemExit(f"could not capture {page}")


def main() -> None:
    STILLS.mkdir(parents=True, exist_ok=True)
    tmp = Path(tempfile.mkdtemp(prefix="ep01-cover-"))
    for rel, w, h, still, deliverable in JOBS:
        src = ROOT / rel
        page = standalone(src, w, h, tmp / (still.replace(".png", ".html")))
        png = capture(page, w, h, STILLS / still)
        with Image.open(png) as im:
            if im.size != (w, h):
                raise SystemExit(f"{still}: got {im.size}, want {(w, h)}")
            im.convert("RGB").save(ROOT / deliverable, "WEBP", quality=92, method=6)
        print(f"{still:26} {w}x{h}  ->  {deliverable}")


if __name__ == "__main__":
    main()
