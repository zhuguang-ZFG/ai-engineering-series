# 提示词 0.1.2 阅读修订

本轮代码与评审记录见 [PR #2](https://github.com/zhuguang-ZFG/ai-engineering-series/pull/2)。下列成品数据来自本地验收；远端合并、main 检查与下载产物记录在下文「合并与云端交付」。

本轮补充第 2、10、15 章的三张原创手绘图，解释房间缺失何时需要追问、工具运行到哪一步、开发题与验证题及留出题何时使用。全册现有六张解释图；青禾仍为虚构教学案例，图中的 8/12 来自故障程序的离线检查，未增加模型实测结论。

新图采用纵向布局，减少并排文字在手机上缩小的问题。第 12、13 章另修正三处含混表达：说明核对实际加载材料的动作、将交接产物明确为报告、明确是谁修改用例预期。章节标题、显式 ID、原有代码、表格、数字和引文均保留。

电子书将仓库材料链接转换为网址时，过去仍指向旧仓库，提示词的新材料在那里不存在。生成链接现指向统一仓库的 `agent-books/`；书内章节仍为内部跳转，显式外部引用与固定提交来源保持原地址。练习包来源说明同步更新，包内版本直接读取书籍登记表。

交付复核还发现 HTML 与 EPUB 的作者字段沿用了旧册作者。页面现在读取本册登记的作者，并对属性值转义；提示词册的两种格式均显示“朱光”，与封面一致。回归检查覆盖实际书籍导出，以及含引号、与号和尖括号的作者名。

## 验证与交付

`python series.py check --project all` 已通过：Agent 的 8 步检查包含 268 项通用测试、574 项构建器测试，427 份 Markdown 与 436 个 Mermaid 图无错误；课程检查含 13 项编辑测试、30 项 Python 脚本测试及 36 项 Node 测试。根目录 34 项测试通过，源码链接的 5 项测试覆盖中文路径、片段锚点与固定版本引用。

本轮 HTML、PDF、EPUB 与练习包由源稿重新生成。PDF 为 115 页、29 个书签；六张图分别在第 19、40、47、58、80、89 页，每张图的全部文字都留在同页。未发现空白页、替换字符或超出页面的文字。实际 HTML 在 390/1280 像素、浅色/深色四种组合中无全页横向溢出、坏锚点或外部运行请求；三张新图在 390 像素视口下的最小文字均约 13.26 像素。旧图仍可能需要放大阅读。

EPUB 的 9 张图片均有替代文字，EPUBCheck 5.4.0 零错误、零警告；练习 ZIP 解压后的 31 项测试通过。详细验收记录见[本册 VERIFY](../../agent-books/prompt/VERIFY.md)。模型 A/B、跨模型迁移与独立读者试读仍待完成。

本地最终练习包 `yuyu-prompt-zh-examples.zip` 为 205,176 字节，包含 81 个文件，清单中 80 项载荷摘要均核对一致，版本号为 0.1.2。SHA-256 为 `f3bb63a55d4013bd1349e9f280b53dc1ceffaa5db8d668baca603e953860818c`。此摘要对应本地验收包；云端重新打包的 ZIP 容器元数据可能不同，应使用随包清单核对载荷。

## 合并与云端交付

[PR #2](https://github.com/zhuguang-ZFG/ai-engineering-series/pull/2) 在测试提交 `6f4747618451117fec341449a6ddef20d34e97ae` 上通过检查后合并，合并提交为 [`f24ef4e`](https://github.com/zhuguang-ZFG/ai-engineering-series/commit/f24ef4e0b318a800dd80cb8a2ed6ac09353cdcc4)，合并树与测试提交一致。PR 检查 [42898514232](https://github.com/zhuguang-ZFG/ai-engineering-series/actions/runs/42898514232) 与合并后的 [main 检查 42900801463](https://github.com/zhuguang-ZFG/ai-engineering-series/actions/runs/42900801463) 通过。

[完整构建 42898554763](https://github.com/zhuguang-ZFG/ai-engineering-series/actions/runs/42898554763) 在 Ubuntu 上运行五个任务，全部通过，产出五份下载文件：

| 下载文件 | 内容 | 本次核对 |
| --- | --- | --- |
| [series-prompt-reading-editions](https://github.com/zhuguang-ZFG/ai-engineering-series/actions/runs/42898554763/artifacts/13802617099) | 提示词 0.1.2 的 HTML、PDF、EPUB 与独立练习 ZIP | 已下载并抽查 |
| [series-prompt-epubcheck](https://github.com/zhuguang-ZFG/ai-engineering-series/actions/runs/42898554763/artifacts/13802651925) | 本次提示词 EPUB 的官方检查报告 | 已下载并核对 |
| [series-llm-reading-editions](https://github.com/zhuguang-ZFG/ai-engineering-series/actions/runs/42898554763/artifacts/13801274311) | 课程离线页面、PDF、EPUB、答案册及对应报告 | 未下载展开 |
| [model-course-reading-reports](https://github.com/zhuguang-ZFG/ai-engineering-series/actions/runs/42898554763/artifacts/13801662171) | 课程无障碍、阅读与机制检查报告 | 未下载展开 |
| [agent-books-check-reports](https://github.com/zhuguang-ZFG/ai-engineering-series/actions/runs/42898554763/artifacts/13800883727) | Agent 项目检查报告 | 未下载展开 |

下载的提示词阅读包中，HTML 版本为 0.1.2、作者为「朱光」，六张解释图均有标题与说明；EPUB 的创作者为「朱光」，内容中标有 0.1.2，标识符与 HTML 一致，六张图均有替代文本且图像非空。云端 PDF 的六个图页（第 19、40、47、58、80、89 页）与 EPUB 内六张图像经逐张目视检查，未发现截断、空白或缺失。EPUBCheck 报告使用 5.3.0，对 `yuyu-prompt-zh.epub` 给出零致命错误、零错误、零警告，报告的 EPUB 摘要与包内文件一致。

练习 ZIP 重新打包后容器摘要与本地验收包不同，包内 `package-manifest.json` 版本为 0.1.2；80 项载荷摘要逐项核对一致，没有缺失或额外文件。模型 A/B、跨模型迁移与独立读者试读仍未完成。

首次项目整合的合并提交、绿色 CI 与课程 PDF 修复记录见[前次交付](release-20261111.md)。各轮验证对应自己的源码与产物，不将旧版的页数或文件摘要当作新版结果。
