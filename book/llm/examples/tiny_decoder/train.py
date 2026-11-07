"""Command-line entry point for the C23-C26 tiny decoder example.

Commands
--------
inspect : architecture, parameter counts, causal-mask check (works with or
          without a trained checkpoint)
train   : pretrain a fresh tiny decoder on ``corpus.jsonl`` and save/reload it
sample  : autoregressive text from a checkpoint
adapt   : full supervised fine-tuning or frozen-base LoRA on ``sft.jsonl``

All data is the course-authored toy corpus in this directory. Nothing is
downloaded, and no external model or weight file is required.
"""

from __future__ import annotations

import argparse
import json
import math
import random
import sys
import time
from dataclasses import asdict
from pathlib import Path
from typing import Any, Sequence

import torch
import torch.nn.functional as F

from model import (
    DecoderConfig,
    DEFAULT_LORA_TARGETS,
    FORMAT,
    TinyDecoder,
    WordTokenizer,
    apply_lora,
    count_parameters,
    future_invisibility_check,
    load_checkpoint,
    save_checkpoint,
    state_checksum,
)

HERE = Path(__file__).resolve().parent
DEFAULT_CORPUS = HERE / "corpus.jsonl"
DEFAULT_SFT = HERE / "sft.jsonl"
DEFAULT_RUNS = HERE / "runs"
SPLITS = ("train", "val", "test")


# ---------------------------------------------------------------------------
# Data loading and batching
# ---------------------------------------------------------------------------


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        raise SystemExit(f"data file not found: {path}")
    records: list[dict[str, Any]] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        stripped = line.strip()
        if not stripped:
            continue
        try:
            record = json.loads(stripped)
        except json.JSONDecodeError as error:
            raise SystemExit(f"{path}:{line_number}: invalid JSON ({error})")
        if not isinstance(record, dict):
            raise SystemExit(f"{path}:{line_number}: each line must be a JSON object")
        records.append(record)
    if not records:
        raise SystemExit(f"data file is empty: {path}")
    return records


def validate_corpus(records: Sequence[dict[str, Any]], label: str = "corpus") -> None:
    required = ("id", "group", "split", "text")
    seen_ids: set[str] = set()
    group_splits: dict[str, set[str]] = {}
    for index, record in enumerate(records):
        for key in required:
            if key not in record or not isinstance(record[key], str):
                raise SystemExit(f"{label} record {index} is missing string field {key!r}")
        if record["split"] not in SPLITS:
            raise SystemExit(f"{label} record {index} has unknown split {record['split']!r}")
        if record["id"] in seen_ids:
            raise SystemExit(f"{label} has duplicate id {record['id']!r}")
        seen_ids.add(record["id"])
        group_splits.setdefault(record["group"], set()).add(record["split"])
    for group, splits in sorted(group_splits.items()):
        if len(splits) != 1:
            raise SystemExit(
                f"{label} group {group!r} spans splits {sorted(splits)}; "
                "held-out groups must not leak into training"
            )


def validate_sft(records: Sequence[dict[str, Any]]) -> None:
    required = ("id", "group", "split", "prompt", "response")
    seen_ids: set[str] = set()
    group_splits: dict[str, set[str]] = {}
    for index, record in enumerate(records):
        for key in required:
            if key not in record or not isinstance(record[key], str):
                raise SystemExit(f"SFT record {index} is missing string field {key!r}")
        if record["split"] not in SPLITS:
            raise SystemExit(f"SFT record {index} has unknown split {record['split']!r}")
        if record["id"] in seen_ids:
            raise SystemExit(f"SFT has duplicate id {record['id']!r}")
        seen_ids.add(record["id"])
        if not record["prompt"].strip() or not record["response"].strip():
            raise SystemExit(f"SFT record {index} has an empty prompt or response")
        group_splits.setdefault(record["group"], set()).add(record["split"])
    for group, splits in sorted(group_splits.items()):
        if len(splits) != 1:
            raise SystemExit(
                f"SFT group {group!r} spans splits {sorted(splits)}; "
                "adaptation groups must not leak into training"
            )


def split_records(records: Sequence[dict[str, Any]], split: str) -> list[dict[str, Any]]:
    return [record for record in records if record["split"] == split]


