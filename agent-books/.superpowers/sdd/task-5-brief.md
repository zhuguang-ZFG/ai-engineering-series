# 驭者·Agent Harness 第 01 章样片 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 产出第 01 章样片：1 条 B 站横屏长讲（15–20 分钟）+ 1 条抖音/小红书竖屏短片（30–60 秒），供用户过片后再批量 02–04。

**Architecture:** 书稿 Markdown 为唯一内容源；先写出可审的脚本与分镜，再分别做长讲动画轨与短片 HTML/Canvas 钩子，配沉稳男声与字幕后合成。发布元数据与合集文案单独成稿，样片过审前不投稿。

**Tech Stack:** 书稿 `第一部分-基础篇/01-智能体编程的新范式.md`；edge-tts 或等价 TTS（沉稳中文男声）；Manim/HTML+Canvas/录屏合成（与现有 BMS 视频流水线可复用处优先）；FFmpeg；B 站/抖音/小红书创作者后台。


## Global Constraints

- 系列名：驭者·Agent Harness；账号：小电讲电路
- B 站长讲：15–20 分钟，1920×1080；短片：30–60 秒，1080×1920
- 短片结构：前 3–5 秒 Opus 风格动效钩子 + 口播讲清一个机制 + 片尾「完整版在 B 站」
- 口播：沉稳男声（禁用晓晓·轻柔）
- 定位：基于开源书稿；片头/片尾/简介标明出处；系列置顶目录
- 样片先行：本计划只做第 01 章；小红书人感少发、不批量
- 技术动画须带书稿中的真实模块名与数字（如 1,884 个 TS 文件 / 512,664 行），不做空泛示意图
- 规格文档：`docs/superpowers/specs/2026-10-27-yuzhe-video-series-design.md`

### File map

| Path | Responsibility |
|------|----------------|
| `docs/video/ch01/long-outline.md` | 长讲大纲、章节时间点草稿 |
| `docs/video/ch01/long-script.md` | 长讲口播全文 |
| `docs/video/ch01/short-script.md` | 短片口播 + 钩子分镜 |
| `docs/video/ch01/publish-meta.md` | 三平台标题/简介/标签/出处文案 |
| `video/ch01/assets/` | 动画源、封面、钩子 HTML |
| `video/ch01/out/ch01-long.mp4` | 长讲成片 |
| `video/ch01/out/ch01-short.mp4` | 短片成片 |
| `video/ch01/out/ch01-long.srt` | 长讲字幕 |
| `video/ch01/out/ch01-cover.png` | B 站封面 |

---

### Task 1: 第 01 章长讲大纲与口播脚本

**Files:**
- Create: `docs/video/ch01/long-outline.md`
- Create: `docs/video/ch01/long-script.md`
- Source: `第一部分-基础篇/01-智能体编程的新范式.md`

**Interfaces:**
- Consumes: 书稿 §1.1–1.3、实战练习、关键要点；规格 Global Constraints
- Produces: `long-outline.md`（含预估分钟与时间点）；`long-script.md`（口播全文，标注 `[ANIM:…]` / `[CODE:…]` 插入点）

- [ ] **Step 1: 建目录**

```bash
mkdir -p docs/video/ch01 video/ch01/assets video/ch01/out
```

- [ ] **Step 2: 写 `long-outline.md`**

必须覆盖这些块（预估总时长 15–20 分钟）：

1. 开场钩子（约 45s）：Chatbot 手工胶水 vs Agent 编排
2. §1.1 范式转移（约 4min）：推理引擎、Tool Use、为何需要 Harness
3. §1.2 全景架构（约 5min）：时间线、1884 文件 / 512664 行、技术栈、核心源码职责
4. §1.3 五大原则（约 6min）：每条原则 1 个动画锚点
5. 实战练习速览（约 2min）：install → `/doctor` → 一次工具调用
6. 总结 + 片尾出处（约 1min）

- [ ] **Step 3: 写 `long-script.md` 口播全文**

要求：口语化中文；专有名词首次给出中英；每个 `[ANIM:…]` 对应 outline 中的一帧；片尾固定句包含「基于开源书稿」与系列名「驭者·Agent Harness」。

- [ ] **Step 4: 自检**

Run: 统计 `long-script.md` 汉字数；按约 220 字/分钟估算，应落在 3300–4400 字（对应 15–20 分钟）。  
Expected: 字数在区间内；outline 六块齐全；无「晓晓」或女声提示。

- [ ] **Step 5: Commit**

```bash
git add docs/video/ch01/long-outline.md docs/video/ch01/long-script.md
git commit -m "docs(video): add ch01 long-form outline and narration script"
```

---

### Task 2: 短片钩子分镜与口播脚本

**Files:**
- Create: `docs/video/ch01/short-script.md`

**Interfaces:**
- Consumes: Task 1 中「Harness vs 简单封装」核心句；规格短片结构
- Produces: `short-script.md`（钩子分镜秒表 + 口播 ≤ 120 字主体 + 片尾句）

- [ ] **Step 1: 写钩子分镜（0–5s）**

分镜须可落地为单一 HTML/Canvas 文件，建议镜头：

- 0.0–1.5s：对话框气泡堆积，人手复制粘贴图标循环
- 1.5–3.5s：气泡收束成中枢节点，连出 Tool / FS / Git / Shell 四路
- 3.5–5.0s：标题字「Agent Harness · 驭者」落版

