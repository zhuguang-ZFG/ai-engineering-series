# 第 05 章视频制作包｜驭者·Agent Harness

> 账号：小电讲电路 · 系列：驭者·Agent Harness · 第 05 章
> 书稿：`第二部分-核心系统篇/05-设置与配置-Agent的基因.md`（英：`en/Part-2-Core-Systems/05-Settings-and-Configuration-Agent-DNA.md`）
> 规则：**先过片，再发布**；本目录脚本可入库，大体积 mp3/mp4 不入库。

## 文件

| 文件 | 用途 |
|------|------|
| `long-outline.md` | B 站长讲分镜大纲（含时间轴与动画清单） |
| `long-script.md` | 长讲全本口播 |
| `short-script.md` | 抖音/小红书竖屏钩子 + 口播 |
| `voice.md` | 音色锁定（沿用云扬） |
| `gate-checklist.md` | 过片门禁 |
| `STATUS.md` | 制作/发布状态 |

## 本章定位

第二部分开篇。前四章装完整车——心跳、双手、护栏；本章往回追一步：**这些行为是谁定的**。

## 叙事线（用户已定：痛点开场）

改了 `settings.json` 却不生效 → 因为配置不是一个文件，是**六层沉积岩**，后者盖前者 → 合并规则不止一种（数组只挂不摘、标量直接盖、策略层只认一份）→ 收刀：六层里有一层，**安全问题上系统根本不看它**。

## 成片目标路径（本机）

- 长讲：`video/ch05/out/ch05-long-v1.mp4`（1920×1080，15–20 min）· **未开渲**
- 短片：`video/ch05/out/ch05-short-v1.mp4`（1080×1920，50.97 s）· **已出片，待过片**

## 流水线复用

- 工具链：`video/ch05/tools` → junction → `video/ch01/tools`
- 长讲：镜像 `video/ch04/hf-remake/build_dense_v2.py`（densify v2 已修 hold 插值泄漏）
- 短片：镜像 `video/ch04/hf-remake/build_short.py`，音频这一层已分叉——音效改用 media-use 自带的免版权库、
  背景音乐加了本地 MusicGen 生成的一条 bed（详见 `STATUS.md`「短片音频」）。ch01–ch04 都没有 bed，本章是第一支；
  后续章节直接抄 ch05 的 `stage_sfx()` / `bgm_tag()`，别再回到 `struct` 现算 WAV。
- 钩子沿革：ch03「锤子 vs 双手」→ ch04「万能钥匙 vs 四道闸」→ ch05「一个文件 vs 六层岩」