def split_summary(records: Sequence[dict[str, Any]]) -> dict[str, Any]:
    summary: dict[str, Any] = {}
    for split in SPLITS:
        selected = split_records(records, split)
        summary[split] = {
            "records": len(selected),
            "groups": sorted({record["group"] for record in selected}),
        }
    return summary


def build_tokenizer(records: Sequence[dict[str, Any]]) -> WordTokenizer:
    training_texts = [record["text"] for record in records if record["split"] == "train"]
    if not training_texts:
        raise SystemExit("corpus has no train split from which to build the vocabulary")
    return WordTokenizer.from_texts(training_texts)


def encode_corpus(
    records: Sequence[dict[str, Any]], tokenizer: WordTokenizer, max_len: int
) -> dict[str, list[list[int]]]:
    encoded: dict[str, list[list[int]]] = {split: [] for split in SPLITS}
    for record in records:
        token_ids = tokenizer.encode(record["text"], add_bos=True, add_eos=True)
        if len(token_ids) > max_len:
            raise SystemExit(
                f"corpus record {record['id']!r} needs {len(token_ids)} tokens, "
                f"but max_len is {max_len}"
            )
        encoded[record["split"]].append(token_ids)
    return encoded


def oov_counts(records: Sequence[dict[str, Any]], tokenizer: WordTokenizer) -> dict[str, int]:
    counts: dict[str, int] = {}
    for split in SPLITS:
        unknown = 0
        for record in records:
            if record["split"] != split:
                continue
            unknown += sum(
                1 for token_id in tokenizer.encode_body(record["text"]) if token_id == tokenizer.unk_id
            )
        counts[split] = unknown
    return counts


def encode_sft(
    records: Sequence[dict[str, Any]], tokenizer: WordTokenizer, max_len: int
) -> dict[str, list[tuple[list[int], list[int]]]]:
    """Encode prompt+response and mask the loss to response tokens only."""
    encoded: dict[str, list[tuple[list[int], list[int]]]] = {split: [] for split in SPLITS}
    for record in records:
        prompt_ids = tokenizer.encode_body(record["prompt"])
        response_ids = tokenizer.encode_body(record["response"]) + [tokenizer.eos_id]
        full = [tokenizer.bos_id] + prompt_ids + response_ids
        if len(full) > max_len:
            raise SystemExit(
                f"SFT record {record['id']!r} needs {len(full)} tokens, "
                f"but max_len is {max_len}"
            )
        inputs = full[:-1]
        targets = [-100] * len(inputs)
        response_start = 1 + len(prompt_ids)
        for target_index in range(len(inputs)):
            position = target_index + 1
            if position >= response_start:
                targets[target_index] = full[position]
        if all(target == -100 for target in targets):
            raise SystemExit(f"SFT record {record['id']!r} has no response targets")
        encoded[record["split"]].append((inputs, targets))
    return encoded


def make_lm_batch(sequences: Sequence[Sequence[int]], pad_id: int) -> tuple[torch.Tensor, torch.Tensor]:
    if not sequences:
        raise ValueError("cannot build an empty batch")
    width = max(len(sequence) - 1 for sequence in sequences)
    if width < 1:
        raise ValueError("sequences must contain at least two tokens")
    inputs = torch.full((len(sequences), width), pad_id, dtype=torch.long)
    targets = torch.full((len(sequences), width), -100, dtype=torch.long)
    for row, sequence in enumerate(sequences):
        tensor = torch.tensor(sequence, dtype=torch.long)
        inputs[row, : tensor.numel() - 1] = tensor[:-1]
        targets[row, : tensor.numel() - 1] = tensor[1:]
    return inputs, targets


def make_sft_batch(
    pairs: Sequence[tuple[Sequence[int], Sequence[int]]], pad_id: int
) -> tuple[torch.Tensor, torch.Tensor]:
    if not pairs:
        raise ValueError("cannot build an empty batch")
    width = max(len(inputs) for inputs, _ in pairs)
    inputs_tensor = torch.full((len(pairs), width), pad_id, dtype=torch.long)
    targets_tensor = torch.full((len(pairs), width), -100, dtype=torch.long)
    for row, (inputs, targets) in enumerate(pairs):
        if len(inputs) != len(targets):
            raise ValueError("SFT input/target length mismatch")
        inputs_tensor[row, : len(inputs)] = torch.tensor(inputs, dtype=torch.long)
        targets_tensor[row, : len(targets)] = torch.tensor(targets, dtype=torch.long)
    return inputs_tensor, targets_tensor


