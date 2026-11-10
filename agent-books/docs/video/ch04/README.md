# 第 04 章视频制作包｜驭者·Agent Harness

> 账号：小电讲电路 · 系列：驭者·Agent Harness · 第 04 章  
> 书稿：`第一部分-基础篇/04-权限管线-Agent的护栏.md`（英：`en/Part-1-Foundations/04-The-Permission-Pipeline-Agent-Guardrails.md`）  
> 规则：**先过片，再发布**；本目录脚本可入库，大体积 mp3/mp4 默认不入库。

## 文件

| 文件 | 用途 |
|------|------|
| `long-outline.md` | B 站长讲分镜大纲（占位） |
| `short-script.md` | 抖音/小红书竖屏钩子+口播 |
| `voice.md` | 音色锁定（沿用云扬） |
| `gate-checklist.md` | 过片门禁 |
| `STATUS.md` | 发布/渲染状态 |

## 成片目标路径（本机）

- 长讲：`video/ch04/out/ch04-long-v1.mp4`（1920×1080，15–20 min）· **未开渲**
- 短片：`video/ch04/out/ch04-short-v1.mp4`（1080×1920，30–60 s）

## 流水线复用

- 工具链：`video/ch04/tools` → junction → `video/ch01/tools`
- 短片：镜像改写 `video/ch03/hf-remake/build_short.py` → ch04 版
- 钩子对仗：ch03「锤子 vs 双手」→ ch04「万能钥匙 vs 四道闸」

更新：2026-10-28 20:44 America/Adak
