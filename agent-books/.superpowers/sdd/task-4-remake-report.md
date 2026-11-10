# Task 4 Remake Report — ch01-long.mp4

- Date: 2026-10-28 (America/Adak)
- Docs followed: `docs/video/ch01/matrix-cookbook.md` (commit da341a4)
- Pipeline: HyperFrames bed + burned captions rail; huashu-art-motion whiteboard inserts ≤8s; Yunyang VO (existing full.mp3)

## Key commands

```text
# 1) HyperFrames skills + project (already inited as video/ch01/hf-remake)
npx hyperframes skills update
npx hyperframes add captions

# 2) VO → SRT (existing transcript preserved)
# npx hyperframes transcribe full.mp3 --language zh
# (used ch01-long.srt → transcript.json --preserve-cues)

# 3) huashu per-shot (whiteboard y3, ≤8s)
$env:PYTHONUTF8=1
uv run --with playwright python scripts/engine/render.py --spec assets/huashu-specs/NN.json --out assets/huashu/NN.mp4
# clips 01–13 rendered on Windows after Playwright Chromium install

# 4) lint / check / render with caption rail
npx hyperframes lint   # 0 errors
npx hyperframes check  # 0 errors (warnings: dead_stretch / nested_media)
npx hyperframes render --low-memory-mode --quality looks --fps 30 --workers 1 `
  -o ../out/ch01-long.mp4

# 5) No looping beds — compositions b01–b06 unique evolving beats + 13 unique huashu inserts
```

## Outputs

- `video/ch01/out/ch01-long.mp4`
- `video/ch01/out/ch01-long.srt`
- cover: TBD after render

## Notes

- Huashu raw renders were ~45MB/7s; recompressed CRF23 (~0.3–0.5MB) for HF ingest.
- Captions: `compositions/captions-zh.html` rail (bottom ~72px), burned via HF captions track.
- Anti-pattern avoided: no `(localT%12)/12` looping beds.