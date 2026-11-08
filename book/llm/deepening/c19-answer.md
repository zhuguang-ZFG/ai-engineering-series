# C19 答案与核对依据

本文件给诊断顺序、算术和对照记录方式，不提供“你的检索器得分”。所有实际数值必须来自你的 `inspect retrieve` / `run` 报告。

## 1. 第一失败边界怎么判

最短路径：

```text
先看 status
→ 再看 usage.calls
→ 再看 retrieval.hits / used
→ 再看 diagnostics.prompt.used_chunk_ids
→ 再看 first_raw_response
→ 再看 first_failure.stage / errors
→ 最后才看 answer
```

对应关系：

| 观察 | 更早的边界 | 不应直接归因 |
| --- | --- | --- |
| `usage.calls=0` 且 `hits=[]` | 检索零命中/阈值 | 模型不会答 |
| `usage.calls=0` 且 `status=unauthorized` | 权限 | 检索排序 |
| `hits` 有正确片段但 `used=false`，并有 `prompt budget dropped` | 提示预算/选择 | 检索没找到 |
| `hits` 有正确片段、`used=true`，claim 选了另一个数字 | 生成/选择 | 切块 |
| `first_failure.stage=validate`，错误是 “claim must be an exact extract” | 提取式契约 | 检索或模型不可用 |
| `first_failure.stage=parse`，raw 是 Markdown 围栏 | 输出格式/解析 | 事实错误 |
| `tool_receipts[].status=failed` | 工具执行/权限 | 模型事实错误 |
| `answered` 且 quote 有效，但条件被截断 | 最终语义复核 | 机械校验已经通过 |

**关键原则**：只要更早的边界已经偏离，后面的现象就是后果。不要把最终的“答错”当成第一原因。

## 2. 三个最小例的答案

### 例 A：检索成功，生成选错

证据组合：

- `retrieval.hits[].used=true`；
- `diagnostics.prompt.used_chunk_ids` 包含该 chunk；
- 该 chunk 的 `text` 同时包含“风速 4.2”和“阵风 6.8”；
- 最终 claim 引用同一 chunk，但 `quote` 是“风速 4.2”。

结论：检索和提示选择都成功，第一边界在模型选择/生成。修复顺序：

1. 先改问题或提示，明确要求“阵风，不是平均风速”；
2. 仍失败时换模型或调整解码设置，但保持其他条件不变；
3. 不要盲目增大 `top_k`，因为相关段落已经在上下文里。

### 例 B：命中被提示预算丢掉

证据组合：

- `retrieval.hits` 中有正确 chunk，但 `used=false`；
- `diagnostics.warnings` 有 `prompt budget dropped <chunk_id>`；
- `diagnostics.prompt.used_chunk_ids` 不含该 chunk；
- 最终 claim 引用了另一个 chunk，或出现 `unknown chunk_id` 的 `citation-failed`。

结论：第一边界是提示组装。修复顺序：

1. 提高 `max_prompt_tokens`，确认模型窗口允许；
2. 降低 `top_k` 或减小 chunk 大小，减少无关片段挤占；
3. 若仍放不下，报告 `prompt-budget-exceeded`，不要静默丢掉证据后假装回答完整。

### 例 C：提取失败

证据组合：

- `first_failure.stage=validate`；
- `errors` 含 `source claim must be an exact extract of its supporting quote`；
- 检索、调用都可能有正常记录。

结论：第一边界是输出契约，不是检索。当前实现要求 claim 逐字来自 quote，answer 只能由已核验 claim 组成；改写和额外推断会被拒绝。修复方式：

- 让模型只输出材料中的原文片段；
- 或把生成的候选 claim 交给人工确认，再决定是否进入最终答案；
- 不要通过放宽校验、删掉 quote 或改成“只要引用存在就算支持”来绕过。

## 3. 精确率/召回率的标准答案

题目表：

| 项目 | Q1 | Q2 | Q3 |
| --- | --- | --- | --- |
| 相关 | A,B,C | D,E | F |
| 取回 | A,D,E | D,E | 无 |
| TP | 1 | 2 | 0 |
| FP | 2 | 0 | 0 |
| FN | 2 | 0 | 1 |
| P | 1/3 | 1 | n/a |
| R | 1/3 | 1 | 0/1=0 |
| hit | 1 | 1 | 0 |

计算：

