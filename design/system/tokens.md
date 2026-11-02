# tokens · 手绘主视觉 × 歸藏约束底座（设计系统地基）

> 本文件是全部 Phase 的唯一色彩/质感/字体依据。视频场景、封面 `covers/*.html`、书籍图解、新增网页出口都引用 `tokens.css`，不再各写各的 hex。
> 定位（用户已定）：**手绘是长相，歸藏是物理定律**——只借它的 OKLCH 收纳 + WCAG/APCA 双阈 + CJK 数值规则，不采纳杂志/瑞士的视觉身份（统一圆角、无投影等一概不用；手绘保留不齐圆角 + 硬投影）。

## 1. 为什么要有派生 token（实测暴露的问题）

手绘原色 `--accent:#1f883d`、`--persimmon:#e2601f` 做**图形/大字/下划线**很好，但直接拿去当小字或色块上的文字会**不达标**（见下表 FAIL 行）。歸藏的做法是保留同色相、在 OKLCH 里降明度派生出 `--accent-ink` / `--accent-on` 供文字使用。本系统照此产出两个深色派生 token，并用 `contrast.mjs` 锁死。

## 2. 实测对比度（`node design/system/contrast.mjs` 复算；阈值取自歸藏 ROLE_FLOORS）

角色下限：正文 {APCA 75, WCAG 7}、次要/小字强调 {60, 4.5}、色块上文字 {45, 4.5}、大字/展示仅 {APCA 45}。

| 用途 | 前景 | 背景 | WCAG | APCA Lc | 角色 | 判定 |
|---|---|---|---|---|---|---|
| 正文/墨线 | `#1f2328` ink | `#fbfaf6` paper | 15.13 | 99.7 | 正文 | PASS |
| 正文 | ink | `#fffdf8` card | 15.54 | 101.6 | 正文 | PASS |
| 正文 | ink | `#d3efd9` marker | 12.88 | 89.1 | 正文 | PASS |
| 次要文字 | `#57606a` | paper | 6.12 | 78.7 | 次要 | PASS |
| 次要文字 | ink-soft | card | 6.29 | 80.6 | 次要 | PASS |
| 结论横幅底 | ink | `#f1f7f2` marker-wash | 14.54 | 97.0 | 正文 | PASS |
| 结论横幅底 | ink-soft | marker-wash | 5.88 | 76.0 | 次要 | PASS |
| 细线/停用卡底 | ink-soft | `#e6e1d4` rule | 4.89 | 64.2 | 次要 | PASS |
| 绿小字/细线 | `#008635` accent-ink | paper | 4.51 | 69.0 | 小字强调 | PASS |
| 绿小字/细线 | accent-ink | marker-wash | 4.33 | 66.3 | 小字强调 | 临界（WCAG <4.5），改放 ink-soft |
| 绿小字/细线 | accent-ink | `#d3efd9` marker | 3.84 | 58.3 | — | **FAIL：绿字不许压绿底** |
| 绿实块上纸色字 | paper | `#008635` accent-block | 4.51 | 74.1 | 色块文字 | PASS |
| 绿下划线/图形（大字档） | `#1f883d` accent | paper | 4.33 | 67.9 | 展示线 | 仅大字/图形，**禁作小字** |
| 橙 CTA 填充/苹果/箭头（大字） | `#e2601f` persimmon | paper | 3.39 | 59.2 | 展示线 | 仅大字/填充，**禁作小字**；小字改 `--persimmon-ink:#c74c00` |

OKLCH 锚点（供再派生/换品牌色）：paper L98.5 C.0054 H95.1｜card L99.4 C.0069 H88.6｜ink L25.4 C.0111 H254｜ink-soft L48.5 C.0196 H251｜marker L92.6 C.0417 H152｜accent L55.2 C.1450 H148.2｜persimmon L64.5 C.1774 H42.9。

## 3. token 用途规则（写死，避免误用）

- **正文/标题/墨线/图解线稿** 一律 `--ink`；次要说明、图注 `--ink-soft`。
- **强调只有一处**：`--accent` 用于波形下划线、图形标记、大号数字（≥展示线尺寸）。需要绿色**小字或细线**时用 `--accent-ink`，不用 `--accent`。
- **marker 高亮** `--marker` 只做关键词底纹，底上只放 `--ink` / `--ink-soft`；**绿字压绿底不达标**（accent-ink/marker APCA 58.3 < 60），`contrast.mjs` 已把它列为禁止组合。
- **结论横幅** 用 `--marker-wash`（比 marker 浅一档）+ `--accent` 描边；它和 `--marker` 的分工是“横幅讲整句结论、marker 标单个词”，同图里两者别混用同一语义。
- **细线与停用态** 用 `--rule`：分隔线、以及“这是错例/已弃用”的灰卡底（如 Mom Test 左列）。灰卡上的文字仍走 `--ink`/`--ink-soft`，不许再引入第四种灰。
- **柿子橙 `--persimmon` 是稀缺点缀**：只给 CTA 块、苹果、方向箭头，且是大号；橙色小字一律 `--persimmon-ink`。
- **实色绿块**（如“下一步/成功”填充）用 `--accent-block` + `--paper` 文字，绝不用白 `#fff`（违反“不用纯白”）。
- 每套版式**最多 1 个 accent 色**；手绘的绿与橙按“一主(绿)一点缀(橙)”分工。
- **以上规则由机器把关**：`design/handdraw/render_figures.py` 出图前会读 `tokens.css` 做白名单校验，并对 `<text fill="#1f883d|#e2601f">` 直接报错——越界色根本渲不出来，不靠人记住。

## 4. 手绘质感签名（三件套，任何新资产必须带上以保证同源）

1. 纸纹：`--paper-grain` 24px 点阵，`opacity .05`，容器 `::after`。
2. 卡片：`--card` 底 + `--ink-line`(4px 墨) + `--radius-hand`(不齐四角) + `--shadow-hard`(8px 9px 0 硬投影，无模糊)。
3. 波形下划线：`--accent` 4px 圆头 SVG（`viewBox 0 0 240 10`），压在标题基线。

## 5. 与现有代码的接缝

- `design/handdraw/covers/cover.css` 与各场景 `<style>` 已内联以上值（`--paper/--ink/--marker/--card/--accent` + `--persimmon:#e2601f`）；Phase E 收敛为引用本 `tokens.css`，Phase G 的网页出口直接 `<link>` 或内联本文件。
- `contrast.mjs` 是 token 的**回归门**：改任何 hex 后 `node design/system/contrast.mjs` 必须仍 `exit=0`；可加进 CI（当前 CI 只跑 `npm test`）。

## 6. 来源

- 手绘风格与配色语义：`~/.agents/skills/handraw-style`（FA-013 / FA-040 / C-11 祖母绿 / C-26 柿子橙 / C-32 炭黑；库内无 hex，色值由本系统定义）。
- 约束底座：歸藏 `dsh-guizang-design` — `guizang-page-skill/scripts/gz-theme.mjs`（OKLCH/WCAG/APCA/ROLE_FLOORS，MIT）、`assets/themes.json`（token 结构）、`references/design-rules.md`（T 规则，见 `cjk-rules.md`）。
