# 抽取模式完整对照 · 迭代03

日期：2026-11-09。同一已缓存 Qwen2.5-0.5B-Instruct revision `7ae557604adf67be50417f59c2c2f167def9a775`，CPU，Python 3.13.14、torch 2.14.1+cpu、transformers 5.21.0、tokenizers 0.23.3。模型/分词器/配置文件哈希见[指纹](../../../../specs/llm-learning-redesign/evidence/extractive-03-model.json)。没有调用付费 API 或重新下载权重。

在同一源码版本下依次执行 copy 与 extract，仅改变 claim_mode（因此切换其既有提示和校验合同）。保持原八题清单、预算、检索、文档和模型不变；两轮都设置 `OMP_NUM_THREADS=4`、`MKL_NUM_THREADS=4`。清单 SHA-256 `5255ec386cd139b139cb72645c1f9de2c35b1ba569d8175c5eb50ab263b805fd` 在两轮开始/结束时相同；没有用 `--case` 筛题，也没有把不支持改成通过。

原计划使用 1.5B 模型：首次进程退出（观察到 -1，原因未确定），之后重跑约 40 分钟仍未产出完整报告，期间可用内存一度约 90 MiB，遂主动停止并保留记录。本页改用已缓存的 0.5B 模型完成独立对照；没有下载新权重。它不能替代 1.5B 的新版本复测，也不能把与历史 1.5B 的分数差归因于抽取模式。两轮仅用日志包装器记录逐题边界，实际调用原 run_pipeline，不提供预置答案。

| 用例 | 原期望 | copy 实际 | extract 实际 |
| --- | --- | --- | --- |
| normal-wind | answered | invalid-response | invalid-response |
| no-hit-coffee | insufficient-evidence | invalid-response | invalid-response |
| conflict-closing | conflict | invalid-response | invalid-response |
| unauthorized-reader | unauthorized | unauthorized | unauthorized |
| missing-source | missing-source | missing-source | missing-source |
| model-missing | model-unavailable | model-unavailable | model-unavailable |
| api-unconfigured | api-config-missing | api-config-missing | api-config-missing |
| agent-calculator | answered | tool-failed | invalid-request |

| 指标 | copy | extract |
| --- | --- | --- |
| 完整八题 | 4/8 | 4/8 |
| fixed 七题子集 | 4/7 | 4/7 |
| 模型调用 | 4 | 3 |
| 输入 token | 5798 | 4562 |
| 输出 token | 517 | 413 |
| 生成调用总耗时 ms（含加载） | 361579.26 | 258379.248 |
| 其中模型加载 ms | 8314.027 | 8007.016 |
| 费用 | null，本地未定价 | null，本地未定价 |

**保留默认 copy，extract 仍为可选 fixed 模式；K3 未通过。** 完整八题的 agent-calculator 在 extract 下先于资料/模型访问返回 invalid-request，原题要求 answered 和成功工具引用，因此保留为失败。七题子集单列，不以 5/7 或其他子集数值代替全清单。质量判断仍需检查原始主张/引用是否回答问题，状态正确本身不是语义全对。

四个通过项均为权限、文件、模型或 API 配置的失败边界；本轮没有通过正常回答、资料不足判断或冲突题。extract 少一次调用是因为 agent 组合被提前拒绝，不能据此宣称它以更少调用完成了同一任务。

## 首次输出的具体失败

- copy 正常问答缺少 `status`，使用单数 `citation`；虽然写出 4.2 米每秒，quote 却是记录用途介绍，不能支持风速主张。咖啡机题还编出材料里没有的“保修期是 1 年”，伴随多段 JSON/围栏及截断，被解析器拒绝。
- extract 正常问答和咖啡机题使用 `claim` 而非 `claims`，返回的结构不符合抽取合同；正常题同时列出不同日期的 4.2 与 5.1，却没有引用，不能只改字段名就算正确。
- 两种模式的冲突题均输出不完整 JSON，且未给出可接受的 conflict 报告；保留 token 上限内的首次输出，不通过追加预算或删题修饰成绩。
- copy 的 Agent 确实提出了 calculator 请求，但 expression 的内容多了一层引号，成为字符串字面量，失败回执为 `unsupported-literal`；没有成功计算结果。extract 的该题为 `invalid-request`、零模型调用。

本轮没有产生通过校验的来源引用，因此新的精确位置由 14 项合同测试和历史真实响应重放验证；[重放记录](../../../../specs/llm-learning-redesign/evidence/extractive-03-replay.json)明确标为旧响应重新校验，不能当作本轮模型生成成功。1.5B 在新版本上的完整复测仍待完成。

耗时是这两次串行 CPU 运行的实际观察，运行中采样可用物理内存约 955 MiB，本机还有其他任务，不当作受控性能结论；null 费用也不表示零成本。精确位置的新增不会让错误或不相关引文变正确，JSON 围栏和冲突漏检也不会因位置字段而消失。

首次响应与失败：[copy 完整记录](../../../../specs/llm-learning-redesign/evidence/extractive-03-copy.json)、[extract 完整记录](../../../../specs/llm-learning-redesign/evidence/extractive-03-extract.json)、[汇总及源码哈希](../../../../specs/llm-learning-redesign/evidence/extractive-03-comparison.json)。此前[基线与七题试验](BASELINE.md)作为历史保留，不覆盖。

## 复做

```bash
python book/llm/examples/assistant/assistant.py evaluate --model /path/to/pinned-model --claim-mode copy --json out/copy.json --markdown out/copy.md
python book/llm/examples/assistant/assistant.py evaluate --model /path/to/pinned-model --claim-mode extract --json out/extract.json --markdown out/extract.md
```

使用相同模型 revision、文档和清单字节，并设置上述 OMP/MKL 线程环境；本轮没有设置 ASSISTANT_API_BASE/MODEL，API 用例才能按原判据验证配置缺失。缺资源如实记失败。evaluate 正常结束的退出码 0 表示评测运行完成，不代表八题全部通过。
