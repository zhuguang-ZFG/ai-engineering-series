# 微型因果 decoder：从零件到 SFT/LoRA

这个目录只做一件事：用 CPU 和本目录内的原创玩具语料，把一个**真实的**因果 Transformer decoder 从零件装起来，完成训练、保存/重载、自回归生成，再比较全量 SFT 与冻结底座的 LoRA。它不下载权重，不调用任何外部模型或接口，也不声称能完成真实用户任务。

对应章节：[C23 从数组走到自动微分](../../lessons/c23.md)、[C24 从零组装最小 decoder](../../lessons/c24.md)、[C25 何时适配参数，何时不该训练](../../lessons/c25.md)、[C26 蒸馏学到的是什么](../../lessons/c26.md)。答案在 [`../../deepening/`](../../deepening/)。

## 文件与数据来源

| 文件 | 作用 |
| --- | --- |
| `model.py` | tokenizer、词嵌入、正弦位置、多头因果注意力、FFN、残差/归一化、输出头、LoRA、保存/重载 |
| `train.py` | `inspect` / `train` / `sample` / `adapt` 四个子命令 |
| `corpus.jsonl` | 预训练语料，192 条，按 `group` 分训练/验证/留出 |
| `sft.jsonl` | 指令-回答样本，90 条，按形容词组分离 |
| `requirements.txt` | 仅 PyTorch，CPU 参考版本 2.14.1 |
| `LICENSE-CORPUS` | 两份语料的 CC0-1.0 说明 |

`corpus.jsonl` 与 `sft.jsonl` 是课程作者为本题编写的原创数据，由 README 记录的词表和模板确定性地展开，不含任何外部书籍段落、模型输出或下载语料。许可证见 `LICENSE-CORPUS`（CC0-1.0）。

语料分组（`train.py` 会拒绝任何横跨多个 split 的 group）：

| 数据 | 训练 | 验证 | 留出 test |
| --- | --- | --- | --- |
| `corpus.jsonl` | `template-g1`…`template-g4`、`command` | `template-g5` | `template-g6` |
| `sft.jsonl` | `adjective-small` / `red` / `quiet` | `adjective-bright` | `adjective-old` / `warm` |

留出组在各自训练集中完全未出现；词表只从预训练的训练文本构建，验证/留出中遇到未登录词会被编码成 `<unk>`，`train.py` 会打印 `oov_tokens`，不会偷偷扩充词表。当前语料的所有单词都至少出现在预训练训练组一次；若改动语料，先看这个计数。

## 模型不是拟合物

```text
token id [B,T]
  -> token embedding [B,T,64]
  + 固定正弦位置 [T,64]                  （无位置参数，重载时重算）
  -> 2 个 block，每个 block：
       LayerNorm -> 4 头因果注意力（每头 16 维）
       -> 残差相加
       -> LayerNorm -> FFN 64 -> 128 -> 64
       -> 残差相加
  -> LayerNorm
  -> 输出头 64 -> V（与 token embedding 权重共享）
```

因果掩码在 softmax **之前**把每个位置右侧的分数置为 `-inf`，所以未来 token 的权重严格为 0。`train.py inspect` 和新训练结束都会实际比较“只改前缀之后的后缀”时前缀 logits 是否一致（`checks.future_invisibility`）。这只证明实现的掩码没有让未来信息进入前缀计算，不证明模型理解语言。

`max_len` 是硬上限；生成到上限就停止，调用方可以从 `positions_used` 看到实际长度，不能假定一定有固定长度的结尾。

## 环境与命令

在仓库根目录运行；CPU 即可。若本机没有 CPU 版 PyTorch：

```bash
python -m pip install --index-url https://download.pytorch.org/whl/cpu -r book/llm/examples/tiny_decoder/requirements.txt
```

所有命令：

```bash
python book/llm/examples/tiny_decoder/train.py --help

# 1. 看结构、参数量、因果掩码检查（可无 checkpoint）
python book/llm/examples/tiny_decoder/train.py inspect

# 2. 预训练并保存；默认写到 tiny_decoder/runs/base.pt
python book/llm/examples/tiny_decoder/train.py train

# 3. 载入检查点生成
python book/llm/examples/tiny_decoder/train.py sample \
  --checkpoint book/llm/examples/tiny_decoder/runs/base.pt \
  --prompt "the red boat" --max-new 12 --temperature 0.8 --top-k 10

# 4. 全量 SFT、LoRA，或两者依次对照
python book/llm/examples/tiny_decoder/train.py adapt --method full
python book/llm/examples/tiny_decoder/train.py adapt --method lora
python book/llm/examples/tiny_decoder/train.py adapt --method both

# 5. 检查适配后的模型（会自动重建 LoRA 包装）
python book/llm/examples/tiny_decoder/train.py inspect \
  --checkpoint book/llm/examples/tiny_decoder/runs/adapt-lora.pt
```

`inspect` / `train` / `sample` / `adapt` 都接受 `--json`：默认输出带缩进，`--json` 输出单行机器可读 JSON。`runs/` 已加入 `.gitignore`，训练产物不应提交。

默认训练规模是 2 层、`d_model=64`、4 头、`d_ff=128`、400 步；CPU 上只是教学规模。可以用 `--steps`、`--batch-size`、`--lr`、`--layers`、`--d-model`、`--heads`、`--d-ff`、`--max-len` 改变条件。改结构后必须重新 `train`，不能把旧 checkpoint 直接塞进新结构。

