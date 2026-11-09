# 发布迁移说明：从旧构建链到 bookctl

> 状态（2026-11-09）：P3 输出与 P5 现有账本 Gate 已完成本地审阅，见[验收续作](spec-verification-2026-11-09.md)；P3.8 的迁移偏差仍保留。P4 产品页视觉审计为 GREEN，P7 门禁与 P8.5 已按此前远端/干净克隆证据勾选。P6 缺独立新版视频，用户确认保留媒体验收未完成。`v0.3.6` 已由 `release.yml` 的标签运行 42423483244 发布；本轮没有新的远端 CI 或发布结果。该版正文由人工改写成 Markdown，装配脚本已改为生成 `release-notes.md`，下一次标签运行生效。

## 1. 范围

本文面向仓库维护者与发布操作者，说明旧构建链（`legacy/pre-platform-2026-11-03` 及更早）到当前 `bookctl` 平台的入口变化、产物布局、链接连续性、回滚方式和发布前检查。书稿内容与章节结构不在迁移范围内；它们仍以 Markdown 为唯一源。

## 2. 旧入口 → 新入口

`scripts/bookctl.py` 是仓库唯一命令入口，`Makefile` 只是它的薄包装。底层构建器也可直接运行 `python -m yuyu_book`（在 `yuyu-book/` 下，或设 `PYTHONPATH=yuyu-book`）。

| 旧入口（legacy 标签） | 当前入口 | 说明 |
|---|---|---|
| `python yuyu-book/build.py --lang zh\|en\|both [--pdf]` | `python scripts/bookctl.py build --product book --lang zh\|en\|both [--pdf]` | 等价；`build.py` 已删除 |
| `make book` / `make book-pdf` | 同名 target，内部改调 `bookctl build` | 参数 `BOOK_LANG` 仍可用 |
| `python yuyu-book/build.py --check` | `python scripts/bookctl.py build --check --mermaid source` | 临时装配，不写 `dist/`、不出 PDF |
| `make check`（`build.py --check` + 两套单测 + `check_book.py` + 图语法） | `make check` / `python scripts/bookctl.py check --fast` | 现在是源码模式，不启动浏览器；另加依赖固定、视频配置与产品幂等检查 |
| 无 | `python scripts/bookctl.py check --full` | Fast 之后加渲染装配与双语 PDF |
| `python yuyu-book/build.py --regen-index` | `python scripts/bookctl.py build --regen-index` | 重建索引后仍继续完整构建 |
| `make clean`（内部 `rm -rf`） | `make clean` / `python scripts/bookctl.py clean` | 跨平台删除 `yuyu-book/dist/` |
| `python yuyu-book/build.py --manifest manifest-omp.json --sources sources-omp.json` | `python scripts/bookctl.py build --product omp --lang zh [--pdf]` | 第二分册仍只出中文 |
| 无 | `python scripts/bookctl.py doctor` / `deps` / `video` | 环境诊断、依赖对账、视频工厂 |
| 无 | `python scripts/bookctl.py release --version X.Y.Z --out-dir <目录> [--epub]` | 原子装配发布目录 |
| `.github/workflows/book.yml` + `check-book.yml` | `book.yml` 的 `Fast` / `Full` / `Omp` / `Bootstrap` 与 `release.yml` | `check-book.yml` 已删除，内容门并入 `Fast` |

## 3. 产物布局

日常构建仍写入 `yuyu-book/dist/`：

```text
yuyu-book/dist/
├── yuyu-agent-harness-zh.html / .pdf
├── yuyu-agent-harness-en.html / .pdf
└── yuyu-omp-zh.html / .pdf
```

`bookctl release` 另建一个全新目录（默认 `yuyu-book/dist/release-<version>`，可用 `--out-dir` 指定）：

```text
release-<version>/
├── yuyu-agent-harness-zh.html / .pdf
├── yuyu-agent-harness-en.html / .pdf
├── yuyu-omp-zh.html / .pdf
├── yuyu-agent-harness-zh.epub / -en.epub / yuyu-omp-zh.epub   # 仅 --epub
├── site.zip
├── video-manifests/ch01..ch15/                                 # 各章内容包
├── video-manifest.json
├── release-notes.json
├── release-notes.md                                            # gh release 正文
├── SHA256SUMS
├── build-report.json
└── artifact-manifest.json
```