- Q1：\(P=1/3\approx0.333\)，\(R=1/3\approx0.333\)。
- Q2：\(P=2/2=1\)，\(R=2/2=1\)。
- Q3：precision 分母为 0，写 `n/a`；recall \(=0/1=0\)；hit=0。
- 微平均：把 Q1–Q3 的 TP/FP/FN 全部相加，\(P=3/5=0.6\)，\(R=3/6=0.5\)。
- 宏平均有三种写法，必须写明：
  - 完全排除空检索 Q3，只对 Q1/Q2 平均：\(P=(1/3+1)/2=2/3\)，\(R=(1/3+1)/2=2/3\)；
  - 保留 Q3 的 recall=0，但 precision 记 `n/a`，precision 只对 Q1/Q2 平均：\(P=2/3\)，\(R=(1/3+1+0)/3=4/9\approx0.444\)；
  - 把 Q3 的 precision 也记为 0：\(P=(1/3+1+0)/3=4/9\approx0.444\)，\(R\) 同样 \(4/9\)。
- 这说明：空检索的 precision 处理会改变宏平均。报告应同时给出逐查询明细和所用口径；不能只写一个“0.444”或“0.667”而不说 Q3 怎么处理。

若只取 Q1/Q2 两个查询，微平均是 \(3/5=0.6\)，宏平均是 \(2/3\approx0.667\)，hit=1.0。

## 4. 单因素切块对照的答案

合格记录：

```text
条件 A：chunk_chars=480, chunk_overlap=80, keyword, threshold=0.08, top_k=3
条件 B：chunk_chars=240, chunk_overlap=80, keyword, threshold=0.08, top_k=3
其余：同一文档版本、同一查询集、同一模型（本轮不调用模型）
```

必须做：

1. 用 `inspect chunk` 保存两套 `start/end`；
2. 用 `inspect retrieve` 保存两套 `hits`；
3. 对每套条件重新标注相关 chunk；
4. 逐查询计算 P/R；
5. 填微/宏/hit；
6. 写结论：采用、不采用或证据不足。

不合格：

- 拿条件 A 的相关 ID 评价条件 B；
- 同时把 `top_k` 从 3 改成 5；
- 删掉低分查询；
- 只看 hit 上升就说召回变好；
- 把切块变小后“命中更多短片段”误当成答案更完整。

切块变小的常见代价：同一事实被拆到多个 chunk，单块可能缺少完整条件；`top_k` 不变时，可能取回更多碎片但缺少上下文。切块变大的常见代价：无关内容进入提示，挤占预算。两种都要在记录里说明。

## 5. 三种失败各一例

合格答案应能写出类似下面的对照（具体字段来自你的报告）：

| 类型 | 状态 | 关键证据 | 第一边界 | 下一步 |
| --- | --- | --- | --- | --- |
| 零命中 | `insufficient-evidence` | `hits=[]`, `usage.calls=0` | 查询/阈值/切块 | 改查询表达，仍单因素对照 |
| 取回没用对 | `answered` 但数字错 | 正确 chunk `used=true`，claim quote 选了另一句 | 生成/选择 | 改提示或模型，不加 `top_k` |
| 提取失败 | `citation-failed` | `first_failure.stage=validate`，claim 不是 quote 子串 | 输出契约 | 输出原文片段，人工确认语义 |

“answered 但语义不完整”的例子：材料写“12 月 1 日至 20 日调整为 18:00”，claim 只写“闭站时间 18:00”。quote 可能存在，机械校验通过；但 claim 丢掉了适用日期，属于语义不完整。第一边界在最终人工复核，修复应补充日期条件，而不是把它算成检索命中。

## 6. 评分表

| 项目 | 合格 | 不合格 |
| --- | --- | --- |
| 诊断顺序 | 从权限/调用前到生成/引用逐层排除 | 一上来就换模型 |
| 调用前/后 | 用 `usage.calls` 分开 | 把零命中说成模型错 |
| 检索证据 | 看 `hits`、`used`、`prompt.used_chunk_ids` | 只看最终 answer |
| 指标 | 分母、微/宏、空结果口径清楚 | 百分比无分母、hit 当召回 |
| 单因素 | 同集合同模型只改一个条件 | 多因素混改、沿用旧标签 |
| 提取契约 | 区分机械通过与语义支持 | 声称逐字 quote 能证明改写 |
| 失败保留 | 保存原始输出和 `first_failure` | 删失败、放宽门槛、手工补答案 |

没有实际报告时，以上只能作为核对表，不能写成“已通过”。
