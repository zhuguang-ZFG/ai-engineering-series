# Task M8 · 双语质量收口审计（BI-AUDIT）

一句话结论：**三条都过**——20 个单元的中英结构逐 unit 完全相等（H2 与 Mermaid
的差都是 0），translationese 终值 zh `0/13/13`、en `15/16/42`，与 git HEAD 逐
unit 一致且优于本轮中途的 BASELINE 快照，notes 英门禁 14 条测试全绿。
本轮中途 en 曾涨到 `21/23`，涨的 6 行全部是本轮自己新写的英文 prose，已改写为
主动语态，**没有回滚，也没有登记例外**。

执行时间 2026-11-04，全部命令与退出码：

```
python docs/yuyu-overhaul/check_bilingual_parity.py        -> 0   bilingual parity OK
python scripts/measure_translationese.py                   -> 0   (见 TRANSLATIONESE-FINAL.txt)
python -m unittest discover -s yuyu-book/tests -p "test_notes.py" -v -> 0   Ran 14 tests, OK
python scripts/check_book.py                               -> 0   174 files / 321 diagrams / 0 errors
```

（`174` 是**写完本文件之后**重跑的数：M7 收尾那次是 173，多的这一份就是 BI-AUDIT.md。
`--max-h2-diff=0` 也实跑过，结论仍是 `bilingual parity OK`。
M3 落 `ILLUST-SYNC.md` 之后同一条命令报 175 —— 这个数每往 `docs/` 加一份 `.md` 就 +1，
是「那一刻的读数」而不是契约，链条在 `BASELINE.md` 的「Mermaid 计数复核」一节。）

---

## 一、Step 1：中英结构对拍

脚本 `docs/yuyu-overhaul/check_bilingual_parity.py`（本轮新建，127 行）。
单元清单取自构建器自己的 `unit_stream(manifest)`，与
`scripts/measure_translationese.py:57` 同一份 20 单元，所以计数不会漂到新书写地面上。

### 口径

| 维度 | 定义 | 为什么这么定 |
| --- | --- | --- |
| 文件存在 | `manifest` 里该 unit 的 `zh`/`en` 路径都 `is_file()` | 少一个文件，后面两个数无从谈起，单独报 `missing` |
| H2 | `^##\s+\S`，且只在**围栏外**统计 | 与 `check_book.py:126–141` 同一套围栏状态机：开栏记 info string、闭栏要求 info 为空且 `~`/`` ` `` 同类不短于开栏 |
| Mermaid | 开栏 info 恰为 `mermaid` 的围栏数 | 同上，`check_book` 的 `diagrams` 就是这个口径，两边对得上才叫「相等」 |

围栏这件事必须写实：`## ` 出现在代码块里不能算一节。变异样本
「围栏内一个假 H2 + 围栏外一个真 H2」测得 `(h2=1, mermaid=0)`，符合预期。

### 阈值 ≤2 的登记（SPEC 要求「自定 ≤2，记入 BI-AUDIT」）

阈值定为 **2**，但实测 **20 个单元的 H2 差全是 0**，Mermaid 差也全是 0。
也就是说这条闸目前有余量，不是在勉强通过。留 2 而不是 0 的理由只有一条，写清楚：
`--max-h2-diff` 是参数，收紧随时可以，且已经证明收紧到 0 仍为绿——

```
python docs/yuyu-overhaul/check_bilingual_parity.py --max-h2-diff=0   # 现网实测仍 OK
```

反过来说：**目前没有证据支持「某些单元天然需要中英 H2 不同」**，等真出现合法的
附录分叉再放宽，而不是先放宽再找理由。

### 实测（20 单元 × 4 个数）

| unit | zh H2 | en H2 | Δ | zh mm | en mm |
| --- | --- | --- | --- | --- | --- |
| front | 7 | 7 | 0 | 3 | 3 |
| ch01 | 6 | 6 | 0 | 5 | 5 |
| ch02 | 6 | 6 | 0 | 5 | 5 |
| ch03 | 6 | 6 | 0 | 7 | 7 |
| ch04 | 7 | 7 | 0 | 7 | 7 |
| ch05 | 6 | 6 | 0 | 6 | 6 |
| ch06 | 6 | 6 | 0 | 7 | 7 |
| ch07 | 7 | 7 | 0 | 7 | 7 |
| ch08 | 7 | 7 | 0 | 8 | 8 |
| ch09 | 8 | 8 | 0 | 8 | 8 |
| ch10 | 9 | 9 | 0 | 11 | 11 |
| ch11 | 7 | 7 | 0 | 7 | 7 |
| ch12 | 6 | 6 | 0 | 21 | 21 |
| ch13 | 8 | 8 | 0 | 10 | 10 |
| ch14 | 8 | 8 | 0 | 12 | 12 |
| ch15 | 8 | 8 | 0 | 11 | 11 |
| apxa | 5 | 5 | 0 | 9 | 9 |
| apxb | 16 | 16 | 0 | 8 | 8 |
| apxc | 15 | 15 | 0 | 6 | 6 |
| apxd | 16 | 16 | 0 | 2 | 2 |
| **合计** | **164** | **164** | **0** | **160** | **160** |

