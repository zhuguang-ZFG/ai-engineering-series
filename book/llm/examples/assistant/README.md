# 资料助手（assistant.py）

这是一个可以直接运行的教学资料助手，不是伪代码，也不是预置回答演示。它把 C13–C17 的接口串成一条完整链路：

```text
文档清单 → 权限检查 → 读取/切块（稳定哈希版本）→ 词项或 embedding 检索
→ 本地真实模型 / 显式 API → 严格 JSON 与逐字引用校验
→ 可选有限工具循环 → JSON/Markdown 证据报告
```

默认不联网、不下载模型、不读取凭据、不返回人工答案。模型缺失、输出坏 JSON、引用不成立、越权、文档缺失、预算不足都会成为报告里的明确失败状态。

**可自动验证的范围是原文摘录，不是自由改写的事实裁判。** 来源 claim 必须是引用 quote 中连续原文，quote 必须在允许的片段中；最终 answer 只能原样列出已核验的 claims，不得额外加入未列主张。工具主张必须有成功回执并包含实际计算结果。程序不能判断任意自然语言蕴含、事实真伪或现行政策，提取片段与问题/版本是否匹配仍需人工复核。不能用“引用存在”给相反主张或额外结论背书。

## 文件

| 文件 | 作用 |
| --- | --- |
| `assistant.py` | 完整 CLI：`inspect`、`run`、`evaluate`、`serve` |
| `documents.json` | 文档清单：`id`、`path`、`version`、`readers` |
| `documents-missing.json` | 失败路径样例：清单里有一篇不存在的文档 |
| `eval-manifest.json` | 冻结的评测预算与逐例期望 |
| `docs/*.md` | 本书原创的授权样例文本，不含第三方材料 |
| `requirements.txt` | `torch`、`transformers`；embedding 不使用 `sentence_transformers` |

样例文档是虚构观测站材料。`review-budget.md` 只对 `teacher` 开放，用来演示检索前的权限过滤。

## 环境与资源

```text
python >= 3.10
pip install -r book/llm/examples/assistant/requirements.txt
```

本地模型和 embedding 目录由使用者提供，代码固定使用 `local_files_only=True`、`trust_remote_code=False`：

- `--model DIR`：带 chat template 的本地因果语言模型目录（例如 Qwen2.5 Instruct 类）。
- `--embedding DIR`：本地 `AutoModel` 句向量目录（例如 MiniLM 类），代码用 attention mask 做均值池化并 L2 归一化。

本仓库不提交权重，也不会在运行时自动下载。资源不存在时返回 `model-unavailable` / `embedding-unavailable` / `chat-template-missing`。

### 可选、显式授权的 API

只有传 `--provider api` 时才会读取以下环境变量并请求用户指定的 OpenAI 兼容端点：

```text
ASSISTANT_API_BASE   # 例如 http://127.0.0.1:8000/v1
ASSISTANT_API_MODEL  # 端点上的模型名
ASSISTANT_API_KEY    # 可选；为空时不发送 Authorization
```

没有 base/model 时立即返回 `api-config-missing`，不发起网络请求。默认 `--provider local`。

## 文档清单与权限

```json
{
  "schema": "assistant-documents/1",
  "documents": [
    {
      "id": "station-log",
      "title": "观测站值班记录",
      "path": "docs/station-log.md",
      "version": "1.0.0",
      "readers": ["student", "teacher"]
    }
  ]
}
```

- `path` 相对清单所在目录，禁止绝对路径、盘符和 `..` 越界。
- `readers` 非空；`"*"` 表示所有读者。每次读取必须显式提供 `--reader` / 请求体 `reader`。
- 未授权文档在读取和检索之前就被过滤，不进入内存，也不参与打分。
- `version` 是人工版本；运行时会计算文件 `sha256`，chunk id 形如 `station-log@<hash12>#000`，报告同时给出两者。清单可选 `sha256` 字段用于固定校验，不匹配返回 `source-version-mismatch`。
- 文件缺失返回 `missing-source`，不是空检索。

## 命令

所有命令从仓库根目录运行。

### 1. inspect：不调用生成模型

