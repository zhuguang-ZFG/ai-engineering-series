# ch01-long v4 remake report

- **Status:** SUCCESS
- **Job:** hyperframes renderJobId `3eb51363-ad95-4e93-b78c-1114d0a09726` (node PID 32544; ffmpeg 28696/33096 StartTime 2026-10-28 19:31 America/Adak)
- **Output:** `D:\Users\claude\claude-code-book-main\video\ch01\out\ch01-long-v4.mp4`
- **Duration:** 1148.37 s (19m 8.4s) — within 900–1200s target
- **Size:** 205,205,029 bytes (~195.7 MB)
- **Video:** 1920x1080 H.264 @ 30fps; Audio AAC stereo 48kHz
- **Render wall time:** ~89m 34s (capture 88m 10s + assemble 3.4s; one mid-run screenshot-session retry, same job)

## Feature checklist (spot + source)

| Item | Result |
|------|--------|
| Watermark 小电讲电路 / 驭者 | YES — top-right on spot frames (t25s, 28s, 33s quiz, 1m05 chariot, 5m30, 10m, 15m, 18m30) |
| Karaoke captions | YES — captions-zh mounted; 4855 `.kw` spans + `#ffe08a` highlight; bottom caption bar on every spot |
| Captions host | host-captions-zh track 10 for full duration |
| Reader interaction | YES — pause「停一下 · 想一想」at ~0:28; quiz「猜一猜」at ~0:33 (A/B/C); b01/b02 quiz+pause in comps |
| 驭者/马车 book metaphor | YES — chariot silhouette (考工记-style) at ~1:05 in §1.1 |
| No meta 吸粉/冲击 | YES — `_verify_v3.py` clean; spot frames show book content only |
| Dense motion / SFX | Included (217 sfx clips in index; gallop/rein_snap/whoosh/etc.) |

## Spot frames

Saved under `video\ch01\out\v4-spot\` and `C:\Users\zhugu\v4-spot\`.

## Not done (per brief)

- Publish / three platforms: not started
- Short-v3 already user-passed (no change this turn)

## Notes

- Babysat existing long-v4 render only; no second render started.
- Mid-capture Protocol error triggered hyperframes' own fresh-screenshot retry; job continued to completion.
- TEMP stayed `.hf-tmpdir\hf-render-fOBYKC`; final assemble wrote `out\ch01-long-v4.mp4` at 2026-10-28 20:41 America/Adak.
