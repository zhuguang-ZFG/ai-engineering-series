# 御舆改造 · 总验收（ACCEPTANCE）

- Date: **2026-11-03 America/Adak**（本机墙钟是 2026-11-04 12:5x CST；Adak 比上海晚 17 小时，
  所以同一段时间在两个日历上差一天。SPEC §「M9 签字」要求按 America/Adak 记，与
  `BASELINE.md:3`、SPEC 头部 `v1.0 · 日期：2026-11-03` 是同一个日子，不是笔误。）
- 执行者：Qoder CLI（`zhuguang-ZFG` 的机器上执行，分支 `p3-pages-split`，起点 `951c0ef`）
- 范围：`docs/YUYU-OVERHAUL-SPEC.md` Task M0–M9，**不含** omp SPEC 的 Task（那本另册移交）
- 状态口径：**本文件写完即 SPEC 执行期结束。全程零 `git commit` / 零 `git push` / 零 `gh pr create`。**

---

## 1. 缺口表 K1–K12 逐条关闭

「关闭」的标准不是“做了点什么”，而是 SPEC §4 那条门禁能不能被一条可复跑的证据回答。

| ID | 缺口 | 结论 | 证据（路径 · 命令 · 实测值） |
|----|------|------|------------------------------|
| K1 | 零基础友好度不足 | **关闭** | `docs/yuyu-overhaul/PEDAGOGY-LOG.md`（B1–B4 批次）；`python docs/yuyu-overhaul/measure_pedagogy.py` 的行数/场景对比；每章罗盘三字段齐（见 K2）。诚实边界：中文 translationese 的改进**不是**相对已提交版本的净收益，见 `BI-AUDIT.md` 第 3 节 |
| K2 | guides 未做反抄袭 QA | **关闭** | `docs/yuyu-overhaul/GUIDES-QA.md` §「逐条核对（20/20）」——20 单元 × question/deliverable/boundary 可检查性逐条；字段契约在 `yuyu_book/core.py:18` 的 `GUIDE_FIELDS`，校验在 `core.py:359-363` |
| K3 | glosses / why_evidence 悬空 | **关闭** | `python -m unittest discover -s yuyu-book/tests -p "test_plain.py" -v` → **Ran 70 tests, OK**（双语 `why` 证据门禁正反两面都在里面）；`ci-local-yuyu` 全量 510 tests OK |
| K4 | 插画/prompts 手册过期 | **关闭** | `docs/yuyu-overhaul/ILLUST-SYNC.md`：reader 与 gallery 重生后 **`git diff` 空**（`beginner-reader.html` / `.en.html` / `illustration-gallery.html` 都不在脏区；措辞已更正——盘上比 HEAD 各多 475/471/309 字节，等于各自行数，因为本机 `core.autocrlf=true`，相同的是**归一行尾后的内容**，不是字节）。差额只在 `docs/illustration-prompts.md`（标题 26 → 盘上 42，本轮补了 16 张章内图的说明段）。Mermaid zh 160 = en 160；SVG 契约 42 张 0 违约 |
| K5 | README/STRUCTURE 双产品描述过时 | **关闭** | `README.md:45`「两条命令各编各的书，不再是『尚未接入』」＋ `:47` 两处边界；`STRUCTURE.md` §3.6 双产品对照表（`book` 20 单元双语 vs `omp` 39 单元 zh） |
| K6 | CI 无 omp paths / 无 omp job | **配置关闭，真绿 open** | `.github/workflows/book.yml`：`omp/**` 进了 `on.paths`（`:14`、`:30`），独立 `omp` job（`:107`）**故意不写 `needs`**，注释 `:101-106` 写明「omp 排印失败不把御舆那一格染红」＋「omp 书稿没进 main 之前这个 job 会在 build 一步失败，不是偶发」。`check-book.yml` 无 `on.paths` 过滤，任何 omp 改动本来就会重跑御舆内容门禁，故不再加 job。**GitHub Actions 真绿不是本 SPEC 的完成条件**（SPEC §6.2），留待推送。**15:14 补 / 15:49 结**：M4 那一格「YAML 经人工目视」的目视面已交出去（对 HEAD `+56 / −0`，纯增量），**15:49 用户回「同意继续」→ 本格已打勾**；「引入 job 的那次 push 会挂一格设计上就红的 `omp`」摊成三条路后**按 ① 落地**（YAML 一字未改，红格由 `book.yml:105–106` 注释说明，`omp/` 进仓本来就是第 6、7 组的事；②③ 到推送窗口再改也来得及）。详见 SPEC M4 验收段 |
| K7 | 构建器重构未收敛验收 | **关闭** | `deco.py`/`labels.py`/`style_css.py` 已是 `git add` 状态（`git status --porcelain` 显示 `A`），`frontmatter.py`/`backmatter.py`/`pages.py` 拆分与 `951c0ef` 一致；`ci-local-yuyu` 的 `build --product book --lang both --pdf` → 两份 PDF 出片（518 / 569 页） |
| K8 | 测试未隔离 `product=omp` | **关闭** | `yuyu-book/tests/test_product_isolation.py`（**Ran 9 tests, OK**）：单元数 20 vs 39 各自唯一、三个登记表名按 product 派生后互斥、产物前缀不撞车、omp 必须显式 `subject_index_registry: null`、别的构建器单测不许加载 omp 清单 |
| K9 | 共享术语 / 互链未落御舆侧 | **部分关闭** | 已落：`docs/yuyu-overhaul/SHARED-TERMS.md`（含「omp 专名不许进御舆释义」清单）＋ `docs/COMPARE-OMP.md` 互链 ＋ `docs/yuyu-overhaul/check_crossrefs.py`（book→omp 23 refs / omp→book 49 refs，0 bad）。**未落（有意）**：`附录/D-术语表.md` 的「丛书共享词」短节——SPEC M7 Step 2 那格标的是「可选」，本轮不顺手做，理由写在 SPEC M7 Step 2 那个不勾的 box（起头是「`附录/D-术语表.md` 的「丛书共享词」短节：**本轮没做**」；M9 之后行号在漂，早期记的 `:884` 别再按号找） |
| K10 | translationese 基线未写进验收 | **关闭** | `TRANSLATIONESE-BASELINE.txt`（轮中快照）→ `TRANSLATIONESE-FINAL.txt`（HEAD 对照 + 本轮终值）→ `BI-AUDIT.md`（三套口径对拍）。终值 zh 0 行/13 处/13 术语、en 15 行/16 处/42 系词；HEAD 与 NOW **逐单元相同** |
| K11 | 根 `OVERHAUL-SPEC.md` 实为 omp 册，易误读 | **标注关闭，去留 open** | `docs/yuyu-overhaul/NOTE-ROOT-OVERHAUL-SPEC.md` 已写明「以 `docs/YUYU-OVERHAUL-SPEC.md` 为御舆真源」；根文件仍在盘上（`OVERHAUL-SPEC.md`，31138 字节，头部 Goal 写的就是 omp）。**删除/移动属提交窗口决定**，SPEC §6.5 已把它挂在那儿，本轮不动 |
| K12 | 提交推送与 CI 真绿未做 | **按设计 open** | 用户拍板「提交推送稍后」；本 SPEC §6.1 禁止执行期内 commit/push。分组建议见本文件第 3 节 |

门禁汇总（SPEC §4 那张表）里，「CI 配置」一行的**真绿**和 Git 一行的**提交**是唯一两个故意留给推送之后的；其余七行本轮都有可复跑证据。

---

## 2. 最终本地跑（M9 Step 2）

两条命令，都是**这台机器**的口径，不是 CI 的口径。两条都已跑完，都是 **exit 0**。

| 命令 | 结果 | 日志 / 出片 |
|------|------|-------------|
| `powershell -File docs/yuyu-overhaul/ci-local-yuyu.ps1` | **`ci-local-yuyu OK`**，进程 exit 0；7 步全过，唯一 exit 1 是页数宣称那步，按字体口径放行 | `docs/yuyu-overhaul/logs/ci-local-yuyu-20261104-125209.log`（12:52:09 → 13:13） |
| `python scripts/bookctl.py build --product omp --lang zh --out-dir yuyu-book/.scratch/omp-final-smoke` | **OK / exit 0**：`yuyu-omp-zh.html: 20.0 MB, 39 units, 242 glosses, 39 lead bands, 381 tier chips` | `yuyu-book/.scratch/omp-final-smoke/`（`.gitignore:11` 盖住，不入库） |

共存是怎么被证明的（不是「两条都绿」就算）：

- 御舆那一格照常出片：`yuyu-agent-harness-zh.html` 5.8 MB / 20 units / 296 glosses → `.pdf` **518 页**；
  `-en.html` 5.9 MB / 303 glosses → `.pdf` **569 页**；两本都 28 bookmarks、14 index folios。
- omp smoke **没有**碰御舆：跑前跑后 `dist/yuyu-agent-harness-zh.html` 的 md5 都是 `2118bdbd4332`，
  mtime 停在 13:03:58（那是御舆自己 build 的时刻）。`make book` 的语义没被 omp 那条路径伤到。
- omp smoke **也没有**覆盖 `dist/yuyu-omp-zh.html`（mtime 仍是 08:19）——`--out-dir` 真的把产物隔开了。
- 顺带一条副产品：smoke 出的 html 与 08:19 那份 **md5 完全相同**（`3d1d23e6…`），说明 omp 构建是确定的，
  不是「每次跑出来不一样、只能祈祷」。
