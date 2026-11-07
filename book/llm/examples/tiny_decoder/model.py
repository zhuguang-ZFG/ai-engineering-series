"""Tiny causal Transformer decoder assembled from readable parts.

The module contains no downloaded weights: every parameter is initialized here,
trained on the course-authored toy corpus, and saved as a plain ``state_dict``.

Parts, in construction order:
    WordTokenizer -> token embedding + learned position embedding
    -> [LayerNorm -> causal multi-head attention -> residual
        -> LayerNorm -> feed-forward -> residual] x n_layers
    -> final LayerNorm -> vocabulary head (tied to the token embedding)

The same file also implements a small LoRA wrapper so ``train.py adapt`` can
compare full supervised fine-tuning with a frozen-base low-rank adapter.
"""

from __future__ import annotations

import hashlib
import math
import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable, Sequence

import torch
import torch.nn.functional as F
from torch import Tensor, nn

FORMAT = "tiny-decoder-v1"
PAD_TOKEN = "<pad>"
BOS_TOKEN = "<bos>"
EOS_TOKEN = "<eos>"
UNK_TOKEN = "<unk>"
SPECIAL_TOKENS: tuple[str, ...] = (PAD_TOKEN, BOS_TOKEN, EOS_TOKEN, UNK_TOKEN)
TOKEN_PATTERN = re.compile(r"[a-z]+|[.,!?;:]")
DEFAULT_LORA_TARGETS: tuple[str, ...] = (
    "attn.qkv",
    "attn.proj",
    "ff.fc1",
    "ff.fc2",
    "head",
)
_BLOCK_LORA_TARGETS: tuple[str, ...] = tuple(
    target for target in DEFAULT_LORA_TARGETS if target != "head"
)


@dataclass(frozen=True)
class DecoderConfig:
    """Shape and size settings stored next to every checkpoint."""

    vocab_size: int
    n_layers: int = 2
    d_model: int = 64
    n_heads: int = 4
    d_ff: int = 128
    max_len: int = 48
    dropout: float = 0.0

    def __post_init__(self) -> None:
        if self.vocab_size < len(SPECIAL_TOKENS):
            raise ValueError("vocab_size must include the four special tokens")
        if self.n_layers < 1:
            raise ValueError("n_layers must be at least 1")
        if self.n_heads < 1:
            raise ValueError("n_heads must be at least 1")
        if self.d_model < 2 or self.d_model % 2 != 0:
            raise ValueError("d_model must be an even positive number")
        if self.d_model % self.n_heads != 0:
            raise ValueError("d_model must be divisible by n_heads")
        if self.d_ff < 1:
            raise ValueError("d_ff must be positive")
        if self.max_len < 2:
            raise ValueError("max_len must be at least 2")
        if not 0.0 <= self.dropout < 1.0:
            raise ValueError("dropout must be in [0, 1)")


def sinusoidal_positions(max_len: int, d_model: int) -> Tensor:
    """Fixed sine/cosine positions from the original Transformer.

    No parameters are allocated for positions, so a frozen-base adapter can
    still address positions beyond those seen during pretraining. The values
    depend only on ``max_len`` and ``d_model`` and are rebuilt on load.
    """
    position = torch.arange(max_len, dtype=torch.float32).unsqueeze(1)
    div_term = torch.exp(
        torch.arange(0, d_model, 2, dtype=torch.float32)
        * (-math.log(10000.0) / d_model)
    )
    encoding = torch.zeros(max_len, d_model, dtype=torch.float32)
    encoding[:, 0::2] = torch.sin(position * div_term)
    encoding[:, 1::2] = torch.cos(position * div_term)
    return encoding


