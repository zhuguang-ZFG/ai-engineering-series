# Omp 分册如何接入 yuyu-book

## 构建命令（仓库根目录）

```text
python scripts/bookctl.py build --product omp --lang zh
python scripts/bookctl.py build --product omp --lang zh --pdf
make book-omp
make book-omp-pdf
```

等价于：

```text
python yuyu-book/build.py --lang zh --manifest manifest-omp.json --sources sources-omp.json [--pdf]
```

`--no-plain` 已经不在这条命令里：M2 之后 omp 自带通俗层登记表，跳过它就等于把
317 个术语标注、381 枚档位芯片和 39 条眉批从书上撕掉。要单独看没有通俗层的排版本，
自己加 `--no-plain` 跑一次即可，它仍是 `build.py` 的正式开关。

产物写到 `yuyu-book/dist/`：

| 文件 | 说明 |
|------|------|
| `yuyu-omp-zh.html` | 离线单文件中文 HTML（Mermaid 已渲染 + `omp/images/` 手绘 data-URI + `yuyu-book/illustrations-omp/` 内联 SVG：39 枚章徽 + 7 幅篇题刻） |
| `yuyu-omp-zh.pdf` | A4 PDF（本机 Edge/Chromium + 微软雅黑等 CJK 字体） |

御舆原目标未改：`make book` / `make book-pdf` 仍只构建 `product=book`。

## 配置

- `yuyu-book/manifest-omp.json`：39 个 unit（前言 + 33 章 + 附录 A–E），`output_prefix=yuyu-omp`，`langs=["zh"]`，`plain_optional=false`，含 compass `guides`
- `yuyu-book/glosses-omp.json`：36 个词条，其中 **20 个在正文加虚线**、**16 个只登记不标**（4 个 `mark=false`，因为正文里只以行内代码出现；12 个 `priority="extra"`，是查得到就够了的产品专有名 / 协议名）。
  这 12 个是 2026-11-04 降级的：附录 D 补全 36 词后，该单元一次出现 32 个待标词，超过渲染器每单元上限 `MAX_PANEL = 22`（`yuyu_book/plain.py:37`），构建直接失败；错误信息给的正是这条路——「能在附录 D 查到的降为 extra」。御舆登记表本来就是 44 core / 58 extra，omp 降级后是 24 / 12，密度没有低于姊妹分册。代价：全书签入的虚线提示从 317 处降到 242 处。
- `yuyu-book/notes-omp.json`：39 条眉批（前言 + 33 章 + 5 附录各一条，≤36 字）
- `yuyu-book/reading-paths-omp.json`：33 章 / 381 节档位芯片（起步 33、主干 297、进阶 51）
- `yuyu-book/sources-omp.json` / `revisions-omp.json`
- 这些文件名不是 `build.py` 里的分支判断，也不是 `registry.py` 给的（它只把 13 个登记表名列进 `FILES`
  白名单，不在表里的直接 `unknown registry`）：通俗层三个由 `yuyu_book/plain.py:70 registry_names()`
  按 manifest 的 `product` 键算出（缺省或 `book` → 裸名，`omp` → `-omp` 兄弟），`revisions` 与主题索引
  两个由 manifest 的 `revisions_registry` / `subject_index_registry` 键给出（后者为 `null`，所以 omp
  不排书末索引），骨架与来源则由命令行 `--manifest` / `--sources` 给出
- 插画双轨：章节内 `images/*.jpg` 相对路径嵌入；正文 Mermaid 目前只有 `omp/ch03.md` 一处，
  OVERHAUL-SPEC 的 M3 目标是每篇 ≥1、全书 ≥12，**尚未达成**
- 第三轨：`yuyu-book/illustrations-omp/` 的内联 SVG，46 份 = 39 枚单元章徽（64×64，每单元一枚）
  + 7 幅篇题刻（200×140，每篇一幅），走御舆同一个 `art._read()` 门禁；
  进度与字节账在 `docs/yuyu-overhaul/ILLUST-SYNC.md` 第九、十节

## 本机已验证（America/Adak 对应机器本地时间 2026-11-04）

- `yuyu-omp-zh.html` 20.0 MB，39 units，1 plates，3 cited links，**242 glosses**（附录 D 补全 + 12 词降 extra 之前是 317），
  39 lead bands，381 tier chips，**39 emblems**，**7 headpieces**，39 keeper notes
- `yuyu-omp-zh.pdf` 30.7 MB，**323 pages**，49 bookmarks，0 index folios（19:4x 那次重建——39 枚章徽上盘之后，
  页数与书签都没动；18:3x 那次是七幅题刻上盘之后 323 页，08:20 那次是 30.6 MB / **321 pages**，
  附录 D 补全前那次是 322 页，各版都留在 `docs/yuyu-overhaul/PDF-PAGES.md` 的对照里）
- 御舆 smoke：`build --product book --lang zh --out-dir yuyu-book/.scratch/book-smoke` 成功
- 全量测试：`python -m unittest discover -s tests`（**39**）与 `-s yuyu-book/tests`（**515**）均 OK。
  2026-11-04 19:3x 这一轮重跑过；`docs/yuyu-overhaul/logs/unittest-after-m2.log` 是 M2 那一刻的记录，
  当时是 **501** —— M6 落 `test_product_isolation.py`（9 条）把它抬到 510，题刻那一轮同一文件再加 `OmpArtTray`
  4 条到 **514**，章徽这一轮再加 1 条（`test_every_omp_unit_opens_with_its_own_emblem`）到 **515**，
  `yuyu-book/revisions.json` 最新一条里的「构建器测试 515 项全绿」由 `test_docclaims.py` 逐轮核对

上一版这里写的是 18.6 MB / 24.7 MB / 238 页 / 47 书签——那是 M1 加厚、M2 通俗层之前的一次
排版，已经翻不出那一页了；页数的逐项对照在 `docs/yuyu-overhaul/PDF-PAGES.md`。

未 commit / 未 push。