- `dist/` 与 `yuyu-book/.scratch/` 都在 `.gitignore` 里（`:8`、`:11`），所以下面 `git status` 看到的脏区
  不含任何构建产物。

`ci-local-yuyu.ps1` 这一段一次跑齐 7 步（4 个护栏 + check --fast + build both --pdf + 页数宣称）：

- 护栏：`check_site_links` OK、`check_block_markers`（40 文件，锚点齐/锁定词形在/围栏数未变）、
  `check_crossrefs`（23 + 49 refs，0 bad）、`check_bilingual_parity`（20 单元 H2 Δ=0、Mermaid Δ=0）
- `bookctl check --fast` → `CHECK OK`；39 tests OK；**510 tests OK** in 215.388s；
  175 Markdown files / 321 diagrams / 0 errors（**这份日志落盘后 `ACCEPTANCE.md` 自己也进了 `docs/`，
  现在同一条命令报 176** —— 该数的口径与「它是读数不是契约」记在 `BASELINE.md` 的 Mermaid 复核一节）
- `build --product book --lang both --pdf` → 两份 HTML + `yuyu-agent-harness-zh.pdf` 与 `-en.pdf`
- `check_artifact_claims.py` → **exit 1，四条都是「本机雅黑页数 vs README 里 CI/Noto 的 505·536」**，
  脚本按 `PDF-PAGES.md` 的口径放行；反向也钉住：若有人把 README 改成本机页数来凑绿，脚本会拦。

> 这台机器上 `check_artifact_claims.py` 必定报红且不是坏了——字体口径不同。想让它在本机变绿，
> 唯一诚实的做法是改 README 的宣称口径为「两套字体各报一数」，那是另一件事，不在本 SPEC 里顺手做。

**14:2x–14:5x 复跑（脱敏与行号更正之后）**：这一批动的是 `docs/**` 三份文档、`.gitignore`、
**3 份 omp 书稿单元**（`omp/ch04.md`、`omp/ch07.md`、`omp/ch29.md` 都是 `manifest-omp.json` 的 unit，
`omp/VERIFY.md` 不是）、4 份 omp capture、10 份日志。第一遍我只跑了轻闸门，并写下
「没碰正文、所以不必重排」——**那句判断是错的**：改了被 `omp/BUILD.md:52` 与
`PDF-PAGES.md:45` 盯着的单元源文件，就得重排，否则那两个数是对着旧源文报的。
于是 14:48:21 补跑 `bookctl build --product omp --lang zh --pdf`，14:51:19 exit 0：
**321 页 / 49 书签 / 39 units / 242 glosses 全部一字未动**，只有体积漂了 HTML +183 B、PDF +2,764 B
（两行新读数已进 `PDF-PAGES.md`，那里也标了 smoke 表旧 sha 结论从此不可抄）。
御舆那四行没有重排，因为这一轮确实没碰御舆单元源文件。
轻闸门那几条同样全绿：`check_book.py` → **176 Markdown / 321 Mermaid / 0 errors**；
`check_site_links` / `check_block_markers`（40 文件）/ `check_crossrefs`（23 + 49，0 bad）/
`check_bilingual_parity`（Δ=0）四条护栏；`test_docclaims` → **9 tests OK**
（复跑口径 `python yuyu-book/tests/test_docclaims.py`；`-m unittest tests.test_docclaims` 是错的模块路径，
那份测试在 `yuyu-book/tests/` 下）。

**15:17–15:35 第四次构建（用户令「生成本地pdf」）**：两条 `bookctl build` 串行、各 exit 0
（`--product book --lang both --pdf` 15:17:51 启动 → 15:31:43 落盘；
`--product omp --lang zh --pdf` → 15:34:55 落盘），成品 **518 / 569 / 321 页**、书签 28 / 28 / 49。
这一轮**御舆与 omp 的单元源文件都没动**，所以它不是「改了源就得重排」那种必需，
而是把同源再排一遍取一份本机成品 PDF 给用户；顺带证伪了上一段最后一句的长期有效性
（「御舆那四行没有重排」到 15:17 为止，现在表里有了新读数）。
页/书签**没有采信构建器自报**：改用仓库钉住的 `pymupdf==1.28.0` 直接开三个文件数，三条 MATCH，
sha256 前缀 `0da7c61e9a89` / `a1a6160cc27b` / `2fd8890af850` 一并写进 `PDF-PAGES.md`
（只对这一对成立，再排即废）。体积漂移：zh PDF **−648 B**、其余五份同字节——归入本文件已有的
「页数不变前提下的字体子集/再排噪声」那一类，不新立解释。
两份新日志各 1 处解释器自报绝对路径，已就地换成 `Users\<用户名>`（行列数不变、残留 0 命中）。
闸门复跑：四护栏 exit 0、`test_docclaims` exit 0、`check_book.py` **176 Markdown / 321 Mermaid / 0 errors**、
`check_artifact_claims` 仍 exit 1（本机雅黑 518·569 vs README 那句 CI/Noto 505·536，
按用户口径**不改 README 凑绿**）。
**这轮最有价值的一条不是 PDF，是 HTML 回归门真的响了一次**：`BASELINE.md` 说「PDF 的 sha 不是指纹、
HTML 的是」，而 15:2x 两份 HTML 的 sha 相对 10:2x 全变、页数一条没动。
用 `find … -newermt "2026-11-04 10:29:00"` 把 10:29 之后动过的构建输入数完（只有
`yuyu-book/revisions.json` 10:49 与四份 en 章节 11:52–11:53），两条差异全部归因、不留噪声：
zh HTML **同字节不同 sha** = `revisions.json` 那句「构建器测试 501 项全绿」→「510 项全绿」是**等长替换**
（成品里 `510 项全绿` 1 次、`501 项全绿` 0 次，实测），en HTML **+49 B** 落在 11:52–11:53 那四次编辑上。
这也把 `PDF-PAGES.md` 里长期挂着的「en 两行为什么是 5,909,019 而不是盘上的 5,909,068」从
「未归因」改写成「两个时刻各自的真读数」——原来那版本文件为了记它写的是「不能断言哪一次数错」，现在能断言了。
扫描侧新踩两条假绿坑（字符类 `[\/]` 吞掉反斜杠、
`git ls-files ''` 空 pathspec 报 0 条），见第 5 节第 9 条第 6、7 项。
**16:10–16:28 第五次构建（附录 D「丛书共享词」落地后的必需重排）**：两条 `bookctl build` 串行、各 exit 0
（book 16:10:46 启动 → zh HTML 16:16、zh PDF 16:18、en HTML 16:23、en PDF 16:24 落盘；omp → HTML 16:26、PDF 16:28）。
与上一轮的本质区别是**这一轮真的改了单元源文件**（`附录/D-术语表.md`、`en/Appendices/D-Glossary.md` 各 12 行），
所以它是 `omp/BUILD.md:52` 与 `PDF-PAGES.md:45` 那两条规则要求的那种重排，不是「再排一遍取成品」；
而 omp 一个单元没碰，于是同一轮里自带对照组：**`yuyu-omp-zh.html` 19,974,383 B、`yuyu-omp-zh.pdf` 30,629,993 B、
321 页 / 49 书签与 15:33/15:34 两份逐字节相同**，只有 sha 随 PDF 内生成时间戳换了
（`2fd8890af850` → `fbefa3d8d8b6`）——「PDF 的 sha 不是可复现指纹」这条规则第二次实测命中，第一次是 10:1x 那回。
御舆四行跟着那 12 行长：zh HTML **+1,578 B**、zh PDF **+12,207 B**、en HTML **+2,485 B**、en PDF **+16,063 B**，
而 **518 / 569 页、28 / 28 书签、14 / 14 index folios 一条没动**，多出的体积落在已有页内、没有溢出新页。
页/书签仍不采信构建器自报：`pymupdf==1.28.0` 直接开文件数，与构建打印逐条 MATCH，
并记下本轮 sha（zh HTML `9846b04e60cdf413`、zh PDF `2bc3af3cc4347782`、en HTML `2df6c199f89eccaa`、
en PDF `2a62a8d0eaaef32f`、omp HTML `38369e7fc4ed6b18`、omp PDF `fbefa3d8d8b613c2`）。
**两条结论的强度必须分开写**：① 构建器自报 en glosses 由 303 变 **304**（zh 仍 296）——本轮唯一动过的 en 单元
就是 `en/Appendices/D-Glossary.md`，所以这 +1 记在它名下，但这是**排除法归因、不是实验证明**，
要证得回滚那 12 行再排一次，本轮没做；② zh HTML 这次是 **+1,578 B 且 sha 变**，与 15:2x 那次
「同字节、不同 sha」是两种信号，这一回内容确实变长了。
**README 本轮一个字没改**：`README:116` 的本机雅黑那一对（518 页 / 25.1 MB、569 页 / 12.6 MB）与 HTML 的
5.8 / 5.9 MB 被本轮实测**重新确认为真**，CI/Noto 那一对 505 / 536 按用户口径继续不动，
`check_artifact_claims` 因此仍 exit 1（四行：`README.md` 与 `en/README.md` 各报 zh 518≠505、en 569≠536）。
**SPEC 那句「勿炸 subject-index」最终是虚警，但过程值得记**：`--regen-index --lang both --check` 本身 exit 0，
打印 `238 terms (238 zh refs, 116 en refs)` 与 `CHECK OK`；跑完盘上 `subject-index.json` 挂着 ` M`，
我一度判定附录 D 把索引炸了。逐项比对结论相反：**4626 行只差缩进、0 处内容差异、`json.loads` 与 HEAD 完全相等**，
而工作区那份是 4 空格缩进——`yuyu_book/core.py:55` 的 `dump_json` 写的是 `indent=2`，
可见 4 空格那版**不是构建器产物**（被外部格式化改过）。`git checkout --` 单路径复原后，
工作区字节等于 `git show HEAD:` 内容做 LF 规范化的结果，说明**重跑 `--regen-index` 能逐字节复现登记表**，
附录 D 新增节没有产生任何索引行（主题索引来自 `glossary_to_index(manifest)` 的 gloss 登记表、
不解析附录 D 正文——这条 13:5x 就记过，本轮再次成立）。
闸门复跑（构建完成后实跑，不引用旧值）：`check_site_links` / `check_block_markers`（40 文件）/
`check_crossrefs`（omp→book 49 refs、0 bad）/ `check_bilingual_parity` 四护栏 exit 0，
其中 **`apxd 17 17 0 2 2`**（附录 D 双语各 17 个 H2、Δ=0，Mermaid 2/2）；
`check_book.py` **176 Markdown / 321 Mermaid / 0 errors**；`test_docclaims` 9 tests OK；
`test_product_isolation` 9 tests OK。
两份新日志各 1 处解释器自报绝对路径，就地换成 `Users\<用户名>`（612→618、395→401 B）；
末行 `BOOK_EXIT=0` / `OMP_EXIT=0`（631 / 413 B）是**我从后台任务 wrapper 的 stdout 补写的**，
不是构建器自己打的——本轮用的是纯重定向，151751 那两份才是命令内自带的。
扫描侧又踩三条，见第 5 节第 9 条第 8、9、10 项：命令文本里的 \\ 会被工具层压成 \
（今天两次，第二次直接把脚本打成 SyntaxError）、文本模式读文件会折叠 CRLF 并把字节数少算、
以及「拿已脱敏的旧日志当阳性对照」等于没有对照。

