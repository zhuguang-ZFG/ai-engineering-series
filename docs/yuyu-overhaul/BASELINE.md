# Yuyu (御舆) overhaul baseline

- Date: 2026-11-03 America/Adak
- Branch: p3-pages-split (dirty; no commit in this SPEC)
- Product: book · output_prefix: yuyu-agent-harness
- Units: 20 (front + ch01–ch15 + apxa–apxd)
- Manifest guides: 20 · Glosses terms (excl schema): 102 · Notes units: 20
  （2026-11-04 逐个重数：`glosses.json` 顶层 103 键、扣掉 `schema_version` = **102**；
  `notes.json` 顶层 21 键、扣掉 `schema_version` = **20**；`yuyu-book/illustrations/` 常规文件 **42** 个）
- Mermaid fences: zh=160 en=160（实测口径：四个部分目录 + `附录/` + `00-前言.md` vs `en/`）
- Illustrations files: 42（`yuyu-book/illustrations/`）
- Commit/push: DEFERRED
- Omp sibling present: `omp/`（M0 那一刻未跟踪；**2026-11-04 实测索引里已有 302 个 `omp/` 文件**
  → `git ls-files omp/ | wc -l`，见下「脏树快照」）· `make book-omp` / `book-omp-pdf` 可用

## Dist · M0 快照（2026-11-03 改造前，本机 Windows 字体，非 CI Noto）

| 文件 | bytes | pages | bookmarks | sha256(前16) |
|------|-------|-------|-----------|--------------|
| `yuyu-agent-harness-zh.html` | 5,740,160 | — | — | `c6c92fe9f02ba0ce` |
| `yuyu-agent-harness-zh.pdf` | 24,105,074 | 507 | 17 | `b435aa3d882306bb` |
| `yuyu-agent-harness-en.html` | 5,863,727 | — | — | `d421c4c85ccdc3f6` |
| `yuyu-agent-harness-en.pdf` | 12,358,555 | 558 | 17 | `d4693d50ae9465d7` |

README:110 已说明 CI（Noto CJK）为 505 页 / 35.0 MB 与 536 页 / 23.8 MB。本表钉的是 M0 那一刻本机
（Windows 雅黑）这一套；两者都不是「错」。

## Dist · 当前值（2026-11-04 17:35–17:44 第六次构建后，同一台机器；15:17–15:34 与 16:10–16:28 两组降为上一次快照）

M2–M4 的改动落地后重跑 `--product book --lang both --pdf`（这一次是 `docs/yuyu-overhaul/ci-local-yuyu.ps1`
里那条同名命令，见 Y-M4 Step 3），同一套 `stat` + PyMuPDF 口径量出来的是下面这组。
**看当前产物请以下表（与 `PDF-PAGES.md` 一致）为准，上面那张 M0 表只作起点对照**：

| 文件 | bytes | pages | bookmarks | sha256(前16) | mtime |
|------|-------|-------|-----------|--------------|-------|
| `yuyu-agent-harness-zh.html` | 5,781,712 | — | — | `10151855e39afac1` | 11-04 10:18 |
| `yuyu-agent-harness-zh.pdf` | 25,112,566 | **518** | 28 | `439f7b8fc0844954` | 11-04 10:20 |
| `yuyu-agent-harness-en.html` | 5,909,019 | — | — | `82f25301b449893f` | 11-04 10:27 |
| `yuyu-agent-harness-en.pdf` | 12,596,335 | **569** | 28 | `e8f173cd4eeba724` | 11-04 10:29 |
| `yuyu-agent-harness-zh.html` | 5,781,712 | — | — | **`52f1d5d715833575`** | 11-04 15:23 |
| `yuyu-agent-harness-zh.pdf` | 25,111,918 | **518** | 28 | `0da7c61e9a896f01` | 11-04 15:25 |
| `yuyu-agent-harness-en.html` | 5,909,068 | — | — | **`8b1b523234c350dc`** | 11-04 15:30 |
| `yuyu-agent-harness-en.pdf` | 12,596,557 | **569** | 28 | `a1a6160cc27bf614` | 11-04 15:31 |
| `yuyu-agent-harness-zh.html` | 5,783,290 | — | — | **`9846b04e60cdf413`** | 11-04 16:16 |
| `yuyu-agent-harness-zh.pdf` | 25,124,125 | **518** | 28 | `2bc3af3cc4347782` | 11-04 16:18 |
| `yuyu-agent-harness-en.html` | 5,911,553 | — | — | **`2df6c199f89eccaa`** | 11-04 16:23 |
| `yuyu-agent-harness-en.pdf` | 12,612,620 | **569** | 28 | `2a62a8d0eaaef32f` | 11-04 16:24 |
| `yuyu-agent-harness-zh.html` | 5,783,290 | — | — | `9846b04e60cdf413` | 11-04 17:35 |
| `yuyu-agent-harness-zh.pdf` | 25,124,773 | **518** | 28 | `df23582f9f5dc826` | 11-04 17:36 |
| `yuyu-agent-harness-en.html` | 5,911,611 | — | — | `01548f3f56891b50` | 11-04 17:43 |
| `yuyu-agent-harness-en.pdf` | 12,611,330 | **569** | 28 | `2d26efadbfde70db` | 11-04 17:44 |

