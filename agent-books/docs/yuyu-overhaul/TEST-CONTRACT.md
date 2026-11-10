# TEST-CONTRACT · 谁钉住了哪个数

Y-M6 Step 3 的产物。这里不收「怎么跑测试」（`CONTRIBUTING.md` 第 2 节有），收的是
**改造期间立起来/加固的断言各自盯什么、数字现在是多少、以及它们能不能真的失败**。
一条从不失败的断言比没有断言更坏，所以每条都配了负例（见「变异表」）。

## 1. 两套单测的当前规模

| 套件 | 命令 | 用例数 |
|------|------|--------|
| 仓库侧 | `python -m unittest discover -s tests` | **39** |
| 构建器侧 | `python -m unittest discover -s yuyu-book/tests` | **510** |

构建器侧的 510 不是随便报的数：`test_docclaims.py:212` 的
`test_the_revision_note_closes_with_the_suite_it_shipped` 会重新 `discover` 一次，
拿 `countTestCases()` 去撞 `revisions.json` **最新那一条** note 里的数字
（zh `构建器测试 (\d+) 项全绿` / en `(\d+) builder tests green`），对不上就红。
本轮加 9 条隔离测试时它立刻把 `501 → 510` 报成失败 —— 这正是它的设计用途，
所以**加完测试必须同轮改 revisions 的那一句**，两句都在 `yuyu-book/revisions.json`（zh 与 en 各一行）。

拆到文件：`test_docclaims` 9、`test_build_contracts` 71、`test_art` 15、`test_illustrations` 18、
`test_product_isolation` 9（新）。其余分布在 `test_manifest` / `test_render_anchors` / `test_pages` /
`test_plain` / `test_notes` / `test_pdf` / `test_audit` 等，清单与职责见 `STRUCTURE.md` §3.2。

## 2. 20 单元契约（御舆）

| 钉住的东西 | 现值 | 谁在盯 |
|------------|------|--------|
| `manifest.json` 单元数（1 前言 + 15 章 + 4 附录） | **20**，id 全局唯一 | `test_manifest`、`core.validate_configs()`、`test_product_isolation` |
| `guides` 覆盖 | 20/20，且 `question`/`deliverable`/`boundary` 的 zh、en 都非空 | `core.validate_configs()`（`build.py --check` 与每次构建都跑） |
| `notes.json` 按语 | 20 条 | `test_notes` + `build.py` 的三处对账（正文 `<div class="keeper">` 数 = 合集 `<li class="kn-row">` 数 = 有按语的单元数） |
| `reading-paths.json` 位置表 | 15 个键（**只覆盖 15 章**，前言与附录没有小节，所以不是 20） | `plain.validate_plain()`：表长必须等于该单元小节数 |
| `glosses.json` | 102 词条（core 44 / extra 58） | `test_docclaims` 重算 README/STRUCTURE 引用的数字 |
| 手绘图装配 | `illustrations/*.svg` 磁盘 **42** 枚；对 20 个单元 id `art.missing()` = 0 枚缺 → 章徽期望 20、题刻期望 4 | `build.py:269` 的 `want_emblems`/`want_heads` + `test_art` |
| 来源登记 | `sources.json` 55 条，全部 https + 钉版 | `test_sources`、`core.validate_configs()` |

## 3. Product isolation（新）

`yuyu-book/tests/test_product_isolation.py`，9 条。设计口径与 SPEC 里那段示例代码不同，
两处是刻意改强的：

1. 示例代码 `from yuyu_book.core import load_manifest` —— 仓里没有这个函数。
   真实入口是 `core.load_configs(manifest_name, sources_name)`（内部走 `registry.load` 并跑 `validate_configs`），
   单元 id 序列用 `core.expected_ids(manifest)`，登记表名用 `plain.registry_names(manifest)`，
   语言用 `plain.manifest_langs(manifest)`。全部换成仓内函数，不再手扒 manifest 的嵌套形状。
2. 示例代码的 `assertTrue(... or True)` 永真、`skipTest` 会在 omp 清单消失时把断言变成 no-op。
   新版两条都不许「没东西可测就过」：omp 清单缺失即 `registry.load` 报错，红。

九条断言（每条对应一种「两本书互相写」的事故）：