`site.zip` 解压后是一个离线站点：`index.html`（门户）、`book.html`（中文整书别名）、`portal.html`、入门分册、图集、知识卡、样章、双语整书 HTML/PDF、`cover.png`、`images/`、`illustration-prompts.md` 与站点索引 JSON 都在压缩包根部，沿用旧站点的文件名。`build-report.json` 记录命令、提交、工作树状态、浏览器/字体与耗时；`artifact-manifest.json` 记录依赖、锁文件与产物 SHA-256。

发布是原子的：所有步骤先写入同级的临时目录，全部成功后才整体改名为目标目录；任何一步失败都不会发布半成品，诊断写到 `.scratch/release-failed/`。`--version` 必须与 `yuyu-book/manifest.json` 的 `version` 完全一致，否则退出码为 2。

## 4. 链接连续性

- **文件名不变**：`yuyu-agent-harness-zh.html`、`yuyu-agent-harness-en.html`、两份 PDF、`yuyu-omp-zh.html` 与旧构建相同；`book.html`、`index.html` 这两个站点别名也继续存在。指向这些路径的既有链接不需要改写。
- **章级锚点不变**：`#front`、`#ch01`–`#ch15`、`#apxa`–`#apxd` 来自 manifest 的单元 `id`，不随排版或构建器变化。
- **小节锚点由标题派生**：改标题就是改锚点。发布前应把产物里的锚点清单与上一版对照；`yuyu_book.audit` 会拒绝成品内部的坏锚点与重复 `id`。
- **产品页链接受检**：`scripts/check_products.py` 会重新生成门户、入门分册、图集、知识卡、样章与索引两次，要求字节一致，并检查本地链接与已发布书名是否对得上；它在 Fast 与发布装配里都会运行。
- **部署仍走 Pages**：`release.yml` 产出的是可归档的 `site.zip`，GitHub Pages 的实际部署仍由 `pages.yml` 负责；两者使用同一组文件名，但不要把发布工件当成已部署站点。

## 5. 回滚

`legacy/pre-platform-2026-11-03` 是平台改造前最后一次构建的附注标签（tag object `30182d5`，提交 `6212391`），包含旧的 `yuyu-book/build.py`、旧 `Makefile`、`book.yml` 与 `check-book.yml`。它只用于重建旧链产物，不是发布标签。

```bash
git fetch --tags
git worktree add ../pre-platform legacy/pre-platform-2026-11-03
cd ../pre-platform
npm ci
python -m pip install -r yuyu-book/requirements.txt
python yuyu-book/build.py --lang both --pdf
```

不要对发布分支执行 `git reset --hard` 或强推标签。该标签是整棵树的旧快照：回滚构建链的同时也会回到旧书稿，并失去此后合入的第二分册与 P3–P6 改动。若只是当前构建链无法出包，应优先修前进；确需回滚时，用独立 worktree 或恢复分支重建并明确记录所用标签。

## 6. 已验证与待补证

### 已有本地证据

- 入口迁移：`bookctl` 的 `doctor` / `check` / `build` / `video` / `release` / `deps` / `clean` 已接线，旧 `yuyu-book/build.py` 已从入口删除。
- P3 同输入结构对照：两套内核产物的结构差异为零，索引页码漂移与纯家具空白页均为零，见 [legacy-v2-structure.md](legacy-v2-structure.md)。来源与政策已在 2026-11-09 复核，冻结工件摘要一致，输出 Gate 收口。
- P4 产品页视觉审计：门户、两版入门分册与图集共用一套墨色令牌，生成器两次运行字节一致，见 [product-visual-audit.md](product-visual-audit.md)。
- P5 内容与断言账本：15 章案例可执行、中英代码对应，现有 6 条 claim 发布校验无告警，18 项边界测试通过；过期条目在发布入口实际阻断。范围见[验收续作](spec-verification-2026-11-09.md)。
- 发布装配的代码合同：版本一致性、临时目录装配、原子改名、`SHA256SUMS` 与两份构建报告都在 `scripts/release.py` 中实现。

