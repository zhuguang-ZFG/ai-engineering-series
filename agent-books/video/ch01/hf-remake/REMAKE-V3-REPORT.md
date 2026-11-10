# ch01-long v3 remake report

- **Status:** SUCCESS
- **Shell:** 605238 / PID 1032 — exit_code 0 (ended 2026-10-28T09:39:58Z)
- **Output:** `D:\Users\claude\claude-code-book-main\video\ch01\out\ch01-long-v3.mp4`
- **Duration:** 1148.37 s (19m 8.4s) — within 900–1200s target
- **Size:** 190,799,708 bytes (~182.0 MB)
- **Video:** 1920x1080 H.264 @ 30fps; Audio AAC stereo 48kHz
- **Render wall time:** ~60m 41s (capture streaming + assemble)

## Feature checklist (spot + source)

| Item | Result |
|------|--------|
| Watermark 小电讲电路 / 驭者 | YES — top-right on all spot frames (t25s, 2m, 5m30, 10m, 15m, 18m30) |
| Karaoke captions | YES — captions-zh mounted; 4855 `.kw` spans + `#ffe08a` highlight anim; bottom caption bar visible every spot |
| Captions count | 147 segments (TRANS) in build; captions host track 10 |
| Reader interaction | YES — quiz「猜一猜」at ~2:16; pause「停一下 · 想一想」at ~0:28; b01/b02 quiz+pause in comps |
| No meta 吸粉/冲击 | YES — `_verify_v3.py` clean; spot frames show book content only |
| Dense motion / 马车 metaphors / SFX | Included in v3 project (pre-render check passed); not re-audited frame-by-frame |

## Spot frames

Saved under `video\ch01\out\v3-spot\` and `C:\Users\zhugu\v3-spot\`.

## Not done (per brief)

- Short video: not started
- Publish / three platforms: not started

## Notes

- Babysat existing Shell 605238 only; no second render started.
- TEMP stayed `.hf-tmpdir`; no ENOENT retry needed.