**15:2x 这组不是新起点，是上面那条「HTML 拿 sha 当回归门」第一次真的抓到东西的记录。**
两份 HTML 的 sha 都变了，页数/书签一条没动，而两条差异都能归因到具体的输入文件（`find -newermt` 只列出
10:29 之后动过的构建输入：`yuyu-book/revisions.json` 10:49、四份 en 章节 11:52–11:53）：

- **zh：字节数一字不差（5,781,712）、sha 却变了。** 因为 `revisions.json` 那条中文改的是
  「构建器测试 **501** 项全绿」→「**510** 项全绿」——等长替换。实测成品里
  `510 项全绿` 命中 1 次、`501 项全绿` **0 次**，机制与「同长度、不同内容」完全对上。
- **en：+49 B。** en 侧那条同样等长（`510 builder tests` 命中 1、`501 builder tests` 命中 0），
  所以 49 B 只能来自 11:52–11:53 那四次 en 章节编辑里 10:27 之后新增的部分——那是 10:27 之后
  **唯一动过的 en 侧内容输入**，没有第二个候选。
- 两条 PDF 的 sha 变化是**预期内**的（元数据里带构建钟点，见下条），核对只看 bytes/pages/bookmarks。

所以上面 10:18–10:29 那四行现在的作用是「上一次构建的快照」，不再是「当前值」；
本表标题里的时间窗随之改为 15:17–15:34（第四次构建，`--product book --lang both --pdf`，exit 0，
日志 `logs/rebuild-book-pdf-20261104-151751.log`）。omp 那一份的当前读数在 `PDF-PAGES.md`（15:33/15:34，
321 页 / 49 书签 / sha `2fd8890af850…`）。

**16:10–16:28 第五次构建**（`--product book --lang both --pdf` 与 `--product omp --lang zh --pdf` 串行，
两条各 exit 0，日志 `logs/rebuild-{{book,omp}}-pdf-20261104-161046.log`）是本轮唯一一次「只改附录 D」的受控重排：
`附录/D-术语表.md` 与 `en/Appendices/D-Glossary.md` 各插 12 行，其余单元一字未动。
结果是 HTML 回归门第二次正常工作——两份 HTML 的 sha **都变了**且这次伴随字节变化（zh +1,578、en +2,485），
PDF 体积 +12,207 / +16,063，而 **518 / 569 页、28 / 28 书签、14 / 14 index folios 全部不动**。
同一轮里 omp 没改，两行**逐字节复现**（HTML 19,974,383、PDF 30,629,993、321 页 / 49 书签），
只有 sha 随 PDF 时间戳换了一个（`2fd8890af850…` → `fbefa3d8d8b6…`）——
**没改源的分册不产生字节差、改了源的分册不产生新页**，这两条同时成立才说明构建链是干净的。

**17:2x–17:4x 第六次构建**（`--product book --lang both --pdf`，exit 0）是为追一份不同源的成品而重排的，顺带给这条规则一个反向样本：zh HTML **字节数与 sha 都一字不差**（5,783,290 / `9846b04e60cdf413`，与 16:16 那行同一值），而同一册的 zh PDF 却 **+648 B**、页数 518 / 书签 28 / 14 index folios 全不动——**同一份 HTML 可以排出不同字节的 PDF**。en 那半边 `en/Appendices/D-Glossary.md` 40,038 → 40,075 B（把术语分歧表从 4 列压成 `check_shared_terms` 认得的 5 列），HTML **+58 B**、PDF **−1,290 B**，页 569 / 书签 28 同样不动。

