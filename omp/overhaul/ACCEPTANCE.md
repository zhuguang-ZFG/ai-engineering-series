# Omp 改造总验收

执行者：Codex。日期：2026-11-05（Asia/Shanghai；America/Adak 为 2026-11-04）。
本轮基于 `1ec7749bdea31b96729eb307f69e12f446284b2e`，沿用已有 M1/M2 内容和插画替换，补齐收尾交付。

## K1–K12 缺口核对

| 缺口 | 结论 | 证据 |
|---|---|---|
| K1 薄章 | 关闭 | 33 章六要素齐，`audit_structure.py --check` 通过；字数仅作观测，见 `chars-final.txt` |
| K2 实战失败路径 | 关闭 | 33 章均有实验和翻车表；沿用 `THICKEN-LOG.md`，未验证项继续保留标记 |
| K3 guides | 关闭 | `GUIDES-QA.md` 39/39；中文装配通过 |
| K4 通俗层 | 关闭 | 36 词、39 条按语、`plain_optional=false`；242 个正文术语标记 |
| K5 Mermaid | 关闭 | 13 张，12 章、七篇覆盖；`audit_delivery.py` 检查总量与逐篇覆盖 |
| K6 已知问题插画 | 关闭 | 16 张替换图复核；另有 6 张入门概念图改用 Pillow 重绘，清掉 `invoking tools`、`KEY FACTS` 等英文错字；`ILLUST-CHECKLIST.md` 全 fixed；成品抽查见下 |
| K7 CI / 构建 | 本地关闭；新改动远端未验 | `ci-local OK`；御舆中文 HTML、Omp HTML/PDF 均成功；内容 CI 增加严格门禁与源稿装配 |
| K8 版本策略 | 关闭 | `PIN-POLICY.md`、`VERIFY.md` 标准矩阵、附录 E；本机三条复验均 exit 0 |
| K9 共享术语 / 对照 | 关闭 | `COMPARE-YUYU.md` 十行对照；21 个有效 `shared_with`；独立、固定 SHA 的对照来源 |
| K10 英文预留 | 关闭 | `en/omp/README.md`、`STATUS.md`；manifest 保持 zh；预留文件无汉字 |
| K11 文风 | 关闭 | `HUMANIZER-LOG.md`；新增文字保留版本、验证范围与历史状态 |
| K12 本机 / box 漂移 | 真源已明确，镜像同步未验 | 本机 `omp/` 是真源；没有 box 访问通道，不宣称完成同步 |

## 验证记录

- 结构门禁：33/33，ch21/ch22 的未验证标记按契约保留。
- 交付门禁：0 errors；新增七项回归测试通过。
- 源稿装配：Omp 中文 `--check --mermaid source` 通过，39 units、13 plates、39 keeper notes。
- 链接与双语：站点链接、跨册引用、御舆 20 单元结构对拍通过。
- 两份 workflow YAML 解析通过；`git diff --check` 通过。
- `python scripts/bookctl.py check --fast` 六步通过（等价 `make check`）：46 项通用测试、515 项构建器测试；183 份 Markdown 内容检查与 333 张 Mermaid 语法检查均 0 errors。
- `powershell -File omp/overhaul/ci-local.ps1` 输出 `ci-local OK`：御舆中文 HTML 为 20 units，Omp 中文 HTML/PDF 为 39 units。

## 成品核对

本轮输出位于 `.scratch/spec-finish/build/`，通过构建器生成；没有手工编辑 `dist/` 或缓存。

| 文件 | 字节 | 页数 / 书签 | SHA-256 |
|---|---:|---|---|
| `omp/yuyu-omp-zh.html` | 18,824,732 | 39 单元 | `a157963863482a0895ff71638bd33d866901f44ede0d089de5dd6e4644a56e41` |
| `omp/yuyu-omp-zh.pdf` | 29,825,891 | 332 页 / 49 书签 | `2013b89e75c7ed4824b00ea991a4e31d59758d5634dbb9f558cb6aa97cf75e97` |

HTML 的 13 个 `figure.diagram` 全部含 SVG，无残留 Mermaid 源码块；102 张正文位图以 data URI 嵌入，
外部图片请求为 0。PDF 一级书签含前言、七篇、五附录及原理札记、按语集、来源与许可。
332 页高于 238 页基线；页数仍是本机字体下的观测值，不替换御舆 README 的 CI 页数口径。

抽查 PDF 第 47、101、192、213、260 页（图 4-3、9-2、20-2、23-1、28-1）：
图形完整，标签可辨，中文题注与相邻正文没有裁切。逐页截图为
`.scratch/spec-finish/pdf-<页码>.png`，总览为 `pdf-samples.jpg`。

本地可执行验收已完成；box 镜像同步与本轮改动对应的远端 CI 保留为未验项。

## 提交与远端范围

本轮没有执行 `git add`、commit、push、合并，也没有修改其他 worktree。
开始时已有的两份未跟踪插画构建日志原样保留。源稿改动与生成的预览分开：
本地成品、抽查截图和临时日志放在忽略目录 `.scratch/spec-finish/`。