class WordTokenizer:
    """Whitespace-free word tokenizer for the toy corpus.

    The vocabulary is built from *training* texts only. Validation and test
    texts are encoded with the same table, so any word that never appeared in
    training becomes ``<unk>`` and is reported by ``train.py`` instead of being
    silently added.
    """

    def __init__(self, tokens: Sequence[str]) -> None:
        self.tokens = list(tokens)
        if tuple(self.tokens[: len(SPECIAL_TOKENS)]) != SPECIAL_TOKENS:
            raise ValueError("vocabulary must start with the four special tokens")
        if len(set(self.tokens)) != len(self.tokens):
            raise ValueError("vocabulary contains duplicate tokens")
        self.stoi = {token: index for index, token in enumerate(self.tokens)}
        self.pad_id = self.stoi[PAD_TOKEN]
        self.bos_id = self.stoi[BOS_TOKEN]
        self.eos_id = self.stoi[EOS_TOKEN]
        self.unk_id = self.stoi[UNK_TOKEN]

    @classmethod
    def from_texts(cls, texts: Iterable[str]) -> "WordTokenizer":
        words: set[str] = set()
        for text in texts:
            words.update(TOKEN_PATTERN.findall(text.lower()))
        return cls(list(SPECIAL_TOKENS) + sorted(words))

    def __len__(self) -> int:
        return len(self.tokens)

    def encode_body(self, text: str) -> list[int]:
        return [
            self.stoi.get(token, self.unk_id)
            for token in TOKEN_PATTERN.findall(text.lower())
        ]

    def encode(self, text: str, add_bos: bool = True, add_eos: bool = True) -> list[int]:
        ids: list[int] = []
        if add_bos:
            ids.append(self.bos_id)
        ids.extend(self.encode_body(text))
        if add_eos:
            ids.append(self.eos_id)
        return ids

    def decode(self, ids: Sequence[int], skip_special: bool = True) -> str:
        pieces: list[str] = []
        for raw in ids:
            index = int(raw)
            token = self.tokens[index] if 0 <= index < len(self.tokens) else UNK_TOKEN
            if skip_special and token in SPECIAL_TOKENS:
                continue
            pieces.append(token)
        text = " ".join(pieces)
        return re.sub(r"\s+([.,!?;:])", r"\1", text)

    def token_list(self) -> list[str]:
        return list(self.tokens)


class CausalSelfAttention(nn.Module):
    """Multi-head self-attention whose mask forbids looking to the right."""

    def __init__(self, config: DecoderConfig) -> None:
        super().__init__()
        self.d_model = config.d_model
        self.n_heads = config.n_heads
        self.head_dim = config.d_model // config.n_heads
        self.max_len = config.max_len
        self.qkv = nn.Linear(config.d_model, 3 * config.d_model, bias=False)
        self.proj = nn.Linear(config.d_model, config.d_model, bias=False)
        self.attn_dropout = nn.Dropout(config.dropout)
        self.resid_dropout = nn.Dropout(config.dropout)
        mask = torch.triu(
            torch.ones(config.max_len, config.max_len, dtype=torch.bool),
            diagonal=1,
        )
        self.register_buffer("causal_mask", mask, persistent=False)

    def forward(self, x: Tensor) -> Tensor:
        batch, length, channels = x.shape
        if length > self.max_len:
            raise ValueError(f"sequence length {length} exceeds max_len {self.max_len}")
        q, k, v = self.qkv(x).split(self.d_model, dim=-1)
        q = q.view(batch, length, self.n_heads, self.head_dim).transpose(1, 2)
        k = k.view(batch, length, self.n_heads, self.head_dim).transpose(1, 2)
        v = v.view(batch, length, self.n_heads, self.head_dim).transpose(1, 2)

        scores = (q @ k.transpose(-2, -1)) / math.sqrt(self.head_dim)
        # Future positions are set to -inf *before* softmax: their weight is
        # exactly zero, so their value vectors cannot enter this row.
        scores = scores.masked_fill(self.causal_mask[:length, :length], float("-inf"))
        weights = F.softmax(scores, dim=-1)
        weights = self.attn_dropout(weights)
        mixed = weights @ v
        mixed = mixed.transpose(1, 2).contiguous().view(batch, length, channels)
        return self.resid_dropout(self.proj(mixed))


