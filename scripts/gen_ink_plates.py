#!/usr/bin/env python3
"""Generate reviewable large plates from the bilingual illustration manual.

Small emblems and explanatory figures remain hand-drawn SVG. Large plates use
graded black ink on transparency; binary conversion is available for explicit
small samples. Credentials come only from NEWAPI_URL / NEWAPI_KEY. Generation
requires an explicit output directory, and never installs files into the book.
Completed raw renders are retained and reused; an uncertain paid POST is never
automatically repeated. --dry-run needs neither credentials nor network.
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import http.client
import io
import json
import os
import pathlib
import re
import sys
import urllib.error
import urllib.request

from PIL import Image, ImageFilter, ImageOps

ROOT = pathlib.Path(__file__).resolve().parents[1]
MANUAL = ROOT / "docs" / "illustration-prompts.md"
ART_DIR = ROOT / "yuyu-book" / "illustrations"

PREAMBLE = (
    "书籍内页手绘插画，炭黑与灰阶，钢笔排线结合东方毛笔笔压，"
    "自然宽窄变化、少量飞白、疏密有致的明暗层次。\n"
    "保留题材中的所有主体和关系；画幅四周留宽松空白，轮廓完整，"
    "线稿清楚，细节适合印刷。透明背景，画面仅由图形组成。\n"
)

# A slot's shape decides the canvas: a 64 px emblem is drawn square, a part
# headpiece and the cover plate are drawn wide.
EMBLEM = ("emblem", 512, "1024x1024")
WIDE = ("wide", 900, "1536x1024")
COVER = ("cover", 1400, "1536x1024")


def plates(product: str = "book") -> list[dict]:
    """Read each section's own prompt without borrowing the next section."""
    if product not in {"book", "omp", "both"}:
        raise ValueError(f"unknown product: {product}")
    text = MANUAL.read_text(encoding="utf-8")
    sections = list(re.finditer(r"^### .*?`(?P<name>[a-z0-9-]+)\.svg`", text, re.M))
    out = []
    for index, match in enumerate(sections):
        name = match.group("name")
        companion = name.startswith("part-omp-")
        if not (_is_plate(name) or companion):
            continue
        if product != "both" and companion != (product == "omp"):
            continue
        end = sections[index + 1].start() if index + 1 < len(sections) else len(text)
        fence = re.search(r"```text\n(?P<prompt>.*?)```", text[match.end():end], re.S)
        if fence is None:
            raise SystemExit(f"{name}: no prompt block in its manual section")
        lines = [line for line in fence.group("prompt").splitlines()
                 if not line.startswith("参考作者/风格名称：")]
        prompt = " ".join(" ".join(lines).split())
        kind, width, size = _shape(name)
        out.append({"name": name, "kind": kind, "width": width,
                    "size": size, "prompt": prompt})
    expected = {"book": 26, "omp": 7, "both": 33}[product]
    if len(out) != expected or len({job["name"] for job in out}) != expected:
        raise SystemExit(f"the manual must name {expected} unique {product} plates")
    return out


def _is_plate(name: str) -> bool:
    """The book's own 26 plates, as against the omp tray's prompts, which the
    manual also carries but this book does not ship."""
    return (name in {"front", "keeper", "cover"}
            or re.fullmatch(r"ch\d{2}", name) is not None
            or re.fullmatch(r"apx[a-z]", name) is not None
            or re.fullmatch(r"part-p\d", name) is not None)


def _shape(name: str) -> tuple[str, int, str]:
    if name == "cover":
        return COVER
    if name.startswith("part-"):
        return WIDE
    return EMBLEM


def credentials() -> tuple[str, str] | None:
    url = os.environ.get("NEWAPI_URL", "").strip()
    key = os.environ.get("NEWAPI_KEY", "").strip()
    return (url.rstrip("/"), key) if url and key else None


