# Task M3 · 插画管线与入门分册同步（ILLUST-SYNC）

结论一句话：**reader / gallery 用当前 dist 重生后 `git diff` 为空**（内容等同 HEAD，
差在行尾：见第二节的更正），
Mermaid 双语各 160 相等，42 张 SVG 零违约，art 两套测 15 + 18 全绿。
K4 那条「插画再生与 prompts 手册可能过期」里，**「再生」这半边当场证伪**
（没过期，重生不出来差异）；**「prompts 手册」这半边确有一个可见缺口**，
不在 SVG 里而在手册的计数边界上，已就地登记（见第四节）。

执行时间 2026-11-04，全部命令与退出码：

```
python scripts/bookctl.py build --product book --lang both   -> 0  （由 ci-local-yuyu 的构建那步承担，12:33/12:41 落盘）
python scripts/build_beginner_reader.py                      -> 0  24 stations × 2 语言
python scripts/build_illustration_gallery.py                 -> 0  42 figures, 190558 字符
python -m unittest discover -s yuyu-book/tests -p "test_art.py"           -> 0  Ran 15, OK
python -m unittest discover -s yuyu-book/tests -p "test_illustrations.py" -> 0  Ran 18, OK
```

---

## 一、Step 1：先建书，再重生 reader

`build_beginner_reader.py:411` 读的正是 `yuyu-book/dist/yuyu-agent-harness-{zh,en}.html`，
所以顺序不能倒：dist 不是新的，重生就是在拿旧正文验旧 reader。
本机 dist 由 12:21 起跑的 `ci-local-yuyu.ps1` 里的
`build --product book --lang both --pdf` 刷新（zh 12:33 / en 12:41），之后才跑重生。

两份输出都是 24 站（15 章 + 前言 + 4 附录 + 封面 + 按语等按 `LANGS[lang]["order"]` 计），
`build_beginner_reader.py:341` 有一句硬检查：**dist 里缺锚点就 `SystemExit`**。
它没抛，说明本轮改过的正文（35 个文件、+668/−117）里，reader 要抓的那些锚点一个没丢。

## 二、Step 2：docs diff 记录（关键结果是「没有 diff」）

```
$ git diff --stat docs/
 docs/YUYU-OVERHAUL-SPEC.md                     | 416 +++++++++++++++++++++----
 docs/illustration-prompts.md                   |  26 ++
 docs/portal.html                               |  36 ++-
 docs/yuyu-overhaul/BASELINE.md                 | 132 +++++++-
 docs/yuyu-overhaul/NOTE-ROOT-OVERHAUL-SPEC.md  |  26 +-
 docs/yuyu-overhaul/TRANSLATIONESE-CURRENT.json |   2 +-
 docs/yuyu-overhaul/check_block_markers.py      | 177 ++++++++---
 7 files changed, 690 insertions(+), 125 deletions(-)
```

**`beginner-reader.html`、`beginner-reader.en.html`、`illustration-gallery.html`
不在上面这张表里。** 它们的 mtime 都被推到 11-04 12:43（确实重写过），内容等同 HEAD。

> **更正一处措辞（13:20 复查时发现的，原先这里写的是「逐字节相同」，不准确。）**
> 盘上这三个文件比 HEAD 的 blob **各多 475 / 471 / 309 字节**，多出来的恰好等于各自的行数：
> 这台机器 `core.autocrlf=true`，`write_text()` 默认把 `\n` 翻成 `\r\n`，而仓里存的是 LF。
> 所以「字节级」是**不同**的，相同的是**经 Git 行尾归一之后的内容**——`git diff` 空、
> `git status` 不列它们，才是这里真正成立的证据，也是 `pages.yml` 那条
> `git diff --exit-code docs/` 真正在比的东西（CI 在 Linux 上检出 LF、生成器也写 LF，
> 两边口径一致，所以这个 CRLF 只会出现在 Windows 工作区，不会让 CI 红）。
> 三个数字（89227 / 87773 / 197677）是**盘上大小**，不是 HEAD blob 大小；
> HEAD 对应的是 88756 / 87298 / 197368。

为什么正文改了 668 行而 reader 一字不变？不是脚本没干活，是它的取材面不在这次改的面上：
reader 的句子取自 dist 里的通俗层区块（`plain` / `analogy` / `take` / `gain` / `bound` / `quiz` / `note`），
这些文本来自 `manifest.json` 的 `guides` 与 `glosses.json` 的 `plain`。本轮对
`manifest.json` 的改动是 **0 增 6 删**，删的 6 行全是块 ID 引用
（`ch01.agent-harness`、`ch05.b-336ab860`、`apxc.b-2ab3b354`、`apxc.b-fcee4414`、
`apxd.b-788aedcf`、`apxd.b-e618e111`），`question`/`deliverable`/`boundary`/`plain`
四条字段一行没动（用 `git diff -U0 HEAD -- yuyu-book/manifest.json` 滤这四个键名，零命中）。

这条恰好把 K1/K4 里那句「入门分册与整书 guides **可能**漂移」收敛成可复核的口径：
**漂移的方向不是靠人记，是靠 `git diff --exit-code docs/`**（见第五节怎么在本地模拟它）。

## 三、Step 3：Mermaid 双语对拍

SPEC 那条一次式的口径是「四个部分目录 + `附录/` + `00-前言.md`」对「整个 `en/`」。
两种口径都实跑（`^````mermaid` 逐文件计数）：

| 口径 | zh | en |
| --- | --- | --- |
| SPEC 原式（en 含 `en/README.md`） | **160** / 20 文件 | **160** / 21 文件 |
| 只算 20 个正文单元（en 排掉 README） | **160** | **160** |

`en/README.md` 一条围栏都没有，所以两种口径同为 160，`BASELINE.md:10` 的
「zh=160 en=160」不需要改数。**Expected 达成，M1 没有增删图。**

第三道独立印证：`check_bilingual_parity.py`（M8 建）逐 unit 数出来的 mermaid 数
zh 160 / en 160，与这里的目录级扫法来自不同实现，两个数撞上了。

