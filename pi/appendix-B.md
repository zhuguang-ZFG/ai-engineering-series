# 附录 B 斜杠命令与键位速查

写作钉：`pi/1.5.0`。扩展、提示模板、技能会往菜单里加命令，所以**当前会话的 `/` 菜单才是完整答案**。

## B.1 模型与设置

| 命令 | 说明 |
| --- | --- |
| `/settings` | 打开设置 |
| `/model [provider/model]` | 选模型 |
| `/thinking [level]` | 设置思考档位 |
| `/scoped-models` | 配置交互循环用的模型 |
| `/login [provider]` / `/logout` | 添加 / 移除凭据 |
| `/llama` | 管理 llama.cpp router 上的模型 |

## B.2 会话与上下文

| 命令 | 说明 |
| --- | --- |
| `/new` | 新会话 |
| `/resume` | 恢复另一个会话 |
| `/name [name]` | 设置/查看会话名 |
| `/session` | 当前会话信息与统计 |
| `/tree` | 在会话树里移动 |
| `/fork` | 从某条用户消息建新会话 |
| `/clone` | 复制当前会话到当前位置 |
| `/compact [instructions]` | 压缩上下文（可带指令） |
| `/import <path>` | 导入 JSONL 会话（保留 ID 与 cwd） |

## B.3 导出与分享

| 命令 | 说明 |
| --- | --- |
| `/copy` | 复制最后一条助手消息 |
| `/export [path]` | 导出 HTML 或 JSONL |
| `/share` | 上传会话并返回查看链接（先审查内容） |
| `/bug [description]` | 准备给开发者的私有报告 |

## B.4 运行时与项目

| 命令 | 说明 |
| --- | --- |
| `/trust` | 保存项目信任决定 |
| `/mcp` | 管理 MCP 服务器（登录、重连、开关、暴露方式） |
| `/reload` | 重载键位、扩展、技能、模板、主题、上下文文件 |
| `/hotkeys` | 显示当前生效的快捷键 |
| `/changelog` | 查看更新日志 |
| `/quit` | 退出 |

`/purge` 不是内置命令，只在加载 pi-purge 扩展后出现。本文固定的 0.2.1 支持 `on`、`off`、`status`、`mode`、`source`；README 提到的 `reload` 子命令尚未实现。完整操作与版本差异见第 18 章。不要把宿主 `/reload` 与 `/purge reload` 混为一谈。

## B.5 快捷键：默认与自定义

- 交互常用：`Enter` 发送、`Shift+Enter` 换行、`Ctrl+O` 展开工具输出、`Ctrl+T` 切换 thinking、
  `Ctrl+P` 循环模型、`Ctrl+L` 打开模型选择、`Shift+Tab` 循环档位、`Ctrl+X` 复制、
  `Alt+Enter` 追加后续、`Alt+Up` 撤回队列、`Escape` 中止。
- 自定义在 `<agent-dir>/keybindings.json`（默认 `~/.pi/agent/keybindings.json`）：

```json
{
  "$schema": "https://pi.dev/schemas/keybindings.schema.json",
  "app.session.new": "ctrl+shift+n",
  "app.session.tree": ["ctrl+shift+t", "alt+shift+t"]
}
```

- 键位写法：`modifier+key`；修饰键 `ctrl`、`shift`、`alt`、`super`，可组合。
  键名支持字母、数字、`escape`、`enter`、`tab`、方向键、`f1`-`f12` 与常见符号。
- 空列表可禁用某个动作：`{"tui.altScreen.pageUp": []}`。
- 改完 `/reload`。`super` 需要终端支持 Kitty 键盘协议，不支持时报不出这个修饰键。

动作名（如 `app.session.new`、`app.session.tree`）以 `docs/keybindings.md` 的 Actions 一节为准。
