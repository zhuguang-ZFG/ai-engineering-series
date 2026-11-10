# 驭者·Agent Harness — 视频矩阵 Cookbook（给重做 Agent）

> 日期：2026-10-28（America/Adak）  
> 目标：第 01 章长讲样片「大片感 + 烧录字幕」重做；短片钩子另线。  
> 研究源：本机克隆 `/workspace/yuzhe-sdd/matrix-research/`（或用户机 `video/ch01/tools/`）。  
> 已锁定口播：`zh-CN-YunyangNeural`，edge-tts `rate=-10%` `pitch=-5Hz`。  
> 现有资产可复用：`video/ch01/assets/vo/`（云扬分段）、`video/ch01/scripts/`（长讲/短片稿）。

---

## 0. 总原则（所有工具共用）

1. **旁白先行**：先有定稿口播 + 词级时间戳，再定镜头时长。禁止估秒循环垫片。
2. **一镜一事**：禁止「12 秒场景循环 + 切页 PPT」。每镜必须有独立画面事件（新物出现 / 路径生长 / 代码走读 / 白板书写）。
3. **字幕硬门槛**：成片必须 **烧录** 中文字幕（画面内可读），并附独立 `.srt`。禁止只发裸 MP4。
4. **确定性渲染**：禁未种子 `Math.random()` / `Date.now()`；同一输入同帧。
5. **Windows 现实**：长片主渲优先 **WSL2 Ubuntu** 或本 bot 的 Linux box；纯 Windows 只做 TTS、剪映精修、最终 QA。
6. **禁止空泛示意图**：架构图 / 对话循环 / 工具调用路径必须来自第 01 章书稿真实模块名。

---

## 1. sweety-handdraw-video

| 项 | 内容 |
|---|---|
| Repo | https://github.com/threerocks/sweety-handdraw-video |
| 定位 | 长文 → **边画边讲** 有声讲解片（手绘描线 + 笔顺手写 + 声画对齐） |
| 驭者任务 | **长讲主视觉候选 A**（知识科普/机制讲解）；不适合硬核代码走读全片独占 |

### Install

```bash
npx skills add threerocks/sweety-handdraw-video --skill sweety-handdraw-video --agent claude-code --global --copy --yes
# 或
git clone https://github.com/threerocks/sweety-handdraw-video.git
bash <skill>/scripts/setup.sh
python <skill>/scripts/handdraw_video.py doctor JOB
```

依赖：Python 3.9+、FFmpeg、Pillow/NumPy/SciPy、中文字体；生图能力（宿主）；配音（VoxCPM2 仅 Apple Silicon / VoiceStudio / 现成旁白 / 自备云 TTS）。

### Agent 如何写场景

1. 写 `design.json`（因果、受众、`presentation.mode`：知识讲解优先 `accumulating_board` / `focus_diagram` / `step_sequence`）。
2. 开场读「黄金 5 秒」写入 `opening_hook`。
3. 旁白分段 ≤100 字 → 生成/导入音频 → `alignment.json`（**驭者：直接导入已锁定的云扬 VO + 对齐**）。
4. `storyboard.json` → `storyboard_lint.py JOB --budget`。
5. 生图前美术指导 → `drawing-plan.json` → 出图门禁 → `job.json`（运镜/转场/overlays）。

### 渲染 MP4

```bash
python scripts/handdraw_video.py build JOB
python scripts/handdraw_video.py render JOB
python scripts/handdraw_video.py verify JOB
python scripts/handdraw_video.py finalize JOB
```

默认竖屏 1280×1920；横屏 B 站长讲需在 options 显式改比例（如 16:9）。

### 字幕

- 管线内置字幕层，按 `alignment.json` 同步；**字幕唯一性是硬门槛**（画面烘焙与外挂轨不得叠双字幕）。
- 交付检查：MP4 无额外字幕轨叠加、看解码画面长句/换句。

### Windows

**partial / 官方 no**：文档写「macOS 与 Linux；Windows 暂不承诺」。VoxCPM2 不适配 Windows/CUDA。  
**workaround**：WSL2 跑完整 skill；或 **旁白用云扬 edge-tts（Windows 已通）+ 对齐文件导入**，只在 WSL/Linux 做 draw/render。

### 驭者归属

