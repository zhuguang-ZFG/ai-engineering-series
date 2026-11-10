#!/usr/bin/env python3
"""Extract one printed text line from a local image with a local TrOCR directory.

This is a teaching example, not a document-understanding service. It reads the
image locally, never downloads a model, never reads credentials, and never
invents recognised text. A non-empty string is returned only by the model.

The --authorized flag is a human assertion that you have the right to process
the image. The program cannot verify a licence or consent; without the flag it
refuses before opening the image or touching the model directory.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
import time
from pathlib import Path
from typing import Any

SCHEMA = "ocr-extract/1"
DEFAULT_MIN_MEAN_LOGPROB = -2.5


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def write_report(report: dict[str, Any], output: Path) -> int:
    try:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(
            json.dumps(report, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
    except OSError as exc:
        print(f"cannot write report to {output}: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 2
    summary: dict[str, Any] = {
        "status": report["status"],
        "output": str(output),
    }
    if report.get("text") is not None:
        summary["text"] = report["text"]
    if report.get("error"):
        summary["error"] = report["error"]
    print(json.dumps(summary, ensure_ascii=False))
    return 0


def fail(
    output: Path,
    status: str,
    exit_code: int,
    message: str,
    *,
    warnings: list[str] | None = None,
    image: dict[str, Any] | None = None,
    region: dict[str, Any] | None = None,
    model: dict[str, Any] | None = None,
    timing: dict[str, Any] | None = None,
) -> int:
    report: dict[str, Any] = {
        "schema": SCHEMA,
        "status": status,
        "text": None,
        "confidence": None,
        "confidence_note": (
            "TrOCR does not expose a calibrated recognition confidence. "
            "mean_token_logprob is a model-internal sequence score, not an "
            "accuracy, probability of correctness, or guarantee."
        ),
        "image": image,
        "region": region,
        "model": model,
        "generation": None,
        "scores": None,
        "timing_ms": timing,
        "warnings": warnings or [],
        "error": {"message": message},
    }
    if write_report(report, output) != 0:
        return 2
    return exit_code


def parse_region(raw: str | None, width: int, height: int) -> tuple[int, int, int, int]:
    if raw is None:
        return 0, 0, width, height
    pieces = [piece.strip() for piece in raw.split(",")]
    if len(pieces) != 4:
        raise ValueError("region must be X,Y,W,H")
    try:
        x, y, w, h = (int(piece) for piece in pieces)
    except ValueError as exc:
        raise ValueError("region coordinates must be integers") from exc
    if w <= 0 or h <= 0:
        raise ValueError("region width and height must be positive")
    if x < 0 or y < 0 or x + w > width or y + h > height:
        raise ValueError(
            f"region ({x},{y},{w},{h}) is outside image bounds ({width}x{height})"
        )
    return x, y, w, h


def looks_like_text(text: str) -> bool:
    return any(character.isalnum() for character in text)


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Extract one printed text line from a local image with a local TrOCR "
            "directory. No network access and no model download."
        )
    )
    parser.add_argument("--image", required=True, help="local image file to read")
    parser.add_argument(
        "--model",
        default=None,
        help="local directory containing TrOCR processor and model files (or a full model directory)",
    )
    parser.add_argument("--output", required=True, help="write the JSON report to this path")
    parser.add_argument(
        "--authorized",
        action="store_true",
        help="assert that you have permission to process this image; required",
    )
    parser.add_argument(
        "--region",
        default=None,
        metavar="X,Y,W,H",
        help="optional crop in pixels, origin top-left; default is the full image",
    )
    parser.add_argument(
        "--max-new-tokens",
        type=int,
        default=64,
        help="generation budget for one line (1-512; default 64)",
    )
    parser.add_argument(
        "--min-mean-logprob",
        type=float,
        default=DEFAULT_MIN_MEAN_LOGPROB,
        help=(
            "mark a non-empty generation uncertain when its mean token log-probability "
            f"is below this value (default {DEFAULT_MIN_MEAN_LOGPROB}); this is an "
            "operational gate, not a calibrated confidence"
        ),
    )
    args = parser.parse_args()
    output = Path(args.output)

    if not 1 <= args.max_new_tokens <= 512:
        return fail(output, "invalid-arguments", 2, "--max-new-tokens must be in [1,512]")
    if not math.isfinite(args.min_mean_logprob):
        return fail(output, "invalid-arguments", 2, "--min-mean-logprob must be finite")

    # Authorisation is checked before opening the image or model directory.
    if not args.authorized:
        return fail(
            output,
            "unauthorized",
            2,
            "missing --authorized: confirm that you have permission to process this image",
        )

    model_dir = Path(args.model) if args.model else None
    if model_dir is None:
        return fail(output, "model-unavailable", 2, "no --model directory was supplied")
    if not model_dir.exists():
        return fail(output, "model-unavailable", 2, f"model directory does not exist: {model_dir}")
    if not model_dir.is_dir():
        return fail(output, "model-unavailable", 2, f"model path is not a directory: {model_dir}")
    config_sha256 = None
    config_path = model_dir / "config.json"
    if config_path.is_file():
        try:
            config_sha256 = sha256_file(config_path)
        except OSError:
            config_sha256 = None

    image_path = Path(args.image)
    if not image_path.exists():
        return fail(output, "invalid-image", 2, f"image does not exist: {image_path}")
    if not image_path.is_file():
        return fail(output, "invalid-image", 2, f"image path is not a file: {image_path}")

    try:
        original_sha256 = sha256_file(image_path)
    except OSError as exc:
        return fail(output, "invalid-image", 2, f"cannot read image bytes: {type(exc).__name__}: {exc}")

    try:
        from PIL import Image, UnidentifiedImageError
    except ImportError as exc:
        return fail(
            output,
            "dependency-unavailable",
            2,
            f"Pillow is required: {type(exc).__name__}: {exc}",
        )

    warnings: list[str] = []
    try:
        with Image.open(image_path) as opened:
            opened.load()
            format_name = opened.format
            width, height = opened.size
            mode = opened.mode
            if getattr(opened, "is_animated", False):
                warnings.append("animated image: only the first frame is used")
            rgb_image = opened.convert("RGB")
    except (UnidentifiedImageError, OSError, ValueError) as exc:
        return fail(
            output,
            "invalid-image",
            2,
            f"Pillow could not decode this image: {type(exc).__name__}: {exc}",
            warnings=warnings,
        )

    if width <= 0 or height <= 0:
        return fail(output, "invalid-image", 2, f"image has invalid dimensions: {width}x{height}")

    image_report: dict[str, Any] = {
        "path": str(image_path),
        "sha256": original_sha256,
        "width": width,
        "height": height,
        "mode": mode,
        "format": format_name,
    }

    try:
        x, y, w, h = parse_region(args.region, width, height)
    except ValueError as exc:
        return fail(output, "invalid-region", 2, str(exc), image=image_report)

    region_image = rgb_image.crop((x, y, x + w, y + h))
    region_report: dict[str, Any] = {
        "x": x,
        "y": y,
        "width": w,
        "height": h,
        "coordinate_system": "pixels, origin top-left",
        "sha256": hashlib.sha256(region_image.tobytes()).hexdigest(),
        "sha256_basis": "decoded RGB pixel bytes in this region",
    }
    if args.region is None:
        warnings.append("no --region supplied: the full image was passed to the line model")

    try:
        import torch
        from transformers import TrOCRProcessor, VisionEncoderDecoderModel
    except Exception as exc:  # pragma: no cover - depends on the reader's environment
        return fail(
            output,
            "dependency-unavailable",
            2,
            f"torch and transformers are required: {type(exc).__name__}: {exc}",
            warnings=warnings,
            image=image_report,
            region=region_report,
        )

    total_started = time.perf_counter()
    load_started = time.perf_counter()
    try:
        processor = TrOCRProcessor.from_pretrained(
            str(model_dir),
            local_files_only=True,
            trust_remote_code=False,
        )
        model = VisionEncoderDecoderModel.from_pretrained(
            str(model_dir),
            local_files_only=True,
            trust_remote_code=False,
        )
        model.eval()
    except Exception as exc:
        return fail(
            output,
            "model-unavailable",
            2,
            f"could not load local TrOCR files from {model_dir}: {type(exc).__name__}: {exc}",
            warnings=warnings,
            image=image_report,
            region=region_report,
        )
    load_ms = round((time.perf_counter() - load_started) * 1000.0, 1)

    model_report: dict[str, Any] = {
        "path": str(model_dir),
        "local_files_only": True,
        "trust_remote_code": False,
        "device": "cpu",
        "config_sha256": config_sha256,
        "max_new_tokens": args.max_new_tokens,
    }

    inference_started = time.perf_counter()
    try:
        pixel_values = processor(images=region_image, return_tensors="pt").pixel_values
        with torch.no_grad():
            generated = model.generate(
                pixel_values,
                max_new_tokens=args.max_new_tokens,
                do_sample=False,
                output_scores=True,
                return_dict_in_generate=True,
            )
    except Exception as exc:
        return fail(
            output,
            "inference-error",
            1,
            f"local generation failed: {type(exc).__name__}: {exc}",
            warnings=warnings,
            image=image_report,
            region=region_report,
            model=model_report,
            timing={"load_ms": load_ms},
        )
    inference_ms = round((time.perf_counter() - inference_started) * 1000.0, 1)

    tokenizer = getattr(processor, "tokenizer", None)
    try:
        if tokenizer is not None:
            text = tokenizer.batch_decode(generated.sequences, skip_special_tokens=True)[0].strip()
        else:
            text = processor.batch_decode(generated.sequences, skip_special_tokens=True)[0].strip()
    except Exception as exc:
        return fail(
            output,
            "inference-error",
            1,
            f"could not decode model output: {type(exc).__name__}: {exc}",
            warnings=warnings,
            image=image_report,
            region=region_report,
            model=model_report,
            timing={"load_ms": load_ms, "inference_ms": inference_ms},
        )

    mean_logprob: float | None = None
    scored_tokens = 0
    generated_tokens = int(generated.sequences.shape[-1]) if hasattr(generated.sequences, "shape") else 0
    try:
        transition_scores = model.compute_transition_scores(
            generated.sequences,
            generated.scores,
            normalize_logits=True,
        )
        scores = transition_scores[0].tolist()
        token_ids = generated.sequences[0].tolist()
        if len(scores) == len(token_ids) - 1:
            token_ids = token_ids[1:]
        if len(scores) != len(token_ids):
            warnings.append(
                "token scores and generated token ids have different lengths; scores were not used"
            )
        else:
            pad_id = getattr(tokenizer, "pad_token_id", None) if tokenizer is not None else None
            values = [
                float(score)
                for token_id, score in zip(token_ids, scores)
                if math.isfinite(float(score)) and (pad_id is None or token_id != pad_id)
            ]
            if values:
                mean_logprob = round(sum(values) / len(values), 4)
                scored_tokens = len(values)
    except Exception as exc:
        warnings.append(f"sequence scores unavailable: {type(exc).__name__}: {exc}")

    scores_report: dict[str, Any] = {
        "mean_token_logprob": mean_logprob,
        "scored_tokens": scored_tokens,
        "uncertain_below": args.min_mean_logprob,
        "basis": (
            "mean log-probability of generated tokens under this model; "
            "not calibrated, not an accuracy estimate"
        ),
    }

    # A generation that stops without an EOS token stopped because it hit the
    # token budget, so its text is a prefix. The score of that prefix can still
    # look good; completeness must be judged separately from the score.
    eos_token_id = getattr(model.config, "eos_token_id", None)
    if eos_token_id is None:
        generation_config = getattr(model, "generation_config", None)
        eos_token_id = getattr(generation_config, "eos_token_id", None)
    if eos_token_id is None and tokenizer is not None:
        eos_token_id = getattr(tokenizer, "eos_token_id", None)
    eos_token_ids: set[int] = set()
    try:
        if isinstance(eos_token_id, (list, tuple, set)):
            eos_token_ids = {int(value) for value in eos_token_id}
        elif eos_token_id is not None:
            eos_token_ids = {int(eos_token_id)}
    except (TypeError, ValueError):
        eos_token_ids = set()

    new_tokens = max(generated_tokens - 1, 0)
    last_token_id: int | None = None
    if new_tokens:
        try:
            last_token_id = int(generated.sequences[0, -1].item())
        except (AttributeError, IndexError, TypeError, ValueError):
            last_token_id = None

    if not eos_token_ids or last_token_id is None:
        termination = "unverified"
    elif last_token_id in eos_token_ids:
        termination = "eos"
    elif new_tokens >= args.max_new_tokens:
        termination = "max_new_tokens"
    else:
        termination = "stopped-without-eos"

    generation_report: dict[str, Any] = {
        "do_sample": False,
        "max_new_tokens": args.max_new_tokens,
        "sequence_tokens": generated_tokens,
        "new_tokens": new_tokens,
        "termination": termination,
    }

    if not text:
        report: dict[str, Any] = {
            "schema": SCHEMA,
            "status": "unreadable",
            "text": None,
            "confidence": None,
            "confidence_note": (
                "TrOCR does not expose a calibrated recognition confidence. "
                "No text is reported because the model produced an empty generation."
            ),
            "image": image_report,
            "region": region_report,
            "model": model_report,
            "generation": generation_report,
            "scores": scores_report,
            "timing_ms": {
                "load_ms": load_ms,
                "inference_ms": inference_ms,
                "total_ms": round((time.perf_counter() - total_started) * 1000.0, 1),
            },
            "warnings": warnings,
            "error": {"message": "empty generation: treat this line as unreadable"},
        }
        if write_report(report, output) != 0:
            return 2
        return 4

    uncertain_reasons: list[str] = []
    if termination == "max_new_tokens":
        uncertain_reasons.append(
            f"generation used the full {args.max_new_tokens}-token budget without an EOS token; "
            "text is a truncated prefix, not a complete line"
        )
    elif termination == "stopped-without-eos":
        uncertain_reasons.append(
            f"generation stopped after {new_tokens} new tokens without an EOS token; "
            "text may be incomplete"
        )
    elif termination == "unverified":
        uncertain_reasons.append(
            "generation termination could not be verified (no usable EOS token id); "
            "text may be a truncated prefix"
        )
    if mean_logprob is not None and mean_logprob < args.min_mean_logprob:
        uncertain_reasons.append(
            f"mean_token_logprob {mean_logprob} is below {args.min_mean_logprob}"
        )
    if not looks_like_text(text):
        uncertain_reasons.append("generation contains no letters or digits")
    status = "uncertain" if uncertain_reasons else "recognized"

    report = {
        "schema": SCHEMA,
        "status": status,
        "text": text,
        "confidence": None,
        "confidence_note": (
            "TrOCR does not expose a calibrated recognition confidence. "
            "The status is an operational gate; verify the text against the image "
            "and the source permission before downstream use."
        ),
        "image": image_report,
        "region": region_report,
        "model": model_report,
        "generation": generation_report,
        "scores": scores_report,
        "timing_ms": {
            "load_ms": load_ms,
            "inference_ms": inference_ms,
            "total_ms": round((time.perf_counter() - total_started) * 1000.0, 1),
        },
        "warnings": warnings,
        "error": (
            {"message": "; ".join(uncertain_reasons)} if uncertain_reasons else None
        ),
    }
    if write_report(report, output) != 0:
        return 2
    return 3 if status == "uncertain" else 0


if __name__ == "__main__":
    raise SystemExit(main())
