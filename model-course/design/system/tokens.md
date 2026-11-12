# tokens · 手绘主视觉 × 歸藏约束底座（设计系统地基）

> 本文件是全部 Phase 的唯一色彩/质感/字体依据。视频场景、封面 `covers/*.html`、书籍图解、新增网页出口都引用 `tokens.css`，不再各写各的 hex。
> 定位（用户已定）：**手绘是长相，歸藏是物理定律**——只借它的 OKLCH 收纳 + WCAG/APCA 双阈 + CJK 数值规则，不采纳杂志/瑞士的视觉身份（统一圆角、无投影等一概不用；手绘保留不齐圆角 + 硬投影）。

## 1. 为什么要有派生 token（实测暴露的问题）

手绘强调原用祖母绿 `#1f883d` + 柿子橙 `#e2601f`。为与御舆（yuyu）卷的墨线 + 朱砂视觉语言同源，强调色整体迁到朱砂 `#B4472F`（OKLCH H34），柿子橙位并入同一朱砂。墨色纸面系统（paper/ink/ink-soft/rule）不变。

## 2. 实测对比度（`node design/system/contrast.mjs` 复算；阈值取自歸藏 ROLE_FLOORS）

角色下限：正文 {APCA 75, WCAG 7}、次要/小字强调 {60, 4.5}、色块上文字 {45, 4.5}、大字/展示仅 {APCA 45}。

| 用途 | 前景 | 背景 | WCAG | APCA Lc | 角色 | 判定 |
|---|---|---|---|---|---|---|
| 正文/墨线 | `#1f2328` ink | `#fbfaf6` paper | 15.13 | 99.7 | 正文 | PASS |
| 正文 | ink | `#fffdf8` card | 15.54 | 101.6 | 正文 | PASS |
| 正文 | ink | `#f0e9d8` marker | 13.05 | 90.0 | 正文 | PASS |
| 次要文字 | `#57606a` | paper | 6.12 | 78.7 | 次要 | PASS |
| 次要文字 | ink-soft | card | 6.29 | 80.6 | 次要 | PASS |
| 结论横幅底 | ink | `#f7f3e8` marker-wash | 14.25 | 95.7 | 正文 | PASS |
| 结论横幅底 | ink-soft | marker-wash | 5.76 | 74.7 | 次要 | PASS |
| 细线/停用卡底 | ink-soft | `#e6e1d4` rule | 4.89 | 64.2 | 次要 | PASS |
| 朱砂小字/细线 | `#B4472F` accent-ink | paper | 5.18 | 73.2 | 小字强调 | PASS |
| 朱砂小字/细线 | accent-ink | card | 5.32 | 75.0 | 小字强调 | PASS |
| 朱砂小字/细线 | accent-ink | `#f0e9d8` marker | 4.47 | 63.4 | — | **禁：双阈下 WCAG <4.5**，红字不压 wash 底 |
| 朱砂实块上纸色字 | paper | `#B4472F` accent-block | 5.18 | 78.2 | 色块文字 | PASS |
| 朱砂下划线/图形 | `#B4472F` accent | paper | 5.18 | 73.2 | 展示线 | 图形/下划线/小字均可用 |

OKLCH 锚点（供再派生/换品牌色）：paper L98.5 C.0054 H95.1｜card L99.4 C.0069 H88.6｜ink L25.4 C.0111 H254｜ink-soft L48.5 C.0196 H251｜marker L93.5 C.0238 H88.2｜marker-wash L96.4 C.0152 H90.2｜accent L54.1 C.1472 H34.0（persimmon 同）。

## 3. token 用途规则（写死，避免误用）

- **正文/标题/墨线/图解线稿** 一律 `--ink`；次要说明、图注 `--ink-soft`。
- **强调只有一处**：`--accent`（朱砂）用于波形下划线、图形标记、数字与小字强调；`--accent-ink` 与它同值，保留两名是为了语义清晰（文字位用 ink 名）。
- **marker 高亮** `--marker` 只做关键词底纹，底上只放 `--ink` / `--ink-soft`；**朱砂字压 wash 底双阈不达标**（accent-ink/marker WCAG 4.47 < 4.5），`contrast.mjs` 已把它列为禁止组合。
- **结论横幅** 用 `--marker-wash`（比 marker 浅一档）+ `--accent` 描边；它和 `--marker` 的分工是“横幅讲整句结论、marker 标单个词”，同图里两者别混用同一语义。
- **细线与停用态** 用 `--rule`：分隔线、以及“这是错例/已弃用”的灰卡底（如 Mom Test 左列）。灰卡上的文字仍走 `--ink`/`--ink-soft`，不许再引入第四种灰。
- **深朱 `--persimmon` 与 `--accent` 同值**：保留 token 名是为了旧排版引用不破；错误/警示标记（叉、失败分支）用它，语义上与“通过”靠符号（✓/✗）区分，不靠色相。
- **实色块**（如“下一步/成功”填充）用 `--accent-block` + `--paper` 文字，绝不用白 `#fff`（违反“不用纯白”）。
- 每套版式**最多 1 个 accent 色**；墨为主、朱砂为记。
- **以上规则由机器把关**：`design/handdraw/render_figures.py` 出图前会读 `tokens.css` 做白名单校验，并对 `<text fill="#1f883d|#e2601f">` 直接报错——越界色根本渲不出来，不靠人记住。

## 4. 手绘质感签名（三件套，任何新资产必须带上以保证同源）

1. 纸纹：`--paper-grain` 24px 点阵，`opacity .05`，容器 `::after`。`background-size` **必须写两值**
   （`24px 24px`）：径向渐变没有内在比例，单值时另一轴按 `100%` 解，点阵会拉成竖条。
2. 卡片：`--card` 底 + `--ink-line`(4px 墨) + `--radius-hand`(不齐四角) + `--shadow-hard`(8px 9px 0 硬投影，无模糊)。
3. 波形下划线：`--accent` 4px 圆头 SVG（`viewBox 0 0 240 10`），压在标题基线。

## 5. 与现有代码的接缝

- `design/handdraw/covers/cover.css` 与各场景 `<style>` 已内联以上值（`--paper/--ink/--marker/--card/--accent` + `--persimmon:#B4472F`）；Phase E 收敛为引用本 `tokens.css`，Phase G 的网页出口直接 `<link>` 或内联本文件。
- `contrast.mjs` 是 token 的**回归门**：改任何 hex 后 `node design/system/contrast.mjs` 必须仍 `exit=0`；可加进 CI（当前 CI 只跑 `npm test`）。

## 6. 来源

- 手绘风格与配色语义：`~/.agents/skills/handraw-style`（FA-013 / FA-040 / C-32 炭黑）；强调色 2026-11 起与御舆卷对齐为朱砂 `#B4472F`（原 C-11 祖母绿 / C-26 柿子橙退役）。
- 约束底座：歸藏 `dsh-guizang-design` — `guizang-page-skill/scripts/gz-theme.mjs`（OKLCH/WCAG/APCA/ROLE_FLOORS，MIT）、`assets/themes.json`（token 结构）、`references/design-rules.md`（T 规则，见 `cjk-rules.md`）。