class FeedForward(nn.Module):
    """Position-wise two-layer network; no mixing across sequence positions."""

    def __init__(self, config: DecoderConfig) -> None:
        super().__init__()
        self.fc1 = nn.Linear(config.d_model, config.d_ff)
        self.fc2 = nn.Linear(config.d_ff, config.d_model)
        self.dropout = nn.Dropout(config.dropout)

    def forward(self, x: Tensor) -> Tensor:
        return self.dropout(self.fc2(F.gelu(self.fc1(x))))


class DecoderBlock(nn.Module):
    """Pre-norm residual block: x + attn(ln(x)), then x + ffn(ln(x))."""

    def __init__(self, config: DecoderConfig) -> None:
        super().__init__()
        self.ln_1 = nn.LayerNorm(config.d_model)
        self.attn = CausalSelfAttention(config)
        self.ln_2 = nn.LayerNorm(config.d_model)
        self.ff = FeedForward(config)

    def forward(self, x: Tensor) -> Tensor:
        x = x + self.attn(self.ln_1(x))
        x = x + self.ff(self.ln_2(x))
        return x


class TinyDecoder(nn.Module):
    """Character-free, word-level causal decoder used by the C23-C26 lessons."""

    def __init__(self, config: DecoderConfig) -> None:
        super().__init__()
        self.config = config
        self.token_embedding = nn.Embedding(config.vocab_size, config.d_model)
        self.register_buffer(
            "position_encoding",
            sinusoidal_positions(config.max_len, config.d_model),
            persistent=False,
        )
        self.blocks = nn.ModuleList(
            [DecoderBlock(config) for _ in range(config.n_layers)]
        )
        self.ln_f = nn.LayerNorm(config.d_model)
        self.head = nn.Linear(config.d_model, config.vocab_size, bias=False)
        # Weight tying: the output head reuses the token embedding matrix.
        # This is a real parameter-sharing choice, not a second copy.
        self.head.weight = self.token_embedding.weight
        self.apply(self._init_weights)
        self.head.weight = self.token_embedding.weight

    @staticmethod
    def _init_weights(module: nn.Module) -> None:
        if isinstance(module, nn.Linear):
            nn.init.normal_(module.weight, mean=0.0, std=0.02)
            if module.bias is not None:
                nn.init.zeros_(module.bias)
        elif isinstance(module, nn.Embedding):
            nn.init.normal_(module.weight, mean=0.0, std=0.02)

    def forward(self, idx: Tensor, targets: Tensor | None = None) -> tuple[Tensor, Tensor | None]:
        """Return ``(logits[B,T,V], loss or None)``.

        ``targets`` is expected to be the input shifted one position left.
        Positions marked ``-100`` (padding and, for SFT, prompt tokens) are
        ignored by the cross-entropy.
        """
        if idx.dim() != 2:
            raise ValueError("idx must have shape [batch, sequence]")
        batch, length = idx.shape
        if length > self.config.max_len:
            raise ValueError(f"sequence length {length} exceeds max_len {self.config.max_len}")
        positions = torch.arange(length, device=idx.device)
        x = self.token_embedding(idx) + self.position_encoding[:length].to(idx.device)
        for block in self.blocks:
            x = block(x)
        x = self.ln_f(x)
        logits = self.head(x)
        loss: Tensor | None = None
        if targets is not None:
            if targets.shape != idx.shape:
                raise ValueError("targets must have the same shape as idx")
            loss = F.cross_entropy(
                logits.reshape(-1, self.config.vocab_size),
                targets.reshape(-1),
                ignore_index=-100,
            )
        return logits, loss

    @torch.no_grad()
    def generate(
        self,
        idx: Sequence[int] | Tensor,
        max_new_tokens: int,
        temperature: float = 0.8,
        top_k: int | None = None,
        eos_id: int | None = None,
    ) -> Tensor:
        """Autoregressive decoding for one sequence.

        ``temperature <= 0`` means greedy selection. The function stops at
        EOS or when the model's ``max_len`` context is full; the caller can
        inspect the returned length instead of assuming a fixed completion.
        """
        was_training = self.training
        self.eval()
        try:
            if isinstance(idx, Tensor):
                tokens = idx.detach().to(dtype=torch.long, device=next(self.parameters()).device).clone()
            else:
                tokens = torch.tensor(list(idx), dtype=torch.long, device=next(self.parameters()).device)
            if tokens.dim() != 1:
                raise ValueError("generate expects one 1-D sequence")
            if tokens.numel() == 0:
                raise ValueError("generate requires a non-empty prompt")
            if tokens.numel() >= self.config.max_len:
                raise ValueError("prompt already fills max_len; shorten the prompt")
            for _ in range(max_new_tokens):
                if tokens.numel() >= self.config.max_len:
                    break
                logits, _ = self(tokens.unsqueeze(0))
                next_logits = logits[0, -1]
                if temperature is None or temperature <= 0.0:
                    next_id = int(torch.argmax(next_logits))
                else:
                    scaled = next_logits / float(temperature)
                    if top_k is not None:
                        k = max(1, min(int(top_k), scaled.numel()))
                        values, indices = torch.topk(scaled, k)
                        probs = F.softmax(values, dim=-1)
                        choice = int(torch.multinomial(probs, 1))
                        next_id = int(indices[choice])
                    else:
                        probs = F.softmax(scaled, dim=-1)
                        next_id = int(torch.multinomial(probs, 1))
                tokens = torch.cat(
                    [tokens, torch.tensor([next_id], dtype=torch.long, device=tokens.device)]
                )
                if eos_id is not None and next_id == eos_id:
                    break
            return tokens
        finally:
            if was_training:
                self.train()