```bash
python book/llm/examples/assistant/assistant.py inspect read \
  --docs book/llm/examples/assistant/documents.json --reader student --doc station-log

python book/llm/examples/assistant/assistant.py inspect chunk \
  --docs book/llm/examples/assistant/documents.json --reader student \
  --chunk-chars 480 --chunk-overlap 80

python book/llm/examples/assistant/assistant.py inspect retrieve \
  --docs book/llm/examples/assistant/documents.json --reader student \
  --query "冬季闭站时间是几点？" --retriever keyword --top-k 3
```

`inspect retrieve` 也支持 `--retriever embedding --embedding DIR`，可直接比较词项与 embedding 的取回结果。`--json PATH` / `--markdown PATH` 可同时落盘。

### 2. run：真实推理与证据报告

```bash
python book/llm/examples/assistant/assistant.py run \
  --docs book/llm/examples/assistant/documents.json --reader student \
  --question "2026 年 10 月 3 日观测站记录的风速是多少？" \
  --model /path/to/local-model \
  --mode fixed --top-k 3 --max-new-tokens 192 \
  --json /tmp/assistant-run.json --markdown /tmp/assistant-run.md
```

Agent 模式：

```bash
python book/llm/examples/assistant/assistant.py run \
  --reader student --question "值班记录里 2026-10-03 的风速是 4.2 米每秒。连续 24 小时的总行程是多少？请用 calculator 计算 4.2*86400。" \
  --model /path/to/local-model --mode agent --allowed-tools calculator \
  --max-steps 4 --max-tool-calls 2
```

- `--mode fixed`：检索 → 一次模型回答 → 校验，不允许工具。
- `--mode agent`：模型在 `--max-steps` 内自行选择 `calculator` 或 `read_document`，或输出最终回答；每个工具都检查参数、权限和预算，失败即停。`read_document` 需要显式加入 `--allowed-tools calculator,read_document`，且仍受文档读者权限限制。
- `--question-file` 与 `--question` 二选一。
- `--repair-attempts 0`（默认）表示严格解析：输出带 Markdown 围栏就是 `invalid-response`，报告保留首次原始输出。设为 `1` 时会显式发起一次“只输出 JSON”的修复调用，并在 `usage.calls` 与原始响应列表中记录，仍不做静默剥壳。
- `--max-new-tokens`、`--max-prompt-tokens`、`--top-k`、`--min-score`、`--max-steps`、`--max-tool-calls` 都是硬预算。prompt 超预算时按分数从低到高丢弃检索块并记录；仍放不下则 `prompt-budget-exceeded`。
- `--claim-mode copy`（默认）：claim 必须是 quote 的逐字连续子串，answer 只能由已核验 claim 组成。
- `--claim-mode extract`（仅 fixed）：模型只给 `status`、`claims[{chunk_id,quote}]` 和可选 `reason`，主张文本由程序直接取 quote，answer 由已核验 quote 拼接。它不移除围栏、错选片段、漏检冲突这些失败；实测对比与限制见 [BASELINE.md](BASELINE.md)。agent 不支持该模式，会在读取资料和调用模型之前返回 `invalid-request`。

### 3. evaluate：先冻结，再调用

```bash
python book/llm/examples/assistant/assistant.py evaluate \
  --manifest book/llm/examples/assistant/eval-manifest.json \
  --model /path/to/local-model \
  --json /tmp/assistant-eval.json --markdown /tmp/assistant-eval.md
```

- 调用任何模型前读取清单字节并记录 `sha256`、大小、mtime；运行后再校验一次，结果写入 `manifest_unchanged`。
- 每例可覆盖 `documents`、`model`、`provider`、`mode`、`retriever`、`allowed_tools`；预算固定在清单 `budgets` 中。
- 逐例比较状态、引用文档和成功工具回执；stdout 打印摘要，`--json` 保存含完整报告的明细。
- 评测完成（无论通过率）退出码为 0；清单或调用本身不可读等操作错误退出码为 1。

完整八题的 copy/extract 实跑与两种统计口径见 [EVALUATION-03.md](EVALUATION-03.md)。`--claim-mode extract` 会对所有题覆盖模式；其中 agent-calculator 仍按原题要求评分，不支持组合保留为失败，并与七题 fixed 子集分开列出。