## 四、Step 4 + 手册那一格：42 张图与 26 条提示词的边界

SVG 契约（`yuyu-book/yuyu_book/art.py` 硬要求：单 svg + viewBox、至少一处
`currentColor`、禁 id/href/url/script/style）对 42 张全量复核：
**`currentColor` 齐、无 `id=`、无 `script`，违约 0 张**；机器口径另有
`test_art.py` 15 测与 `test_illustrations.py` 18 测，同日实跑均 OK。
所以 SPEC Files 里那句「仅当 SVG 违约时改 `illustrations/*.svg`」的条件不成立——
**这一轮一张 SVG 都没动**。

真过期的是手册的**计数边界**：`docs/illustration-prompts.md` 标题写「26 份手绘插图」，
盘上有 42 张 `.svg`，差额是 16 张章内插图（`ch01-five-pillars` … `ch15-harness-wheel`），
它们不走「生图提示词 → 手写 SVG」这条管线，手册里既没有它们的条目、也没有一句话说明为什么没有。
读者只能看到 26 vs 42 这个对不上的数。

处置（写在手册里，**没有**替那 16 张编造双语提示词——编就是凭空造真源）：
新增一节「手册不覆盖的另一类：16 张章内插图」，内容全部可复核——

- 16 个文件名逐条列出，并写明 26 + 16 = 42 与盘上计数对齐；
- 它们的取舍记录在 `.superpowers/sdd/2026-11-02-illustration-rollout/`
  （`progress.md`、`fix-round-1-section.md`），改画先读那两份；
- 两类图共用同一套 `art.py` 契约，附本次 42/0 违约的实测；
- 将来若真为某张章内插图补提示词，要连标题里的「26 份」一起改，不能只改正文。

同时在手册开头那句「本书 26 份插图…」后补一行指针，指向文末这节，
免得只读前言的人把 26 当成全书图数。本次对手册的净改动：**+26 行，删 0 行**。

## 五、pages 契约：本地能模拟哪半边，不能模拟哪半边

`pages.yml:79` 是 `git diff --exit-code docs/`——先重建、再看 committed docs 有没有变，
变红意味着「 shipped 副本过期」。

- **能本地证的一半**：重建后三份再生品零 diff（第二节）。这正是那条 CI 步骤要防的事，
  在本机已经成立。
- **不能本地证的一半**：`git diff --exit-code docs/` 是**路径级**的，它不区分
  「再生品」和「人写的文档」。写下本文件这一刻，`docs/` 下是
  **7 个已跟踪文件被改 + 27 项未跟踪**（未跟踪里 11 项在 `logs/`、16 项不是，本文件算一个），
  7 个已跟踪改动里有 5 份是人写的账（SPEC、BASELINE、手册新节、NOTE-ROOT、护栏脚本），
  1 份是再生品但本轮该变（`portal.html`），1 份是度量快照（`TRANSLATIONESE-CURRENT.json`）。
  所以这条检查在**提交之前**本地必定红，且这个红是设计使然：CI 跑到那一步时工作树是干净的，
  只会看见重建差异。
  把 `--exit-code` 放宽成「只看三份 html」来凑绿，就是篡改契约，**没做**。

## 六、M3 验收

- [x] ILLUST-SYNC 有记录（本文件）；reader/gallery 已再生（12:43 重写，内容与 HEAD 相同）
- [x] Mermaid 双语计数一致（160 = 160，两种口径 + 一个独立实现三方对上）
- [x] **未** commit/push（本轮零 `git add`；`docs/` 的 7 改 + 27 未跟踪原样留着等人拍板）

## 七、仍然开着的（M3 没做的）

1. **`docs/portal.html` 的改动没有再生口径**。它由 `scripts/build_site_portal.py` 手写驱动，
   本次只是随 M5 的门面改动变了 24/12 行（新增第 5 张卡片）。`pages.yml:103` 把它建到
   `site/index.html` 而不是 `docs/`，所以 `git diff --exit-code docs/` **校不到它**——
   committed 的 `docs/portal.html` 与脚本输出是否一致，目前没有机器闸。要不要补一条，
   归 M9 的移交建议。
2. **16 张章内插图没有双语提示词条目**——本轮登记了边界，没有补条目（见第四节理由）。
3. **站点发布契约（pages 真绿）留待 push 之后**，与 K6/K12 同一格。

## 八、配图缺口实测（17:00，为「多增加手绘」做的前置测量，不动图与正文）

用户 16:4x 转向「先把 omp 和 claude 的知识补全」，并点名用 `yang0/handraw-style` 多增加手绘。

### 1. 三层配图的真实覆盖（拿 16:28 那份成品数标记，不采信自报）

| 层 | 解析入口 | 御舆 zh | omp zh |
|----|----------|---------|--------|
| 章徽 emblem | `build.py:413` → `art.emblem(u.id)` → `illustrations/<unit-id>.svg` | **20** | **0** |
| 篇题刻 headpiece | `frontmatter.py:143` → `art.headpiece(part["id"])` → `part-<id>.svg` | **4** | **0** |
| 章末驿卒 keeper | `build.py:439` → `art.keeper()` → `keeper.svg` | 20 | **39（共用御舆那枚）** |
| 正文插图 ill | ill 围栏 → `art.drawing(name)` → `<name>.svg` | **16** | **0** |

计数方式：在两份 dist 里分别数 `<span class="ch-emblem"`、`<div class="pd-art"`、`<div class="keeper">` 三个串。
omp 得 `0 / 0 / 39`，御舆 zh 得 `20 / 4 / 20`（`yuyu-book/dist/yuyu-omp-zh.html` 19,974,383 B，16:28 那份）。

### 2. omp 缺的是**两层全部**，不是几张

- `manifest-omp.json` 单元 id 共 **39 个**：`omp-ch01`…`omp-ch33` + `omp-apxa`…`omp-apxe` + `omp-front`；盘上同名 `.svg` **0 个**。
- 篇 id 共 **7 个**（`omp-p1`…`omp-p7`，标题依次 打地基 / 上手 / 工具箱 / 上下文与记忆 / 扩展 / 实战 / 精通），
  对应 `part-omp-p1.svg`…`part-omp-p7.svg`，同样 **0 个**。
