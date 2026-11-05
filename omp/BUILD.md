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

Omp 默认加载自己的通俗层登记表，包括术语标注、档位芯片和 39 条按语。
需要比较没有通俗层的排版时，可在 `build.py` 命令中加入 `--no-plain`。

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
- 插画双轨：章节内 `images/*.jpg` 相对路径嵌入；正文有 13 张 Mermaid，覆盖全部七篇，
  已达到每篇 ≥1、全书 ≥12 的要求。16 张已知问题图的替换记录见 `overhaul/ILLUST-CHECKLIST.md`。
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

以上数字保留为 2026-11-04 的历史构建记录；本轮实测与验收结论见 `overhaul/ACCEPTANCE.md`。

## CI 与本地复现

Book CI 的 `book`、`omp` 是独立 job；omp job 先检查结构与交付要求，再生成中文 HTML/PDF，
artifact 名为 `yuyu-omp-dist`。内容 CI 也检查 omp 门禁，并用 `--check --mermaid source` 装配源稿。
实际远端状态以具体提交对应的 workflow run 为准，本地成功不能代替远端运行结果。

Windows 可从仓库根执行：

```powershell
powershell -File omp/overhaul/ci-local.ps1
```

脚本逐条检查原生命令退出码，失败即停止；默认输出到 `.scratch/spec-finish/build/`，
分别放置御舆中文 HTML 与 Omp 中文 HTML/PDF。可通过 `-OutDir` 指定另一个输出目录。
完整共享回归仍使用 `python scripts/bookctl.py check --fast`（等价于 `make check`）。

## 英文开启条件

`en/omp/README.md` 与 `STATUS.md` 只预留翻译入口，当前仍为 `langs=["zh"]`。
需完成前言、33 章、五附录及通俗层、插画标签的英文内容，补齐全部 `en` 路径，
通过双语结构、引用与未翻译汉字检查后，才能扩展语言列表、隔离测试和 CI。
具体顺序见 `yuyu-book/PRODUCTS.md`。

## 用 Python 重绘入门插图

`python scripts/draw_omp_illustrations.py` 默认先写预览；确认后加 `--out-dir omp/images` 更新六张正文插图。
脚本用项目已有 Pillow 与本机中文字体绘制；字体选择、单图生成和语义约束见
`omp/overhaul/PYTHON-ILLUSTRATIONS.md`。重新生成后需构建 Omp 并检查 HTML/PDF 中的字与箭头。
