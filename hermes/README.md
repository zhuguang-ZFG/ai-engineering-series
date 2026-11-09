# Hermes Agent：记忆、技能与持续任务

状态：已立项，当前为提纲与源码研究阶段。整书 HTML、PDF 和 EPUB 尚未生成。

研究重点：跨会话知识、技能维护和持续任务。基线：v0.23.0，提交 `2bd378ed1b8d6bf2192cb26e0a55ff3091e6bd19`。[上游固定版本](https://github.com/NousResearch/hermes-agent/tree/2bd378ed1b8d6bf2192cb26e0a55ff3091e6bd19)，许可证 MIT，访问日期 2026-11-09。

[逐章提纲](outline.md) · [统一任务表](../docs/agent-series/tasks.json) · [来源锁文件](../docs/agent-series/sources.lock.json)

按中文分册推进，英文版尚未启动。完成正文后将复用公共构建器，生成独立的 `yuyu-hermes-zh.html/.pdf/.epub`，最终放到主工作区 `yuyu-book/dist/`。

首轮源码入口：

- [run_agent.py](https://github.com/NousResearch/hermes-agent/tree/2bd378ed1b8d6bf2192cb26e0a55ff3091e6bd19/run_agent.py)
- [agent](https://github.com/NousResearch/hermes-agent/tree/2bd378ed1b8d6bf2192cb26e0a55ff3091e6bd19/agent)
- [tools](https://github.com/NousResearch/hermes-agent/tree/2bd378ed1b8d6bf2192cb26e0a55ff3091e6bd19/tools)
- [skills](https://github.com/NousResearch/hermes-agent/tree/2bd378ed1b8d6bf2192cb26e0a55ff3091e6bd19/skills)
- [cron](https://github.com/NousResearch/hermes-agent/tree/2bd378ed1b8d6bf2192cb26e0a55ff3091e6bd19/cron)
- [gateway](https://github.com/NousResearch/hermes-agent/tree/2bd378ed1b8d6bf2192cb26e0a55ff3091e6bd19/gateway)
- [hermes_state.py](https://github.com/NousResearch/hermes-agent/tree/2bd378ed1b8d6bf2192cb26e0a55ff3091e6bd19/hermes_state.py)
