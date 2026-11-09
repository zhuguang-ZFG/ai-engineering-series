# 参与修订

先读 [STRUCTURE.md](STRUCTURE.md) 了解仓库的两层契约：**Markdown 书稿是唯一内容源，构建器只读不写**；锚点、目录、图号、脚注、书签、页码都在构建时派生。书稿本身可以改，但改动只能由人决定——构建器永不回写正文，v0.3.1 里那三处自相矛盾的数字是人工核对后落的原稿修正，并由 `test_docclaims` 的门禁钉住（正文声明的总数必须等于它下面那张表/那张图）。本文讲环境、命令、改动流程和门禁。

## 1. 环境

```bash
# Node 22+（package.json 的 engines 要求 >=22），用于 mermaid 解析与图板渲染
npm ci                                  # 安装 mermaid 11.17.2 + jsdom 26.1.0

# Python 侧依赖（Markdown / Pygments / playwright / PyMuPDF / fonttools / Pillow）
python -m pip install -r yuyu-book/requirements.txt
```

`requirements.txt` 是从 `uv.lock` 导出的精确版本，不是手写的范围约束。升级依赖时改 `pyproject.toml`，然后：

```bash
uv lock
uv export --format requirements-txt --no-hashes --no-emit-project --no-annotate > yuyu-book/requirements.txt
python scripts/bookctl.py doctor    # 核对安装版本与 requirements/lock 一致
```

渲染 Mermaid 图版和打印 PDF 需要一个 Chromium 系浏览器。构建器按 **msedge → chrome → Playwright 自带 chromium** 的顺序自动探测，装了前两者之一就直接可用；都没有时：

```bash
python -m playwright install chromium   # 注意是 Python 包提供的 CLI，不是 npx
```

也可以显式指定：`--browser "C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe"`。**一个坑**：走自动探测分支时构建器会带上 `--allow-file-access-from-files`，而用 `--browser` 指定可执行文件时不会带；如果图板报"harness failed to load"，先去掉 `--browser` 让它自动探测。只想跑通构建而不渲染图版，可以用 `--mermaid source`（完全不启动浏览器，图源以代码块排版）。

## 2. 常用命令

日常入口是 `bookctl`：

```bash
python scripts/bookctl.py doctor       # 一次列全 python/node/浏览器/字体/依赖/写权限
python scripts/bookctl.py check --fast # 依赖 + 源码装配 + 两套单测 + 内容/图语法 + 视频 + 产品幂等（PR 层）
python scripts/bookctl.py check --full # fast + 渲染装配 + 双语 PDF
python scripts/bookctl.py build --product book --lang both --pdf
python scripts/bookctl.py deps         # requirements.txt 与 uv.lock 对照
python scripts/bookctl.py clean        # 删除 yuyu-book/dist（不依赖 rm -rf）
```

调试单个阶段也通过同一入口，不再调用已删除的 `yuyu-book/build.py`：

```bash
python scripts/bookctl.py build --check               # 临时装配两语版，不写 dist、不出 PDF
python scripts/bookctl.py build --lang zh             # 只出中文版 HTML
python scripts/bookctl.py build --lang en --pdf       # 英文版 HTML + PDF
python scripts/bookctl.py build --regen-index         # 重建索引后继续完整构建
```

仓库根 `Makefile` 只是上面命令的薄包装；Windows 没有 make 时直接跑 `python scripts/bookctl.py ...`：

```bash
make            # 列出可用目标
make doctor     # 环境报告
make book       # 双语 HTML
make book-pdf   # 双语 HTML + PDF
make check      # = check --fast
make check-full # = check --full
make index      # --regen-index
make clean      # 删除 yuyu-book/dist
```

两个变量可以覆盖：`make PYTHON=python3`（Linux CI 用）、`make BOOK_LANG=zh`（只出一语；刻意不叫 `LANG`，那是 shell 已经在导出的 locale 变量）。

改动前后都建议跑一遍既有内容门：

```bash
python scripts/check_book.py                    # 相对链接落点、围栏闭合、Mermaid 里的字面量 \n、图版间距
npm run check:diagrams                          # 用锁定的 mermaid 解析器逐图 parse
python -m unittest discover -s tests            # 仓库现有单测（star history 等）
python -m unittest discover -s yuyu-book/tests  # 构建契约：manifest/来源/围栏与图题/交叉引用/审计/版式 WCAG
```