**18:48/18:50 第七次构建只跑了 `--product omp --lang zh --pdf`**（七幅 omp 篇题刻上盘之后），所以**上面 17:35–17:44 那四行仍是御舆的当前值**，本表不跟着变；omp 那一册的读数一律在 `PDF-PAGES.md`（HTML 19,980,906 B / **+6,523**、PDF 30,671,601 B / **323 页** / 49 书签 / 0 index folios）。
README:116 本机雅黑那一对（518 页 / 25.1 MB、569 页 / 12.6 MB）与 HTML 5.8 / 5.9 MB 因此**继续成立，本轮未改 README**；
CI/Noto 那一对 505 / 536 按规矩仍不动。

**19:42/19:44 第八次构建同样只跑了 omp**（`--manifest manifest-omp.json --sources sources-omp.json --pdf`，39 枚章徽上盘之后），所以**上面 17:35–17:44 那四行仍是御舆的当前值**，本表继续不跟着变。omp 那一册现在的读数：HTML **20,002,729 B / sha16 `db7fe445da500f35`**（比上一段那句 19,980,906 多 **21,823**，逐枚能对到盘上文件，见 `ILLUST-SYNC.md` 第十节第 4 小节），PDF **30,726,600 B / 323 页 / 49 书签 / 0 index folios / sha16 `43486e9b27ade561`**（多 **54,999 B 而页与书签不动**）。这一轮另添一条可复用的观测：**带 `--pdf` 的那一趟不改写 HTML**——19:42 写完 HTML，19:44 带 `--pdf` 重跑后 HTML 的 mtime 仍停在 19:42:04、字节与 sha 一字未动；再叠上「把托盘换成只有 7 幅题刻的探针目录能逐字节复现 18:48 那份」，两件事一起说明 omp 的 HTML 是输入的纯函数，带时间戳、字节不稳的那一半只有 PDF。


**PDF 的 sha 不是可复现指纹，HTML 的是。** 本轮 08:47→10:18 重跑之后：两份 HTML 字节级一字不差
（`10151855e39afac1` / `82f25301b449893f` 与上表旧值相同），两份 PDF 的 bytes / pages / bookmarks 全部相同、
sha 却各变了一个（旧值 `8e08f9ba48dfa1b2` / `be8f129f58b24801`）。原因在 PDF 元数据里，实测：
PyMuPDF 报 `producer= yuyu-book`、`creationDate= modDate= D:20261104021836+00'00'`（zh，文件 mtime 10:20:14）
与 `D:20261104022813+00'00'`（en，mtime 10:29:42）——时间戳就是那次构建的钟点，写进了 PDF。
所以：**核对 PDF 是否漂了，看 bytes / pages / bookmarks 三项，不要拿 sha 当门**；
sha 只在「同一次构建的两次拷贝之间」有意义。HTML 反之，可以拿 sha 当回归门。
本表此前的 PDF sha 值（08:49 / 08:59 那一版）不是「错了」，是「已被下一次构建刷掉」——这正是上面这条规则要防的误读。

相对 M0（M0 行：中文 507 页 / 24,105,074 B、英文 558 页 / 12,358,555 B）：
截至 10:18–10:29 那次是中文 **+11 页 / +1,007,492 B**、英文 **+11 页 / +237,780 B**；
按 16:1x 第五次构建的当前值是中文 **+11 页 / +1,019,051 B**、英文 **+11 页 / +254,065 B**，书签 17 → 28。
两组的页数与书签一致，差的只是体积——抄数时注意是哪一次。
HTML 行的 pages/bookmarks 是 `—`：PyMuPDF 能打开 HTML 但报出的 1,704/445 是它按文本解析出来的，不是页数，别抄。
README:110 的雅黑口径（518 页 / 25.1 MB、569 页 / 12.6 MB）已与本表一致；本文件此前记的
「507 页 / 24.1 MB 与 558 页 / 12.4 MB」是 M0 那一刻的旧值，现已标注为快照。
构建日志：本轮这四次产物的完整步骤退出码在 `logs/ci-local-yuyu-20261104-100401.log`（严格 UTF-8、
0 个 U+FFFD、末行 `ci-local-yuyu OK`）；上一版 08:47–08:59 的那次在 `logs/rebuild-book-pdf-after-xref.log`；
机器生成的对照读数（含 smoke）：`logs/consistency-sweep-2026-11-04.log`；字节/页数的三条机制见 `PDF-PAGES.md`。