class LoRALinear(nn.Module):
    """Frozen linear layer plus a trainable low-rank update.

    ``y = base(x) + scaling * x @ A.T @ B.T`` with ``A`` shaped
    ``[rank, in_features]`` and ``B`` shaped ``[out_features, rank]``.
    ``B`` starts at zero, so a freshly wrapped model produces exactly the same
    logits as its frozen base until training changes the adapter.
    """

    def __init__(self, base: nn.Linear, rank: int = 4, alpha: float = 8.0) -> None:
        super().__init__()
        if rank < 1:
            raise ValueError("LoRA rank must be at least 1")
        self.base = base
        self.rank = rank
        self.alpha = float(alpha)
        self.scaling = self.alpha / self.rank
        for parameter in self.base.parameters():
            parameter.requires_grad_(False)
        self.lora_A = nn.Parameter(torch.empty(rank, base.in_features))
        self.lora_B = nn.Parameter(torch.zeros(base.out_features, rank))
        nn.init.kaiming_uniform_(self.lora_A, a=math.sqrt(5))

    def forward(self, x: Tensor) -> Tensor:
        update = (x @ self.lora_A.transpose(0, 1)) @ self.lora_B.transpose(0, 1)
        return self.base(x) + update * self.scaling


def _resolve_relative(module: nn.Module, dotted: str) -> tuple[nn.Module, str]:
    parts = dotted.split(".")
    if not parts or any(not part for part in parts):
        raise ValueError(f"invalid module path: {dotted!r}")
    parent: nn.Module = module
    for part in parts[:-1]:
        if not hasattr(parent, part):
            raise ValueError(f"module path not found: {dotted!r}")
        parent = getattr(parent, part)
    return parent, parts[-1]