def generate(base: str, key: str, model: str, prompt: str, size: str) -> bytes:
    payload = {"model": model, "prompt": PREAMBLE + "\n" + prompt,
               "n": 1, "size": size, "background": "transparent"}
    request = urllib.request.Request(
        base + "/v1/images/generations",
        data=json.dumps(payload).encode(),
        headers={"Authorization": "Bearer " + key,
                 "Content-Type": "application/json"},
    )
    body = _read_channel(request)
    item = json.loads(body)["data"][0]
    if item.get("b64_json"):
        return base64.b64decode(item["b64_json"])
    if item.get("url"):
        with urllib.request.urlopen(item["url"], timeout=600) as response:
            return response.read()
    raise SystemExit("the channel returned neither b64_json nor a url")


def _read_channel(request: urllib.request.Request) -> bytes:
    """Send a paid generation once; an interrupted reply may still be billed."""
    try:
        with urllib.request.urlopen(request, timeout=600) as response:
            return response.read()
    except urllib.error.HTTPError as exc:
        raise SystemExit(f"image request refused (HTTP {exc.code}); not retried") from exc
    except (urllib.error.URLError, OSError, http.client.IncompleteRead) as exc:
        raise SystemExit(
            f"image response incomplete ({type(exc).__name__}); inspect the request "
            "before generating again") from exc


def _threshold(gray: Image.Image) -> Image.Image:
    """Otsu on the histogram: the model's paper is uniform, so one cut between
    paper and ink keeps a thin stroke and drops a grey halo."""
    hist = gray.histogram()
    total = sum(hist)
    if not total:
        return gray
    sum_all = sum(level * count for level, count in enumerate(hist))
    weight_bg = 0
    sum_bg = 0.0
    best, cut = -1.0, 128
    for level, count in enumerate(hist):
        weight_bg += count
        if not weight_bg:
            continue
        weight_fg = total - weight_bg
        if not weight_fg:
            break
        sum_bg += level * count
        mean_bg = sum_bg / weight_bg
        mean_fg = (sum_all - sum_bg) / weight_fg
        between = weight_bg * weight_fg * (mean_bg - mean_fg) ** 2
        if between > best:
            best, cut = between, level
    return gray.point(lambda value: 0 if value <= cut else 255)


def to_plate(raw: bytes, width: int) -> bytes:
    """Composite a render onto paper, then extract transparent binary ink."""
    with Image.open(io.BytesIO(raw)) as source:
        paper = Image.new("RGBA", source.size, (255, 255, 255, 255))
        paper.alpha_composite(source.convert("RGBA"))
        # paper grain turns into pepper at one bit; a median pass drops a dot
        # smaller than a hair before the threshold commits it to ink
        gray = paper.convert("L").filter(ImageFilter.MedianFilter(5))
        ink = _threshold(gray)
        ratio = width / ink.width
        size = (width, max(1, round(ink.height * ratio)))
        ink = ink.resize(size, Image.LANCZOS).point(
            lambda value: 0 if value < 128 else 255)
        plate = Image.new("RGBA", size, (0, 0, 0, 255))
        plate.putalpha(ink.point(lambda value: 255 - value))
        buffer = io.BytesIO()
        plate.save(buffer, "PNG", optimize=True)
        return buffer.getvalue()


