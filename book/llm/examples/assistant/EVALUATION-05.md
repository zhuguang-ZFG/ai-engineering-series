# 05 · 更强授权模型单变量对照（冻结预算）

日期：2026-11-10。目的：K3 计划项"固定原问题/模型/预算，每次只改一个因素"下的模型单变量实验——只把生成模型从本地 1.5B 换成显式授权的 API 强模型，问题、期望、预算、校验器全部保持冻结。

## 方法与冻结

- 原冻结清单 `eval-manifest.json`（SHA-256 `5255ec386cd139b139cb72645c1f9de2c35b1ba569d8175c5eb50ab263b805fd`）未改动。
- 按清单头部"修改评测集前先复制并提升版本"的流程，新建 [eval-manifest-api.json](eval-manifest-api.json)（SHA-256 `69cc43945a67447b7e01bf85dd092faa66778b86e1a6173679e2799b23dccd3f`）：问题、期望、`budgets`（max_new_tokens=192、api_timeout=15 等）逐字一致，仅四个实际调用模型的用例加 `provider: api`；四个不触达模型的边界用例（unauthorized-reader、missing-source、model-missing、api-unconfigured）仍在冻结清单下本地运行，结果与历史一致。
- 本文件与证据不记录任何密钥值；只记录环境变量名与端点域名。

## 凭证可用性实测（本机环境变量，2026-11-10）

| 端点 | 结果 |
| --- | --- |
| NVIDIA NIM（integrate.api.nvidia.com） | 账号可用面极窄：mistral-large-4 可调；kimi-k2.6、nemotron-ultra-253b、mistral-large-2、yi-large、palmyra 系列均 "Function not found for account"（404） |
| Moonshot 官方（api.moonshot.cn / .ai） | KIMI_API_KEY 401 |
| Cloudflare AI 网关 | 各 key 均 Authentication error（10000） |
| StepFun 官方 | 目录可读；step-3.5-flash 调用 quota_exceeded |
| Google Gemini | GOOGLE_API_KEY 无效（INVALID_ARGUMENT） |
| ModelScope OpenAI 兼容 | /models 200；chat/completions 持续 "Unexpected Server Error" |
| LIMA（chat.donglicao.com） | 410 Gone |
| Z.AI coding（api.z.ai/coding/paas/v1） | nginx 404 |

结论：本机环境中唯一可调用的更强授权模型是 NVIDIA NIM 的 `mistralai/mistral-large-4-1t-a52b`。

## 单变量结果（mistralai/mistral-large-4-1t-a52b，temperature 0，冻结预算）

| 用例 | 期望 | 实际 | 判定 |
| --- | --- | --- | --- |
| normal-wind | answered | generation-failed | 失败 |
| no-hit-coffee | insufficient-evidence | generation-failed | 失败 |
| conflict-closing | conflict | generation-failed | 失败 |
| agent-calculator | answered + calculator | generation-failed | 失败 |
| unauthorized-reader 等四边界（冻结清单本地） | 各自期望 | 全部符合 | 通过 |

完整报告：[冻结清单本地运行](../../specs/llm-learning-redesign/evidence/quality-05-frozen-local.json)、[API 强模型运行](../../specs/llm-learning-redesign/evidence/quality-05-api-mistral-large-4.json)。两次 `manifest_unchanged: true`。证据副本中的工作区绝对路径已脱敏为仓库相对路径（原始终端输出留在本机 out/k3-api/，不入库）。

## 失败首个边界

- 直接复演 harness 载荷（max_tokens=192、temperature 0、response_format json_object）：完成 192 个 token 后 `finish_reason=length`、`message.content=null`——该推理模型把全部预算花在 reasoning tokens 上，没有产出最终内容；单次延迟约 36s，也超过清单 `api_timeout=15`。
- 放大 max_tokens 的对照探针（512）：同一模型正常返回字符串内容（`ok`，finish=stop），说明模型本身可用，失败是"冻结预算 × 推理模型"的结构性冲突，不是端点或鉴权问题。
- harness 拒绝 `message.content is not a string` 并保留首次失败，行为正确：不剥壳、不修复、不重试到满意。

## 判定

- "更强授权模型 ⇒ K3 通过"证伪：在冻结预算下，可用的强模型是推理型，预算与超时双重不兼容；这不是放宽预算的理由。
- 需要非推理、低延迟、严格 JSON 的强 instruct 模型才能继续做模型单变量；本机环境变量中剩余未识别网关（MUYUAN/JIANZHILE/LABS100X/VOYA/ARCDENT/CURSOR_AGENT/AIGATEWAY_*/OPENCODE_GO_* 等）需操作者指明对应端点后重试。
- K3 继续失败；四个边界用例保持绿色。已排除：端点不可达、鉴权失败、配额之外的因素。
