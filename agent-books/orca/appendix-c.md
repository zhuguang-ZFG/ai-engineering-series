# 附录 C：实验记录与复现边界

<!-- block: orca-apxc.b-opening -->
本篇按实验编号记录第 1–6 章用到的每一次观测，写清命令、当时的输出与这次观测证明不了什么。

## C.1 观测表

E1–E6 的观测日期为 2026-11-22；E7–E41 为 2026-11-23。环境同为 Windows，已安装 Orca 1.4.269。

| 编号 | 做了什么 | 得到什么 | 证明范围 |
| --- | --- | --- | --- |
| E1 | `orca.exe --version` | `1.4.269`，退出码 `0` | 命令行启动器可运行，版本与安装包一致 |
| E2 | `orca.exe status` | 八行键值，退出码 `0`，`runtimeState: ready`、`runtimeReachable: true` | 本机运行时在线；不含其他机器的信息 |
| E3 | 读 `app.asar` 的 `package.json` | `name: orca`、`version: 1.4.269`、`main: ./out/main/index.js` | 桌面包自身的版本与入口 |
| E4 | 读注册表卸载项 | `DisplayVersion: 1.4.269` | 安装器记录的版本 |
| E5 | 查发布 API | `v1.4.269`，`published_at` 为 2026-11-21T17:57Z，tag 指向提交 `af41be4` | 发布 tag 存在且与安装版本同名；发布提交与本书固定的源码提交 `c354ab3` 不是同一个 |
| E6 | 读公开提交的 `package.json` | `version: 1.4.214`（`package.json:3`） | 主干版本字段落后于发布 tag |
| E7 | `orca.exe worktree current --json`（在一个 Orca 工作树目录里） | 一条登记记录，含 `identity.key`、`baseRef`、`pushTarget`、`createdWithAgent`、`workspaceStatus` 等字段 | 该工作树在 Orca 侧的登记；换一个目录结果不同 |
| E8 | `orca.exe repo list --json` | 已登记仓库的 `path`、`kind`、`upstream`、`gitRemoteIdentity`、`hookSettings` 字段 | 本机注册表的当次内容；仓库集合随时可变 |
| E9 | `git worktree list` 与 `git rev-parse --git-dir` | 主工作树一行加工作树数行；gitdir 指向 `<主仓库>/.git/worktrees/<id>` | git 层的工作树布局；不证明 Orca 字段的含义 |
| E10 | `orca.exe worktree list --json` | `hostScope`、`totalCount`、`truncated`、`worktrees`；主工作树也在列表里 | 列表层的字段名与截断标记；当次数值不可比 |
| E11 | 读 `resources/skills/current-manifest.json` | `schemaVersion: 3`、11 条技能，每条 `{name, sourcePath, packageDigest, files}`，文件条目含 `exactSha256`/`textNormalizedSha256`/`identitySha256` 三种摘要 | 随包清单的字段形状；未逐字节校验摘要 |
| E12 | 列 `%APPDATA%\orca` 与其 `agent-hooks/` 子目录 | 80 个条目（本机当次）；`agent-hooks/` 含 `endpoint.cmd`、`agent-identities.db`、`last-status.db` | 用户数据目录的落位与钩子端点文件存在；条目数随机器与时间变化 |
| E13 | 列 `%LOCALAPPDATA%\orca\daemon-host-profiles` | `<host 哈希>\<版本>\build-<构建号>\` 下一份物化运行体，顶层六项（`Orca.exe`、`resources/` 等） | 运行时档案的物化布局；目录名是本机当次标识，不写进事实 |
| E14 | 列 `~/.orca/agent-hooks/` | 八个文件：`claude-hook.cmd`、`claude-hook-impl.cmd`、`claude-statusline.cmd`、`claude-statusline.installed`、`codex-hook.cmd`、`cursor-hook.cmd`、`qoder-hook.cmd`、`orca-agent-hook.exe` | agent CLI 侧钩子文件的存在与命名；其中的命令未执行 |
| E15 | `orca.exe skills installed`、`skills list`、`skills get orca-cli` | `list` 11 行「名字: 描述」；`get` 打印一份 Markdown 指南；`installed` 每条三行（名字 (短哈希)、描述、归属标签） | 三条只读子命令的输出形状；技能名与哈希因机器而异，不引具体值 |
| E16 | `cat` 工作树根的 `.git` 与管理目录的 `gitdir` | 两个文件各一行指针，互相指向 | 工作树与主仓库的连接方式；不含 Orca 信息 |
| E17 | 列 `.git/worktrees/<id>/` 并读 `commondir` 与 `HEAD` | 九个条目；`commondir` 为 `../..`，`HEAD` 为 `ref: refs/heads/<分支>` | 每树一份的状态清单与共享区指针；分支引用在共享区 |
| E18 | 两处 `git rev-parse HEAD` 与 `git rev-parse --git-path objects` | 两个不同的 40 位提交号；objects 解析到主仓库 `.git/objects` | 两树各指各的提交、对象库共享；不证明暂存区内容 |
| E19 | `orca.exe worktree current --json`（在一棵未登记的 git 工作树里） | `ok: false`、`selector_not_found`、消息 "No Orca workspace contains the current directory"，退出码 `1` | git 工作树不等于 Orca 工作区；登记是 Orca 的一层 |
| E20 | `orca.exe worktree ps` | 每工作区数行：名字与活跃时间、`id::<路径>`、`environment`、`address`、agent 与 terminal、分支与 PR 行、live/pty/unread、preview | 跨树总览的字段形状；名字、identity、PR 行是当次值，不引具体内容 |
| E21 | 临时仓库里两次 `git worktree add` 同一分支，再试 `--detach` 与 `--force --force` | 默认报 `fatal: 'w1' is already used by worktree at <路径>`（退出码 `128`）；`--detach` 成功（`(detached HEAD)`）；`--force --force` 成功（同分支两棵树）；git 2.54 | 同一分支默认不进两棵树，是默认约束不是必然；两条绕开路径存在；仓库用完即删 |
| E22 | `orca.exe orchestration run-list --json` | `ok: true`，`runs` 一条 legacy 行：`id`、`objective`、`legacy: true`，退出码 `0` | 记账面在没有绑定时也可读；不含其他 Run |
| E23 | `orca.exe orchestration run-current --json` | `{"ok":true,"result":{"runId":null}}`，退出码 `0` | 调用者没有绑定 Run；有账本不等于有协调者 |
| E24 | `orca.exe orchestration task-list --json` | `ok: false`、`run_required`，消息指明 `run-create`/`run-use` 两条修法，`effectsApplied: false`，退出码 `1` | Run 级动词的准入；报错无副作用 |
| E25 | `orca.exe orchestration inbox --json` | `{"ok":true,"result":{"messages":[]}}`，退出码 `0` | 全机邮箱列表为空；条数随机器变化 |
| E26 | `orca.exe orchestration run-show --id run_legacy_local --json` | `removedWork`：`coverage: complete`、`recordedSince` 时间戳、`tasks/dispatches/workers/terminals/activeWorkersAtRemoval` 全为 0、`lastRemovedAt: null`，退出码 `0` | Run 的移除账本字段形状；时间戳是当次值 |
| E27 | `orca.exe orchestration inbox --run run_legacy_local --json` | `messages: []`，退出码 `0` | Run 视角的收件箱可读 |
| E28 | `orca.exe orchestration check --peek --json` | `messages: []`，退出码 `0` | `--peek` 在未绑定 Run 时可读且不标记 |
| E29 | `orca.exe orchestration gate-list --json` | 与 E24 同形的 `run_required`，退出码 `1` | 决策门同样是 Run 级动词 |
| E30 | `orca.exe orchestration worker-list --json` | `{"ok":true,"result":{"workers":[],"scope":{"source":"all"}}}`，退出码 `0` | 无 worker 时的字段形状；`scope` 字段存在 |
| E31 | `orca.exe environment list --json` | `{"id":"local","ok":true,"result":{"environments":[]},"_meta":{"runtimeId":"local"}}`，退出码 `0` | 本机配对存储为空；条数随机器变化 |
| E32 | `orca.exe host list --json` | 8 行：1 条 `kind: local`（`name`、`id`、`selector`、`machineName`、`platform: win32`）与 7 条 `kind: ssh`（`name`、`id`、`selector`、`connected: false`，无 `platform`），退出码 `0` | 三种寻址的行形状；行数、目标名与 `machineName` 是当次值 |
| E33 | `orca.exe host name --json` | `{"machineName":"<本机名>","platform":"win32"}`，`_meta.runtimeId` 为当次 UUID，退出码 `0` | 回答者的名字与平台；UUID 不是稳定别名 |
| E34 | `orca.exe environment show --environment no-such-env --json` | `invalid_argument`，消息 `Unknown environment: no-such-env`，退出码 `1` | 未知选择器不静默 |
| E35 | `orca.exe environment status --environment local --json` | `invalid_argument`，消息指出 `local` 是本机自己的 Orca、不是保存的环境，附 `nextSteps`，退出码 `1` | 选择器不是路由：status 只作用于托管服务器 |
| E36 | `orca.exe environment list --environment local --json` | 与 E35 同形的 `invalid_argument`（`environment list` 版本），退出码 `1` | `list` 只答本机账本 |
| E37 | `orca.exe host list --environment local --json` | `invalid_argument`：`--environment` 不重定向 `host list`，附两条 `nextSteps`，退出码 `1` | 一份答案只描述一台机器 |
| E38 | `orca.exe environment show --environment local --json` | 与 E35 同形的 `invalid_argument`（`environment show` 版本），退出码 `1` | 与 E34 相区别：`local` 不是未知，而是不可作用于该组 |
| E39 | `orca.exe environment add`（无参数） | `Missing required --name`，退出码 `1` | 必填参数在配对前就被校验 |
| E40 | `orca.exe host name --environment local --json` | `machineName` 与 `platform: win32`，退出码 `0` | `--environment` 在按服务器回答的命令上就是路由；`local` 指本机自己的 Orca |
| E41 | `orca.exe host name --environment no-such-env --json` | `invalid_argument`：`Unknown Orca server in --environment no-such-env…`，附 `knownEnvironments`（空）与 `knownSshTargets`（带 `generation` 的行），退出码 `1` | 按名字查服务器；查不到就报错，不静默改答别处 |

E1 到 E4 四个数字互相一致，E6 不一致。这个不一致不说明安装出错，只说明版本字段的提交时机与发布时机不同；第 1.2 节按这个范围陈述。

## C.2 复现命令

```powershell
$orca = "$env:LOCALAPPDATA\Programs\orca\resources\bin\orca.exe"
& $orca --version
& $orca status
```

E3 的做法是在 `app.asar` 里取出 `package.json`。头部是四个 32 位小端整数：`4`、拾取器长度、头部长度、JSON 长度，JSON 长度是**第四个**字段（本机为 `4 1815476 1815472 1815467`）。偏移 16 处的 JSON 不是 `package.json` 本文，而是归档索引，根键是 `files`；按第三个字段的长度切它，会多出五个字节报 `Extra data`。数据区的起点是 `8 + 第二个字段`，`files` 里每个条目记着自己的相对 `offset` 与 `size`。下面这段在写作机器上原样跑通过，输出见其后：

```python
import json, os, struct
asar = os.path.expandvars(r"%LOCALAPPDATA%\Programs\orca\resources\app.asar")
with open(asar, "rb") as f:
    _, pickle_size, _, json_len = struct.unpack("<4I", f.read(16))
    header = json.loads(f.read(json_len))            # 归档索引，根键是 files
    entry = header["files"]["package.json"]
    f.seek(8 + pickle_size + int(entry["offset"]))   # 数据区起点 = 8 + 第二个字段
    pkg = json.loads(f.read(int(entry["size"])))
