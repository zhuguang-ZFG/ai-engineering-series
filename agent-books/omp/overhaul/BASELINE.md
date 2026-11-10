# Overhaul baseline

- Date: 2026-11-03 America/Adak
- Branch: p3-pages-split (dirty; no commit in this SPEC)
- Writing pin: omp/18.15.0
- Verified pin (user Windows Bun): omp/18.16.0 (`%USERPROFILE%\.bun\bin\omp.exe`)
- Commit/push: DEFERRED

## 产物（本机实测，非 CI 字体）

| 文件 | bytes | pages | bookmarks | sha256(前16) |
|------|-------|-------|-----------|--------------|
| `yuyu-book/dist/yuyu-omp-zh.html` | 19,525,253 | — | — | `23e7c14e45447449` |
| `yuyu-book/dist/yuyu-omp-zh.pdf` | 25,877,857 | 238 | 21 | `c5b1adb56d2faf8d` |

SPEC §1.1 宣称的 238 页与本机一致（`pdf.py` 书签 21 条，非 SPEC 写的「约 47」——以本表为准）。

## 内容体量（`python omp/overhaul/count_chars.py`）

- 章 + 附录 + 前言文件数：39
- 正文章（ch01–ch33）原始字符合计：119,653 · 汉字合计：50,806
- 全书（含附录/前言）原始字符合计：130,225 · 汉字合计：55,908
- 单章最短：ch23（2,075 字符 / 861 汉字）· 单章最长：ch04（6,991 字符 / 1,812 汉字）
- 汉字 < 4500 的章：33/33 · 原始字符 < 4500 的章：28/33
- `omp/images/` 文件数：108
- ```` ```mermaid ```` 围栏总数（全书）：1（在 `ch03.md`）
- 含「版本核对」小节的章：33/33（附录 5 篇各有 1 处命中）
- `manifest-omp.json`：`product=omp` · `langs=["zh"]` · `output_prefix=yuyu-omp` ·
  `plain_optional=true` · 单元 39（parts 33 units + appendices 5 + front）· `guides` 39 条
- 装载状态：`bookctl build --product omp` 仍带 `--no-plain`（见 `yuyu-book/PRODUCTS.md`），
  即当前 omp 构建不加载 glosses/notes，产物统计为 `0 glosses / 0 keeper notes`

## 构建基线（改造前必须为绿）

```text
python yuyu-book/build.py --manifest manifest-omp.json --sources sources-omp.json \
    --no-plain --lang zh --check
→ [zh] yuyu-omp-zh.html: 19.5 MB, 39 units, 1 plates, 3 cited links,
       0 glosses, 0 lead bands, 0 tier chips, 0 emblems, 0 headpieces, 0 keeper notes
→ CHECK OK
```

## 真源与镜像

- 真源：本机 `D:\Users\claude\claude-code-book-main\omp\`
- box 镜像 `/workspace/omp-book/`：本次执行未做同步（无该环境的访问通道），以本机为准

## M0 期间唯一的落盘修正

`yuyu-book/manifest-omp.json` 漏写 `schema_version`，导致御舆门禁
`test_registry.ShippedRegistries` 红（`None != 1`），即本 SPEC 全局约束 7
「不破坏御舆」在基线时已不成立。M0 补 `"schema_version": 1`（与
`sources-omp.json` / `revisions-omp.json` 一致）后该测 9 项通过，
omp `--check` 仍绿。除这一行外 M0 未改任何内容。

## 脏树快照

- `git-status-baseline.txt`（24 行）· `git-diffstat-baseline.txt`（11 改 + 汇总）
- 关键项：`omp/` 未跟踪；`scripts/bookctl.py`、`yuyu-book/build.py`、`yuyu-book/yuyu_book/*.py`（10 个）已改；
  `yuyu-book/yuyu_book/{deco,labels,style_css}.py` 未跟踪；`OVERHAUL-SPEC.md` 在仓根与 `omp/` 各一份（**M0 那一刻内容相同**）。
  2026-11-04 复核：两份已分叉——`omp/` 那份回写了进度复选框与执行说明。同一分钟实测
  （`stat` + `diff`）：仓根 31,138 B / 11-03 21:41 未再改动，`omp/` 35,233 B / 11-04 08:26，
  差 4,095 B、**79 个差异行**，其中 **38 行是复选框**（19 对：仓根 `- [ ]` ↔ omp `- [x]`）。
  复选框计数：仓根未勾 62 / 已勾 0，`omp/` 未勾 43 / 已勾 19。
  （本条初记的「66 行差异、36 行复选框、omp 未勾 44」是更早一刻的状态，此后又勾上了几格——
  这两个口径会随进度漂，引用前重跑 `diff OVERHAUL-SPEC.md omp/OVERHAUL-SPEC.md | grep -c '^[<>]'`。）
  **以 `omp/OVERHAUL-SPEC.md` 为准**；仓根那份只作历史快照，别再改它。

## 执行期偏差（2026-11-04 记录，两条都未由本轮擅自纠正）

1. **工作树里有 324 个已暂存（staged）文件**，而 `STRUCTURE-GATE.md` 第五节与两份 SPEC 都写了「严禁 `git add`」。
   本轮没有执行过 `git add`，也没有 `reset`——只如实记下这个偏差。分布（2026-11-04 09:35 用
   `git -c core.quotepath=false diff --cached --name-only` 分组重数，合计 324）：
   `omp/` 共 302 = 顶层 md 45（33 章 + 5 附录 + `00-前言`/`BUILD`/`README`/`VERIFY`/`outline`/`resources`/`OVERHAUL-SPEC`）
   + `omp/images` 108 + `omp/facts` 136（`live-18.16.0` 96 + 其余 40）+ `omp/overhaul` 13；
   `docs/` 共 12 = `docs/yuyu-overhaul` 9 + `docs/yuyu-overhaul/logs` 2 + `docs/YUYU-OVERHAUL-SPEC.md` 1；
   `yuyu-book/` 共 9（6 份 json/md + `yuyu_book/{deco,labels,style_css}.py`）；仓根 `OVERHAUL-SPEC.md` 1。
   （本节初记的「章稿 44」少了一个 `omp/OVERHAUL-SPEC.md`，是手数错的；初记的「docs 9+2+1」**拆法本来就对**，
   上一版把它当成错值改掉是我的复核又数错了一次——两种写法都指向同一个 12。）
   索引会随日志/文档新增而漂，引用这组数前先重跑上面那条命令。
   同批新增的 `docs/yuyu-overhaul/check_crossrefs.py` **保持未跟踪**，未进索引。
2. **提交前必须先处理的泄漏面**：`omp/facts/live-18.16.0/models-list.txt`（39 行）也在那 324 个里。
   它没有密钥（`sk-…`／`Bearer …`／`x-api-key` 三类模式实测 0 命中，也没有对外域名），
   但第一行是自建网关的内部名 `<私有网关甲> (2)`，整份是该账号的模型清单——`STRUCTURE-GATE.md:78` 早写明
   「含用户私有网关名，只作形状参考，禁止把表贴进书稿或 VERIFY」。AGENTS.md 的 Security 一节同样禁止把凭据类内容入库。
   处理方式（任选，需用户拍板）：提交前把它从索引里撤下 / 加进 `.gitignore` / 换成脱敏后的表。
   同目录的 `help-*.txt` 是纯 `--help` 原文，不在此列。