Mermaid 合计 160/160 与 `BASELINE.md:10` 的「zh=160 en=160」独立吻合；
它不等于 `check_book.py` 报的 321，后者是全仓 `.md`（含 `omp/`、`docs/`）。
两个数不矛盾，别把它们当一个。

### 变异证明（绿不是空的）

用 `tempfile` 造 fixture、把 `ROOT` 与 `unit_pairs` 打桩后实跑，三类失败都能红：

```
threshold=2  -> FAIL unitB: mermaid zh=0 en=1 not equal
             -> FAIL unitF: missing missing.md
threshold=1  -> 同上（H2 差 1 仍放行，符合语义）
H2 差 3 的样本 -> threshold=2/1/0 各报 1 条：big: H2 zh=4 en=1 diff=3 > N
main() 退出码 = 失败条数 = 2
```

退出码取「失败单元数」，CI 直接用它，不需要再解析文本。

### G8 的第三维「罗盘字段」：不在这里重复

SPEC:46 给 G8 的口径是「标题/围栏数/罗盘字段」。罗盘三卡的字段落在
`yuyu-book/manifest.json` 的 `guides`，是**一条记录里同时带 zh 与 en**，
不存在「两个文件各数一遍」的对拍问题；它已有机器闸：
`yuyu-book/yuyu_book/core.py:359–363` 对 `GUIDE_FIELDS = (question,
deliverable, boundary)` × `langs` 逐字段判空，而 `core.py:337` 的 `langs`
取 `manifest.get("langs") or ("zh","en")`——`manifest.json` 里没有 `langs`
键，所以**即使只构建 zh，en 侧罗盘字段照样校**。这条在 `check --fast`
第二步 `source build` 里跑，实测 20/20 单元三字段齐（另带
`plain/plain_evidence/analogy/sources`，20 单元都有来源芯片）。
在 parity 脚本里再实现一遍只会多一个会漂的口径，故不做，只在此登记证据位置。

### 接进哪道闸：ci-local-yuyu.ps1，不动 `check --fast` 的六步

这条脚本已经串进 `docs/yuyu-overhaul/ci-local-yuyu.ps1` 的新「离线护栏」段
（`check_site_links` / `check_block_markers` / `check_crossrefs` /
`check_bilingual_parity`），放在最贵的一步之前，让便宜的红先红。

为什么不进 `check --fast`：那六步（`scripts/bookctl.py:251`）的**步数是被钉住的宣称**
——README、STRUCTURE、`revisions.json` 与 `test_docclaims.py` 都写着「六步」，
加一步就得同步改一批被钉的数字，那是另一格的活，不该混进质量收口。
`ci-local-yuyu.ps1` 不在任何测试的钉住范围内（全仓 grep 无引用），改它无连带。
护栏段单独用 PowerShell 复刻 `Step` 语义实跑过：4 条全 exit 0，
`ci-local-yuyu.ps1` 本体 `Parser::ParseFile` 无语法错误，BOM+CRLF 未丢。

---

## 二、Step 2：translationese 三个读数，谁跟谁比

`docs/yuyu-overhaul/TRANSLATIONESE-FINAL.txt`（本轮新建）里那张表是 NOW。
可比的对照物有两个，性质不同，必须先分清：

| 读数 | 怎么来的 | 能不能当「改前」 |
| --- | --- | --- |
| BASELINE `zh 2/15/13`、`en 19/20/42` | 本轮 **Y-M1 执行中途**的工作树快照，且 B1（前言+ch01–04）与 B3（ch09–ch12）当时已落盘 | **不能**。它本身已经是改中之物 |
| HEAD `zh 0/13/13`、`en 15/16/42` | `git archive HEAD`（951c0ef，本轮一切改动之前）导出后按同一 `prose_walls` + `line_counts` 重算 | **能**，这才是可比对象 |
| NOW `zh 0/13/13`、`en 15/16/42` | 当前工作树 | 本轮终值 |

三点读数并到 unit 级（zh 省略全零行，en 列 `行/处/系词`）：

