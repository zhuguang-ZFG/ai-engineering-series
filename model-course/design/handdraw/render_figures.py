"""Rasterise hand-drawn figure SVGs to PNG for visual review.

Usage: python design/handdraw/render_figures.py llm-work agent-loop ...
       python design/handdraw/render_figures.py --all
"""

import re
import subprocess
import sys
import tempfile
from pathlib import Path

CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
ROOT = Path(__file__).resolve().parents[2]
SVG_DIR = ROOT / "book" / "assets" / "handdraw"
OUT_DIR = ROOT / "design" / "handdraw" / "renders"
TOKENS = ROOT / "design" / "system" / "tokens.css"

SIZE_RE = re.compile(r'(?<![-\w])(width|height)\s*=\s*"(\d+(?:\.\d+)?)"')
HEX_RE = re.compile(r'#[0-9a-fA-F]{6}')


def allowed_colors() -> set:
    """tokens.css is the single source of truth; a figure may not invent a colour."""
    return {h.lower() for h in HEX_RE.findall(TOKENS.read_text(encoding="utf-8"))}


def check_tokens(path: Path) -> None:
    allowed = allowed_colors()
    text = path.read_text(encoding="utf-8")
    stray = {h.lower() for h in HEX_RE.findall(text)} - allowed
    if stray:
        raise SystemExit(
            f"{path.name}: off-token {', '.join(sorted(stray))} — add it to "
            f"design/system/tokens.css and measure it in contrast.mjs, or use a token"
        )
    # role misuse: the retired bright green/orange pair stays banned on text; the
    # cinnabar accent (#B4472F) passes accentInk and may carry small text.
    bad = re.findall(r'<text[^>]*fill="(#1f883d|#e2601f)"', text)
    if bad:
        raise SystemExit(
            f"{path.name}: {len(bad)} text run(s) in retired display colours {sorted(set(bad))} "
            f"— use #B4472F (accent-ink) or a token; the bright green/orange pair is retired"
        )


def svg_size(path: Path):
    head = path.read_text(encoding="utf-8")[:4000]
    tag = head[head.find("<svg") : head.index(">", head.find("<svg")) + 1]
    found = {k: int(float(v)) for k, v in SIZE_RE.findall(tag)}
    if "width" in found and "height" in found:
        return found["width"], found["height"]
    box = re.search(r'viewBox="[\d.\-]+\s+[\d.\-]+\s+([\d.]+)\s+([\d.]+)"', tag)
    if box:
        return int(float(box.group(1))), int(float(box.group(2)))
    raise SystemExit(f"{path.name}: no width/height or viewBox")


def render(slug: str) -> Path:
    svg = SVG_DIR / f"{slug}.svg"
    if not svg.exists():
        raise SystemExit(f"missing {svg}")
    check_tokens(svg)
    width, height = svg_size(svg)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    png = OUT_DIR / f"hd-{slug}.png"
    with tempfile.TemporaryDirectory(prefix="hd-shot-") as profile:
        subprocess.run(
            [
                CHROME,
                "--headless=new",
                "--disable-gpu",
                "--hide-scrollbars",
                "--force-device-scale-factor=1",
                f"--user-data-dir={profile}",
                f"--window-size={width},{height}",
                f"--screenshot={png}",
                svg.as_uri(),
            ],
            check=True,
            capture_output=True,
        )
    if not png.exists() or png.stat().st_size < 5000:
        raise SystemExit(f"{png} rendered empty")
    print(f"{slug}: {width}x{height} -> {png.relative_to(ROOT)}")
    return png


def main() -> None:
    args = sys.argv[1:]
    if not args:
        raise SystemExit(__doc__)
    slugs = sorted(p.stem for p in SVG_DIR.glob("*.svg")) if args == ["--all"] else args
    for slug in slugs:
        render(slug)


if __name__ == "__main__":
    main()
