# 附录 A：固定版本与源码导航
<!-- block: hermes-apxa.b-opening -->
遇到书中描述与本机不一致时，先确认正在读哪份程序。本书将 Hermes Agent 固定在 v0.23.0，对应提交 2bd378ed1b8d6bf2192cb26e0a55ff3091e6bd19。网站会继续更新，安装器也可能默认获取较新版本；它们适合查当前用法，却不能直接解释本书实验的结果。

## A.1 保存一个能重找的版本
源码来自 NousResearch/hermes-agent，许可证为 MIT。本书的原创说明和示例沿用本仓库的出版约定。引用上游代码时保留原作者及许可信息，不把上游仓库里的第三方素材一并视为可自由再发布。

```powershell
git clone https://github.com/NousResearch/hermes-agent.git hermes-agent-reference
git -C hermes-agent-reference checkout --detach 2bd378ed1b8d6bf2192cb26e0a55ff3091e6bd19
git -C hermes-agent-reference rev-parse HEAD
```

最后一行应打印上述完整提交号。tag 名字方便人交流，完整提交号方便机器重现；如果 tag 是附注标签，标签对象本身的哈希还会与提交哈希不同。记录版本时应明确保存的是 commit，不要把两者混在一列。

只读源码无需填入模型凭据。若要完整安装，按这一提交的 README 与 pyproject.toml 准备 Python 和依赖。复制当前官网的安装命令后再假定它装到了书中版本，会使后续差异很难定位。本书没有执行完整宿主安装，附录 C 说明了实际运行组件的方式。

## A.2 按一个问题选择入口
| 想弄明白的行为 | 首先读的文件 | 再追到哪里 |
| --- | --- | --- |
| 一次任务怎样进入循环 | run_agent.py | agent/agent_init.py、工具调用路径 |
| 长期记忆如何保存 | tools/memory_tool.py | tools/memory_tool_store.py |
| 本轮系统提示里为什么还是旧记忆 | agent/memory_manager.py | MemoryStore 的加载与快照 |
| 技能从哪里被发现 | agent/skill_utils.py | tools/skills_tool.py |
| 谁能改技能文件 | tools/skill_manager_tool.py | 来源目录与写入路径 |
| 插件如何加载和卸载 | hermes_cli/plugins.py | plugins_discovery.py、plugins_manifest.py |
| 工具名称如何归属 | tools/registry.py | 注册者与调用者 |
| 历史搜索为何少了某些记录 | tools/session_search_tool.py | hermes_state.py |
| 定时任务何时真正执行 | cron/jobs.py | cron/scheduler.py |
| 多平台消息如何选择会话 | gateway/session.py | 对应平台适配器 |
| 命令在哪台机器执行 | tools/terminal_tool.py | 后端创建与会话管理 |
| 子任务如何继承执行条件 | tools/delegate_tool.py | 子 Agent 的创建参数 |

不要只搜索一个类名就停止。调用参数决定这一次使用了什么默认值；返回值消费方决定错误是否真的中止流程。例如注册接口能返回一个清理句柄，只有追到宿主保存并调用句柄的地方，才能解释卸载效果。

## A.3 升级后先看哪几处差异
一次小升级也可能改掉插件发现范围、默认工具集或 memory 的错误返回结构。升级前保留旧环境与一份脱敏样本；升级后先复跑附录 C 的小实验，再用全新 profile 做一个完整任务。旧数据库迁移与旧插件兼容应单独观察，避免把所有失败都归为模型表现波动。

比较源码时，把变动分成数据格式、默认值和执行路径三类。数据格式变化影响旧文件能否读取；默认值变化影响没有显式配置的用户；执行路径变化影响相同输入会不会走到另一套工具或后端。这三类需要的回归样本并不相同。

固定来源：[完整源码树](https://github.com/NousResearch/hermes-agent/tree/2bd378ed1b8d6bf2192cb26e0a55ff3091e6bd19)、[安装说明](https://github.com/NousResearch/hermes-agent/blob/2bd378ed1b8d6bf2192cb26e0a55ff3091e6bd19/README.md)、[依赖声明](https://github.com/NousResearch/hermes-agent/blob/2bd378ed1b8d6bf2192cb26e0a55ff3091e6bd19/pyproject.toml)。