`yuyu-book/tests` 不需要浏览器、不渲染图、不写书稿；它把 `--check` 抓不到的东西钉死：附录 D 表格到索引的映射、`MermaidBlock.line` 必须仍是文件里的行号（图题靠它对位）、`第 N 章` 在 `<code>/<pre>/<svg>` 子树里不许被加链、配色 token 的 WCAG 4.5:1 对比度。Windows 控制台若因中文断言报编码错误，加 `PYTHONIOENCODING=utf-8`。

还有一道只在 Book CI 里跑的门：`python scripts/check_artifact_claims.py`。中文版 README 与 `en/README.md` 的「离线整书」各引了一遍 PDF 页数与单文件 HTML 体积，八项都核对。页数跟着构建机那套中文字体走（CI 装 Noto CJK，换一台装了微软雅黑的 Windows 两份都排得更长，README 里照实写着那台机器的数字），所以本地对着自己的 `dist/` 跑必红，只有指向同一次 CI 刚排出来的产物才绿；单文件 HTML 与字体无关，体积那四项本地也能核。数字对不上、产物缺失、或者那两句话被改写成别的说法，都退出非零。

## 3. 新增或修改一章

1. **写 Markdown**，中英文两份都要动。
2. **首行 H1 必须能被构建器识别**（`core.normalize_h1()` 的模板，围栏内不算）：
   - 中文：`# 前言` / `# 第 2 章：对话循环 -- Agent 的心跳` / `# 附录 A：源码导航地图`
   - 英文：`# Foreword` / `# Chapter 2: The Dialog Loop -- The Agent's Heartbeat` / `# Appendix A: Architecture Navigation Map`
   - 冒号可省；正文里的 ` -- `（两侧空格）会被规整成破折号 `—`，连续空格会被压成一个。
   - 找不到顶层 H1，或第一个 H1 不匹配上面任一模板，直接 `BuildError`。
3. **在 `yuyu-book/manifest.json` 登记**：`parts[].units[]`（或 `appendices[]`）里加 `{id, zh, en}`；`id` 同时就是成品里的锚点（`#ch09`、`#apxd`），改 `id` 等于改全书链接目标。两个语言路径都必须存在，否则 `validate_configs()` 报错。
4. **补罗盘条目** `guides[<id>]`：`question` / `deliverable` / `boundary` 三个字段，每个都要 **zh 与 en 双语非空**。校验要求 guides 恰好覆盖所有单元（多一个少一个都不行），`audit` 还要求成品里的罗盘卡数量不少于单元数。
5. **挂来源** `guides[<id>].sources`：填 `sources.json` 里已有的 id，写错 id 会被 `unknown source id` 拒绝。这些 id 在书里渲染成"来源锚点"chip，指向 `#source-<id>`。
6. **补通俗层**（可选但强烈建议）：`guides[<id>].plain` 是一句章首导读带，`guides[<id>].analogy` 是紧跟其后的“打个比方”。两者都要 zh / en 双语，且必须同时给 `guides[<id>].plain_evidence` —— 一组稳定块 ID，例如 `ch03.tool-generics`，指回书稿里真正支撑这句话的块。块不能是代码围栏，且必须含登记过的词形；导读带要求中英两侧都有证据。两语不共用标记时分别登记两个 ID，不要把中文证据当作英文证据。旧 `文件:行号` 只供历史迁移读取，不再新增。
7. **画一枚章徽**：`yuyu-book/illustrations/<id>.svg`（新篇再加 `part-<篇id>.svg`）。不画不会失败——构建器只统计"磁盘上有的图是否都上了页面"——但每个单元的标题行就空着一格。规格见第 5.2 节。
8. 顺手更新 `yuyu-book/revisions.json` 的版本说明（zh/en 各一份）。

## 4. 新增一条来源（`yuyu-book/sources.json`）

以来源 id 为键的字典条目。id 必须匹配 `^[a-z0-9][a-z0-9-]*$`。

**必填非空字段**：`title`、`authority`、`kind`、`url`、`snapshot`、`accessed`、`license`、`scope`。

