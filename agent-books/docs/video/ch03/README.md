# 第 03 章视频制作包｜驭者·Agent Harness

> 账号：小电讲电路 · 系列：驭者·Agent Harness · 第 03 章  
> 书稿：`第一部分-基础篇/03-工具系统-Agent的双手.md`  
> 规则：**先过片，再发布**；本目录脚本可入库，大体积 mp3/mp4 默认不入库。

## 文件

| 文件 | 用途 |
|------|------|
| `long-outline.md` | B 站长讲分镜大纲 |
| `long-script.md` | 长讲口播底稿（沉稳男声） |
| `short-script.md` | 抖音/小红书竖屏钩子+口播 |
| `voice.md` | 音色锁定（沿用云扬） |
| `gate-checklist.md` | 过片门禁 |
| `STATUS-REPORT.md` | 启动状态 |

## 成片目标路径（本机）

- 长讲：`video/ch03/out/ch03-long-v1.mp4`（1920×1080，15–20 min）
- 短片：`video/ch03/out/ch03-short-v1.mp4`（1080×1920，30–60 s）

## 流水线复用

- 工具链：`video/ch03/tools` → junction → `video/ch01/tools`（sweety / HyperFrames / huashu / lemo-opuscar）
- 短片：镜像改写 `video/ch02/hf-remake/build_short.py` → ch03 版（非一键复用，需改口播与画面卡）
- 长讲：HyperFrames densify + edge-tts 分片，模式同 ch02