- 对齐御舆的程序化图层 = **46 张新图**（39 章徽 + 7 题刻），每张 ≤6,000 B、`currentColor` 描线。
- 正文插图是另一件事：omp 现在 **0 个 ill 围栏**（御舆 zh/en 各 16，落在 15 个文件里——`03-工具系统` 独占 2 处）。
  omp 的 `langs` 是 `["zh"]`，所以它只有一侧；**别把御舆的双语相等门禁套到 omp 头上**，那条对 omp 是空集。

### 3. 每加一张图要过的闸（这才是「工程量」的答案）

装载器本身（`art.py:30-57`）：单个 `<svg>` 带 `viewBox`、必须出现 `currentColor`、禁 `id=` / `href=` / `url(` / `<style>` / `<script>`，
章徽与题刻 ≤ `MAX_BYTES` 6,000 B，正文插图与扉页 ≤ `PLATE_BYTES` 20,000 B。
`test_art.py:49,59` 与 `test_build_contracts.py:602` **遍历 `illustrations/*.svg` 全量**，新图一进目录就被这三处审。

| 闸 | 位置 | 加一张图要动什么 |
|----|------|------------------|
| 磁盘计数 | `test_docclaims.py:71 drawings()` = `glob("*.svg")` 的条数 | `README.md:127` 那句「全书另有 42 份手写线描图」与 `STRUCTURE.md:122` 的 42 分项表，**两处都要跟着改数**，且句子改了措辞让正则找不到也算失败 |
| 画廊 | `scripts/build_illustration_gallery.py:24 ORDER` + `:48 PLAIN` | 新图要进 `ORDER` 并配一句白话题注，否则不进 `docs/illustration-gallery.html`（该文件是已跟踪产物，须重生） |
| 装配 | `build.py:270-276` | `want_emblems = 本产物单元 id 中磁盘有图的个数`，与页面里实际出现的 `<span class="ch-emblem"` 数必须相等——图放对了 id 就自动成立，放错名字不会报错但也不会出现 |
| 手册 | `docs/illustration-prompts.md` | 每张新图一条中英双语提示词（现有 26 条目的格式：隐喻 + 中文提示词 + English prompt） |
| 双语 | `check_bilingual_parity.py` | 只对**御舆**的正文围栏计数相等生效；给御舆加正文插图必须 zh/en 同加 |

### 4. 更正我本轮口头说过的一句话（它没进过任何账本）

我在对话里说过「盘上 42 张 SVG 里 ≥26 张未被引用」——**错**，且错得典型：只数了 ill 围栏，
忘了章徽/题刻/驿卒/扉页这四类是**程序按 id 直接取**的（`emblem(u.id)`、`headpiece(part_id)`、`keeper()`、`cover_plate()`）。
正确的账：`42 = 20 章徽 + 4 题刻 + 1 驿卒 + 1 扉页 + 16 正文插图`，与 `STRUCTURE.md:122` 的分项**逐条对上**，孤儿图 **0 张**。
复核：`grep -rn "未被引用\|没被引用\|orphan" docs/ README.md` 至写本节时 0 命中——错话只停在对话里，账本干净。

### 5. 许可与署名（点名外部风格包的必查项）