- Long：机制隐喻段（Harness=驭手）、概念引入、小结口诀 — 用手绘板书感。  
- Short：可选 15–30s 钩子，但优先 lemo-opuscar。

---

## 2. HyperFrames（HeyGen）

| 项 | 内容 |
|---|---|
| Repo | https://github.com/heygen-com/hyperframes |
| 定位 | **HTML/CSS/GSAP → 确定性 MP4**；Agent 友好；烧录字幕生态最全 |
| 驭者任务 | **长讲底层渲染床 + 烧录字幕 + 多 beat HTML 构图**（主轴推荐） |

### Install

```bash
npx hyperframes skills update          # 装 core skills
npx hyperframes init ch01-long --non-interactive
# 可选：全套
npx hyperframes skills
# 或
npx skills add heygen-com/hyperframes --all
```

依赖：Node、FFmpeg、headless Chrome；`bun` 仅开发 monorepo 需要。

### Agent 如何写场景（7 步流水线）

| # | 产物 | 说明 |
|---|---|---|
| 1 Capture | `capture/` | 可选：截品牌/书稿图 |
| 2 Design | `DESIGN.md` | 驭者深色工程风：色板、字号、系列名条 |
| 3 Script | `SCRIPT.md` | 用已定稿口播，不重写 |
| 4 Storyboard | `STORYBOARD.md` | 每 beat：mood / assets / animations / transitions |
| 5 VO+Timing | `narration.*` + `transcript.json` | **导入云扬音频** → `npx hyperframes transcribe` |
| 6 Build | `compositions/*.html` | **一 beat 一 HTML**；GSAP root on `window.__timelines` |
| 7 Validate | lint/check + 静帧 | `npx hyperframes lint` && `npx hyperframes check` |

创作路由：长讲讲解用 `/hyperframes` + faceless-explainer 思路；字幕用 captions 组件 / overlay doctrine。

场景合约要点：

- HTML `class="clip"` + `data-*` 时长
- 动画 seekable（GSAP paused root）
- 禁未种子随机；禁渲染时网络请求

### 渲染 MP4

```bash
npx hyperframes preview
npx hyperframes render
# 常用：从项目目录
npx hyperframes lint && npx hyperframes check && npx hyperframes render
```

Registry 可加组件：

```bash
npx hyperframes add captions
npx hyperframes catalog --tag captions
```

### 字幕（烧录 / 同步）— 强支持

```bash
# 词级时间戳
npx hyperframes transcribe narration.wav --language zh
npx hyperframes transcribe transcript.json --to srt

# 已有成片补字幕（embedded / overlay）
npx hyperframes init caps --non-interactive --video video.mp4
# 读 captions-overlay doctrine：drop / rail / embed
# rail = 默认下三分之一 verbatim；embed = 稀缺高潮大字
```

规则：字幕是 **overlay**，不要为字幕腾死区把构图上移；关键小字避开底部中央 ~80px。

### Windows

**yes（基本）**：CLI/渲染跨平台；README 含 Windows Git LFS 指引。注意：whisper/parakeet 模型下载、Chrome headless 路径。大陆网络可能需镜像。  
**推荐**：Windows 做 TTS+转录；重渲也可本机，但长片更稳在 WSL。

### 驭者归属

- Long：**主渲染器**。每章 8–15 个 beat HTML（开场钩子、架构、对话循环、工具路径、代码走读、口诀、片尾）。  
- Short：可渲竖屏，但短片钩子优先 lemo。

---

## 3. huashu-art-motion

| 项 | 内容 |
|---|---|
| Repo | https://github.com/alchaincyf/huashu-art-motion |
| 定位 | 代码艺术动画 + **9 种解说语法**（白板/Vox/3b1b/Kurzgesagt…）参数化片段 |
| 驭者任务 | 长讲 **机制/白板/图表镜头**；禁止整片蓝紫 AI slop |

### Install

```bash
npx skills add alchaincyf/huashu-art-motion
# 引擎依赖
uv run --with playwright playwright install chromium
```

依赖：uv、ffmpeg、Playwright Chromium。

### Agent 如何写场景

**轨道档（推荐给重做 agent）**：

1. 写 `<项目>/镜头表.md`（画风锁死、色板、每镜 2–6s、开头 3s 具体小场景非标题）。
2. `uv run scripts/storyboard_lint.py 镜头表.md --script 文稿.txt`
3. `cp -R scripts/engine <项目>/代码工程`
4. 参数化片段：从 `examples/<语法>.json` 抄结构，改内容：