样例 `eval-manifest.json` 覆盖：正常引用、资料不足、冲突、越权读者、缺失源文件、缺失模型、未配置 API、Agent 计算器。`no-hit-coffee` 的历史注释称零命中，但词项检索实际会取回其他观测站片段；应按运行报告判断是否零命中，不按 case 名推断。原冻结清单不为修正文案而改写。0.5B 级模型经常无法通过严格引用/冲突判据；保留失败是基线证据，不应删用例或放宽校验。

### 4. serve：本地教学服务

```bash
python book/llm/examples/assistant/assistant.py serve \
  --docs book/llm/examples/assistant/documents.json \
  --reader student --model /path/to/local-model --host 127.0.0.1 --port 8765
```

```bash
curl -s http://127.0.0.1:8765/health
curl -s -X POST http://127.0.0.1:8765/query \
  -H "Content-Type: application/json" \
  -d '{"question":"2026-10-03 的风速是多少？","reader":"student","mode":"fixed","top_k":3}'
```

只允许回环地址；请求体上限 16 KiB。查询参数：`question`、`reader`（必填）、`mode`、`retriever`、`top_k`、`min_score`。响应就是 `assistant-report/1`。HTTP 码：内容状态 200；越权 403；输入/清单/引用错误 400；源文件缺失或版本不符 409；模型/生成失败 502。

服务只允许请求使用启动时 `--reader` 选定的身份；请求体声明其他 reader 在读取文档前返回 403。CLI 的 reader 是本地操作者的教学配置，不是多用户登录系统；不要将该示例暴露公网，也不要把自报身份当认证。`/health` 仅证明服务循环活着，模型是否可用需通过一条有证据的 `/query` 检查。

## 精确引文位置（仅 extract）

抽取报告在 `config.claim_contract` 标记 `source-extract/2`。来源引用保留 `quote`、`start/end`，新增程序计算的 `quote_start/quote_end`：

| 字段/约定 | 含义 |
| --- | --- |
| `start/end` | 整个 chunk 的文档范围；旧含义保持不变 |
| `quote_start/quote_end` | 引文的 `[起点, 终点)`，基于去 BOM、统一为 LF 后的文档 Unicode 码点 |
| 重复匹配 | 取模型所选 chunk 内、空白规范化后第一次匹配；不声称模型指定了多个重复位置中的哪一次 |
| 空白 | 仅折叠连续空白用于匹配，返回位置映射到折叠前文本；不做大小写/标点/Unicode 归一化 |
| `sha256` | 原文件字节的 SHA-256；不是解码后文本或单条 quote 的哈希 |
| 兼容 | 顶层 `assistant-report/1` 保留；默认 copy/agent 和旧报告不新增这些位置字段。读取者应先检查 claim_contract |

模型仍只提交 `chunk_id` 与 `quote`，不得自行提交偏移或另一条主张。Markdown 报告也显示精确范围。拿到一次有来源引用的 extract 报告后，可在仓库根目录用下面的方式回查第一条引用；`out/report.json` 需换成你的真实报告文件。

```python
import hashlib
import json
from pathlib import Path

report = json.loads(Path("out/report.json").read_text(encoding="utf-8"))
assert report["config"]["claim_contract"] == "source-extract/2"
citation = report["claims"][0]["citations"][0]
manifest_path = Path("book/llm/examples/assistant/documents.json")
manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
entry = next(d for d in manifest["documents"] if d["id"] == citation["doc_id"])
raw = (manifest_path.parent / entry["path"]).read_bytes()
assert hashlib.sha256(raw).hexdigest() == citation["sha256"]
text = raw.decode("utf-8-sig").replace("\r\n", "\n").replace("\r", "\n")
start, end = citation["quote_start"], citation["quote_end"]
assert citation["start"] <= start < end <= citation["end"] <= len(text)
assert " ".join(text[start:end].split()) == " ".join(citation["quote"].split())
print(text[start:end])
```