def batches(sequences: Sequence[Sequence[int]], size: int) -> list[Sequence[Sequence[int]]]:
    return [sequences[index : index + size] for index in range(0, len(sequences), size)]


# ---------------------------------------------------------------------------
# Evaluation, training, checks
# ---------------------------------------------------------------------------


def evaluate_lm(
    model: TinyDecoder,
    sequences: Sequence[Sequence[int]],
    pad_id: int,
    batch_size: int = 32,
) -> dict[str, float | int]:
    model.eval()
    vocab_size = model.config.vocab_size
    total_loss = 0.0
    target_tokens = 0
    with torch.no_grad():
        for batch in batches(sequences, batch_size):
            inputs, targets = make_lm_batch(batch, pad_id)
            logits, _ = model(inputs)
            total_loss += float(
                F.cross_entropy(
                    logits.reshape(-1, vocab_size),
                    targets.reshape(-1),
                    ignore_index=-100,
                    reduction="sum",
                )
            )
            target_tokens += int((targets != -100).sum())
    loss = total_loss / max(target_tokens, 1)
    return {
        "loss": loss,
        "perplexity": math.exp(min(loss, 20.0)),
        "target_tokens": target_tokens,
        "sequences": len(sequences),
    }


def evaluate_sft(
    model: TinyDecoder,
    pairs: Sequence[tuple[Sequence[int], Sequence[int]]],
    pad_id: int,
    batch_size: int = 32,
) -> dict[str, float | int]:
    model.eval()
    vocab_size = model.config.vocab_size
    total_loss = 0.0
    target_tokens = 0
    with torch.no_grad():
        for batch in batches(pairs, batch_size):
            inputs, targets = make_sft_batch(batch, pad_id)
            logits, _ = model(inputs)
            total_loss += float(
                F.cross_entropy(
                    logits.reshape(-1, vocab_size),
                    targets.reshape(-1),
                    ignore_index=-100,
                    reduction="sum",
                )
            )
            target_tokens += int((targets != -100).sum())
    loss = total_loss / max(target_tokens, 1)
    return {
        "loss": loss,
        "perplexity": math.exp(min(loss, 20.0)),
        "target_tokens": target_tokens,
        "sequences": len(pairs),
    }


def train_lm(
    model: TinyDecoder,
    sequences: Sequence[Sequence[int]],
    pad_id: int,
    steps: int,
    batch_size: int,
    learning_rate: float,
    seed: int,
    log_every: int = 20,
) -> list[dict[str, float | int]]:
    if not sequences:
        raise SystemExit("no training sequences")
    parameters = [parameter for parameter in model.parameters() if parameter.requires_grad]
    if not parameters:
        raise SystemExit("no trainable parameters")
    optimizer = torch.optim.AdamW(parameters, lr=learning_rate, weight_decay=0.01)
    rng = random.Random(seed)
    model.train()
    history: list[dict[str, float | int]] = []
    for step in range(steps):
        batch = [sequences[rng.randrange(len(sequences))] for _ in range(batch_size)]
        inputs, targets = make_lm_batch(batch, pad_id)
        optimizer.zero_grad(set_to_none=True)
        logits, _ = model(inputs)
        loss = F.cross_entropy(
            logits.reshape(-1, model.config.vocab_size),
            targets.reshape(-1),
            ignore_index=-100,
        )
        loss.backward()
        torch.nn.utils.clip_grad_norm_(parameters, 1.0)
        optimizer.step()
        if step % log_every == 0 or step == steps - 1:
            history.append({"step": step + 1, "batch_loss_before_update": float(loss.detach())})
    return history


