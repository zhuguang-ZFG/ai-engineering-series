# 纯抽取契约：已实现范围与剩余验收

更新：2026-11-08。`--claim-mode extract` 已实现为可选模式，仅支持 `--mode fixed`，默认仍为 `copy`。本文件将原提案与实际实现分开；K3 仍未通过，实测见 [BASELINE.md](../../book/llm/examples/assistant/BASELINE.md)。

## 为什么保留严格引用

真实 1.5B 模型曾为 `normal-wind` 找到含 `2026-10-03` 和 `4.2 米每秒` 的原文，却把主张改写成一句新话，因而被 copy 的连续摘录规则拒绝。copy 要求主张是其 quote 的连续子串，并非主张必须等于整段 quote。真实 quote 本身不能证明任意转述成立，例如“地点尚未确定”不能支持“地点已确定为图书馆”。

原八题基线 4/8；只增强输出契约的提示词对照仍 4/8 且开销上升，已拒绝。抽取模式改由模型选择原文、程序构造可核对主张，不能解决选择无关原文、旧版本或漏掉冲突。

## 当前实际合同

模型返回：

```json
{"status":"answered","claims":[{"chunk_id":"...","quote":"..."}]}
```

- `status` 接受 `answered`、`insufficient`、`conflict`，可附 `reason`；证据不足时 claims 为空。当前校验器允许省略 reason，此时使用“资料不足，无法回答。”，不能把它当作模型给出了失败原因。
- 每条 claim 仅含 `chunk_id`、`quote`；规范化后的 quote 长度为 2–300 字符，须在相应规范化 chunk 中连续出现，不能拼接不连续段落。
- 输出报告保留 `claims[].text` 和 citations 结构。程序移除显示主张开头的 Markdown 标题符号，引用 quote 保留；answer 按顺序拼接核验后的主张。
- 冲突要求至少两条主张、来自不同文档；是否确为当前问题的冲突仍须评测。
- `start/end` 表示 chunk 在原文的位置，**不是 quote 的精确起止位置**。
- agent/extract 组合返回 `invalid-request`；copy/agent 的原合同保留。

正文 [C13](../../book/llm/lessons/c13.md)、[C15](../../book/llm/lessons/c15.md)、[C17](../../book/llm/lessons/c17.md) 和 [助手说明](../../book/llm/examples/assistant/README.md) 已说明模式与边界。新增模式没有删除旧报告字段，也没有将自由改写设为默认。

## 验收台账

| 要求 | 状态与证据 |
| --- | --- |
| 不接受相反主张借真实 quote 通过 | copy 保留连续摘录校验，extract 从核验原文生成主张；现有实现/反例记录见 IMPLEMENTATION |
| 正确/错误 quote、冲突、无证据分支 | 运行时有独立分支；完整 K3 的语义适用性和首次模型输出仍须逐例核验 |
| 固定问题集对照 | 七个 fixed 用例 copy 4/7、extract 5/7，模型调用均三次；这是子集，不能当完整八题结果 |
| 文档与默认兼容 | 本批已对齐 C13/C15/C17；默认 copy、agent 的行为保留 |
| 精确原文位置 | 尚未实现 `quote_start/quote_end`；需定义规范化到原字符的位置映射、重复引用定位和版本兼容后补充验证 |
| 完整八题和版本绑定 | 待完成包括 agent 不支持路径的完整比较，分别记录清单/源码/模型哈希、token 与延迟；保留旧八题清单，不改题求通过 |

不新增自由总结模式。若今后引入，必须另有人工核验或可检验的事实支持方法；它不是当前抽取主线的必需项。精确位置及全清单比较完成前，这份契约不能整体标为完成。