**门禁**（`core.validate_configs()`，不满足即构建失败）：

- `url` 必须 `https://` 开头。
- `kind: github` → `pinned` 里必须有 `tag` 或 `commit` 之一。
- `kind: npm` → `pinned.version` 必填。
- `kind: community` → 必须 `normative: false` 且有 `accessed`；若给了 `pinned.commit`，必须是完整 40 位 SHA（长度校验目前只对 community 生效）。

**约定**（构建器不检查，但请遵守）：

- GitHub 条目按现有做法写完整 40 位 SHA，而不是分支名——`main` 会移动，叙述就无法回溯。现有 6 条 github 条目全是完整 SHA。
- `snapshot` 写清读取时间与核对方式（例："2026-10-25 读取该 commit 下的 CHANGELOG.md，HTTP 200，首条版本号 2.1.310"）；`accessed` 写日期；`scope` 写这条来源用来核对全书的哪类叙述。**只登记书目元数据，不转载来源正文**——这也是 `license` 字段一律写"链接引用，不转载"的原因。
- Anthropic 的源码、文档、博客与 changelog 一律链接引用，不复制进书稿或成品。
- 不要把 GPL 系许可的资产（图、字体、代码片段）打包进书的单文件成品：本书文字是 CC BY-NC-SA 4.0，非商业 + 相同方式共享的条款与 copyleft 强传染条款混装会两头都不干净。

## 5. 书稿行文规范

这些规则决定了成品能不能过审计、以及排版是否成立。

**中文排版**

- 全角标点，中英文之间留半角空格；术语首次出现给中英对照。
- 正文不使用 emoji。图注编号、罗盘卡与提示框的图形标记（✦ ⚠ ↗ ◎ ※）由渲染器注入，不需要也不应该在 Markdown 里手写。
- 表格里的排版符号（✓ ✗ ★ ☆）可以用。

**代码围栏**

- 必须闭合，未闭合会报 `unclosed code fence at line N`，并且审计会以"`<pre>`/`<code>` 内嵌块级元素"再抓一次。
- **声明语言**：` ```json `、` ```typescript `、` ```bash ` 等。围栏 info 串会成为代码板右上角的语言角标（`data-lang`）；不写语言的围栏拿不到角标，且按纯文本高亮。围栏数量与渲染出的代码块数量必须一一对应，否则报"rendered code blocks but N source fences"。
- Mermaid 围栏固定写 ` ```mermaid `。图题取自动态扫描的**最近上层 H2**，所以每张图前要有一个 H2 标题；没有就回落成"架构示意"。图内换行用 `<br/>`，写字面量 `\n` 会被 `scripts/check_book.py` 拦下。
- **图与图之间的距离**：`scripts/check_book.py` 按 manifest 的两语正文，量相邻两个视觉断点（图版、表格、代码围栏）之间那段纯文字有多长；超过 `WALL_CEILING`（当前中文 2885、英文 8049 字符）就报错，同时把每种语言最长的三处打在输出末尾，当作下一轮的点位清单。这两个数是**当轮实测的最大墙**，不是许可额度——墙只许变矮：补图之后顺手把上限改低到新实测值，放宽上限得在提交信息里说清为什么。
- **图的宽度**：Mermaid 按自己的坐标排版，正文栏只有 635px。viewBox 宽超过 1150 单位的图版会被 `floor_wide_svg()` 钉上 `min-width`（最宽 2600px），屏幕上横向拖动阅读、图题带"可横向拖动"提示，打印时归零回到整页可见。所以画超大依赖图前先想清楚：横向铺开 = 读者要拖，宁可拆成两张 H2 下的小图。
- **图在纸面上的尺寸**：纸面没有滚动条，只有两块可用地——竖版版心 176×245mm（665×926 CSS px）与横版折页 170mm 高（993×642 CSS px）。构建时 `plate_cap()` 给"很高、按 6pt 字号底线缩放后正好还放得进栏宽"的图写一条 `--plate-cap`（150–245mm），让它独占版面而不是被压小——成品里中文版抬了 6 张、英文版 10 张；`plate_landscape()` 把"横过来才读得清"的图（竖着不足 6pt、横着能到 5pt 且好上一成半）挂上 `landscape` 类，独占一张 `@page plate-landscape` 横向 A4——中文版 18 张、英文版 25 张，一张图一张纸。折页**不写** `--plate-cap`：横版纸面只有 170mm 高，图版吃满 165mm 就会把图题挤到下一张纸上。两头都够不着的极端长条仍留在正文流里，纸面上就是小：中文版还剩 1 张（3725×1330 单位，约 2.4pt），英文版 3 张（2.4–3.3pt）。这几个数是量成品得来的，不是契约：`grep -c '<figure[^>]*landscape' yuyu-book/dist/*.html` 数一遍，PDF 里横过来的纸页与它一一相等，改图之后要跟着改这段。**HTML 才是全保真产物**，这类图请引导读者在屏幕上横向拖开看。
- **三个会把整本书的图打崩的写法**：别给 `.diagram-frame` 或图版容器加 `width:fit-content`——mermaid 的 SVG 根节点写的是 `width="100%"`，百分比宽度在 fit-content 父级里塌成 0，159 张图会集体消失（`test_build_contracts` 里有一条负向断言盯着它）；别加 `filter:`——打印引擎会把滤镜子树光栅化，图里的字退化成像素（PDF 里选不中、搜不到），文件体积还能翻倍；也别在 `figure.landscape` 上写 `break-after:page`——命名页面本身就会结束这一张纸，两个都写会在每个折页后面多出一张空白。
- **图的颜色**：优先不写颜色，`mermaid.py` 的 `THEME` 会把无主节点排成书色。已经写了 `classDef`/`style` 的图也不必回改正文——构建时 `reink_colors()` 按色相把 fill/stroke/color 重染进 `BOOK_FAMILIES` 七组书色（蓝→sky、绿→jade、橙黄→brass、红→cinnabar、紫→plum、近白→card、其余→neutral），角色区分保留，色板统一。写新图时按语义选色即可，别指望某个具体十六进制出现在成品里。

