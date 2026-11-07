# C24 答案与核算：从零组装最小 decoder

## 1. 因果掩码

`T=3` 时允许的位置是“自己及左边”，禁止右侧：

```text
M = [[ 0, -inf, -inf],
     [ 0,   0, -inf],
     [ 0,   0,   0]]
```

第 0 行只能看位置 0；第 1 行能看 0、1；第 2 行能看 0、1、2。代码里 `torch.triu(..., diagonal=1)` 只取严格上三角，所以对角线保留。对每一行做 softmax 时，`-inf` 的位置 `exp(-inf)=0`，权重和为 1；未来位置不会进入分母。

若先 softmax 再乘掩码，分母已经包含了未来项，归一化后的权重不再是“只在允许位置上的分布”。这是常见错误，`future_invisibility` 会暴露它。

## 2. 单头手算

`dh=2`，`q=[1,0]`，`k1=[1,0]`，`k2=[0,1]`，缩放 `1/sqrt(2)≈0.7071`：

```text
score1 = 0.7071 × (1×1 + 0×0) = 0.7071
score2 = 0.7071 × (1×0 + 0×1) = 0
```

softmax：

```text
exp(0.7071) ≈ 2.0281
exp(0)      = 1
sum         ≈ 3.0281
w1 ≈ 0.6698
w2 ≈ 0.3302
```

`v1=[10,0]`、`v2=[0,20]`，输出：

```text
out = 0.6698 × [10,0] + 0.3302 × [0,20]
    ≈ [6.698, 6.604]
```

这个例子只核对公式；真实模型有 4 个头，每个头 16 维，权重由训练得到。

## 3. 目标错位

```text
full:   [BOS, the, small, kite, shines, ., EOS]
inputs: [BOS, the, small, kite, shines, .]
target: [the, small, kite, shines, ., EOS]
```

`inputs[1:]` 是 `[the, small, kite, shines, .]`，`target[:-1]` 也是同一串，所以 `aligned=true`。第 0 个位置输入 `BOS` 预测 `the`；最后一个输入位置 `.` 预测 `EOS`。

如果把 `target` 写成 `inputs`，模型会被训练成“看到当前 token 就复制它”，训练损失可能下降，但生成时容易重复，且 `target_shift.aligned` 会失败。

## 4. 参数量

默认 `C=64`、`V=50`、2 层、`d_ff=128`，tied head：

```text
token embedding: 50×64 = 3,200
每层 LN×2:       2×2×64 = 256
每层 qkv:        64×192 = 12,288
每层 proj:       64×64 = 4,096
每层 FFN:        (64×128+128) + (128×64+64) = 8,320 + 8,256 = 16,576
每层合计:        256 + 12,288 + 4,096 + 16,576 = 33,216
2 层:            66,432
最终 LN:         128
输出头:          与 token embedding 共享，0 额外
总计:            3,200 + 66,432 + 128 = 69,760
```

变体：

- 3 层：`69,760 + 33,216 = 102,976`。
- 输出头解绑：多 `64×50=3,200`，即 `72,960`。
- `V=60`：token embedding 变成 `60×64=3,840`，总计 `70,400`（tied head 不额外加）。
- `n_heads=8`：QKV 的总宽度仍是 `3C`，参数总量不变（仍是 `69,760`），只是每个头 `dh=8`、分数形状仍 `[B,H,T,T]`。前提是 `C` 能被 8 整除。
- 把 `d_ff` 改成 256：每层 FFN 变为 `(64×256+256)+(256×64+64)=16,640+16,448=33,088`，每层多 16,512，两层多 33,024，总计 `102,784`。

`inspect` 打印的是实际模型计数；手算应和它一致，不一致就先查 bias、tied head、层数或 `d_ff`。

## 5. 去掉掩码会怎样

把 `scores.masked_fill(...)` 注释掉后，`future_invisibility_check` 会看到：只改后缀时，前 `prefix_len=4` 个位置的 logits 也变了，`bitwise_equal=false`，`max_abs_diff` 非零。原因不是训练不好，而是前缀位置的注意力读到了未来 token。

修复顺序：先恢复掩码，再重跑检查；不要用调学习率、增加层数或换数据来“压”这个失败。因果性是结构契约。

如果检查仍然显示 `suffix_changed=false`，说明你改的后缀没有影响最后一个位置（例如改动落在被完全 mask 的位置，或模型输出饱和）；换一条更长、更靠右的改动再试，避免检查本身没有区分力。

## 6. 生成与重载

- `temperature=0`：每步 argmax，结果由当前权重唯一决定；同一个 checkpoint、同一个 prompt 应得到同一串 token。
- `temperature>0`：按概率采样；同 seed 可重放，不同 seed 结果可能不同。`top-k` 只保留前 `k` 个候选，仍不是事实校验。
- `positions_used` 记录实际用了多少位置；到 `max_len=48` 会停止。`hit_eos=true` 表示自然结束，不代表内容正确。
- 重载：`torch.save` 保存 `state_dict` + 配置 + 词表；`torch.load(weights_only=True)` 后 `load_state_dict(strict=True)`。对同一输入比较 logits，`bitwise_equal=true` 才说明保存/载入路径一致。若不一致，先查词表顺序和配置，再查 LoRA 包装。

## 7. 失败诊断

| 现象 | 可能原因 | 先做 |
| --- | --- | --- |
| 训练损失降，生成重复 | 目标错位成复制 | 看 `target_shift.aligned` |
| 前缀输出随未来变化 | 掩码缺失/先 softmax 后掩码 | `future_invisibility` |
| 留出损失异常低 | group 跨 split 泄漏 | `corpus.splits` 与 group 检查 |
| `F.cross_entropy` 目标数不对 | 补位没设 `-100` | 打印 `(targets != -100).sum()` |
| 载入键不匹配 | 配置/结构/词表不一致 | 对比 `config` 与 `state_dict` 键 |
| 序列超长报错 | 超过 `max_len` | 缩短序列或增大 `max_len` 并重训 |

## 8. 项目检查

运行 `train.py inspect` 时应能看到：

- `architecture.positions` 说明固定正弦、`max_len=48`；
- `parameters.total` 与手算一致；
- `checks.future_invisibility.bitwise_equal` 为真；
- 带 checkpoint 时 `sample` 有实际生成字段。

运行 `train.py train` 后，`checks.reload` 应给出保存/重载比较；`losses.val` 与 `losses.test` 是留出组测量，不是通用能力。与 X05 的 bigram 对照时，记住 bigram 没有注意力、位置和 FFN，不能用同一损失数字直接排名。
