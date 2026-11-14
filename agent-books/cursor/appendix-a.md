# 附录 A：命令与文件位置

<!-- block: cursor-apxa.b-opening -->
Cursor CLI 装出来的命令叫 `agent`，配置与规则分散在两个目录里；这张表把入口和落点对齐。

## A.1 安装与核对

```bash
curl https://cursor.com/install -fsS | bash          # macOS / Linux / WSL
```

```powershell
irm 'https://cursor.com/install?win32=true' | iex    # Windows PowerShell
```

安装后核对入口，不核对版本号：

```bash
command -v agent
agent --help
agent about
```

`agent about` 显示版本、系统与账号信息（`https://cursor.com/docs/cli/reference/parameters`，访问日期 2026-11-13）。本书不写具体版本号：文档不发布可引用的版本编号，写死的数字很快过期。

## A.2 主要子命令

| 命令 | 作用 |
| --- | --- |
| `agent` | 进入交互模式 |
| `agent -p "…"` | 非交互，回答打印到 stdout |
| `agent ls` | 列出历史会话并选一个继续 |
| `agent --resume [chatId]` | 继续指定会话 |
| `agent --continue` | 继续上一个会话 |
| `agent create-chat` | 新建空会话并返回 id |
| `agent mcp list` | 列出已配置的 MCP 服务器与状态 |
| `agent update` | 升级 CLI |
| `agent acp` | 启动 ACP 服务模式（默认帮助里隐藏） |

## A.3 文件位置

| 路径 | 内容 | 能否按项目覆盖 |
| --- | --- | --- |
| `~/.cursor/cli-config.json` | 全局设置与权限 | 只有权限能在项目里加 |
| `<project>/.cursor/cli.json` | 项目级权限 | 本身即覆盖层 |
| `<project>/.cursor/rules/*.mdc` | 项目规则 | 随仓库走 |
| `~/.cursor/worktrees/<repo>/<name>` | `-w` 建出的 worktree | — |

Windows 上全局配置在 `$env:USERPROFILE\.cursor\cli-config.json`；`CURSOR_CONFIG_DIR` 可整体改目录，Linux 上 `XDG_CONFIG_HOME` 也生效。

## A.4 会改环境的命令

`agent update` 升级 CLI 本体；`agent install-shell-integration` 往 `~/.zshrc` 写一段 shell 集成，`uninstall-shell-integration` 反向移除。三条都会改你的机器，跑之前先看清楚。

`agent --force` 与 `agent --yolo` 是同一个开关。团队管理员关掉 Run Everything 后，带 `--force` 的运行会在发出提示词之前直接报错退出。
