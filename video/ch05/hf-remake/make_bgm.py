#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Make the ch05 short's music bed: short/assets/bgm/track.wav.

build_short.py only mounts the bed; it does not generate it (this takes about
three minutes on CPU). Run it once, then rebuild:

    python3 video/ch05/hf-remake/make_bgm.py
    python3 video/ch05/hf-remake/build_short.py

Why this file exists instead of the skill's own command:
  * `media-use resolve --only bgm` derives its length from the TTS voices it made
    itself and caps at 30 s, so it cannot produce a 51 s bed.
  * The engine prefers Lyria whenever a Google key is present, and would
    `pip install google-genai` and spend that key. This script calls the local
    MusicGen route directly and never touches the network beyond the model hub.
  * The engine spawns the generator detached; on this machine three detached
    runs died mid-generation with no traceback. Foreground works, so this is
    foreground.

Measured on this machine (torch 2.14.1+cpu, 6 threads, --seed 7): model load
5.3-5.9 s, the 24 s seed in 175-202 s, peak 0.890, output -18.3 LUFS / -1.0 dBTP /
LRA 4.1 LU. Those last three are reproducible: a second run to a scratch path came
out md5-identical (8511a9a71ad36b49cf138c04cce7c434), only the wall time moved.
build_short.py parks it 12 LU under the -24.9 LUFS narration with BGM_GAIN = 0.117
(-18.6 dB).
"""
from __future__ import annotations

import argparse
import math
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE / "short" / "assets" / "bgm" / "track.wav"

PROMPT = (
    "calm minimal electronic instrumental underscore, muted synth plucks over a soft warm pad, "
    "steady low pulse, restrained documentary tech explainer background, instrumental, loopable"
)
TARGET_S = 51.0     # the film is 50.936 s; one second of headroom
SEED_S = 24.0       # kept short on purpose: tokens cost CPU time and RAM
TOKEN_RATE = 50     # musicgen-small decodes 50 tokens per second of audio
CROSSFADE_S = 2.0   # the engine's own default is 0.3 s, too short to hide a loop
FADE_IN_S = 0.8     # must match data-fade-in in build_short.py's bgm_tag()
FADE_OUT_S = 1.5
MUSIC_SEED = 7      # pinned: the LUFS numbers below are only true for this take


def equal_power_loop(seed, target_len: int, xf: int):
    import numpy as np

    if seed.shape[0] >= target_len:
        return seed[:target_len]
    xf = min(xf, seed.shape[0] // 2)
    if xf < 1:
        reps = int(math.ceil(target_len / seed.shape[0]))
        return np.tile(seed, reps)[:target_len]
    ramp = np.linspace(0.0, 1.0, xf, dtype="float32")
    fade_out, fade_in = np.cos(ramp * (math.pi / 2)), np.sin(ramp * (math.pi / 2))
    out = seed.copy()
    while out.shape[0] < target_len:
        out = np.concatenate(
            [out[:-xf], out[-xf:] * fade_out + seed[:xf] * fade_in, seed[xf:]]
        )
    return out[:target_len]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed-seconds", type=float, default=SEED_S)
    ap.add_argument("--target-seconds", type=float, default=TARGET_S)
    ap.add_argument("--seed", type=int, default=MUSIC_SEED,
                    help="MusicGen sampling seed; the documented levels were measured on this one")
    ap.add_argument("--force", action="store_true", help="overwrite an existing track.wav")
    ap.add_argument("--out", type=Path, default=OUT,
                    help="where to write; point it at a scratch file to verify the seed")
    args = ap.parse_args()
    out = args.out

    if out.exists() and not args.force:
        print(f"exists, use --force to overwrite: {out}")
        return 0

    import numpy as np
    import soundfile as sf
    import torch
    from transformers import AutoProcessor, MusicgenForConditionalGeneration

    torch.set_num_threads(6)
    torch.manual_seed(args.seed)
    out.parent.mkdir(parents=True, exist_ok=True)

    started = time.time()
    processor = AutoProcessor.from_pretrained("facebook/musicgen-small")
    model = MusicgenForConditionalGeneration.from_pretrained("facebook/musicgen-small")
    model.eval()
    sr = int(model.config.audio_encoder.sampling_rate)
    print(f"model loaded in {time.time() - started:.1f}s sr={sr}")

    tokens = max(1, int(math.ceil(min(args.seed_seconds, args.target_seconds) * TOKEN_RATE)))
    started = time.time()
    inputs = processor(text=[PROMPT], padding=True, return_tensors="pt")
    audio = model.generate(**inputs, max_new_tokens=tokens, do_sample=True)
    seed = audio[0, 0].detach().cpu().numpy().astype("float32")
    print(f"seed of {seed.shape[0] / sr:.2f}s generated in {time.time() - started:.1f}s")

    peak = float(np.max(np.abs(seed)))
    if peak > 1e-6:
        seed = seed * (0.89 / peak)

    want = max(1, int(round(args.target_seconds * sr)))
    final = equal_power_loop(seed, want, int(round(CROSSFADE_S * sr)))
    n_in = min(int(round(FADE_IN_S * sr)), final.shape[0] // 2)
    n_out = min(int(round(FADE_OUT_S * sr)), final.shape[0] // 2)
    final[:n_in] *= np.linspace(0.0, 1.0, n_in, dtype="float32")
    final[-n_out:] *= np.linspace(1.0, 0.0, n_out, dtype="float32")

    sf.write(str(out), final, sr)
    print(f"wrote {out} duration={final.shape[0] / sr:.3f}s peak={float(np.max(np.abs(final))):.3f}")
    print("next: python3 build_short.py   (expect bgm=yes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
