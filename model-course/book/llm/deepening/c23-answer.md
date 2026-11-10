# C23 答案与核算：从数组走到自动微分

## 1. 手算梯度并与 autograd 对照

取 `w=1.5`、`x=-2`、`b=0.5`、`y=1`：

```text
pred = 1.5 × (-2) + 0.5 = -2.5
error = pred - y = -3.5
L = (-3.5)^2 = 12.25
∂L/∂w = 2 × (pred - y) × x = 2 × (-3.5) × (-2) = 14
∂L/∂b = 2 × (pred - y) = 2 × (-3.5) = -7
```

学习率 `0.1` 时：

```text
w_new = 1.5 - 0.1 × 14 = 0.1
b_new = 0.5 - 0.1 × (-7) = 1.2
pred_new = 0.1 × (-2) + 1.2 = 1.0
L_new = (1.0 - 1)^2 = 0
```

这组数一步到零，是因为它是二次函数且步长恰好；换一组数或换学习率就不保证。不要把它记成“梯度下降一步一定到最优”。

对应代码：

```python
import torch

w = torch.tensor(1.5, requires_grad=True)
b = torch.tensor(0.5, requires_grad=True)
x = torch.tensor(-2.0)
y = torch.tensor(1.0)

pred = w * x + b
loss = (pred - y) ** 2
loss.backward()
print(w.grad, b.grad)   # tensor(14.) tensor(-7.)
```

如果希望在**新的前向图**里冻结 `w`：

```python
w.requires_grad_(False)
w.grad = None
b.grad = None
pred = w * x + b
loss = (pred - y) ** 2
loss.backward()
print(w.grad, b.grad)   # None tensor(-7.)
```

冻结不会自动删除上一次的 `w.grad`，所以这里先清掉历史梯度，再做新的前向与反向。此后 `w.grad is None` 表示这次没有为 `w` 累积梯度，不是“梯度等于 0”；`w` 仍参与前向计算，`b` 也仍能得到梯度。要冻结就在下一次前向前设置，并重新建图。

## 2. 广播

```python
a = torch.tensor([[1.0], [2.0], [3.0]])       # [3, 1]
b = torch.tensor([[10.0, 20.0, 30.0, 40.0]])  # [1, 4]
c = a + b                                     # [3, 4]
```

`c[2,3] = a[2,0] + b[0,3] = 3 + 40 = 43`。最右维 `1` 与 `4` 对齐后扩展，`3` 与 `1` 也扩展；没有真的把 3 行复制成 12 行存储。

`a = torch.zeros(3, 2)` 与 `b = torch.zeros(3, 4)` 不能广播：最右维 2 与 4 既不等也没有 1，报错发生在最后一维。若你先看到的是更早的维度错误，说明前面还有别的形状问题；从最右维往左查。

## 3. 模型里的形状链

| 步骤 | 形状 | 说明 |
| --- | --- | --- |
| `idx` | `[B, T]` | token 编号 |
| token embedding | `[B, T, C]` | 查表得到向量 |
| 位置编码 | `[T, C]` | 广播加到批次 |
| `qkv` 线性层 | `[B, T, 3C]` | 一次算 Q/K/V |
| 拆头 | `[B, H, T, dh]` | `C=H×dh` |
| 分数 | `[B, H, T, T]` | 缩放点积 |
| 掩码 | `[T, T]` | 布尔，广播到分数 |
| 加权 value | `[B, H, T, dh]` | 拼回 `[B, T, C]` |
| FFN 中间 | `[B, T, d_ff]` | 逐位置 |
| logits | `[B, T, V]` | 与目标逐位置交叉熵 |

`x + sublayer(x)` 能成立，前提是子层输出仍是 `[B, T, C]`。如果残差报形状错误，先找哪个子层改了 `T` 或 `C`，不要先改残差。

## 4. 保存/载入

本课保存：

```text
format + config + vocab + state_dict + adaptation + meta
```

载入时：

```python
payload = torch.load(path, map_location="cpu", weights_only=True)
config = DecoderConfig(**payload["config"])
tokenizer = WordTokenizer(payload["vocab"])
model = TinyDecoder(config)
model.load_state_dict(payload["state_dict"], strict=True)
```

`strict=True` 会检查键是否完全匹配。载入后对同一输入比较 logits；`bitwise_equal=true` 说明这条路径没有丢参数或换词表顺序。若只保存 `model.state_dict()` 而不保存配置和词表，另一台机器无法仅凭权重知道 `C`、层数、头数和 token 顺序；这就是“保存模型对象”不如保存可重建材料的理由。

`weights_only=True` 限制反序列化可引用的对象；本课 payload 只有字典、列表、字符串、数字和 tensor。不要为了打开陌生文件改成 `False`。

## 5. 失败诊断

| 现象 | 首先检查 |
| --- | --- |
| 连续两步后参数方向不对 | 是否每步 `optimizer.zero_grad(set_to_none=True)` |
| `w.grad is None` | `requires_grad` 是否为 `False`，或是否在 `torch.no_grad()` 里 |
| 形状能跑但注意力每行一样 | 掩码形状是否错误广播；是否先 softmax 后掩码 |
| 载入后 logits 不一致 | 词表顺序、配置、LoRA 包装、保存时机 |
| 序列超长静默变短 | 代码应显式拒绝；检查 `max_len` 与截断逻辑 |
| 保存文件打不开 | 是否保存了整模块而不是 `state_dict`；是否用了不匹配的类 |

## 6. 项目检查

`inspect` 的 `parameters` 表来自 `count_parameters`：`model.parameters()` 会去重，所以 tied embedding/head 只算一次。固定正弦位置没有参数；`architecture` 中的 `positions` 说明它是 `max_len` 长度的固定编码。`checks.future_invisibility` 在未训练模型上也应给出布尔结果；它检查的是掩码实现，不是模型质量。

`train` 的 `checks.reload` 是保存后重新载入再比较 logits；`checks.target_shift` 是输入/目标错位检查。三者都不是“训练效果”指标；训练效果要看 `losses` 和独立留出材料。