| unit | zh BASELINE | zh HEAD | zh NOW | en BASELINE | en HEAD | en NOW |
| --- | --- | --- | --- | --- | --- | --- |
| front | 0 | 0 | 0 | 0/0/2 | 0/0/2 | 0/0/2 |
| ch01 | 0 | 0 | 0 | 4/4/3 | 4/4/3 | 4/4/3 |
| ch02 | 0 | 0 | 0 | 0/0/3 | 0/0/3 | 0/0/3 |
| ch03 | 0 | 0 | 0 | 0/0/2 | 0/0/2 | 0/0/2 |
| ch04 | 0 | 0 | 0 | 2/2/3 | 2/2/3 | 2/2/3 |
| ch05 | 0 | 0 | 0 | 1/1/4 | 1/1/4 | 1/1/4 |
| ch06 | 0 | 0 | 0 | 0/0/3 | 0/0/3 | **0/0/3**（中途 1） |
| ch07 | 0 | 0 | 0 | 0/0/3 | 0/0/3 | **0/0/3**（中途 2） |
| ch08 | 0 | 0 | 0 | 0/0/3 | 0/0/3 | **0/0/3**（中途 2） |
| ch09 | 0 | 0 | 0 | **6/6/2** | 3/3/2 | 3/3/2 |
| ch10 | **1/1/0** | 0/0/0 | 0/0/0 | **1/1/1** | 0/0/1 | 0/0/1 |
| ch11 | **1/2/1** | 0/1/1 | 0/1/1 | 0/0/0 | 0/0/0 | 0/0/0 |
| ch12 | 0 | 0 | 0 | 1/1/4 | 1/1/4 | 1/1/4 |
| ch13 | 0 | 0 | 0 | 2/2/3 | 2/2/3 | **2/2/3**（中途 3） |
| ch14 | 0 | 0 | 0 | 0/0/1 | 0/0/1 | 0/0/1 |
| ch15 | 0 | 0 | 0 | 2/3/0 | 2/3/0 | 2/3/0 |
| apxa–apxd | 0 | 0 | 0 | 0/0/(1,2,2,0) | 同 | 同 |
| **TOTAL** | **2/15/13** | **0/13/13** | **0/13/13** | **19/20/42** | **15/16/42** | **15/16/42** |

读法：zh 与 en 的 NOW 都与 HEAD **逐 unit 相同**（不是总数碰巧相等——
逐条对过 `head-full.json`）。而本轮确实动了这些文件：把 `git diff --numstat HEAD`
限到 20 单元的那 40 个路径上，是 **34 个文件改动、+668/−116**（其余 6 个文件本轮没碰）。
所以这句话才成立：**本轮的 prose 工作没有把翻译腔带回书里**；
「比 HEAD 更好」这句话不成立，也不该说。

SPEC Step 2 的期望是「不差于 BASELINE」。zh `0/13` 优于 `2/15`，
en `15/16` 优于 `19/20`，两条都不需要例外登记。

### 中途 en 涨到 21/23 的归因，和 6 行 NEW/OLD

M8 一开跑就复现出 en `21 行 / 23 处`（比 BASELINE 的 `19/20` 还差 2 行，
比 HEAD 的 `15/16` 差 6 行）。那 6 行落在四条 unit 上，与 HEAD 的差是
ch06 +1、ch07 +2、ch08 +2、ch13 +1（`21 − 15 = 6`，与改写了 6 行这件事对上）。
逐行核对 HEAD：

**涨出来的 6 行全是本轮新写的句子。** 判据不是印象，是 `git diff -U0 HEAD`——
这 6 行在 diff 里全部只出现在 `+` 侧，HEAD 同一行号上是完全不同的材料
（ch06 L18 与 ch13 L12 在 HEAD 是空行/前言围栏，ch07 L20/L23 是「白板」比喻段，
ch08 L20 是「护栏 vs 神经系统」段）。
HEAD 里唯一含 `misconfigured` 的是 ch08 L391 那句定语用法
（"one misconfigured hook could make…"），不是被动，不计——所以「照抄 HEAD 的旧被动」
这个解释被排除了。

处置：6 行改主动，改前留在 `TRANSLATIONESE-BASELINE.txt` 之外无处可查，
改后与中文原句逐条对过意思。

| 位置 | 改前 | 改后 |
| --- | --- | --- |
| `en/…/06-…Long-Term-Memory.md:18` | whether it should not **be stored** at all | whether the system should keep it out of storage entirely |
| `en/…/07-…Working-Memory.md:20` | old content must **be erased** | the window drops old content |
| `en/…/07-…Working-Memory.md:23` | how much of your effective context window **is left** | how much of your effective context window you have left |
| `en/…/08-…Extension-Points.md:20` | You thought the hook **was misconfigured** | You blamed the hook's configuration |
| `en/…/08-…Extension-Points.md:29` | How the same hooks **are wired** in another harness | How another harness wires the same hooks |
| `en/…/13-…Performance-Optimization.md:12` | whether data **is held back** until it's complete or **sent** the moment it's written | whether the pipeline waits until a chunk is complete before emitting it, or forwards it the moment it arrives |