### 仍待补证

- P3.8 跳过弃用阶段的迁移偏差、P6 旧新字幕与独立渲染视频的兼容审阅。
- 本轮代码的远端 CI 尚未运行；历史 `task_verify` 的 unverified 不改写成通过。
- 若书稿或版式变化，README 的 PDF 页数与 HTML 体积要按发布 CI 的 Noto 产物重钉，不能用本机字体数字替代。

## 7. 发布检查清单

1. 确认工作树干净，版本在 `yuyu-book/manifest.json`、`yuyu-book/revisions.json` 与准备打的标签三处一致。
2. 运行 `python scripts/bookctl.py deps` 与 `doctor`；依赖必须与 `uv.lock` 对齐。
3. 跑 `python scripts/bookctl.py check --full`；在 CI 产物上再跑 `python scripts/check_artifact_claims.py`。
4. 完成干净克隆演练（Windows 与 Ubuntu 各一次），记录能否从零安装到 `doctor` 全绿。
5. 在空目录运行 `python scripts/bookctl.py release --version X.Y.Z --out-dir <新目录> --epub`。
6. 在发布目录运行 `sha256sum --check SHA256SUMS`，核对 `build-report.json` 的提交、工作树状态与浏览器/字体身份。
7. 解压 `site.zip`，离线打开 `index.html`、`book.html` 与至少一章，检查章级锚点、目录和跨章链接。
8. 推送 `vX.Y.Z` 标签，等 `release.yml` 完成 Full、装配与校验，再核对 GitHub Release 资产；手动触发的 workflow 只上传工件，不创建 Release。
9. 发布失败时保留失败报告与标签，不做静默替换；需要回退时按第 5 节使用 `legacy/pre-platform-2026-11-03`。

## 8. 相关记录

- [架构决策记录](../architecture-decisions.md)
- [P3 结构对照](legacy-v2-structure.md)
- [产品页视觉审计](product-visual-audit.md)
- [基线说明](../baseline/README.md)
- [贡献流程](../../CONTRIBUTING.md)

## 2026-11-07 本轮继续验证

动画与正文切片已落地：画廊重播在减少动效偏好下不再启动 JavaScript 动画，运行中切换偏好会停止并恢复静态成品；第 2 章同步澄清取消、清理和背压，第 6 章同步补充记忆读取时的当前证据核对。浏览器与窄测试证据见 `product-visual-audit.md`。

现场命令结果：Fast 八步通过（192 项通用测试、542 项构建器测试、333 张 Mermaid、15 章配置、11 个产物幂等）；最终双语源稿装配通过，Omp 六要素 33/33、交付审计 0 errors。`prove --config-only` 对 ch01–ch05 各用两个独立进程重建，输出字节一致。`ch06 --audio` 正确退出 1，明确报告长短版均无真实录音；不能据此宣称音频已交付。

受管验证仍为 **unverified**：`task_verify run` 返回 `project-or-git-baseline-unavailable`、`checks=[]`，不是失败也不是通过。GitNexus 现场只有无关仓库的索引，本仓库未索引，未改动任何索引。

总计划保持未完成：P3/P5 的测试与比较政策尚待审查，P6 的真实音频与关键帧仍缺证，P8 的全新 Windows/Ubuntu 克隆演练与正式发布尚无本轮结果。既有暂存删除、测试、CI 与发布脚本也须按各自范围审查；本轮未将它们批量提交或合并，未用旧 PR 的成功状态替代本轮改动的 CI。

用户随后批准前述候选审查范围。补充交叉引用检查发现一个稳定 ID 迁移兼容缺口：`check_crossrefs.py` 原来只读文件第一行，遇到 H1 前的块注释便误报章节缺失。最小回归先出现 1 failed / 1 passed；读取边界改为复用 `markdown_scan.scan_markdown()` 的可见正文后，同两条回归通过，真实双向检查为 23 / 49 条、0 bad，既有 Omp 28 项测试通过。注释与代码围栏中的假标题仍不能满足缺失章节引用，未删引用或放宽目标匹配。

