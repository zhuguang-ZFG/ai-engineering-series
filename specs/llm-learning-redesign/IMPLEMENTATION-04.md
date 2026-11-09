# 教材迭代04：1.5B 复测、章节实跑与交付基础

日期：2026-11-09，课程 1.1.2 技术试读版。先完成原模型复测，再按失败证据修订教材与交付工具；K1–K5 的硬判据不变，完整 spec 仍有缺口。

## 模型质量

三轮均跑完原八题，清单与预算不变。1.5B copy 4/8，extract 原版 5/8，新系统提示 5/8，逐例状态相同。修正 extract 的系统/用户消息 schema 冲突；copy、agent、extract 用户消息、校验器与解码未改。实际源码集成与受测候选系统消息逐字一致，见[集成核对](evidence/quality-04-integration.json)。

预登记规则要求分数不降、边界不变、没有新接受的无依据回答；本次满足，但没有测得质量提升。风速仍输出围栏、冲突仍未列出两份依据、Agent/extract 仍不支持；默认 copy 另有自由改写和错误工具 action。全文首次响应、模型/源码/清单摘要与采用判定见[完整对照](../../book/llm/examples/assistant/EVALUATION-04.md)。前批两次未完成记录保留，不与本批成绩混计。

## 章节与 K4

[逐章审校](CHAPTER-RUN-04.md)登记 C11–C30 的实际覆盖和缺口。修正 C11 的时间分隔/BOM/空值，C12 字节数，C18 预期失败计分与跨次清单哈希，C18/C22 清单移动后的相对路径，C23 自动微分及冻结历史梯度，C27 未声明依赖，C28 重叠/空文本预算，C29 就绪与 HTTP 状态说明。修前输出与修后输出都保留，不只写最终通过。

C13–C22 的 20 条本地模型命令已执行，含 6 轮评测、41 个用例执行；C13 可选 API 未执行。C18/C22 的五轮完整八题均 4/8，通过的是预期边界拒绝；正常问答和工具任务继续失败。C20 实际读到注入文本后提出错误计算器请求，不能把工具拒绝称为模型抗注入成功。完整首次输出与分章结果见[章节证据](evidence/quality-04-chapter-models.json)。

K4 使用默认 400 步训练及各 120 步 SFT/LoRA，从同一底座开始，记录训练/验证/留出损失、真实生成、参数哈希、梯度冻结与重载。临时去掉掩码能检出未来泄漏，跨 split group 被拒绝；X09 梯度中心差分和错误教师结果符合数值。详见 [K4 技术证据](K4-TECHNICAL-04.md)。这是课程维护者的实操汇集，独立阶段作业与讲解仍待验收。

## 环境、OCR 与 K5 基础

原推理 venv 继承系统包，只能作为历史运行环境。新建不继承系统包的 CPython 3.13 venv，按版本/wheel 哈希离线安装并执行 pip check、真实 embedding、训练与 OCR。初始 37 包锁遗漏 protobuf，OCR 首次失败；日志显示 SentencePiece 转换因缺 protobuf 而回退，最后报 tiktoken 缺失。补入 protobuf 7.36.2 后同一模型/图片识别成功，截断、未授权和非法区域均按预期返回；最终锁为 38 包。[环境](evidence/quality-04-environment.json)、[OCR 修前修后](evidence/quality-04-ocr.json)均有记录。

新增 [release_store.py](../../book/llm/examples/delivery/release_store.py)：显式 payload 全文件哈希、独立版本目录、不覆盖旧版、拒绝链接及未登记文件、验证后原子替换当前指针、再次校验当前版本。回退通过选择旧目录实现；工具不执行清单命令或管理进程。四项回归覆盖构建/选择/回退、损坏候选保留旧指针、文件/清单篡改及错误路径/缺文件不发布。

实际从发布副本启动 loopback 服务，注入缺源故障并切回旧包，验证健康、查询、坏 JSON、身份越权与服务停止；边界行为恢复。随后以真实 0.5B 重做同一个已知有证据的问题：回滚前后均为 HTTP 400 invalid-response，故障版本为 HTTP 409 missing-source，三次健康均 200、身份越权均 403。[就绪试验](evidence/quality-04-delivery-readiness.json)判定失败，回滚恢复的是旧包及原有失败行为，不能称为可用服务恢复。K5 的授权陌生材料、冻结 20 题、留出质量及另一人独立启动仍待完成。

## 验证与发布记录

1.1.2 同源导出为正文 449 页、答案 207 页。完整 `npm test` 实际退出 0，69 项单元测试通过（Python 33、Node 36）；三套官方 EPUBCheck 5.3.0 零错误/警告。240 组 EPUB 重排、56 组本批网页布局、92 页可访问性/4 条键盘流、15 阅读行为/50 布局及原书阅读检查通过。已审看 PDF 403/243/391 页和 C18 手机/C29 桌面截图。[本地验证记录](evidence/quality-iteration-04.json)绑定本批源码和成品哈希。

首轮截图定位未处理 PDF 中文跨行，完成布局检查后出现 StopIteration；改为去空白定位并完成最终检查。PowerShell 曾把 unittest 的 stderr 当成命令错误，后经 subprocess 明确记录全检查退出 0。两项是验证包装问题，未改测试断言或降低验收条件。

C20 的 HTTP 测试包装曾绕过 main 的工具白名单规范化；保留首轮报告后，通过正式 CLI 子进程补跑两次请求，配置恢复为 `["calculator"]`，结果仍为 400 invalid-response。此次只修正测试入口；发布回滚试验本来就使用 CLI，不受影响。详细记录见[逐章审校](CHAPTER-RUN-04.md)。

发布与 CI 按实际 GitHub 记录登记；此前 CI 不充当本批结果。`task_verify` 当前无可调用工具/有效基线，保持 unverified；本地测试不替代独立审查。

本批发布入口为 [PR #12](https://github.com/zhuguang-ZFG/vibe-coding-101-course/pull/12)；首个实现提交 `54d603b` 的 [CI](https://github.com/zhuguang-ZFG/vibe-coding-101-course/actions/runs/42509996211) 全部通过。最终提交、合并及 main CI 以 PR 的提交/检查记录和[工作流记录](https://github.com/zhuguang-ZFG/vibe-coding-101-course/actions/workflows/ci.yml)为准；首轮通过仅覆盖首个提交。环境记录同时保存 Windows 安装时的原始锁文件哈希及 Git LF 文本哈希，避免换行差异被误认为依赖改变。

## 继续条件

模型问答质量、未覆盖来源/独立作业、陌生项目与真人验收继续见 [STATUS](../STATUS.md)。独立阅读器正文/重排与实际读屏语音仍未通过，不用浏览器检查替代。未参与制作的人应使用本批交付条件复做，不能由作者或 agent 填写其成绩。