ch08 L20 那条对着中文「你以为是钩子没配上」核过：改后仍把责任归到「你怪到配置上」，
没有偷换成「你以为是钩子没跑」。

**是否回滚：否。** 6 行都是本轮未提交的新句，主动语态版意思不变，没有需要退回的旧文本。

### zh 那 2 行（BASELINE 有、HEAD 没有）怎么解释

BASELINE 记 ch10 `1/1/0`、ch11 `1/2/1`，HEAD 实测 ch10 `0/0/0`、ch11 `0/1/1`。
也就是说**这两行在 HEAD 里不存在**——它们是本轮 B3 批次（ch09–ch12）自己在
工作树上写进去的，后来的批次又把它们清掉了。
结论只有一条能说出口：zh 从 BASELINE 到 NOW 的改善**不是本轮相对已提交版本的净收益**，
而是中途自伤的愈合。把 `2/15 → 0/13` 当战果写进任何宣称都是错的，
这条写在这儿就是为了拦住下一个这么写的人。

`/13` 那 13 处 `被` 全部是术语式样（`被动的`/`被调用者`/`被调用方`/`被测系统`），
脚本单列不计入可改行，HEAD 与 NOW 一字不差。

---

## 三、Step 3：notes 英门禁

`python -m unittest discover -s yuyu-book/tests -p "test_notes.py" -v` →
**Ran 14 tests in 0.019s，OK，exit 0**。SPEC 点名的三件事各自对应到实测存在的测试名：

| 断言 | 测试 |
| --- | --- |
| 英文按语不带汉字 | `test_an_english_note_may_not_carry_han` |
| 按语长度 | `test_a_too_long_note_fails` |
| 术语锁（按语必须含本单元登记词形） | `test_a_note_without_any_registered_form_fails` / `test_a_form_that_is_not_in_this_units_text_fails` / `test_the_english_note_is_locked_by_the_english_forms` |
| 20 单元一条不多一条不少 | `test_every_unit_needs_its_note_and_no_unit_invents_one` |
| 出厂数据过自己的闸 | `test_the_shipped_notes_pass_their_own_gate` |

另外 4 条（`KeeperDrawing` 2 条 + `NotesPage` 2 条）管车辙卡的尺寸与按语页的排布，
不在 M8 的关注面上，一并绿。

---

## 四、M8 验收

- [x] BI-AUDIT 勾完（本文件）
- [x] notes 测绿（14 tests, OK, exit 0）
- [x] **未** commit/push（本轮全程未执行 `git add`/`commit`/`push`；
  工作树状态见 `BASELINE.md` 的脏树快照一节，本轮只增未提交面）

新落盘的两个文件：`docs/yuyu-overhaul/check_bilingual_parity.py`、
`docs/yuyu-overhaul/TRANSLATIONESE-FINAL.txt`；改动一个：
`docs/yuyu-overhaul/ci-local-yuyu.ps1`（加离线护栏段）。
BI-AUDIT 与 `TRANSLATIONESE-FINAL.txt` 都在 `docs/` 下，会被 `check_book.py` 的
链接与正文墙闸扫到，本文件写完后 `check_book.py` 实测 `0 errors`。

---

## 五、仍缺的证据（不装作有）

1. **中途 21/23 那一瞬没有机器快照落盘。** 上面的 NEW/OLD 判定是用
   「HEAD 同行号内容比对 + diff 只在 `+` 侧」两条独立证据还原的，
   不是当时存下的 `--json` 输出。以后同一轮改写开始前先
   `measure_translationese.py --json > .scratch/pre-edit.json` 留一张，
   就不必还原了。
2. **双语结构检查已接入 CI 配置，远端运行尚待验证。** 2026-11-04 续做时，
   `book.yml` 与 `check-book.yml` 已增加 `check_bilingual_parity.py` 独立步骤，
   Book CI 的路径过滤也覆盖此脚本。本地 20 单元全部通过，缺文件、H2 差 3、
   Mermaid 不等的反例均判失败；实际 GitHub Actions 结果须在获准推送后验证。
3. **H2 阈值 2 目前没有实例需要它**（全为 0）。若日后收紧到 0，
   本文件「阈值 ≤2 的登记」一节要跟着改，不能留着旧数字。
4. **omp 分册不适用本格**：omp 是 zh-only（`bookctl.py` 的 `--product omp`
   对 `--lang en` 直接报 "omp product is zh-only for now"），
   没有第二条语言可对拍。omp 的单元数契约由
   `yuyu-book/tests/test_product_isolation.py` 守，不在这里重复。
