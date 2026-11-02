# 手绘风改造方案（handraw-style）

> 依据 [yang0/handraw-style](https://github.com/yang0/handraw-style) 的风格库与规则生成。
> 本目录交付提示词与点位方案，并落地了代码绘制的封面与首批图解；`covers/cover-art-fa013.webp` 为 FA-013 真出图 key visual（无字）。
> 原始需求逐字存档于 `original-request.txt`。

## 一句话目标

把课程从「截图 + 代码海报」升级成一套统一的手绘语言：**封面靠一个隐喻抓住眼球，正文靠图解替读者减负**。

## 推荐组合

💡 智能推荐组合（本次由主题语义实时选定，可换编号）

| 用途 | 风格 | 主题色 | 为什么 |
| --- | --- | --- | --- |
| 书封面 + 5 集视频封面 | `FA-013` Bold Flat Everyday Satire（Jean Jullien） | `C-11` 祖母绿（主）+ `C-26` 柿子橙（点缀） | 粗黑轮廓 + 平涂色块在手机缩略图上依然一眼可辨；互联网生活讽刺的气质正合「不会写代码也能做软件」的反差幽默；祖母绿沿用课程品牌绿，柿子橙只给 CTA 和苹果用 |
| 书籍知识图解 | `FA-040` Minimalist 2D Hand-Drawn Doodle | `C-32` 炭黑（线稿）+ `C-11` 祖母绿（标注） | 轻柔线条、低细节、概括造型，图解的主角是结构与标签而不是质感；炭黑线稿配祖母绿标注，打印和夜间模式都不刺眼 |

风格激活核查（基线模型 gpt-image-2，用官方解析器实测，非人工猜测）：

```bash
cd ~/.agents/skills/handraw-style
python skills/handdraw-style-prompter/scripts/resolve_reference.py --model gpt-image-2 --style FA-013
python skills/handdraw-style-prompter/scripts/resolve_reference.py --model gpt-image-2 --style FA-040
```

- `FA-013`：`activation_source=name+style`，`use_reference_image=false`，`include_prompt_traits=false` → 提示词只写作者与风格名，**不写核心特征、不需要垫图**。
- `FA-040`：`activation_source=name+style+traits`，`use_reference_image=false`，`include_prompt_traits=true` → 提示词带核心风格特征，**不需要垫图**。

因此本方案全部提示词均为纯文本直出，无参考图依赖——**前提是你用 gpt-image-2**。
换未校准模型（即梦、Midjourney、nano banana 等）时，解析器返回 `name+style+traits+reference-image`，必须另附编号参考图并加隔离指令，否则画风会漂：

- 参考图（已核实存在）：`images/individual/FA/FA-013.webp`（封面）、`images/individual/FA/FA-040.webp`（图解），位于安装根目录下。
- 隔离指令（中英任选，放在提示词末尾）：`所附图片仅用于参考画风。只提取参考图的风格特征，例如线条、笔触、媒介、材质、色彩倾向和整体视觉语言；不要使用、复制或延续参考图中的任何主体、人物、动物、服装、道具、动作、姿态、场景、背景、构图、布局、文字或故事。最终画面内容完全以用户提供的主题为准。`

## 本机安装记录

- 安装位置：`~/.agents/skills/handraw-style`（shallow clone，版本 `1.9.8`，101 MB，含 `images/` 参考图与 `skills/` 子技能）。
- omp 加载：已加入 `~/.omp/agent/config.yml` 的 `skills.includeSkills`（`handraw-style`、`handdraw-style-prompter`），`skill://handdraw-style-prompter` 可直接读取。
- 自检：`python skills/handdraw-style-prompter/scripts/validate_library.py` 可跑通索引与画廊重建；上游自身有 1 条 FAIL——`skills/release-illustration-planner/SKILL.md:94` 泄漏了作者本地路径 `file:///E:/handraw-style/...`，不影响本方案使用。
- 更新：`cd ~/.agents/skills/handraw-style && git pull --depth 1`。

## 资产改造清单

| 资产 | 现状 | 改造稿 |
| --- | --- | --- |
| 书封面 `book/assets/cover.svg` / `cover.webp` | ✅ 手绘 + 已对齐 `design/system` token（卡面 `#fffdf8`、角标 `#008635`+纸色字 4.51:1/APCA 74、柿子橙苹果）；webp 由 `render_book_cover.py` 重出 | `covers.md` 第 0 组（已落地） |
| EP.01 横/竖封面 `deliverables/{landscape,vertical}-cover.webp` | ✅ composition 已手绘皮肤（b21a488）并按 composition 重截（c7715ea）；CTA 改 `#008635` 底 + 纸色字（原白字压 `#1f883d` 实测 4.33:1 不达标） | `render_ep01_covers.py` |
| FA-013 真出图 key visual `covers/cover-art-fa013.webp` | ✅ 已出图（1376×768、画面无字；`prompt_style.py --style FA-013 --color C-26` 的确定性提示词） | Phase G 落地页/deck hero 可复用；带字封面仍以代码绘制为准（中文排版可控） |
| EP.02/03/04 封面 `deliverables/ep0X-cover.webp` | ✅ 已换成手绘稿（2026-10-31） | `covers.md` 第 3–5 组 → 实现在 `covers/ep0X.html` |
| 书籍正文知识图解 | 已用**手写 SVG** 落地首批 6 张入正文（见 `book-illustrations.md`）；215 节全量点位未扫 | Phase C：`prompt_style.py` 批量出词 + `insert_illustrations.py` 回填 |
| 视频正片场景 | ✅ 手绘皮肤（纸面/墨线/marker/硬阴影/纸纹 + kinetic 动效）**已铺满 5 工程 31 场景并重渲 5 支成片**（b21a488/3b31a9b）；仅欠“场景内示意图换成手绘图形隐喻” | Phase E：图解层（时序中性、不改时长） |

> **视觉 token 的权威来源已上移到 `design/system/`**（`tokens.css` + `tokens.md` + `contrast.mjs` + `cjk-rules.md` + `deai-rules.md`）：本目录的 `cover.css`/场景内联值与之同源，后续以 `design/system/` 为准。手绘=长相，歸藏=可读性约束（OKLCH+WCAG/APCA 双阈、CJK T 规则）。

## 知识图解的七条红线（来自 article-illustration-planner + 本书实际图况，执行时必须遵守）

1. 不画微缩摆拍、书桌、咖啡杯、童话小精灵——画面 100% 给图表本身。
2. **不许把知识画丢**：公式、权重数字、判断阈值、关键台词必须作为图中标签保留；正文同步保留结论。
3. 必须用真图形隐喻：层级用金字塔、筛选用漏斗、对比用双列、流程用路径图，严禁把文字抄进方框就算图解。
4. 间距：相邻插图正文间隔 ≥400–500 字且跨标题；连续 1000–1200 字以上无图的段落优先补图。
5. **只新增，不替换**：书中已有的 `<figure>`（含 CC BY / CC BY-SA / 公有领域照片与 Design Council 官方双钻图）连同 `figcaption` 和署名原样保留；新图不得顶替它们，否则署名丢失、图说失锚。
6. 间距按**已有图片**计算，不是从 0 开始：JTBD、访谈、双钻等章已有 8–14 张图，新图解要落在没有图的小节，不与现有 figure 背靠背。
7. 图解不出现人物角色：主角是结构、箭头与标签（封面才允许人物幽默）。

## 已落地：EP.02–EP.04 封面改造成手绘（2026-10-31）

封面不再依赖生图模型，改成**代码画**：`covers/ep0X.html` + 共用 `covers/cover.css`，视觉 token 与视频手绘层完全一致
（纸面 `#fbfaf6`、纸纹 24 px 点阵、墨线 `#1f2328`、marker `#d3efd9`、硬阴影、手绘地面线、波形下划线），
每个 EP 一套独立隐喻：打字机写诗 / 拖行李箱搬进文件夹房子 / 从笔记本跳进云再落到手机。

```bash
python design/handdraw/render_covers.py          # 9 张：ep02–04 × 16:9 / 4:3 / 3:4
```

渲染用无头 Chrome（每次独立 `--user-data-dir`，Chrome 单例锁会让并发截图静默失败），尺寸钉死：
16:9 = 1920×1080（B站 + `deliverables/ep0X-cover.webp`），4:3 = 1440×1080，3:4 = 1080×1440（抖音竖封面 / 视频号资料卡）。

EP.01 的横 / 竖封面不走这套 html：它们本来就是 `videos/{landscape,vertical}/compositions/cover.html`，
但这两个 template 没挂进任何 project index，`hyperframes snapshot` 够不到。它们的时间线只是一段 t=0 缩放到 1 的
Ken Burns，静态 markup 就是封面本身，于是抽 `<template>` 出来直接截图：

```bash
python design/handdraw/render_ep01_covers.py     # 2 张：1920×1080 + 1080×1920
```

**平台侧还没换**：抖音 / B 站 / 视频号线上仍是 2026-10-30 的旧「绿蛇海报」；仓库里已是新手绘稿，要同步必须重新上传封面。

## 出图与回填流程

1. 从 `covers.md` / `book-illustrations.md` 复制提示词到生图模型（中文或英文任一）。
2. 封面按既有规格导出：B站 1920×1080、抖音 1080×1440 / 1440×1080、视频号 3:4 资料卡。
3. 插图回填到 `book/book.md` 对应章节，图片放 `book/assets/images/handdraw/`，正文保留公式与结论。
4. 跑 `npm test`（会校验本地图片引用完整），再提交。

## 尚未做、需要时再点名的事

- 带字封面的真出图版本：FA-013 key visual 已出（`covers/cover-art-fa013.webp`，无字）；若要 AI 版封面，中文标题仍需代码叠加，暂以 SVG/代码封面为交付口径。
- 场景内示意图的手绘化（Phase E：皮肤已铺满 31 场景，只欠把“截图/示意图”换成图形隐喻；时序中性、不改时长，需重渲）。
- 全书 215 节的完整插图点位扫描与回填（Phase C：已交 6 张，`prompt_style.py` + `insert_illustrations.py` 可批量）。
- 全书正文 / 配音稿 / 字幕的去 AI 味（Phase D 正文 refactor、Phase F 口播 recreate + 逐集重剪，口径见 `design/system/deai-rules.md`）。
- 新增网页出口：落地页 / deck / 小红书卡片（Phase G，借歸藏工作循环 + 手绘 token）。

> 完整改造路线见根 SPEC（本改造计划 rapid-lake-darter）；地基与约束见 `design/system/`。
