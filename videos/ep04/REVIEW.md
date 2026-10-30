# EP.04 「把这条蛇，放到公网上」 review log

Timeline: 8 scenes, 187.472 s @ 1920×1080 / 30 fps. Voice `edge-tts zh-CN-XiaoxiaoNeural`
(rate +0%, same as EP.03). BGM `assets/bgm/track-long.wav` @ 0.16 with 0.8 s fade-in /
2 s fade-out. Built from the EP.03 scaffolding: same tools, same components, same palette.

Topic is fixed by EP.03's ending: 「下一期，把项目发布上线，让别人用手机就能打开你做的蛇」.

| scene | id | start | dur | content |
|---|---|---|---|---|
| s1 | hero1 | 0.000 | 19.324 | hook: localhost 只活在你自己的电脑里 |
| s2 | why | 19.324 | 23.980 | 回环地址不出网卡 → 三样东西 → 托管平台全包 |
| s3 | build | 43.304 | 25.684 | dev 带热更新，build 产出 dist，只发 dist |
| s4 | host | 68.988 | 24.484 | Cloudflare Pages / Vercel，两个问题，一条 https 链接 |
| s5 | phone | 93.472 | 22.396 | 真机四条：能玩 / 声音 / 布局 / 首屏；触屏要加按钮 |
| s6 | update | 115.868 | 22.468 | 提交即部署；改坏了用一条命令回滚 |
| s7 | pitfall | 138.336 | 25.732 | 三个坑：传 node_modules / 密钥进前端 / 只在桌面测 |
| s8 | hero2 | 164.068 | 23.404 | 四期小结 + 下一期预告（存档与排行榜，数据放哪） |

## audio and captions

Each scene's WAV is the edge-tts take of `assets/voice/<scene>.txt`; `tools/make_voice.py` writes
them, `tools/tts_words.py` re-synthesises each and proves the take against the shipped WAV
(±0.03 s) before caching `[[start, end, word], …]`. `tools/build_captions_v2.py` lays the shown
text on those word timings and asserts each scene's last cue lands within 0.6 s of its audio.

| scene | chars | wav dur | words | last word end |
|---|---|---|---|---|
| s1-hook | 91 | 18.624 | 52 | 18.062 |
| s2-why | 116 | 23.280 | 54 | 22.700 |
| s3-build | 130 | 24.984 | 56 | 24.413 |
| s4-host | 125 | 23.784 | 53 | 23.200 |
| s5-phone | 99 | 21.696 | 54 | 21.113 |
| s6-update | 104 | 21.768 | 53 | 21.175 |
| s7-pitfall | 116 | 25.032 | 57 | 24.450 |
| s8-next | 102 | 22.704 | 58 | 22.112 |

118 caption groups, first cue 0.225 s, last cue ends 186.365 s. Slot = wav + 0.70 s between
scenes; the pause budget is what keeps each scene's track from bleeding into the next one.

## checks

`npm run check` passes with 0 errors, 0 warnings: layout 0 issues across 9 samples, contrast
47/47 text checks pass WCAG AA, craft type floor clear, audio 0 errors.

Two craft defects were found and fixed while iterating (both would have shipped silently):

- `phone.html` address bar: `https://vibe-snake.pages.dev` at 26 px overflowed a 46 px box and
  wrapped mid-token; the domain now reads `vibe-snake.pages.dev` on one line at 28 px.
- `phone.html` TOUCH panel: at 40 px the 17-glyph line wrapped leaving 「钮」 alone; 36 px fits.
- `update.html` command bar: `#c9d1d9` / `#56d364` instead of the muted pair, so the fade-in does
  not dip under 3:1 against `#0d1117`.

## covers

`assets/covers/` is the Opus 5.5 snake family, cloned from the EP.03 sources
(`.tmp/covers/opus55/ep04-{3x4,4x3,16x9}`) and re-lettered: EP.04 badge, 打包 · 部署 · 链接发出去,
the big green 上线, a `deploy` card with ✓ 上传 / ✓ 分配域名 / ✓ 签发证书, plus the terminal
`npm run build → dist/ 24 files` and the live URL. 3:4 1080×1440, 4:3 1440×1080, 16:9 1920×1080.

## 发布记录 — 2026-10-30

| 平台 | ID | 时长 | 封面 | 备注 |
|---|---|---|---|---|
| B站 | `BV1gKxv67Ejf` (cid `43178594090`) | 188 s | `80690e07eb196883a5df7cd8c2633dfe6ed186e8.jpg` 1920×1080 | 分区 科技数码 (tid 231)，7 标签，desc 226，合集 9443639 第 5 集 |
| 抖音 | `7702405242045959465` | 187500 ms | 540×721 | 合集「不会写代码也能做软件｜VIBE 101」第 5 集 |
| 视频号 | `export/UzFfBgAAxISJSCYFPleGk8zT4DCaiwiStB84jXY-SwHcUbwFWQ` | 187.5 s | `coverUrl` 540×720，与 `cover3x4.jpg` 差 3.14 | 短标题「手机也能玩你的蛇」，desc 159，合集 VIBECODING 第 5 条 |

B站封面校验：把 `pic` 下载后与 `assets/covers/cover16x9.png` 逐像素比，整体差 1.58、
左 10% 条 2.06、右 10% 条 0.77 —— 均匀 JPEG 噪声，说明存档的是完整 16:9 原图，
不是 4:3 中心裁切再拉伸。

B站封面对话框有一个坑：点 `完成` 后会弹 `videoup-confirm-modal`
（检测到个人空间封面（16:9）未修改），而它的 `.sync-confirm-preview-img` 以 1440×1080
的原始尺寸铺在按钮上面，指针点击全被它吃掉。隐藏那张预览图，再点 `确认同步`（846,376）才能把
4:3 的画布同步到 16:9。

视频号封面校验：`post_list` 里该条的 `thumbUrl`（1080×607）对视频 0.5 s 帧的差是 12.2、
对我们的 4:3 封面的差是 200 —— 那是横版视频缩略图，不是资料卡；`coverUrl`（540×720，3:4）
与 `cover3x4.jpg` 的差是 3.14，所以个人主页卡片用的确实是我们的封面。
`shareCoverUrl`（720×405）仍是取帧，和 EP.03 一样：分享卡片编辑器打不开，已接受。
合集顺序用 `collection/get_collection_feed_list` 核对：reel → EP.01 → EP.02 → EP.03 → EP.04。

视频号卡住一次的根因：上传页标签在后台（`document.visibilityState === "hidden"`），
微前端没跑完初始化（页面一直显示「页面初始化中」），此时 `DOM.setFileInputFiles` 和点击都无效。
先 `Page.bringToFront` + `Emulation.setFocusEmulationEnabled`，等表单渲染出来再设文件，上传才动。