def to_tonal_plate(raw: bytes, width: int, height: int, levels: int = 64) -> bytes:
    """Keep brush shading as black ink with graded alpha in a fixed canvas."""
    with Image.open(io.BytesIO(raw)) as source:
        paper = Image.new("RGBA", source.size, (255, 255, 255, 255))
        paper.alpha_composite(source.convert("RGBA"))
        ink = ImageOps.invert(paper.convert("L"))
        ink = ImageOps.contain(ink, (width, height), Image.Resampling.LANCZOS)
        # Graded alpha keeps shading without carrying paper grain as millions
        # of nearly identical colours in the offline HTML. Sixty-four levels
        # hold a brush; fewer are the fallback when a wide plate runs long.
        span = max(1, levels - 1)
        ink = ink.point(lambda value: round(round(value * span / 255) * 255 / span))
        alpha = Image.new("L", (width, height), 0)
        alpha.paste(ink, ((width - ink.width) // 2, (height - ink.height) // 2))
        plate = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        plate.putalpha(alpha)
        buffer = io.BytesIO()
        plate.save(buffer, "PNG", optimize=True)
        return buffer.getvalue()


def to_tonal_plate_within(raw: bytes, width: int, height: int, budget: int,
                          levels=(64, 48, 32, 24, 16, 12)) -> tuple[bytes, int]:
    """The finest alpha grading whose PNG still fits the inlining budget.

    A wide plate at sixty-four levels can land just over the ceiling; grading
    coarser costs a little shading, while cropping or shrinking would cost the
    subject. Refuses rather than shipping a plate the book cannot afford.
    """
    tried = []
    for level in levels:
        plate = to_tonal_plate(raw, width, height, levels=level)
        if len(plate) <= budget:
            return plate, level
        tried.append((level, len(plate)))
    raise ValueError(f"even {levels[-1]} levels reach {tried[-1][1]} bytes, "
                     f"over the {budget} budget: {tried}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--product", choices=("book", "omp", "both"), default="book")
    parser.add_argument("--only", default="", help="explicit comma-separated sample names")
    parser.add_argument("--out", type=pathlib.Path, help="review directory outside the book")
    parser.add_argument("--model", default="gpt-image-2.6-sunburst")
    parser.add_argument("--keep-raw", type=pathlib.Path, help="raw archive (default: OUT/raw)")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)
    jobs = plates(args.product)
    wanted = {name.strip() for name in args.only.split(",") if name.strip()}
    if wanted:
        missing = wanted - {job["name"] for job in jobs}
        if missing:
            parser.error(f"unknown plates: {sorted(missing)}")
        jobs = [job for job in jobs if job["name"] in wanted]
    else:
        jobs = [job for job in jobs if job["kind"] != "emblem"]
    key = credentials()
    if key is not None and not args.dry_run and args.out is None:
        parser.error("generation requires --out for review; nothing is installed automatically")
    for job in jobs:
        print(f"{job['name']:<16} {job['width']:>4}px {job['size']:<9}", flush=True)
        if args.dry_run or key is None:
            continue
        out = args.out
        path = out / f"{job['name']}.png"
        if path.exists():
            print(f"  retained {path}; no new request", flush=True)
            continue
        keep = args.keep_raw or out / "raw"
        raw_path = keep / f"{job['name']}-raw.png"
        record_path = keep / f"{job['name']}.json"
        prompt = job["prompt"]
        if job["kind"] == "cover":
            prompt += " 横向宽景构图，主体位于画幅中部，宽高约二比一。"
        request_record = {"model": args.model, "size": job["size"],
                          "prompt": PREAMBLE + "\n" + prompt, "background": "transparent"}
        keep.mkdir(parents=True, exist_ok=True)
        if record_path.exists():
            record = json.loads(record_path.read_text(encoding="utf-8"))
            if record["request"] != request_record:
                raise SystemExit(f"{job['name']}: archived prompt differs; choose a new review directory")
            if not raw_path.exists():
                raise SystemExit(f"{job['name']}: earlier request is unresolved; not repeated")
            raw = raw_path.read_bytes()
        else:
            record = {"request": request_record, "status": "requested"}
            record_path.write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8")
            raw = generate(key[0], key[1], args.model, prompt, job["size"])
            raw_path.write_bytes(raw)
        if job["kind"] == "emblem":
            plate = to_plate(raw, job["width"])
            budget = 60_000
            levels = None
        else:
            height = 658 if job["kind"] == "cover" else 630
            budget = 400_000 if job["kind"] == "cover" else 200_000
            try:
                plate, levels = to_tonal_plate_within(
                    raw, job["width"], height, budget)
            except ValueError as exc:
                raise SystemExit(f"{job['name']}: {exc}; raw retained") from exc
        if len(plate) > budget:
            raise SystemExit(f"{job['name']}: {len(plate)} bytes exceeds {budget}; raw retained")
        out.mkdir(parents=True, exist_ok=True)
        path.write_bytes(plate)
        with Image.open(io.BytesIO(raw)) as source:
            record["returned_size"] = list(source.size)
        record.update(status="complete", raw_sha256=hashlib.sha256(raw).hexdigest(),
                      plate_sha256=hashlib.sha256(plate).hexdigest(), plate_bytes=len(plate),
                      alpha_levels=levels)
        record_path.write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"  -> {path} {len(plate)} bytes", flush=True)
    return 0




if __name__ == "__main__":
    sys.exit(main())
