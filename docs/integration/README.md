# 两个项目怎样合到一起

本次整合将 Agent 系列和大模型课程放进一个根仓库。源码分别保留在 `agent-books/` 与 `model-course/`，根目录提供书架、阅读路线和 `series.py`。两侧继续使用各自的构建器、依赖锁与内容判据。

首次导入的本地验收见[合并验收记录](VERIFICATION.md)；新增手绘图、提示词 0.1.1 成品与新仓发布进度见[本轮发布记录](release-20261111.md)。

| 导入内容 | 来源 | 本次基线 |
| --- | --- | --- |
| `agent-books/` | `D:\Users\claude\.agent-series-wt` | `6ee786749b909eeb9a14bc11d8afe7bbde29934c` 加该工作区当前未提交内容，包含 Kimi 与提示词册 |
| `model-course/` | `D:\Users\dmx\vibe-coding-101-course` | `e74c7315bb8e72aa501e11ba4aef29a8efc66c17` 加该工作区当前未提交内容 |
| 旧主目录独有记录 | `D:\Users\claude\claude-code-book-main` | 六份文件另存快照，保留原路径及内容 |

整合提交保留三个父提交：新仓引导提交、Agent 来源提交和课程来源提交。因此两侧历史都可从统一仓库追溯；本地另保留 `source-agent-history` 与 `source-model-course` 分支。子目录不携带自己的 `.git`。这次导入同时保留来源工作区中的未提交源码，因此仅查看两个来源提交号不能还原全部输入；逐文件来源与指纹以 [import-manifest.json](import-manifest.json) 为准。

旧主目录停在 `dcdc3950425178a4f4639901641d43161dc81b00`，它是 Agent 导入基线的祖先，后者领先 107 个提交。排除缓存和派生成品后，核对了旧主目录的 267 个未提交源码文件：171 个与新基线当前内容一致（包括仅换行差异），76 个内容精确存在于新基线可达历史，20 个存在局部差异或版本组合。索引中三份重命名文件的内容也已被历史承接。

[legacy-main-snapshot.zip](legacy-main-snapshot.zip) 保存下列六份本地独有文件：

| 原路径 | 保留原因 |
| --- | --- |
| `.gitignore` | 11 条视频派生 JSON 忽略规则尚未进入新基线 |
| `README.md` | 中文知识卡与样章直达链接；统一根 README 已保留入口 |
| `en/README.md` | 英文知识卡与样章直达链接；统一根 README 已保留入口 |
| `pi/VERIFY.md` | 一次本机构建的独有字节数与 SHA-256 记录 |
| `docs/superpowers/plans/2026-11-03-total-project-transformation.md` | P3/P4/P5 的详细本地验收记录 |
| `tests/test_entry_points.py` | 三项旧过渡入口测试，作为历史记录保留 |

旧 `yuyu-book/build.py` 和 `.github/workflows/check-book.yml` 已在后续平台切换中退出。产品索引逻辑进入 `yuyu_book/cli.py`，Pi 隔离测试进入 `test_pi_product.py`；旧入口测试依赖的 `YUYU_BOOKCTL` 也已退出当前流程。因此快照保留旧记录，当前构建沿用新入口。

课程版本、提示词版本和工具源码版本各自登记，整合日期不覆盖它们。旧报告中的绝对路径、提交号、页数、成品哈希与 CI 地址描述的是当时的版本，保持其历史含义。本次检查的命令、环境和结果另记，不能用旧项目的绿色 CI 证明新根仓已经通过远端 CI，也不能从文件复制或构建成功推断模型质量、教学效果或跨平台可用性。

源码导入清单与阅读成品分别管理。缓存、依赖目录、私有配置和临时文件按导入范围排除；既有 PDF、EPUB 等阅读成品由根收集命令汇总，阅读可用性以本次实际产物为准。来源许可见 [LICENSES.md](../../LICENSES.md)。