print(pkg["name"], pkg["version"], pkg["main"])
```

本机输出：`orca 1.4.269 ./out/main/index.js`。

第 2 章的四组只读观测（前三组在任一 Orca 工作树目录里运行，第四组的两条 git 命令在同一目录里）：

```powershell
& $orca repo list --json
& $orca worktree current --json
& $orca worktree list --json
git worktree list
git rev-parse --git-dir
```

第 3 章的观测（E11–E15；三条 skills 子命令在任一目录运行）：

```powershell
& $orca skills list
& $orca skills get orca-cli
& $orca skills installed
Get-ChildItem "$env:APPDATA\orca" | Select-Object -ExpandProperty Name
Get-ChildItem "$env:APPDATA\orca\agent-hooks" | Select-Object -ExpandProperty Name
Get-ChildItem "$env:LOCALAPPDATA\orca\daemon-host-profiles" -Recurse -Depth 2 | Select-Object -ExpandProperty FullName
Get-ChildItem "$HOME\.orca\agent-hooks" | Select-Object -ExpandProperty Name
Get-Content "$env:LOCALAPPDATA\Programs\orca\resources\skills\current-manifest.json" -TotalCount 30
```

第 4 章的观测（E16–E20；git 命令在同一棵 git 工作树里运行，`<主仓库>` 换成你的主检出路径）：

```powershell
Get-Content .git
$admin = git rev-parse --git-dir
Get-ChildItem $admin | Select-Object -ExpandProperty Name
Get-Content "$admin/commondir"
Get-Content "$admin/HEAD"
git rev-parse HEAD
git -C <主仓库> rev-parse HEAD
git rev-parse --git-path objects
git status --short
& $orca worktree current --json
& $orca worktree ps
```

E21 在一个用完即删的临时仓库里（先 `git init`、提交一次、建分支 `w1`）：

```powershell
git worktree add <路径一> w1
git worktree add <路径二> w1                 # 期望：fatal: 'w1' is already used by worktree at <路径一>
git worktree add --detach <路径二> w1        # 成功：git worktree list 显示 (detached HEAD)
git worktree add --force --force <路径三> w1 # 成功：强行越过默认拒绝（本机 git 2.54）
```

第 5 章的观测（E22–E30；在一个未绑定 Run 的目录里运行）：

```powershell
& $orca orchestration run-list --json
& $orca orchestration run-current --json
& $orca orchestration task-list --json        # 期望：run_required，退出码 1
& $orca orchestration inbox --json
& $orca orchestration run-show --id run_legacy_local --json
& $orca orchestration inbox --run run_legacy_local --json
& $orca orchestration check --peek --json
& $orca orchestration gate-list --json        # 期望：run_required，退出码 1
& $orca orchestration worker-list --json
```

第 6 章的观测（E31–E39；在任一目录运行，不需要远端主机）：

```powershell
& $orca environment list --json
& $orca host list --json
& $orca host name --json
& $orca environment show --environment no-such-env --json   # 期望：invalid_argument，退出码 1
& $orca environment status --environment local --json       # 期望：local 不是保存的环境，退出码 1
& $orca environment list --environment local --json         # 期望：同上，退出码 1
& $orca host list --environment local --json                # 期望：--environment 不重定向，退出码 1
& $orca environment show --environment local --json         # 期望：同上，退出码 1
& $orca environment add                                     # 期望：Missing required --name，退出码 1
& $orca host name --environment local --json                # 期望：machineName/platform，退出码 0
& $orca host name --environment no-such-env --json          # 期望：Unknown Orca server，退出码 1
```

## C.3 没有做的事

下列各项本章没有验证，读到相关说法时应视为未证实：

- `orca serve` 未单独启动，因此「无界面运行时能独立工作」只依据帮助文本的措辞。
- macOS 与 Linux 的安装目录结构未实测。
- `orcad-template/` 下的 worker 入口未逐个运行，职责划分是读文件名得出的。
- `skills/current-manifest.json` 中的 11 个技能只确认了清单与摘要字段存在，未逐字节校验摘要。
- `Diagnostics`、`Accounts`、`Hosts`、`Environments` 各组命令未执行。
- `worktree create` 与 `worktree rm` 的完整闭环没有执行，只在已登记仓库上做只读观测；文档所述「创建在后台进行」按 `docs/site/content/docs/model/worktrees.mdx` 陈述。
- `--issue` / `--pr` 挂接后 `linkedWorkItem` 的自动填充、hooks（`--setup run`）的执行内容未实测。
- 远端 host 上的 worktree 与 parent/child lineage 未实测。
- 第 6 章的配对一次都没有完成：`environment add` 只跑到缺参校验（E39），未带真实 `orca://pair?code=...` 执行；`orca pair` 未运行，`environment rm` 与 `host rm` 未执行。
- SSH 连接未建立（`host list` 的 ssh 行全部 `connected: false`），因此 `platform` 缺席、`host name --environment <name>` 未观测；`orca serve` 未单独启动，`--pairing-address`、`--bind`、`--allow-public` 与 `--mobile-pairing` 均未实测。
- 托管服务器没有对真实的已保存服务器执行过任何动词：`status` 只跑到 `--environment local` 的拒绝（E35），`update`、`rollback`、`recover`、`stop`、`forget`、`cancel-stop` 六条未运行；`--force` 的推迟更新、`--accept-changed-state` 的恢复与 `stop` 的「主机证明退出」语义按帮助文本与 `src/cli/specs/managed-server.ts` 陈述。
- `Environment Recipes`（`vm recipe doctor`、`vm env doctor`）与 Cloud VM 的 `orca.yaml` 配方未运行；`remote-servers.mdx` 的令牌撤销与 `Shared Server Access` 未在界面核对。
- 远端 Orca Server 的 Linux 命名（`orca-ide`）与安装结构只在 `remote-servers.mdx` 里核对，未在 Linux 上实测。
- `orca.yaml`、`.worktreeinclude`、`.orca/issue-command` 的生效链路未实测：键、限制与三选按 `docs/site/content/docs/model/orca-yaml.mdx` 陈述，要等一次真实的 `worktree create`。
- `.claude/`、`.codex/` 钩子的执行与 `CLAUDE.md`/`AGENTS.md` 的读取按 `docs/site/content/docs/agents/hooks-memory.mdx` 陈述，未造场景观察。
- `skills install/update/share`、`agent hooks status|on|off`、Settings 各面板未执行、未截图。
- `%APPDATA%\orca` 内的数据库与密钥文件只确认了名字，未打开内容。
- `worktree activate` 与 sleep/archive 未执行；删树留分支的复核（preserved branches）与 sidebar 的隐藏工作树卡按文档陈述。
- `ports` 与 `workspace cleanup` 三条子命令未执行，只引帮助文本。
- 三条通道（Worktree Shared Paths、`sharedDirectories`、`.worktreeinclude`）的链接与副本效果按 `worktrees.mdx` 与 `orca-yaml.mdx` 陈述，未实测改动互通；`worktree ps` 只固定了输出形状。
- 编排闭环未执行：`run-create`、`task-create`、`worker-start`、`send`、`reply`、`worker-read` 无一运行，worker 的终端与 transcript 没有样本。
- `deny`、`worker-abandon`、`worker-release`、`worker-keep-open`、`dispatch --inject`、`task-update` 的状态迁移与 `reset` 未执行。
- 内置技能指南的行为口径按原文陈述、未实测：约 4 个的并发、三次失败的熔断、`--retry-of` 链、effort 档位数字、worktree 放置决策树、远端按 Dispatch ID 寻址。
- `--on` 远端服务器、`ORCA_ENVIRONMENT` 与配对码未设置、未验证；第 5 章引用的四份 `src/cli/specs/` 规格文件只按钉住提交的目录清单指认，未逐行读实现。

## C.4 本篇的边界

观测表是可复现的最小集合，不构成对 Orca 行为的全面验证。E2 与 E7–E10 的输出依赖当次进程与登记状态；E12–E41 的目录条目、技能集合、Run 账本、工作区瞬时状态、主机行数与配对存储随机器与时间变化，E16–E19 依赖当次两棵树的提交与路径；E22–E30 在无绑定 Run 的目录里观测，`recordedSince` 只保留字段名；E32–E33 的 `machineName`、目标名与 UUID 是当次值，E40–E41 的 `knownSshTargets` 行与其 `generation` 序号同样随机器变化，书里只留字段形状。可比较的是字段名与就绪值的含义，不是具体数值。
