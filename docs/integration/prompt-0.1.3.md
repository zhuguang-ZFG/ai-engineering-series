# 提示词 0.1.3 正文精修与图版重排

本轮把第 7、8、16 章三张图重排为纵向版面，并对全书正文做第二轮精修。下列成品数据来自本地验收；远端合并、main 检查与下载产物记录在下文「合并与云端交付」。

0.1.1 加入的三张图当时按 760 像素宽的横向画布绘制，电子书在 390 像素一栏里按宽度整体缩放，图内最小文字只剩 6.76–7.14 像素，正文里的解释反而比图更清楚。本轮把三张图改为与其他三张一致的 560 像素宽纵向版面：材料版本图改为三份材料自上而下堆叠，每项字段另起一行；会话交接图把「相符」与「有差异」两条分支并排放在核对菱形下方，中断时间线折成两行；配对比较图保留 A/B 两列矩阵，把脚注拆成三行。图内文字逐串与上一版对照，只移动换行位置，信息没有增删；三张图仍在 20 KB 上限内。窄屏可读性从此由测试守住：`yuyu-book/tests/test_art.py` 断言每张图的 viewBox 宽与最小字号之比，390 像素列宽下最小字号低于 13 像素即失败。

正文这一轮读的是句子本身，不是词表：回指式复述（把上一句刚说过的结论再说一遍）、段落开头的预告句（「下面从输入检查开始」）、把操作结果拔高成判断的句子。22 份文件逐项核对，9 份共改动 25 行——第 1、2、3、5、6、7、16、17 章与附录 A，其余 13 份一字未动。核对脚本要求行数不变、标题与表格等受保护行逐字节相同、空行结构不变、行内代码/链接/引文/数字集合不变；改完再逐句回到上下文，确认没有把「尚未运行」写成「已经运行」、没有新增事实。第 16 章一处把「约定自相矛盾足以成为保留修正的理由」改为按逐例状态陈述，因为原句把一次改动的原因说成了整体结论。

## 验证与交付

`python series.py check --project all` 已通过：Agent 的 8 步检查包含 268 项通用测试、575 项构建器测试，427 份 Markdown 与 436 个 Mermaid 图无错误；课程检查含 13 项编辑测试、30 项 Python 脚本测试及 36 项 Node 测试。根目录 34 项测试通过。构建器测试由上一轮的 574 项增至 575 项，新增的是窄屏字号判据；`revisions.json` 最新一条记录同步改为此数。

本轮 HTML、PDF、EPUB 与练习包由源稿重新生成。PDF 为 118 页、29 个书签；六张图分别在第 19、40、49、60、82、92 页，每张图的全部文字都留在同页，未发现空白页、替换字符或超出页面的文字。实际 HTML 在 390/1280 像素、浅色/深色四种组合中无全页横向溢出、坏锚点或外部运行请求；六张图在 390 像素视口下的最小文字均约 13.26 像素，本轮起不再区分「新图」与「旧图」。EPUB 的 9 张图片均有替代文字；练习 ZIP 解压后的 31 项测试通过，包内 `package-manifest.json` 版本为 0.1.3。详细验收记录见[本册 VERIFY](../../agent-books/prompt/VERIFY.md)。模型 A/B、跨模型迁移与独立读者试读仍待完成。

EPUBCheck 本轮改用与 CI 相同的固定发布包 5.3.0（SHA-256 `6c07e68584b2e2ce2f89fe06e1246dfead3eb36b46b340e7d93524f29dcff6c5`），对 `yuyu-prompt-zh.epub` 给出零致命错误、零错误、零警告；0.1.2 及更早记录用的是 5.4.0，两版报告不能互相替代。

本地最终练习包 `yuyu-prompt-zh-examples.zip` 为 225,108 字节，包含 83 个文件，清单中 82 项载荷摘要均核对一致，版本号为 0.1.3。SHA-256 为 `63f23da902d5b558cf89c450100aca145805239cc3cfc3c1ec1b62fc57849f32`。跑 31 项测试时用的是先于验证记录打包的那份校验包（225,151 字节，SHA-256 `25e3da55…`），它的摘要记在证据的 `validation_package_sha256` 字段，与上面这份包含验证记录的成品包不是同一文件。云端重新打包的 ZIP 容器元数据可能不同，应使用随包清单核对载荷。

