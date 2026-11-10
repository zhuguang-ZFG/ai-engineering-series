# 附录 A：命令与运行目录

<!-- block: kimi-apxa.b-opening -->
CLI 命令在 shell 执行，斜杠命令在 Kimi 界面输入；运行目录和当前会话会影响它们的结果。

## A.1 书籍仓库中的离线检查

```powershell
python kimi/examples/check_inventory.py
python kimi/examples/check_inventory.py --fixed
python -m unittest discover -s kimi/examples -p "test_*.py" -v
python kimi/examples/probe_cli.py --output .scratch/kimi-cli-proof.json
```

第一条的退出码 `1` 是故意保留的业务失败；第二、三条应成功。最后一条需要真实 Kimi 可执行文件，但不发送模型提示。Python 例子使用标准库；源码组件实验需要单独的 Node 依赖，见附录 C。

## A.2 练习目录中的启动命令

| 命令 | 用途 |
| --- | --- |
| `kimi --version` | 核对版本 |
| `kimi --help` | 查看实际参数 |
| `kimi doctor` | 检查配置 |
| `kimi --continue` | 继续当前目录最近会话 |
| `kimi --session` | 交互选择会话 |
| `kimi --session ID` | 恢复指定会话 |
| `kimi --agent-file ./review-plugin/agents/inventory-reviewer.md` | 用指定角色新建会话 |
| `kimi --skills-dir ./review-plugin/skills` | 用显式技能目录启动 |
| `kimi acp` | 启动 ACP stdio 服务 |

`--agent` 与 `--agent-file` 互斥，二者也不能与恢复参数合用。`--continue` 与 `--session` 互斥。带 `ID` 的命令需要替换实际会话标识。

## A.3 终端界面的斜杠命令

| 命令 | 用途 |
| --- | --- |
| `/plugins install ./review-plugin` | 安装练习插件 |
| `/plugins info chengming-review` | 查看信息与诊断 |
| `/plugins reload` | 重读插件状态与清单 |
| `/reload` | 重新加载会话配置与扩展 |
| `/chengming-review:review inventory.py` | 触发插件审查命令 |
| `/skill:chengming-review:review-inventory` | 显式调用插件技能 |
| `/mcp` | 查看 MCP 服务状态 |
| `/sessions` | 浏览会话 |
| `/compact` | 压缩上下文 |
| `/fork` | 创建会话分叉 |

这些命令不能直接粘到 PowerShell 中执行。普通目录技能使用 `/skill:review-inventory`；安装为插件后使用带插件前缀的名字。

## A.4 书籍构建

在书籍仓库根目录执行：

```powershell
python scripts/bookctl.py build --product kimi --lang zh --pdf --epub
```

构建输出 `yuyu-kimi-zh.html`、`yuyu-kimi-zh.pdf` 和 `yuyu-kimi-zh.epub`。PDF 需要浏览器和中文字体，EPUB 检查使用 EPUBCheck。生成文件由构建器维护，不直接编辑。

依据：[固定版本命令参考](https://github.com/MoonshotAI/kimi-code/blob/1c142a007c10e881602690def96057c23a2baa12/docs/en/reference/kimi-command.md)。