**引用与链接**

- 跨章引用直接写"第 9 章""附录 B"（英文写 `Chapter 9` / `Appendix B`），构建时自动加链（覆盖第 1–15 章与附录 A–D）；调试时可加 `--no-autolink`。
- 不要在正文里写指向 `.md` 的相对链接——书稿之间的互指应通过"第 N 章"表达，否则审计报 `residual .md links`。
- 不要手写锚点、图号、脚注编号：它们全部派生自 Markdown 标题与链接顺序。
- 外链写成普通 Markdown 链接即可，构建器会自动加上标编号并在单元末尾生成"引用链接"清单。

**提示框（callout）**

以 `> **标签：** 正文` 开头的引用块会被识别成对应色板的 callout，标签必须命中内置映射（括号说明会被剥掉后比较）：

| 标签 | 类型 |
|------|------|
| 最佳实践 / 正确做法 / 推荐做法 | tip |
| 反模式警告 / 危险 / 注意 | warning |
| 交叉引用 / 交叉引用提示 | info |
| 设计洞察 / 原理 | concept |
| best practice / correct approach | tip |
| anti-pattern warning / warning | warning |
| cross-reference / extended reflection / practical application scenarios | info |
| memories that should be saved | tip |
| memories that should not be saved | warning |
| design insight | concept |
| learning objectives / reference answer(s) / reference answer hints | note（硬编码兜底列表） |

命中不了的标签会保持成普通引用块，不会报错——所以想真正出框，请照抄上表的标签写法。

**双语同步**

`en/` 下的英文镜像与中文逐单元对应，章节标题模板不同但结构一致；只改中文不改英文会让两语版的图数、脚注数、索引词条数对不上。英文书稿不得夹带汉字，唯一例外精确到附录 D 术语表的第二列（中文译名）；`test_manifest` 会扫描全部英文单元，定义列或正文里的残留都会按文件与行号报错。

### 5.1 通俗层：白话注、导读带、阅读路线

通俗层是构建时叠在书稿上的一层，**从不回写 Markdown**。四个落点：