## 合并与云端交付

[PR #4](https://github.com/zhuguang-ZFG/ai-engineering-series/pull/4) 在测试提交 `13cbd0e9d49d67e52de390c9eddbdcde7ca6c1dd` 上通过检查后合并，合并提交为 [`3c21752`](https://github.com/zhuguang-ZFG/ai-engineering-series/commit/3c217524c0625521ff3aa596b3514ff0f0318911)，两者文件树同为 `bb507923de9d49261a8c776b27f3d2123e33c666`，即检查通过的内容就是落进 main 的内容。PR 检查 [42948027180](https://github.com/zhuguang-ZFG/ai-engineering-series/actions/runs/42948027180) 与合并后的 [main 检查 42948833787](https://github.com/zhuguang-ZFG/ai-engineering-series/actions/runs/42948833787) 均通过；这两次运行默认不构建阅读包，产物由下面的完整构建提供。

[完整构建 42949923614](https://github.com/zhuguang-ZFG/ai-engineering-series/actions/runs/42949923614) 以 `build_books=true` 在 main 上触发，五个任务全部通过，产出五份下载文件：

| 下载文件 | 内容 | 本次核对 |
| --- | --- | --- |
| [series-prompt-reading-editions](https://github.com/zhuguang-ZFG/ai-engineering-series/actions/runs/42949923614/artifacts/13824972610) | 提示词 0.1.3 的 HTML、PDF、EPUB 与独立练习 ZIP | 已下载并逐项核对 |
| [series-prompt-epubcheck](https://github.com/zhuguang-ZFG/ai-engineering-series/actions/runs/42949923614/artifacts/13824818039) | 本次提示词 EPUB 的官方检查报告 | 已下载并核对 |
| [series-llm-reading-editions](https://github.com/zhuguang-ZFG/ai-engineering-series/actions/runs/42949923614/artifacts/13824424791) | 课程离线页面、PDF、EPUB、答案册及对应报告 | 未下载展开 |
| [model-course-reading-reports](https://github.com/zhuguang-ZFG/ai-engineering-series/actions/runs/42949923614/artifacts/13824023925) | 课程无障碍、阅读与机制检查报告 | 未下载展开 |
| [agent-books-check-reports](https://github.com/zhuguang-ZFG/ai-engineering-series/actions/runs/42949923614/artifacts/13825091647) | Agent 项目检查报告 | 未下载展开 |

云端阅读包在 Ubuntu 上重建：HTML 为 533,995 字节（SHA-256 `553ef4a8…`），作者元数据为「朱光」，版本标记含 0.1.3，六张解释图的 viewBox 均为 560 宽，其中本轮重排的三张分别为 710、800、750 高，六个 `<desc>` 齐备，无外部运行请求。PDF 为 17,634,155 字节、118 页、29 个书签，六图仍在第 19、40、49、60、82、92 页，无空白页、无替换字符；另把重排的三张所在页（第 40、49、92 页）在 Linux 字体下逐张目视检查，文字未截断、图注仍在同页。EPUB 为 1,276,413 字节，创作者为「朱光」，标识符 `urn:sha256:553ef4a8…` 与云端 HTML 一致，9 张图均有替代文字；CI 的 EPUBCheck 5.3.0 报告对它给出零致命错误、零错误、零警告，报告记录的 EPUB 摘要与包内文件一致。练习 ZIP 为 224,726 字节、83 个文件，`package-manifest.json` 版本 0.1.3，82 项载荷摘要逐项核对一致，无缺失或多余文件。

云端与本地是两次独立构建，三份电子书文件的字节并不相同（HTML 相差 3,400 字节，PDF 相差 12,754,581 字节，EPUB 相差 15,887 字节），本轮只核对页数、书签数、图所在页与文字落位一致，未对这些字节差逐项归因。练习 ZIP 的 82 项载荷中有 37 项摘要不同，逐项验证后全部由换行符差异造成：本地工作副本按 CRLF 保存，CI 检出为 LF；把 CRLF 换成 LF 后 37 项摘要与云端一致，其余 45 项本就相同。

模型 A/B、跨模型迁移与独立读者试读仍未完成。上一轮的合并与云端数据见 [0.1.2 阅读修订](prompt-0.1.2.md)。