本次新加 `tests/test_crossrefs.py` 两条行为回归，并修改检查输入 `docs/yuyu-overhaul/check_crossrefs.py`；这两项在前述批准之后产生，仍须单独审查并保持 **unverified**。前述 Fast 计数对应增加这两条回归之前的运行，不回写成更大的通过计数。

两项交叉引用候选随后获用户批准；再次执行 `task_verify run` 仍返回 `project-or-git-baseline-unavailable`、`checks=[]`，批准不等于受管检查通过。本机真实媒体检查补充：ch01、ch02、ch03、ch04 的 `check --chapter ... --audio` 均退出 0；ch05 退出 1，原因为 long 格式仍是 scripted 且没有 narration 声明，short 资产未报错。ch06–ch15 未找到真实录音。未改变 episode 状态、音频要求或质量阈值来消除这项失败。

PDF 抽查还发现第 2 章三层 Mermaid 在纸面并排压成细带；双语源码只增加不可见布局连线 `~~~`，使各层纵向排列，不新增流程或依赖语义。旧排版快照不作为最终成品交付，最终重建目录为 `.scratch/delivery-layout-20261107/`。

最终本地成品已生成：御舆中文 PDF 524 页 / 28 书签（25,385,887 B）、英文 PDF 581 页 / 28 书签（12,937,002 B）、Omp PDF 347 页 / 49 书签（37,770,646 B）。对应 EPUB 分别为 12,729,514 / 9,565,148 / 14,781,667 B；三份 EPUBCheck 均报告 0 fatals / 0 errors / 0 warnings / 0 infos。ZIP 完整性、首项未压缩 mimetype、图片内嵌和无脚本检查通过；中文 EPUB 在 480 px 浏览器中实际打开第 2 章，缺图 0，正文可重排。PDF 首／中／末页文本与书签检查通过，中文第 66 页图版目视确认纵排。

首轮 EPUB 转换在整本长页直接截图 SVG 时超时；`build_epub.py` 现在把每张 SVG 连同计算后的墨色、字体及 viewBox 比例移到独立栅格页再截图，避免书籍滚动／布局干扰，不增大超时也不跳过失败图。真实三册转换与 EPUBCheck 是修复后的端到端证据；未新增永久 EPUB 回归，隔离绘图仍缺专门的失败路径回归。此实现和最终成品为本地未提交候选，不能冒称由 HEAD 单独重建。

## 2026-11-08 合并后收口

平台候选经 PR #32 以 merge commit `ca807e647b10dff9dccc89ebf92a8bba06ae9c24` 合入 `main`。该提交的 Book CI（run 42400549985）Fast / Full / Omp / Bootstrap（windows-latest、ubuntu-latest）全部成功，Pages（run 42400550064）成功。`release.yml` 在 `30ca46a` 上手动运行成功（run 42397600190）；该提交与合并提交的树同为 `b65e1970e9765326e44c9796919420d74846c1b3`。

最终本地成品在确认绿色之后从全新 Windows clone（detach 合并提交，未复用旧 `dist/`）重建到 `ebook-final-ca807e6-green/`，`build-report.json` 记录的提交为 `ca807e6`。此前 `.scratch/delivery-layout-20261107/` 与 `ebook-final-ca807e6/` 的构建早于 Full 结案，只作中间验证，不作为最终交付。

| 分册 | PDF 页数 / 书签 | PDF 字节 | EPUB 字节 |
|---|---|---:|---:|
| `yuyu-agent-harness-zh` | 524 / 28 | 23,528,265 | 12,729,807 |
| `yuyu-agent-harness-en` | 581 / 28 | 12,016,293 | 9,565,176 |
| `yuyu-omp-zh` | 432 / 49 | 61,253,411 | 30,065,292 |

