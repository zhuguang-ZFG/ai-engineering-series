# ch02 启动状态报告（不过片不发布）

## 合集
- docs/video/ch01/bili-meta-ch01.json **无** season_id / 合集 ID
- 本机 biliup 不在 PATH，本任务**未创建、未核实** B站「驭者·Agent Harness」合集
- 建议过片后再建合集并把 ch01 BV1rGx76EEpJ + ch02 一并挂入

## 文案（docs/video/ch02/）
| 文件 | 标题/要点 |
|------|-----------|
| long-outline.md | 对话循环·Agent的心跳 · ~18:30 · 钩子/循环/AsyncGenerator/马车/猜一猜/收束 |
| long-script.md | 全本口播 ~3397 字 · Yunyang -10%/-5Hz |
| short-script.md | 钩子「Promise≠AsyncGenerator」· 30s 竖屏 |
| voice.md / gate-checklist.md / README.md | 声线与过片门禁 |

## 工程脚手架（video/ch02/）
- 镜像 ch01：out/ assets/ hf-remake/short/ .hf-tmpdir/ tools→ch01
- build_short.py（已跑通）· synth_long_vo.py（后台跑）
- SFX + book-chariot-paper 已复用

## 成片
- **短片已渲**：video/ch02/out/ch02-short-v1.mp4（~30.9s / 1080×1920 / ~8.1MB）
- spot：out/short-spot/t01|t06|t14|t22|t28.jpg
- 长讲：**未开 densify 渲**；口播分片 edge-tts 后台合成中（assets/vo/c*.mp3）

## 未做 / Blockers
- 未发布任何平台（按任务门禁）
- 合集未建
- 长讲 densify 待口播齐 + 用户短片过片后再开
- HyperFrames TMP 已指到项目 .hf-tmpdir

## Long VO（2026-10-28）
- 完成：31/31 分片 video/ch02/assets/vo/c000.mp3–c030.mp3 + 配套 .txt
- 更正（2026-11-01）：那 31 个 `.srt` 全是 0 字节。脚本按 `WordBoundary` 收词级时间，而 edge-tts 7.x 的 `Communicate` 默认只回 `SentenceBoundary`。脚本已补 `boundary="WordBoundary"`，但这三章的音频是已发布片的配音，重跑会换音频，所以字幕留空，真要烧字幕时整章重合成。细节见 `docs/video/ch05/STATUS.md` 的字幕一节
- 声线：zh-CN-YunyangNeural rate=-10% pitch=-5Hz
- 总时长约 **10.5 min**（628s），字数 3414
- 清单：assets/vo/vo-manifest.json · chunks.json
- 合集：已存在 season_id **9436416**（含 BV1rGx76EEpJ）；本任务不新建
- 未开 HyperFrames 长讲 densify（等短片过片）