## 改造前的既有红灯（重要，非本次改动引入）

1. **`python scripts/bookctl.py check --fast` 曾失败**：
   `test_registry.ShippedRegistries.test_every_registry_declares_the_current_version`
   → `AssertionError: None != 1 : manifest-omp.json`。
   成因：`registry.FILES` 已包含 omp 清单，而 `yuyu-book/manifest-omp.json` 漏写
   `schema_version`（`sources-omp.json` / `revisions-omp.json` 都有）。
   **已在 M0 补 `"schema_version": 1`**；补后 `test_registry` 9 测通过、omp `--check` 仍绿。
   全量 `check --fast` 复跑归入 Y-M4。**2026-11-04 M7 收尾实跑：六步全绿、exit 0** ——
   deps → `build.py --check --mermaid source`（`CHECK OK`）→ `tests` **39 OK** → `yuyu-book/tests` **510 OK** →
   `check_book.py` 173 Markdown / 321 Mermaid / **0 errors** → `npm run check:diagrams` 321 / 0 errors。
   （M8 收尾重跑：`174 Markdown files, 321 Mermaid diagrams, 0 errors` —— 多的那一份是
   `docs/yuyu-overhaul/BI-AUDIT.md`；`321` 没动，本轮往正文里没加围栏。
   `TRANSLATIONESE-FINAL.txt` 与 `check_bilingual_parity.py` 不是 `.md`，不进这个数。）
   中间这一次曾**红过**：`content` 那一步报 5 条 `missing target`，全是本轮新文档自己写进去的
   （`SITE-LINKS.md` 门户缺陷段 2 条、SPEC 验收段 3 条；当时记作 `SITE-LINKS.md:43`、
   `YUYU-OVERHAUL-SPEC.md:620`、`:839`/`:841`——M9 复核发现这三个号已不复现：SPEC 之后被反复补字，
   而索引里存的还是 777 行的旧版，只能按内容找）。
   原因是 `check_book.py:147` 把行内反引号里的 href 属性赋值与「方括号紧跟圆括号」的链接写法也当真链接扫，
   只跳代码围栏；改写成不带这两种形状的叙述后归零。**没有**为了让闸门绿而放宽 `check_book.py`。
   （记这条的时候我自己又把同一种写法抄回了本文件与 SPEC 各一次，被这条闸门当场再抓一遍 —— 见下表最后一行。）

2. **`python scripts/check_artifact_claims.py` 本机退出码 1**：它按设计比对 CI/Noto 口径的
   505/536/5.8 MB，而本机 `dist/` 是 Windows 字体排出的 507/558/5.7 MB。脚本自己的提示是
   「point this script at the CI artifact dir」。→ Y-M4 Step 3 的 `ci-local-yuyu.ps1` 会撞上它；
   处置见该里程碑（例外表 / 指向 CI 产物目录），**不改 README 谎报本机为 CI 口径**。
   **已按「例外表」这条路落地**（2026-11-04，Y-M4 Step 3 转绿）：脚本先确认 README 里 505 与 536 两个数
   还在（被改过就 throw），再只放行行尾匹配 `has \d+ pages, README says (505|536)` 的 `[STALE]` 行，
   其它任何差异照常红；并且要求至少 1 条——一条都没有说明本机已变成 CI 口径或 README 被动过，同样 throw。
   实测放行 4 条（`README.md` 与 `en/README.md` 各报 zh 518/505、en 569/536）。

## 构建/校验基线命令

```text
python scripts/bookctl.py check --fast                       # 曾红于 manifest-omp（见上）
python yuyu-book/build.py --lang both --check                 # plain 层全量校验（Y-M2/M3 用）
python scripts/check_artifact_claims.py                       # 本机红（CI 口径）
```

## 真源

- 御舆真源：本机仓 `00-前言.md` + 四部分 15 章 + `附录/` + `en/`
- 权威 SPEC：`docs/YUYU-OVERHAUL-SPEC.md`（本文件所属）
- 根目录 `OVERHAUL-SPEC.md` 是 omp SPEC 副本 → 见 `NOTE-ROOT-OVERHAUL-SPEC.md`
- box 备份 `/workspace/omp-book/`：本次执行未做同步（无该环境访问通道）

## 脏树快照

