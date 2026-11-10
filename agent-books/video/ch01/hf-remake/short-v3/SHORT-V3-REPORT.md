# ch01-short-v3 deliverable (t173 polish)

**Path:** video/ch01/out/ch01-short-v3.mp4
**Backup of prior:** video/ch01/out/ch01-short-v2-backup.mp4 (+ original ch01-short-v2.mp4 kept)
**Duration:** 32.6s · **Size:** ~7.8 MB · **Res:** 1080×1920 @ 30fps
**No publish** (awaiting user gate)

## Improvements over v2
- **Denser motion:** faster hook beats; 5 alert pops (超时/格式/权限/上下文/打破) phrase-locked; VS 能跑/能停/能诊断 bullets on phrase onsets
- **Caption↔画面 sync:** kinetic muted during cart so karaoke + 考工记 plate carry meaning; scene cuts still on SentenceBoundary
- **马车:** book cover.svg → book-chariot-paper.png, portrait object-fit:cover crop; annotations 骏马/辔/舆/御者 phrase-locked; NOT cartoon
- **互动:** 猜一猜 before plate (Harness → 辔/缰绳)
- **watermark:** 小电讲电路 / 驭者 · Agent Harness
- **SFX / karaoke:** retained + stronger karaoke highlight
- **scrub:** META_TOTAL 0 (no 吸粉/冲击)

## Spot-check
| t | frame | ok |
|---|---|---|
| 5.2 | anti + caption | yes |
| 10.5 | alert 超时 | yes |
| 23.2 | quiz over VS | yes |
| 24.7 | book plate + 骏马 +「模型是马」 | yes |
| 26.0 | plate + 辔 +「Harness 是缰绳…」 | yes |
| 29.0 | CTA + chips | yes |

## Long-v4
Densified + assembled (build_dense_v4.py): 217 beats / 217 SFX / book-plate chariot TL; render started separately → out/ch01-long-v4.mp4.
