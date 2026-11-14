# 附录 A：命令与运行目录

<!-- block: grok-apxa.b-opening -->
安装、启动、无头运行和 ACP 服务各自走不同的入口，先把它们摆在同一张表里，再看每条命令会写哪些目录。

## A.1 安装与版本

官方给的是两条安装脚本，装完命令名是 `grok`：

```bash
curl -fsSL https://x.ai/cli/install.sh | bash   # macOS / Linux / Git Bash
```

```powershell
irm https://x.ai/cli/install.ps1 | iex          # Windows PowerShell
```

安装后先核对实际跑的是哪一个程序：

```bash
grok --version
grok --help
```

本书以仓库 `xai-org/grok-build` 的 `SOURCE_REV` 为准钉住源码版本，发布程序的版本号记在各版本自己的变更记录里。两者不是同一件事：`SOURCE_REV` 说明你读的是哪一份源码，`grok --version` 说明你机器上装的是哪个构建。

## A.2 从源码构建

源码是 Rust workspace，根 `Cargo.toml` 是生成文件，仓库 README 明确要求改各 crate 自己的 `Cargo.toml`：

```bash
cargo run -p xai-grok-pager-bin              # 构建并启动 TUI
cargo build -p xai-grok-pager-bin --release  # 产物 target/release/xai-grok-pager
cargo check -p xai-grok-pager-bin            # 快速校验
```

构建前需要 DotSlash 在 `PATH` 上，`bin/protoc` 靠它取到编译器；macOS 与 Linux 是受支持的构建宿主，Windows 构建按 README 的说法是尽力而为。

## A.3 三种运行形态

| 形态 | 命令 | 何时退出 |
| --- | --- | --- |
| 全屏 TUI | `grok` | 你退出 TUI |
| 无头单次 | `grok -p "提示词"` | 回答打印完 |
| ACP 服务 | `grok agent stdio` | 客户端关闭连接 |

无头模式还有 `--prompt-json` 与 `--prompt-file` 两个触发方式，以及输出格式开关；它们的完整字段见附录 B。

## A.4 会写入的目录

| 位置 | 内容 | 来源 |
| --- | --- | --- |
| `~/.grok/config.toml` | 用户配置 | 配置文档的优先级表 |
| `~/.grok/sessions/<编码后的工作目录>/<会话 id>/` | 会话记录、计划、回滚点、压缩检查点 | 会话文档的存储布局 |
| `~/.grok/docs/user-guide/` | 启动时释放的用户手册 | 配置文档开头 |

`GROK_HOME` 可以把这些根目录整体挪走；挪走之后，TUI 与无头模式读的是同一个新根。

## A.5 这本书用到的命令

```powershell
python grok/examples/check_release.py
python grok/examples/check_release.py --fixed
python -m unittest discover -s grok/examples -p "test_*.py" -v
```

第一条的退出码 `1` 是故意保留的业务失败：故障版闸门有 3 个用例与预期不符。第二、三条应当成功。三条命令都不调用模型。
