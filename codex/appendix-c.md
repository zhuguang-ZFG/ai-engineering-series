# 附录 C：实验复现与证据边界

<!-- block: codex-apxc.b-opening -->
本册完成了固定 Windows CLI 的规则与静态协议实验；模型任务、平台沙箱和外部服务实验没有被计入已验证结果。

## C.1 实际运行范围

实验使用 Python 标准库驱动真实 `codex.exe`，明确传入规则文件。驱动只调用版本、帮助、策略检查和 schema 生成路径，没有启动代理会话，没有调用外部模型。子进程环境仅保留程序查找和 Windows 必需项，没有把模型 API key、代理或账号变量传进去。

这些子命令在钉版 CLI 中有独立分发路径：execpolicy 调用检查器，schema 生成调用协议生成函数。它们不需要创建任务线程。这个设计让本地验证可以保持范围清楚，而不是以“应该不会调用模型”作为假设。

## C.2 运行命令

```powershell
python codex/examples/check-local-cli.py --binary PATH_TO_PINNED_CODEX_EXE
```

将占位符替换为固定 0.167.0 原生程序路径，不能传 npm 的 `.cmd` 入口给这个 Python 驱动。脚本核对版本后才继续。不要使用 Python `-O`，因为脚本使用 assert 检查行为。

成功时输出结果 JSON 和 `.scratch/agent-series/codex-local-*` 证据目录。原始 schema 与帮助文本留在忽略目录，公开记录只保留必要结果、版本与摘要。脚本没有把用户路径写入公开 facts 文件。

## C.3 八项结果

两项只读 Git 前缀得到 allow，推送得到 prompt，明确的强制推送形式得到 forbidden。未列出的提交命令与绝对路径命令无匹配。故意错误的正例导致非零退出。最后生成协议 JSON，检查四个关键方法存在。八项均通过。

这些命令 token 没有被作为真实 Git 操作执行；尤其没有向远端推送。静态 schema 也没有启动 app-server 会话。结果应按这层含义阅读，不要扩展成“代理已完成代码修复”。

## C.4 哪些仍需运行

Windows、Linux、macOS 的文件和网络沙箱边界；真实模型请求到工具结果的完整链；交互审批与自动审查；Hook 实际发现、信任、执行和取消；MCP 的断线重连；resume/fork 后的实际历史与文件对照。这些内容在正文中按源码机制、官方说明或读者实验设计呈现，没有伪造通过记录。

本册正文完整并不意味着所有平台与外部服务组合都已运行。一本可维护的工程书应让读者知道哪些结论可以直接复核，哪些需要在自己的环境补测。新增证据后可以更新这一附录，保留旧记录的日期与版本。

## C.5 对照升级结果

先保留旧规则文件和 JSON 结果，再用新版本运行。比较 decision、matchedRules、退出状态与协议结构；发现差异后回到源码，确认是预期接口变化还是异常。不要直接覆盖旧 facts，否则版本变化的轨迹会丢失。

原始数据若含环境相关路径，公开之前改为相对描述，并保留脚本与输入摘要。摘要用于证明输入一致，不会替代运行结果本身；一个哈希值不能告诉你测试究竟检查了什么。

## 证据入口

[验证记录](VERIFY.md)、[示例说明](https://github.com/zhuguang-ZFG/claude-code-book/blob/main/codex/examples/README.md)、[本机脱敏结果](https://github.com/zhuguang-ZFG/claude-code-book/blob/main/codex/facts/local-cli-20261110.json)。