def train_sft(
    model: TinyDecoder,
    pairs: Sequence[tuple[Sequence[int], Sequence[int]]],
    pad_id: int,
    steps: int,
    batch_size: int,
    learning_rate: float,
    seed: int,
    log_every: int = 20,
) -> list[dict[str, float | int]]:
    if not pairs:
        raise SystemExit("no SFT training pairs")
    parameters = [parameter for parameter in model.parameters() if parameter.requires_grad]
    if not parameters:
        raise SystemExit("no trainable parameters")
    optimizer = torch.optim.AdamW(parameters, lr=learning_rate, weight_decay=0.01)
    rng = random.Random(seed)
    model.train()
    history: list[dict[str, float | int]] = []
    for step in range(steps):
        batch = [pairs[rng.randrange(len(pairs))] for _ in range(batch_size)]
        inputs, targets = make_sft_batch(batch, pad_id)
        optimizer.zero_grad(set_to_none=True)
        logits, _ = model(inputs)
        loss = F.cross_entropy(
            logits.reshape(-1, model.config.vocab_size),
            targets.reshape(-1),
            ignore_index=-100,
        )
        loss.backward()
        torch.nn.utils.clip_grad_norm_(parameters, 1.0)
        optimizer.step()
        if step % log_every == 0 or step == steps - 1:
            history.append({"step": step + 1, "batch_loss_before_update": float(loss.detach())})
    return history


def logits_for_checkpoint(
    checkpoint: Path, inputs: torch.Tensor, tokenizer: WordTokenizer
) -> torch.Tensor:
    model, loaded_tokenizer, _ = load_checkpoint(checkpoint)
    if loaded_tokenizer.token_list() != tokenizer.token_list():
        raise SystemExit("reloaded checkpoint vocabulary differs from the in-memory vocabulary")
    model.eval()
    with torch.no_grad():
        logits, _ = model(inputs)
    return logits


def reload_check(
    checkpoint: Path,
    model: TinyDecoder,
    tokenizer: WordTokenizer,
    inputs: torch.Tensor,
) -> dict[str, Any]:
    model.eval()
    with torch.no_grad():
        before, _ = model(inputs)
    after = logits_for_checkpoint(checkpoint, inputs, tokenizer)
    difference = float((before - after).abs().max())
    return {
        "checkpoint": str(checkpoint),
        "bitwise_equal": bool(torch.equal(before, after)),
        "max_abs_diff": difference,
    }


def target_shift_check(sequence: Sequence[int], tokenizer: WordTokenizer) -> dict[str, Any]:
    if len(sequence) < 2:
        raise ValueError("sequence is too short")
    inputs = list(sequence[:-1])
    targets = list(sequence[1:])
    return {
        "tokens": [tokenizer.decode([token_id]) for token_id in sequence],
        "input": [tokenizer.decode([token_id]) for token_id in inputs],
        "target": [tokenizer.decode([token_id]) for token_id in targets],
        "aligned": all(inputs[index + 1] == targets[index] for index in range(len(inputs) - 1)),
    }


def generate_text(
    model: TinyDecoder,
    tokenizer: WordTokenizer,
    prompt: str,
    max_new_tokens: int,
    temperature: float,
    top_k: int | None,
    seed: int,
) -> dict[str, Any]:
    torch.manual_seed(seed)
    prompt_ids = tokenizer.encode_body(prompt)
    if not prompt_ids:
        raise SystemExit("prompt contains no known token pattern")
    start = [tokenizer.bos_id] + prompt_ids
    if len(start) >= model.config.max_len:
        raise SystemExit(
            f"prompt needs {len(start)} positions; checkpoint max_len is {model.config.max_len}"
        )
    output = model.generate(
        start,
        max_new_tokens=max_new_tokens,
        temperature=temperature,
        top_k=top_k,
        eos_id=tokenizer.eos_id,
    )
    output_ids = [int(token_id) for token_id in output]
    continuation = output_ids[len(start) :]
    return {
        "prompt": prompt,
        "prompt_ids": start,
        "generated_ids": continuation,
        "generated_text": tokenizer.decode(continuation),
        "full_text": tokenizer.decode(output_ids),
        "hit_eos": bool(output_ids and output_ids[-1] == tokenizer.eos_id),
        "positions_used": len(output_ids),
        "max_len": model.config.max_len,
        "temperature": temperature,
        "top_k": top_k,
    }


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------


