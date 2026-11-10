# 真实助手冻结评测基线（K3/K4 证据）

本文件保留首次基线、提示词对照和早期七题抽取试验的历史结果。精确位置扩展后的完整八题 copy/extract 对照见 [EVALUATION-03.md](EVALUATION-03.md)，不覆盖或重算下文旧结果。

日期：2026-11-08。模型：本地 `Qwen/Qwen2.5-1.5B-Instruct`，revision `989aa7980e4cf806f80c7fef2b1adb7bc71aa306`，CPU，`local_files_only=True`。清单：[eval-manifest.json](eval-manifest.json)，sha256 `5255ec38…b805fd`，调用前后未变。用例、预算与阈值均来自该文件；未改测试或 runner，本文件不是 CI 基线。

## 结果（8 例，4 通过 / 4 失败）

| 用例 | 期望 | 实际 | 说明 |
| --- | --- | --- | --- |
| normal-wind | answered | citation-failed | 模型找到了正确原句 `## 2026-10-03\n风速 4.2 米每秒`，但 claim 写成“2026-10-03 的观测站记录显示风速为 4.2 米每秒”。精确摘录规则拒绝自由改写；未放宽校验求通过 |
| no-hit-coffee | insufficient-evidence | invalid-response | 输出 Markdown 围栏；严格 JSON 拒绝，首次原文保留 |
| conflict-closing | conflict | answered | 模型未识别 17:30 政策与 18:00 临时通知的冲突 |
| unauthorized-reader | unauthorized | unauthorized | 检索前权限停止 |
| missing-source | missing-source | missing-source | 模型调用前清单失败 |
| model-missing | model-unavailable | model-unavailable | 无备用模型或预置答案 |
| api-unconfigured | api-config-missing | api-config-missing | 显式 API 缺配置时不发网络请求 |
| agent-calculator | answered | invalid-response | 模型输出 `"action":"calculate"`，不是允许的 `tool`/`answer` |

汇总用量：4 次模型调用、5798 输入 token、371 输出 token、延迟 453.7 秒、加载 12.8 秒、费用 `null`（本地 CPU 未定价）。

## 单变量对照：在用户消息末尾追加显式输出契约

只改一个因素：把结尾的“只输出 JSON”换成包含键名、允许动作名和逐字引用要求的完整契约；模型、清单、预算、阈值、校验器均不变。

| 指标 | 基线 | 显式契约 |
| --- | --- | --- |
| 通过 | 4/8 | 4/8 |
| 模型调用 | 4 | 6 |
| 输入 token | 5798 | 10164 |
| agent-calculator | invalid-response（非法动作名） | budget-exhausted（进入真实工具循环但未在 3 步内完成） |
| conflict-closing | answered | insufficient-evidence（仍非 conflict） |

结论：**拒绝该改动**。它让 agent 走到真实工具循环，但没有提高冻结通过数，且增加 75% 输入 token 与两次调用。代码恢复原状；失败证据保留。不能把“失败状态变了”写成质量提升。

## 复现

```bash
python book/llm/examples/assistant/assistant.py evaluate \
  --model /absolute/path/to/Qwen2.5-1.5B-Instruct \
  --json out/eval.json --markdown out/eval.md
```

复现需固定模型 revision 与清单哈希；不得只重跑失败用例后宣称改善，也不得删除失败用例。真实 0.5B 模型在同一严格任务上同样多次输出 Markdown 围栏，未采集为独立基线。

## 边界判定：为什么没有继续放宽

该用例的事实检索已经正确：命中片段含 `2026-10-03` 与 `4.2 米每秒`，模型也复制了这段 quote。失败只发生在它把 claim 改写成一句转述。

若要让它通过，只有两种方案：

1. 接受“quote 真实、claim 是转述”——已被反例否定：同一原句可以为相反结论背书。
2. 改为纯抽取协议：模型只给 `chunk_id` 与 `quote`，报告中的主张文本由程序直接取 quote，answer 也由已核验 quote 组成。

方案 2 不削弱证据边界，但会改变公开的报告/主张契约、章节中的字段说明和模型提示，属于需要单独评审的设计变更，不能在评测调参中顺手改掉。因此本轮保留严格契约与真实失败，把方案 2 列为下一步候选；在评审前不宣称 K3 通过。

在更强模型或人工复核转述之前，K3 的结论是：**检索与权限可用，严格引用边界正确，模型格式与转述能力不足**。

## 可选纯抽取模式（默认关闭）

`--claim-mode extract`（仅 fixed）：模型只返回 `status`、`claims[{chunk_id,quote}]`，可选 `reason`；主张文本由程序直接取 quote，answer 由已核验 quote 组成。默认仍是 `copy`，旧契约与旧报告不变。

同一冻结清单的 7 个 fixed 用例对比（Qwen2.5-1.5B，同一模型与预算）：

| 指标 | copy（默认） | extract |
| --- | --- | --- |
| 通过 | 4/7 | 5/7 |
| 模型调用 | 3 | 3 |
| 输入 token | 约 4.4k | 4562 |
| normal-wind | citation-failed（claim 转述） | invalid-response（Markdown 围栏 + 判为 insufficient） |
| no-hit-coffee | invalid-response（围栏） | insufficient-evidence（通过） |
| conflict-closing | answered（未识别冲突） | insufficient-evidence（仍非 conflict） |

结论：抽取模式移除了“转述被拒”这一失败模式，但没有解决 JSON 围栏、检索后仍判资料不足、冲突漏检；通过数只 +1，且部分差异来自模型输出不稳定。因此保留为可选教学对照，不设为默认，也不据此宣称 K3 通过。agent 模式暂不支持 extract，会明确返回 `invalid-request`。
