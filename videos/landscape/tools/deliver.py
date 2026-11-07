#!/usr/bin/env python3
"""Downscale a 4K supersampled master to the 1080p platform delivery.

Render the master first (Chrome deviceScaleFactor supersampling keeps the
layout, then Lanczos downscaling recovers crisp text edges):

    npm run render:4k

Then:

    npm run deliver -- renders/<master>.mp4

The 4K master is kept for platforms that accept 4K (Bilibili); Douyin and
WeChat Channels cap at 1080p and use the derived file.
"""

import subprocess
import sys
from pathlib import Path


def probe_size(path: Path) -> tuple[int, int]:
    out = subprocess.run(
        [
            "ffprobe",
            "-v",
            "error",
            "-select_streams",
            "v:0",
            "-show_entries",
            "stream=width,height",
            "-of",
            "csv=p=0",
            str(path),
        ],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    width, height = out.split(",")
    return int(width), int(height)


def main() -> int:
    if len(sys.argv) != 2:
        print(__doc__.strip(), file=sys.stderr)
        return 2

    master = Path(sys.argv[1])
    if not master.is_file():
        print(f"missing master: {master}", file=sys.stderr)
        return 1

    width, height = probe_size(master)
    if width >= height:
        target = (1920, 1080)
    else:
        target = (1080, 1920)
    if (width, height) == target:
        print(f"{master} is already {target[0]}x{target[1]}", file=sys.stderr)
        return 1

    stem = master.stem.removesuffix("_4k_master")
    output = master.with_name(f"{stem}_1080p_delivery.mp4")
    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-v",
            "error",
            "-i",
            str(master),
            "-vf",
            f"scale={target[0]}:{target[1]}:flags=lanczos+accurate_rnd+full_chroma_int",
            "-c:v",
            "libx264",
            "-preset",
            "slow",
            "-crf",
            "13",
            "-pix_fmt",
            "yuv420p",
            "-profile:v",
            "high",
            "-level",
            "4.2",
            "-colorspace",
            "bt709",
            "-color_primaries",
            "bt709",
            "-color_trc",
            "bt709",
            "-movflags",
            "+faststart",
            "-c:a",
            "copy",
            str(output),
        ],
        check=True,
    )
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