```bash
uv run --with playwright python 代码工程/render.py --spec 镜01.json --out 镜01.mp4
# 单片段 ≤8 秒，超了拆镜
```

驭者优先语法：

- `whiteboard` / 白板：对话循环、工具调用路径  
- `3b1b`：抽象机制  
- `vox`：调查桌 + 真实截图/代码素材满幅  
- `kinetic type`：开场钩子大字（慎用，≤1–2 镜）

### 渲染 MP4

```bash
# 单镜
uv run --with playwright python $E/render.py --spec 镜NN.json --out 镜NN.mp4 --audit
# 整片 scenes
uv run --with playwright python $E/render.py --out 成片.mp4 --audio 口播.wav
# 拼接多镜
ffmpeg -f concat -safe 0 -i 镜头列表.txt -c:v libx264 -crf 16 -pix_fmt yuv420p -an 成片.mp4
ffmpeg -i 成片.mp4 -i 口播.wav -map 0:v -map 1:a -c:v copy -c:a aac -shortest 成片_口播.mp4
# 交付门禁
uv run scripts/deliver.py 成片_口播.mp4 --root <项目> --qa <项目>/qa/... --out output/
```

`finish: soft|film|punch` 可加暗角/颗粒成片感。

### 字幕

- **不自带口播烧录字幕管线**；需外部：HyperFrames captions / ffmpeg `subtitles=` / Remotion captions。  
- 有 `subzone_gate.py` 检查图形是否侵入字幕区（浅底）。

### Windows

**partial**：Playwright+uv 可在 Windows 跑；中文路径/编码需小心。官方示例偏 Unix shell。  
**workaround**：WSL 跑 render/deliver；或本机 Python 但 concat 用 PowerShell 等价脚本。

### 驭者归属

- Long：白板推导段、架构生长段、数字/对比图表。  
- Short：3–5s 艺术钩子（选 1 种风格卡，勿拼贴）。

---

## 4. lemo-opuscar

| 项 | 内容 |
|---|---|
| Repo | https://github.com/lemomo-ai/lemo-opuscar |
| 定位 | **59+ 代码成片风格库**；短片电影感；时间线驱动画面/声/乐/字幕 |
| 驭者任务 | **抖音/小红书短片主轴**；长讲片头 5–8s 风格钩子 |

### Install

```bash
claude plugin marketplace add lemomo-ai/lemo-opuscar
claude plugin install lemo-opuscar@lemolab
# 或
git clone https://github.com/lemomo-ai/lemo-opuscar.git
# 依赖分层
sh plugin/skills/lemo-opuscar/scripts/setup.sh deps
sh plugin/skills/lemo-opuscar/scripts/setup.sh deps voice   # edge-tts 中文 + whisper
```

依赖：Node 20+、ffmpeg、Python 3.11+/uv；3D 风格要 GPU。

### Agent 如何写场景

读三件套：`DIRECTOR.md` + `TECHNIQUE.md` + `styles/<style>/STYLE.md`。

页面合约：

```js
window.DUR = 54.2;
window.render = (t) => { /* deterministic */ };
window.READY = true;
window.EV = [{t, type, ...}];
window.TEXTS = (t) => [{id, text, x0, y0, x1, y1}];
```

单一 `timeline` 驱动画面/声/字幕。驭者短片建议风格方向：工程蓝图 / 暗色终端 / 墨水信息图（避免无来源的花哨 3D）。

### 渲染 MP4

```bash
export LIB=~/lemo-opuscar   # skill 模式
node $LIB/core/render/still.mjs "$HERE" 1.5 12 --range 0:50:2
node $LIB/core/render/video.mjs "$HERE" --fps 24 --workers 3 --out "$HERE/out/video.mp4"
$LIB/.venv/bin/python "$HERE/mix.py"
sh $LIB/core/render/mux.sh "$HERE/out/video.mp4" "$HERE/out/mix.wav" "$HERE/film.mp4" 24
```

中文配音：`core/tts/tts_zh.py`（edge-tts，需网络）— 可改为直接喂云扬已渲 WAV。

### 字幕

- `core/render/srt.py cues.json out.srt`
- **烧录**：字幕设计写在页面风格内（caption 是画面一部分）+ mux  
- 词级时间：`asr_check.py` / faster-whisper

