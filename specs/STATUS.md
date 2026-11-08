# 大模型：从入门到精通 · 实际进度

更新：2026-11-08。按用户最新要求，主线为五阶段三十章：会使用 → 懂原理 → 能实现 → 会改进 → 独立交付。这里的“精通”对应五道能力门，不承诺读完即可掌握基础模型研究的所有领域。原《Vibe Coding 101》保留为编程实践补充。

**当前是技术试读版，完整 spec 尚未完成。** 三十章、分离答案、真实模型/训练/OCR 示例和网页/PDF/EPUB 已实现；程序能运行、构建通过与读者能独立完成课程是不同证据。

## 已有成果

| 范围 | 实际完成 | 证据 |
| --- | --- | --- |
| N00/N02–N04 内容与结构 | 三十章、三十份答案、五阶段先修路线；保留十二课实验和旧链接 | [课程](../exports/llm/course.html)、[知识映射](llm-learning-redesign/KNOWLEDGE-MAP.md) |
| N01/N05 真实应用 | 本地真实推理、embedding、资料权限、引用校验、有限工具与服务；失败显式返回 | [助手说明](../book/llm/examples/assistant/README.md)、[实现记录](llm-learning-redesign/IMPLEMENTATION.md) |
| N06 冻结评测 | 完整八题基线 4/8；显式提示词单变量对照仍 4/8、输入 token 增加约 75%，已拒绝该改动；可选抽取模式七题子集 5/7 | [首次基线与对照](../book/llm/examples/assistant/BASELINE.md)；子集结果不代表全八题或 K3 通过 |
| N07 小模型训练 | 69,760 参数 decoder 的 80 步训练、留出结果、因果性与重载核验；40 步 SFT、40 步 LoRA，6,600 可训练参数及冻结底座 | [实现记录](llm-learning-redesign/IMPLEMENTATION.md)、[运行说明](../book/llm/examples/tiny_decoder/README.md) |
| N08 图像与交付教学 | 真实英文单行 OCR，截断/无权限失败路径；C27–C30 题包、交付说明与包校验程序 | [OCR](../book/llm/examples/ocr/README.md)、[C30](../book/llm/lessons/c30.md) |
| 本批修订 | 恢复大模型主入口；C13/C15/C17 对齐实际抽取字段与限制；C30 修复缺哈希仍成功、越界路径和自身哈希问题；完成扫描脚本及回归检查 | [本批记录](llm-learning-redesign/IMPLEMENTATION-02.md) |
| 原书上一批发布 | 原书结构/阅读修订及机制图已合并，本地 main 同步至 `80d0513`；这是上一批证据 | [PR #9](https://github.com/zhuguang-ZFG/vibe-coding-101-course/pull/9)、[main CI](https://github.com/zhuguang-ZFG/vibe-coding-101-course/actions/runs/42489349958) |

## 尚未完成的 spec

| 项目 | 具体缺口 | 下一项可验收工作 |
| --- | --- | --- |
| N05 / K3 模型质量 | 默认模式仍有 JSON 格式、引用转述、冲突漏检和工具循环失败 | 固定原评测与预算，定位首个失败边界后只改一个因素，保留所有首次结果；不得改题或放宽证据规则求通过 |
| 抽取契约 | 已支持 fixed/extract，但 `start/end` 是整块位置；尚无 `quote_start/quote_end`，agent 不支持 extract；七题子集不覆盖第八题 | 按[契约台账](llm-learning-redesign/EXTRACTIVE-CONTRACT.md)补精确位置及版本兼容，完成含不支持路径的全清单对照 |
| N05–N09 工程审校 | 本批核对 C13/C15/C17/C30；C11–C30 全部命令、其他图文数值和来源尚未完成逐章实跑审查 | 按章记录命令、依赖、首次输出和失败，不把个别例子推广成全书正确 |
| N06/N07 / K4 整体验收 | 冻结基线、单变量对照、训练与适配分别有证据；尚缺完整阶段作业与独立讲解/复做记录 | 汇集留出评测、参数冻结/重载、错误教师和失败归因，按 K4 全部判据审查；不要求优化一定变好 |
| N08 / K5 陌生项目 | 现有 OCR 和交付题包不能替代陌生题材完整项目；助手依赖仍为范围约束，缺经复建验证的锁定环境与完整回退包 | 先冻结陌生题材问题集，交付真实运行、锁定依赖、故障/回退证据，再由未参与制作的人从干净环境复做 |
| N09 独立阅读器与读屏 | 浏览器重排/键盘/可访问树已检查；独立阅读器正文/重排和真实读屏语音尚未通过 | 按[阅读器记录](llm-learning-redesign/READER-REVIEW.md)与[读屏记录](llm-learning-redesign/SCREEN-READER-REVIEW.md)实机完成，保留结果 |
| N10 / K1–K5 教学验收 | 缺真实初学者全程记录；K1/K2 题包存在，但学习结果未知 | 保留 T05 至少三人试读、T10 及新版至少六人/至少五人各自独立通过要求；不能由 agent 填写或拼接不同人的阶段成绩 |
| 独立验证工具 | `task_verify` 无可执行的项目基线，本批也无可调用工具 | 由实际可用的工具及有效基线完成后再改状态；目前为 unverified，绿色 CI 不替代它 |

## 继续入口

执行顺序见[当前计划](PLAN.md)，完整硬判据见[逐项验收](llm-learning-redesign/ACCEPTANCE.md)。本批提交、生成文件哈希、检查数量和发布证据在[本批记录](llm-learning-redesign/IMPLEMENTATION-02.md)登记。历史证据保持原样，不用旧成品哈希或上一批 CI 代表新版本。
