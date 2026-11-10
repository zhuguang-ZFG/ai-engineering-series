# Task 4 Report — Ch01 long lecture (pipeline restart)

**Status:** DONE_WITH_CONCERNS  
**Date:** 2026-10-28 (America/Adak)  
**Machine:** ca3e8acb-383a-46c7-968d-a39e42832327  
**Repo:** D:\Users\claude\claude-code-book-main

## Deliverables

| File | Result |
|------|--------|
| `video/ch01/out/ch01-long.mp4` | **OK** — 1920×1080 H.264 + AAC, **1148.33 s (~19:08)** ∈ [900,1200] |
| `video/ch01/out/ch01-long.srt` | **OK** — 147 cues, UTF-8 from edge-tts VTT |
| `video/ch01/out/ch01-cover.png` | **OK** — 1920×1080, title「智能体编程的新范式｜驭者·Agent Harness 01」 |

## Stack pieces actually used

| Piece | Used how |
|-------|----------|
| **HyperFrames** (`npx hyperframes` 0.8.210) | Rendered 6×12s hand-draw / engineering-board scene beds (`video/ch01/hf-long/scene-*.html` → `video/ch01/assets/beds/bed-*.mp4`) with `--low-memory-mode -w 1 -f 24 -q draft`. Beds looped+concat+muxed with VO via FFmpeg. |
| **huashu-art-motion** (cloned + exercised) | Whiteboard grammar `y3_whiteboard` still rendered: `video/ch01/assets/huashu/still/t003.00.png` from `assets/huashu/ch01-whiteboard.json`. Grammar cards/icons informed canvas stroke motifs in HF scenes. |
| **sweety-handdraw-video** (cloned only) | Repo present under `video/ch01/tools/sweety-handdraw-video`. **Not run end-to-end**: upstream states **macOS/Linux only**, Windows not promised; also needs image-gen host + VoxCPM2/VoiceStudio. Hand-draw *style* (stroke reveal, board grid, motif draw-on) approximated in HyperFrames Canvas instead. Locked voice remains edge-tts (not VoxCPM). |
| **edge-tts** | `zh-CN-YunyangNeural` `--rate=-10%` `--pitch=-5Hz`; 38 segments → `assets/vo/mp3` → `full.mp3` (~19:08). |

## Sources

- `docs/video/ch01/long-script.md` / `long-outline.md`
- Spec override: `docs/superpowers/specs/2026-10-27-yuzhe-video-pipeline-matrix.md`

## Method (pilot)

1. Extract VO paragraphs → edge-tts segments → concat audio + SRT.
2. Author HyperFrames compositions with seekable GSAP + Canvas stroke animations for hook / paradigm / arch / principles / practice / outro (numbers **1,884** / **512,664** on arch bed).
3. Render beds with HyperFrames low-memory mode (machine ~1–3 GB free; full continuous 19‑min HF capture judged unsafe).
4. Loop each bed to chapter duration, concat, mux Yunyang track.
5. Cover via Pillow; huashu whiteboard still for grammar proof.

## Gaps / concerns

1. **sweety full pipeline not executed on Windows** — clone + style appropriation only; true stroke-by-stroke Pillow/VoxCPM path needs Linux/macOS or upstream Windows support.
2. **Not a single continuous HyperFrames 19‑min capture** — motif-bed loop assembly used due to RAM; beds are real HF renders, timeline is FFmpeg.
3. **huashu used as still/grammar**, not full narrated film inside the long MP4 (upstream `render.py` defaults to locale encoding; ASCII spec workaround). Can re-render short y3 clips and cut into beds later.
4. **Visual loop repetition** — each chapter reuses a 12s bed; acceptable for pilot, upgrade path is longer per-chapter HF comps or sweety pages once host supports it.
5. Large binaries (`ch01-long.mp4` ~54 MB, tool clones) — commit policy left to controller; scripts/specs should be committed.

## Hard checks

```
ffprobe duration ≈ 1148.33 s
streams: h264 1920x1080 + aac
srt cues: 147
cover: ch01-cover.png present
```