**术语白话注**（`yuyu-book/glosses.json`）一条一个术语：`term.{zh,en}`、`forms.{zh,en}`（正文里要匹配的表面写法，大小写与连字符照抄）、`plain.{zh,en}`（一句能懂的话）、`analogy`（可选比方）、`priority`、`evidence`。只有 `priority: "core"` 的词会在正文首现处画虚线，而章末面板列的就是这批画了线的词——两处是同一批，构建时断言，不存在「只进面板不上正文」的中间档。`"extra"` 的词两者都不沾，只在附录 D 可查。一个单元最多 22 个新词，超了构建失败——那时把最通用的词降成 `extra`，而不是删掉解释（本书正是这样给 `Agent Harness` 与主循环腾出位置的）。

**导读带与比方**在 `guides[<id>].plain` / `.analogy`，配 `guides[<id>].plain_evidence`。长度上限（超出即 `BuildError`）：导读带 zh 60 字 / en 170 字符，比方 zh 52 / en 160；浮窗里的白话 zh 40 / en 130，比方 zh 44 / en 130。

**阅读路线**（`yuyu-book/reading-paths.json`）按单元存一个小节顺序的位置列表，取值 `start` / `core` / `deep`（成品里渲染成"起步 / 主干 / 进阶"）。长度必须等于该单元实际渲染出的 `<h2>` 数：加了小节忘了同步，构建会直接报错，而不是把徽盖到别的小节上。

**按语**（`yuyu-book/notes.json`）以单元 id 为键，`{zh, en}` 各一句，由坐在章末车辙上方的老驿卒说出来，书末「按语集」再把二十条按阅读顺序收成一页。门禁是 `plain.validate_notes()`：中文 ≤36 字、英文 ≤130 字符，英文里不许夹汉字，二十个单元缺一条或多一条没主的都让构建失败；最要紧的是**术语锁**——句子里必须有一个 `glosses.json` 登记过的词形，而且那个词形要真的站在这一单元自己的 Markdown 里（构建器读的是源文件，不认「意思差不多」：第 1 章正文写的是 `Agent Harness`，写「智能体线束」会被退回；第 14 章写「规划模式」，写「计划模式」同样被退回）。旁白可以借书自己的比喻，不许凭空造词，也不许替书稿发表它没说过的论断——这是这一层与「白话不能以说错为代价」同一条底线的另一面。按语里也宁可不写数字：写了，`test_docclaims` 就要拿它跟仓库重算出来的值对表（`KEEPER_TOTALS` 目前钉住附录 B 那行的工具总数，要写别的数先去那里登记它从哪算来）；把数目写成汉字（「五十五」「六十多」）等于对一切门禁隐身——这本书正是被一个写成汉字的约数骗过的，所以这条规矩先管到自己这一层。

整层可以 `--no-plain` 关掉，用来对比开合前后的成品。

**底线：通俗不能以说错为代价。** 每一句白话都要能在书稿里指出行号；`validate_plain()` 会逐条核对证据指针落在代码围栏之外、那一行确实含登记过的词形，core 词条与每条导读带要求中英两侧都有证据。写不出证据的白话，就是还没读懂正文——先别写。

### 5.2 插图：章徽、篇题刻与扉页车图

- 位置与命名：`yuyu-book/illustrations/<unit-id>.svg`（20 枚章徽）、`illustrations/part-<p1..p4>.svg`（4 幅题刻）、`illustrations/cover.svg`（扉页那幅四马单辕古车，1000×470）、`illustrations/keeper.svg`（章末那枚老驿卒的斗笠与灯笼，64×64，每章内联一次，测试把它的体积钉在 3 KB 以内）。
- 章徽是 64×64 的单线小图、描边 2.1；题刻是 200×140 的小版画、描边 1.5；车图铺满整个版面、按层次分档描线（轮与辕 6.5/6，马身 4，辐与细部 1.2–2）。屏幕上题刻约 216px 宽、章徽 74px，三者不该用同一档笔画粗细。
- 硬约束（`art.py` 的装载器逐条把关，违反即构建失败）：只用 `currentColor` 上色——一张图同时管屏幕、暗色模式与纸面，不需要第二份文件；不得出现 `id=`（同一份图会被内联进单文件几十次，一个 id 就是一次重复 id，审计会在离图很远的地方炸）、`href=`、`url(`、`<style>`、`<script>`；必须有 `viewBox`；章徽与题刻单文件 ≤ 6 KB，车图另设 `PLATE_BYTES` 上限（它只出现一次，不必跟着章徽的预算走）。
- 语义优先于好看：图要能指着正文解释。第 12 章是桥（MCP 桥接外部协议），附录 C 是配电箱上的回路表（功能标志），第 1 章是辐辏之轮，第一部分是一整只三十辐的轮。看不出对应关系的图，等于给读者添噪声。
- 章徽落在章名右侧的标题行末尾（纸面上缩到 2.4rem），题刻落在篇分隔页起头、压在出血的车轮影子上。少一枚图不会失败，但那一格的标题行就空着——`app.build_edition()` 会按“磁盘上能装配的图”逐个对账。

