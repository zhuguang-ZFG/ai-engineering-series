# C13 答案与核对依据

本答案不提供“标准模型输出”，因为输出必须来自你的模型和输入。它给出可核对的行为、字段和失败处理。

## 1. 一次真实 run 的最小证据

保存 `out/c13-first.json` 后，至少检查：

```json
{
  "status": "answered",
  "question": "设备手册里，风速传感器多久校准一次？",
  "reader": "student",
  "claims": [
    {
      "text": "风速传感器建议每 180 天校准一次。",
      "citations": [
        {
          "kind": "source",
          "chunk_id": "equipment-guide@<sha256 前 12 位>#000",
          "doc_id": "equipment-guide",
          "quote": "风速传感器建议每 180 天校准一次。",
          "version": "1.0.0",
          "sha256": "…"
        }
      ]
    }
  ],
  "diagnostics": {"first_raw_response": "...", "first_failure": null},
  "usage": {"calls": 1, "prompt_tokens": 612, "completion_tokens": 48, "latency_ms": 1800.0, "cost": null}
}
```

字段关系（数值仅示意，不是一次成功运行的证明）：`claim.text` 必须是 `quote` 的逐字连续子串，`quote` 必须是所引 chunk 的逐字连续片段；`answer` 只能由已核验 claim 原文组成，不能加额外句子。`version`/`sha256` 对应清单里的当前文档；`usage` 反映实际调用。`tokens` 或 `cost` 未知时写 `null`，不要填 0 冒充“免费”。

回查方法：在清单找到 `doc_id` 的 `path`，用编辑器打开对应版本，搜索 `quote`。若搜不到，检查是否换了版本、是否跨了切块边界、是否被 Markdown 渲染改变了空白。空白差异可以规范化后比较，但不能把改写的句子当成原文。

## 2. 材料未覆盖

问题：“今天食堂几点开门？”示例文档没有食堂。预期之一：

```json
{"status": "insufficient-evidence", "claims": [], "diagnostics": {"first_failure": "no-supporting-chunk"}}
```

预期是 `insufficient-evidence`，`claims` 为空。若模型硬给“食堂 7:00 开门”并挂设备手册引用，会因 `quote` 不在原文或 `claim.text` 不是 `quote` 的逐字连续子串而 `citation-failed`；不能靠“材料未说明”这句改写绕过引用校验。判定标准是：**有没有把常识写成材料事实**，以及 answer 是否只由已验证 claim 原文组成。

## 3. 无权限读者

把 `--reader` 换成无权限身份后：

- 若文档不可见，`inspect read` 不列出它；
- 若问题仍可回答，只能基于可见材料；
- 若必须用无权限材料，`status` 应为 `unauthorized` 或明确的无权限错误。

不要为了让命令成功而删除 `readers` 字段。正确做法是取得授权、换用公开文档，或在报告中记录“无权限，未读取正文”。日志和报告中不应出现无权正文。

## 4. 模型不存在

```bash
python book/llm/examples/assistant/assistant.py run \
  --docs book/llm/examples/assistant/documents.json \
  --reader student \
  --question "设备手册里，风速传感器多久校准一次？" \
  --model "/absolute/path/that/does-not-exist" \
  --json out/c13-model-missing.json
```

预期：

- `status: "model-unavailable"`（或等价错误）；
- `diagnostics.first_failure` 包含路径/加载错误；
- 非零退出码（以 CLI 实际行为为准）；
- 不生成 `answered` 报告，不返回示例答案。

恢复正确路径后重跑，比较两次 `usage`：第二次应有真实调用记录（calls/latency/tokens 至少一项变化）。如果两次完全一样，可能是读到了旧输出文件或程序缓存。

## 5. 为什么保留 `first_raw_response`

整理后的 `claims` 是解析和校验后的结果，可能掩盖：

- 模型返回了空内容或拒绝回答；
- 返回了两段互相矛盾的话，只保留了一段；
- JSON 字段被修复脚本改写；
- 引用是模型编的，解析器没有发现。

保留首次原始响应，才能区分“模型错”“解析错”“校验错”。它不是给读者看的最终答案，而是排错证据；敏感内容要按权限处理，不能因为“诊断”就绕过隐私。

## 核对清单

- [ ] 真实模型/授权 API 调用，输入变化会改变输出；
- [ ] `--reader` 生效，无权限文档未进入上下文；
- [ ] 每条主张有 `quote`/`chunk_id`/版本或工具回执；
- [ ] `status` 能区分无证据、冲突、越权、模型不可用；
- [ ] `first_raw_response`/`first_failure` 保留；
- [ ] `usage` 不是伪造的固定值，费用未知为 `null`；
- [ ] 资源/许可记录写清楚，没有把“未运行”写成“已验证”。

本章不提供模型权重或 API 密钥；缺少资源时，以上检查只能记录为待验。
