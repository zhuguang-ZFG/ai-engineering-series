# 插图扩容设计：实物图 / 手绘图 / 连续动图

日期：2026-11-01　状态：手绘与连续动图通道已落地（第四十一轮），实物位图待做
负责人：正文与构建器同仓演进，无独立分支

## 1. 要解决的问题

《御舆》原本的手写图只有三个落点：章徽（章名右侧，64×64）、篇题刻（篇首，
200×140）、扉页车图（1000×470）。正文里一张画都插不进去——所有解释都靠
Mermaid 结构图承担。结果是：读者看得见数据流，看不见「这东西长什么样、
按什么顺序发生」。

三类配图各自要补的缺口：

| 类别 | 现状 | 目标 |
| --- | --- | --- |
| 手绘图（矢量） | 28 份，正文 2 张（均在 ch03） | 每个单元正文至少 1 张，随文字迭代继续加密 |
| 连续动图 | 1 条四格胶片（ch03 编排流水线） | 凡是「有先后顺序的过程」都画成胶片：对话循环、钩子拦截、压缩、权限判定 |
| 实物图（位图） | 0 张 | 扉页与四篇题刻各配一张静物实拍/写实图，正文仍走矢量 |

量出来的地板：20 个单元里带正文图版的目前只有 ch03 一个（中英各两张 `ill`
围栏），所以「每个单元正文至少 1 张」是缺口 19 个单元，不是修辞。

## 2. 已定的两个决策

1. **实物图走混合路线**：正文一律矢量（可重着墨、可逐笔回放、体积小），
   只有扉页与篇题刻用位图。理由：单文件离线成品里，正文插图要跟着
   `currentColor` 在暗色纸面与打印之间切换，位图做不到；而扉页一年只印一次
   体积，值得为它换真实光影。
2. **连续动图走双层**：HTML 里滚动逐帧 + 悬停循环播放，PDF 里退化成整条画好的
   静态胶片条。理由：滚动时间线（`animation-timeline: view()`）只在浏览器存在，
   Chromium 打印与 `prefers-reduced-motion` 必须仍有完整可读的图。

## 3. 手绘通道（已实现）

```
正文 ```ill 围栏（一行画名）
  → core.extract_illustrations：换成 @@ILL:<sha1(file|line|name)[:12]>@@
  → render.drawing_slots：题注 = 上方最近的 H2（与 Mermaid 同规则）
  → render.plate_repl：art.drawing(name) 原样内联，根元素带 seq 类即判为连续
  → render.illu_figure：<figure class="illu illu-{line|seq}" id="fig-{uid}">
  → audit：未解析的绘图占位 = 构建失败
  → style.py：ink-draw / ink-pop / 逐格滚动 range / 悬停 ink-cycle
