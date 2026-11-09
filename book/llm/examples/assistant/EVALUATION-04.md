# 1.5B 完整复测与系统提示对照 · 迭代04

日期：2026-11-09。Qwen/Qwen2.5-1.5B-Instruct，revision `989aa7980e4cf806f80c7fef2b1adb7bc71aa306`，CPU，Python 3.13.14、torch 2.14.1+cpu、transformers 5.21.0、tokenizers 0.23.3；OMP/MKL 线程数均为 4。前批两次未完成尝试仍是未完成，不能计分；本页三份报告都跑完原八题。

三轮使用相同历史虚拟环境，继承系统包。另有[干净环境复建](../../../../specs/llm-learning-redesign/evidence/quality-04-environment.json)，不能把它倒填为本次 1.5B 对照环境。权重与分词器指纹见[1.5B 资源记录](../../../../specs/llm-learning-redesign/evidence/extractive-03-model-1.5b.json)，没有重新下载或提交权重。

## 冻结与单变量

原清单 SHA-256 为 `5255ec386cd139b139cb72645c1f9de2c35b1ba569d8175c5eb50ab263b805fd`，三轮开始/结束一致；未删题、改预期、加预算或做 JSON 修复。基线源码来自 `327dd33e9bfa7ccc818077f71866f03c0c79c119`，LF SHA-256 为 `1b3857e3b76193d01577ba0a12fee2f674371d1ad48504f11d57ce1777b3247b`。

原 extract 在用户消息要求 `chunk_id/quote`，系统消息却要求 copy 的 `answer/text/citations`，合同冲突。本次候选**只改 extract 的系统消息**，用户消息、校验器、资料、解码和原预算保持一致。候选系统消息 SHA-256 为 `a33e7084801f818dffe4b7fc20028c7808db864cc0b5d4483638a881ee676876`。计划在基线完成前登记，全文及采用规则见[对照记录](../../../../specs/llm-learning-redesign/evidence/quality-04-comparison.json)。

| 用例 | copy 基线 | extract 基线 | extract 新系统提示 |
| --- | --- | --- | --- |
| normal-wind | citation-failed（失败） | invalid-response（失败） | invalid-response（失败） |
| no-hit-coffee | invalid-response（失败） | insufficient-evidence（通过） | insufficient-evidence（通过） |
| conflict-closing | answered（失败） | insufficient-evidence（失败） | insufficient-evidence（失败） |
| unauthorized-reader | unauthorized（通过） | unauthorized（通过） | unauthorized（通过） |
| missing-source | missing-source（通过） | missing-source（通过） | missing-source（通过） |
| model-missing | model-unavailable（通过） | model-unavailable（通过） | model-unavailable（通过） |
| api-unconfigured | api-config-missing（通过） | api-config-missing（通过） | api-config-missing（通过） |
| agent-calculator | invalid-response（失败） | invalid-request（失败） | invalid-request（失败） |

| 指标 | copy 基线 | extract 基线 | extract 新系统提示 |
| --- | --- | --- | --- |
| 完整八题 | 4/8 | 5/8 | 5/8 |
| fixed 七题子集 | 4/7 | 5/7 | 5/7 |
| 模型调用次数 | 4 | 3 | 3 |
| 输入 token | 5798 | 4562 | 4625 |
| 输出 token | 371 | 96 | 70 |
| 调用耗时 ms（含首次加载） | 1790885.657 | 643170.366 | 593054.373 |
| 加载耗时 ms | 24321.079 | 15291.597 | 10098.124 |

## 判定与剩余失败

采用 extract 专用系统提示；默认 copy 和 agent 提示保持原行为。 两次 extract 均为 5/8，逐例状态相同；本次修复只消除系统/用户消息的 schema 冲突，没有证据表明质量提升。

- 候选没有新接受的 answered/conflict 主张：三道实际生成题中，风速题输出围栏并被拒绝，咖啡机返回不足，冲突题仍只返回不足。没有新的引文可以被错误当成回答。
- 咖啡机不足理由与资料缺少保修期相符；冲突题虽然说存在冲突，却没有按合同返回两份文档的证据，因此仍按原判据失败。
- 五个不调用模型的权限、缺源、缺模型、未配 API 与 agent/extract 边界状态及调用数均与基线一致。
- copy 的原始冲突回答只摘取临时 18:00 规则，省略其 12 月 1 日至 20 日适用条件，不能视为充分回答；原评分失败保留。
- 采用条件只支持消除合同矛盾；不声称分数、事实性、冲突能力或速度改善，K3 继续失败。

Agent/extract 原题要求 answered 和成功工具引用，但该组合不受支持，实际 invalid-request 继续计失败。固定七题子集单列，不能替代完整八题。咖啡机题虽名为 no-hit，实际可能有词项命中；按原证据不足判据评分，不用题名代替检索事实。

这些是开发用例，不是未见留出集；模型拒绝、机械引用校验与语义完整性也要分开。计时来自内存紧张的共用工作站，不得据此声称速度提升。费用均为 null，未计价不代表零成本。K3 与独立教学验收仍未通过。

## 复做与首次响应

当前源码下的本地命令：

```text
python book/llm/examples/assistant/assistant.py evaluate --model <同 revision 的本地目录> --claim-mode copy --json out/copy.json
python book/llm/examples/assistant/assistant.py evaluate --model <同 revision 的本地目录> --claim-mode extract --json out/extract.json
```

复现原 extract 基线需使用上述基线提交；新源码的 extract 若已采用修正，就不再代表旧提示。完整首次输出：[copy](../../../../specs/llm-learning-redesign/evidence/quality-04-baseline-copy.json)、[原 extract](../../../../specs/llm-learning-redesign/evidence/quality-04-baseline-extract.json)、[候选 extract](../../../../specs/llm-learning-redesign/evidence/quality-04-candidate-extract.json)。失败响应未剥围栏、未改写，也未重复到满意后换掉首次结果。