### Windows

**partial → 用 WSL**：官方「Windows use WSL」。  
Native Win 不作为主路径。

### 驭者归属

- Short：**主工具**（30–60s，前 3–5s 钩子 + 口播机制一句）。  
- Long：仅片头 sting / 转场包装，不扛 15–20 分钟。

---

## 5. Remotion official skills

| 项 | 内容 |
|---|---|
| Docs | https://www.remotion.dev/docs/ai/skills |
| Skills repo | https://github.com/remotion-dev/skills |
| 定位 | React 时间线视频；字幕组件成熟；生态基石 |
| 驭者任务 | 长讲 **代码高亮走读 / 复杂 UI 动效**；与 video-shotcraft 共用 |

### Install

```bash
npx skills add remotion-dev/skills
# 或新项目
bun create video
npx remotion add @remotion/captions
npx remotion add @remotion/install-whisper-cpp   # 可选转录
```

### Agent 如何写场景

- `/remotion-best-practices` 总览  
- Composition + `<Sequence>` + `useCurrentFrame()`  
- 媒体：`staticFile()`；动画用 spring/interpolate  
- 确定性：固定 fps、禁随机

### 渲染 MP4

```bash
npx remotion studio
npx remotion render <CompositionId> out/ch01.mp4
npx remotion still <CompositionId> out/frame.png
# Linux 低核
npx remotion render <id> out.mp4 --concurrency=1
```

### 字幕

```ts
import type { Caption } from "@remotion/captions";
import { createTikTokStyleCaptions, parseSrt } from "@remotion/captions";
// Whisper → toCaptions() → captions.json → Sequence 渲染 = 烧录
```

从已有 SRT：`parseSrt({ input })`。词级高亮用 `createTikTokStyleCaptions`。

### Windows

**yes**：Remotion 官方支持 Windows。注意 Chrome 下载与并发。公司商用需核对 Remotion 许可。

### 驭者归属

- Long：代码走读、终端模拟、UI 状态机演示。  
- Short：单镜头动效（配合 shotcraft 卡）。

---

## 6. explainroo

| 项 | 内容 |
|---|---|
| Repo | https://github.com/vincentsch/explainroo |
| 定位 | **极速** 口播讲解：`script.md` + `scenes.js` → Kokoro/Whisper → MP4 |
| 驭者任务 | 短片备选；长讲「赶工期」降级方案（电影感弱于 HF+huashu） |

### Install

```bash
git clone https://github.com/vincentsch/explainroo.git "$HOME/.explainroo"
cd "$HOME/.explainroo" && npm install
node bin/explainroo.js doctor --fetch
# 中文
python -m pip install "misaki[zh]"
```

依赖：Node ≥20.11、ffmpeg、Chrome/Chromium。Windows 明确支持。

### Agent 如何写场景

```bash
explainroo init videos/ch01 --theme midnight --title "Agent Harness" --size youtube
# 写 script.md（旁白先行）与 scenes.js（at: '词' 或 '#marker'）
explainroo voice videos/ch01
explainroo check videos/ch01
explainroo still videos/ch01
explainroo sheet videos/ch01
```

主题：`paper|clean|chalk|blueprint|midnight|editorial`。驭者工程向用 `midnight` / `blueprint`。

### 渲染 MP4

```bash
explainroo render videos/ch01 --draft
explainroo render videos/ch01
explainroo verify videos/ch01
# → videos/ch01/out/video.mp4 + .srt + .vtt + cover
```

竖屏：`explainroo render ... --size tiktok`（自动开 word-by-word captions）。

### 字幕

- 默认竖/方屏 `captions: true`（烧录卡拉 OK）  
- 始终导出 `.srt` / `.vtt`  
- `{shown|spoken}` 控制字幕显示 vs 发音  
- 勿在画面再画一遍与字幕相同的整句

可用自备录音替代 Kokoro；**驭者应注入云扬音频**（若 CLI 支持 recording 路径则优先）。

### Windows

**yes**（CI 含 Windows）。中文用 `python` 非 `python3`；设 `EXPLAINROO_PYTHON` 如有 venv。

### 驭者归属

- Short：快速验证选题。  
- Long：仅当 HF/Remotion 阻塞时的备用整片引擎。

---

## 7. video-shotcraft

