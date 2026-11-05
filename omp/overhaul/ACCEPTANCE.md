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
| K6 已知问题插画 | 关闭 | 16 张替换图复核；`ILLUST-CHECKLIST.md` 全 fixed；成品抽查见下 |
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