### 5.3 断言账本：会随版本腐坏的句子

`yuyu-book/claims.json` 登记的是**会随上游版本变化**的断言：版本号、价格、数量、默认行为、性能数字与功能标志。这些句子写得再准，也只是在 `verified` 那一天准；账本让它们在过期时自己喊出来，而不是等读者发现。

一条 claim 的形状：

```json
{
  "id": "claude-code-baseline-version",
  "kind": "version",
  "risk": "high",
  "value": "2.1.310",
  "applies_to": "0.3.x",
  "source": "cc-release-v2-1-310",
  "verified": "2026-11-02",
  "review_days": 90,
  "status": "active",
  "zh": {"unit": "ch04", "block": "ch04.release-notes", "quote": "Claude Code 2.1.310（本书基线）"},
  "en": {"unit": "ch04", "block": "ch04.release-notes", "quote": "Claude Code 2.1.310 (this book's baseline)"}
}
```

规则：

- `id` 是小写连字符 slug，全书唯一；中英两侧共用这一个 id，不许各起一个。
- `kind` 取 `version` / `price` / `count` / `default` / `performance` / `flag`；`risk` 取 `high` / `normal`；`status` 取 `active` / `retired`。
- `value` 是这条断言的最小可核对 token（`2.1.310`、`$3.00`、`55`、`72%`、`PROACTIVE`）。它必须**同时**出现在 `zh.quote` 与 `en.quote` 里：只改一侧的译文，另一侧的门禁立刻失败。`quote` 必须是所在 block 的原文子串，不是改写。
- 引用块要先在 Markdown 里落一个稳定标记（`<!-- block: ch04.release-notes -->`），再把 `unit` / `block` 写进账本。自动生成的 `b-xxxxxxxx` 在两语版本里通常不同，所以两侧的 `block` 各写各的，`id` 必须相同。
- `source` 必须是 `sources.json` 已有的 id；`verified` 是复核日期（`YYYY-MM-DD`），`review_days` 是复查周期。
- `status: "retired"` 表示断言已不适用：账本不再追它的正文位置，但条目保留作历史。
- 过期语义：`risk: "high"` 的 claim 过期后，CI 记一条 warning，发布构建（`bookctl build`）直接失败；`risk: "normal"` 只记 warning。复核后改 `verified`，或把 `status` 改成 `retired`。

新增或修改一条断言时，先跑 `python -m unittest yuyu-book.tests.test_claims -v`；它会把「块不存在」「引文漂移」「一侧已改另一侧没改」「来源不存在」「过期」分条报出来。

### 5.4 事实、推断、教学简化与作者建议

同一页里混着四种语气，读者有权知道哪一句是上游说的、哪一句是本书的判断。四种句子用固定的开头或标签，不许含混：

| 类型 | 触发方式 | 写法 | 例子 |
|---|---|---|---|
| 事实 | 能在 `sources.json` 的固定链接或仓库代码快照里直接指到 | 陈述句 + 来源链接；会腐坏的数进 `claims.json` | 「Claude Code 2.1.310（本书基线）……」 |
| 推断 | 上游没有明说，是本书从代码形状、日志或行为反推出来的 | 句首写「推断：」/ `Inference:`，并给出证据链；结论用「更可能」「按当前实现」收住 | 「推断：这里先做 batch 再裁剪，是为了把两趟遍历压成一趟；证据是……」 |
| 教学简化 | 为了让读者先建立模型而故意省略的细节 | 段落或 callout 里写明「为讲解起见」/ `For teaching purposes`，并在后文指出简化掉的真实分支 | 「为讲解起见，这里把调度器当成 FIFO；真实实现里还有……」 |
| 作者建议 | 本书的工程意见，不是对 Claude Code 的描述 | 句首写「建议：」/ `Recommendation:`；不得用「Claude Code 会……」的口气 | 「建议：给写工具加白名单，而不是把所有 `Bash` 都放行。」 |