| 断言 | 挡住什么 |
|------|----------|
| book = 20 且 id 唯一 | 御舆契约被第二本书稀释或重复 id |
| omp = 39 且 id 唯一 | 第二本书的骨架漂了却没人知道 |
| 两个产品的 `glosses`/`notes`/`paths` 登记表名互斥、都在 `registry.FILES`、且文件真在磁盘上 | 给 omp 写通俗层时静默改写御舆的登记表 |
| `load_configs()` 无参仍是御舆（product 视为 `book`、20 单元） | 默认路径漂移，让所有「book-only」测试其实测的是 omp |
| omp 走同一个 `validate_configs()`，且 `manifest_langs == ("zh",)` | 用隔离当借口降低第二本书的配置门禁 |
| 产物文件名集合不相交（`yuyu-agent-harness-{zh,en}` vs `yuyu-omp-zh`，html+pdf） | 后一次构建覆盖前一次的产物 |
| omp **显式**写 `"subject_index_registry": null` | `build.py:190` 的默认值会让 omp 构建去盖章御舆的主题索引 |
| omp `langs: ["zh"]`、御舆**不写** `langs` | 御舆丢掉双语默认，或 omp 假装自己有英文版（`KeyError` 而不是缺文件） |
| 除本文件外，`yuyu-book/tests/` 里没有任何 `test_*.py` 读 `manifest-omp` | 20 单元契约的第二道防线 |

**故意没有的断言**：两个产品的单元 id 不许相同。id 会变成 `article id` 与 `#ch09` 这类锚点，
但两本书是两份独立 HTML，锚点命名空间本来就各是各的 —— `ch01` 同名不是事故，写成门禁只会逼人乱改 id
（而 `STRUCTURE.md` §5 明说改单元 id 等于改全书锚点）。

## 4. 变异表（证明上面这些不是摆设）

用 `registry.load` 的内存版包装注入缺陷、逐条跑对应断言（不改磁盘、跑完即弃）：

| 注入的缺陷 | 结果 |
|------------|------|
| 御舆少一个附录 | `AssertionError: 19 != 20` |
| 御舆附录重复登记一次 | `AssertionError: 21 != 20` |
| omp 少一章 | `AssertionError: 38 != 39` |
| omp 的 `output_prefix` 改成 `yuyu-agent-harness` | 撞车断言红（`'yuyu-agent-harness' == 'yuyu-agent-harness'`） |
| omp 删掉 `subject_index_registry` 键 | 「必须显式声明」红 |
| omp 的 `product` 改成 `book` | 登记表互斥红（`'glosses.json' == 'glosses.json'`） |
| omp 的 `langs` 改成 `["zh","en"]` | 语言门禁红（`+ ['zh']`） |
| omp 的 guides 少一个单元 | `validate_configs` 报 `guides missing for: omp-front` |
| 御舆清单被写上 `product: omp` | 「默认 loader 仍是御舆」红 |
| 在 `yuyu-book/tests/` 放一个临时 `test_zz_probe.py`，内容只提 `manifest-omp` | 扫描那条红：`['test_zz_probe.py'] load omp's manifest from a book-only suite`（探针文件当场删除） |

十条全部按预期失败；正例在现树 `Ran 9 tests ... OK`。

## 5. 与既有护栏的分工（不要重复钉）

`check_bilingual_parity.py` 同时由 `book.yml`、`check-book.yml` 和本地
`ci-local-yuyu.ps1` 调用。CI 将它作为独立步骤执行，不计入 `bookctl check --fast`
的六步。`book.yml` 的路径过滤包含该脚本，修改检查逻辑也会触发检查。

| 护栏 | 管什么 | 位置 |
|------|--------|------|
| `check_crossrefs.py` | 两书互链的章号/章名对不对 | `docs/yuyu-overhaul/` |
| `check_block_markers.py` | 40 个文件的证据块标记 | 同上 |
| `check_site_links.py` | 门户引用的发布目标存在性 + 门面文档相对链接 | 同上（Y-M5） |
| `check_bilingual_parity.py` | 20 单元中英：文件存在 / H2 差 ≤ 阈值 / Mermaid 数相等 | 同上（M8）。**只数标题与围栏**：罗盘三字段仍由 `core.py:359–363` 管（`manifest.json` 无 `langs`，故恒校 zh+en），在这里再实现一遍只会多一个会漂的口径 |
| `check_artifact_claims.py` | README 宣称的页数/体积 | `scripts/`（按 CI/Noto 口径，本机设计上红，例外表见 `BASELINE.md`） |
| `test_docclaims` | README / STRUCTURE / CREDITS / revisions 里每个数字重算 | `yuyu-book/tests/` |
| `test_product_isolation` | 两产品写权限与契约互不侵犯 | 同上（Y-M6） |
