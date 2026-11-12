# 插图风格迁移记录（2026-11-12）

用户反馈：大模型卷的插图与御舆（yuyu）卷风格不像。核实对象是**图与版面**：课程图是薄荷绿卡片 + 微软雅黑的线框箭头图，御舆卷是墨线 + 朱砂的东方手绘。本轮把课程设计系统整体迁到后者，并修掉一个让旧图悄悄复活的构建缺陷。

## 1. 色彩：祖母绿/柿子橙 → 墨 + 朱砂

| 角色 | 旧值 | 新值 | 实测（`node design/system/contrast.mjs`） |
| --- | --- | --- | --- |
| `--marker` | `#d3efd9` 绿 wash | `#f0e9d8` 暖纸 wash | ink/marker 13.05:1 · APCA 90.0 |
| `--marker-wash` | `#f1f7f2` | `#f7f3e8` | ink 14.25:1 · APCA 95.7 |
| `--accent` / `--accent-ink` / `--accent-block` | `#1f883d` / `#008635` | `#B4472F` 朱砂一色 | 对 paper 5.18:1 · APCA 73.2，小字亦达标 |
| `--persimmon` 系 | `#e2601f` / `#c74c00` | `#B4472F`（同族，靠 ✓/✗ 符号区分语义） | 同上 |

12 组角色对全部 PASS；原“绿字压绿底”禁组合在新色下 WCAG 4.47 < 4.5，仍保留在 `contrast.mjs` 的 FORBIDDEN 中。
`design/system/tokens.md`、`tokens.css`、`design/handdraw/*` 文档同步改写；`render_figures.py` 的白名单自动跟随 `tokens.css`。

## 2. 字体：无衬线 → 衬线

全部生成器（`build-story-figures`、`build-learning-figures`、`mechanism-art`、`mechanism-templates`、`build-application-figures`、`export_books` 封面、10 张手工图）的图内文字从 `Microsoft YaHei` 改为 `'Noto Serif SC','Source Han Serif SC','Songti SC','SimSun',serif`，与课程正文和御舆卷同一语言。

## 3. 构建缺陷：栅格缓存按文件名复用

`scripts/llm/export_course.py` 的 `ensure_image` 原先以 `<stem>.png` 作缓存键（`if not target.exists()`）。改图后旧 PNG 不失效，30 章 PDF/EPUB 继续嵌入旧绿图——首轮改色后合成的 PDF 仍是绿色，就是这个原因。

修复：缓存键带源文件 SHA-256 前 10 位（`image_name()`），SVG 一变名称就变；封面、全书地图、五张阶段图、正文图的 `<img src>` 与 EPUB `cover-image` 清单一并改为该名称。回归测试 `scripts/test_export_course_images.py`：同 stem 内容变 ⇒ 名称变；内容不变 ⇒ 名称稳定；非 SVG 保持原名。

## 4. 验证

| 项目 | 结果 |
| --- | --- |
| `npm test`（editorial + book + llm + fixtures + validate） | 通过（`scripts` 用例 33 项，含新增 3 项） |
| `check:reading:llm` / `check:accessibility:llm` / `check:mechanisms:llm` | 通过：15 flows / 50 layouts；100 pages / 4 keyboard flows；6 flows / 60 layouts，0 外网请求 |
| EPUBCheck 5.3.0 | `llm-explained-handdraw.epub`、`llm-course.epub`、`llm-course-answers.epub` 全部 0 fatal / 0 error / 0 warning，报告按各自 SHA 绑定 |
| 合订本 | 重新合成：2312 页、69 spine、775 条目；PDF `23ed0aa4…`、EPUB `11de3883…`；EPUBCheck 0/0/0 |
| 视觉抽查 | 第 21 页（图 C02-1）等由绿卡雅黑变为暖纸衬线；题注“绿色表示…”等 5 处文字同步改为红色/朱砂 |

## 5. 第二轮：图面去纸底（同日稍后）

用户仍判插图“像贴片”。根因是 `artPaper()` 给每张图铺了独立纸面 `#fbfaf6` + 颗粒 pattern + 0.8 细框 + 四角角标，与御舆卷“墨线直接落在页面上”的画法不同。处理：

- 删除 `scripts/llm/figure-frame.mjs`；四个生成器去掉插值；`build-static-frames.mjs` 从“贴版”改为“剥版”（10 张手写图同样去掉纸面/颗粒/细框/角标），`--check` 幂等。
- 51 张 SVG 重出；像素验证 `attention-row` 角标区暗像素 229→0、全库 `figure-grain` 0 命中。
- **只剥版还不够**：打印样式 `@media print{html,body{background:#ffffff}}` 加 `page.pdf(print_background=True)` 让 PDF 页为纯白，而 `ensure_image` 把台面色 `#fbfaf1` 烤进了每张 PNG——白页上仍是米色方块（页 22 实测 13 927 像素），正是用户说的“贴片”。
- 于是栅格化改透明：台面 `background:transparent` + `screenshot(omit_background=True)`，图变成带 alpha 的 PNG，屏幕（纸色页 `#fbfaf6`）与打印（白页）都直接落在页面上；`RASTER_VERSION` 并入缓存名 `<stem>-<digest>-r2.png`，渲染变更不再被旧 PNG 遮蔽（与第 3 节同一教训）。
- 复验：`attention-row-…-r2.png` 角 `(0,0,0,0)`、alpha-0 像素 1 023 401；PDF 页 22 米色像素 13 927→0；EPUBCheck 三册 0/0/0；`npm test` 通过；course PDF 416 页。

## 6. 未改动

- `videos/` 九支视频与 `scripts/llm/build-media.mjs`：成品已审阅冻结，改其来源会使 `media-manifest` 的 sourceHash 失效并触发重审；视频如需同风格，另开一轮重渲。
- `design/system/REVIEW.md` 等历史评审记录：保留当时事实，不回写。
