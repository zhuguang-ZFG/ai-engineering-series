# 当前执行计划：大模型从入门到精通

更新：2026-11-08。按用户最新要求，主任务为五阶段三十章大模型课程，原《Vibe Coding 101》作为编程实践补充。用户已授权提交、推送、合并及确认 CI；本轮交付仍标为技术试读版，不把未通过的能力门改记完成。

## 当前进度与下一步

逐项已完成和未完成范围以 [STATUS.md](STATUS.md) 为入口，教学/真实运行判据保持在 [ACCEPTANCE.md](llm-learning-redesign/ACCEPTANCE.md)。

1. 完成本批入口与教材修订：主入口恢复五阶段路线，C13/C15/C17 对齐实际助手模式，C30 包自检拒绝缺哈希、越界路径与篡改，纳入此前遗留的 `scan_deai.py` 修改。
2. 核对真实模型完整八题复跑的首次结果，保留失败，不以代码测试通过代替 K3 模型质量。
3. 从同一源码重建网页、正文/答案及旧实验书；完成适用单元、构建、链接、布局、键盘及 EPUBCheck，并保存本批证据。
4. 按既有授权提交、推送、合并；确认 PR 与合并后的 main CI，更新本地 main，检查工作树。
5. 后续按 N05–N10 推进质量修复、工程全章实跑、陌生项目及真人验收。具体缺口与下一项检查见 [STATUS.md](STATUS.md)，不能因本批发布而关闭。

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