---

## 3. 提交分组建议（只建议，**不执行**）

SPEC M9 Step 3 给了 7 组。脏区 **479** 条（`git status --porcelain -uall`，15:3x 复数；本节下面第 1、2 条拦路处理**之前**是 567 条，14:5x 曾读作 477——多的 2 条是 15:1x 两份构建日志），
其中索引里已带 `A`/`AM` 状态的是 **323** 条（14:5x 实测 293 `A` + 30 `AM`；13:5x 那次是 292 `A` + 31 `AM`，
差的 1 条就是第 3 条脱敏后为刷新 index blob 而 `git add` 的 `omp/ch29.md`——见本节末尾第 8 条）。
这 323 条都是之前某个窗口 `git add` 留下的，本轮只摘掉第 1 条那一个。
分项：`omp/**` **366**（比原来少 1，就是被摘掉的那份 `models-list.txt`）· `docs/**` 43（**注**：含本轮自己写的 `ACCEPTANCE.md`）·
`.scratch/**` **0**（已被新规则忽略，盘上 89 条还在原地）·
`en/` 18 · `yuyu_book/*.py` 12 · `yuyu-book/*.json|md|build.py` 11 · 中文正文 17（含 `00-前言.md`）·
根文档 5（`.gitignore` `Makefile` `README.md` `STRUCTURE.md` `OVERHAUL-SPEC.md`）· `.github/` 2 ·
`scripts/` 2 · `yuyu-book/tests/` 1。按御舆侧可独立成 commit 的顺序：

| # | 建议 subject | 装什么 | 为什么这堆能自成一个 commit |
|---|--------------|--------|------------------------------|
| 1 | `refactor(yuyu-book): converge style/deco/labels split` | `yuyu_book/*.py` 12 份：`style` `deco`* `labels`* `style_css`* `render` `pages` `frontmatter` `pdf` `core` `registry` `art` `plain`（* = 本轮新建、已在索引里）。`backmatter.py` 与 `951c0ef` 一致、本轮没动。再加 `yuyu-book/build.py` + `scripts/bookctl.py` + `Makefile`（`book-omp` / `book-omp-pdf` 两个 target 与 help 行） | 拆文件、CLI 的 `--product` 分派、make target 是同一件事的三面；`test_build_contracts` / `test_pages` 是它的门禁 |
| 2 | `docs(yuyu): pedagogy pass B1–B4` | zh 正文 17 份 + `en/` 18 份 | 双语必须同增同减；`check_bilingual_parity` 已经把 Δ=0 钉住 |
| 3 | `fix(plain): guides/glosses/notes evidence` | 御舆侧只有 3 份登记表真的变了：`manifest.json`（+0/−6，删的是行号引用）、`reading-paths.json`（+4/−1）、`revisions.json`（+2/−2）。**`guides.json` / `glosses.json` / `notes.json` 与 HEAD 零差异**（`git diff --quiet HEAD` 三句都静默）。omp 侧另 6 份（`*-omp.json`）归第 7 组 | 这一组的实质是「QA 验过、不必改」——把 20/20 的核对结果写进 `GUIDES-QA.md`，而不是为了有 diff 而动登记表。混进第 2 组会让人以为正文改动是靠登记表变的 |
| 4 | `docs(site): portal dual entry + STRUCTURE products` | 根：`README.md` `STRUCTURE.md`；`scripts/build_site_portal.py`（门户双入口的实际生成器）与它的产物 `docs/portal.html`（+24/−12，
内容是 M5 那句「本站只发布御舆；同仓第二分册…仍在施工中」写进 `og:description`；生成器与产物必须同一组，否则 `pages.yml` 的再生成对比会红）；册内：`docs/illustration-prompts.md`、`docs/COMPARE-OMP.md`、`docs/yuyu-overhaul/*`（17 份 .md/.txt + 2 份 .json 证据、5 个 .py（4 个护栏 + `measure_pedagogy.py`）、`ci-local-yuyu.ps1`、14 份 `logs/`（**15:1x 起盘上是 16 份**：新增 `rebuild-{book,omp}-pdf-20261104-151751.log`）——其中 7 份原本带本机账户名，新两份又各带 1 处，合计 **9 份**，**已全部就地脱敏**，整目录 add 不再有风险，见第 3 节拦路第 3 条）、`yuyu-book/PRODUCTS.md`。**`CONTRIBUTING.md` 本轮没动**（不在脏区） | 站点契约测试（`test_docclaims` 9 tests）重算 README/STRUCTURE 里的每个数字，文档与数字不能分两次改；`pages.yml` 的 `git diff --exit-code docs/` 也只认这一组 |
| 5 | `test: product isolation` | `yuyu-book/tests/test_product_isolation.py` | 单文件；必须在 1 之后（依赖 registry 的 product 派生） |
| 6 | `ci: isolate omp job` | `.github/workflows/{book,pages}.yml` | **建议与 omp SPEC 的推送窗口协调**；`omp/` 不进 main 之前 `book.yml` 的 omp job 会红（YAML 注释已写明） |
| 7 | `docs(omp): …` | `omp/**` 366 条 **加上 6 份不在 `omp/` 底下的 omp 配置**：`yuyu-book/{glosses,manifest,notes,revisions,sources,reading-paths}-omp.json` | 归 omp SPEC 移交清单，御舆这边不替它写 message。**这一组的坑**：只 `git add omp/` 会把那 6 份落下，而 `book.yml` 的 omp job 靠 `manifest-omp.json`/`sources-omp.json` 才跑得起来——少一份就是「YAML 没问题但 job 红」，很难查。更糟的是 `reading-paths-omp.json` **至今是 `??`（连索引都没进）**，其余 5 份已在索引里 |
| 0 | `chore(repo): keep local scratch and raw captures out of the index`（可选，也可并进 6） | `.gitignore`：本轮加的两条 —— `/.scratch/`（89 条一次性探针、HEAD 对照树、分离式 CI 日志）与 `omp/facts/live-*/models-list.txt`（原始 `omp models` 实况，会把私有网关名连模型清单一并打出来；书里引用的是同目录 `*-redacted.txt`） | 单独一条是因为它**只改忽略规则、不动内容**，回滚代价最小；而且它必须在第 7 组之前落地，否则 `git add -A` 会把两份都拖回去 |

> **16:4x 停机后复数（取代本节开头那个 479）**：调研工作流 stop、四个根目录文件挪进 `yuyu-book/.scratch/kimi-cursor-survey/` 之后，
> 脏区 **483** 条，两次读数（相隔 3 s）完全一致 —— 并发写入确实停了，上面 489/500/487 那一串作废为「抖动期间的瞬时值」。
> 分项：`A ` **293** · `AM` **30** · ` M` **60** · `??` **100**（293+30+60+100=483，与总数闭合）。
> 按本节口径分桶，**逐桶相加正好等于 483**：`omp/**` 366 · `docs/**` **47** · `en/` **19** · `yuyu_book/*.py` 12 ·
> `yuyu-book/*.json|md|build.py` 11 · 中文正文 **18** · 根文档 5（`.gitignore` `Makefile` `README.md` `STRUCTURE.md` `OVERHAUL-SPEC.md`，
> `00-前言.md` 归中文正文那一桶，不重复计）· `.github/` 2 · `scripts/` 2 · `yuyu-book/tests/` 1。
> 与 15:3x 那次（479 = 293/30/58/98）对账，四条增量都有名有姓：
> `docs/**` 45 → 47 是 `logs/rebuild-{book,omp}-pdf-20261104-161046.log` 这一对；
> ` M` 58 → 60 是 `附录/D-术语表.md` 与 `en/Appendices/D-Glossary.md`（两条都是 ` M`，不是 `AM`——它们已在索引里、本轮又改了工作树）；
> 中文正文 17 → 18、`en/` 18 → 19 也是同一件事的两面（附录 D 落地必须双语同增，`check_bilingual_parity` 只认这个）。
> **提交分组的人请注意两件事**：① `docs/yuyu-overhaul/ACCEPTANCE.md` 与 `docs/yuyu-overhaul/PDF-PAGES.md` 至今是 `??`——
> 连索引都没进，`git add omp/ docs/` 这类按目录 add 之前必须确认它们在里面，否则这两份账本会整份漏掉；
> `BASELINE.md` 与 `docs/YUYU-OVERHAUL-SPEC.md` 是 `AM`（索引里有旧版，工作树又新了）。
> ② 那四份调研文件**不会**出现在脏区里（`git check-ignore -v` 命中 `.gitignore:11` 的 `yuyu-book/.scratch/`），
> 也就是说 `git add -A` 不会误收它们，也不必手工排除。