只读查询确认：`1ec7749bdea31b96729eb307f69e12f446284b2e` 的 Book CI 与「检查书籍内容」均为 success。
该结果只覆盖既有提交，本轮未提交改动尚无远端运行结果。

后续可将本轮按以下两组提交，不必重做已在历史中的导入和插画替换：

1. `docs(omp): finish version policy, comparison and English reservation`
2. `test(omp): enforce structure and delivery acceptance in CI`

提交时应把门禁脚本、测试和 workflow 一起纳入；仅提交 workflow 会引用缺失脚本。
box 同步需要在具备该环境访问通道时执行，不能用本地构建结果代替。

## 补记（2026-11-05）：Python 重绘六张入门图

图 1-1、1-2、2-1、7-2、15-1、16-1 改由 `scripts/draw_omp_illustrations.py` 用 Pillow 与本机
中文字体绘制，替换仍带英文错字的手绘版；正文沿用原 JPG 路径，四处图注随画面改写。
绘制命令、语义边界与字体查找见 `PYTHON-ILLUSTRATIONS.md`，`ILLUST-CHECKLIST.md` 记了本轮清单。

首轮发布用质量 94、无色度抽样，单张 330,000–420,000 字节，撞上 `yuyu-book/yuyu_book/art.py`
的 `PHOTO_BYTES`（单图 300,000 字节内嵌预算），`--product omp` 构建直接失败。编码降到质量 80
（小字边缘与 94 无可辨差异）后最坏 271,877 字节；脚本另加护栏，任一图超预算就在写盘前返回非零。

验证：

- `python omp/overhaul/audit_structure.py --check`：33/33 章六要素齐。
- `python omp/overhaul/audit_delivery.py`：0 errors。
- `python -m unittest tests.test_omp_overhaul`：25 项通过；`unittest discover -s tests`：64 项通过。
- `python scripts/bookctl.py check --fast`：64 项通用测试、515 项构建器测试，185 份 Markdown
  与 333 张 Mermaid 均 0 errors。
- `powershell -File omp/overhaul/ci-local.ps1`：`ci-local OK`，御舆中文 HTML 与 Omp HTML/PDF 均成功。

| 文件 | 字节 | 页数 / 书签 | SHA-256 |
|---|---:|---|---|
| `yuyu-omp-zh.html` | 19,683,873 | 39 单元 | `18026664d8f43bfbd0d14003ce8ca80edca7b4086198bc7a970edc66e09b3ffe` |
| `yuyu-omp-zh.pdf` | 30,481,068 | 332 页 / 49 书签 | `b0660f637e0c39feb188cbc3a277b02c6f25e5a8957dc55424e5a54bd689a231` |

页数与书签数与上一轮一致（332 页 / 49 书签），HTML 因六张位图变大增加约 0.9 MB。
PDF 抽查第 14、15、22、80、148、156 页（图 1-1、1-2、2-1、7-2、15-1、16-1）：
版面缩放下标签仍可辨，箭头方向与中文题注未被裁切。逐页截图在
`.scratch/python-illustrations/pdf-pages/`，构建产物在 `.scratch/python-illustrations/build/`。

本轮改动进入独立提交与 PR，远端 CI 以该 PR 的运行记录为准；box 镜像仍未同步。

## 全量手绘替换（B1–B6，2026-11-05）

按 `HANDDRAWN-REWORK-SPEC.md` 把 `omp/images/` 的 92 张旧手绘 JPG 全部改为
`scripts/draw_omp_illustrations.py` 生成；另有 16 张维持 `visual-redesign/` 的 SVG 导出，
4 张为上游截图。批次提交：B1 `0e920c2`、B2 `523238a`、B3 `f4e5c74`、B4 `a265c40`、
B5 `fda8d02`、B6 `b9ec3d1`，截图 `12d0b0b`。B5 顺带为 6 张从未被正文引用的图补了题注与位置，
并把与 `fig23-3-keys` 撞号的 profile 图改为 `fig23-4-profile`。

验证：

- `python scripts/draw_omp_illustrations.py --out-dir .scratch/allcheck`：92 张全量重生成成功，
  最大 271,877 字节，0 张超过 300,000 的 `PHOTO_BYTES`。
- `python omp/overhaul/audit_structure.py --check`：33/33 章六要素齐。
- `python omp/overhaul/audit_delivery.py`：0 errors。
- `python -m unittest tests.test_omp_overhaul`：28 项通过（新增 `IllustrationCoverageTests`：
  每张 JPG 必须属于脚本生成、SVG 导出、上游截图之一，三类互斥，编号与图集一致）。
- `python -m unittest discover -s tests`：67 项通过；`-s yuyu-book/tests`：515 项通过。
- `bookctl build --product omp --lang zh --pdf`：39 单元、13 图版、245 术语、382 个分级徽标，0 index folios。
- `python scripts/bookctl.py check --fast`：6 步通过，333 张 Mermaid 0 errors。

