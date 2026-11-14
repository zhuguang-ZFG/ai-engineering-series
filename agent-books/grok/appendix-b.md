# 附录 B：配置与源码导航

<!-- block: grok-apxb.b-opening -->
配置按层级从高到低生效，`requirements.toml` 中标记 `pin` 的键可压住命令行与环境变量；源码则按目录分工。B.1 与 B.3 两张表分别记这两件事。

## B.1 配置优先级

从高到低，共七层：

| 层 | 例子 | 谁在它之上 |
| --- | --- | --- |
| 1 命令行旗标 | `--yolo`、`--model`、`--sandbox` | `requirements.toml` 中标记 `pin` 的键 |
| 2 环境变量 | `XAI_API_KEY`、`GROK_MEMORY` | 命令行；`pin` 键 |
| 3 `requirements.toml` / MDM | 组织下发的强制项 | 无更上层 |
| 4 `GROK_CONFIG` / `GROK_CONFIG_PATH` 叠加层 | 启动器注入的 JSON 或文件 | 前三层 |
| 5 `config.toml` | `~/.grok/config.toml` | 上面四层 |
| 6 `managed_config.toml` | 组织部署的默认值 | `config.toml` 及以上 |
| 7 内置默认值 | 程序自己的兜底 | 其余全部 |

配置文件这几层是从低往高合并的：`managed_config.toml` → `config.toml` → 叠加层 → `requirements.toml` / MDM。所以组织策略压得住 `config.toml`，也压得住叠加层；`pin` 键还会压住命令行与环境变量。

## B.2 两个叠加层变量

`GROK_CONFIG` 是内联 JSON，`GROK_CONFIG_PATH` 是另一个文件；两者都有时 `GROK_CONFIG` 胜。它们只覆盖自己写了的那几个键，并且受一份 allowlist 限制，只能动 `models`、`features`、收窄的 `toolset` 与 `shell_environment_policy` 的过滤字段。空值当作没设，格式坏掉会打一条警告再退回另一个变量。

白名单之外的键会被拒绝，叠加层因此不构成提权路径。

## B.3 源码导航

| 路径 | 内容 |
| --- | --- |
| `crates/codegen/xai-grok-pager-bin` | 组合根，构建 `xai-grok-pager` 可执行文件 |
| `crates/codegen/xai-grok-pager` | TUI：滚动区、提示框、弹窗、渲染 |
| `crates/codegen/xai-grok-shell` | Agent 运行时，以及 leader / stdio / headless 入口 |
| `crates/codegen/xai-grok-tools` | 工具实现（终端、文件编辑、搜索等） |
| `crates/codegen/xai-grok-workspace` | 宿主文件系统、版本控制、执行、检查点 |
| `crates/codegen/xai-chat-state` | 会话状态、压缩与历史 |

用户手册随 pager 一起发布，源码里在 `crates/codegen/xai-grok-pager/docs/user-guide/`；启动时会释放到 `~/.grok/docs/user-guide/`，所以装好的程序自己带着这份文档。

## B.4 开发命令

```bash
cargo check -p xai-grok-config   # 按 crate 校验
cargo test -p xai-grok-config    # 按 crate 测试
cargo clippy -p <crate>          # 根目录 clippy.toml 为规则
cargo fmt --all                  # 根目录 rustfmt.toml 为格式
```

README 明确建议别跑全 workspace 构建，它慢；仓库也不接受外部贡献，引用它的行为时要区分「源码这么写」与「发布版这样跑」。