def _lora_plan(
    model: TinyDecoder, targets: Sequence[str]
) -> list[tuple[int | None, str]]:
    """Normalize public relative targets and saved qualified targets.

    Public targets stay relative (``attn.qkv``, ``ff.fc1``, ``head``) and mean
    "apply to every block". A checkpoint may also contain fully qualified
    names such as ``blocks.1.ff.fc2``; those address exactly one block. Both
    forms are accepted so a checkpoint written by an older writer still loads.
    """
    plan: list[tuple[int | None, str]] = []
    unknown: list[str] = []
    for target in targets:
        if not isinstance(target, str) or not target:
            unknown.append(repr(target))
            continue
        if target == "head":
            plan.append((None, "head"))
            continue
        if target in _BLOCK_LORA_TARGETS:
            plan.extend((index, target) for index in range(len(model.blocks)))
            continue
        if target.startswith("blocks."):
            parts = target.split(".")
            relative = ".".join(parts[2:])
            if len(parts) >= 3 and parts[1].isdigit() and relative in _BLOCK_LORA_TARGETS:
                block_index = int(parts[1])
                if 0 <= block_index < len(model.blocks):
                    plan.append((block_index, relative))
                    continue
        unknown.append(target)
    if unknown:
        raise ValueError(f"unsupported LoRA target(s): {unknown}")
    unique: list[tuple[int | None, str]] = []
    seen: set[tuple[int | None, str]] = set()
    for item in plan:
        if item not in seen:
            seen.add(item)
            unique.append(item)
    return unique


def apply_lora(
    model: TinyDecoder,
    rank: int = 4,
    alpha: float = 8.0,
    targets: Sequence[str] | None = None,
) -> list[str]:
    """Freeze every base parameter, then wrap selected Linear layers.

    ``targets`` defaults to the public relative list. Fully qualified names
    from a saved checkpoint (for example ``blocks.0.attn.qkv``) are also
    accepted and resolved to that block. Only the new ``lora_A`` / ``lora_B``
    parameters remain trainable. The returned fully qualified names describe
    the layers actually wrapped.
    """
    selected = list(DEFAULT_LORA_TARGETS if targets is None else targets)
    if not selected:
        raise ValueError("at least one LoRA target is required")
    plan = _lora_plan(model, selected)
    if any(relative == "head" for _, relative in plan) and not isinstance(
        model.head, nn.Linear
    ):
        raise TypeError("head is already wrapped; apply_lora was called twice")
    for parameter in model.parameters():
        parameter.requires_grad_(False)

    wrapped: list[str] = []
    for block_index, relative in plan:
        if relative == "head":
            model.head = LoRALinear(model.head, rank=rank, alpha=alpha)
            wrapped.append("head")
            continue
        block = model.blocks[int(block_index)]
        parent, name = _resolve_relative(block, relative)
        child = getattr(parent, name)
        if not isinstance(child, nn.Linear):
            raise TypeError(f"target {relative!r} is not a plain Linear layer")
        setattr(parent, name, LoRALinear(child, rank=rank, alpha=alpha))
        wrapped.append(f"blocks.{block_index}.{relative}")

    for name, parameter in model.named_parameters():
        if name.endswith("lora_A") or name.endswith("lora_B"):
            parameter.requires_grad_(True)
    return wrapped


def count_parameters(model: nn.Module) -> dict[str, int]:
    """Count unique parameters, so a tied embedding/head is counted once."""

    total = sum(parameter.numel() for parameter in model.parameters())
    trainable = sum(
        parameter.numel() for parameter in model.parameters() if parameter.requires_grad
    )
    return {"total": total, "trainable": trainable, "frozen": total - trainable}


def state_checksum(model: nn.Module, kind: str = "base") -> str:
    """SHA-256 over named parameter bytes, used to prove frozen/base changes.

    ``kind="base"`` skips LoRA adapter tensors; ``kind="lora"`` includes only
    them. The checksum is an equality test for this run's device and dtype, not
    a cryptographic identity claim about the model's ideas.
    """
    if kind not in {"base", "lora"}:
        raise ValueError("kind must be 'base' or 'lora'")
    digest = hashlib.sha256()
    for name, parameter in sorted(model.named_parameters(), key=lambda item: item[0]):
        is_lora = name.endswith("lora_A") or name.endswith("lora_B")
        if kind == "base" and is_lora:
            continue
        if kind == "lora" and not is_lora:
            continue
        # A wrapped layer exposes the same frozen tensor as ``...base.weight``.
        # Normalizing that segment keeps before/after-wrap checksums comparable.
        normalized = name.replace(".base.", ".")
        value = parameter.detach().to("cpu").contiguous()
        digest.update(normalized.encode("utf-8"))
        digest.update(str(tuple(value.shape)).encode("ascii"))
        digest.update(value.numpy().tobytes())
    return digest.hexdigest()


