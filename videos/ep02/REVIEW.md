# EP.02 「会写诗的贪吃蛇」 review log

Timeline: 8 scenes, 194.5 s @ 1920×1080 / 30 fps. Voice `edge-tts zh-CN-XiaoxiaoNeural`
(rate +4%), BGM `assets/bgm/track-long.wav` @ 0.16 with 0.8 s fade-in / 2 s fade-out.

| scene | id | start | dur | content |
|---|---|---|---|---|
| s1 | hero1 | 0.0 | 16.9 | hook: 上期那条蛇，现在会写诗 |
| s2 | need | 16.9 | 29.1 | 四句话需求 vs 太糊/能跑 |
| s3 | play | 46.0 | 21.4 | 对话 → 单文件 → 跑起来的检查清单 |
| s4 | break | 67.4 | 24.1 | 现象+期望 修 bug，报错整段贴 |
| s5 | poem | 91.5 | 25.5 | 食物换成汉字，吃满三个续一句诗 |
| s6 | polish | 117.0 | 31.0 | 打磨：一次只改一件事（2×2 卡片） |
| s7 | pitfall | 148.0 | 22.3 | 三个坑：一次改十处 / 只贴报错 / 不存版本 |
| s8 | hero2 | 170.3 | 24.2 | 小结 + 下一期预告（本地 AI IDE） |

## check

`npm run check` (hyperframes 0.8.210): **passed** — lint 0/0, runtime 0/0, layout 0/0,
motion 0/0, contrast 0/0 (66/66 WCAG AA), craft 0/0, audio 0/0.
Report `9c9284eb-184f-4c3c-a61e-8384b21af867.json`.

Fixed during the pass:

- `gsap_non_transform_motion` on `#y-head` (animated `left`/`top`) → transform `x`/`y`.
- `text_below_floor`: every text run raised to ≥ 28 px.
- `content_overlap` × 4 and `text_hidden_beneath_opaque`: bottom bands of `break`,
  `poem`, `polish`, `pitfall`, `play` ran into the caption strip (top 896 px).
  Boards/panels and the `p-poembar` moved above 890 px; `need` cards 148 → 176 px and
  terminal line 2 shortened so it no longer wraps.

## captions

`tools/build_captions_v2.py` (VAD from the WAV, clause-split from the transcript).

Defect found and fixed while building EP.02: `clauses()` stripped `[A-Za-z0-9]+`
before splitting, so every Latin token vanished from the rendered captions
(`变成 能接住的`, `一次让 改十处`). The filter is gone; Latin/digits are kept
verbatim, packing is now clause-aware (≤ 8 chars, never splitting a Latin run) and
1-char groups merge into the neighbour instead of being dropped.

Coverage invariant (verified): concatenating each segment's caption text reproduces
its transcript exactly, punctuation-insensitive — 142 groups, 0 overlaps,
max group 10 chars (`装一个 AI IDE`).

## covers

Reused the EP.01 snake family, retitled for EP.02 (`EP.02` pill, 上期那条蛇，现在会 / 写诗,
把吃方块，改成吃汉字, `> 吃掉春风来，拼成一句诗`):

- `assets/covers/cover3x4.jpg` 1080×1440 (Douyin 竖封面 / 视频号 profile)
- `assets/covers/cover4x3.jpg` 1440×1080 (Douyin 横封面)
- `assets/covers/cover16x9.png` 1920×1080 (Bilibili)

Bilibili's 封面制作 editor stores exactly the art you last applied (`完成`) and the public
`pic` mirrors it: applying the 4:3 art gave a 1440×1080 `pic`, applying the 16:9 art gave
1920×1080 matching `cover16x9.png` (mean abs diff 1.57). Upload the 16:9 art last.

## render + delivery

- `renders/llm101-ep02_4k_master.mp4` 3840×2160, 194.5 s, 21.9 MB (supersampled master)
- `renders/llm101-ep02_1080p_delivery.mp4` 1920×1080, CRF 13 Lanczos, 12.0 MB
- `renders/llm101-ep02_latest.mp4` copy of the delivery
- Loudness −16.7 LUFS integrated / −2.1 dBTP (EP.01: −16.5 / −1.9)

## publish

| platform | id | evidence |
|---|---|---|
| Bilibili | `BV1YWxP6YECS` | state 0, 195 s, tid 231, 7 tags, season 不会写代码也能做软件｜VIBE CODING 101, `pic` 1920×1080 = 16:9 art. **Re-cut 4K master swapped in 2026-10-30 15:5x via 更换视频**: `cid 43174596317`, title 37 / desc 252 / 7 tags / tid 231 / season 9443639 re-verified on `/x/vupre/web/archive/view`, queue row read `llm101-ep02_2026-10-30_14-04-04 4K 上传完成` |
| Douyin | `7702367532556111154` | **Re-published 2026-10-30** after deleting the desynced cut: 194500 ms, title 14 / desc 130 chars, 横 4:3 + 竖 3:4 art applied, 合集 VIBE 101 第3集, 自主声明 无需添加自主声明. Superseded `7702278077363014922` |
| 视频号 | `export/UzFfBgAAxICJKDpzbCyHk8zT4DCavAP2L3D81dEyD0uEcp17fg` | 1920×1080, 11,047,779 B (= the re-cut delivery), 短标题 会写诗的贪吃蛇, 190 字描述, 合集 VIBECODING 第3集, 视频标注 含AI生成内容, 3:4 封面. Superseded `…xKCJfC5kdgW…` |

Douyin submitted with 无需添加自主声明 and 立即发布/公开 defaults; the publish-options dialog did not
appear on either publish run (the click went straight to 内容管理), so 不同时发布 was not available to set.

视频号 shares the playlist card from the 3:4 art; the 4:3 分享卡片 editor still refuses to open
(`.horizon-img-wrap .edit-btn` no-op), same as EP.01.

## caption timing — re-cut 2026-10-30

The track that shipped first (`sha256 7078d7b5…`, 142 groups) drifted: the builder timed cues from
each clip's duration while the narration had been re-fitted with `--rate`, so every clause after the
first ran late. `tools/build_captions_v2.py` now takes its word timings from the TTS engine's
`WordBoundary` stream, cached per scene by `tools/tts_words.py`, and asserts each scene's last cue.

`compositions/captions.html` now holds the re-cut track: **125 groups**, `sha256 c9342eaf…`, same
100% text match, and it is the track burned into the re-uploaded delivery (`…_1080p_delivery.mp4`,
11,047,779 B). Running the builder again reproduces it byte-for-byte as long as the cached word
timings exist.

There is no git repository anywhere under the workspace root (`llm101-ep02`, `llm101-film`, `llm101-ep03`
and the workspace root all report "not a git work tree"), so a superseded `captions.html` can only be
recovered from a manual copy — keep one before rebuilding. Any future re-render must also re-upload on
all three platforms, since the captions are burned in.

