# EP.03 「这条蛇，住进项目里」 review log

Timeline: 8 scenes, 191.2 s @ 1920×1080 / 30 fps. Voice `edge-tts zh-CN-XiaoxiaoNeural`
(default rate — EP.01/02 used +4%; 4 % is imperceptible across episodes, noted for the record).
BGM `assets/bgm/track-long.wav` @ 0.16 with 0.8 s fade-in / 2 s fade-out.

Topic is fixed by EP.02's ending: 「下一期我们离开浏览器，装一个 AI IDE，把这条蛇搬到本地项目里，
加文件、加依赖、加调试」.

| scene | id | start | dur | content |
|---|---|---|---|---|
| s1 | hero1 | 0.0 | 17.4 | hook: 蛇还在，但它只是一个网页文件 |
| s2 | why | 17.4 | 27.5 | 单文件四件事做不了 → 本地项目四件都能 |
| s3 | install | 44.9 | 22.6 | 装 Cursor：下载 / 登录 / 打开文件夹 / 通读结构 |
| s4 | move | 67.5 | 24.8 | 拆成 index.html + style.css + game.js，只搬家不改行为 |
| s5 | deps | 92.3 | 25.5 | package.json 清单、锁文件、node_modules 别读别提交 |
| s6 | debug | 117.8 | 27.1 | 断点停住看变量与调用栈，先复现再定位最后改 |
| s7 | pitfall | 144.9 | 22.1 | 三个坑：喂 node_modules / 一次装五个 / 不写 .gitignore |
| s8 | hero2 | 167.0 | 24.2 | 小结 + 下一期预告（发布上线） |

Scene slots are voice duration + 0.7 s; offsets are recomputed from the WAVs, never hand-tuned.

## check

`npm run check` (hyperframes 0.8.210): **passed, clean** — lint 0/0, runtime 0/0, layout 0/0,
motion 0/0, contrast 83/83 WCAG AA, craft 0/0, audio 0/0 (report `4a1694e8-143c-489f-90af-41ddbb97dc7e`).

Fixed during the pass:

- `text_box_overflow` / `container_overflow` in `deps` (package.json card): 27 px / 1.62
  code line box grew past the 388 px card → card 408 px, code 28 px / 1.45, term moved to 744.
- `gsap_repeated_fromto_without_baseline` on `#g-cur1` → second call is now `tl.to()`.
- `studio_missing_editable_id` on the three `.m-strip` rows → `#m-s1..m-s3`.
- `text_occluded` (debug line numbers under the execution-band overlay) → `.g-cur` z-index 1,
  `#g-lines` z-index 2.
- Contrast: `#i-tree-h`, `#i-ed .ln`, `#g-ln i` = `#30363d` on `#0d1117` (1.55:1) → `#6e7681`.
- `text_below_floor`: every run raised to ≥ 28 px (tree header, file rows, editor, terminal,
  cards, PAUSED chip, PITFALL labels) and `#g-stack` 140 → 152 px.

## captions

`tools/build_captions_v2.py` — cue times come from the TTS engine's own word boundaries
(`tools/tts_words.py` caches `assets/voice/<scene>.words.json`), text comes from the transcript.

Two generator defects surfaced on this episode's material and are fixed in all three copies
(`llm101-film`, `llm101-ep02`, `llm101-ep03` — bodies now byte-identical, only `OFFSETS` differs):

1. `PUNCT` split on every `.`, so `index.html` / `game.js` / `package.json` broke at the dot
   (`结构放 index` | `html`). A dot is now a boundary only when it is not between two word
   characters (`(?<![A-Za-z0-9_])\.+|\.+(?![A-Za-z0-9_])`).
2. `latin_split` only protected `[A-Za-z0-9-]`, so `node_modules` split at the underscore.
   The guard now uses `WORD_CH = set("-_.")`, and a space immediately before a Latin token
   flushes the current group (`len ≥ 2`, never when both sides are Latin) so `把整个` +
   `node_modules` / `项目里先有` + `package.json` no longer fuse; a hard 14-char cap backs it up.

Coverage invariant (verified): concatenating each segment's caption text reproduces its
transcript exactly, punctuation-insensitive — **127 groups, 0 overlaps, 0 cue-edge spaces,
max group 12 chars, 5 `AI` tokens, last cue ends 190.11 s of 191.2 s**.