`git-status-baseline.txt`（24 行）· `git-diffstat-baseline.txt`（**13** 改 + 汇总行；本节初记 11 是手数错的）
未跟踪重构文件：`yuyu-book/yuyu_book/{deco,labels,style_css}.py`、`yuyu-book/PRODUCTS.md`、
`yuyu-book/manifest-omp.json`、`yuyu-book/sources-omp.json`、`yuyu-book/revisions-omp.json`、`omp/`

这两份 txt 是 **M0 那一刻（11-03 21:41）** 的快照，不是当前树况。2026-11-04 复核：索引里已有
**324 个已暂存文件**（`git status --porcelain` = 296 `A` + 28 `AM`），工作树另有 79 改 / 79 未跟踪。
**M7 收尾重数（同日更晚）**：暂存总数仍是 **324**，但分布变成 **293 `A` + 31 `AM`**（口径没变、只是几份
已在索引的文件被这轮编辑过）；工作树 **57 ` M` + 90 `??`**。本轮编辑过、且本来就已在索引里的 6 份，
现在都是 `AM`：`docs/YUYU-OVERHAUL-SPEC.md`、`docs/yuyu-overhaul/BASELINE.md`、`omp/BUILD.md`、
`omp/README.md`、`omp/overhaul/BASELINE.md`、`omp/overhaul/STRUCTURE-GATE.md`；
本轮新写、尚未进索引的 4 份是 ` M`：`README.md`、`STRUCTURE.md`、`en/README.md`、`yuyu-book/revisions.json`。
本轮没执行过 `git add`，也没有 `reset`；暂存分布与提交前的泄漏面（`omp/facts/live-18.16.0/models-list.txt`
含私有网关名）记在 `omp/overhaul/BASELINE.md`，两处口径一致，处置待用户拍板。

**M9 收尾重数（同日更晚，拍板之后）**：用户点头后处置了那一份泄漏文件 ——
`git restore --staged omp/facts/live-18.16.0/models-list.txt`（本体未删，仍 5118 字节，状态回到 `??`），
并补了两条忽略规则：`.gitignore:85` `omp/facts/live-*/models-list.txt`、`.gitignore:91` `/.scratch/`
（后者盖住仓库根那 89 条一次性探针产物；`:11` 的 `yuyu-book/.scratch/` 只管构建输出）。
索引 324 → **323**（13:5x 实测 292 `A` + 31 `AM`；14:5x 再数 **293 `A` + 30 `AM`**，总数与脏项都没变，
变的只是分布——下面那条 omp 脱敏改完必须 `git add` 才能刷新 index blob，`omp/ch29.md` 因此由 `AM` 转 `A`），
脏项合计 477 = 293 `A` + 30 `AM` + 58 ` M` + 96 `??`（**15:3x 复数：479 = 293 + 30 + 58 + 98**，涨的两条是 15:1x 两份构建日志，`docs/**` 43→45，`A`/`AM`/` M` 一条没动）。
上面那段「本轮没执行过 `git add`」对 M0–M7 那些轮次仍成立；M9 这一轮动的是索引的**反面**（摘出一条），
既不是 `add` 也不是 `reset`，所以 M0 Step 4 那格的不勾理由不因此改变。
漏面还剩一条归 omp 分册：`C:\Users\<用户名>` 在 `omp/ch04.md:115`、`omp/ch07.md:202`、`omp/ch29.md:3`、
`omp/VERIFY.md:106` 与 `omp/facts/live-18.16.0/config-path.txt:1`，五处互为引用 —— **这五处已办**（用户点头后一次改齐，
四条正文改走 `%USERPROFILE%` 或占位、那份 capture 按仓内 `*-redacted.txt` 先例保留输出形状与 `exit=0` 再抹账户名；
逐条改法见 `ACCEPTANCE.md` 第 3 节拦路第 3 条）。这是御舆轮次唯一一次动 omp 分册**正文**，且只动隐私、不动论点；
14:57 又动了同目录 4 份**证据 capture**（见下），正文仍只有那 3 份单元 + `VERIFY.md`。
**动了 3 份单元源文件就得重排**：14:48:21 → 14:51:19 跑 `bookctl build --product omp --lang zh --pdf`，
exit 0，`321 pages / 49 bookmarks / 39 units / 242 glosses` 与 08:20 那一次**一字不差**，
只有体积漂了（HTML +183 B、PDF +2,764 B），两行新读数进了 `PDF-PAGES.md`；
御舆那四行没重排，因为这一轮没碰御舆任何单元源文件。
**同一条词也在我这一侧**：`git grep -l` 扫出来 `docs/YUYU-OVERHAUL-SPEC.md`（2 处）与本文件（1 处）
原本携带那个字面路径，M9 已全部改写为 `C:\Users\<用户名>` 占位（占位符放在行内反引号里，不会被当标签吞掉）。
另扫出 `docs/yuyu-overhaul/logs/` 盘上 14 份日志里 **7 份未跟踪的都带它、共 23 处**——解释器/Node 把自身
绝对路径打进 stdout 的副产品；已在索引的那 2 份（`unittest-after-m1.log`、`unittest-at-HEAD.log`）0 命中。
**这 23 处连同 omp 侧 3 处（`omp/overhaul/logs/` 1、`plugin-doctor.txt` 1、`tiny-models-list.txt` 1）共 26 处，
14:30/14:31 已就地把 `Users\<账户名>` 换成 `Users\<用户名>`**——只换路径那一段，退出码、计数、时长一个字节没动，
所以第 4 组那句「14 份 `logs/`」重新成立，「8 份日志」那格可以照着 add 了。
   **15:1x 之后这句要按 16 份读**（两份新构建日志各 1 处解释器自报路径，已同样就地脱敏、残留 0 命中）。
