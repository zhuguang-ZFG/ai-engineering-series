# C16 答案与核对依据

## 1. 固定流程 vs Agent

| 项目 | 固定流程 | 有限 Agent |
| --- | --- | --- |
| 下一步谁决定 | 程序写死 | 模型在预算内选择 |
| 工具数量 | 固定 | 白名单内可选 |
| 失败路径 | 程序分支 | 模型选择 + 程序校验 |
| 可预测性 | 高 | 较低，需要步数/调用上限 |
| 证据 | 回执仍必须保留 | 回执仍必须保留 |

固定流程也可以真实执行；Agent 不等于“更高级”。如果任务步骤固定、输入简单，固定流程更易测试和审计。Agent 适合需要根据中间结果选择下一步的任务，但必须有终止条件。

## 2. 四种失败

| 失败 | 请求 | 期望 | 不应出现 |
| --- | --- | --- | --- |
| 坏参数/坏表达式 | `{"expression": 3}` 或多余字段；`{"expression":"3+"}` | 前者 `invalid-response`、未执行；后者 `tool-failed`，回执错误 `invalid-expression` | 把非字符串自动转成表达式，或把语法错误当成功 |
| 代码/调用/字符串字面量 | `{"expression":"__import__('os')"}`；`{"expression":"'a'+'b'"}` | 回执失败 `unsupported-expression` / `unsupported-literal`，最终 `tool-failed` | 执行 Python 代码或拼接字符串 |
| 除零 | `{"expression":"1/0"}` | 回执失败 `division-by-zero` | `Infinity`、`NaN`、成功摘要 |
| 未知工具 | 模型请求 `send_email`；或 CLI 传 `--allowed-tools send_email` | 模型请求：`permission-denied`、未执行；CLI：参数解析报 `unknown tools`、退出码 2，未生成报告 | 猜测并执行，或把内部 `unknown-tool` 分支当成 CLI 输出 |
| 无权限读取 | 无权限 `doc_id` | `permission-denied`，无正文 | 先读后删引用 |

注意：`"3+4"` 是合法表达式，会返回 `7`，不是坏参数。失败发生在 `validate_tool_request`/`calculate` 时，回执或 `first_failure` 必须保留具体错误码；不能把“校验拒绝”和“执行失败”混成同一状态。

## 3. 预算耗尽

`--max-tool-calls 1` 而任务需要两次调用时，实际报告的状态是 `budget-exhausted`，`diagnostics.first_failure.stage` 为 `tool`，已成功的第一次回执保留，`answer` 为 `null`、`claims` 为空（下面为字段示意，`step` 等数值以实际报告为准）：

```json
{
  "status": "budget-exhausted",
  "answer": null,
  "claims": [],
  "tool_receipts": [
    {
      "receipt_id": "tool-1",
      "tool": "calculator",
      "status": "succeeded",
      "arguments": {"expression": "3*14"},
      "result": 42
    }
  ],
  "diagnostics": {
    "first_failure": {
      "status": "budget-exhausted",
      "stage": "tool",
      "detail": {"max_tool_calls": 1}
    }
  }
}
```

关键是：报告说明“未完成”，不把第一次调用的结果拼成最终答案。预算上限是安全边界，不是建议值。

## 4. 参数 schema

`calculator` 的实际参数只有一个字段：

```json
{
  "name": "calculator",
  "description": "对单个数值算术表达式字符串求值；只允许数字、括号、一元 +/- 和 + - * / // % **",
  "parameters": {
    "type": "object",
    "required": ["expression"],
    "additionalProperties": false,
    "properties": {
      "expression": {
        "type": "string",
        "minLength": 1,
        "maxLength": 200,
        "description": "单行；数字字面量绝对值 <= 1e12；指数绝对值 <= 64；结果绝对值 <= 1e12；禁止名字、函数调用、属性访问、字符串/容器字面量和其他运算符"
      }
    }
  }
}
```

错误码按阶段区分：请求形状不对（非字符串、多余字段、工具不在白名单）在 `validate_tool_request` 阶段返回 `invalid-response` / `permission-denied`，不执行；表达式进入 `calculate()` 后可能返回 `invalid-expression`（语法错误）、`unsupported-expression`（调用/名字/属性等）、`unsupported-literal`（字符串、布尔等非数值常量）、`unsupported-operation`（位运算、比较等非白名单运算符）、`division-by-zero`、`exponent-limit`、`overflow`。执行失败会写入失败回执并让最终状态为 `tool-failed`。

这里接受的是**受限数值算术表达式字符串**，不是任意代码：程序先 `ast.parse(..., mode="eval")`，再递归只解释数值常量、一元正负号和白名单二元运算，绝不调用 `eval`、不解析名字或调用。这样既保留了“`3*14`”这类自然输入，又把可执行面限制在数值运算；字符串字面量、函数调用和任意语句在 AST 白名单阶段就被拒绝。长度、指数和结果上限用于避免一次调用消耗过多资源。

## 5. 写入工具设计

只设计，不执行。示例 `create_note`：

- **确认**：应用向用户显示“将写入哪个文件、内容摘要、覆盖/新建”，用户明确确认后才执行；
- **权限**：调用者必须有写权限，路径限制在工作区；
- **幂等键**：客户端生成 `request_id`，重复请求返回同一结果；
- **回执**：记录文件路径、哈希、时间、执行状态；
- **回滚**：保留旧文件备份，失败/取消时恢复；
- **未知**：超时后按 `request_id` 查询，不能重试到重复写入。

## 核对清单

- [ ] 工具名和参数先校验后执行；
- [ ] 失败/超时/未知不产生成功结果；
- [ ] 调用次数和步数有上限；
- [ ] 工具回执与主张绑定；`answer` 只列已验证 claims，来源 claim 的 `text` 是其 `quote` 的逐字连续子串；
- [ ] 没有 `eval`/任意代码执行；
- [ ] 写操作有人工确认、权限、幂等和回滚设计；
- [ ] 没有把固定流程称为 Agent，也没有把模型“说要调用”当成已执行。
