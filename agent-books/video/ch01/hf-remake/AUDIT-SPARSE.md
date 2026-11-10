# AUDIT-SPARSE — ch01-long.mp4 画面稀疏诊断

日期：2026-10-28（America/Adak）  
成片：`video/ch01/out/ch01-long.mp4`（~19:08 / 157MB / 烧录中文字幕）  
抽帧：`video/ch01/hf-remake/audit-frames/`（t0003…t1120，约 30s–60s 间隔）

## 量化（来自 `build_remake.py` BLOCKS）

| 指标 | 当前值 | 问题 |
|------|--------|------|
| 总时长 | 1148.4s | — |
| HTML 块 | 6 | 块内长静帧 |
| Beat 数 | **30** | 全片平均 **38.3s/beat**，最长 **80s** 同屏文字 |
| Huashu 镜头 | **13** | 合计仅 **93s**，覆盖率 **8.1%** |
| 单镜 huashu | ~7s | 符合 ≤8s，但插入过稀 |

分块：

- b01_hook 43.9s · 4 beats · 1 huashu · avg 11.0s
- b02_paradigm 221.4s · 5 beats · 3 huashu · avg **44.3s**
- b03_arch 303.3s · 6 beats · 2 huashu · avg **50.6s**
- b04_principles 341.8s · 6 beats · 5 huashu · avg **57.0s**
- b05_practice 146.4s · 4 beats · 1 huashu · avg 36.6s
- b06_outro 91.4s · 5 beats · 1 huashu · avg 18.3s

## Top 5 稀疏缺口（用户观感对应）

1. **几乎没有「马车 / 驭者」书稿隐喻画面**  
   前言《考工记》舆·辕·辐·軎辖·轼·御 ↔ Harness 映射、以及「模型是马 / Harness 是缰绳鞍具」只在口播出现；画面全是工程卡片，书的意思没画出来。

2. **长静帧标题卡（PPT 感）**  
   Beat 以 fade-in `h1/h2` 为主，随后数十秒无新事件；违反 cookbook「一镜一事 / 禁止 12s 循环垫片式切页」。

3. **Huashu 覆盖仅 8%**  
   13 段白板插入之间是大片空工程背景 + 静态字；视觉节奏不像吸粉短视频/长讲钩子。

4. **缺冲击运镜与转场**  
   无 punch-in、无零件飞入映射、无 callout/sticker 按关键词弹出；开场不够「砸」。

5. **无点状音效冲击**  
   只有云扬口播，关键揭示（Harness 定义、数字 1884、原则序号、隐喻亮相）没有 whoosh/impact/UI blip；听觉偏「安静讲课墙纸」。

## 加厚方向（已锁定，禁止循环 ambient beds）

- 更多/更短镜头：目标 avg shot **≤6–8s** 有事件；GSAP 动能字 + 图解生长 + 隐喻序列。
- **硬性**：马车/驭者隐喻必须成片运动（驭者揽辔、骏马、舆辕辐映射）。
- **硬性**：关键 beat 配 SFX（whoosh / impact / rein-snap / gallop-sting / UI blip），不盖过口播；禁循环垫乐。
- 字幕：继续烧录中文；口播沿用 `full.mp3`。
- 先交付 `out/ch01-long-dense-proof.mp4`（45–90s），再全片 `out/ch01-long-v3.mp4`。