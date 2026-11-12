# 动画层的动效语言（kinetic motion layer）

书里的静态插画用手绘语法，视频里的动画沿用同一套语言：纸面、墨线、marker 笔触，外加一层"动"的规则。
动效规则不是凭感觉定的，来自 GitHub 上的 motion-design 技能参考实现：

- `artkruglov/motion-design-film` — `references/motion-design.md`：入场用 `back` 过冲、字母级 stagger、marker sweep、按节拍剪辑、任何画面静止不超过约 1.5 s。
- `paceM99/motion-advertorial-skill` — HTML/GSAP 动效广告的节奏组织方式（对照参考，未安装）。

只把它们的**规则**落进本仓库的 composition，不引入它们的时间轴工具链：本项目的场景时长由
`scripts/validate.mjs` 钉死，配音切点来自 TTS `WordBoundary`，任何动效都必须是**时序中性**的。

## 1. 五条落地的规则

| 规则 | 参考出处 | 本项目的实现 |
| --- | --- | --- |
| 标题逐字过冲入场 | stagger 0.03–0.05 s、`back` 过冲 | `ksplit()` 拆字 → `back.out(1.9)`、45 ms stagger、`y:44 → 0`、`scale:1.28 → 1`、`rotation:-3° → 0` |
| 关键词 marker 扫过 | marker sweep behind a word | `--gk` 0%→100%，`background-size` 驱动浅绿高亮，0.4 s |
| 手绘下划线画出来 | line drawing (stroke-dashoffset) | `--sq` 0→240 px，配合标题 `::after` 的 SVG 波形 |
| 卡片弹入而非淡入 | scale 1.3→1 比 0→1 更有力 | 133 处卡片入场：`scale:0.95 → 1` + `back.out(1.5)`，原时长不变 |
| 静止不超过 ~1.5 s | holds: slow drift | 保留 Ken-Burns 底线：`#root` `scale:1 → 1.03`，时长等于场景真实长度 |

## 2. 不能动的三条红线

1. **透明度不参与入场动画。** 标题、tag 的入场只动 `transform`；一旦让 `opacity` 从 0 起，WCAG 采样点会抓到低对比度帧（ep03 曾出现 `1.44:1`）。
2. **时长与切点不变。** 入场 tween 的 `duration` 与 `position` 保持原值；唯一的例外是标题段，它按原 tween 的 position 平移（`pos`、`pos+0.34`、`pos+0.5`），所以藏在 `data-start="27.5"` 里的标题（竖版 `#r-map-title`）不会提前播完。
3. **不覆盖作者已写的 scale 起点。** 已经带 `scale: 0` / `.4` / `.75` 的入场（如 `#g-bp`、`#r-apple`、`#p-keys .p-key`）保持原样；自动加 pop 只作用于没有 scale 键的 tween，并且 `from` 与 `to` 两侧同时给值（GSAP `fromTo` 只 tween `to` 对象里出现的键）。

## 3. 视觉 token

| 用途 | 值 |
| --- | --- |
| 纸面底色 | `#fbfaf6` |
| 纸纹 | `radial-gradient(#1f2328 0.6px, transparent 0.7px)` / `24px` / `opacity .05` |
| 卡片填充 | `#fffdf8` |
| 墨线 | `4px solid #1f2328`（深色块 `3px`） |
| 圆角 | `16px 11px 18px 9px`（不齐的手绘感） |
| 硬阴影 | `8px 9px 0 rgba(31,35,40,.12)`（卡片）/ `.18`（大块） |
| marker 高亮 | `#f0e9d8`，覆盖关键词 42% 高度、基线 74% |
| 波形下划线 | `#B4472F`，4 px 圆头，240×10 SVG |

## 4. 验收方式

1. `npm run check`：五个工程全部 `Check passed`，WCAG 文本检查全过（ep02 108、ep03 51、ep04 63、landscape 62、vertical 81）。
2. `snapshot --review`：肉眼确认逐字入场、marker、波形下划线三段时序都对。
3. 像素验证 pop 真的收在 1.0：ep04 `#w-url`（CSS 宽 860）在 30 s 处实测顶边墨线跨 848–859 px，符合漂移缩放 1.00–1.03 区间；若 scale 卡在 0.95 会是 ~817 px。