这段代码假定你使用已核验的课程本地清单，并已有相应资料权限；自建项目应沿用助手的清单路径/权限校验。它只核对位置与文本，不能判断引文是否回答问题、是否漏掉条件或是否现行有效。

## 报告结构

```json
{
  "schema": "assistant-report/1",
  "status": "answered",
  "question": "...",
  "reader": "student",
  "mode": "fixed",
  "provider": "local",
  "model": "/path/to/model",
  "documents": [
    {"doc_id": "station-log", "version": "1.0.0", "sha256": "...", "readers": ["student"]}
  ],
  "retrieval": {
    "retriever": "keyword", "threshold": 0.08, "top_k": 3,
    "filtered_doc_count": 1,
    "authorized_doc_ids": ["station-log"],
    "hits": [{"chunk_id": "station-log@...", "doc_id": "station-log", "score": 0.61, "used": true}]
  },
  "answer": "风速 4.2 米每秒",
  "claims": [
    {
      "text": "风速 4.2 米每秒",
      "citations": [
        {"kind": "source", "chunk_id": "station-log@...", "doc_id": "station-log",
         "version": "1.0.0", "sha256": "...", "start": 120, "end": 168,
         "quote": "风速 4.2 米每秒"}
      ]
    }
  ],
  "tool_receipts": [],
  "usage": {"calls": 1, "prompt_tokens": 733, "completion_tokens": 84,
            "latency_ms": 2310.5, "model_load_ms": 1400.2,
            "cost": null, "cost_basis": "local-compute-not-priced"},
  "diagnostics": {
    "first_raw_response": "{\"status\":\"answered\",...}",
    "first_failure": null,
    "raw_responses": [{"step": 1, "attempt": 0, "raw": "...", "prompt_tokens": 733}],
    "warnings": []
  }
}
```

关键约束：

- `claims[].citations[].quote` 必须是所引 chunk 的逐字连续片段（空白规范化后比较）；`chunk_id` 必须来自本次实际使用的检索结果。
- 工具引用写作 `{"tool_receipt_id":"tool-1"}`，回执必须成功；`calculator` 的结果还要出现在 claim 文本中。
- `answered` 至少一条带引用的 claim；`insufficient-evidence` 必须没有 claim；`conflict` 至少两条 claim 且引用两个不同文档。
- 没有命中阈值时不调用模型；模型调用失败时 `answer` 为 `null`。不存在“失败后改用手写答案”的分支。
- 本地费用为 `null`（`local-compute-not-priced`）；API 只有同时提供 `--price-input-per-1k` 和 `--price-output-per-1k` 才计算费用。
- `diagnostics.first_raw_response` 保留模型第一次输出，哪怕它是围栏文本或坏 JSON；`first_failure` 给出阶段和细节。

## 状态与退出码

`run` / `serve` 的内容状态：`answered`、`insufficient-evidence`、`conflict`。

失败状态：`missing-reader`、`unauthorized`、`missing-doc`、`missing-source`、`source-decode-failed`、`source-version-mismatch`、`invalid-manifest`、`model-config-missing`、`model-unavailable`、`embedding-unavailable`、`chat-template-missing`、`prompt-budget-exceeded`、`api-config-missing`、`generation-failed`、`invalid-response`、`citation-failed`、`permission-denied`、`tool-failed`、`budget-exhausted`、`internal-error`。

CLI 退出码：内容状态 0，其他 1，参数错误由 argparse 返回 2。`evaluate` 完成即 0。状态是报告的一部分，不应只看退出码。

## 已知限制

- 样例读者/文档只用于教学，不是生产权限系统；真实部署应接入身份服务和审计。
- 词项检索对中文使用单字 + 二元组；embedding 阈值依赖具体模型，样例默认 0.30，需要在验证集上重新解释。
- 本地模型输出能力取决于模型本身；严格 JSON、引用逐字匹配和冲突判断会大量暴露小模型失败。这不是程序替你生成答案的理由。
- 不执行任意代码；计算器只接受受限 AST 的数值表达式，工具失败会停止循环。
- 没有测试替身、模拟模型或硬编码引用。样例文档是原创文本，使用前请遵守仓库许可。