| 项 | 内容 |
|---|---|
| Repo | https://github.com/Vincentwei1021/video-shotcraft |
| 定位 | **152 级镜头配方卡** + Remotion 模板 + 节奏/音效 + Motion Workbench |
| 驭者任务 | 长讲/短片的 **单镜电影感运镜**；产品感开场；不做全书手绘 |

### Install

```bash
npx skills add Vincentwei1021/video-shotcraft
# 或 clone 后读 SKILL.md；渲染走 Remotion
```

依赖：Node/npm、ffmpeg、uv（仅 BGM 卡点）、puppeteer（截页）。

### Agent 如何写场景

1. 选模式：模板 / 自主自由创作 / 共同创作。  
2. 扫 `references/shots/` 或 Gallery 选卡（一镜一动效）。  
3. **必须读卡内「参考实现」TSX**，禁止凭卡名重写。  
4. 真实页面用截图纹理；抽象开场可手搓 UI。  
5. 审美：`aesthetic-rules.md`；卡点：`music-beat-sync.md`。

### 渲染 MP4

```bash
npx remotion render <comp> out/film.mp4
npx remotion still <comp> out/check.png
node workbench/scripts/open.mjs <成片工程目录>   # 帧级改字幕/颜色后导出
```

### 字幕

- Remotion captions 组件 + workbench 字幕轨  
- 可选导出剪映草稿（Mac 实测，Windows 未验证）

### Windows

**partial**：Remotion 可跑；剪映导出未验证；截页 puppeteer 需本机 Chrome。

### 驭者归属

- Long：开场英雄镜、模块飞入、spotlight 卡片、结尾 logo 收束（每类手法全片只用一次主角）。  
- Short：整支可按 Ink Press 类节奏做 30–45s（需真实 UI 素材时）。

---

## 8. onetake

| 项 | 内容 |
|---|---|
| Repo | https://github.com/feitangyuan/onetake |
| 定位 | **一镜到底** 产品动效；carry 连续性可测；非 Remotion/HF |
| 驭者任务 | 短片/片头「不 PPT」；长讲不适用 |

许可：PolyForm Noncommercial（商用需 Pro）。

### Install

```bash
git clone https://github.com/feitangyuan/onetake.git
# 复制 skill 到 agent skills 目录；读 SKILL.md
python3 scripts/look.py sheet
```

依赖：Python3、Chrome/Playwright、ffmpeg。

### Agent 如何写场景

硬顺序：拆参考 → 三个概念给用户挑 → beat sheet（rhythm+carry）→ 实拍/重建 UI → 单文件 `comp.html` + `window.__seek(t)` → 渲 → sfx → `verify_promo.py`。

```bash
cp templates/comp.html lib/motion.js cases/yuzhe-hook/
python3 scripts/probe.py cases/yuzhe-hook/comp.html
python3 scripts/stills.py comp.html --times 0.7,2.4,3.8 --out stills.png
```

### 渲染 MP4

```bash
python3 scripts/render.py comp.html --out draft.mp4 --sfx sfx.wav          # 1080p30
python3 scripts/render.py comp.html --out film.mp4 --final --sfx sfx.wav   # 4K60
python3 scripts/verify_promo.py draft.mp4 --comp comp.html
```

旁白/字幕：`scripts/vo_tools.py`（词级时间、多语言 `?lang=`）。

### 字幕

- VO tools 生成字幕；烧录进 composition 文本层  
- 适合短片，不适合 15–20 分钟口播密度

### Windows

**partial**：Python+Playwright 可试；文档与案例偏 macOS。建议 WSL。

### 驭者归属

- Short：15–30s 发布感钩子（Harness 隐喻一镜 carry）。  
- Long：不要整片 onetake。

---

## 9. 推荐重做配方 — 第 01 章长讲（Windows 约束下最大化电影感）

### 角色分工（钉死）

| 段落 | 工具 | 产出 |
|---|---|---|
| 0:00–0:08 开场钩子 | lemo-opuscar **或** onetake（二选一，先 lemo） | 竖/横皆可先横 1920×1080 |
| 概念/架构/循环/工具路径 | **huashu** 白板/Vox 语法，≤8s/镜 | `镜NN.mp4` 序列 |
| 代码走读 | **Remotion**（+ shotcraft 卡可选） | 高亮代码 Composition |
| 全片床 + 烧录字幕 + 混音 | **HyperFrames** | 最终 `ch01-long.mp4` |
| 口播 | 已有云扬 VO（勿换引擎） | `assets/vo/` |
| 边画边讲彩蛋段（可选 1 段） | sweety @ **WSL** | 插入 HF timeline |
| 短片 30–60s | lemo-opuscar 主；explainroo 备 | 竖屏 1080×1920 |