| 文件 | 字节 | 页数 / 书签 | SHA-256 |
|---|---:|---|---|
| `yuyu-omp-zh.html` | 28,935,624 | 39 单元 | `3a43c826d86912f0ffe767dd282683e17cfa42f9af36b5d93209522df90280a9` |
| `yuyu-omp-zh.pdf` | 37,622,560 | 343 页 / 49 书签 | `66c46510bfa73edc3c20a37fbec50fba5ae520ec6e511cd8fa3cfb79ad43e8e5` |

体积上升来自位图分辨率统一为 2400×1600；页数由 332 增到 343：B5 补引用的 6 张图、ch07 新增的
§7.5a 与附录 E.9 各贡献一段版面。

## 上游素材与内容补充（2026-11-05）

授权来自用户「可以在 GitHub 上找仓库增加项目内容、插图等」。上游 `can1357/oh-my-pi` 钉扎提交
`88a69582c755bd000e8dc0290981fc787a4f400c`，许可证 MIT。

- 插图：README 演示 `assets/ask.webp`、`slash.webp`、`models.webp`、`lspv.webp` 转成
  `fig6-6-ask-shot`、`fig6-7-slash-shot`、`fig5-3-model-selector`、`fig11-4-lsp-shot`，宽度压到 1100、
  质量 82，单张 40–49 KB；正文补题注（ch05、ch06、ch11）。来源登记 `sources-omp.json` 的 `omp-readme-assets`。
- 内容一：ch07 新增 §7.5a「把别人拉进同一个会话：`/collab` 与 `omp join`」——命令语义逐条对照本机
  `omp collab --help` 与 `omp join --help`（v18.16.0）核实，链接形态取该 help 的 EXAMPLE。
- 内容二：附录 E.9「上游 README 的二十一项能力，在本书哪里」——21 行对照索引；三处（流式规则、`/resolve` 冲突解决、Slack）标注「未展开」，避免用宣传语充当规范。来源登记 `omp-readme`（`normative: false`）。
- `yuyu-book/reading-paths-omp.json` 的 `omp-ch07` 增补一格 tier，与新增 H2 对齐（13→14）。

## 手绘扩容 B7–B24（2026-11-05/06）

授权来自用户「可以多增加插图和手绘」「要多轮迭代优化」。`omp/images` 由 112 张增至 197 张，
新增 85 张全部由 `scripts/draw_omp_illustrations.py` 生成并登记在 `FIGURES`；正文按
「先图后节」插题注。批次提交：B7 `16ed8bf`、B8 `23d57cb`、B9 `957a9c5`、B10+B11 `25358ac`、
B12+B13 `da2f8c5`、B14 `6531405`、B15 `a3567ad`、B16 `01c865b`、B17 `8d5ec2b`、B18 `e888673`、
B19 `ce8fbda`、B20 `1a3f9b8`、B21 `5051589`；
第二批：B22 `036ae74`（ch1–3）、B23 `21129a4`（附录 A–E）、B24 `1cf861f`（前言双图）；
另有附录 D 证据重指 `85567d8`，以及并入 main（PR #23，P3.6）的合并提交 `7df3c88`。

编码策略：`encode_jpeg()` 先 4:4:4，超 300,000 字节预算才降 4:2:0；旧图重生成逐位一致
（抽查 `fig13-1`、`fig15-1`、`figD-1`，`cmp` 无差异），历史验收哈希不受影响。85 张新图
单张 186–288 KB。

证据对位：插点统一放在该章已有证据行之后；八处被迫位移逐条按内容核对后重指——
`ch13.md:174→178→182`、`ch10.md:149→153→157`、`ch13.md:152→156`、`ch03.md:220→224`、
`ch14.md:57→61`、`appendix-D.md:14`（`85567d8`）、`ch02.md:125→129`（toks）、
`ch03.md:224→228`（子命令）。

验证：

- `python omp/overhaul/audit_structure.py --check`：33/33 章六要素齐。
- `python omp/overhaul/audit_delivery.py`：0 errors。
- `python -m unittest discover -s tests`：67 项通过。
- `python -m unittest discover -s yuyu-book/tests`：并入 main 后通过。
- `python scripts/bookctl.py build --product omp --lang zh --pdf`：39 单元、13 图版、245 术语，
  PDF 397 页 / 49 书签，0 index folios。

| 文件 | 字节 | 页数 / 书签 | SHA-256 |
|---|---:|---|---|
| `yuyu-omp-zh.html` | 55,361,531 | 39 单元 | `8f83fe5089545cfc091c846271f9ff3dbf42b5a35fdea68c5fa9cae1cb2fbce5` |
| `yuyu-omp-zh.pdf` | 58,232,085 | 397 页 / 49 书签 | `4caacb2abcdc522b6f4edae752749350c8cea78c36acdffa4cb327174a1b3fa8` |

体积与页数上升来自新增 85 张位图与对应版面（343→397 页）；构建产物位于 `.scratch/final-build4/`。
