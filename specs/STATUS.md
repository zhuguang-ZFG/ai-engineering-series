# 大模型：从入门到精通 · 实际进度

更新：2026-11-10。按用户最新要求，主线为五阶段三十章：会使用 → 懂原理 → 能实现 → 会改进 → 独立交付。这里的“精通”对应五道能力门，不承诺读完即可掌握基础模型研究的所有领域。原《Vibe Coding 101》保留为编程实践补充。

**当前是技术试读版，完整 spec 尚未完成。** 三十章、分离答案、真实模型/训练/OCR 示例和网页/PDF/EPUB 已实现；程序能运行、构建通过与读者能独立完成课程是不同证据。

## 已有成果

| 范围 | 实际完成 | 证据 |
| --- | --- | --- |
| N00/N02–N04 内容与结构 | 三十章、三十份答案、五阶段先修路线；保留十二课实验和旧链接 | [课程](../exports/llm/course.html)、[知识映射](llm-learning-redesign/KNOWLEDGE-MAP.md) |
| N01/N05 真实应用 | 本地真实推理、embedding、资料权限、引用校验、有限工具与服务；失败显式返回 | [助手说明](../book/llm/examples/assistant/README.md)、[实现记录](llm-learning-redesign/IMPLEMENTATION.md) |
| N06 冻结评测 / 1.5B 复测 | 原八题完整跑完：copy 4/8，extract 修前/修后均 5/8；专用系统提示消除格式合同冲突，未测得质量提升，K3 仍失败 | [本批完整对照](../book/llm/examples/assistant/EVALUATION-04.md)；此前未完成尝试和 0.5B 结果保留，不混计 |
| N07 小模型训练 / K4 技术 | 干净环境默认 400 步训练、各 120 步全量 SFT/LoRA；69,760 底座/6,600 适配参数；留出、冻结、重载、掩码故障、分组泄漏和错误教师均有记录 | [K4 技术证据](llm-learning-redesign/K4-TECHNICAL-04.md)；独立阶段验收仍待完成 |
| N08 图像与交付教学 | 干净环境 OCR 依赖已修复，识别及失败边界实跑；38 包 wheel 哈希锁、发布目录构建/校验/切换及真实服务回退完成；已知查询回滚前后均格式失败，就绪未通过 | [OCR](../book/llm/examples/ocr/README.md)、[交付工具](../book/llm/examples/delivery/README.md)、[最终环境](llm-learning-redesign/evidence/quality-04-environment.json)、[就绪实测](llm-learning-redesign/evidence/quality-04-delivery-readiness.json) |
| 主线与工程修订 | 恢复大模型主入口；C13/C15/C17 对齐实际抽取字段与限制；C30 修复包校验；完成扫描脚本及回归检查，已合并 | [迭代02](llm-learning-redesign/IMPLEMENTATION-02.md)、[PR #10](https://github.com/zhuguang-ZFG/vibe-coding-101-course/pull/10)、[main CI](https://github.com/zhuguang-ZFG/vibe-coding-101-course/actions/runs/42492449772) |
| 上批抽取位置与对照 | source-extract/2 精确字符位置；0.5B 完整八题 copy/extract 均 4/8；C13/C14/C16/C17 修订；已合并为 327dd33 | [迭代03](llm-learning-redesign/IMPLEMENTATION-03.md)、[PR #11](https://github.com/zhuguang-ZFG/vibe-coding-101-course/pull/11)、[main CI](https://github.com/zhuguang-ZFG/vibe-coding-101-course/actions/runs/42503813403) |
| 本批章节审校 | C11–C30 已有覆盖表；20 条本地模型命令、6 轮评测共 41 个用例执行及 HTTP/回滚实测完成；修正八章工程与说明错误，所有模型失败保留 | [实跑审校表](llm-learning-redesign/CHAPTER-RUN-04.md)、[章节原始结果](llm-learning-redesign/evidence/quality-04-chapter-models.json)、[迭代04](llm-learning-redesign/IMPLEMENTATION-04.md) |
| 本批正文审校 | 去 AI 味按校准实修（客服腔/高频词清零、4 处整句装饰粗体解开，扫描 122 → 116，保留功能性强调）；c11–c30 共 27 处图补齐图注并清理 alt 内部编号，构建后为 figure/figcaption；`vectors.md`/`generation.md` 两处措辞；全部门禁通过 | `design/system/scan_deai.py` 复扫、`npm test`、`check:reading:llm`、`check:accessibility:llm`；电子书重导并重绑 EPUBCheck；`llm-course.epub`/`llm-course-answers.epub` 官方 EPUBCheck 5.3.0 零错误零警告，结果登记在 [llm-course-epubcheck.json](../deliverables/llm-course-epubcheck.json)、[llm-course-answers-epubcheck.json](../deliverables/llm-course-answers-epubcheck.json)；已随 [PR #13](https://github.com/zhuguang-ZFG/vibe-coding-101-course/pull/13) 合并为 `ded8491`，[main CI](https://github.com/zhuguang-ZFG/vibe-coding-101-course/actions/runs/42777133014) 通过 |
| 本批动画教学图 | 7 张课文流程图（工具回执环、检索取回、上下文选择、方案选择、材料到交付、评测三分、梯度步）加 SMIL 错峰高亮逐步巡访；底图完整，EPUB/打印静态可读；动画经生成器产出，`--check` 字节比对覆盖；截图实证高亮巡步；本批待提交合并，merge 证据登记在 PR 正文 | `stepTour`（mechanism-art.mjs）、Playwright 截图（tmp/anim-proof.png）；`npm test`、`check:reading:llm`、`check:accessibility:llm` 通过；三书 EPUBCheck 5.3.0 重绑零错误零警告 |
| 原书上一批发布 | 原书结构/阅读修订及机制图已合并，本地 main 同步至 `80d0513`；这是上一批证据 | [PR #9](https://github.com/zhuguang-ZFG/vibe-coding-101-course/pull/9)、[main CI](https://github.com/zhuguang-ZFG/vibe-coding-101-course/actions/runs/42489349958) |

## 尚未完成的 spec

| 项目 | 具体缺口 | 下一项可验收工作 |
| --- | --- | --- |
| N05 / K3 模型质量 | 默认模式仍有 JSON 格式、引用转述、冲突漏检和工具失败；C20 模型受资料注入影响，错误调用被工具边界阻止；已知查询就绪失败 | 固定原评测与预算，定位首个失败边界后只改一个因素，保留所有首次结果；不得改题或放宽证据规则求通过 |
| N05–N09 工程审校 | C11–C30 已有逐章实跑记录；可选 API、读者自选任务、部分图文来源与独立作业未完成全面审查 | 按[覆盖表](llm-learning-redesign/CHAPTER-RUN-04.md)继续补缺，不把作者命令执行或预期错误返回推广成全书正确 |
| N06/N07 / K4 整体验收 | 已汇集基线/单变量、训练适配、留出、冻结/重载、错误教师与失败证据；尚缺学习者完整阶段作业、独立讲解/复做 | 按 K4 全部判据验收独立操作者；不要求优化一定变好，不用作者技术记录替代教学结果 |
| N08 / K5 陌生项目 | 环境、OCR 和课程资料的发布/故障/回退基础已完成；回退恢复旧包但已知查询仍 HTTP 400，尚缺可用就绪、陌生项目、冻结 20 题留出与另一人独立交付 | 先解决并复测有引用的真实就绪查询，再冻结获授权陌生题材与判据，完成真实问答/引用、失败和回退；由未参与制作的人复做 |
| N09 独立阅读器与读屏 | 浏览器重排/键盘/可访问树已检查；独立阅读器正文/重排和真实读屏语音尚未通过 | 按[阅读器记录](llm-learning-redesign/READER-REVIEW.md)与[读屏记录](llm-learning-redesign/SCREEN-READER-REVIEW.md)实机完成，保留结果 |
| N10 / K1–K5 教学验收 | 缺真实初学者全程记录；K1/K2 题包存在，但学习结果未知 | 保留 T05 至少三人试读、T10 及新版至少六人/至少五人各自独立通过要求；不能由 agent 填写或拼接不同人的阶段成绩 |
| 独立验证工具 | `task_verify` 无可执行的项目基线，本批也无可调用工具 | 由实际可用的工具及有效基线完成后再改状态；目前为 unverified，绿色 CI 不替代它 |

## 继续入口

执行顺序见[当前计划](PLAN.md)，完整硬判据见[逐项验收](llm-learning-redesign/ACCEPTANCE.md)。本批结果在[迭代04](llm-learning-redesign/IMPLEMENTATION-04.md)登记。历史证据保持原样，不用旧成品哈希或上一批 CI 代表新版本。