def cmd_inspect(args: argparse.Namespace) -> dict[str, Any]:
    if args.checkpoint:
        checkpoint = Path(args.checkpoint)
        model, tokenizer, payload = load_checkpoint(checkpoint)
        config = DecoderConfig(**payload["config"])
        adaptation = payload.get("adaptation") or {}
        source = str(checkpoint)
        trained = True
    else:
        records = load_jsonl(DEFAULT_CORPUS)
        validate_corpus(records)
        tokenizer = build_tokenizer(records)
        config = DecoderConfig(vocab_size=len(tokenizer))
        torch.manual_seed(0)
        model = TinyDecoder(config)
        adaptation = {}
        source = f"untrained default model from {DEFAULT_CORPUS.name}"
        trained = False

    model.eval()
    report: dict[str, Any] = {
        "format": FORMAT,
        "command": "inspect",
        "source": source,
        "trained": trained,
        "config": asdict(config),
        "vocab_size": len(tokenizer),
        "parameters": count_parameters(model),
        "adaptation": adaptation,
        "architecture": {
            "embedding": f"[batch, seq] -> [batch, seq, {config.d_model}]",
            "positions": f"learned, max_len={config.max_len}",
            "attention": (
                f"{config.n_heads} heads x {config.d_model // config.n_heads} dims, "
                "upper-triangular causal mask"
            ),
            "feed_forward": f"{config.d_model} -> {config.d_ff} -> {config.d_model}",
            "blocks": config.n_layers,
            "head": f"{config.d_model} -> {config.vocab_size}, tied to token embedding",
        },
        "checks": {
            "future_invisibility": future_invisibility_check(model, tokenizer),
            "base_checksum": state_checksum(model, "base"),
        },
    }
    if trained:
        report["sample"] = generate_text(
            model,
            tokenizer,
            prompt=args.prompt,
            max_new_tokens=args.max_new,
            temperature=args.temperature,
            top_k=args.top_k,
            seed=args.seed,
        )
    else:
        report["note"] = "untrained parameters; sample output is omitted on purpose"
    return report


def cmd_train(args: argparse.Namespace) -> dict[str, Any]:
    if args.steps < 1 or args.batch_size < 1:
        raise SystemExit("--steps and --batch-size must be positive")
    started = time.perf_counter()
    records = load_jsonl(Path(args.corpus))
    validate_corpus(records)
    tokenizer = build_tokenizer(records)
    config = DecoderConfig(
        vocab_size=len(tokenizer),
        n_layers=args.layers,
        d_model=args.d_model,
        n_heads=args.heads,
        d_ff=args.d_ff,
        max_len=args.max_len,
    )
    encoded = encode_corpus(records, tokenizer, config.max_len)
    if not encoded["train"]:
        raise SystemExit("train split is empty")
    torch.manual_seed(args.seed)
    model = TinyDecoder(config)
    parameters = count_parameters(model)
    history = train_lm(
        model,
        encoded["train"],
        tokenizer.pad_id,
        steps=args.steps,
        batch_size=args.batch_size,
        learning_rate=args.lr,
        seed=args.seed,
    )
    losses = {
        split: evaluate_lm(model, encoded[split], tokenizer.pad_id) if encoded[split] else None
        for split in SPLITS
    }
    output = Path(args.out)
    save_checkpoint(
        output,
        model,
        tokenizer,
        config,
        adaptation={},
        meta={
            "command": "train",
            "corpus": str(Path(args.corpus)),
            "steps": args.steps,
            "batch_size": args.batch_size,
            "learning_rate": args.lr,
            "seed": args.seed,
        },
    )
    check_batch = encoded["val"] or encoded["test"] or encoded["train"]
    check_inputs, _ = make_lm_batch(check_batch[:4], tokenizer.pad_id)
    reload = reload_check(output, model, tokenizer, check_inputs)
    sample = generate_text(
        model,
        tokenizer,
        prompt=args.prompt,
        max_new_tokens=args.max_new,
        temperature=args.temperature,
        top_k=args.top_k,
        seed=args.seed,
    )
    elapsed = time.perf_counter() - started
    return {
        "format": FORMAT,
        "command": "train",
        "corpus": {
            "path": str(Path(args.corpus)),
            "records": len(records),
            "splits": split_summary(records),
            "oov_tokens": oov_counts(records, tokenizer),
            "vocab_size": len(tokenizer),
            "vocabulary": tokenizer.token_list(),
        },
        "config": asdict(config),
        "parameters": parameters,
        "training": {
            "steps": args.steps,
            "batch_size": args.batch_size,
            "learning_rate": args.lr,
            "seed": args.seed,
            "history": history,
        },
        "losses": losses,
        "checks": {
            "target_shift": target_shift_check(encoded["train"][0], tokenizer),
            "future_invisibility": future_invisibility_check(model, tokenizer),
            "reload": reload,
        },
        "sample": sample,
        "artifact": {
            "checkpoint": str(output),
            "bytes": output.stat().st_size if output.exists() else None,
        },
        "seconds": elapsed,
    }


