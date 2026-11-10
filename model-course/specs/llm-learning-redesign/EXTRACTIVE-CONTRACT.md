# 纯抽取契约：已实现范围与剩余验收

更新：2026-11-09。`--claim-mode extract` 为可选模式，仅支持 `--mode fixed`，默认仍为 `copy`。精确位置扩展 `source-extract/2` 已实现；本批使用缓存的 0.5B 模型做独立八题对照，原计划 1.5B 复测因资源压力未完成，详见[迭代03](IMPLEMENTATION-03.md)。历史 1.5B 实测见 [BASELINE.md](../../book/llm/examples/assistant/BASELINE.md)，不能把跨模型分数差归因于抽取模式。K3 仍未通过。

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
- `start/end` 表示整个 chunk；`quote_start/quote_end` 表示引文在同一文档中的半开范围。坐标按 UTF-8 去 BOM、CRLF/CR 统一为 LF 后的 Unicode 码点计数，不是原文件字节或 UTF-16 单元；sha256 仍绑定原文件字节。
- 连续空白在匹配时折叠成一个空格，返回位置映射到折叠前的文档字符；不做大小写、标点或 Unicode 归一化。同一 chunk 中重复匹配取第一次，不能由此断言模型选了哪一次重复。
- JSON 的 `config.claim_contract=source-extract/2` 标记附加合同，Markdown 也显示精确范围。默认 copy/agent 和旧报告不新增该标记/字段，旧 start/end 仍是 chunk 范围。
- agent/extract 组合在资料读取和模型调用前返回 `invalid-request`；模型不允许提交偏移或新主张，位置由程序计算。

正文 [C13](../../book/llm/lessons/c13.md)、[C15](../../book/llm/lessons/c15.md)、[C17](../../book/llm/lessons/c17.md) 和 [助手说明](../../book/llm/examples/assistant/README.md) 已说明模式与边界。新增模式没有删除旧报告字段，也没有将自由改写设为默认。

## 验收台账

| 要求 | 状态与证据 |
| --- | --- |
| 不接受相反主张借真实 quote 通过 | copy 保留连续摘录校验，extract 从核验原文生成主张；现有实现/反例记录见 IMPLEMENTATION |
| 正确/错误 quote、冲突、无证据分支 | 运行时有独立分支；完整 K3 的语义适用性和首次模型输出仍须逐例核验 |
| 固定问题集对照 | 本批 0.5B 独立对照：完整八题 copy 4/8、extract 4/8；fixed 七题子集分别 4/7、4/7；八题不删题、不改变 agent 的原期望，完整首次输出见 [EVALUATION-03](../../book/llm/examples/assistant/EVALUATION-03.md) |
| 文档与默认兼容 | 本批已对齐 C13/C15/C17；默认 copy、agent 的行为保留 |
| 精确原文位置 | 已实现 source-extract/2；14 项针对性测试覆盖字符映射、重复位置、解码/原文件哈希、兼容和失败边界；实际 CLI 拒绝不支持组合 |
| 完整八题和版本绑定 | 已完成两轮 0.5B 独立实跑，绑定源码、原清单、文档及模型七个文件的 SHA-256；1.5B 的两次未完成尝试另记，新版本复测仍待资源，不补造成绩。详见迭代03及 comparison/model 证据 |

不新增自由总结模式，也不扩展 extract 的 agent 支持。它们不是当前 fixed 抽取合同的必需项。完成位置合同和全清单比较只关闭该技术子项，K3 的回答质量和原八题硬判据仍须独立满足。