判定顺序：先问「上游文档/代码能不能直接指到」。能，是事实；不能但有条证据链，是推断；为了教学压掉了真实分支，是教学简化；与上游无关、只是本书希望你怎么做，是作者建议。

英文侧用同一套标签（`Inference:` / `For teaching purposes` / `Recommendation:`），与中文段落一一对应；不要只在中文里标。

### 5.5 结构差异规则与提交来源

`scripts/compare_legacy.py` 在读取构建产物前校验 `docs/baseline/legacy-v2-deltas.json`。
每条规则必须有路径、非空原因和真实的 7–40 位提交 SHA；该提交必须已存在于本地 Git 历史。
浅克隆缺少来源提交时先 fetch 对应历史，不用 `working tree`、版本标签或无关 SHA 代替。
提交存在只证明可定位；审阅者仍须核对该提交是否确实解释了这条内容差异。

匹配条件只能二选一：

- 数量变化：有限数值 `delta`，逐项核对增量；`kind: "len"` 表示列表长度变化。
- 版本、日期等精确变化：同时提供 `legacy` 与 `fresh`，任一端不同都不匹配。

不得混用两种条件，也不得只写一端或删掉条件让规则变成通配放行。
来源和结构错误以退出码 2 报出；合法规则仍未覆盖的产物差异保持退出码 1。
新增或修改规则、回归测试、runner 或 CI 策略仍须独立审阅；本地测试通过不等于受管验证已通过。

P5 内容的本地来源提交为 `6d4e3c0475d28d2ebb7630518a2f6721c9a01620`。
该提交包含双语练习、断言账本与构建前校验；不包含 P3 样式拆分、P4 产品适配或视频迁移。


## 6. 审计会拒绝什么

`yuyu-book/yuyu_book/audit.py` 在写出文件之前扫描整份 HTML，任一项不过即构建失败：

- 页内锚点指向不存在的 id（`broken anchors`）
- 同一 id 出现两次（`duplicate ids`）
- `<script>` 标签——成品必须无 JS
- 非 `data:` 的 `<img>`——离线保证
- 残留的 Markdown 围栏、未解析的 `@@MM:` 占位符
- `<pre>` / `<code>` 内嵌套了块级元素（未闭合围栏吞正文的典型症状）
- 闭合标签不配对
- 出现 `mermaid-missing`，或 SVG 数量少于预期（`--mermaid render` 才检查数量）
- `article` 数量或 `compass` 卡数量少于单元数
- 指向 `.md` 的残余链接

`audit()` 之后 `app.build_edition()` 还有五道对账：正文术语标记数必须等于章末面板行数；章末按语数必须等于“按语集”的行数、且等于该语言真有按语的单元数；导读带、罗盘、新词面板、tier 徽、章徽、题刻的数量要写进统计行并与预期相等；磁盘上每一枚能装配的图都必须真的上了页面；主题索引每一行必须恰有一枚页码空位，交给 PDF 阶段的 `PrintManifest.index_rows` 必须与页面行同名同序。通俗层自身的证据与长度规则由 `plain.validate_plain()` 与 `plain.validate_notes()` 在装配之前把关，见第 5.1 节。

PDF 阶段另有五道：命名目标缺失（`no destination found for ...`）、量页码那一趟没有目的地（`measuring print has no destination for ...`）、页码落进空位后翻页位置变了（`index folio(s) moved between the measuring print and this one`）、目录页码盖不全（`stamped only N of M contents rows`），以及目标文件被占用（`cannot replace yuyu-agent-harness-*.pdf`）——最后一道在 Windows 上尤其常见：阅读器、资源管理器的预览、或一个还开着 `dist/` 里 PDF 的校验脚本都会锁住文件；关掉它重跑即可，未盖章的 `*.raw.pdf` 会留在原地。索引页码要打印两趟，所以 `--pdf` 每种语言多花一趟打印的时间。打印出来的行内页码写回 `dist/` 里那份 HTML（屏幕上这一格本就隐藏，读屏也不会念出一个只有纸才知道的数）。

