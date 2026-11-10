# ch01-long-v4 densify plan

Status: planned / not rendered yet. Source: ch01-long-v3 (~19m08s).

## Goals
- Higher motion density: shorten holds from ~8–12s → ~4–6s beat cadence
- More huashu whiteboard inserts (reuse 01–13 assets; double-insert where VO allows)
- Keep: watermark 小电讲电路/驭者, karaoke captions, 猜一猜互动, 马车隐喻, 云扬 VO
- Hard A/V sync: scene/beat cuts land on transcript phrase boundaries (same discipline as short-v2)
- No 吸粉/冲击 meta on screen
- Output: video/ch01/out/ch01-long-v4.mp4
- No publish until user gate

## Approach
1. Clone build_dense_v3.py → build_dense_v4.py
2. Split each BLOCKS beat that holds >7s into 2 micro-beats (kinetic label + diagram punch)
3. Add huashu re-entries mid-section (e.g. arch layers again near tools; principles chips cascade)
4. Align beat `start` offsets to nearest transcript word boundaries from transcript.json
5. Increase SFX density (~1 hit / 2–3s on phrase onsets)
6. Spot-check frames every ~60s for caption lag and sparse holds before full render

## Block densify targets (relative)
| block | v3 beats | v4 target |
|---|---|---|
| b01_hook | 7 | 11–12 |
| b02_paradigm | 12 | 18–20 |
| b03_arch | 12 | 18–20 |
| b04_principles | 13 | 20–22 |
| b05_practice | ~6 | 10–12 |
| b06_outro | ~4 | 6–8 |

## Order
1. Deliver short-v2 first (user gate)
2. Then implement build_dense_v4 + assemble + render overnight-class job

## Book-faithful chariot (t171-t172)
- Source: yuyu-book/illustrations/cover.svg (Kaogongji four-horse plate, single-line baimiao)
- Raster: assets/book-chariot-paper.png (paper ink) — NOT cartoon ellipse SVG
- Annotations as print slips (骏马/辔/舆/御者), phrase-locked to VO
- Same asset + discipline for every chariot beat in long-v4
- Full polish bar: dense motion, caption-picture sync, watermark, karaoke, quiz, SFX, no meta

## Progress
- short-v2 delivered polished (book plate + sync)
- build_dense_v4.py: CHARIOT_SVG → book plate HTML (assets/book-chariot-paper.png)
- Still TODO before render: densify beat table (shorter holds), copy plate into long project assets, phrase-lock captions, overnight render



## Progress update (t173)
- short-v3 delivered for gate: out/ch01-short-v3.mp4
- build_dense_v4 densified: b01=9 b02=45 b03=54 b04=63 b05=28 b06=18 beats; huashu doubled mid-section; SFX 217; chariot TL → book-plate Ken Burns; META_WARN_TOTAL 0
- assemble OK; overnight render next