**14:57 又补了一批，比这两批加起来还多**：同一目录 4 份 JSON capture（`skill-list-json` 54、
`agents-unpack-json` 7、`plugin-doctor-json` 1、`ps-json` 1）共 **63 处**，形态是转义后的
`Users\\<账户名>`——上一版三次扫描都只容得下一个分隔符，整批漏报（坑记在 `ACCEPTANCE.md` 第 9 条第 4 项）。
这 63 处同样就地替换、保留原转义形状，四份改完仍是合法 JSON；机器输出两批合计 **89 处**。
处置口径与为什么不加忽略规则（那 7 份被 5 份文档引用了 22 次，14:4x 实测、记账后涨到 23）见
`ACCEPTANCE.md` 第 3 节拦路第 3 条；
那条还记了一个反直觉的事实：这个词**已经在 HEAD 里**（**6 份** video 侧文档共 **13 处**；上一版记的
「4 份 9 处」是分隔符坑量出来的少数），脱敏是止损，不是首次暴露。

同一时刻的另一半树况：`docs/yuyu-overhaul/` 下 **14 个文件从未进索引**（`git status --porcelain` 实测 14 行 `??`）——
6 份文档/护栏（`GUIDES-QA.md`、`HUMANIZER-LOG.md`、`PEDAGOGY-LOG.md`、`PLAIN-FIX-LOG.md`、
`PDF-PAGES.md`、`check_crossrefs.py`）+ `logs/` 里 8 份日志
（`consistency-sweep-2026-11-04`、`doctor-checkfast-after-xref`、`rebuild-book-pdf-after-xref`、
`rebuild-book-pdf-both`、`smoke-both-after-xref`、`unittest-after-m2`、`unittest-after-xref`、
`unittest-concurrent-anomaly`）。M7 收尾重数：这一格已到 **21 行 `??`**，多出的是
`SHARED-TERMS.md`、`SITE-LINKS.md`、`TEST-CONTRACT.md`、`check_site_links.py`、`ci-local-yuyu.ps1`
与 `logs/ci-local-yuyu-20261104-{095428,100401}.log`；仓库根的 `docs/COMPARE-OMP.md` 也是 `??`。
而 `BASELINE.md`、`NOTE-ROOT-OVERHAUL-SPEC.md`、
`docs/YUYU-OVERHAUL-SPEC.md`、`omp/overhaul/*` 是 `AM`：先前已被暂存、本轮又在工作树里改过，
提交时它们会带上这轮的修改。两个集合别混——`??` 是「写了但没 add」，324 是「早先已经进过索引」。

## Mermaid 计数复核

M0 记的 `zh=160 en=160` 在 2026-11-04 重数仍成立（口径：`00-前言.md` + 四个部分目录 + `附录/` = 20 个 zh 文件；
`en/**/*.md` = 21 个文件，其中 `en/README.md` 不计入正文单元）。M2–M4 的正文改动没有增删 mermaid 围栏。

