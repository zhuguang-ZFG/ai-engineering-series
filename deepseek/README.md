# DeepSeek Harness：插件化运行时

状态：已立项，当前为提纲与源码研究阶段。整书 HTML、PDF 和 EPUB 尚未生成。

研究重点：Cordis、服务依赖和可替换循环。基线：fcc0ad462172522aaf5c93a7b2e01f6b9f0b0159，提交 `fcc0ad462172522aaf5c93a7b2e01f6b9f0b0159`。[上游固定版本](https://github.com/deepseek-ai/deepseek-harness/tree/fcc0ad462172522aaf5c93a7b2e01f6b9f0b0159)，许可证 MIT，访问日期 2026-11-09。

[逐章提纲](outline.md) · [统一任务表](../docs/agent-series/tasks.json) · [来源锁文件](../docs/agent-series/sources.lock.json)

按中文分册推进，英文版尚未启动。完成正文后将复用公共构建器，生成独立的 `yuyu-deepseek-zh.html/.pdf/.epub`，最终放到主工作区 `yuyu-book/dist/`。

首轮源码入口：

- [packages/core](https://github.com/deepseek-ai/deepseek-harness/tree/fcc0ad462172522aaf5c93a7b2e01f6b9f0b0159/packages/core)
- [docs/architecture.md](https://github.com/deepseek-ai/deepseek-harness/tree/fcc0ad462172522aaf5c93a7b2e01f6b9f0b0159/docs/architecture.md)