### 提交前必须先处理的事（第 1、2、3 条本轮**已办**，第 4 条是给执行提交的人的告诫）

1. ~~**`omp/facts/live-18.16.0/models-list.txt` 已经在索引里**~~ —— **已摘**（13:5x）：
   `git restore --staged omp/facts/live-18.16.0/models-list.txt`，文件还在盘上（5118 字节，未被删），
   现在状态是 `??`，且 `.gitignore:85` 的 `omp/facts/live-*/models-list.txt` 让下一次
   `git add -A` 不会把它拖回来。索引条目 324 → **323**。
   为什么单摘这一份：全量扫过 136 个已暂存的 `omp/facts/**`，只有它的模式命中是真的
   （`<私有网关甲>`、`<私有网关乙>` 两个网关名 + 21 个私有型号，含 `<私有型号>`）；
   其余命中项要么是上游文档里的示例（`/Users/alice`），要么是 `--token` 一类旗标名。
2. ~~**根 `.scratch/` 未跟踪且未被忽略**~~ —— **已加规则**：`.gitignore:91` 的 `/.scratch/`
   （写成 `/.scratch/` 而不是 `.scratch/`，是为了**只**盖仓库根那一份，
   `yuyu-book/.scratch/` 由 `:11` 管，两条口径分开）。盘上 89 条一个没删，只是不再进脏区：
   脏区 567 → 477。已核对新规则**没有误伤任何已跟踪文件**——`git ls-files -i -c --exclude-standard`
   列出 12 条 `.superpowers/sdd/*`，那是那里自带的 `*` 规则（历史状态，靠 `git add -f` 收的，与本轮无关）。
3. **本机 Windows 账户名写在 omp 的正文里**（一开始它**不是**御舆侧的活——不该由我替第二分册改书稿口吻；
   用户 14:5x 点头后按下面「五处同改」执行，动的是路径写法，不是叙述语气）。
   下面一律用 `<用户名>` 代指那个词——它本身就是要脱敏的东西，所以这份账里也不把它写全：
   全仓按该词扫，命中 5 处真路径 + 2 处无害，另外还命中了我自己写的御舆文档与 7 份运行日志（见本节末）：

   | 位置 | 内容 | 性质 |
   |------|------|------|
   | `omp/ch04.md:115` | `…（例如 C:\Users\<用户名>\.bun\bin\omp.exe）` | 出版物正文里的真机路径 |
   | `omp/ch07.md:202` | `本机已验（18.16.0）回 C:\Users\<用户名>\.omp\agent` | 同上，且与下面那份 capture 互为引用 |
   | `omp/ch29.md:3` | `…你的技能里写着 C:\Users\<用户名>\…` | 故事里的「反面例子」，但用的真是你的机器 |
   | `omp/VERIFY.md:106` | `C:\Users\<用户名>\.bun\bin\omp.exe` | 核对记录 |
   | `omp/facts/live-18.16.0/config-path.txt:1` | 整个文件就一行 `C:\Users\<用户名>\.omp\agent` | 上面三条的证据源 |

   无害的两处：`yuyu-book/manifest-omp.json:7` 里的 `zhuguang-ZFG` 是公开仓库 URL 的一部分（仓本来就挂在这个账号下，
   指它不增加任何暴露）；SPEC 末尾那行「执行者：Qoder CLI（… 的机器、分支 `p3-pages-split`）」是同一个 GitHub handle
   的署名，不是路径（它原来记作 `docs/YUYU-OVERHAUL-SPEC.md:1076`，M9 补字后行号已漂，按内容找别按号找）。
   **要改就得五处一起改**：正文改成 `%USERPROFILE%\.bun\bin\omp.exe` 这类中性写法（`omp/ch04.md:115`
   前半句本来就是这么写的，括注是后加的），capture 换成脱敏版并同步 ch07 那句引用；
   只改 capture 不改正文，会让「本机已验」指向一个内容对不上的文件。
   **已办（用户点头「同意继续」后执行，五份文件的 mtime 都是 14:27）**。按「五处同改」做完：

   | 位置 | 改法 |
   |------|------|
   | `omp/ch04.md:115` | 删掉那条真路径括注，只留 `%USERPROFILE%\.bun\bin\omp.exe`，括注改成「展开成你的用户主目录，各人不同」 |
   | `omp/ch07.md:202` | 值写作 `%USERPROFILE%\.omp\agent`，并注明那份 capture 已就地脱敏、真值本机重跑 `omp config path` 即得 |
   | `omp/ch29.md:3` | 故事句里的路径写作 `C:\Users\<你的用户名>\...`，语气不动 |
   | `omp/VERIFY.md:106` | 主写法换成 `%USERPROFILE%\.bun\bin\omp.exe`，展开式写作 `<用户名>`，并加一句「本机账户名不入书稿」 |
   | `omp/facts/live-18.16.0/config-path.txt` | 整份重写为脱敏 capture（27 字节 → 329 字节，CRLF 不变）：`$ omp config path` 头 + 脱敏说明 + `C:\Users\<用户名>\.omp\agent` + `exit=0`，沿用同目录 `models-find-flash-redacted.txt` 的先例 |

   **这里有一条会咬人的机制，值得单记**：这 5 份**都已经在索引里**，改完工作区并不等于改完索引——
   `git commit` 提交的是 index blob，不 add 就会把带泄漏的旧版本提交出去。本轮对
   `omp/{VERIFY,ch04,ch07,ch29}.md` 与 `omp/facts/live-18.16.0/config-path.txt` 这 5 个显式路径跑了
   `git add`（**这是本 SPEC 执行期内御舆轮次第一次、也是唯一一次 `git add`，只刷 index blob，未 commit/push**）。
   复验口径必须是索引而非工作区：`git -c core.quotepath=off grep -l -I --cached "Users.$(…getuser…)"`
   —— 结果从 **11 份**缩到 **6 份**，且这 6 份全是 HEAD 既有、与 HEAD 逐字节相同的 video 侧文档
   （见本节末与第 9 条第 4 项；这一格上一版写的是「9 份缩到 4 份」，那是同一个分隔符坑量出来的）。
   索引总数不变（323），但分布从 292 `A` + 31 `AM` 变成 **293 `A` + 30 `AM`**（`omp/ch29.md` 由 `AM` 转 `A`）。

   **御舆这一侧也一并扫干净了**，而且比原计划多做了一步：
   - `docs/YUYU-OVERHAUL-SPEC.md`（2 处）与 `docs/yuyu-overhaul/BASELINE.md`（1 处）原本携带我自己
     抄进去的字面路径（这两个文件的**索引 blob 里没有**——那是本轮才写进工作区的），已改写为
     `C:\Users\<用户名>` 占位；本文件的表格与扫描段同批改写。
   - **日志没走「不入仓」或「加忽略规则」那两条路，走了第三条**：就地脱敏。理由很实在——文档里对
     被脱敏的那 7 份日志的引用有 **22 处**（14:4x 实测；这份账本后来自己又提了一次 `122150`，
     14:5x 复数是 **23** —— 引用数会随记账增长，别当契约），摊在 5 份文档上
     （`YUYU-OVERHAUL-SPEC.md` 7、`BASELINE.md` 7、
     本文件 5、`PDF-PAGES.md` 2、`SITE-LINKS.md` 1；7 个文件名里 6 个被引到，只有
     `ci-local-yuyu-20261104-122150` 一次都没人引用——它照样脱敏，因为 add 进去就是暴露），
     加忽略规则就得把这 22 句全改成「本机留存」，
     而日志的**证据价值在退出码、计数与时长**，绝对解释器路径只是噪声；把它替换掉不损伤任何一条宣称。
     第一批共替换 **26 处**：`docs/yuyu-overhaul/logs/` 7 份 23 处（`ci-local-yuyu-20261104-{100401,122150,125209}`
     各 6、`smoke-both-after-xref` 2、`doctor-checkfast-after-xref` / `rebuild-book-pdf-after-xref` /
     `rebuild-book-pdf-both` 各 1）+ `omp/facts/live-18.16.0/{plugin-doctor,tiny-models-list}.txt` 各 1 +
     `omp/overhaul/logs/rebuild-omp-pdf-after-appD.log` 1。后三份是**这次扫描新查出来的**，不在原五处清单里。
     替换是字节级、只动路径里账户名那一段，行数与行尾一个没变。
     **两个尖括号别混**：真落进文件里的占位符是 `<用户名>`（跟 `models-*-redacted.txt` 的先例一致），
     而本账本文字里写的 `<账户名>` 只是**叙述用**的代称、不是任何文件里的字节——
     要复算落盘面就 grep `<用户名>`，grep `<账户名>` 只会找到这几本账。
     所以上面第 4 组那句「14 份 `logs/`」**重新成立**，不需要 `git add -f`，也不需要改任何引用。
     **15:1x 起这句要读成 16 份**（两份新构建日志各 1 处、同样就地换 `<用户名>`，替换前后 LF/CR 条数一字不差），
     「整目录 add 不再有泄漏风险」这条对新两份同样成立——15:3x 面上复扫：1184 条路径、形状命中 13 处，新日志贡献 0。
   - **14:4x 又翻出一批，而且比前面全部加起来还多**：`omp/facts/live-18.16.0/` 的 4 份 JSON capture
     —— `skill-list-json.txt` **54** 处、`agents-unpack-json.txt` **7**、`plugin-doctor-json.txt` **1**、
     `ps-json.txt` **1**，共 **63 处**，全是 `C:\\Users\\<账户名>\\...` 这种 JSON 转义形态（`filePath`、
     `baseDir`、`targetDir` 字段）。这四份都是 `??` 且**没被忽略**，属于第 7 组 `git add omp/...` 一把梭
     就会发出去的面。它们被 4 份 omp 正文引用共 **10** 次（`omp/ch29.md` 6、`omp/ch13.md` 2、
     `omp/ch30.md` 1、`omp/appendix-C.md` 1；口径是 `grep -o … --include=*.md omp/`，
     本账本为了记这件事自己又添了几处，不在那 10 里），所以同样走就地脱敏而不是加忽略规则
     ——加规则会让这 10 句变成空指向。
     替换保留各文件自己的分隔符形状（JSON 里仍是 `\\`），改完四份**都还能 `json.loads` 通过**。
     两批合计 **89 处**机器输出替换（26 + 63）。占位符本身的现存总数别在这里抄死——
     本文件每写一次 `<用户名>` 它就 +1；要复现这个数就扫可提交面：
     `git ls-files` 并上 `git ls-files --others --exclude-standard`，逐份数 `<用户名>`。
   - 终检口径：把「可提交面」（`git ls-files` 的 1086 条 ∪ `--others --exclude-standard` 的 96 条，
     共 **1182 个路径**）逐个按**路径形状**扫一遍，结果从原来的 77 处降到 **13 处**，
     **15:3x 复跑同一条：`--others` 涨到 98（就是这次新增的两份 `rebuild-*-pdf-20261104-151751.log`）、
     面变 **1184 条**，命中仍是 **13 处 / 6 份**，新日志各贡献 0（每份原本 1 处，已换 `<用户名>`）；
     面上 `<用户名>` 占位符当时 **119 处**——这数每写一次账本就涨，别抄死，按上一条的命令现算**。
     剩下这 13 处**全在 TRACKED 且与 HEAD 逐字节相同**的 6 份 video 侧文档里
     （`docs/video/ch04/STATUS.md` 6、`docs/video/ch03/STATUS.md` 3、
     `docs/video/ch01/gate-checklist.md` 1、`video/ch01/hf-remake/REMAKE-V{3,4}-REPORT.md` 各 1、
     `video/ch05/hf-remake/short/assets/sfx/CREDITS.md` 1）——本 SPEC 的提交面不新增任何一处暴露。
     **本节上一版把这里记成「4 份 9 处」，那个数是错的**，错因见下面第 9 条第 4 项：
     那两份多出来的文档写的是 JSON 转义形态 `Users\\<账户名>`（两个反斜杠），
     而 `Users.` 这个「一个任意字符」的通配匹配不上两个字符。
     复核命令别把词写全，现取现扫（正则里给足 1–3 个分隔符）：
     `git -c core.quotepath=off grep -c -E "Users[/\\\\:]{1,3}$(python -c 'import getpass;print(getpass.getuser())')" HEAD`。
     也就是说这些脱敏是**止损、不是首次暴露**；要清进历史得 rebase/filter-repo，那是本 SPEC 之外的另一件事，
     本轮没碰、也不建议顺手碰。