def cmd_sample(args: argparse.Namespace) -> dict[str, Any]:
    checkpoint = Path(args.checkpoint)
    model, tokenizer, payload = load_checkpoint(checkpoint)
    return {
        "format": FORMAT,
        "command": "sample",
        "checkpoint": str(checkpoint),
        "adaptation": payload.get("adaptation") or {},
        "sample": generate_text(
            model,
            tokenizer,
            prompt=args.prompt,
            max_new_tokens=args.max_new,
            temperature=args.temperature,
            top_k=args.top_k,
            seed=args.seed,
        ),
    }


def _adapt_one(
    base_checkpoint: Path,
    sft_records: Sequence[dict[str, Any]],
    method: str,
    rank: int,
    alpha: float,
    steps: int,
    batch_size: int,
    learning_rate: float,
    seed: int,
    output: Path,
    sample_max_new: int,
) -> dict[str, Any]:
    started = time.perf_counter()
    model, tokenizer, payload = load_checkpoint(base_checkpoint)
    if (payload.get("adaptation") or {}).get("method"):
        raise SystemExit("adapt expects a base checkpoint, not an already adapted checkpoint")
    encoded = encode_sft(sft_records, tokenizer, model.config.max_len)
    if not encoded["train"]:
        raise SystemExit("SFT train split is empty")
    base_losses = {
        split: evaluate_sft(model, encoded[split], tokenizer.pad_id) if encoded[split] else None
        for split in SPLITS
    }
    base_checksum_before = state_checksum(model, "base")
    lora_checksum_before = state_checksum(model, "lora")
    parameters_before = count_parameters(model)

    torch.manual_seed(seed)
    wrapped: list[str] = []
    if method == "lora":
        wrapped = apply_lora(model, rank=rank, alpha=alpha)
    parameters_after_setup = count_parameters(model)
    if method == "lora":
        base_checksum_after_wrap = state_checksum(model, "base")
        if base_checksum_after_wrap != base_checksum_before:
            raise SystemExit("wrapping LoRA changed frozen base parameters")
        lora_checksum_after_wrap = state_checksum(model, "lora")

    history = train_sft(
        model,
        encoded["train"],
        tokenizer.pad_id,
        steps=steps,
        batch_size=batch_size,
        learning_rate=learning_rate,
        seed=seed,
    )
    adapted_losses = {
        split: evaluate_sft(model, encoded[split], tokenizer.pad_id) if encoded[split] else None
        for split in SPLITS
    }
    base_checksum_after = state_checksum(model, "base")
    lora_checksum_after = state_checksum(model, "lora")
    adaptation = (
        {
            "method": "lora",
            "rank": rank,
            "alpha": alpha,
            "targets": list(DEFAULT_LORA_TARGETS),
        }
        if method == "lora"
        else {"method": "full"}
    )
    save_checkpoint(
        output,
        model,
        tokenizer,
        model.config,
        adaptation=adaptation,
        meta={
            "command": "adapt",
            "base_checkpoint": str(base_checkpoint),
            "sft": str(DEFAULT_SFT),
            "method": method,
            "steps": steps,
            "batch_size": batch_size,
            "learning_rate": learning_rate,
            "seed": seed,
        },
    )
    check_pairs = encoded["val"] or encoded["test"] or encoded["train"]
    check_inputs, _ = make_sft_batch(check_pairs[:4], tokenizer.pad_id)
    reload = reload_check(output, model, tokenizer, check_inputs)

    eval_records = split_records(sft_records, "val") or split_records(sft_records, "test") or split_records(sft_records, "train")
    sample_prompt = eval_records[0]["prompt"] if eval_records else "say the red boat ."
    sample = generate_text(
        model,
        tokenizer,
        prompt=sample_prompt,
        max_new_tokens=sample_max_new,
        temperature=0.0,
        top_k=None,
        seed=seed,
    )
    base_grads_all_none = all(
        parameter.grad is None
        for name, parameter in model.named_parameters()
        if not (name.endswith("lora_A") or name.endswith("lora_B"))
    )
    elapsed = time.perf_counter() - started
    return {
        "method": method,
        "checkpoint": str(output),
        "bytes": output.stat().st_size if output.exists() else None,
        "parameters": {
            "before": parameters_before,
            "after_setup": parameters_after_setup,
            "trainable_after_setup": parameters_after_setup["trainable"],
        },
        "checks": {
            "base_checksum_before": base_checksum_before,
            "base_checksum_after": base_checksum_after,
            "base_unchanged": base_checksum_before == base_checksum_after,
            "lora_checksum_before": lora_checksum_before,
            "lora_checksum_after": lora_checksum_after,
            "lora_changed": lora_checksum_before != lora_checksum_after,
            "base_grads_all_none": base_grads_all_none,
            "base_frozen": (base_checksum_before == base_checksum_after) if method == "lora" else False,
            "base_updated": (base_checksum_before != base_checksum_after) if method == "full" else False,
            "reload": reload,
        },
        "losses": {
            "before": base_losses,
            "after": adapted_losses,
            "delta_val": _loss_delta(base_losses, adapted_losses, "val"),
            "delta_test": _loss_delta(base_losses, adapted_losses, "test"),
        },
        "training": {
            "steps": steps,
            "batch_size": batch_size,
            "learning_rate": learning_rate,
            "seed": seed,
            "history": history,
        },
        "sample": sample,
        "seconds": elapsed,
    }


