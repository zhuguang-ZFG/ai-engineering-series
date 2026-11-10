# 附录 B：命令与配置速查

<!-- block: codex-apxb.b-opening -->
先按任务选择命令，再读取固定版本帮助；会写配置、启动模型或产生外部副作用的命令需要对应的运行条件。

## B.1 只读查询与静态生成

| 命令 | 用途 | 本书执行情况 |
| --- | --- | --- |
| `codex --version` | 确认程序版本 | 已运行 |
| `codex --help` | 查看顶层入口和参数 | 已运行 |
| `codex exec --help` | 查看无人值守参数 | 已运行 |
| `codex plugin --help` | 查看插件管理命令 | 已运行 |
| `codex execpolicy check --help` | 查看规则检查参数 | 已运行 |
| `codex app-server generate-json-schema --out DIR` | 生成当前协议结构 | 已运行，322 份 JSON |

静态 schema 生成会写指定输出目录，但不会因此启动一个模型会话。把输出放在独立临时目录，避免覆盖已有手写文件。

## B.2 日常任务入口

交互启动使用 `codex`，非交互使用 `codex exec`。`resume` 延续历史，`fork` 分支历史，`-C` 指定工作目录，`--worktree` 请求托管工作树。参数组合以同版本帮助为准；本书尚未运行这些完整模型会话。

```powershell
codex.cmd -C . --sandbox read-only --ask-for-approval on-request
codex.cmd exec --json --output-last-message .scratch/result.md "检查项目测试入口"
```

运行前确认模型与认证配置可用。命令示例不包含账号凭据，也不要求在公共仓库写入密钥。需要自动化时使用受控 secret 注入，并保证失败日志不会输出完整值。

## B.3 权限相关选项

`--sandbox` 接受 `read-only`、`workspace-write` 和 `danger-full-access`。顶层 `--ask-for-approval` 接受 `on-request`、`never`。`--add-dir` 增加可写目录。`--approve-for-me` 把审批交给自动审查，帮助说明它使用 workspace-write 沙箱。

这些选项分别控制不同机制：`never` 关闭询问但不增加访问能力，`--add-dir` 增加可写范围但不改变任务授权，Hook 信任与普通工具批准也分别处理。绕过选项需要明确的外部隔离与审查条件，初次使用保持默认检查。

## B.4 exec 的输出与隔离提示

`--json` 输出事件，`--output-last-message` 保存最后答复，`--output-schema` 限制最终回答结构，`--ephemeral` 不持久保存会话文件。它们都不保证项目文件不会被工具修改。

`--ignore-user-config` 跳过用户配置文件，但帮助明确说明认证仍使用 Codex 用户目录；`--ignore-rules` 跳过用户和项目执行规则。二者都不是完整的匿名隔离模式。需要无账号检查时优先选用本书已经运行的静态子命令。

## B.5 规则文件检查

```powershell
codex.cmd execpolicy check --rules codex/examples/review.rules --pretty git diff --stat
```

返回 `matchedRules` 与可能存在的 `decision`。无匹配时省略 decision；解析错误和正反例验证失败应视为加载失败。多个规则命中取最严格值，详细机制见第 10 章。

## 来源

[固定参数定义](https://github.com/openai/codex/blob/086ccc833bc9cf01024ad2dd6af7dbd421b6bf9a/codex-rs/cli/src/main.rs)、[exec 参数](https://github.com/openai/codex/blob/086ccc833bc9cf01024ad2dd6af7dbd421b6bf9a/codex-rs/exec/src/cli.rs)、[规则契约](https://github.com/openai/codex/blob/086ccc833bc9cf01024ad2dd6af7dbd421b6bf9a/codex-rs/execpolicy/README.md)。