## 7. PDF 的机器相关性

`pdf.py` 打印 A4 后用 PyMuPDF 补书签、眉标、页脚页码与目录页码。眉标要量真实字宽，所以必须拿到一个本机 CJK 字体文件：`CJK_FONTS` 依次列 Windows（微软雅黑/宋体/黑体）、macOS（PingFang/Songti）与 Linux（Noto CJK，Debian/Ubuntu 上是 `fonts-noto-cjk`）的常见路径。中文版找不到任何一份就直接 `BuildError`，不会静默产出丢字的眉标；英文版走内置 Helvetica，无此要求。书签、页脚页码与目录页码本身用内置 Helvetica 数字，不受字体影响。因此装好字体的 runner 才能产出可交付的 PDF，`book.yml` 已为此安装 `fonts-noto-cjk`。

## 8. 提交前检查清单

- [ ] `python scripts/bookctl.py check --fast`（或 `make check`）通过；涉及图版/PDF 时用 `check --full`
- [ ] 中文与英文两份 Markdown 同步修改
- [ ] 英文书稿无汉字残留（附录 D 的双语译名列除外）
- [ ] 新单元已在 `manifest.json` 登记，且 `guides` 三字段双语齐备
- [ ] 新来源已过第 4 节的门禁，`snapshot`/`accessed`/`scope` 写实
- [ ] 动到通俗层时，每条新写的白话都带指得回书稿的 `plain_evidence` / `evidence`，中英两侧齐备；新单元有 `illustrations/<id>.svg`，并在 `notes.json` 里留一条按语（术语锁会替你核对那句里有没有本单元真正用过的词形）
- [ ] 若动到版本号，`revisions.json` 与 `manifest.json` 的 `version`/`date` 一致
- [ ] 版本、价格、数量、默认行为、性能数字或功能标志的增改，已在 `claims.json` 登记，且中英 `quote` 都含同一个 `value`（第 5.3 节）
- [ ] 事实、推断、教学简化与作者建议按第 5.4 节的标签分开，英文侧同标
- [ ] 章节增删导致 PDF 页数或单文件体积变化时，两份 README「离线整书」那一行的数字跟着改（Book CI 的 `scripts/check_artifact_claims.py` 会替你核对）
- [ ] 涉及显示问题，注明阅读平台、文件与复现步骤

CI 的书籍门禁统一在 `.github/workflows/book.yml`：`Fast` 运行源码装配、两套单测、内容、图语法、视频配置和产品幂等检查；`Full` 在 Fast 后运行渲染与双语 PDF；`Omp` 独立检查第二分册；`Bootstrap` 矩阵检查 Windows 与 Ubuntu 环境。`.github/workflows/release.yml` 负责版本一致性、最终装配、校验和与标签发布；`pages.yml` 负责站点部署。旧 `check-book.yml` 已退出。工作流存在不等于已执行通过，合并时必须核对同一候选提交的远端状态。架构边界见 [架构决策记录](docs/architecture-decisions.md)。

视频迁移的实物比较使用 `python scripts/bookctl.py video compare --help`。指定章节、长短格式、旧 SRT/VTT、新流程生成的 transcript JSON，以及独立渲染的旧新版视频；`--report` 写出带输入 SHA-256 的审阅结果。缺少任何一侧的视频或字幕证据都不能判为通过；抽样帧检查不代替 `video check --audio`。分句或时间轴有意变更时，保留差异报告并审阅，不能放宽比较阈值消除结果。示例及已知缺口见 [P6 验收续作](docs/migrations/spec-verification-2026-11-09.md)。

## 9. 反馈渠道

技术错误、案例补充、表达改进都欢迎走 Issue 或 PR，请附上章节、小节、建议改法与参考来源。涉及 Anthropic 官方行为变更时，优先给出可钉住的来源链接（带 tag 或完整 commit SHA）。