### sync defect (found after the first render)

The first render shipped captions that ran **ahead of the voice** — the viewer's complaint
「字幕和配音对不上」. Measured against whispered ASR of the same WAVs, median cue error was
**+3.03 s**, p90 6.19 s, worst 7.92 s, and every scene's cue list stopped **4.5–8.2 s before its
audio ended**:

| scene | audio | old last cue ended early by |
|---|---|---|
| s1 | 16.70 | 4.51 s |
| s2 | 26.81 | 8.18 s |
| s3 | 21.94 | 6.50 s |
| s4 | 24.12 | 7.53 s |
| s5 | 24.84 | 7.10 s |
| s6 | 26.35 | 7.72 s |
| s7 | 21.43 | 6.64 s |
| s8 | 23.52 | 5.74 s |

Root cause: `align()` laid clauses on a *speech-time* axis (pauses removed) and `pack()` then
added the scene offset straight to those numbers — `speech_to_wall()` existed but was never
called. Every cue after a pause was early by that pause, and the total of them is exactly the
shortfall above.

Two rejected alternatives: keeping the char-ratio model and merely mapping through
`speech_to_wall()` (measured below — 2 s outliers survive inside long clauses), and ASR-driven
forced alignment (adds a 500 MB model to a build step, and misrecognised characters need fuzzy
matching against the script).

Fix: cue time now comes from the engine's `WordBoundary` stream. `tools/tts_words.py` re-synthesises
each scene and asserts the regenerated take is the shipped take (duration within 30 ms; a
different take fails loudly), then caches `[[start, end, word], …]`. The caption builder walks the
shown text through that spoken stream one character at a time, so each character inherits the
timestamp of the character it came from; characters the engine drops while pronouncing a token
(`style.css` is spoken `style` + `css`) inherit the next syllable, and any real divergence
aborts the build.

Guard added to the builder: every scene's last cue must land within 0.6 s of its audio end.
The guard fails on the old output (8/8 scenes, worst 8.18 s) and passes on the new one.

Verified after the fix, again against whispered ASR (independent of the TTS timeline):
**median +0.03 s, mean |error| 0.06 s, p90 0.15 s, max 0.32 s**; per-scene last-cue offset
+0.38…+0.42 s (trailing silence).

Caption fades were replaced with a 12 px slide-in: a fade dimmed the pill itself, so a frame
sampled mid-fade measured 1.33:1 against a bright scene. Slide keeps the pill at full opacity
at every frame (contrast 83/83).