别把这两个数和 `check --fast` 报的 **「174 Markdown files, 321 Mermaid diagrams」** 当成矛盾
（M8 收尾实跑；M0 那次是 169，M7 收尾 173，M8 再加一份 `BI-AUDIT.md` 到 174，Mermaid 一条没动。
M3 又加 `ILLUST-SYNC.md` → 同一条命令报 **175**；M9 落 `ACCEPTANCE.md` 后是 **176**。
**这个数每往 `docs/` 落一份 .md 就 +1，
它是「那一刻的读数」，不是契约**；要引用就引当下实跑，别抄本文件里任何一个）：
后者是 `scripts/check_book.py` 的全仓口径（`root.rglob('*.md')`，只排掉 `video/`、`node_modules/`
和点开头目录，因此 `omp/`、两份 SPEC 自己的围栏都在内），前者只数御舆正文。
两个口径**不能互相抄**，御舆侧要引用就用 160/160。

## 文档 ≠ 磁盘：本轮收口项

「先修一致性与护栏」这条口径要求每次改动都留下可对拍的账。下表每一项都是**先看盘上是什么、再改文档**，
右列的出处均可用一行命令复核（命令在对应文件里）。

| 位置 | 文档原来写 | 盘上实际 | 依据 |
|------|-----------|----------|------|
| `omp/README.md` 抬头 | 「Phase 2 再接流水线」 | Book CI 已有独立 `omp` job | `.github/workflows/book.yml:107`，产物 `yuyu-omp-dist`（:144） |
| `omp/README.md` 对照表「构建」行 | 「Phase 1 **未接入** `make book`」 | 两条目标都在 | `Makefile:48` `book-omp`、`:51` `book-omp-pdf` |
| `omp/README.md` 关系段 | 「对照表见仓库外方案文档 / 后续附录」 | 对照表在仓内三份文件里 | `omp/overhaul/CROSSREF-MAP.md`、`docs/COMPARE-OMP.md`、`docs/yuyu-overhaul/SHARED-TERMS.md` |
| `omp/BUILD.md` 全量测试行 | 「（501）均 OK」引 M2 日志 | 本轮重跑 **39 + 510** | `logs/unittest-after-m2.log` 那一刻是 501；M6 加 9 条 → 510 |
| `STRUCTURE.md` §1 `tests/` 行 | 只列 2 个模块 | 7 个模块 | `ls tests/test_*.py` |
| `STRUCTURE.md` §1 `docs/` 行 | 漏 `COMPARE-OMP.md`、`banner.svg` / `tagline.svg`、`baseline/`、`migrations/`、`notes/`、`superpowers/`、`video/` | 按盘上补齐 | `ls docs/` |
| `docs/COMPARE-OMP.md` 两处链接 | `[`SHARED-TERMS.md`](SHARED-TERMS.md)` → 从 `docs/` 解析即死链 | 改指 `yuyu-overhaul/SHARED-TERMS.md` | `check_site_links.py` 的 `FRONT_DOOR` 已纳入该文件（4 → 5 份） |
| `docs/COMPARE-OMP.md` 勿混段 | omp 独有「22 个词」、共享「14 个」 | **21** 独有、**15** 共享 id | `SHARED-TERMS.md` §六 的命令 |
| `docs/COMPARE-OMP.md` 构建事实表 | omp 通俗层「20 / 12 / 4 不标」 | **24 core / 12 extra**（无未标） | `glosses-omp.json` 的 `priority` 计数 |
| `README.md` 第二分册段 | 无两书对照入口 | 新增一句，链 `docs/COMPARE-OMP.md` 与 `docs/yuyu-overhaul/SHARED-TERMS.md` | `check_site_links.py` 校这条相对链接 |
| `BASELINE.md` Dist 当前值 | 11-04 08:47–08:59 那一次读数 | 10:18–10:29 重建后（HTML sha 未变、PDF sha 换、页数与字节未变） | `logs/ci-local-yuyu-20261104-100401.log` |
| `docs/YUYU-OVERHAUL-SPEC.md` M7 验收两行 + `docs/yuyu-overhaul/SITE-LINKS.md` 门户缺陷段两行 + `SPEC` 另验收段一行（当时记 `:620`/`:839`/`:841`，M9 复核已不复现） | 讲缺陷时把指向部署名的 href 赋值、以及方括号紧跟圆括号的链接例子原样抄进行内反引号 | `check_book.py` 不看反引号、只看代码围栏，于是本轮文档自己贡献了 **5 条 `missing target`** | 改写这三处（属性名不再带引号形式、链接例子拆开），`content` 回到 0 errors；**记这条账的段落本身又踩了一次**，同一天再改一遍才归零 |
| `BASELINE.md` 脏树快照两格 | 「14 行 `??`」「296 `A` + 28 `AM`」 | **21 行 `??`**、**293 `A` + 31 `AM`**（暂存总数 324 未变，本轮零 `git add`） | `git status --porcelain` 实测，已并列写出「那一刻」与「M7 收尾重数」 |
| `BASELINE.md` 本文件两格的 173 | M7 收尾时 `check_book.py` 报 **173 Markdown files** | M8 写完 `BI-AUDIT.md` 后重跑 **174**（Mermaid 仍 321，正文没加围栏） | 169（M0）→ 173（M7）→ 174（M8）→ **175**（M9 写 `ILLUST-SYNC.md`）→ **176**（M9 写 `ACCEPTANCE.md`，14:1x 实测 `176 Markdown files, 321 Mermaid diagrams, 0 errors`）五段读数并写，不覆盖历史 |
| `TRANSLATIONESE-BASELINE.txt` 的性质 | 文件名容易被读成「改造前快照」 | 它是 **Y-M1 中途的工作树快照**；可比的「改前」是 HEAD（zh `0/13/13`、en `15/16/42`） | `BI-AUDIT.md` 第二节三点读数表；HEAD 侧用 `git archive HEAD` + 同一 `prose_walls`/`line_counts` 重算，40 个文件全在 |
| `YUYU-OVERHAUL-SPEC.md` M8 Step 2 的命令 | 用 `Tee-Object` 落 `TRANSLATIONESE-FINAL.txt` | PS 5.1 下 `Tee-Object` 默认 UTF-16/ANSI，中文表头会花；改用 Python 侧重定向（CRLF、UTF-8、exit 0） | 同一个坑已在 `ci-local-yuyu.ps1` 头部注释登记第 2 条；SPEC 里写明偏离，不改命令装没事 |
| `YUYU-OVERHAUL-SPEC.md` M8 Files 首行 | 「Modify: 不合格的 `en/**` 段落与 `notes.json` en」 | `notes.json` 的 en 侧**零改动**：14 条测试本来就全绿 | `test_notes.py` 实跑 `Ran 14 tests, OK`；SPEC 里如实写「不合格的部分为零」，不删那一行 |
| `ci-local-yuyu.ps1` | 只跑 `check --fast` + 构建 + 页数例外闸 | 新增「离线护栏」段：`check_site_links` / `check_block_markers` / `check_crossrefs` / **`check_bilingual_parity`** 四条，放在最贵的一步之前 | 四条独立实跑各 exit 0；`Parser::ParseFile` 无语法错误，BOM+CRLF 未丢；不进 `check --fast` 是因为**六步是被钉的宣称** |

