# 附录 C：各 Agent 的能力与入口对照

<!-- block: prompt-apxc.b-opening -->
本附录把提示任务接到系列中的固定版本工具册。表中的验证来自对应分册已有记录，不表示青禾案例已经在这些工具中完成模型任务。

## C.1 按问题找入口

| 想解决的问题 | 阅读入口 | 在本册中的对应位置 |
| --- | --- | --- |
| 把重复步骤整理成 Skill | [Kimi 第 9 章](../kimi/ch09.md) | 第 12 章的可维护资源 |
| 定义只读审查角色并装配插件 | [Kimi 第 10 章](../kimi/ch10.md)、[第 11 章](../kimi/ch11.md) | 第 11–13 章的职责和任务包 |
| 核对工具权限与审批 | [OpenCode 第 7 章](../opencode/ch07.md) | 第 14 章的宿主限制 |
| 沿工具请求查看本机操作 | [Codex 第 6 章](../codex/ch06.md) | 第 10 章的动作与回执 |
| 处理长期记忆中的过期信息 | [Hermes 第 8 章](../hermes/ch08.md) | 第 6–8 章的版本和恢复 |
| 理解插件生命周期和失败清理 | [DeepSeek 实验附录](../deepseek/appendix-c.md) | 第 10、12 章的工具状态 |

每个产品的规则格式、发现路径、权限选项和会话行为，都要按链接中对应的固定版本核对。只把文件名改成相似名称，还不能算完成了迁移。

## C.2 固定版本与证据层次

| 工具册基线 | 对应册已记录的实测 | 不能据此声称完成的范围 |
| --- | --- | --- |
| OpenCode v1.19.5 | 原创处理器、固定 Windows 宿主的插件与工具权限场景；模型响应使用本地替身 | 青禾真实模型审查、其他平台和所有权限路径 |
| DeepSeek Harness 固定提交 | 原提交内 Cordis 组件的生命周期与事件场景 | 完整 dsh 应用、远端模型与操作系统沙箱 |
| Hermes v0.23.0 | 上游记忆与技能组件、原创插件离线处理器、本地资料库流程 | 完整宿主、真实模型任务、聊天平台投递 |
| Codex CLI 0.167.0 | Windows CLI 规则检查、静态协议生成及离线工程练习 | 实际模型到工具的完整任务、各平台沙箱、真实会话恢复 |
| Kimi Code 2.5.2 | 固定解析器与 Hook 组件、真实 CLI 帮助和 ACP 握手、原创库存检查 | 完整模型审查、真实 IDE 会话、全部插件安装与恢复流程 |

完整证据分别见 [OpenCode](../opencode/appendix-c.md)、[DeepSeek](../deepseek/appendix-c.md)、[Hermes](../hermes/appendix-c.md)、[Codex](../codex/appendix-c.md)、[Kimi](../kimi/appendix-c.md)。这里不把组件通过数相加成某种工具能力排名。

固定来源采用完整提交：

- [OpenCode](https://github.com/anomalyco/opencode/tree/810c0eba1a7348036f8bdf61e6632d0c36c6876c)。
- [DeepSeek Harness](https://github.com/deepseek-ai/deepseek-harness/tree/fcc0ad462172522aaf5c93a7b2e01f6b9f0b0159)。
- [Hermes](https://github.com/NousResearch/hermes-agent/tree/2bd378ed1b8d6bf2192cb26e0a55ff3091e6bd19)。
- [Codex](https://github.com/openai/codex/tree/086ccc833bc9cf01024ad2dd6af7dbd421b6bf9a)。
- [Kimi Code](https://github.com/MoonshotAI/kimi-code/tree/1c142a007c10e881602690def96057c23a2baa12)。

## C.3 在自己的环境中重新接入

先记录实际安装版本与来源，再选择一条最小的只读任务。确认材料确实读入、工具范围符合要求、响应能够原样保存，最后才运行完整题集。某个产品提供的能力与某次任务成功，是两种不同证据。

把提示迁入目标工具时，检查额外项目规则、历史记忆、工具列表和输出限制。发现必须修改的地方，另存适配版本，并按[第 17 章](ch17.md)保留原样迁移与修改后的结果。当前没有两个真实环境的青禾模型对照，不能依据这张表宣布已经跨工具兼容。