4. **别用 `git add -A` / `git add .`**：479 条脏项里 366 条属 omp 册（omp 那 366 一条没涨，涨的 2 条在 `docs/**`），第 7 组之外的一把梭会把
   两本书的账搅在一起。按本表逐组 `git add <显式路径>`；第 7 组尤其要带上那 6 份 `yuyu-book/*-omp.json`。

### 推送后才成立的事

- GitHub Actions 真绿（SPEC §6.2）。`omp` job 的红/绿取决于 `omp/` 是否进 main。
- `pages.yml` 的 `git diff --exit-code docs/`（SPEC §6.4）：推送前重跑一次 M3 那两条再生命令。
  本轮实测「重生后 `git diff` 为空」，所以这条门禁现在是松的——但正文若再变，它会立刻咬住。
  **一个只有 Linux 才暴露的口径**：三个生成器（`build_site_portal.py:138`、
  `build_beginner_reader.py:517`、`build_illustration_gallery.py:176`）都用
  `write_text(..., encoding="utf-8")`，没传 `newline="\n"`。本机 `core.autocrlf=true` 于是工作区是
  CRLF、仓里是 LF，靠 Git 归一才看不出差别。CI 里两端都是 LF，所以不会红；但**任何关掉
  `core.autocrlf` 或在 Linux 上重新生成再回 Windows 提交的人**，会拿到一整份文件的 EOL diff。
  真要根治就是给这三行加 `newline="\n"`，或者加 `.gitattributes`（现在**没有** `.gitattributes`）。
  本轮没改——那是构建器的事，不该混在文档收口里。

---

## 4. Git 确认（M9 Step 4）

```
$ git status -sb
## p3-pages-split...origin/p3-pages-split
 M .github/workflows/book.yml
 ...
```

实测（13:2x，本轮最后一次）：

- 分支行 `## p3-pages-split...origin/p3-pages-split` **没有 `[ahead N]` 也没有 `[behind N]`** ——
  `git rev-list --count --left-right HEAD...origin/p3-pages-split` = `0 0`。
  这就是「零 commit、零 push」的硬证据，比“我记得没跑过 git commit”可靠：
  本地 `HEAD` 与远端分支指到同一个提交。
- `git log --oneline -1` = `951c0ef refactor(book): P3.4 拆出 frontmatter/backmatter，pages 保留正文组件`
  —— 与本 SPEC 执行开始时同一个提交；`git reflog` 最新一条也是它（2026-11-03）。
- 脏区总量 **477** 条（`--porcelain -uall`；本节第 1、2 条拦路处理前是 567）：索引里带 `A`/`AM` 的
  **323** 条（纯 `A` 293 + `AM` 30，14:5x 实测；13:5x 读数为 292/31，差的 1 条见第 5 节第 8 条）、
  工作区已跟踪未暂存 ` M` **58** 条、未跟踪 `??` **96** 条。
  **15:3x 为「生成本地pdf」重排后再数一次：总量 479 = `A ` 293 + `AM` 30 + ` M` 58 + `??` 98。**
  涨的 2 条正是 `docs/yuyu-overhaul/logs/rebuild-{book,omp}-pdf-20261104-151751.log`
  （`docs/**` 因此 43 → **45**），`A`/`AM`/` M` 三档一条没动 —— 构建不碰索引，这条得实测才敢说。
  `git status -sb` 折叠行数这次与 `-uall` **同为 479**（14:4x 那两个读数也一致），
  说明脏区里已没有「整目录未跟踪」被折叠的情形。
  其中 `omp/**` 366、`docs/**` 43（这两个数得用 `git -c core.quotepath=off status --porcelain` 数——
  中文路径默认被八进制转义引起来，`^.. omp/` 会漏掉 `A  "omp/00-前言.md"` 这类行，实测差 1 条）；
  `.scratch/**` 已归零（盘上 89 份文件、顶层 30 项都在，只是被 `/.scratch/` 挡在脏区外；
  本轮清掉了自己生成的 `.scratch/gitignore-head.tmp`——它与 `git show HEAD:.gitignore` 逐字节相同，
  一条命令就能复原，故 90 份/顶层 31 项 → 89 份/30 项）。
- **16:49 再数一次（当时的当前值，17:5x 已被取代）**：`git status --porcelain -uall` = **483** 条
  （`A ` 293 / `AM` 30 / ` M` 60 / `??` 100），不带 `-uall` 同样是 483 —— 未跟踪项已全是逐文件行，目录折叠不复存在。
  `git status -sb` 非空行数 **484** = 1 行分支头 + 483 条，与 `-uall` 对齐。
  分支行仍然**没有 `[ahead N]` / `[behind N]`**，`git log --oneline -1` 仍是 `951c0ef`（与本 SPEC 开始时同一个提交）——
  「零 commit、零 push」到 16:49 依然成立。
- **17:5x 再数一次（当时的当前值，18:5x 已取代）**：`git status --porcelain` = **484** 条
  （`A ` 293 / `AM` 30 / ` M` **61** / `??` 100），不带 `-uall` 与带 `-uall` 同为 484，
  `git status -sb` 非空行数 **485** = 1 行分支头 + 484 条。比 16:49 那次只多 **1** 条，
  多的是 `yuyu-book/tests/test_docclaims.py`——为追 `en/**` 那道汉字闸收窄了术语条目数的度量口径
  （26,920 → 27,484 B），由干净转为 ` M`。**本轮没有往仓库里新增任何一个文件**，所以 `??` 仍是 100：
  这轮的构建日志写在仓库外的临时文件里，不进 `docs/yuyu-overhaul/logs/`（原因见第 5 节第 11 条末段），
  `logs/` 因此停在 **18 份**（本轮 0 新增，最新两份仍是 16:31 那对 `rebuild-*-pdf-20261104-161046.log`）。`docs/**` 用 `git -c core.quotepath=off status --porcelain | grep -c "^.. docs/"`
  现数是 **47** 条。分支行仍然**没有** `[ahead N]` / `[behind N]`，`git log --oneline -1` 仍是 `951c0ef`
  ——「零 commit、零 push」到 17:5x 依然成立。