## 每个命令实际打印什么

### `train`

关键字段：

- `corpus.splits`：每个 split 的记录数与 group 列表；可核对 group 没有跨 split。
- `corpus.oov_tokens`：验证/留出中编码成 `<unk>` 的 token 数。
- `parameters`：`total` / `trainable` / `frozen`。预训练时三者关系应当是全可训练。
- `training.history`：每若干步的**更新前**批次损失；不是预画的下降曲线。
- `losses.train` / `losses.val` / `losses.test`：训练后在这三组上重新计算的逐目标 token 交叉熵与困惑度。留出组的损失通常高于训练组；这只说明这组玩具数据上的情况，不能外推成通用能力。
- `checks.target_shift`：同一序列的输入与目标是否真的错开一位；`aligned=true` 才说明 `x=[t0..tT-1]`、`y=[t1..tT]`。
- `checks.future_invisibility`：`bitwise_equal`、`max_abs_diff`、`suffix_changed`。若把掩码去掉或错位，这里会暴露。
- `checks.reload`：把 checkpoint 重新载入后，与保存前模型在固定输入上的 logits 是否逐位相等（`bitwise_equal`、`max_abs_diff`）。
- `sample`：本次自回归结果、`generated_ids`、`generated_text`、`hit_eos`、`positions_used`。
- `artifact`：checkpoint 路径与字节数；`seconds`：本次实际墙钟时间。

保存格式是 `state_dict` + 配置 + 词表 + 适配元数据，没有 pickle 整个 Python 对象；载入使用 `torch.load(..., weights_only=True)`。这样可以重建模型结构，但不会执行 checkpoint 里的任意对象。

### `sample`

打印 `prompt`、`prompt_ids`、`generated_ids`、`generated_text`、`full_text`、`hit_eos`、`positions_used`、`temperature`、`top_k`、`max_len`。`temperature <= 0` 表示贪心；否则按温度缩放，`--top-k` 会先截断再采样。生成是逐 token 的真实前向计算，没有查表拼接。

### `adapt`

`--method lora` 时：

- `parameters.before`：底座参数量（全冻结前）。
- `parameters.after_setup`：包装 LoRA 后的总参数/可训练/冻结计数。可训练参数只来自 `lora_A`、`lora_B`。
- `checks.base_checksum_before` / `after` / `base_unchanged`：底座参数哈希；LoRA 训练后应不变。
- `checks.lora_changed`：适配器参数哈希应变化，证明真的更新了。
- `checks.base_grads_all_none`：底座参数没有累积梯度。
- `checks.reload`：保存为带 LoRA 元数据的 checkpoint 后，重新包装并载入，logits 是否一致。
- `losses.before` / `after` / `delta_val` / `delta_test`：SFT 训练组、验证组、留出组的损失变化；只在这组玩具样本上解释。

`--method full` 时所有参数可训练，底座哈希会变化（`base_updated=true`），因此 `base_frozen=false`。`--method both` 会从同一个底座分别训练两份模型，输出 `comparison.full` 与 `comparison.lora`，并保存 `adapt-full.pt`、`adapt-lora.pt`。两种方法都不保证一定更好；要结合 `losses` 的验证/留出结果和实际任务另评。

LoRA 的低秩更新是 `y = base(x) + (alpha / rank) * x @ A.T @ B.T`；`B` 初始化为零，所以刚包装时模型与底座 logits 相同，之后只训练 `A`、`B`。本示例保留独立适配器，不把它合并回底座。

### `inspect`

打印 `config`、`vocab_size`、`parameters`、`adaptation`、`architecture`、`checks.future_invisibility`、`checks.base_checksum`；带 checkpoint 时还打印 `sample`。不提供 checkpoint 时使用默认结构和从 `corpus.jsonl` 训练组构建的词表，明确标为未训练（`trained=false`），不会伪造一段像样的生成。

## 会失败的条件

- 语料 group 横跨 split：直接拒绝（防止留出泄漏）。
- 序列超过 `max_len`：拒绝，不静默截断。
- `d_model` 为奇数、不能被 `n_heads` 整除、`n_heads < 1`：配置错误。
- checkpoint 的词表与配置大小不一致：拒绝载入。
- LoRA rank < 1：拒绝。
- 从已经适配过的 checkpoint 再做 `adapt`：拒绝，避免叠加无法解释的适配。
- 载入别人的 checkpoint：本示例只接受本目录 `FORMAT` 的 `state_dict` 结构；不要用 `weights_only=False` 去打开来路不明的文件。

## 边界

- 这是玩具语言模型，语料只有几百条短句、词表很小；它没有世界知识，不是聊天助手，也不能完成真实业务任务。
- 留出损失、生成样例和 SFT/LoRA 对照都是**本目录数据上的测量**。它们不能证明通用泛化、不能证明 LoRA 一定优于全量 SFT，也不能当成商用模型内部机制或蒸馏效果的证据。
- C26 的蒸馏实验仍以已有 X09 教学分布为准；本目录的 `sft.jsonl` 是作者编写的示范数据，不是教师模型的输出，不能声称做了模型到模型的蒸馏。
