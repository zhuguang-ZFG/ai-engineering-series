# 当前执行计划：大模型从入门到精通

更新：2026-11-09。按用户最新要求，主任务为五阶段三十章大模型课程，原《Vibe Coding 101》作为编程实践补充。用户已授权提交、推送、合并及确认 CI；本轮交付仍标为技术试读版，不把未通过的能力门改记完成。

## 当前进度与下一步

逐项已完成和未完成范围以 [STATUS.md](STATUS.md) 为入口，教学/真实运行判据保持在 [ACCEPTANCE.md](llm-learning-redesign/ACCEPTANCE.md)。

本批已完成 source-extract/2 精确位置合同、提前拒绝不支持组合、原冻结八题的 0.5B 独立对照、C13/C14/C16/C17 命令修订与同源成品验证。完整八题 copy 4/8、extract 4/8；fixed 七题子集分别 4/7、4/7，K3 仍未通过。代码/运行/书籍证据见[迭代03](llm-learning-redesign/IMPLEMENTATION-03.md)，发布按用户既有授权执行。

1. 下一批先在资源允许时补完 1.5B 新版本八题复测，再处理 N05 的首个质量失败边界：保留本批完整首次响应，分别定位 JSON 格式、摘录不符、冲突遗漏与工具请求错误；固定问题/模型/预算，每次只改变一个因素。原八题硬判据不改。
2. 继续 C11–C30 全章命令与图文来源实跑审校；本批只关闭已核对的局部错误，不能推广成全章/全书验收。
3. 汇集 K4 完整阶段证据，随后冻结陌生题材任务，完成锁定环境、故障与回退演练，再进入独立复做。
4. 独立阅读器、实际读屏与 K1–K5 真人验收继续保留；逐项条件见 [STATUS.md](STATUS.md)。

上一批主入口、C30 包校验和遗留扫描脚本已随 [PR #10](https://github.com/zhuguang-ZFG/vibe-coding-101-course/pull/10) 合并为 `ab27bd1`，[main CI](https://github.com/zhuguang-ZFG/vibe-coding-101-course/actions/runs/42492449772) 通过；本地工作树当时干净。该结果不替代本批检查。

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