- **18:5x 再数一次（当时的当前值，20:0x 已取代）**：`git status --porcelain` = **486** 条（`A ` 293 / `AM` 30 / ` M` **62** / `??` **101**），`git status -sb` 非空 **487** = 1 行分支头 + 486。与上一轮最要紧的差别不是那 +2，是**`-uall` 与不带 `-uall` 又分开了**：486 vs **492**，差 6 = 七幅 omp 篇题刻被 `yuyu-book/illustrations-omp/` 这一条目录行折叠掉了。上一轮明写「脏区里已没有『整目录未跟踪』被折叠的情形」，这句话只活了一轮就被自己的新目录推翻——**只要往仓库放一个新目录，折叠就回来**，所以本节后面任何「脏区总量」都得同时给两个口径。` M` +1 归 `yuyu-book/tests/test_art.py`（排除法，理由见 SPEC M9 Step 4 那条）。`docs/**` 47、`omp/**` 366、`logs/` 18 份三条都没动；分支行仍然**没有** `[ahead N]` / `[behind N]`，`git log --oneline -1` 仍是 `951c0ef`——「零 commit、零 push」到 18:5x 成立。
- **20:0x 再数一次（本节当前可引用的值）**：`git status --porcelain` = **486** 条（`A ` 293 / `AM` 30 / ` M` **62** / `??` **101**）——四个桶与 18:5x 逐桶相同，`git status -sb` 非空仍是 **487**。这一轮发了 **39 枚 omp 章徽**（`yuyu-book/illustrations-omp/omp-*.svg`），脏项总数却一条没涨：它们落进了一个本来就整目录未跟踪的目录，git 继续只报 `?? yuyu-book/illustrations-omp/` 那一行。这是对 18:5x 那条结论的必要补充——「只要往仓库放一个新目录，折叠就回来」只说了前半句，**放在已有未跟踪目录里的新文件连折叠都不触发**，靠目录行看得见它、靠文件名看不见。两个口径于是再次分开：486 vs `-uall` **531**，`??` 101 → **146** = 101 − 1 条目录行 + 46 份 SVG（7 幅篇题刻 + 39 枚章徽），531 − 492 = **39** 正好是本轮枚数。` M` 不翻牌的原因见 SPEC M9 Step 4 的 20:0x 那条（本轮写过的 10 个已有文件早在各自桶里）。**本轮又踩了一次第 336 行写明的引号陷阱**：`git status --porcelain | grep -c ' omp/'` 现数 **365**，比 pathspec 的 **366** 少 1，漏的还是 `A  "omp/00-前言.md"`——数目录一律带 pathspec。`docs/**` **47**、`omp/**` **366**、`yuyu-book/**` **27**、`logs/` 仍 **18 份**（日志照旧写在仓库外，见第 5 节第 11 条末段）；分支行仍然**没有** `[ahead N]` / `[behind N]`，`git log --oneline -1` 仍是 `951c0ef`——「零 commit、零 push」到 20:0x 成立。复现：`git status --porcelain | cut -c1-2 | sort | uniq -c`、`git status --porcelain -uall | wc -l`、`git status --porcelain -uall -- yuyu-book/illustrations-omp/ | wc -l`（= 46）。
- 构建产物一条都不在里面：`yuyu-book/dist/`（`.gitignore:8`）与
  `yuyu-book/.scratch/`（`:11`）都被盖住；`__pycache__/`（`:4`）也盖住了护栏脚本跑出来的 .pyc。

**预期且要求**：仍然脏、仍然没有 commit。SPEC 执行期到此结束；
用户下一条关于提交的指令才是执行依据。在那之前，任何人（包括下一个 agent）看到这份文件，
都应把它当作「未提交」状态的说明，而不是「已合并」。

---

## 5. 本轮遗留（写清楚，免得被当成已完成）

1. **`check_bilingual_parity.py` 已接入 GitHub Actions 配置（2026-11-04 续做）**。
   `book.yml` 与 `check-book.yml` 均在安装 Python 依赖后单独运行此检查；
   `book.yml` 的 push / pull_request 路径过滤也覆盖脚本自身的修改。
   `bookctl check --fast` 仍为六步，本地 `ci-local-yuyu.ps1` 保留原有调用。
   远端执行结果须在后续获准提交、推送后验证。
   本轮本地验证：Python 3.13 执行 `python scripts/bookctl.py check --fast`
   六步全部通过（仓库测试 39 项、构建器测试 515 项、176 份 Markdown、
   333 张 Mermaid 图，内容与图表错误均为 0）。双语检查 20 单元通过；
   两份 workflow YAML 可解析，独立检查步骤及两类路径过滤均已核对。
   缺文件、H2 差 3、Mermaid 不等三类反例均判失败。
2. **K9 的「可选」那格仍未做**：`附录/D-术语表.md` 里那一节「丛书共享词」。
3. **K11 的根 `OVERHAUL-SPEC.md` 还在盘上**，去留是提交窗口的事。
4. **中文通俗化不等于净收益**：`BI-AUDIT.md` 第 3 节——BASELINE 里 ch10/ch11 那两条「被 x」
   是本轮 B3 批次自己引进又清掉的临时回潮，对 HEAD 而言 zh 是 0→0。对外别说「消掉了多少处」，
   说「与提交版持平，且没有新增」。
5. **页数宣称两套口径**：README 写 CI/Noto 的 505·536，本机雅黑实测 518·569。
   `PDF-PAGES.md` 解释了为什么，`ci-local-yuyu.ps1` 只放行这一类差异。
6. **M0 那一格仍保持不勾，且这里不粉饰**：SPEC `:207` 原文写「本 SPEC 执行期内确实一次没跑过
   `git add`」，这半句被本轮自己的证据推翻了——`git-status-baseline.txt` 里 `OVERHAUL-SPEC.md` 与
   `docs/YUYU-OVERHAUL-SPEC.md` 当时是 `??`，现在两个都是 `A`，所以 M0 之后确实有窗口 `git add` 过
   （看暂存面是 omp 那一侧的轮次）。已就地改成「commit/push 这条是真的（`0 0`），git add 这条不能这么写」。
   这条不影响「零 commit」的结论，影响的是**下一句**：323 条已在索引里的东西（本轮从 324 摘掉那份
   带私有网关名的文件，见第 3 节拦路第 1 条），一旦有人敲 `git commit` 就会**整批**连带进去——
   按顶层目录数是 **301 条 `omp/` + 12 条 `docs/` + 9 条 `yuyu-book/` + 1 条根 `OVERHAUL-SPEC.md`**
   （`git -c core.quotepath=off diff --cached --name-only | sed 's#/.*##' | sort | uniq -c`），
   也就是第二分册整本书加上它的构建配置。那 9 条 `yuyu-book/` 是 5 份 `*-omp.json`
   （`glosses`/`manifest`/`notes` 为 `AM`，`revisions`/`sources` 为 `A`）+ `PRODUCTS.md` + 3 份构建器
   `.py`；第 6 份 `reading-paths-omp.json` **仍是 `??`、不在索引里**，所以「6 份 omp 配置」这句
   以后别照抄——索引里只有 5 份。
   **这里要撤回一个我之前写混的数**：那句「其中包括 366 条 `omp/**`」用的是**脏区**口径
   （`git status --porcelain -uall` 里 omp 占 366），不是索引口径；`git commit` 只看索引里的 301 条，
   366 里剩下的 65 条要么未跟踪、要么已跟踪未暂存，不 add 就进不去。两个口径别串门。
   摘掉那一条只是把最尖的泄漏面拔掉，**不等于索引已经干净**；真要分 7 组提交，得先把索引整个重置
   （`git reset` 会把 323 条全部退回工作区、一个文件都不删），再按第 3 节逐组显式 `git add`。
   这一步动静不小，等用户明确下令再做，本轮没做。
7. **box 备份没同步**：M9 的 `Files: Sync: box /workspace/omp-book/YUYU-OVERHAUL-SPEC.md` 在这台机器上
   不可执行——`/workspace/omp-book` 不存在（`ls -d` 无此路径）。SPEC `:124` 已写明真源优先级是
   本机仓 > box，`BASELINE.md` 「真源」那一节（现 `:102`）也记了「本次执行未做同步（无该环境访问通道）」
   ——这条也是行号引用，它会跟着漂，按内容找。
   要同步得换到有那个挂载的环境做，不是本轮漏了。