**不要**：再用「12 秒循环 HTML 床」垫满 19 分钟。

### 执行步骤（Agent 可照抄）

```text
A. 准备（Windows 可做）
   1. 确认 video/ch01 口播稿与 vo/*.wav + 合并 srt（merged.srt）
   2. 若无词级戳：npx hyperframes transcribe <master.wav> --language zh
   3. 按 STORYBOARD 切 10–14 个 beat（每 beat 真实时长来自 transcript）

B. 分镜画面（WSL 或 Linux box 优先）
   4. huashu：为每个机制 beat 写 镜NN.json（whiteboard/vox），render → 镜NN.mp4
   5. Remotion：代码走读 1–2 个 composition，render 片段
   6. lemo：只做 5–8s 片头，mux 无声或带击打音效

C. HyperFrames 组装
   7. npx hyperframes init video/ch01/hf-remake --non-interactive
   8. DESIGN.md = 驭者深色工程风；SCRIPT = 定稿口播
   9. 每 beat 一个 compositions/*.html：
        - 视频层：嵌入对应 镜NN.mp4 / Remotion 片段（或重建为 seekable HTML）
        - 禁止循环；duration = transcript 边界
   10. 加 captions（rail 为主，章名/口诀处 1 次 embed）
   11. npx hyperframes lint && check && render

D. 烧录兜底（若 HF 字幕未进画面）
   12. ffmpeg -i raw.mp4 -vf "subtitles=ch01.srt:force_style='FontName=Noto Sans CJK SC,FontSize=22,Outline=2'" -c:a copy ch01-long.mp4

E. 验收（不过不交付）
   - 时长 15–20 min
   - 抽帧：每 30s 一张，无重复循环感
   - 字幕全程可读、无双字幕
   - 听感：云扬 -10%/-5Hz
   - 片尾：基于开源书稿 + 合集引导
```

### Top 避坑（对照旧样片失败）

1. 同一 HTML 场景 `seek(t % loop)` 循环 → 观感 PPT。  
2. 只有 SRT 外挂、平台默认关字幕 → 用户说「没字幕」。必须烧录。  
3. 蓝紫渐变星空底 → huashu deliver 会红灯；驭者用深灰/琥珀工程色。  
4. 每镜都 zoom-in → 「放 PPT」；推拉要有来有回。  
5. 短片工具硬扛长片 → lemo/onetake/explainroo 单片甜区 ≤3 分钟。

### 短片并行（不要堵长讲）

```bash
# 建议风格：暗色信息图 / 终端
# 在 WSL：
cd <lemo-film-dir>
# 喂短片脚本 video/ch01/scripts/*short* + 云扬 short vo
# build.sh → film.mp4（1080x1920）
```

---

## 10. 本地研究克隆索引

| 工具 | 研究克隆 SHA（box） |
|---|---|
| sweety-handdraw-video | `1142980` |
| hyperframes | `4f0bdfb` |
| huashu-art-motion | `8a0d7d7` |
| lemo-opuscar | `413a6bd` |
| explainroo | `e95232c` |
| video-shotcraft | `43bd349` |
| onetake | `013a61a` |
| remotion-skills | `30d4553` |

Box 路径：`/workspace/yuzhe-sdd/matrix-research/`。  
用户机工具目录：`D:\Users\claude\claude-code-book-main\video\ch01\tools\`（可把本 cookbook 与浅克隆同步过去）。

---

## 11. 一页速查：谁扛什么

```
长讲成片 ──► HyperFrames（床 + 烧录字幕）
              ├─ 机制动画 ──► huashu-art-motion
              ├─ 代码走读 ──► Remotion (+ shotcraft 单卡)
              ├─ 片头钩子 ──► lemo-opuscar / onetake
              └─ 手绘板书段 ──► sweety @ WSL（可选）

短片成片 ──► lemo-opuscar
              └─ 备选 explainroo（要速度）
```

---

*本文件供重做 Agent 直接执行；改栈先改本节配方表，再动渲染。*