```

契约（改任何一条都要先看测试）：

- 画名只允许 `[a-z0-9][a-z0-9._-]*`，一个围栏一个名字；名字之外的内容报错。
- 图版预算 `art.PLATE_BYTES = 20 KB`，章徽预算 6 KB；`ill` 围栏不计入代码语言。
- 手写 SVG 禁止 `id=`、`href=`、`url()`、`<script>/<style>/<iframe>`，必须用
  `currentColor`，必须有 `viewBox`——由 `art._read` 把关，画廊与正文共用同一道闸。
- 是否连续由图自己声明（根元素 class 含 `seq`），正文不写「如何播放」。
- 带 `pathLength="100"` 的形状走 `ink-draw`；真实单位 `stroke-dasharray` 的元素
  不得再带 `pathLength`；`<g class="frame">` 必须是 svg 的第 1～4 个子元素，
  装饰性连线追加在帧组之后，否则 `nth-child` 的滚动 range 会错位。
- 悬停循环必须同时写 `animation-timeline:auto` 与 `animation-range:normal`，
  且规则要排在 `nth-child` 滚动 range 之后（同特异度，靠源序取胜）。
- 滚动逐帧整段包在 `@media screen and (prefers-reduced-motion: no-preference)`
  + `@supports (animation-timeline: view())` 里：打印与降级动态拿不到动画，
  于是 PDF 里就是一条画完的静态胶片，不需要额外的打印样式。这一层是决策 2
  的兑现处，`test_build_contracts.py` 目前只对章徽那一层有断言，图版这一层的
  断言要在下一轮补上。
- 实物位图只允许 `photo()` 产出 data URI，单张 300 KB 封顶；外链一律视为
  离线保证的破口。通道已存在：成品页面里的 img 标签只要 src 指向
  `illustrations/` 前缀，就由 `render.inline_images` 就地改写，前缀不对直接
  `BuildError`；缺的是有来源有许可的图，以及扉页／篇题刻接受位图的那一个槽位。

## 4. 铺开顺序

先给「最长正文墙」和「最讲顺序」的单元配图，而不是按章号平铺：

| 优先级 | 单元 | 画什么 | 类型 |
| --- | --- | --- | --- |
| 1 | ch02 对话循环 | 提问→工具→回填→再提问的循环胶片 | seq |
| 2 | ch01（zh 墙 2515／en 墙 7011） | 五大原则的手掌／工作台式示意 | line |
| 3 | ch04 权限与审批 | 判定分叉：一次询问、一次放行、一次拦截 | seq |
| 4 | ch07 钩子 | 事件在管线上被拦下的时刻 | seq |
| 5 | ch13 上下文压缩 | 压缩前／压缩中／压缩后的三格 | seq |
| 6 | 扉页 + 4 篇题刻 | 实物位图（古车、驿道、工坊、灯下） | photo |

每加一张图的固定动作（缺一即视为未做完）：

1. 画 SVG 进 `yuyu-book/illustrations/`，过 `art._read` 的闸；
2. 正文加 `ill` 围栏 + 一句引子，双语同步，严格一行换一行；
3. 平移 `glosses.json` / `manifest.json` 的 `file:line` 锚点并逐条验证术语仍在原位；
4. 更新 `scripts/build_illustration_gallery.py` 的 `ORDER` / `WIDTH` / 双语题注，
   重跑画廊、入门读本、门户三个生成器；
5. 同步 README / STRUCTURE / CREDITS 的图数声明（`test_docclaims` 会核对）；
6. 五道闸全绿后，账本 `revisions.json` 记一轮，数字当场重测。

## 5. 与文字迭代的关系

两类工作共用一套纪律：一行换一行、锚点不动、双语同步、五道闸
（`build.py --check` 两路、构建器测试、仓库 tests、`check_book.py`、
`check:diagrams`）。

文字侧的余量从此只由一个脚本口径：`python scripts/measure_translationese.py`。
它只数 `check_book.prose_walls` 认定的正文墙——表格、代码围栏与 Mermaid 源
都不算；`--sample=N` 打印的就是「真的计入了行数」的原句和命中片段，判伪不必
再另起一套正则。2026-11-01 首次全量测得：

| 语言 | 形状 | 行 | 处 | 另列（不改） |
| --- | --- | --- | --- | --- |
| 中文 | 「被x」 | 132 | 162 | 术语式样 15（被动的／被调用者一类） |
| 英文 | be+过去分词、情态+be+过去分词 | 554 | 801 | 系词用法 54（is based on 一类） |

最集中的几处：中文 ch12 14 行、ch07 13 行、ch13 11 行；英文 ch12 51 行、
ch02 50 行、ch03 42 行、ch11 40 行。一轮只挑一族、只动一个单元，改完当场重跑
脚本，把新数写进 `revisions.json`。

需要明说的一件事：账本里第三十九、四十轮的数（如「全书由 31 行降到 27 行」）
用的是当时临时的正则，今天已经无法复现。从第四十一轮起，凡落在 commit message
与 `revisions.json` 的数字，都必须能由这个脚本重新打印出来——复现不了的数就当
错数处理，不复用。

## 6. 不做的事

- 不新增第 21 个单元，20 单元的契约不动。
- 不引入任何外部运行时资源、生成产物或来源不明的第三方素材；位图必须登记
  来源与许可（`CREDITS.md` §三），只接受 MIT／Apache 一类宽松许可。
- 不为「以后可能用到」预留抽象；`ill` 通道只服务手写矢量，位图只服务扉页与题刻。