8. **原来那三个泄漏面已办，第四个是这轮复扫时新冒出来的，也办了；只剩一个决定**：
   ① omp 那 5 处 `<用户名>` —— **已按「五处同改」做完**，并因它们已在索引里而 `git add` 刷新了 index blob
   （细节与复验口径见第 3 节拦路第 3 条）；
   ② `docs/yuyu-overhaul/logs/` 那 7 份日志 —— **已办，且既不是「不入仓」也不是「加忽略规则」**：
   就地脱敏（连同这次新扫出的 `omp/facts/live-18.16.0/{plugin-doctor,tiny-models-list}.txt` 与
   `omp/overhaul/logs/rebuild-omp-pdf-after-appD.log`，共 26 处），这样 22 处「见 `logs/x.log`」的引用
   仍然指得到真文件，第 4 组也仍可整目录 add；
   ③ **第 14:4x 复扫新查出来的第四面**：`omp/facts/live-18.16.0/` 的 4 份 JSON capture 共 **63 处**
   （`skill-list-json` 54、`agents-unpack-json` 7、`plugin-doctor-json` 1、`ps-json` 1），
   形态是 `Users\\<账户名>`（JSON 转义，两个分隔符），4 份都是 `??` 且没被忽略，
   被 4 份 omp 正文引用 10 次 —— 同样就地脱敏、保住引用，改完四份仍是合法 JSON。
   两批机器输出合计 **89 处**；可提交面因此从 77 处降到 13 处，那 13 处全在与 HEAD 相同的旧文档里。
   这一面是**第 9 条第 4 项那个分隔符坑直接造成的漏报**，不是当初不想办。
   ④ **还剩这个**：索引里 323 条要不要整体 `git reset` 再按 7 组重放。本轮**有意不做**，理由写死在这儿：
   本 SPEC 禁止 commit，那么 reset 之后无法逐组建起 7 个 commit，只是把别人那一轮留下的暂存记录抹掉、
   原地再 add 回同一批文件——**收益为零、代价是丢信息**。真正的重放必须发生在提交窗口里
   （reset → add 第 k 组 → commit，k=1…7 交替），那需要用户当场解除「不 commit」这条。
   另外两条与「这个词」有关的事实，别再当成已完成：
   - 同一个词**早在 HEAD 里**（**6 份** video 侧文档 **13 处**，见第 9 条第 4 项）。①②③是**止损**，不是清除；
     要「仓里从此查不到它」得改历史（rebase / filter-repo），那是本 SPEC 之外的另一件事，本轮没碰。
   - 工作区改了 **不等于** 索引改了。今后任何一处再脱敏，只要那个文件已在索引里，
     就得配套 `git add <显式路径>`，否则提交出去的还是带泄漏的旧 blob；
     复验要用 `--cached`，不能只看 `git status`（`AM` 也会显示成「已暂存」的样子）。
