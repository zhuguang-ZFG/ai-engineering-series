# 附录 B：配置与源码导航

<!-- block: orca-apxb.b-opening -->
这一篇按「你要找的东西」分组，给出去处；不按目录名的字母顺序排。

## B.1 仓库顶层

公开提交 `c354ab3` 的根目录里，与阅读顺序相关的是这几项：

| 路径 | 里面是什么 | 什么时候去 |
| --- | --- | --- |
| `src/` | Electron 主进程、渲染层与工作区实现 | 查行为时最先看 |
| `src/cli/specs/` | 各命令组的参数与输出形状，编排面是 `orchestration*.ts` 四份 | 查命令的进出与字段时看（第 5 章） |
| `native/` | 平台相关的原生模块与工作区包 | 查 Windows 通知、注册表、安全 |
| `resources/` | 打包进安装产物的资源与 `win32/bin` 启动器 | 查命令行护栏与随包技能 |
| `cloud/` | 云端组件 | 查远端运行时与账号 |
| `mobile/` | 移动端 | 查配对与通知 |
| `docs/` | 文档站源文件 | 查官方说法 |
| `skills/`、`skill-guides/`、`skill-stubs/` | 随包技能与其指南、桩 | 查 `skills` 命令的素材 |
| `config/` | 仓库自用的脚本与配置 | 查开发流程，不是产品配置 |
| `tests/`、`examples/` | 测试与示例 | 复现时参考 |

`pnpm-workspace.yaml` 显式列出了 Windows 原生工作区（`native/windows-notifications`、`native/windows-registry`、`native/windows-security`）与 `src/packages/*`（`pnpm-workspace.yaml:5-8`）。文件开头的注释说明了为什么要显式列出：`file:` 依赖在 Windows 上重链接时，虚拟存储的变动会与 node-gyp 抢跑，把 `@vscode/windows-process-tree` 的 `binding.gyp` 删掉（`pnpm-workspace.yaml:2-3`）。

## B.2 运行时（orcad）

运行时的源码集中在两处：

- `src/main/orcad/`：`orcad-connector.ts`、`orcad-relay.ts`、`orcad-served-profile.ts`、`orcad-orca-account.ts`
- `src/main/wsl/orcad/`：`wsl-orcad-watch.ts`、`wsl-orcad-deploy.ts`、`wsl-orcad-incumbent.ts`

另有 `src/main/node-runtime/orcad-cache-path.ts` 管缓存路径。安装目录里 `relay/wsl/` 的存在与 `wsl-orcad-deploy.ts` 这一层对得上；`orcad-template/` 下的 worker 入口（`agent-identity-`、`bots-db-`、`claude-conversation-fork-`、`claude-profile-setup-`、`codex-project-trust-`、`command-path-directory-`）说明运行时会按职责分进程。

## B.3 两个容易误认的配置文件

仓库根有两个看名字像产品配置的文件，它们其实是仓库自用的：

| 文件 | 内容 | 它服务于 |
| --- | --- | --- |
| `.mcp.json` | 一个 `orca-component-fixtures` 服务，命令是 `node config/scripts/component-fixtures/fixtures-mcp-server.mjs`（`.mcp.json:1-9`） | 仓库的组件测试夹具 |
| `orca.yaml` | `scripts.setup` 两步：跑 `config/scripts/development/setup/run-internal-dev-setup.mjs`，再 `pnpm install`（`orca.yaml:1-4`） | 开发环境初始化 |

把 `.mcp.json` 当成「Orca 的 MCP 配置」会得出错误的结论：它是仓库给夹具用的，你的项目配置不在这里。

## B.4 本篇的边界

本篇只列到目录与文件名的层级，没有逐个大目录展开。`src/` 与 `cloud/` 的模块划分按文件名判断，未做调用关系分析。官方配置项的权威说明在 `docs/` 与文档站，本篇不复述。
