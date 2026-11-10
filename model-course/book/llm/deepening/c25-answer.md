# C25 答案与核算：何时适配参数，何时不该训练

## 1. LoRA 参数账本

默认 `C=64`、`V=50`、2 层、`rank r=4`、`alpha=8`，缩放 `alpha/r=2.0`。每个 block：

```text
qkv: A [4,64] + B [192,4] = 256 + 768 = 1,024
proj: A [4,64] + B [64,4] = 256 + 256 = 512
fc1: A [4,64] + B [128,4] = 256 + 512 = 768
fc2: A [4,128] + B [64,4] = 512 + 256 = 768
每层合计 = 3,072
2 层 = 6,144
head: A [4,64] + B [50,4] = 256 + 200 = 456
LoRA 总计 = 6,600
```

底座 69,760 个参数冻结，包装后：

```text
total      = 69,760 + 6,600 = 76,360
trainable  = 6,600
frozen     = 69,760
```

全量 SFT 的可训练参数是 69,760，冻结为 0；它更新的是底座本身。LoRA 的 `base_checksum` 应全程不变，适配器哈希应变化。

变体：

- `rank=8`：每个 block 的 A/B 参数量翻倍，`6,144×2=12,288`，head `912`，总计 **13,200**；包装后总参数 82,960，冻结仍 69,760。
- 只包 `qkv` + `proj` + `head`：每层 `1,024+512=1,536`，两层 3,072，加 head 456，总计 **3,528**；包装后总参数 73,288。
- 只包 `qkv` + `proj`，不包 head：**3,072**；总参数 72,832。
- 只包 `qkv`：每层 1,024，两层 2,048；不包 head 时总参数 71,808，包 head 时 72,264。
- 头数从 4 改 8：QKV 总参数量仍由 `C` 决定，不改变 LoRA 的 qkv 参数账本；改变的是每个头的 `dh`。

## 2. SFT 的损失掩码

以 `sft-small-00` 为例：

```text
full:    [BOS, say, the, small, boat, ., the, small, boat, floats, ., EOS]
prompt:  [say, the, small, boat, .]                 长度 5
response:[the, small, boat, floats, ., EOS]         长度 6
inputs:  full[:-1]                                  长度 11
targets: full[1:] 但提示部分置 -100
```

`response_start = 1 + len(prompt) = 6`。输入位置 `0..4` 的目标是 `-100`；位置 `5` 的目标是 `full[6] = "the"`，这是回答的第一个 token；位置 `10` 的目标是 `EOS`。所以回答段（含 EOS）贡献 6 个目标 token，提示段贡献 0 个。

如果提示长度变成 6：

```text
response_start = 1 + 6 = 7
第一个有损失的目标位置 = 6（它对应 full[7]，即回答首 token）
```

提示仍然作为 `inputs` 的前缀进入模型，只是不计算“预测提示”的损失。若把提示也设为正常目标，模型会学习复述指令，损失数字可能更低，但目标变了。

## 3. 全量 SFT 与 LoRA 的对照表

运行 `adapt --method both` 后，用自己的输出填表，不要照抄示意值：

| 项目 | full SFT | LoRA |
| --- | --- | --- |
| `parameters.trainable` | 69,760 | 6,600 |
| 底座是否冻结 | 否 | 是 |
| `base_updated` | true | false |
| `base_frozen` | false | true |
| 底座哈希 | 变化 | 不变 |
| 适配器哈希 | 不存在（或空） | 变化（`lora_changed=true`） |
| `base_grads_all_none` | 通常 false | true |
| `reload.bitwise_equal` | 应为 true | 应为 true |
| `delta_val` / `delta_test` | 以本次输出为准 | 以本次输出为准 |

工程事实：参数量、冻结、哈希、重载一致性。数据测量：`losses.before/after` 与 `delta_val/delta_test`。业务判断：是否改善目标错误、是否满足成本/延迟/许可；这些不能由训练损失替代。

`base_grads_all_none=true` 的含义是底座参数没有 `.grad`，不是“梯度刚好为 0”。LoRA 的底座 `requires_grad=False`，也没有被放进 AdamW 的参数列表；这两条要同时成立。

## 4. 比较时不要预设赢家

LoRA 可训练参数少，可能更稳、更省显存，也可能容量不足；全量 SFT 容量大，也可能过拟合或遗忘。rank、alpha、目标层、学习率、步数、数据量都会影响结果。一个公平对照至少要做到：

- 同一底座 checkpoint；
- 同一 SFT 训练/验证/留出组；
- 同一种子、同一步数、同一批大小（或明确说明差异）；
- 相同解码设置；
- 报告重载与冻结检查，而不只报告损失；
- 保留失败记录。

即使 LoRA 的留出损失更低，也不能直接说“LoRA 更好”；只能说“在这个玩具数据、这组超参数和这些评测题上，LoRA 的验证/留出损失是 X”。反之亦然。

## 5. 什么时候不该训练

- 需求只是让模型看到新资料：先比较提示、RAG、工具调用。
- 评测未冻结：先做 C18 的验证集和判据。
- 数据许可不清：不要训练。
- 错误来自检索/工具/权限：训练参数不会修“没取到资料”。
- 成本高于收益：适配要数据、训练、评测、部署和回滚。
- 需要逐条引用和最新事实：不要用参数记忆替代检索与引用。

SFT 与偏好训练也不同：SFT 用示范告诉模型“这样回答”，偏好训练用成对比较告诉模型“更偏好哪一种”。本课只做 SFT/LoRA，不执行偏好优化。

## 6. 失败诊断

| 现象 | 检查 |
| --- | --- |
| 训练损失低但只会复述提示 | 提示段是否误设为正常目标 |
| 验证损失虚低 | SFT group 是否跨 split；是否用评测题训练 |
| `unsupported LoRA target(s)` | checkpoint 的目标名与载入解析是否一致；本实现同时接受相对名和 `blocks.<i>.<name>` 全路径 |
| `head is already wrapped` | 同一模型是否被 `apply_lora` 包了两次 |
| 从已适配 checkpoint 再 adapt | 是否应先回到 `base.pt`；本课会拒绝叠加 |
| 底座哈希变化但声称冻结 | 优化器是否误收了底座参数；是否在冻结前就建了优化器 |
| `lora_changed=false` | 适配器是否可训练、学习率是否为 0、是否根本没更新 |
| 只保存 adapter 后载入失败 | 是否先重建 LoRA 包装；本课保存完整 state dict 与元数据 |
| rank=0/负数 | 配置错误，直接拒绝 |
| 训练/留出都变差 | 学习率、步数、数据量或目标设计问题；做单变量对照 |

## 7. 项目检查

`adapt --method both` 的 `comparison` 下每个方法都有 `parameters`、`checks`、`losses`、`sample`、`seconds`。先看硬检查（冻结/重载/哈希），再看损失，再看生成样例；不要用 `sample.generated_text` 的个别句子替代留出评测。

本课的 `sft.jsonl` 是作者编写的示范，不是教师模型输出；因此这里的“适配”不能当成蒸馏证据。C26 会单独讲教师信号、KL/T² 和错误继承。
