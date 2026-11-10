# 来源与许可

这个根仓将两套项目放在一起管理。各目录、引用资料和第三方依赖继续遵循各自的许可；本页不为所有文件授予一个统一的新许可。

| 内容 | 来源与许可范围 |
| --- | --- |
| Agent 项目的书籍文字 | 原《御舆：解码 Agent Harness》，作者 LinTsinghua，来源 [lintsinghua/claude-code-book](https://github.com/lintsinghua/claude-code-book)。保留 [agent-books/LICENSE](agent-books/LICENSE) 中的 CC BY-NC-SA 4.0 及署名、非商业、相同方式共享条件。具体文件另有声明时按该声明处理。 |
| Agent 工具资料与引用 | 版本、来源、引用范围和上游许可分别记录在 [主册来源表](agent-books/yuyu-book/sources.json)、各分册 `sources-*.json` 与[工具源码锁](agent-books/docs/agent-series/sources.lock.json)。工具自身的 MIT 等许可不自动覆盖全部书稿或第三方材料。 |
| 大模型课程与 Vibe Coding 补充原稿 | 保留 [model-course/README.md](model-course/README.md) 的来源说明。Vibe Coding 内容整理自 [datawhalechina/easy-vibe](https://github.com/datawhalechina/easy-vibe)；导入来源尚未明确可用于全部内容的授权范围，本次整合不替它补写开源许可。课程根目录也未提供适用于全部文件的 LICENSE。 |
| 分词快照 | [fixtures/NOTICE.md](model-course/book/llm/fixtures/NOTICE.md) 说明 `js-tiktoken@1.0.21` 数据的使用范围，完整 MIT 许可保存在 [js-tiktoken-LICENSE](model-course/book/llm/fixtures/js-tiktoken-LICENSE)。快照仅保存教学输入涉及的 token ID 与字节。 |
| 小 decoder 教学语料 | [LICENSE-CORPUS](model-course/book/llm/examples/tiny_decoder/LICENSE-CORPUS) 将该目录的 `corpus.jsonl` 与 `sft.jsonl` 以 CC0-1.0 提供。这个范围不扩展到全课程、PyTorch 或其他外部资源。 |

提示词册的“青禾工作坊”及配套人物、活动和回执是原创虚构教学材料；课程中的固定生成、材料核验样例也有自建数据说明。引用这些材料时保留教学性质，不能把它们写成现实活动记录或在线模型的实测输出。

重新分发时，随对应内容保留作者、来源、许可正文及改动说明。未明确授权的内容仍需确认其使用范围；将文件导入本地仓库、生成 PDF 或复制到系列书架，不会改变原有权利。依赖包与图片、字体、模型、数据集的许可仍分别有效。

导入路径、基线和独有文件快照见[整合记录](docs/integration/README.md)，逐文件来源见[导入清单](docs/integration/import-manifest.json)。