Omp 分册由 347 页增至 432 页、体积由 37.8 MB 增至 61.3 MB，来自合并 `main` 后的照片与版式内容，不是本轮动画切片引入的回归。三份 EPUB 的 EPUBCheck 均为 0 fatals / 0 errors / 0 warnings / 0 infos；ZIP 首项为未压缩 `mimetype`、无脚本、正文图片全部内嵌。PDF 首／中／末页文本与书签检查通过，中文第 66 页三层图版目视确认纵排。

`SHA256SUMS` 覆盖 3 份 HTML、3 份 PDF、3 份 EPUB，共 9 项，用 Python `hashlib` 逐项复核一致。本机 Git Bash 的 `sha256sum -c` 因 MSYS 文本模式误报全部失败；同一清单格式在 Linux CI 的 `Verify checksums` 步骤已通过，产物本身无差异。两次重建的 EPUB 摘要不同（`source_sha256` 相同），转换会写入运行时间元数据，故跨运行复核以结构和 EPUBCheck 为准，不要求字节相等。

未完成项（当时）：P8.6 的 `v*` 标签与 GitHub Release 在合并当日尚未创建（见下节发布结果）；P3/P5 门禁仍待独立审阅；P6.4 的字幕与关键帧比较仍缺旧版 SRT 证据；`task_verify` 仍返回 `project-or-git-baseline-unavailable`、`checks=[]`。README 的 PDF 页数与 HTML 体积继续采用 CI Noto 口径，不用本机字体数字替代。

## 2026-11-08 v0.3.6 发布

标签 `v0.3.6`（标签对象 `cbdbe0f`）指向提交 `4050c7c5a758c23aa3ae769609b83fde22d43630`；该提交的 Book CI（run 42420868596）与 Pages（run 42420868560）在打标签前已全绿。`release.yml` 由标签推送触发（run 42423483244，52m23s），完成 Full、断言检查、装配、`sha256sum --check` 与 `gh release create`，发布 15 个资产：三册 HTML/PDF/EPUB、`site.zip`、`video-manifest.json`、`release-notes.json`、`build-report.json`、`artifact-manifest.json` 与 `SHA256SUMS`。

发布后逐一复核：14 个可直接下载的文件与 `SHA256SUMS` 摘要一致；`SHA256SUMS` 另含 239 条 `video-manifests/**` 路径，它们只存在于装配目录与站点包，不作为单独资产上传（`unpublished_all_video=true`）。PDF 为中文 520 页 / 28 书签 / 34.5 MB、英文 559 页 / 28 书签 / 23.5 MB、Omp 432 页 / 49 书签 / 72.0 MB；三份 EPUB 的 ZIP 与未压缩 `mimetype` 首项通过；`site.zip` 含 `index.html` 与 `book.html`；`build-report.json` 记录提交 `4050c7c`、状态 `passed`。

流水线原先把 `release-notes.json`（机器可读 JSON）直接当作 `gh release create --notes-file`，`v0.3.6` 的正文因此是 JSON，发布后用 `gh release edit --notes-file` 换成可读 Markdown。现在装配脚本自己写两份：`release-notes.json` 保留机器可读记录，`release-notes.md` 由 `release_notes_markdown()` 从 `yuyu-book/revisions.json` 的最新条目渲染成 Markdown（标题带日期，中英各一节，附 `sha256sum --check SHA256SUMS` 与迁移说明指引）；`release.yml` 用它作 `--notes-file` 并把 `*.md` 一并上传。`tests/test_release_contracts.py` 的 `ReleaseNotes` 逐条对照账本，`tests/test_ci_contracts.py` 的 `test_release_body_is_published_from_markdown_notes` 钉住 workflow 只引用 Markdown。下一次标签运行的正文才会真正走这条路径；`v0.3.6` 的正文仍是人工修正的版本。

README 的 CI PDF 体积曾写为 36.4 / 24.3 MB，而发布资产实测为 34.5 / 23.5 MB；页数 520 / 559 与 `check_artifact_claims.py` 的对账口径未变。两版 README 的 PDF 体积与本机 Windows 体积已按发布与本轮干净克隆实测回填。
