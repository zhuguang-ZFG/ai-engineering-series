# Progress ledger

Repo: D:\\Users\\claude\\claude-code-book-main (main)
Plan: docs/superpowers/plans/2026-10-27-yuzhe-ch01-pilot.md

Task 1: complete (commits 560e960..ef75a5a, review clean)
Task 2: complete (commits ef75a5a..fbf9d6c, controller review clean)
Task 3: complete (commit 4b8068f, user confirmed YunyangNeural -10%/-5Hz)

Pipeline remapped 2026-10-27: long=sweety-handdraw+HyperFrames+huashu-art-motion; short=lemo-opuscar; voice Yunyang locked.

Task 4: complete (DONE_WITH_CONCERNS) — ch01-long.mp4 1148s 1920x1080 + srt + cover; HF beds + huashu still + edge-tts; sweety clone-only on Windows. See task-4-report.md
Task 4: complete with concerns (a4acbe4, 1148s; sweety Windows unsupported, HF beds+ffmpeg)

## Beyond the ch01 pilot

The pilot plan covers ch01 only. ch02-ch04 were produced afterwards against
the same pipeline; each chapter's own record lives in `docs/video/<ch>/STATUS.md`
and is the authority for what shipped where. Summary as of 2026-10-29:

| 章 | 短片 | 长讲 | B站 | 抖音 | 小红书 | 视频号 |
|----|------|------|-----|------|--------|--------|
| ch01 | v2 | v4 (1148s) | BV1rGx76EEpJ | — | — | — |
| ch02 | v3 (~31s) | v1 (~100MB, 未过片) | 未发 | — | — | — |
| ch03 | v1 (~46s) | v2 (~597s) | BV1W4sZ6TERE | PENDING | PENDING | — |
| ch04 | v1 (~39s) | v2 (~453s) | BV1Kkso6MEvv | DONE | BLOCKED (账号禁发) | DONE |

合集：season_id 9436416「驭者·Agent Harness」。

Timing calibration (established at ch05): narration runs at **2.89 汉字/秒** with
云扬 -10%/-5Hz, back-computed from ch02's measured VO (628s ÷ 1811 汉字). Across
ch01-ch04 the ratio of finished runtime to pure narration time stays within
0.97-1.03, so the animation beds run under the voice rather than adding hold
time — which means 口播汉字数 ÷ 2.89 predicts the finished runtime while the
script is still being written. Worth knowing because the "15-20 min" line in
every gate checklist had been passed over in silence: ch03 shipped at 9.9 min
and ch04 at 7.6 min. ch05's script was sized against the measured rate instead.

Rules carried forward, both learned the hard way:

- 先过片，再发布 — the gate checklist in each chapter's package is a hard
  precondition, and ch02's long cut has not passed it yet.
- 视频号 allows one post-publish description edit with a 20-character budget,
  so the full description and tags must go into the publish form before
  submitting. ch04 spent its single edit recovering an empty description.

Next: ch05「设置与配置 -- Agent 的基因」, source
`第二部分-核心系统篇/05-设置与配置-Agent的基因.md`.
