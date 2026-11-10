# 当前执行计划：大模型从入门到精通

更新：2026-11-10。按用户最新要求，主任务为五阶段三十章大模型课程，原《Vibe Coding 101》作为编程实践补充。用户已授权提交、推送、合并及确认 CI；本轮交付仍标为技术试读版，不把未通过的能力门改记完成。

本批正文审校（去 AI 味、图注补齐、可读性）：按 REVIEW.md 校准选择性去 AI 味——保留功能性粗体与真辨析句，实修客服腔/AI 高频词清零、解开 4 处整句装饰粗体，扫描缺陷 122 → 116；为 c11–c30 的 27 处无注图按 c01–c10 房规补 `*图：…*` 图注并清理 alt 中的 `G##` 内部编号，构建后全部成为 `<figure class="curriculum-figure"><figcaption>`（网页/PDF/EPUB 同步）；另修 `vectors.md`、`generation.md` 两处措辞。只改 `book/llm/lessons/*.md`，未动测试/runner/扫描政策；`npm test`、`check:reading:llm`、`check:accessibility:llm` 通过，电子书已重导并重绑 EPUBCheck。已随 [PR #13](https://github.com/zhuguang-ZFG/vibe-coding-101-course/pull/13) 合并为 `ded8491`，[main CI](https://github.com/zhuguang-ZFG/vibe-coding-101-course/actions/runs/42777133014) 通过。

本批 K3 provider/模型栈试验（非隔离单变量）：按冻结清单的"复制并提升版本"流程新建 `eval-manifest-api.json`（问题/期望/预算逐字一致，仅四个生成用例加 provider=api），把生成侧从本地 1.5B 换成唯一可调用的更强授权模型（NVIDIA NIM mistral-large-4）。结果 4/4 生成用例 generation-failed，但逐例失败不均一：2 例读超时、2 例内容非字符串（其中 agent-calculator 的首次工具请求完全符合合同）；且本地→API 同时引入 prompt 计量（字符近似×2）与 response_format 两项栈差异，归因不能收窄到模型单一因素。192-token 复演探针（finish=length、content=null，512-token 探针正常）仅作辅助证据。凭证可用性全表、逐例事实与三种下一步隔离方案见 [EVALUATION-05](../../../book/llm/examples/assistant/EVALUATION-05.md)；"更强模型⇒K3 通过"证伪，K3 继续失败，四边界用例保持绿色。剩余未识别网关需操作者指明端点后再试。已随 [PR #15](https://github.com/zhuguang-ZFG/vibe-coding-101-course/pull/15) 合并为 `ea344de`，[main CI](https://github.com/zhuguang-ZFG/vibe-coding-101-course/actions/runs/42784424640) 通过。

本批动画教学图：给 c11–c30 课文引用的 7 张流程图（tool-execution-loop、retrieve-then-answer、context-selection、choose-an-approach、materials-to-result、evaluation-split、gradient-step）在生成器中加入 SMIL 错峰高亮——绿色描边逐步巡访步骤、循环播放；底图始终完整，EPUB/打印/无 SMIL 读者看到静态全图。共享帮手 `stepTour` 在 `mechanism-art.mjs`，动画只进生成器（`--check` 字节比对），网页/PDF/EPUB 同步重导；`npm test`、`check:reading:llm`、`check:accessibility:llm` 通过，三本书 EPUBCheck 5.3.0 重绑零错误零警告。本批待提交合并，merge 证据在 PR 正文登记，不再另推登记提交。

## 当前进度与下一步

逐项已完成和未完成范围以 [STATUS.md](STATUS.md) 为入口，教学/真实运行判据保持在 [ACCEPTANCE.md](llm-learning-redesign/ACCEPTANCE.md)。

本批完成原 1.5B 八题复测：copy 4/8、extract 修前/修后均 5/8。extract 专用系统提示消除格式合同冲突，未测得质量提升。C11–C30 逐章覆盖、20 条本地模型命令、6 轮评测共 41 个用例执行、K4 默认训练/适配与边界、38 包干净环境及 OCR 依赖修正、发布包校验/选择/回退见[迭代04](llm-learning-redesign/IMPLEMENTATION-04.md)。真实已知查询在回滚前后均 HTTP 400，模型就绪仍失败；K1–K5 整体仍未通过。

1. 继续处理 N05 模型质量：格式围栏、原文改写、冲突条件遗漏与错误工具动作仍未解决。固定原问题/模型/预算，每次只改一个因素；不得为了通过剥围栏、放宽引用或改原八题预期。采用本批提示修正只代表合同一致，不代表质量提升。
2. 按 [C11–C30 覆盖表](llm-learning-redesign/CHAPTER-RUN-04.md)补齐未覆盖命令分支、图文来源、读者自选材料和独立作业；实际模型失败继续列出，不用命令退出码 0 关闭质量缺口。
3. 用 [K4 证据](llm-learning-redesign/K4-TECHNICAL-04.md)组织完整独立作业/讲解。K5 先解决并复测本批失败的有引用就绪查询，再冻结获授权陌生题材与 20 题判据，复用已交付的环境锁和发布工具，完成真实问答、留出、就绪和回退，再由另一人独立复做。课程内置材料不算陌生项目。
4. 独立阅读器、实际读屏与 K1–K5 真人验收继续保留；逐项条件见 [STATUS.md](STATUS.md)。

上一批精确引用与 0.5B 对照已随 [PR #11](https://github.com/zhuguang-ZFG/vibe-coding-101-course/pull/11) 合并为 `327dd33`，[main CI](https://github.com/zhuguang-ZFG/vibe-coding-101-course/actions/runs/42503813403) 通过；此前遗留扫描脚本已随 PR #10 完成。历史结果不替代本批检查。

## 复核命令

```text
npm run build:llm
npm run export:books:llm
python scripts/llm/check_epub.py --jar <EPUBCheck-5.3.0/epubcheck.jar>
npm test
npm run check:reading:book
npm run check:accessibility:llm
npm run check:reading:llm
```

新版正文和答案 EPUB 还需分别运行官方 EPUBCheck。代码、教材或生成器变更后重新绑定 sourceHash；生成 HTML/PDF/EPUB 不手改。真人、独立阅读器与实际读屏另记，不能用作者烟测替代。

## 原书历史交付

原书 195 章、八张图及阅读修订已随 [PR #9](https://github.com/zhuguang-ZFG/vibe-coding-101-course/pull/9) 合并为 `80d05130a213d15e6ef1785590ed2844ae69e702`，[main CI](https://github.com/zhuguang-ZFG/vibe-coding-101-course/actions/runs/42489349958) 通过。各批记录保留在[技术修订](original-book-review.md)、[插图](original-book-illustration-02.md)和[阅读修订](original-book-readability-03.md)。这些证据仅覆盖当时列明的章节/技术与阅读范围，不表示所有第三方 API 均已实跑，也不代表大模型 K1–K5 已通过。
