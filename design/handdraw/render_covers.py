#!/usr/bin/env python3
"""Render the hand-drawn episode covers to every platform size.

Source art lives in `design/handdraw/covers/<ep>.html` and shares
`cover.css` (paper / ink / marker / hard-shadow tokens lifted from the video
hand-drawn layer, see design/handdraw/motion-language.md §3).

    python design/handdraw/render_covers.py --out design/handdraw/renders

Each still is captured with headless Chrome at the exact target size. Chrome
refuses to run two captures at once against the same profile, so every call
gets a throwaway --user-data-dir and the script waits for the PNG to land.
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
COVERS = ROOT / "design" / "handdraw" / "covers"
CHROME = Path(r"C:\Program Files\Google\Chrome\Application\chrome.exe")

# (name, width, height) — the three platform crops the episodes ship
RATIOS = [("16x9", 1920, 1080), ("4x3", 1440, 1080), ("3x4", 1080, 1440)]
EPISODES = ["ep02", "ep03", "ep04"]


def capture(html: Path, out: Path, width: int, height: int, attempts: int = 3) -> None:
    out.parent.mkdir(parents=True, exist_ok=True)
    for attempt in range(1, attempts + 1):
        if out.exists():
            out.unlink()
        profile = Path(tempfile.mkdtemp(prefix="cover-chrome-"))
        try:
            proc = subprocess.run(
                [
                    str(CHROME),
                    "--headless=new",
                    "--disable-gpu",
                    "--hide-scrollbars",
                    "--disable-extensions",
                    "--no-first-run",
                    "--no-default-browser-check",
                    "--force-device-scale-factor=1",
                    f"--user-data-dir={profile}",
                    f"--screenshot={out}",
                    f"--window-size={width},{height}",
                    html.as_uri(),
                ],
                capture_output=True,
                text=True,
                timeout=90,
            )
        except subprocess.TimeoutExpired:
            proc = None
        finally:
            shutil.rmtree(profile, ignore_errors=True)

        if out.exists() and out.stat().st_size > 0:
            return
        # Chrome lost the singleton lock or the page never painted; retry.
        time.sleep(1.2 * attempt)
    detail = (proc.stderr or "").strip().splitlines()[-1:] if proc else ["timeout"]
    raise SystemExit(f"render failed for {out.name}: {detail}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default=str(ROOT / "design" / "handdraw" / "renders"))
    parser.add_argument("--only", nargs="*", default=None, help="limit to these episode ids")
    args = parser.parse_args()

    out_dir = Path(args.out)
    episodes = args.only or EPISODES
    for ep in episodes:
        html = COVERS / f"{ep}.html"
        if not html.is_file():
            raise SystemExit(f"missing cover source: {html}")
        for name, width, height in RATIOS:
            target = out_dir / f"{ep}-{name}.png"
            capture(html, target, width, height)
            print(f"{target.relative_to(ROOT) if target.is_relative_to(ROOT) else target}  {width}x{height}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