def _loss_delta(
    before: dict[str, Any], after: dict[str, Any], split: str
) -> float | None:
    if before.get(split) is None or after.get(split) is None:
        return None
    return float(after[split]["loss"] - before[split]["loss"])


def _output_paths(method: str, requested: str | None) -> dict[str, Path]:
    if method == "both":
        if requested is None:
            return {
                "full": DEFAULT_RUNS / "adapt-full.pt",
                "lora": DEFAULT_RUNS / "adapt-lora.pt",
            }
        base = Path(requested)
        suffix = base.suffix or ".pt"
        return {
            "full": base.parent / f"{base.stem}-full{suffix}",
            "lora": base.parent / f"{base.stem}-lora{suffix}",
        }
    return {method: Path(requested) if requested else DEFAULT_RUNS / f"adapt-{method}.pt"}


def cmd_adapt(args: argparse.Namespace) -> dict[str, Any]:
    if args.steps < 1 or args.batch_size < 1:
        raise SystemExit("--steps and --batch-size must be positive")
    if args.method == "lora" and args.rank < 1:
        raise SystemExit("--rank must be positive")
    base_checkpoint = Path(args.checkpoint)
    if not base_checkpoint.exists():
        raise SystemExit(f"base checkpoint not found: {base_checkpoint}")
    sft_records = load_jsonl(Path(args.sft))
    validate_sft(sft_records)
    outputs = _output_paths(args.method, args.out)
    methods = ["full", "lora"] if args.method == "both" else [args.method]
    results = {
        method: _adapt_one(
            base_checkpoint,
            sft_records,
            method=method,
            rank=args.rank,
            alpha=args.alpha,
            steps=args.steps,
            batch_size=args.batch_size,
            learning_rate=args.lr,
            seed=args.seed,
            output=outputs[method],
            sample_max_new=args.max_new,
        )
        for method in methods
    }
    report: dict[str, Any] = {
        "format": FORMAT,
        "command": "adapt",
        "base_checkpoint": str(base_checkpoint),
        "sft": {
            "path": str(Path(args.sft)),
            "records": len(sft_records),
            "splits": split_summary(sft_records),
            "vocab_size": len(load_checkpoint(base_checkpoint)[1]),
        },
        "note": (
            "LoRA adapters are kept separate and are not merged into the base; "
            "full SFT updates every parameter. Held-out losses are measurements "
            "on this toy data only, not evidence of general capability."
        ),
    }
    if args.method == "both":
        report["comparison"] = results
    else:
        report.update(results[args.method])
    return report


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="train.py",
        description=(
            "Tiny CPU causal Transformer decoder: train, sample, inspect, and "
            "compare full SFT with frozen-base LoRA. Course-authored toy data only."
        ),
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    inspect_parser = subparsers.add_parser(
        "inspect", help="show architecture, parameter counts, and causal-mask check"
    )
    inspect_parser.add_argument("--checkpoint", type=Path, default=None, help="optional checkpoint to inspect")
    inspect_parser.add_argument("--prompt", default="the red boat")
    inspect_parser.add_argument("--max-new", type=int, default=12)
    inspect_parser.add_argument("--temperature", type=float, default=0.8)
    inspect_parser.add_argument("--top-k", type=int, default=10)
    inspect_parser.add_argument("--seed", type=int, default=0)
    inspect_parser.add_argument("--json", action="store_true", help="compact machine-readable output")

    train_parser = subparsers.add_parser("train", help="pretrain a tiny decoder from corpus.jsonl")
    train_parser.add_argument("--corpus", type=Path, default=DEFAULT_CORPUS)
    train_parser.add_argument("--steps", type=int, default=400)
    train_parser.add_argument("--batch-size", type=int, default=24)
    train_parser.add_argument("--lr", type=float, default=3e-3)
    train_parser.add_argument("--seed", type=int, default=7)
    train_parser.add_argument("--layers", type=int, default=2)
    train_parser.add_argument("--d-model", type=int, default=64)
    train_parser.add_argument("--heads", type=int, default=4)
    train_parser.add_argument("--d-ff", type=int, default=128)
    train_parser.add_argument("--max-len", type=int, default=48)
    train_parser.add_argument("--out", type=Path, default=DEFAULT_RUNS / "base.pt")
    train_parser.add_argument("--prompt", default="the red boat")
    train_parser.add_argument("--max-new", type=int, default=12)
    train_parser.add_argument("--temperature", type=float, default=0.8)
    train_parser.add_argument("--top-k", type=int, default=10)
    train_parser.add_argument("--json", action="store_true")

    sample_parser = subparsers.add_parser("sample", help="generate text from a checkpoint")
    sample_parser.add_argument("--checkpoint", type=Path, default=DEFAULT_RUNS / "base.pt")
    sample_parser.add_argument("--prompt", default="the red boat")
    sample_parser.add_argument("--max-new", type=int, default=16)
    sample_parser.add_argument("--temperature", type=float, default=0.8)
    sample_parser.add_argument("--top-k", type=int, default=10)
    sample_parser.add_argument("--seed", type=int, default=0)
    sample_parser.add_argument("--json", action="store_true")

    adapt_parser = subparsers.add_parser(
        "adapt", help="full SFT or frozen-base LoRA on sft.jsonl"
    )
    adapt_parser.add_argument("--checkpoint", type=Path, default=DEFAULT_RUNS / "base.pt")
    adapt_parser.add_argument("--sft", type=Path, default=DEFAULT_SFT)
    adapt_parser.add_argument("--method", choices=("full", "lora", "both"), default="lora")
    adapt_parser.add_argument("--rank", type=int, default=4)
    adapt_parser.add_argument("--alpha", type=float, default=8.0)
    adapt_parser.add_argument("--steps", type=int, default=120)
    adapt_parser.add_argument("--batch-size", type=int, default=8)
    adapt_parser.add_argument("--lr", type=float, default=2e-3)
    adapt_parser.add_argument("--seed", type=int, default=11)
    adapt_parser.add_argument("--max-new", type=int, default=12)
    adapt_parser.add_argument("--out", type=Path, default=None)
    adapt_parser.add_argument("--json", action="store_true")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        if args.command == "inspect":
            report = cmd_inspect(args)
        elif args.command == "train":
            report = cmd_train(args)
        elif args.command == "sample":
            report = cmd_sample(args)
        elif args.command == "adapt":
            report = cmd_adapt(args)
        else:
            parser.error(f"unknown command {args.command!r}")
            return 2
    except (FileNotFoundError, ValueError, RuntimeError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 1
    print(json.dumps(report, ensure_ascii=False, indent=None if args.json else 2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