Fixed by the 2026-10-30 re-cut: EP.01 (`llm101-film`, 153 cues, `sha256 fb014005…`) and EP.02
(125 cues, `sha256 c9342eaf…`) were rebuilt from the TTS `WordBoundary` cache and re-uploaded on
all three platforms; the earlier note here (shipped bytes `83b104f5…` / `7078d7b5…`, "re-cutting
them is a separate delete-and-upload") is obsolete. The remaining reviewable items are the
`PUNCT` dot bug and its fix, both covered in *caption punctuation fix* below.

## covers

New-but-related family in `D:/Users/dmx/.tmp/covers/opus55/ep03-{3x4,4x3,16x9}/`, archived to
`assets/covers/`:

- `cover3x4.jpg` 1080×1440 (抖音 竖封面 / 视频号 资料卡)
- `cover4x3.jpg` 1440×1080 (抖音 横封面)
- `cover16x9.png` 1920×1080 (Bilibili)

Motif: the same segmented snake ribbon, now ending inside an IDE window — file chips
`index.html / style.css / game.js / package.json` plus a terminal `$ npm i howler` →
`$ npm run dev`. Headline 这条蛇，现在住进 / **项目**. Vision review: 9/10 on all three,
no clipping or overlap; the ribbon passes behind the green 项目 by design.

Bilibili stores the last-applied art and the public `pic` mirrors it — upload the 16:9 art last.

## render + delivery

- `renders/llm101-ep03_<stamp>.mp4` 3840×2160 supersampled master
- `renders/llm101-ep03_<stamp>_1080p_delivery.mp4` 1920×1080, CRF 13 Lanczos
- `renders/llm101-ep03_2026-10-30_16-21-34_1080p_delivery.mp4` is the current upload file (10,237,207 B); no `_latest.mp4` copy is kept in this project

## publish

First cut (desynced captions) published 13:09, then replaced once the sync fix landed.

| platform | id | evidence |
|---|---|---|
| Bilibili | `BV1ALxY6aExs` (same BV, 更换视频) | first cut verified at state 0, 192 s, 3840×2160, tid 231, title 38, desc 263, 7 tags, season 9443639, `pic` diff 1.62. **Re-cut 4K master live**: `cid 43170990112 → 43174659974 → 43175972597` (the second swap carries the `.gitignore` caption fix), archive view 38 / 263 / 7 tags / tid 231 / season 9443639, `playurl timelength 191210 ms`, `pic …50403964f9556d54c8.jpg` 1920×1080 diff 1.76 vs `cover16x9.png`. The earlier 13:41 submit never swapped the file — the 更换视频 upload has to be driven through `Page.setInterceptFileChooserDialog` + `Page.fileChooserOpened` + `DOM.setFileInputFiles`, a DOM `.click()` on 更换视频 produces no file input at all |
| Douyin | `7702378920691207450` | **Re-published 2026-10-30 16:4x** (`.gitignore` fix): 191211 ms, `mix_info.statis.current_episode` 4, cover 540×721 (3:4 art), superseded `7702368106731162916`. Earlier re-publish, for the record: **re-published 2026-10-30 16:0x** (deleted the previous re-cut so the 合集 numbering could be rebuilt): 191200 ms, title 14 chars, desc 143 chars, 横 4:3 + 竖 3:4 art, 合集 VIBE 101 第4集, 自主声明 无需添加. Superseded `7702331649249266971`. **The description was rewritten, not restored** — the original 162-char text only ever existed on the deleted work and is not in `platform_meta.json` or any file, so this desc is newly authored in the EP.01/EP.02 house pattern (title + 3 lessons + 3 pitfalls + CTA). EP.01/EP.02 descs came verbatim from `platform_meta.json` |
| 视频号 | `export/UzFfBgAAxIuJXHkJb1qGk8zT4DCa-hE5jbUSVZ9XdjpkMLvrNg` | **Re-published 2026-10-30 16:49** (`.gitignore` fix): 191.2 s, 1920×1080, 10,237,207 B, 短标题 `住进项目里的蛇`, 127 字描述, 资料卡 3:4 = `cover3x4.jpg`, 声明原创 (list reads 原创审核中), 合集 VIBECODING 第4集. Superseded `…xKaJCFMYeTGHk8zT4DCajYhMhDSW24_oTF4EgIk0ug` (191 s, 10,249,007 B, 162 字描述). **That 162-char description was lost with the deletion** — it existed only on the live post and in no file; the replacement uses the newly written 抖音 text. |

Bilibili 更换视频 resets the form (its dialog says 个性化配置需重新设置): title, description,
tags, 分区, 合集 and cover all had to be re-entered — the BV and its season slot survive, the
metadata does not. The description was recovered verbatim from the still-live archive (263 chars).
Deleting instead would have needed a geetest captcha the delete endpoint demands (code 340022).

## caption re-cut wave — 2026-10-30

All three episodes were re-rendered after the `tts_words` fix; EP.01 and EP.02 shipped with the
desynced track originally, so every platform had to be refreshed.

| platform | EP.01 | EP.02 | EP.03 |
|---|---|---|---|
| Bilibili | `BV1CoxY6YEhF`, cid `43174464613` | `BV1YWxP6YECS`, cid `43174596317` | `BV1ALxY6aExs`, cid `43175972597` |
| Douyin | `7702366884670246195` 第2集 | `7702367532556111154` 第3集 | `7702378920691207450` 第4集 |
| 视频号 | `…xIeJfCQjJC-Hk8zT4DCaE8uzMLHtIu11S1lMQJ8oeg` | `…xICJKDpzbCyHk8zT4DCavAP2L3D81dEyD0uEcp17fg` | `…xIuJXHkJb1qGk8zT4DCa-hE5jbUSVZ9XdjpkMLvrNg` |

Douyin 合集 numbers are assigned by publish order and existing works never renumber, so the only
way to restore 第2/3/4集 was to delete all three re-cuts and re-upload EP.01 → EP.02 → EP.03 in
order. 视频号 does have a 更改排序 dialog (`.collection-order-draggable-list`, SortableJS-style
handles `.drag-icon-wrap` at x≈381): a CDP `mouse.down` + stepped `mouse.move` + `mouse.up` drag
persists immediately, no save button. Bilibili 更换视频 keeps the season slot; per-episode
metadata (title / desc / tags / tid 231 / cover) was verified again after the swap.

Every post id above was re-read from the platforms' own list APIs after the fact, not copied from
intent: `creator.douyin.com/web/api/media/aweme/post/` (durations 215510 / 194518 / 191211 ms, covers
540×721, `mix_info.statis.current_episode` 2 / 3 / 4) and
`channels.weixin.qq.com/cgi-bin/mmfinderassistant-bin/post/post_list` (short titles 不会写代码也能做软件 /
会写诗的贪吃蛇 / 住进项目里的蛇; 视频号 desc lengths 84 / 190 / **127** — EP.03's original 162-char text
died with the deleted post, same loss as the 抖音 description). `platform_meta.json` still carries the
*superseded* 视频号 id `…xKKJLHlqaF6Hk8zT4DCa88MFzQdijfsZxivY0JT9UA` and the old 抖音 ids for EP.01/EP.02.

## caption punctuation fix — 2026-10-30 16:2x

The s7 narration says `不写 .gitignore`, but the shipped track showed `gitignore`: `PUNCT` split on a dot
when *either* side was a non-word character, and the dot here sits after a space. Collapsed the two
alternatives into one two-sided guard in all three builders:

```python
PUNCT = (r"(?:[，。！？、；：—\,!\?]+"
         r"|(?<![A-Za-z0-9_])\.+(?![A-Za-z0-9_])"   # dot: only when neither side is a word char
         r"|(?<![A-Za-z0-9])-+"                      # hyphen rule left untouched
         r"|-+(?![A-Za-z0-9]))")
```

Rebuild result: `llm101-ep03/compositions/captions.html` changed exactly one cue (`gitignore` →
`.gitignore` at 161.392 s, 127 cues otherwise identical, `sha256` before/after kept in
`.tmp/recut/ep03_captions_before.html`). `llm101-film` (153 cues) and `llm101-ep02` (125 cues) rebuilt
**byte-identical**, so their published videos still match their `captions.html` and needed no re-upload.

`npm run check` clean (83/83 contrast, 0 craft/audio errors) → `npm run render:4k` →
`renders/llm101-ep03_2026-10-30_16-21-34.mp4` (16,857,470 B) → `npm run deliver -- <master>` →
`…_1080p_delivery.mp4` (10,237,207 B). Frame at 161.55 s confirms the caption band reads `.gitignore`.

Re-uploaded on all three platforms (ids in the table above). Bilibili 更换视频 again reset the cover to
auto frames; the 封面制作 dialog saves the **4:3** canvas crop (1440×1080) as an intermediate, but the
cover that reaches the archive is the 16:9 upload — verified `pic` = 1920×1080, diff 1.76 vs art.

## B站合集顺序 — 2026-10-30

合集 9443639 was live with the reel at 序号 1, **EP.02 at 2 and EP.01 at 3** — the 更换视频 flow keeps the
season slot but re-appends the episode, so the two swaps left them transposed. Fixed in 合集管理 →
`编辑` → the `视频（4）` table: drag the `.sort-drag` handle of 序号 3 up one row, then `立即提交`.

Two drag attempts did nothing, and the cause was not the widget: the handles sat at y≈810/864/918 while the
viewport is 770 px tall, so every `mouse.down` landed outside the page. `scrollIntoView({block:'center'})`
on `.ep-table`, re-measure (412/466/520/574), then a stepped drag (1364,520) → (1364,452) reorders in one go
and `立即提交` returns to 合集管理.

Public check after the save (`/x/web-interface/view` → `ugc_season.sections[0].episodes`):
1 `BV1S1xc6QEmX` reel · 2 `BV1CoxY6YEhF` EP.01 · 3 `BV1YWxP6YECS` EP.02 · 4 `BV1ALxY6aExs` EP.03 — same
sequence 抖音 reports through `mix_info.statis.current_episode` (1/2/3/4) and 视频号 through its
VIBECODING collection.
