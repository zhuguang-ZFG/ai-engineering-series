# C21 答案与核对依据

本文件给出固定流程与 Agent 的对照方法、失败状态和停止条件。实际调用次数、延迟和结果必须来自你的报告；没有运行就写“未运行”。

## 1. 判据答案

一个合格的决策表：

| 问题 | 若“是” | 若“否” |
| --- | --- | --- |
| 步骤是否事先完全确定？ | 固定流程优先 | 继续判断 |
| 是否必须执行真实动作？ | 需要工具 | 可能只需检索/回答 |
| 下一步是否依赖中间结果？ | Agent 可能有益 | 固定调用更简单 |
| 错误代价是否高？ | 固定流程 + 人工确认 | 可考虑有限 Agent |
| 是否有冻结对照？ | 可以比较 | 先补 C18，不急着上 Agent |

“需要工具”不等于“需要 Agent”。固定流程也可以调用工具；Agent 的额外能力是**模型选择下一步**，代价是更多调用、更多状态和更复杂的失败路径。

## 2. 同一计算题的对照

题目：

> 2026-10-03 风速 4.2 米每秒，连续 24 小时总行程是多少米？请用 calculator 计算 4.2*86400。

### 固定模式

命令：

```bash
python book/llm/examples/assistant/assistant.py run \
  --docs book/llm/examples/assistant/documents.json \
  --reader student \
  --question "值班记录里 2026-10-03 的风速是 4.2 米每秒。如果连续 24 小时都保持这个风速，总行程是多少米？请计算 4.2*86400。" \
  --model path/to/local-model \
  --mode fixed --top-k 3 --max-new-tokens 192 \
  --json out/c21/fixed.json
```

应检查：

- `mode` 为 `fixed`；
- `tool_receipts` 为空；
- 若模型只输出“362880”而没有 source quote，`insufficient-evidence` 或 `citation-failed` 都可能是正确结果；
- 不能因为模型“算对了”就认为证据充分；固定模式没有执行工具。

### Agent 模式

命令：

```bash
python book/llm/examples/assistant/assistant.py run \
  --docs book/llm/examples/assistant/documents.json \
  --reader student \
  --question "值班记录里 2026-10-03 的风速是 4.2 米每秒。如果连续 24 小时都保持这个风速，总行程是多少米？请用 calculator 计算 4.2*86400。" \
  --model path/to/local-model \
  --mode agent \
  --allowed-tools calculator \
  --max-steps 4 --max-tool-calls 2 \
  --top-k 3 --max-new-tokens 192 \
  --json out/c21/agent.json
```

合格证据链：

```text
模型请求：action=tool, tool=calculator, arguments={"expression":"4.2*86400"}
执行回执：receipt_id=tool-1, status=succeeded, result=362880
最终 claim：包含 362880，并引用 {"tool_receipt_id":"tool-1"}
最终 answer：只包含已核验 claim 的文本
```

注意：

- `4.2*86400 = 362880` 是算术事实，但报告仍要证明工具真的执行了；
- `usage.calls` 至少 2（工具请求 + 最终回答），具体取决于模型行为；
- `tool_receipts` 数量不等于 `usage.calls`；
- 若模型直接回答而不调用工具，`tool_receipts` 为空，最终可能因没有材料 quote 被拒绝；这不是工具失败。

### 结论可以是什么

- 如果 Agent 质量与固定流程相同，但调用次数/延迟更高：**不采用 Agent**。
- 如果固定流程无法合法地产生计算证据，而 Agent 能用工具回执完成：可以考虑采用，但要有预算和权限边界。
- 如果 Agent 经常走错步骤或预算耗尽：先修提示/模型/任务设计，不能把失败隐藏成“自主性代价”。

## 3. 不需要 Agent 的对照

问题：“2026-10-03 的风速是多少？”

固定模式足够。Agent 模式即使最终也答对，通常也会多一次“决定是否调用工具”的模型调用；若它调用 `read_document`，还会多一次工具回执和上下文增长。合格结论：

> 在该任务上，固定流程已满足质量底线；Agent 未带来额外质量收益，且有更多调用/失败点，因此不采用 Agent。

这不是“Agent 不好”，而是“这个任务不需要”。不要把“不采用”写成“未完成”。

## 4. 三种失败的答案

### 4.1 未允许的工具

命令中 `--allowed-tools calculator`，模型请求 `read_document`。

预期：

```text
status = permission-denied
first_failure.stage = tool
detail.tool = read_document
detail.allowed_tools = ["calculator"]
tool_receipts = []
```

说明：请求在参数/白名单校验阶段被拒绝，工具没有执行，因此没有回执。`permission-denied` 在这里表示“工具不被允许”，不是文档读者权限；两者都在程序侧，但原因不同。

### 4.2 坏参数

模型请求：

```json
{"action":"tool","tool":"calculator","arguments":{"a":4.2,"b":86400}}
```

预期：

```text
status = invalid-response
first_failure.stage = tool
reason = calculator arguments must be exactly ['expression']
tool_receipts = []
```

不能自动把 `a`/`b` 转成表达式执行；这会绕过 schema 和审计。

### 4.3 预算耗尽

- `--max-steps 1 --max-tool-calls 0`，模型请求工具：`budget-exhausted`；
- `--max-steps 2 --max-tool-calls 1`，模型先调用一次工具、再请求第二次工具：第二次触发 `budget-exhausted`；
- `--max-steps 4 --max-tool-calls 2`，模型连续调用两次后仍请求工具：`budget-exhausted`；
- 步数用完但模型没有给出最终回答：`budget-exhausted`。

合格行为：保留已成功回执，但**不把中间结果拼成最终答案**；报告说明未完成。

### 4.4 权限边界

学生请求 `read_document(review-budget)`：

```text
工具回执 status=failed, error=permission-denied
report status=permission-denied（或 tool-failed，取决于失败位置）
正文不出现
```

教师请求同一文档：

```text
工具回执 status=succeeded
result.text 最多 1500 字符，truncated=true/false
仍需 source citation 或人工核对才能支持 claim
```

`read_document` 成功只证明读取动作；不能把回执当成逐字引用证明。

## 5. 停止条件写法

一个可用的停止条件：

```text
允许工具：calculator（或 calculator,read_document）
最大模型决策步数：4（含最终回答）
最大工具调用：2
参数：完全匹配 schema，不自动转换
权限：每次调用按当前 reader 检查
失败：任一步失败立即停止，不自动重试
输出格式：严格 JSON；repair_attempts 在运行前固定
预算：超步数/工具数/提示 token 即停止并报告
未知：超时或状态不明时不重复执行，先查回执/状态
```

为什么这些是硬边界：

- 防止模型无限循环；
- 防止一次失败后继续用错误结果；
- 让成本可预测；
- 让审计能复原每一步；
- 让“未完成”成为可报告状态，而不是伪造成功。

## 6. 评分表

| 项目 | 合格 | 不合格 |
| --- | --- | --- |
| 对照 | 同任务、同判据，固定 vs Agent | 换题后比较 |
| 工具证据 | 成功回执 + claim 引用 | 模型说调用就算 |
| 失败 | 越权/坏参数/预算各有状态 | 自动重试到通过 |
| 权限 | 学生无正文，教师可读 | 改 readers 绕过 |
| 结论 | 采用/不采用都有理由 | 认为 Agent 必然更好 |
| 停止 | 步数/调用/失败/提示预算清楚 | 无上限、静默重试 |
| 引用 | 区分 source quote 与 tool receipt | 把回执当逐字引用 |

没有实际报告时，以上只能作为检查表；不能写成“已通过”。
