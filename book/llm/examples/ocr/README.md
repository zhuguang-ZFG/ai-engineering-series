# 本地印刷行 OCR（TrOCR）

这个目录只做一件事：把**一张图里的一行印刷文字**交给本地 TrOCR 识别，并把识别结果、图像哈希、裁剪区域、模型信息和失败状态写成 JSON。它不是 PDF 解析器，不是扫描件版面分析器，也不会自动下载权重或上传图片。

```text
图像字节 → SHA-256 → 解码/裁剪区域 → 本地 TrOCR（Pillow + processor/model）
→ 原始生成文本 → 状态（recognized / uncertain / unreadable）
→ JSON：text + image.sha256 + region + scores + 真实错误
```

`text` 只来自模型生成。任何失败路径都不会填入示例句、默认答案或“看起来合理”的文字。

## 文件

| 文件 | 作用 |
| --- | --- |
| `extract.py` | 单行提取 CLI；权限、模型、图像、区域、推理五类错误分别落为状态 |
| `make_sample.py` | 生成原创样张 `REPAIR WORKSHOP AT 10:00`，用于可重复的本机试跑 |
| `requirements.txt` | 固定本轮 CPU 测试使用的 torch / transformers / Pillow / sentencepiece 版本 |
| `README.md` | 本文：授权边界、模型许可、命令、输出字段和已知限制 |

## 授权与隐私边界

运行 `extract.py` 必须显式传入 `--authorized`。这是**使用者对处理权的声明**，程序无法验证：

- 图片属于你，或你已获得处理许可；
- 其中不含未经授权的个人信息、客户资料、未公开文档或受限制的扫描件；
- 本地模型许可允许你的用途，且你没有把权重再分发；
- 下游使用（检索、发布、训练）另有依据。

没有 `--authorized` 时，程序在打开图像和读取模型目录之前返回 `unauthorized`，仍会写出 JSON 报告。不要通过改代码、改状态或去掉检查来“通过”；需要处理权时应先取得授权。

`extract.py` 默认只在本机运行：`local_files_only=True`、`trust_remote_code=False`，不访问网络、不读取 API 凭据。它不把图片或文本写入日志；报告中的 `image.path` 与 `text` 会包含本地路径和识别内容，保存和分享报告前要自行检查隐私。

## 模型来源与许可

本仓库**不提交模型权重**，也不会在运行时下载。你需要准备一个本地 TrOCR 目录，包含 processor 与模型文件，例如 `microsoft/trocr-small-printed` 的本地副本。

- `microsoft/trocr-small-printed` 的模型卡明确说明它用于 OCR（印刷文本行）；上游 `unilm/trocr` 仓库根目录为 MIT。
- 但该模型在 Hugging Face 模型卡中**没有可依赖的 `license` 字段**，也没有随权重提供明确许可证文件。因此：不能把权重当成 MIT 再分发，也不能声称“模型权重就是 MIT”。本课程只记录模型卡允许 OCR 使用这一事实；再分发、商用、训练衍生模型等用途需要你自行取得明确许可。
- 上游代码许可（MIT）不等于模型权重许可。两者不要混为一谈。
- 模型目录不进入 git；分享交付包时只写路径、来源和用途，不打包无权再分发的权重。

## 安装

在仓库根目录：

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
python -m pip install -r book/llm/examples/ocr/requirements.txt
```

`sentencepiece==0.2.1` 是 TrOCR 分词器的实际依赖。**本轮课程维护环境实测的第一次失败就是环境里缺 `sentencepiece`**：模型加载阶段报错。后来在隔离虚拟环境安装 `sentencepiece==0.2.1` 后，同一模型目录的识别才成功。不要看到 `transformers` 已安装就跳过这一步。

如果平台没有对应 `torch==2.14.1` 的轮子，记录你的实际版本、设备和差异，不要把未测版本写成已验证。`requirements.txt` 是本轮实测下限，不是所有平台的通用锁文件。

## 生成原创样张

默认样张是一行英文印刷字：

```bash
python book/llm/examples/ocr/make_sample.py \
  --output book/llm/examples/ocr/sample-line.png