- [ ] **Step 2: 写口播（约 25–45s 可念完）**

只讲清一个机制：为什么需要 Agent Harness 而不是简单 API 封装。结尾句：`完整版在 B 站合集「驭者·Agent Harness」。`

- [ ] **Step 3: 自检时长**

按 4 字/秒粗算口播时长 + 5s 钩子，总长必须 ≤ 60s 且 ≥ 30s。

- [ ] **Step 4: Commit**

```bash
git add docs/video/ch01/short-script.md
git commit -m "docs(video): add ch01 short hook storyboard and VO"
```

---

### Task 3: 选定沉稳男声并出试音

**Files:**
- Create: `video/ch01/assets/voice-sample-long.mp3`
- Create: `video/ch01/assets/voice-sample-short.mp3`
- Create: `docs/video/ch01/voice.md`

**Interfaces:**
- Consumes: `long-script.md` 前 80 字；`short-script.md` 全文
- Produces: `voice.md` 记录引擎、voice id、rate/pitch；两段试音文件

- [ ] **Step 1: 列出候选男声（edge-tts 或本机已有）**

至少试 2 个中文男声（例如 `zh-CN-YunxiNeural`、`zh-CN-YunjianNeural`），rate/pitch 微调到「沉稳」而非播音腔。

- [ ] **Step 2: 渲染试音并写入 `voice.md`**

`voice.md` 必须含：最终选用的 voice id、rate、pitch、一条否决理由（为什么不用另一个）。

- [ ] **Step 3: 用户可听试音**

把两个 mp3 路径交给用户确认；未确认前不批量合成全片配音。

- [ ] **Step 4: Commit 文案（音频若太大可 gitignore，但 `voice.md` 必提交）**

```bash
git add docs/video/ch01/voice.md
git commit -m "docs(video): lock ch01 male narration voice settings"
```

---

### Task 4: 长讲动画资产与合成

**Files:**
- Create: `video/ch01/assets/anim-*.mp4` 或等价序列帧
- Create: `video/ch01/out/ch01-long.mp4`
- Create: `video/ch01/out/ch01-long.srt`
- Create: `video/ch01/out/ch01-cover.png`

**Interfaces:**
- Consumes: `long-script.md`、`voice.md`、书稿中的架构数字与五大原则名
- Produces: 可审长讲成片 + SRT + 封面

- [ ] **Step 1: 按 `[ANIM:…]` 清单做动画**

最低动画集：

1. Chatbot 人工胶水序列 → Agent 工具编排
2. Claude Code 规模数字卡（1884 files / 512664 LOC）
3. 五大原则图标条依次点亮
4. `/doctor` → 工具调用一次完整路径

- [ ] **Step 2: 合成男声全片配音**

用 Task 3 锁定的 voice 设置渲染 `long-script.md` 全稿。

- [ ] **Step 3: 时间线合成 `ch01-long.mp4`**

画幅 1920×1080；总时长必须在 15:00–20:00；片头/片尾含系列名与「基于开源书稿」。

- [ ] **Step 4: 导出 SRT 与封面**

封面文案建议：`智能体编程的新范式｜驭者·Agent Harness 01`；避免假乱码。

- [ ] **Step 5: 硬性验收**

```bash
ffprobe -v error -show_entries format=duration -of default=nw=1:nk=1 video/ch01/out/ch01-long.mp4
```

Expected: duration 在 900–1200 秒；存在非空 `ch01-long.srt` 与 `ch01-cover.png`。

- [ ] **Step 6: Commit 元数据与可追踪清单（大文件按仓库惯例处理）**

```bash
git add docs/video/ch01/
git commit -m "feat(video): assemble ch01 long lecture pilot assets"
```

---


### Task 5: 短片动效钩子与竖屏合成

**Files:**
- Create: `video/ch01/assets/hook.html`
- Create: `video/ch01/out/ch01-short.mp4`

**Interfaces:**
- Consumes: `short-script.md`、`voice.md`
- Produces: 竖屏短片成片 30–60s

- [ ] **Step 1: 实现 `hook.html`**

单文件可播放；按 short-script 0–5s 分镜；深色底；无外网依赖（或构建时打进包）。

- [ ] **Step 2: 录制钩子为无声视频轨**

分辨率 1080×1920 或先 1080p 再加左右安全区裁切为竖屏。

- [ ] **Step 3: 拼接口播段与片尾导流字卡**

总时长强制 clamp 到 [30, 60] 秒。

- [ ] **Step 4: 验收**

```bash
ffprobe -v error -show_entries format=duration -of default=nw=1:nk=1 video/ch01/out/ch01-short.mp4
```

Expected: 30–60 秒；画面含钩子与「完整版在 B 站」信息。

- [ ] **Step 5: Commit**

```bash
git add video/ch01/assets/hook.html docs/video/ch01/
git commit -m "feat(video): assemble ch01 vertical short pilot"
```

---


## PIPELINE OVERRIDE
Short: lemo-opuscar primary (Opus style hooks); explainroo fallback.
Voice: zh-CN-YunyangNeural -10% -5Hz
Script: docs/video/ch01/short-script.md
Output: video/ch01/out/ch01-short.mp4 1080x1920, 30-60s
Clone lemomo-ai/lemo-opuscar under video/ch01/tools if needed.