def future_invisibility_check(
    model: TinyDecoder,
    tokenizer: WordTokenizer,
    text: str = "the red boat floats .",
    prefix_len: int = 4,
    seed: int = 0,
) -> dict[str, object]:
    """Change only the suffix after ``prefix_len`` and compare prefix logits.

    Equal logits are evidence that the implemented mask cuts the future off at
    the architecture level. They do not show that the model understands or
    predicts anything useful.
    """
    was_training = model.training
    model.eval()
    try:
        ids = tokenizer.encode(text, add_bos=True, add_eos=True)
        if len(ids) < prefix_len + 2:
            raise ValueError("text is too short for the requested prefix length")
        altered = list(ids)
        generator = torch.Generator().manual_seed(seed)
        for position in range(prefix_len, len(altered)):
            candidates = [index for index in range(len(tokenizer)) if index != altered[position]]
            pick = int(torch.randint(len(candidates), (1,), generator=generator))
            altered[position] = candidates[pick]
        left = torch.tensor(ids, dtype=torch.long).unsqueeze(0)
        right = torch.tensor(altered, dtype=torch.long).unsqueeze(0)
        with torch.no_grad():
            logits_left, _ = model(left)
            logits_right, _ = model(right)
        prefix_left = logits_left[:, :prefix_len, :]
        prefix_right = logits_right[:, :prefix_len, :]
        difference = float((prefix_left - prefix_right).abs().max())
        return {
            "prefix_len": prefix_len,
            "sequence_len": len(ids),
            "bitwise_equal": bool(torch.equal(prefix_left, prefix_right)),
            "max_abs_diff": difference,
            "suffix_changed": bool(
                not torch.equal(logits_left[:, -1:, :], logits_right[:, -1:, :])
            ),
        }
    finally:
        if was_training:
            model.train()


def save_checkpoint(
    path: Path | str,
    model: TinyDecoder,
    tokenizer: WordTokenizer,
    config: DecoderConfig,
    adaptation: dict[str, object] | None = None,
    meta: dict[str, object] | None = None,
) -> Path:
    """Save a self-describing checkpoint (state dict + config + vocabulary)."""
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "format": FORMAT,
        "config": asdict(config),
        "vocab": tokenizer.token_list(),
        "state_dict": model.state_dict(),
        "adaptation": adaptation or {},
        "meta": meta or {},
    }
    torch.save(payload, destination)
    return destination


def load_checkpoint(path: Path | str) -> tuple[TinyDecoder, WordTokenizer, dict[str, object]]:
    """Load a checkpoint with ``weights_only=True`` and rebuild any LoRA kit."""
    source = Path(path)
    if not source.exists():
        raise FileNotFoundError(f"checkpoint not found: {source}")
    payload = torch.load(source, map_location="cpu", weights_only=True)
    if not isinstance(payload, dict) or payload.get("format") != FORMAT:
        raise ValueError(f"not a {FORMAT} checkpoint: {source}")
    config = DecoderConfig(**payload["config"])
    tokenizer = WordTokenizer(payload["vocab"])
    if len(tokenizer) != config.vocab_size:
        raise ValueError("checkpoint vocabulary does not match config.vocab_size")
    model = TinyDecoder(config)
    adaptation = dict(payload.get("adaptation") or {})
    if adaptation.get("method") == "lora":
        apply_lora(
            model,
            rank=int(adaptation["rank"]),
            alpha=float(adaptation["alpha"]),
            targets=tuple(adaptation.get("targets") or DEFAULT_LORA_TARGETS),
        )
    model.load_state_dict(payload["state_dict"], strict=True)
    model.eval()
    return model, tokenizer, payload
