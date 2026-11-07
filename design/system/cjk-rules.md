# CJK 排版规则（约束底座 · 移植自歸藏 design-rules.md T1–T14）

> 适用范围：Phase G 新增网页出口（落地页/deck/卡片）、书内自有 HTML figure、封面 `covers/*.html` 的中文排版。
> 不适用范围：Markdown 正文书（由阅读端渲染，仅保留 `~/book` 现有约定）；视频场景里的大号标题沿用现有字号栈。
> 定位：**只取歸藏的“可读性数值”，不取它的“杂志/瑞士长相”**。手绘保留不齐圆角 + 硬投影（瑞士风不用，此处覆盖之）。

## 落地条目（每条含歸藏出处 + 本项目实现口径）

| # | 规则 | 歸藏出处（clreq / 实测） | 本项目实现 |
|---|---|---|---|
| T1 | `<html lang="zh">`；中文规则挂 `:lang(zh)` | clreq 依赖语言标记 | 出口 HTML 一律写 lang；避免对纯代码块套中文规则 |
| T2 | 正文 17px（`--text-size:1.0625rem`） | 设计决定（15.2px 对汉字偏小） | `tokens.css --text-size`；deck 卡片正文可按场景放大但≥17px |
| T3 | 行高 1.8（瑞士）/1.85（杂志） | 中文行距 1.5–2 倍，1.2 过密 | 长文出口用 1.85；大字/卡片用 1.6–1.8 |
| T4 | 行长 `max-width:36em`（≈36 汉字） | Baymard 50–75 拉丁→汉字换算（歸藏推断值） | 落地页正文栏 ≤36 字/行 |
| T5 | 正文两端对齐 `justify`；列表/含链接代码段左齐 | clreq §6.2 | 出口正文 justify；表格、命令、URL 段 `text-align:start` |
| T6 | 不首行缩进，段距 1em | clreq 段间空白分段 | `--para-gap:1em`，无 `text-indent` |
| T7 | 中文 `letter-spacing:0`（英文可微调） | 汉字等宽方块，加字距破坏密排 | 标题勿加负字距（笔画粘连） |
| T8 | 避头尾 `line-break:strict` | clreq §6.1.1 行首行尾禁则 | 出口正文加 `line-break:strict` |
| T9 | 标点挤压 `text-spacing-trim:normal`（Chromium+需字体 halt/chws）；Safari `hanging-punctuation:allow-end` | clreq 标点宽度 | 渐进增强：不支持则不处理（现有 Chrome 无原生即跳过） |
| T10 | 中西文/中数字间 ≤1/4em 间距（作者未留空格处）；`%`/`°` 前不加 | clreq §6.3.3 + 中文文案指北 | 出口用渲染器插 `<span>` 或直接半角空格；跳过 `code/pre/kbd/svg` 与属性。书正文沿用现状 |
| T11 | 长串 `overflow-wrap:break-word`，长 URL 不撑破版心 | 裸链接 | 出口加 `overflow-wrap:anywhere` |
| T12 | 中文强调**不用伪斜体**，用着重号（横排在字下）；英文/代码仍斜体 | clreq §5.3.1 | 出口 `text-emphasis:filled dot`；**禁用 `font-style:italic` 斜体中文** |
| T13 | 字体栈西文在前、中文在后 | 系统字体规范 | `--font-sans`（Inter…Noto Sans SC…）；课程标题既有 `Noto Sans JP` 栈保留 |
| T14 | 标题字重≥300（细体在 1x 屏发虚），行高 1.4（h2/h3） | 中文对字重/行高更敏感 | deck/落地页标题≥300；勿用 100/200 细体 |

## 版式红线（歸藏 + 本系统）

- **不用纯白 `#fff` / 纯黑 `#000`**：底用 `--paper`，字用 `--ink`，块上字用 `--paper`。手绘天然满足。
- **每套风格 1 个 accent**：本系统主 accent=绿 `--accent`，橙仅点缀（见 tokens.md §3）。
- **图表用 accent + 灰交替，不用多彩**；**accent 线仅用于组件内部标记**（如 blockquote 左线、波形下划线）。
- 几乎不用线；全文最多 2 条粗线；section 间靠 ≥64px 间距分隔，不画分隔线。
- 不做首字下沉；不采纳 `(01)` 括号编号、描边巨型装饰数字、章节整块色底（瑞士/杂志专属，与手绘冲突）。

## 与手绘的取舍（明确覆盖点）

| 歸藏默认 | 本系统覆盖为 | 原因 |
|---|---|---|
| 统一小圆角 / 无投影 | `--radius-hand` 不齐四角 + `--shadow-hard` 硬投影 | 手绘签名，一眼同源优先 |
| 卡片 1px 细边框 | `--ink-line` 4px 墨线 | 手绘轮廓 |
| 严格瑞士栅格 | 保留可读性栅格，但允许手绘地面线/波形等非几何装饰 | 手绘是长相 |

> 数值规则（T2–T14）全部采纳；只有“视觉身份”层（圆角/投影/线宽/装饰）让位于手绘。