上游 `handraw-style` 是 **MIT 且附署名要求**：用了就要可见地 credit `yang0` 与仓库链接。
本仓已有署名位——`docs/illustration-prompts.md:3-4`「以开源项目 [yang0/handraw-style](https://github.com/yang0/handraw-style) 的画风体系绘制」，
**要求已满足**，新增条目沿用同一句。基准配方也早已写在同一页：`FD-001 · Dynamic East-Asian Ink Editorial`，
`C-32 炭黑` 统领、`C-15 朱砂` 只作章印与书级点缀。
两条红线：上游 `images/` 那 48 MB 参考图**不进仓**（垫图只在本地生图时临时引用）；
该 skill 自带的「分享到网站/论坛」路由**不在本轮授权范围**，不自动触发。
### 6. 本轮实际落笔（17:06）：只写了提示词，一张图都没画

`docs/illustration-prompts.md` 追加一节「第二分册 omp · 7 幅篇题刻」，实测：

- 体积 **35,338 → 49,550 B（+14,212）**，行尾 **1,015 CRLF / 0 个裸 LF**（本文件全量 CRLF，追加沿用同一行尾）。
- 新增 `### omp ` 小节 **7 个**，每条给「隐喻 + 中文提示词 + English prompt」三段式，与既有 26 条同格式。
- 配方按手册「为新增章节续画」模板**实时研判**得出，不是抄映射表：画风 `FA-010 · Tom Gauld | Geometric Literary Deadpan`、
  主题色 `C-32 炭黑` 统领 + `C-35 石板灰` 作第二层、`C-15 朱砂` 仍只作书级点缀。三个编号与作者名逐条核过上游
  `references/styles.json`（367 条）与 `references/colors.json`（36 条）。
- **`yuyu-book/illustrations/` 一个字节没动**：盘上仍是 **42** 张 `.svg`。

因此第 3 节那四道闸**一道都没触发**，这正是反向验证：`README.md:127` 与 `STRUCTURE.md:122` 的「42」仍然为真、
gallery 的 `ORDER` 不必加项、`check_bilingual_parity` 无新围栏可数。实跑两道门禁确认没把声明改脏：

```
python -m unittest discover -s yuyu-book/tests -p "test_docclaims.py"     -> Ran 9 tests, OK
python -m unittest discover -s yuyu-book/tests -p "test_art.py"            -> Ran 15 tests, OK
```

（`test_docclaims` 用 `glob("illustrations/*.svg")` 现数，所以「只写提示词不动图」这条路**不可能**让 42 失真；
一旦开始放 SVG，README 那句、STRUCTURE 那张表、gallery 的 `ORDER`+`PLAIN` 三处必须同一轮改完。）

**还欠着的**：7 幅题刻的 SVG（`part-omp-p1..p7.svg`，各 ≤6,000 B）与 39 枚章徽（`omp-ch01..33`、`omp-apxa..e`、`omp-front`）
一张都没画；画之前要先定一件事——**omp 的图放哪个目录**，见下面第 7 节。

### 7. 两条路（实测出来的，不是猜的）

| | A：共用 `yuyu-book/illustrations/` | B：omp 自己一个目录 |
|---|---|---|
| 代码 | **零改动**（`art.py:16` 的 `ART_DIR` 是模块常量，两册都从这里取） | `ART_DIR` 得按 product 派生：`art.py` 5 个入口 + `test_docclaims.py:71` 的 `BOOK_DIR / "illustrations"` 都要跟着改 |
| 文档计数 | `drawings()` 数的是**目录里全部** `.svg`，42 → 88 会把 `README.md:127` 那句和 `STRUCTURE.md:122` 的分项一起打穿，两处必须同轮改 | 御舆那两处**保持 42 不变**，omp 的张数另找地方写（`omp/BUILD.md` 归 omp SPEC） |
| 画廊 | 46 张 omp 图会混进 `docs/illustration-gallery.html`（御舆读者侧的成品，README:17 直接链它），`ORDER`/`PLAIN` 要么加 46 条题注、要么显式不收 | 画廊天然只有御舆那 42 张 |
| 契约文本 | 与 `STRUCTURE.md:170` 明写的「`illustrations/` 那批章徽与题刻都是按 **book** 的骨架钉死的」相冲 | 与那句话相顺 |
| 既成事实 | omp **已经在共用**这个目录：成品里 `keeper.svg` 内联 39 次（16:28 那份 `yuyu-omp-zh.html`） | 走 B 就得先回答「驿卒跟谁走」——复制一份、还是留一条显式的共享白名单 |

推荐 **B**：两册的读者契约是分开的（御舆对外发布、omp 还在 `0.1.0-wip`），把 omp 的 46 张塞进御舆那三处被测试盯住的「42」里，
换来的只是省下一次 `ART_DIR` 派生；而 `test_product_isolation` 的整条立意就是「两个产品不许互相写对方的东西」。
代价要认下来：B 需要**先解决驿卒**——最省事的做法是 `art.py` 读图时「先查本产品的目录，查不到再回落共享目录」，
这样 omp 的章徽/题刻必须自带、驿卒继续共用，行为与今天完全一致，只是新图不再混进御舆的计数与画廊。

两条路都**不需要**动御舆正文；区别只在「omp 的图落在哪」与「哪几处声明要跟着改数」。

## 九、路线 B 落地（18:2x–18:5x）：omp 有了自己的图目录，7 幅题刻已上盘

第 7 节推荐的那条路（B）按你「同意继续」执行。落地的不是「按 product 派生 `ART_DIR`」，
而是更省的一步：**装载顺序**。

### 1. 代码实际改了哪两处（第 7 节那张表把工程量估高了）

| 处 | 改动 | 体积 |
|---|---|---|
| `yuyu-book/yuyu_book/art.py` | 新增 `OMP_ART_DIR = …/illustrations-omp` 与 `_search_dirs()`；`_read()` 与 `missing()` 改为按 `[OMP_ART_DIR, ART_DIR]` 逐个查 | 5,484 → **6,138 B**（+654） |
| `yuyu-book/tests/test_art.py` | `Loader.setUp/tearDown` 除 `ART_DIR` 外还要把 `OMP_ART_DIR` 沙箱化——否则沙箱里的「缺图」会被真目录里同名的 omp 图答上 | → **6,322 B** |
| `yuyu-book/tests/test_product_isolation.py` | 新开 `OmpArtTray` 四道断言（`:111`） | 5,618 → **7,612 B**（+1,994） |

第 7 节写的「`art.py` 5 个入口 + `test_docclaims.py:71` 都要跟着改」不成立：`emblem()` /
`headpiece()` / `keeper()` / `cover_plate()` / `drawing()` 五个入口全都只经由 `_read()`，
所以真正的装载口只有 **1 个**，加上给 `build.py` 那道装配数护栏用的 `missing()`，共 **2 个函数**。
`test_docclaims.py` 也**不需要**为「42」改任何东西——它数的是 `illustrations/*.svg`，新目录是兄弟不是子集，
盘上实测御舆那 42 张一张没动（`ls yuyu-book/illustrations/*.svg | wc -l` = **42**）。
`photo()` 仍只认 `ART_DIR`：omp 的正文 JPG 由 `render.inline_images()` 按单元目录解析，与 `ART_DIR` 无关。

### 2. 一次查找为什么够用，以及它靠什么撑着

不需要 product 参数，因为两册的 id 命名空间不重叠：御舆 20 个单元 + `p1..p4`，
omp 39 个单元（`omp-front` / `omp-ch01..33` / `omp-apxa..e`）+ `omp-p1..omp-p7`，交集实测为空。
这句话现在是**测试**而不是口头假设——`OmpArtTray` 里两条：
`test_the_two_volumes_name_no_unit_or_part_alike`（id 不重叠）与
`test_the_two_trays_declare_no_drawing_of_the_same_name`（两个目录不重名，重名会让 omp 目录盖掉御舆的图，
而 `build.py` 那两道计数护栏照样平衡，读不出来）。驿卒 `keeper.svg` 留在共享目录，靠回落命中：
本轮实测 `yuyu-omp-zh.html` 里 `kp-art` 仍是 **39** 次内联，与 16:26 那份同数。

### 3. 7 幅题刻（`part-omp-p1..p7.svg`）

盘上 **7 个文件 / 6,222 B**（含行尾），逐幅：`p1 771`、`p2 961`、`p3 847`、`p4 1,099`、
`p5 1,020`、`p6 806`、`p7 718`——单幅上限 6,000 B，最胖的一幅用了 **18%**。
`viewBox="0 0 200 140"`、`currentColor` 描线、`pathLength="100"`、无 `id=`/`href=`/`url(`/`<style>`，
与御舆那 4 幅题刻同一条格式（对照 `illustrations/part-p4.svg`，798 B）。
风格按第 6 节写好的配方执行：`FA-010 · Tom Gauld | Geometric Literary Deadpan` 的几何冷面 +
`C-32 炭黑` 统领、`C-35 石板灰` 用 `opacity` 落地（书里 `.pd-art{color:var(--bronze)}`，
第二层色靠透明度而不是第二个颜色值，这正是 `currentColor` 契约能同时管屏幕/暗色/纸面的原因）。
七幅的母题分别对应七篇：一圈三点（模型＋工具＋循环）、终端窗口与进门箭头、工具挂架、
被两侧挤压的容器（上下文压缩）、三个插座与一只待插的件、越过墙到旗子的路线、
一叠规则被一条斜线贯穿。

### 4. 成品侧的实测

`python scripts/bookctl.py build --product omp --lang zh` 退出 0，自报
「39 units, 1 plates, …, **0 emblems, 7 headpieces**, 39 keeper notes」；
`yuyu-omp-zh.html` **19,974,383 → 19,980,906 B（+6,523）**，页内 `<div class="pd-art"` 由 **0 → 7**。
这 6,523 个字节能算平：七幅 SVG 去掉行尾共 **6,208 B**，加外层
`<div class="pd-art" aria-hidden="true">` + `</div>`（45 B）× **7** = **6,523 B**。
配对也是逐条验的，不靠总数相等：把成品里每个 `<section class="part-divider" id="omp-pN">` 切出来，
断言它内联的正是 `illustrations-omp/part-omp-pN.svg` 的字节、且不含其余六幅——七条全 True。

**目视验证的做法与它的局限**：20 MB 的单文件页在 headless Edge 里 25 s 预算内渲染不出内容
（截出来是一张纯色图），所以改成把成品里的 `<style>` 两块（80,793 B）与七个 divider section
原样抽出来单独渲染——用的是**同一份 shipped CSS 与同一份 section**，不是复刻的 mock。
逐篇截图确认七幅都落在篇号与篇名之上、尺寸约 `min(13.5rem,62%)`、暗色下自动改墨。
（先出的那张 9,000 px 长图按 1,300 px 等分裁是**错的**——divider 不等高，裁出来的图把
p4 的容器配到了「第五篇 扩展」头上；改成「一节一页」逐张截才对。）

### 5. 这一轮过的闸

```
python -m unittest discover -s yuyu-book/tests   -> Ran 514 tests, OK      # 本轮前 510
python -m unittest discover -s tests             -> Ran 39 tests, OK
python scripts/bookctl.py check --fast           -> check fast: 6 steps passed, exit 0
python scripts/check_book.py（在 --fast 内）      -> 176 Markdown files, 321 Mermaid diagrams, 0 errors
```

两道红是**先红后修**的，过程记在 `ACCEPTANCE.md` 第 5 节第 12 条（隔离闸 grep 的是
`manifest-omp` 这个字符串，正确反应是搬家不是加白名单；套件条数同时是 `revisions.json`
里中英各一句的读者可见宣称，510 → 514 就地修订顶部 0.3.5 条目）。
`scripts/check_artifact_claims.py` 仍 **exit 1**（CI Noto 505/536 与本机雅黑 518/569 之差，设计如此）。

### 6. 还欠着的

- **39 枚章徽**：`omp-front`、`omp-ch01..33`、`omp-apxa..e` 一张未画，成品实测 `ch-emblem` = **0**。
  画之前 `OmpArtTray` 只钉了题刻那一层，章徽层没有断言——**缺 39 枚不会让测试变红**，
  只会让 `build.py` 的自报数停在 0，所以这条缺口以本文件为准，别当成已完成。
- **正文 `ill` 围栏**：omp 正文仍是 0 个围栏（第 2 节那三层里的第三层）。
- 每放一张 SVG 的连带清单（第 3 节那四道闸）在本轮只走了「新目录」这一支：
  `STRUCTURE.md:123` 新增一行并由 `test_docclaims.py:84 omp_drawings()` 钉住 **7**；
  御舆侧 `README.md:127`、`CREDITS.md`、gallery 的 `ORDER`/`PLAIN` 三处**不需要动**，
  因为 gallery 的 `on_disk != set(ORDER)` 那道自检只数 `illustrations/`（实测 42 张，未变）。
  omp 自己的图**没有**进 `docs/illustration-gallery.html`——那是御舆读者侧的成品。

### 7. 同一轮的文档侧同步（把「还没画」那句改掉）

图画上盘，说它「还没画」的句子就变成假话。这一轮改的四处都是**现状声明**，不是历史读数：

| 文件 | 字节 | 改了什么 |
|------|------|----------|
| `docs/illustration-prompts.md` | 49,550 → **50,290**（+740） | 标题「26 份手绘插图」→「御舆 26 份 + 第二分册 omp 7 幅篇题刻」；omp 那节标题去掉「**SVG 尚未落成**」、正文三段「还没画 / 画完那天要改 README 与 STRUCTURE 的张数」换成落点与实测字节，并写明这一批走独立目录、**没有**打穿御舆那三处 42 |
| `omp/BUILD.md` | 4,394 → **4,750**（+356） | 「0 emblems，0 headpieces」→「0 emblems，**7 headpieces**」；PDF 行 321 → **323 pages**（并把 08:20 那次降为历史读数）；套件 510 → **514**；新增「第三轨」一条说明章徽层仍缺 39 枚 |
| `docs/yuyu-overhaul/PDF-PAGES.md` | 24,623 → **26,424**（+1,801） | 表尾追加 18:48 / 18:50 两行 + 一行「御舆四份本轮未重建」（sha16 与 mtime 一并记）；「与基线的对照」那张「现在」列表 omp 321 → **323**、+83 → **+85 页**，御舆两行字节改为本机当前实测 |
| `docs/yuyu-overhaul/BASELINE.md` | 26,148 → **27,546**（+1,398） | 「Dist · 当前值」表补第六次构建（17:35–17:44）四行，并写明**第七次只跑了 omp**，所以那四行仍是御舆当前值、omp 的读数一律在 `PDF-PAGES.md` |

行尾照旧逐文件核对：`docs/illustration-prompts.md` 全量 **1,022 CRLF / 0 裸 LF**（原 1,015，多的 7 行是这一节自己），
`omp/BUILD.md` **65 CRLF / 0 裸 LF**，其余改到的 SPEC、ACCEPTANCE、PDF-PAGES 与本文件都是 **LF only**（现数），
`BASELINE.md` 这次现数是 **267 CRLF**，与本轮开始时手记的「LF only」不符，写脚本前以盘上为准才没把 CRLF 文件改成混合行尾。

手册那条计数边界顺手复核了一遍，`grep` 现数：「## 手册不覆盖的另一类」之前 `### ` 条目 **26** 条（20 单元章徽 + 老驿卒 + 4 篇题刻 + 扉页车图），
`### omp ` 条目 **7** 条，全文 132 处 ``` 围栏成对——「26」这句从此不再是「整本手册只有 26 条」的误读。

重跑本轮全部读数的命令：

```bash
ls yuyu-book/illustrations/*.svg | wc -l                       # 42（御舆，未变）
ls yuyu-book/illustrations-omp/*.svg | wc -l                  # 7
python - <<'PY'
import pathlib
t = pathlib.Path("yuyu-book/illustrations-omp")
print(sum(p.stat().st_size for p in sorted(t.glob("*.svg"))), "bytes on disk")
print(sum(len(p.read_text("utf-8").strip()) for p in sorted(t.glob("*.svg"))) + 7*45,
      "= 应等于 omp HTML 的增量")
PY
python -m unittest discover -s yuyu-book/tests -p "test_product_isolation.py"   # 13 tests OK
```

## 十、39 枚章徽落地（19:0x–20:1x）：omp 的章首不再是空白带

第 9 节第 6 小节的欠账（「**39 枚章徽**：`omp-front`、`omp-ch01..33`、`omp-apxa..e` 一张未画」）本轮清掉。
生成器与对照表都在仓库外：`D:\Temp\User\draw_omp_emblems.py`（40 个条目、39 个 uid，`--write` 落盘）与
`D:\Temp\User\omp_emblem_sheet.py`（拿成品 CSS 排版）。

### 1. 盘上现数

```
yuyu-book/illustrations-omp/  46 份 SVG = 39 枚章徽（19,920 B）+ 7 幅题刻（6,222 B），共 26,142 B
最大一枚                    766 B（omp-ch29）= 6,000 B 预算的 12.8 %
最小一枚                    229 B（omp-ch22，那枚拼图块线最少）
中位                        517 B（omp-ch12）
```

格式沿用房规一条不改：`<svg viewBox="0 0 64 64" fill="none" stroke="currentColor" stroke-width="2.2"
stroke-linecap="round" stroke-linejoin="round">`，每个描线 `path`/`circle` 带 `pathLength="100"`，
灰阶靠 `opacity`（必要时配更细的 `stroke-width`），实心点写 `fill="currentColor" stroke="none"` 且**不**带
`pathLength`；单行、结尾 CRLF。**不挂**御舆那套 `a-*` 动画类——成品里的画出规则是
`.ch-emblem path[pathLength],.ch-emblem circle[pathLength]`，本来就不分产品，挂了反而多一层耦合。

### 2. 判好坏靠的是眼睛，不是测试

20 MB 的单文件页在 headless Edge 里排不出来，所以对照表的做法是：从 `dist/yuyu-omp-zh.html` 里抽出成品自带的
两份 `<style>`（80,763 B），把每枚章徽塞进真正的 `.ch-head-row`（印 + 标题 + 章徽），按 4.6rem 与 3.2rem 各排一遍，
再 headless 截图看。**看出来的问题共 9 枚**：batch 1 的 `ch01`（箭头太弱）、`ch04`（折线是噪声、点看不见）、
`ch05`（插脚糊成一团）、`ch06`（箭头压到框）已在上一轮改过；本轮看 `emblems_b2.png` 又抓到
`ch08`（页外一颗孤点，读起来像脏点）、`ch09`（外框 + 划掉线互相压）、`ch15`（两排点，3.2rem 下只剩一团）、
`ch18`（火星与框脱节），以及 `emblems_b4a.png` 里的 `ch21`（钩没有眼、螺母太小）。改法分别是：
`ch08` 改成放大镜压在页角、`ch09` 改成 diff 块（减一行加一行，去掉外框）、`ch15` 改成「上面摊开的四行压成下面两行粗的」、
`ch18` 改成八角火星 + 框住的关键词、`ch21` 加钩眼并放大螺母。
这些改动没有一条是测试逼出来的——`art._read()` 只保证尺寸与禁令，画得读不读得出来它管不着。

一处工具误差要记下：对照表里那格「印」用的是 `uid[-1].upper()`，而 `build.py:404` 对章用的是 `digits.zfill(2)`，
所以表上第 8 章写作「8」、成品里是「08」（附录两边都是单字母，一致）。错的只是对照表的这一列，章徽本体不受影响。

### 3. 补的那道闸：空托盘以前不会红

`build.py:266` 的门是 `n_emblems != want_emblems`，而 `want_emblems = len(ids) - len(art.missing(ids))`——
一枚章徽都没有时两边都是 0，**0/0 照样通过**。这就是第 9 节第 6 小节说的「缺 39 枚不会让测试变红」。
本轮在 `test_product_isolation.OmpArtTray` 加了绝对的那一半：

```python
def test_every_omp_unit_opens_with_its_own_emblem(self):
    ids = expected_ids(self.omp)
    self.assertEqual(len(ids), OMP_UNITS)
    self.assertEqual(art.missing(ids), [], "omp units opening without a drawing")
```

于是该文件 13 → **14 tests**，构建器套 514 → **515**（`Ran 515 tests in 228.687s`，两条红：
`STRUCTURE.md: claims ['7'], the data says ['46']` 与 `revisions.json: '514' != '515'`，都是预期的连带，已改）。
通用套 `Ran 39 tests OK`。

### 4. 字节能算平（这次连余数都没有）

先做个反证：把托盘临时换成「只有 7 幅题刻」的探针目录（`--out-dir`，不碰 `dist/`）重跑 HTML，
得到 **19,980,906 B / sha16 `72dc22d002656d94`**——与第 9 节记的那份 18:48 成品**逐字节相同**。
也就是说 18:48 那次构建里 `39 emblems` 那格其实是 **0 emblems**，batch 1 的 8 枚是在那之后才落盘的。

然后：

```
20,002,729 − 19,980,906 = 21,823
39 个 <span class="ch-emblem" aria-hidden="true">…</span> 实测合计 = 21,792
omp-front 第一次拿到 <div class="ch-head-row">…</div> 外壳        =     31
21,792 + 31 = 21,823 ✓
```

页内标记同步核对：`ch-emblem` 0 → **39**，`ch-head-row` 38 → **39**，`ch-seal` 38 → **38**
（前言本来没有印，是靠章徽才第一次套上 head-row）。`revisions.json` 那两处 514→515 不在这个差里：
探针是在改完之后跑的，两边都带 515，说明 omp 的 HTML 根本不渲染那份修订页——这条是实测副产物，记下来免得下次又猜。

PDF：`30,671,601 → 30,726,600`（**+54,999 B**），页数 **323 → 323 不变**，书签 **49 → 49 不变**，
sha16 `e27c16c56c8ef6d6 → 43486e9b27ade561`。纸面抽检：PyMuPDF 渲染第 89 页（第 8 章章首），
放大镜压在页角那枚章徽确实印出来了，2.4rem 下读得清；`89 / 323` 的页码也说明它没把后面顶页。

### 5. 文档侧同步（把「7 份」那句改掉）

| 文件 | 改了什么 | 字节 |
|------|----------|------|
| `STRUCTURE.md` | `illustrations-omp/` 那行「7 份」→「46 份」，并写清两道门各管一半 | 45,676 B（253 CRLF） |
| `yuyu-book/revisions.json` | entries[0] 的「构建器测试 514 项全绿」/“514 builder tests green” → 515 | 268,693 B，宽度不变 |
| `yuyu-book/tests/test_product_isolation.py` | 新增 `test_every_omp_unit_opens_with_its_own_emblem` | 8,121 B |
| `omp/BUILD.md` | 「0 emblems」→ 39、产物表与第三轨写明 46 份、套数 514→515 并补上「再加 1 条」那一步 | 4,750 → **5,013 B**（67 CRLF，纯 CRLF） |
| `docs/illustration-prompts.md` | omp 那一节从「7 幅篇题刻」扩到「7 题刻 + 39 章徽」，新增一小节写清**章徽这一层没有生图配方**、房规、39 句隐喻与字节 | 50,290 → **54,995 B**（1,087 CRLF / 0 裸 LF，132 处围栏仍成对；`### omp ` 条目仍是 **7**——新小节故意不叫 `### omp …`，免得那个读数被误读成 8 条配方） |
| `docs/YUYU-OVERHAUL-SPEC.md` | M9 Step 4 补一条 20:0x 脏区读数，并把 18:5x 那条降级为「被取代」 | 95,084 → **97,424 B**（+2,340；1,318 行全 LF、0 CRLF） |
| `docs/yuyu-overhaul/ACCEPTANCE.md` | 第 4 节同一动作：18:5x 改为「当时的当前值，20:0x 已取代」，新增 20:0x 为当前可引用值 | 64,788 → **66,544 B**（+1,756；560 行全 LF、0 CRLF） |

脏区读数（本轮最后一次 = 20:0x，`git log --oneline -1` 仍是 `951c0ef`、ahead/behind 仍是 `0 0`）：
`git status --porcelain | wc -l` = **486**，`git status --porcelain -uall | wc -l` = **531**；
折叠口径的桶仍是 `A ` 293 + `AM` 30 + ` M` 62 + `??` 101 = 486，展开口径 `??` 101 → **146**。
486 与 18:5x 那次相同，是因为 `yuyu-book/illustrations-omp/` 整个目录仍未跟踪、被折叠成**一条** `?? `；
39 枚新章徽只体现在展开口径上：492 → 531，差 **39**，与落盘文件数逐一对上。
复现命令：`git status --porcelain | cut -c1-2 | sort | uniq -c` 与 `git status --porcelain -uall | grep -c illustrations-omp`（46）。
20:0x 把那两条台账改完之后又数了一遍：**四个桶逐桶与 18:5x 相同**（486 / 531 / `-sb` 非空 487 三值也都没动）——本轮写过的 10 个已有文件此前全都已在各自桶里，唯一的新增是那 39 枚 SVG，而它们落进的是一个本来就整目录未跟踪的目录，所以折叠口径连涨一条都不会涨。这是第 9 节末句「只要往仓库放一个新目录，折叠就回来」的另一半：**放在已有未跟踪目录里的新文件，连折叠都不触发**。
同一轮还撞了一次旧陷阱（`ACCEPTANCE.md` 第 4 节早就写过）：`git status --porcelain | grep -c ' omp/'` 现数 **365**，而 `git status --porcelain -- omp/ | wc -l` 是 **366**，差的还是 `A  "omp/00-前言.md"` 那行——非 ASCII 路径被 git 加了引号，前缀从 ` omp/` 变成 `"omp/`。**数目录一律带 pathspec**，`grep` 前缀不作准。

### 6. 本轮全部读数的复测命令

```bash
ls yuyu-book/illustrations-omp/omp-*.svg | wc -l              # 39
ls yuyu-book/illustrations-omp/*.svg | wc -l                  # 46
python - <<'PY'
import pathlib, statistics
t = pathlib.Path("yuyu-book/illustrations-omp")
em = sorted(t.glob("omp-*.svg"), key=lambda p: p.stat().st_size)
sz = [p.stat().st_size for p in em]
print(len(em), sum(sz), "min", sz[0], em[0].name,
      "max", sz[-1], em[-1].name, "median", statistics.median(sz))
PY
grep -o '<span class="ch-emblem"' yuyu-book/dist/yuyu-omp-zh.html | wc -l   # 39
python - <<'PY'
import fitz
d = fitz.open("yuyu-book/dist/yuyu-omp-zh.pdf")
print(d.page_count, len(d.get_toc()))          # 323 49
PY
python -m unittest discover -s yuyu-book/tests  # Ran 515 tests, OK
```

### 7. 仍然开着的

- 章徽的**内容**没有第二人复核过：9 枚的修改判据是我对着截图说的「3.2rem 下读不读得清」，
  这条判据本身没进任何测试，换个人可能给出不同的答案。
- ~~御舆那 20 枚章徽本轮一张没动，两册章徽的「手」是否已经分叉，没人比过~~ → 20:1x 比过了，见下面第 8 小节。
- 3 个共享术语（Agent Harness / Main Loop / Subagent）仍在等人拍板。
- `check_artifact_claims.py` 仍按设计 exit 1；SPEC `:207` 那格（`git add`）在用户的提交窗口之前不会勾。
- 第 8 小节比出来的一件事**没有**转成改动：御舆侧 4 份附录章徽的根 `stroke-width` 是 2.1、其余全是 2.2。
  统一它要重排御舆成品（本轮只建过 omp），所以只记录、不动手。

### 8. 两册章徽的「手」比过了（20:1x，纯测量，一张图都没动）

同一条 `viewBox="0 0 64 64"` 那一层，御舆 20 枚（`front` + `ch01..15` + `apxa..d`）对 omp 39 枚：

| 度量 | 御舆 20 枚 | omp 39 枚 |
|------|-----------|-----------|
| 份数 / 总字节 / 中位字节 | 20 / 17,248 / **785.5** | 39 / 19,920 / **517** |
| 根 `stroke-width` | 2.2 × 16、**2.1 × 4**（只有四份附录） | 2.2 × 39 |
| shape 总数 / 实心点 / 描线 | 192 / 43 / 149 | 226 / 16 / 210 |
| 带 `pathLength` 的描线 | 142 | 210 |
| `stroke-dasharray` | 7 | **0** |
| class 名（去重） | **45**（`a-*` 章级钩子 19 个 + 子动效 26 个） | **0** |

三条结论：

1. **「每个描线都带 `pathLength`」在两册都 100% 成立**，只是御舆的房规里虚线是例外。御舆 149 − 142 = 7 个缺口，
   逐个查证**正好就是那 7 根虚线**（`front` 1、`ch01` 1、`ch10` 4、`ch14` 1），非虚线且无 `pathLength`
   的描线条数两册都是 **0**。`style_css.py:348` 那句注释是这条例外的出处：动画只挂 `pathLength="100"`，
   虚线保住真实单位的 dash 节奏、改走 `ink-fade`。所以 142/149 与 210/210 两个比率不是分叉，是「御舆用虚线、omp 一根没用」。
2. **唯一的真分叉是 class 那一层，而且是上一轮定下的设计**：御舆带 45 个 class（19 个 `a-*` 是章级 hover 钩子，
   26 个是子动效名），omp 一枚都不带。两册共用同一条 `.ch-emblem path[pathLength],.ch-emblem circle[pathLength]`
   属性选择器，所以 omp 不挂 class 也照样自己画出来——第 1 小节末句写的就是这件事，本轮把它从「声明」变成「比过」。
3. **没有孤儿钩子。** 粗查 class 名在 `style_css.py` 里查不到规则的三个是 `march`（`front`）、`b1`（`ch11`）、`t1`（`apxb`），
   逐个看下去都是**同组第一个的记号**而非死钩子：`front` 写的是 `class="march m75"`，规则挂在 `.m75`
   （`style_css.py:447` `.a-front:hover .m75{animation:ink-march-75 …}`）；`ch11` 是 `blink b1` + `blink b2`，
   基类 `.a-plug:hover .blink` 管第一条、`.b2{animation-delay:.55s}` 管第二条；`apxb` 是 `tick t1/t2/t3`，
   基类 `.a-list:hover .tick` 加 `.t2`/`.t3` 两条 delay。也就是说这三条画面行为全部正确，只是名字不接规则。

复现（只读，不改盘）：

```bash
python - <<'PY'
import pathlib, re, statistics
book = ["front"] + [f"ch{i:02d}" for i in range(1, 16)] + ["apxa", "apxb", "apxc", "apxd"]
sets = {"book": [pathlib.Path("yuyu-book/illustrations") / f"{n}.svg" for n in book],
        "omp": sorted(pathlib.Path("yuyu-book/illustrations-omp").glob("omp-*.svg"))}
for label, files in sets.items():
    shapes = dots = pl = dash = orphan = 0
    for p in files:
        s = p.read_text(encoding="utf-8")
        for m in re.finditer(r'<(path|circle|line|polyline|rect|ellipse)\b[^>]*?/?>', s):
            tag = m.group(0); shapes += 1
            isdot = 'fill="currentColor"' in tag
            dots += isdot
            pl += 'pathLength' in tag; dash += 'stroke-dasharray' in tag
            orphan += (not isdot) and ('pathLength' not in tag) and ('stroke-dasharray' not in tag)
    sz = [p.stat().st_size for p in files]
    print(label, len(files), sum(sz), statistics.median(sz), "shapes", shapes,
          "dots", dots, "pathLength", pl, "dash", dash, "stroked-no-pl-nondash", orphan)
PY
grep -o 'class="[^"]*"' yuyu-book/illustrations-omp/omp-*.svg | wc -l   # 0 —— omp 这一层一个 class 都不带
```

御舆 20 枚的 `shapes 192 / dots 43 / pathLength 142 / dash 7 / stroked-no-pl-nondash 0`、
omp 39 枚的 `226 / 16 / 210 / 0 / 0` 应当逐字复现；复现不出来的那一位就是本轮比错了。


