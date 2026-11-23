# 附录 A：命令与运行目录

<!-- block: orca-apxa.b-opening -->
这一篇把第 1–11 章用到的路径与命令收成一张表，方便排查时照着敲。

## A.1 安装根

Windows 发布版的安装根是 `%LOCALAPPDATA%\Programs\orca`。卸载项记录在 `HKCU\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\{GUID}`，其中 `DisplayVersion`、`DisplayIcon`、`UninstallString` 三个值可以直接读出版本与路径。

| 条目 | 值（示例机） | 说明 |
| --- | --- | --- |
| `DisplayVersion` | `1.4.269` | 与 `app.asar` 内版本一致 |
| `DisplayIcon` | `…\Programs\orca\Orca.exe,0` | 桌面应用主程序 |
| `UninstallString` | `…\Programs\orca\Uninstall Orca.exe /currentuser` | 用户级安装 |

`resources/` 是判断版本的权威位置：`app.asar` 里打包了桌面端的 `package.json`，`app-update.yml` 说明了更新来源。后者在本机的内容是 `owner: stablyai`、`repo: orca`、`provider: github`、`releaseType: draft`、`updaterCacheDirName: orca-updater`、`publisherName: SignPath Foundation`。

## A.2 命令行命令组

`orca --help` 在本机 1.4.269 里的分组远不止这些；下表按原文顺序摘引第 1–11 章用到的 18 组：

| 分组 | 命令 | 用途 |
| --- | --- | --- |
| Startup | `open`、`serve`、`status` | 启动、无界面运行、自检 |
| Diagnostics | `diagnostics memory` | 采集内存快照 |
| Agent Discovery | `agent-context` | 打印给 Agent 用的命令 schema（第 8 章） |
| References | `reference list/add/remove/find` | 关联评审与议题（第 8 章读了两条） |
| Agent Sessions | `search` | 在某个 host 上全文检索会话（第 8 章） |
| Accounts | `account add/list/select/rm` | 托管账号 |
| Skills | `skills installed/share/list/get/install/update` | 技能安装与分发（第 3 章读文本，第 9 章补 JSON 与来源分类） |
| Artifacts | `artifacts` | 共享产物的发布与更新（第 9 章读 `list`） |
| Hosts | `host name/list/rm` | 可目标机器与它们的寻址（第 6 章） |
| Environments | `environment add/list/show/rm`、`status/update/rollback/recover/stop/forget/cancel-stop` | 远端运行时、配对码与托管服务器（第 6 章） |
| Plugins | `plugin create/types/validate/inspect/release-entry/test/check/list/logs` | 插件开发与校验（第 9 章读 `list`/`logs`） |
| Automations | `automations list/show/create/edit/remove/run/runs` | 定时任务与运行历史（第 9 章读 `list`/`runs`/`show`） |
| Projects | `project list/setups/setup-existing-folder/setup-clone/setup-create/setup-update/setup-delete` | 项目与 host 准备的登记；工作树基址参数在 `setup-create`（第 9 章读 `list`/`setups`） |
| Repos | `repo list/add/show/set/hide/unhide/set-base-ref/search-refs` | 仓库登记与默认基点 |
| Worktrees | `worktree list/show/activate/current/create/set/rm/ps`、`ports` | 工作树的登记、创建与观测（第 2、4 章；第 10 章补 create/rm 的受控闭环；第 11 章补 --setup 四档与 rm 的三道闸门） |
| Workspace Cleanup | `workspace cleanup preview/run/report` | 清理规则的预览、执行与历史（第 7 章读，第 10 章执行 run） |
| Agents | `agent launch/installed/list/show/read/hooks`、`claude-teams` | 在 worktree 里启动与观察 agent（第 8 章补 show/read；第 10 章拨 hooks off/on 一回） |
| Orchestration | `orchestration run-create/run-use/run-current/run-list/run-show`、`send/reply/check/inbox/ask`、`task-*`、`worker-*`、`gate-*`、`dispatch`、`deny`、`reset` | 编排的 Run、任务、worker 与消息；31 条子命令，2 条已 Retired（第 5 章） |

其余分组（Terminals 与 Environment Recipes 到 Browser Automation 等）十章未展开，需要时照帮助全文查。

这张表的用处不是背命令，而是判断一个说法属于哪一层：`skills` 与 `plugin` 是两组命令，前者分发技能，后者开发插件，不要混用。

## A.3 自检命令

```powershell
$orca = "$env:LOCALAPPDATA\Programs\orca\resources\bin\orca.exe"
& $orca --version
& $orca status
```

`--version` 输出一行版本号，退出码 `0`。`status` 输出八行键值，退出码同样为 `0`，其中 `appRunning`、`runtimeReachable`、`runtimeConnectionState`、`graphState` 四个字段是判断依据。`pid` 与 `runtimeId` 是本机进程的标识，不是配置项。

`orca.cmd` 与 `orca.exe` 不要混用：前者只是包装，遇到 `orchestration send` 或 `orchestration reply` 会以退出码 `2` 拒绝转发（`resources/win32/bin/orca.cmd:11-21`）。

## A.4 本篇的边界

macOS 的 app bundle 与 Linux 的包路径没有实测。第 7 章之前，`Diagnostics`、`Accounts`、`Workspace Cleanup` 与 `Agents` 各组只读到帮助文本；第 7 章补了 `diagnostics memory`、`account list`、`agent hooks status`、`agent installed`、`agent list`、`ports`、`workspace cleanup preview` 与 `workspace cleanup report` 的只读实测，`account add/select/rm` 仍未执行。`Repos` 与 `Worktrees` 执行了只读子命令，见第 2 章；第 4 章补了 `worktree current` 的负观测与 `worktree ps` 的输出形状，`ports` 的观测挪到第 7 章（E46）；第 8 章补了 `agent show`、`agent read`、`search`（含 `--index-status`）、`reference list`、`reference find` 与 `agent-context` 的只读实测；`search` 的翻页与过滤、`reference` 的真实挂接、chat 类会话的读法仍未执行。第 9 章补了 `skills list/get/installed`、`plugin list/logs`、`artifacts list`、`automations list/runs/show` 与 `project list/setups` 的只读实测；五组的写侧（`skills install/share`、`plugin install/enable`、`artifacts share`、`automations create`、`project setup-*`）仍未执行。第 10 章第一次动真状态：`worktree create`/`rm` 的探针闭环（`--delete-branch`，四路核验零残留）、`workspace cleanup run` 两次（规则全关、`counts` 全 0）与 `agent hooks off/on` 一回（末态与基线逐字段一致），全部做完即还原，见附录 C.2。`Orchestration` 执行了只读子命令（`run-list`、`run-show`、`run-current`、`inbox`、`check --peek`、`task-list`/`gate-list` 的负观测、`worker-list`），见第 5 章，写命令未执行。`Hosts` 与 `Environments` 在第 6 章执行了 `host list`、`host name`、`environment list` 与四条选择器拒绝的只读观测；`environment status` 只跑到 `--environment local` 的拒绝、`environment add` 只跑到缺参校验。`host rm`、`environment rm` 与 `update/rollback/recover/stop/forget/cancel-stop` 未执行。上表的分组名与命令名来自本机 `orca --help` 的输出，随时可能随版本调整，排查时以你在本机看到的为准；主帮助只列各组摘要，`orca host --help` 与 `orca environment --help` 才是组内全集。