```

输出 JSON 会给出路径、文本、宽高、文件 SHA-256 和字体来源。默认字体来自 Pillow 自带字体，不引入第三方扫描件；生成的 PNG 是课程原创测试材料。可以用 `--text` 换一行自己的合法文本，例如：

```bash
python book/llm/examples/ocr/make_sample.py \
  --output out/my-line.png \
  --text "VALVE CLOSED BEFORE SERVICE"
```

样张是合成印刷字，不代表真实扫描的褶皱、倾斜、污渍、手写或多语言版面。

## 运行提取

```bash
python book/llm/examples/ocr/extract.py \
  --image book/llm/examples/ocr/sample-line.png \
  --model /path/to/trocr-small-printed-local \
  --output out/sample-line.json \
  --authorized
```

可选裁剪区域（像素，原点在左上角）：

```bash
python book/llm/examples/ocr/extract.py \
  --image scan.png \
  --model /path/to/trocr-local \
  --region 120,340,900,80 \
  --output out/scan-line.json \
  --authorized
```

`--region` 用于只取一行或一个标注框；不传时整张图进入模型，报告会记录“未裁剪”警告。区域越界、宽高非正、坐标不是整数都会返回 `invalid-region`。

生成预算默认 64 个 token，单行通常足够；不要为了“多识别一点”把它调得很大，模型可能继续生成看似文字的内容。`--min-mean-logprob` 是操作阈值，不是准确率。

## 输出字段

成功或可判定的报告结构：

```json
{
  "schema": "ocr-extract/1",
  "status": "recognized",
  "text": "<模型实际生成的字符串>",
  "confidence": null,
  "confidence_note": "TrOCR does not expose a calibrated recognition confidence...",
  "image": {
    "path": "...",
    "sha256": "<原始图像文件字节的 SHA-256>",
    "width": 800,
    "height": 120,
    "mode": "RGB",
    "format": "PNG"
  },
  "region": {
    "x": 0,
    "y": 0,
    "width": 800,
    "height": 120,
    "coordinate_system": "pixels, origin top-left",
    "sha256": "<裁剪区域解码后 RGB 像素字节的 SHA-256>",
    "sha256_basis": "decoded RGB pixel bytes in this region"
  },
  "model": {
    "path": "...",
    "local_files_only": true,
    "trust_remote_code": false,
    "device": "cpu",
    "config_sha256": "<config.json 的 SHA-256，若存在>"
  },
  "generation": {
    "do_sample": false,
    "max_new_tokens": 64,
    "sequence_tokens": 20
  },
  "scores": {
    "mean_token_logprob": null,
    "scored_tokens": 0,
    "uncertain_below": -2.5,
    "basis": "mean log-probability ... not calibrated, not an accuracy estimate"
  },
  "timing_ms": {
    "load_ms": 0.0,
    "inference_ms": 0.0,
    "total_ms": 0.0
  },
  "warnings": [],
  "error": null
}
```

字段含义：

- `text` 是模型原始输出的 `strip()` 结果（只去掉首尾空白，不改内部字符）；如果下游要求完全逐字，请以该字符串为准并在报告中保留原图。
- `image.sha256` 是原始图像**文件字节**的哈希；替换图片、重新保存或改元数据都会变化。它是“我看的是哪张图”的第一层证据。
- `region.sha256` 是裁剪后 `RGB` **像素字节**的哈希，不是 PNG 重编码后的文件哈希。它回答“模型实际看了哪一块像素”。
- `region` 的坐标相对原图，原点左上；页码或版面坐标要另外记录，不能拿这个数组冒充页码。
- `model.local_files_only` 与 `trust_remote_code` 固定为 `true` / `false`，表示没有自动下载、没有执行远端自定义代码。
- `scores.mean_token_logprob` 只是模型内部序列分数。**本程序不把任何数值解释为“识别正确率”**；`confidence` 永远是 `null`。同一分数在不同图片、字体、模型上不可直接当概率比较。
- `timing_ms` 是本次进程的实际测量，受首次加载、CPU、图片大小影响；不能拿去承诺服务延迟。

## 状态、错误与退出码

| `status` | 含义 | 退出码 | 是否调用模型 |
| --- | --- | --- | --- |
| `recognized` | 非空生成，且通过操作阈值 | 0 | 是 |
| `uncertain` | 非空生成，但平均 token log-prob 低于阈值，或不含字母/数字 | 3 | 是 |
| `unreadable` | 模型生成空串；不要自行补全 | 4 | 是 |
| `unauthorized` | 未传 `--authorized`；未打开图像/模型 | 2 | 否 |
| `model-unavailable` | 没给 `--model`、目录不存在/不是目录、文件不完整或加载失败 | 2 | 否/加载失败 |
| `invalid-image` | 路径不存在、不是文件、Pillow 无法解码、尺寸非法 | 2 | 否 |
| `invalid-region` | 区域格式错误、非正大小或越界 | 2 | 否 |
| `invalid-arguments` | token 预算或 log-prob 阈值非法 | 2 | 否 |
| `dependency-unavailable` | Pillow / torch / transformers 未安装 | 2 | 否 |
| `inference-error` | 本地生成或解码抛出异常 | 1 | 尝试过 |

`uncertain` 仍会给出 `text`，但它不是“已确认”。`unreadable` 的 `text` 是 `null`，`error.message` 说明是空生成；不要让下游把 `null` 当成空字符串继续拼接。所有失败报告都保留已经取得的 `image`/`region` 证据，但不含伪造文本。

## 下游引用契约

本课程从 C27 起采用**逐字引用**规则：下游答案只能使用经过核验的原文片段；如果系统改写、概括或翻译原文，必须有人工复核并明确标注“改写，未经逐字核对”。OCR 结果同样如此：

1. 先用 `image.sha256` 固定输入；
2. 用 `region` 固定模型看到的位置；
3. 用 `text` 回看原图像素，逐字核对；
4. 只有核对通过的片段才能进入答案/引用；
5. `uncertain`/`unreadable` 不得被下游“补全”为确定事实。

这条规则不保证 OCR 一定正确，只是把“模型说了什么”和“材料确实写了什么”分开。

## 本轮实际烟测记录（课程维护环境）

以下是本轮课程维护环境在隔离环境中实际执行的结果，不是本 README 作者复跑，也不是通用准确率：

- 识别对象：原创印刷行 `REPAIR WORKSHOP AT 10:00`（与 `make_sample.py` 的默认文本相同；实际烟测图像由课程维护环境生成，像素哈希以那次报告为准）。
- 实际输出：`REPAIR WORKSHOP AT 10:00`，推理耗时约 `1.792 s`（报告中的计时口径以该次运行为准）。
- 第一次尝试失败：环境缺少 `sentencepiece`，模型加载失败；在隔离虚拟环境安装 `sentencepiece==0.2.1` 后成功。
- 环境：Python 3.13、Torch 2.14.1 CPU、Transformers 5.21.0、Pillow 12.3.0、`sentencepiece 0.2.1`。

这只证明“该机器、该模型目录、该合成样张”能跑通一次；不证明扫描件、手写、中文、表格或多行版面同样可用，也不证明其他模型目录可直接复用。

## 已知限制

- **单行印刷英文**是设计目标。TrOCR 的输入是一个文本行图像；整页文档应先做文本层提取或版面/行检测，不要把整页直接当作一行。
- 不自动应用 EXIF 方向；手机照片可能横置或倒置。先旋转/导出为正立图像，再运行；报告不会替你推断方向。
- 不支持手写、复杂表格、公式、竖排、多栏、印章、低分辨率、强透视和严重污渍。遇到这些情况应报告 `uncertain`/`unreadable` 或“需要其他工具”，而不是让模型猜。
- 模型可能生成看似合理的错字，尤其是相似字形、数字和专有名词。必须逐字回看原图；`mean_token_logprob` 不是校准概率，不能单独作为验收依据。
- 没有页码、版面框、阅读顺序、表格结构；`region` 只是你传入的像素裁剪。页码/区域引用要在调用方单独维护。
- 只使用 CPU 路径；CUDA/MPS 需要另测，不能把 CPU 耗时外推到 GPU 服务。
- 没有批量、队列、并发、超时取消或服务健康检查；这些属于 C29 的交付工程，不是本脚本的承诺。
- 模型权重许可需要使用者自行确认；本仓库不提供再分发保证。

## 相关章节

- [C27 图片、扫描件与多模态边界](../../lessons/c27.md)
- [C27 答案与核对](../../deepening/c27-answer.md)
- 旧的 [多模态回查](../../../../exports/llm/multimodal-reference.html) 只提供概念对照，不是本章实测记录。