9. **这一轮复验时踩到七条会让扫描「假干净」或「假报警」的坑，值得钉住**（**16:4x 复测又加六条，共十三条**，第 8–13 项在本条末尾）：
   - `git grep -I` 会**静默跳过二进制**。隐私扫描少了 `-I` 才算完整：本轮两条都跑了
     （`git grep -l --cached "Users[/\\]<账户名>"` 与带 `-I` 的同一条），结果同为 6 份 HEAD 既有文档
     共 13 处，
     所以没有泄漏被 `-I` 藏住 —— 但这是**跑出来的**，不是 `-I` 那条的保证。索引共 1086 条，逐条
     `git cat-file` 也能覆盖，只是要一次批量、别手写循环。
   - **别用 `git show :/<路径>` 读 index blob**。`:/<文本>` 是「按提交信息正则找提交」的修订语法，
     `:/omp/ch04.md` 会被解析成一次提交信息搜索而不是阶段 0 的对象；本轮因此拿到过一次
     「索引 0 命中」的**假绿**。读索引只有两条靠谱路子：`git grep --cached`，或
     `git ls-files -s` 取 SHA 再 `git cat-file blob <sha>`。
   - 本机账户名 `<账户名>` 是 git 署名 `zhuguang-ZFG` 的**前缀**。裸扫 `<账户名>` 会命中 63 处公开 handle
     （多数在 `omp/facts/live-18.16.0/skill-list-json.txt` 这类 JSON 的作者字段里），把一次干净扫描
     报成大片泄漏。`zhuguang-ZFG` 出现在公开仓库 URL 里不构成额外暴露（见本节第 3 条「无害的两处」）。
   - **最阴的一条：分隔符的个数。** 只写 `Users.<账户名>` 或 `Users[\\/]<账户名>` 都只容得下**一个**
     分隔符，而 JSON 里的路径是 `Users\\<账户名>`（转义后是两个字符）。本轮因此把 HEAD 既有泄漏面
     报成「4 份 9 处」，实际是 **6 份 13 处**——多出来的 `docs/video/ch03/STATUS.md`（3 处）与
     `docs/video/ch01/gate-checklist.md`（1 处）正是转义形态。同一形状还骗过了对 4 份 omp capture 的
     初筛，让我一度以为可提交面已经干净，其实那 63 处一直在盘上。正确写法是给足重复：
     `Users[/\\]{1,3}<账户名>`；HEAD 面的复算命令在本节第 3 条末尾那条。
     （本文件上一版把这条「正确写法」抄成了 `Users[/\\:]{1,3}`，类里多一个冒号——冒号不参与任何
     真实路径，所以它只会让读者以为自己和这条口径等价；15:3x 顺手改回。）
   - 占位符里的分隔符要跟原文一致。日志里是 `Users\<用户名>`（反斜杠），我拿
     `grep -c "Users/<用户名>"`（正斜杠）去复验，得到 0 命中、一度以为脱敏没落盘。
     复验要么只数 `<用户名>`，要么按 `[\\/]` 匹配；本轮按 mtime 复核更硬：7 份日志与 2 份 capture
     都是 14:30、`omp/overhaul/logs/` 那份 14:31、4 份 JSON capture 是 14:57，与 89 处替换一一对上。
   - **第 6 条（15:2x，新）：字符类里的反斜杠会吃掉紧跟它的那个字符。** 我用字符串拼接生成模式，
     拼出来是 `[\/]` —— 看着像「反斜杠或正斜杠」，实际是「反斜杠把 `/` 转义了，类里只有 `/」，
     反斜杠**不是成员**。拿它扫 15:1x 那两份新日志得 **0 命中**，读起来完全像「构建日志本来就干净」，
     而每份里实打实有 1 处 `C:\Users\<账户名>\scoop\...`（解释器自报命令行）。
     可靠写法两种：把两个反斜杠显式放进类（`[\\/]`），或者干脆用交替 `(?:\\\\|/)`。
     **并且任何 0 命中都必须先拿一条已知会命中的样本自证**——本轮加的三条探针
     （单反斜杠、正斜杠、双反斜杠）现在每次都跑，跑不过就报错而不是报「干净」。
   - **第 7 条（15:2x，新）：`git ls-files ''` 是空 pathspec，不是「不加过滤」。**
     第一遍表面扫描把 flag 一律当 argv 尾巴传（tracked 那次传了空字符串），
     结果 `tracked=0 others=0 surface=0`、命中 0 —— 一次彻头彻尾的假绿，而且它长得最像好消息。
     修法是 flag 为空就**不要传那个参数**，再对空面显式断言（`assert tracked`），
     让「面为空」变成硬失败而不是一个可以抄进账本的数字。
   - **第 8 条（16:4x，新）：工具层会吃掉命令文本里的一级反斜杠。** 我写 \\，到达 Python 只剩 \。
     本轮三次触发：① 字符类 `\[/]` 那类模式失效（16:2x「新日志 0 命中」就是它）；
     ② `str.replace('\\','/')` 变成 `replace('\','/')` → SyntaxError；③ `'\' not in p` 同样 SyntaxError。
     对策：**含反斜杠的 Python 不走 shell 内联**，落成仓库外的脚本文件再执行（本轮就是 `edit_acceptance*.py`），
     或在脚本里用 `chr(92)` 拼。占位符也不能用会被正文里已有字母串吞掉的短记号——
     我第一版用 `B`，`.replace('B', …)` 当场把 `BASELINE.md` 改成 `\ASELINE.md`。
   - **第 9 条（16:4x，新）：文本模式读文件会折叠 CRLF，字节数与 CR 数一起少算。**
     第一遍量 16:1x 那两份新日志，我报出「604 B / LF 8 / **CR 0**」，盘上真实是 **612 B / CR 8 / LF 8**——
     `open(...,encoding=...)` 已把 \r\n 变成 \n，再 `len(s.encode())` 自然少 8 个字节。
     对策：凡量字节、量行尾，一律 `open(...,'rb')` 在字节上做。
   - **第 10 条（16:4x，新）：阳性对照不能拿已脱敏的旧样本。** 那次 0 命中我顺手拿 `rebuild-*-151751.log` 当对照，
     可它 15:3x 已被换成 `Users\<用户名>`，而 `<` 不在 `[A-Za-z0-9._-]` 里，**必然 0 命中**——
     「pattern 坏了」与「对照无效」两个错误叠在一起，输出看着完全可信。
     对策：对照用**内联字面量**（单反斜杠、正斜杠、双反斜杠各写死一条），三个都命中才算 pattern 可用。
   - **第 11 条（16:4x，新）：四份台账的 EOL 互不统一。** 实测温：`BASELINE.md` 259 个 CRLF，
     `PDF-PAGES.md` / `ACCEPTANCE.md` / `YUYU-OVERHAUL-SPEC.md` **纯 LF**（CRLF 0）；
     而 `附录/D-术语表.md`、`en/Appendices/D-Glossary.md` 各 316 个 CRLF。
     按 CRLF 去锚一个 LF 文件的结果是**静默 0 命中**——本轮第一次往 `PDF-PAGES.md` 插行就是这样失败的。
     对策：锚定前逐文件探测原始字节里有没有 CRLF，别信「docs 一律 CRLF」这种整仓口径。
   - **第 12 条（16:4x，新）：复验期间工作区不是静止的。** 16:31–16:40 脏区总数连读三次为 **489 / 500 / 487**，
     起因是本轮为分册候选做调研而启动的后台工作流**把检索证据直接写进了仓库根目录**：
     `gs.html` 44,063 B、`kimi_install.sh` 19,407 B、`nat.yml` 5,962 B、`rel.yml` 6,548 B 一度在盘上，
     另有 `.kcs_tree.json` 1,393,046 B、`.verify/kimi.json` 449,780 B、`.verify/kimi-2.4.1.tgz` 18,742,688 B
     到复测时已自行消失。**用户 16:4x 令「先不要搞 cursor」，该工作流已 stop，四个根目录文件已挪进
     `yuyu-book/.scratch/kimi-cursor-survey/`（该目录被忽略规则盖住，不进脏区）。**
     对策：凡引用「脏区条数」这类自引用计数，必须等编排任务退出后复测，并把「此数是在并发写入期间读的」写在同一行。
   - **第 13 条（16:4x，新）：`git status --porcelain` 会给非 ASCII 路径加引号并八进制转义**
     （实测输出形如 `"\351\231\204\275\225/\346\234\257\205..."`，
     即 `附录/D-术语表.md` 整串被八进制转义），拿中文文件名做 `endswith` 匹配会假报「不在脏区列表里」——
     本轮我就是这样把 `附录/D-术语表.md` 误读成干净的。对策：走 `git status -z` 的 NUL 分隔字段，
     或 `git ls-files -s` 按字节匹配，不要解析给人看的那一列。
   - **第 13 条附注（16:49 自查，新）：上面六条原先一律标成「16:5x」，而那是写下时还没到达的时刻。**
     16:49 读系统表，再比对 mtime：`PDF-PAGES.md` 16:33:51、`BASELINE.md` 16:35:31、本文件 16:48:21
     ——六条只能在 16:35–16:48 之间写成，所以标注统一改为 **16:4x**。
     第 12 条里「用户令先不要搞 cursor」那一句更虚：**会话记录（6 份 .jsonl 全扫）里这条指令没有独立 user 行**，
     它只出现在 16:47:11 的压缩摘要里；能取证的最近锚点是 16:43:52 那条 handraw 请求，只能反推它在此之前。
     所以那处同样写 16:4x，并把「无法取证准确时刻」写在同一句里。
     教训与脏区读数同类：**时间戳和计数一样，不实测就不配写进账本**——而且它错的方向是「未来」，
     看起来比错向过去更隐蔽。
10. **写警告的那只手自己又漏了一次**：上面第 9 条正在讲「别把账户名抄进文档」，而我在 14:4x 的编辑里
    亲手把裸的账户名抄进本文件 **5 处**（第 3 条的复验命令、第 9 条的模式示例与说明句里都有）。
    发现时它们只在工作树、本文件也不在索引里，已全部换成 `<账户名>`；四份账本
    （SPEC / `ACCEPTANCE` / `BASELINE` / `PDF-PAGES`）复扫裸名 **0 命中**。
    机制性原因很实在：「把刚跑出来的命令原样贴进文档」和「把标识符原样贴进文档」是同一个动作。
    所以命令要写成 `$(python -c 'import getpass;print(getpass.getuser())')` 这种**现取现扫**的形式，
    贴结果就得先过一遍占位。这条是本节第 3 条「别把词写全」的复发记录，不是新规则。
11. **17:1x–17:5x：勾一格之前，得跑那一格真正归谁管的闸，而不是手边最熟的那条命令。**
    M7 的「`附录/D-术语表.md` 丛书共享词」那格在 17:0x 被我改成 `[x]`，依据只有两条——
    `check_book.py` 0 errors、两份 `dist/*.html` 里 grep 得到标题。这两条都是**成品面**的证据，
    而真正管着这格的两道闸住在测试里：`en/**` 不许裸汉字在
    `test_manifest.py:23`（`HAN_RX`）+ `:56-60`（唯一豁免 = `apxd` 里「恰好 5 格、只有第 2 格带汉字」的行），
    术语条目数在 `test_docclaims.py:48` 的 `glossary_rows`。`check_book.py` 一辈子不会替我喊这两声。
    17:1x 全套跑完 `FAILED (failures=1)`，红的正是英文半边（4 列表 + 两列中文 + 一个「六」）；
    压成 5 列、汉字收进第 2 格之后又冒出第二个红——`en/README.md:109` 的 **122 bilingual term definitions**
    被顶成 125，因为新表也是「5 格 + 首格 ASCII」，被条数度量当成了三条术语。
    **两条都不是闸太严**：第一条是书稿真写了规则禁止的东西，第二条是我把非条目行数成了条目。
    盘上三口径实测（同一份书稿）：as-shipped zh 122 / en 125；在分歧表处截断 zh 122 / en 122；
    要求末格写「第 N 章」116 / 116（这个口径连原文都对不上，排除）。
    选截断，代价是**本轮动了一处测试代码**：`glossary_rows` 加 `cut`，遇到
    `## Series-wide shared terms` / `## 丛书共享词` 就停；`untranslated_han` 的豁免条件一个字没松。
    顺带一条要给后来人的：**中英两张表的列数从此不一样（zh 4 列 / en 5 列），是这条闸逼的，不是笔误，
    别当对称性问题「修平」**——把它修回 4 列，510 那个套件立刻红。
    17:4x 复测全套：`bookctl check --fast` 六步 exit 0（那一步内部就是 **Ran 510 tests OK**）、
    根目录 **39 tests OK**、四条护栏（site_links / block_markers / crossrefs / bilingual_parity）各 exit 0
    （parity 报 `apxd 17 17 0 2 2`：新标题两边同时多一个，对齐没破）、`check_book.py` 176 份 / 321 幅 / 0 errors、
    `check_artifact_claims.py` 仍 **exit 1**（CI Noto 505/536 与本机雅黑 518/569 之差，设计如此，不放行）。
    书稿一改，16:2x 那两份 en 产物就不再同源，所以 17:35–17:44 重跑 `--product book --lang both --pdf`：
    PyMuPDF 实测 **518 / 569 页、28 / 28 书签**，一个页号没动，明细在 `PDF-PAGES.md` 17:35/17:36/17:43/17:44 四行。
    **为什么日志不进仓**：解释器自报的那一行是绝对路径，其中一段就是本机账户名；
    15:1x 那两轮的先例是「写进 `logs/` 再就地脱敏」，本轮判断这条内容读者不需要复核
    （需要的数全在 `PDF-PAGES.md` 表里），就把它留在仓库外，省一次「抄进来再抹掉」的复发面。
    对策：文档类格子改勾之前，先问「哪几个测试读这份文件」，然后跑那个套件——
    `python -m unittest discover -s yuyu-book/tests`（或 `make check`），不是 `check_book.py` 一条。
12. **18:2x–18:5x：往测试里加东西，会同时踩到两道「数测试条数」的闸，而它们要的是相反的动作。**
    路线 B 落地时我先给 `art.py` 加了 `OMP_ART_DIR` + `_search_dirs()`，再把 omp 题刻的四道断言写进
    `test_art.py`——它本来就是管插画的套件，看起来是唯一正确的家。全套 516 跑出两个红，都不是「闸太严」：
    - `test_product_isolation.py:102 test_no_other_test_loads_the_omp_manifest` 报
      `['test_art.py'] != []`（断言在 `:108`）。这道闸的实现是**拿字符串 `manifest-omp` 去 grep 除自己
      以外的每一个 `test_*.py`**，不去读谁的 `setUpClass`。它 docstring 里写的理由是：book-only 套件是
      「20 单元契约」的第二道防线，omp 的骨架一旦混进去，那个 20 就会被悄悄放宽或糊掉。
      **正确的反应不是给它加白名单**——加白名单正是它要防的那个动作——而是承认 omp 的契约本来就住在
      这个文件里（它已经在 `setUpClass` 里 `registry.load(OMP)`）。四道断言整体搬进
      `test_product_isolation.py:111` 新开的 `OmpArtTray`，`test_art.py` 退回只数御舆。
      搬完净差 **+4 条**：我原先写了 6 条，其中「两册 id 不重叠」与「两个目录不重名」本来就是隔离命题，
      放对地方之后不再算插画套件的条数。
    - `test_docclaims.py:229 test_the_revision_note_closes_with_the_suite_it_shipped` 报
      `revisions.zh: the note says 510, discovery says 514`——**套件条数是书里一句读者看得见的话**：
      `yuyu-book/revisions.json` 最新条目（0.3.5）末尾中英各一句「构建器测试 N 项全绿」/
      "N builder tests green"，闸把它与 `unittest discover` 的现数对齐（报错点在 `:242`）。
      改法沿用这个 overhaul 一直在做的**就地修订顶部条目**：`git show HEAD:yuyu-book/revisions.json`
      里同一句是 **501**，本轮开始前盘上是 **510**，本轮改成 **514**；不新增版本条目——0.3.5 还没发布，
      本轮也没提交。
    顺带一条同族的连带修改：`STRUCTURE.md` 的 `art.py` 那一行（`:102`）原样写着图只从
    `illustrations/` 取，路线 B 之后它是过期的，已补上「先查 `illustrations-omp/<id>.svg`、
    查不到回落 `illustrations/<id>.svg`」；新目录自己占一行（`:123`），那行的 **7** 由
    `test_docclaims.py:84 omp_drawings()` 现数钉住，跟御舆那个 42（`:81 drawings()`）分开数，
    所以 42 的三处读者声明一个字没动。
    对策：**动 `yuyu-book/tests/` 之前先问「这条断言属于哪个产品」**，动完立刻跑
    `python -m unittest discover -s yuyu-book/tests`，并准备好同轮改 `revisions.json` 那两句——
    少跑这一次，读者手里就是一本写着过期测试数的书。
