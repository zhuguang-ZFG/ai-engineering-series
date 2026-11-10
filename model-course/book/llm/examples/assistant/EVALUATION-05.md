# 05 · 更强授权模型 + API provider 栈试验（非隔离单变量）

日期：2026-11-10。目的：K3 计划项"固定原问题/预算，每次只改一个因素"的模型侧试验。本批把生成侧从"本地 1.5B"换成"显式授权的 API 强模型"，问题、期望、`budgets` 保持冻结；但本地→API 同时引入两项 provider 栈差异（见下），因此本试验是 provider/模型栈对照，**不是**隔离的模型单变量，不能直接当作"模型因素"的结论基线。

## 与本地 1.5B 基线的栈差异（同为冻结预算下的真实差异）

| 因素 | 本地 1.5B | 本批 API | 影响 |
| --- | --- | --- | --- |
| prompt 预算计量 | `count_tokens` 精确 token，上限 2048 | `count_chars` 字符近似，上限 2048×2≈4096 字符 | API 侧实际允许更长的 prompt，检索块被丢弃的边界不同 |
| 输出合同 | 解码参数 `do_sample=False`，无 response_format | `response_format={"type":"json_object"}` + temperature 0 | API 侧有显式 JSON 模式；本地无 |
| 超时 | 本地 CPU 推理无读超时（仅总时长人工约束） | `api_timeout=15` 秒硬超时 | 推理模型的首 token 延迟可能直接触发 TimeoutError |
| 计费/计量 | token 实测 | provider usage 字段，缺价时不计价 | 只影响报告字段，不影响判分 |

后续要真正隔离"模型"因素，需在**同一 provider 栈**下比较非推理强模型与基线，或把上述差异逐项固定后再换模型。

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

| 用例 | 期望 | 实际 | 首个失败 | 判定 |
| --- | --- | --- | --- | --- |
| normal-wind | answered | generation-failed | 读超时（15s 内无响应，raw 0 条） | 失败 |
| no-hit-coffee | insufficient-evidence | generation-failed | 响应到达但 `message.content` 非字符串（raw 0 条） | 失败 |
| conflict-closing | conflict | generation-failed | 读超时（raw 0 条） | 失败 |
| agent-calculator | answered + calculator | generation-failed | 第一步有效工具请求后，后续内容非字符串 | 失败 |
| unauthorized-reader 等四边界（冻结清单本地） | 各自期望 | 全部符合 | — | 通过 |

逐例事实（来自 quality-05-api-mistral-large-4.json 的 `diagnostics`）：

- 两例**读超时**（normal-wind、conflict-closing）：15 秒内未收到响应体，无法观察其 token 用途；不能声称它们"烧光预算"。
- 两例**内容非字符串**（no-hit-coffee、agent-calculator 后续步）：响应到达但 `content` 为空/非字符串。
- **agent-calculator 的第一步是有效工具请求**：`{"action":"tool","tool":"calculator","arguments":{"expression":"4.2*86400"}}`——在该 provider 栈与冻结预算下，模型具备按合同发起正确工具调用的能力；失败发生在后续步。
- 因此"四例全部因推理烧光 token 而失败"不成立：只有独立的 192-token 复演探针支持"该模型在 192 token 内可能完不成推理+作答"，且该探针是单次简化载荷，不等于各用例的真实 prompt。

完整报告：[冻结清单本地运行](../../specs/llm-learning-redesign/evidence/quality-05-frozen-local.json)、[API 强模型运行](../../specs/llm-learning-redesign/evidence/quality-05-api-mistral-large-4.json)。两次 `manifest_unchanged: true`。证据副本中的工作区绝对路径已脱敏为仓库相对路径（原始终端输出留在本机 out/k3-api/，不入库）。

## 失败模式与辅助证据

逐例失败分两类：读超时（2 例，首 token 延迟超 15s）、响应到达但内容非字符串（2 例，其中 agent-calculator 已有有效首次工具请求）。harness 拒绝非字符串内容并保留首次失败，行为正确：不剥壳、不修复、不重试到满意。

辅助证据（不是各用例的直接证明）：用与 harness 相同的载荷（max_tokens=192、temperature 0、response_format json_object）做单次简化探针，该模型跑满 192 token 后 `finish_reason=length`、`content=null`——推理 token 占满预算时确实无最终内容；同一模型在 max_tokens=512 探针下正常返回字符串（`ok`，finish=stop）。这支持"该推理模型与 192 token 预算可能结构性不兼容"，但不证明四个用例各自都因此失败。

## 判定

- "更强授权模型 ⇒ K3 通过"证伪，但**归因不能收窄到"模型"单一因素**：本批同时换了 provider 栈（prompt 计量放宽到字符近似×2、新增 response_format 合同、15s 硬超时），且逐例失败模式不均一（超时 vs 内容非字符串 vs 有效工具请求后失败）。
- 可记录的正面事实：在该 provider 栈与冻结预算下，agent-calculator 的首次工具请求完全符合合同，说明强模型具备按合同行动的能力；失败集中在超时与后续步内容形态。
- K3 继续失败；四个边界用例保持绿色。已排除：端点不可达、鉴权失败、配额之外的因素。
- 下一步隔离方案（任选一）：① 找到非推理强 instruct 模型、在同一 API provider 栈下重跑本清单——若通过，才能说"模型因素"是主因；② 在同一 provider 栈下重跑并放宽 api_timeout 单变量，区分超时与预算的贡献；③ 继续用本地 1.5B，只改 response_format/预算计量中的一项。本机剩余未识别网关（MUYUAN/JIANZHILE/LABS100X/VOYA/ARCDENT/CURSOR_AGENT/AIGATEWAY_*/OPENCODE_GO_* 等）需操作者指明端点后才可执行①。