**没收口的，写明为什么没收**：

- `omp/FUSION-PLAN.md` —— 御舆 SPEC M7、`docs/COMPARE-OMP.md` 与 omp 侧都把它当 §3 对照表的出处，
  **文件不存在**。本轮没有补写它（补一份「方案文档」等于凭空造真源），改为把它的职能落到
  `CROSSREF-MAP.md`（逐章）+ `SHARED-TERMS.md`（逐词）这两份有盘上依据的文件里。
- `omp/COMPARE-YUYU.md` —— 归 omp SPEC M6，御舆侧不代写；`COMPARE-OMP.md` 因此不放指向它的链接。
- `附录/D-术语表.md` 的「丛书共享词」短节 —— 标的是「可选」，动它要过锚点/字墙/主题索引三套契约，留给拍板。
- `docs/yuyu-overhaul/PEDAGOGY-LOG.md:102` 与 SPEC 里若干处仍写 501/442/422 —— 那些是**逐条引日志的历史事实**，
  改掉就是篡改证据，一律不动。
- `check_bilingual_parity.py` **没进 GitHub Actions** —— 本轮只把它串进本地 `ci-local-yuyu.ps1`。
  远端要不要接、以及 `check --fast` 要不要从六步变七步（那要同步改 README/STRUCTURE/revisions
  三处被钉的「六步」宣称），属 M9 的移交建议，不由 M8 自己拍。
- `docs/` 下 `superpowers/`、`video/` 两目录属其它工作，本轮只在 `STRUCTURE.md` 里如实登记其存在，未整理内容。
