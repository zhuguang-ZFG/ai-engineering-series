# 附录 A 命令行参数速查

写作钉：`pi/1.5.0`。**以你本机的 `pi --help` 为准**；扩展会注册额外旗标，本书不重复列出。

## A.1 用法与子命令

```text
pi [options] [--] [@files...] [messages...]
pi install <source> [-l]
pi remove <source> [-l]
pi uninstall <source> [-l]
pi update [target]
pi list
pi config [-l]
pi auth <check|print-api-key|print-bearer-token>
pi mcp <add|remove|list|login|logout>
```

## A.2 输出与模式

| 参数 | 说明 |
| --- | --- |
| `-p`, `--print` | 跑完提示，把最终助手文本写 stdout 后退出 |
| `--mode text` | 文本输出；stdin/stdout 是终端时仍开 TUI |
| `--mode json` | 输出 JSONL 事件后退出 |
| `--mode rpc` | stdin 读命令、stdout 写响应/事件，常驻 |
| `--export <file> [output]` | 把会话导出为 HTML 并退出 |
| `--verbose` | 强制详细启动输出（覆盖 quietStartup） |

## A.3 模型与推理

| 参数 | 说明 |
| --- | --- |
| `--provider <name>` | 限定 `--model` 的查找范围；必须与 `--model` 同用 |
| `--model <pattern>` | 按 ID 或模糊名选模型；支持 `provider/id` 与 `:<thinking>` |
| `--api-key <key>` | 本次运行的非持久 key；需要已选模型 |
| `--thinking <level>` | `off`/`minimal`/`low`/`medium`/`high`/`xhigh`/`max` |
| `--models <patterns>` | 启动与循环用的模型范围（逗号分隔、支持 glob） |
| `--list-models [search]` | 列出可用模型（可模糊过滤）后退出 |

## A.4 会话

| 参数 | 说明 |
| --- | --- |
| `-c`, `--continue` | 继续**当前目录**最近一次会话 |
| `-r`, `--resume` | 打开会话选择器 |
| `--session <path\|id>` | 按文件路径或完整/部分 ID 打开会话 |
| `--session-id <id>` | 使用/创建当前目录下一个指定 ID 的会话 |
| `--fork <path\|id>` | 把某会话 fork 到当前目录 |
| `--session-dir <dir>` | 会话存储目录 |
| `--no-session` | 不保存会话 |
| `-n`, `--name <name>` | 设置会话显示名 |

## A.5 工具与资源

| 参数 | 说明 |
| --- | --- |
| `-nt`, `--no-tools` | 关闭所有内置/扩展/自定义/MCP 工具 |
| `-nbt`, `--no-builtin-tools` | 只关内置工具，保留扩展/自定义工具 |
| `-t`, `--tools <list>` | 允许列表；纯名字替换默认集，也可用 `+name`/`-name` 增删（两者不能混） |
| `-xt`, `--exclude-tools <list>` | 禁用的工具名/模式 |
| `-e`, `--extension <path>` | 加载扩展文件/目录或 `builtin:<name>`，可重复 |
| `-ne`, `--no-extensions` | 关闭自动发现与内置扩展（显式 `-e` 仍加载） |
| `--no-mcp` | 关闭内置 MCP 支持 |
| `--skill <path>` / `-ns`, `--no-skills` | 加载 / 关闭技能 |
| `--prompt-template <path>` / `-np`, `--no-prompt-templates` | 加载 / 关闭提示模板 |
| `--theme <path>` / `--use-theme <name[/name]>` / `--no-themes` | 主题资源 |
| `-nc`, `--no-context-files` | 不加载 `AGENTS.md` / `CLAUDE.md` |

## A.6 提示与进程

| 参数 | 说明 |
| --- | --- |
| `--system-prompt <text>` | 覆盖默认系统提示 |
| `--append-system-prompt <text>` | 追加文本或文件内容（可重复） |
| `--tui-mode <fullscreen\|regular>` | 终端界面模式 |
| `-a`, `--approve` / `-na`, `--no-approve` | 本次运行信任/不信任项目资源 |
| `--offline` | 关闭启动网络操作（同 `PI_OFFLINE=1`） |

## A.7 校验过的错误行为

| 命令 | 输出 | 退出码 |
| --- | --- | --- |
| `pi --nope` | `Error: Unknown option: --nope` | 1 |
| `pi --model`（漏值） | `Error: Unknown option: --model` | 1 |
| `pi --provider nvidia "hi"` | `Error: --provider requires --model` | 1 |
| `pi --tools read,+bash ...` | `Error: --tools: tool names cannot be mixed with +name or -name entries` | 1 |
| `pi --list-models zzzz` | `No models matching "zzzz"` | **0** |

**记住最后一行**：目录查询的"没找到"不是错误。
