# 附录 C：实验记录与复现边界

<!-- block: orca-apxc.b-opening -->
本篇按实验编号记录第 1–10 章用到的每一次观测，写清命令、当时的输出与这次观测证明不了什么。

## C.1 观测表

E1–E6 的观测日期为 2026-11-22；E7–E94 为 2026-11-23。环境同为 Windows，已安装 Orca 1.4.269。

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
| E42 | `orca diagnostics memory --json`（在 Orca 工作树目录里） | `result` 九键：`app`（`main`/`renderer`/`other` 各 `cpu`/`memory`/`privateMemory`，汇成总计与 `history`）、`host`（八键，含 `availableMemorySource`）、`collectedAt`、`processCommitMetric`、`processMemoryMetric: working-set`、`totalCpu`、`totalMemory`、`totalPrivateMemory`、`worktrees`（本机当次 6 行，`worktreeId` 形如 `<repoId>::<路径>`，`sessions` 行带 `sessionId`、`paneKey`、`pid`），退出码 `0` | 点状快照的字段形状与当次读数；数值随进程变化，不可复现 |
| E43 | `orca account list --json` | 五服务商块（`antigravity`、`claude`、`codex`、`devin`、`opencode`）各带 `accounts`/`activeAccountId`；`claude`/`codex` 带 `activeAccountIdsByRuntime`（`host`/`wsl`）；`codex` 带 `systemDefault`；`rateLimits` 22 键，含 11 个服务商块与辅助/布尔键；当次账号表全空，多数限流 `unavailable`、`cursor` 为 `ok`，退出码 `0` | 托管账号与限流的字段形状；账号行数与限流状态是当次值 |
| E44 | `orca account list --environment local --json` | `invalid_argument`：消息直言 `--environment` 不重定向 `account list`（`id: local`、`_meta.runtimeId: null`），退出码 `1` | 账号清单只答本机 |
| E45 | `orca agent hooks status --json` | `enabled: true`、`appliedBy: runtime`、`settingsPath` 指向 `profiles\local-default\profile-state.db`、`statuses` 23 行（本机当次 4 行 `installed`，`managedHooksPresent: true`），退出码 `0` | 钩子开关与逐 CLI 落位；`state` 枚举随安装情况变化 |
| E46 | `orca ports --json`（在 Orca 工作树目录里；另在非工作区目录对照） | 工作树里：`platform: win32`、`scannedAt`、`ports: []`、`executionHostId: local`，退出码 `0`；非工作区目录：`selector_not_found`「No Orca workspace contains the current directory」，退出码 `1` | 端口归属的输出形状与 `ports` 的目录依赖；端口行随 dev server 变化 |
| E47 | `orca workspace cleanup preview --json` | `rows` 16 行，行键 `worktreeId`/`repoId`/`repoName`/`displayName`/`branch`/`path`/`evaluation`；当次全部 `action: keep`（11 行 `not-removable`、5 行 `rules-off`），退出码 `0` | 预览的判定字段与「不动手」；行数与原因随规则与仓库变化 |
| E48 | `orca workspace cleanup report --json` | `runs: []`、`running: false`、`nextRunAt: null`；`id` 与 `_meta.runtimeId` 为当次 UUID，退出码 `0` | 清理历史与排期的字段形状；本机从未运行自动清理 |
| E49 | `orca agent installed --json` | `agents` 9 行，行键 `id`/`name`/`default`，当次 `default` 为 `claude`，退出码 `0` | 可启动 CLI 的清单形状；行数与默认值随机器变化 |
| E50 | `orca agent list --json` | `agents` 6 行，全部 `kind: terminal`（5 `working`、1 `done`），行键含 `orcaSessionId`、`paneKey`、`lastAssistantMessage`、`updatedAt` 等，退出码 `0` | 运行中会话的行形状；消息内容与标题不引 |
| E51 | `orca ports --environment local --json` | 与 E46 同形的四键（`ports` 为空数组），退出码 `0` | `--environment` 在端口读数上是路由，`local` 答本机 |
| E52 | `orca workspace cleanup preview --environment local --json` | 与 E47 同一批 16 行（`worktreeId` 集合相同、顺序不同），退出码 `0` | 路由回本机时答案同源；行序不稳定，不是信息 |
| E53 | `orca diagnostics memory --environment local --json` | 与 E42 同形、数值不同（`worktreeId` 集合相同），退出码 `0` | 快照是点状的：形状稳定，数值只代表当次 |
| E54 | `orca agent list --json` | `result` 三键 `agents`/`truncated`/`hostScope`（`hostIds: ["local"]`、`omittedHostIds: []`）；`agents` 本机当次 6 行，其中 1 行 `orcaSessionId: null`，退出码 `0` | 列表信封的形状；行数与状态是当次值，无 id 的行不能拿去 show/read |
| E55 | `orca agent show --id "orca_session_id:<会话 ID>" --json`（另加 `--environment local` 对照） | `result` 三键 `orcaSessionId`/`kind`/`places`；`places` 本机当次 1 行，行键与 `agent list` 相同（12 键）；两次退出码均 `0` | 会话落位的形状；多窗格与关闭态未观测 |
| E56 | `orca agent read --id "orca_session_id:<会话 ID>" --limit 3 --json`（另加 `--environment local`、`--limit 1` 对照） | `result` 六键 `orcaSessionId`/`kind`/`agent`/`source`（`transcript`）/`entries`/`limited`（`true`）；条目 `kind: message`、`role: assistant`、`text` 可为空、`tools` 记工具名；两次退出码均 `0` | 会话内容的条目形状；条数是当次值，文字不引 |
| E57 | `orca agent show`/`agent read` 对同一不存在的 id | 两条都返回 `agent_unknown`，消息「No agent … on this Orca. If it runs on another host, run this there or add `--environment <host>`.」，退出码 `1` | 查不到的 id 不静默；两条修法写在消息里 |
| E58 | `orca search --index-status --json` | `result` 十四键：`supportedAgents`（25 个）、`enabled: true`、`phase: current`、`filesIndexed`（4574）、`filesDue`（0）、`filesFailed`（0）、`messagesIndexed`（117866）、`degradedRoots`（空）、`sessionsByAgent`（9 个 agent）等，退出码 `0` | 索引状态的可盘点字段；数值是当次值 |
| E59 | `orca search --query "worktree" --limit 5 --json` | `result` 六键 `kind`/`hits`/`page`/`generation`/`truncated`/`durationMs`；`hits` 5 条，每条 11 键（`agent`/`sessionId`/`title`/`cwd`/`branch`/`updatedAt`/`messageCount`/`score`/`evidence`/`source`/`resumeCommand`）；`page.hasMore: true`，退出码 `0` | 命中与分页的形状；命中可来自别的项目与 agent，标题与片段不引 |
| E60 | `orca search --query "worktree" --scope conversation --limit 5 --json` | 与 E59 同一批 5 条、同一顺序，退出码 `0` | 两种 scope 在这条查询上不可区分；工具输出未命中 |
| E61 | `orca search --query "worktree" --environment local --limit 5 --json` | 与 E59 同一批 5 条、同一顺序，退出码 `0` | `--environment` 在检索上是路由，`local` 答本机 |
| E62 | `orca reference list --worktree current --json`（在工作树目录里；另加 `--environment local` 对照） | `result` 两键 `worktree`（35 键，含十三个 `linked*` 键）与 `references`（空数组），两次退出码均 `0` | 挂接的字段形状与空状态；有挂接的行未观测 |
| E63 | `orca reference find STA-1234 --json` | `result` 五键 `kind: reference_matches`/`query`/`scope`（`source: stored-metadata`、`includeArchived: false`）/`truncated: false`/`matches`（空数组），退出码 `0` | 只读存储的挂接；查不到给空结果，不报错 |
| E64 | `orca agent-context --json` | `schemaVersion: 1`、`commandCount: 417`、`commands`；条目 11 键（`command`/`path`/`aliases`/`argumentMode`/`summary`/`usage`/`flags`/`positionalArgs`/`repeatableFlags`/`examples`/`notes`），`argumentMode` 当次取值 `parsed` 与 `passthrough`，退出码 `0` | 命令面的机器可读版形状；417 条未逐条核对 |
| E65 | `orca skills list --json` | 顶层单键 `topics`，11 条，每条 `name`/`description`，退出码 `0` | 随包指南元数据的本地形状；无信封、不联系运行时 |
| E66 | `orca skills installed --json` | 信封 `id`/`ok`/`result`/`_meta`；153 条，条目六键 `id`/`name`/`description`/`providers`/`sourceKind`/`sourceLabel`；`sourceKind` home 119、bundled 33、plugin 1；`providers` agent-skills 117、codex 28、claude 7、agent-skills+claude 1 | 技能发现的运行时信封与来源分类；描述文字不引 |
| E67 | `orca plugin list --json` | 信封 `ok`/`result`，无 `id`/`_meta`；2 行、每行 26 键；两行 `idle`、`execution: data`、`official`/`bundled` 均 `true` | 插件清单的裸信封与当次行；六种状态只见 `idle` |
| E68 | `orca automations list --json` | `result` 三键 `automations`（空）、`items`（空）、`orphanCount: 0`，退出码 `0` | 定时任务清单的空状态形状 |
| E69 | `orca artifacts list --json` | 信封 `id`/`ok`/`result`/`_meta`；`artifacts` 空数组，退出码 `0` | 账号侧工件的空状态；`runtimeId` 每次调用不同 |
| E70 | `orca project list --json` | 12 行；`id` 两种形状 `github:<owner>/<repo>` 11 行、`repo:<uuid>` 1 行；`kind` git 11、folder 1；`providerIdentity` 四键 `host`/`owner`/`provider`/`repo` | 项目底册的 id 形状与来源键 |
| E71 | `orca skills get jira-tickets --json`；同法 `orca-cli` 与 `--full` | 顶层 `name`/`markdown`/`full` 三键；`jira-tickets` 的 `markdown` 1706 字符，`orca-cli` 44777，`--full` 152065 且 `full: true`。另 E71b 未知 topic：退出码 `1`，stderr 报 「Unknown skill topic」并列出全部 11 个可用 topic | 指南正文的本地形状与 `--full` 的口径；查不到附完整清单 |
| E72 | `orca automations show no-such-id --json` | 退出码 `1`，`ok: false`，`error.code: runtime_error`，消息原文 「Automation not found.」 | 定时任务查不到的报错形状；错误码笼统 |
| E73 | `orca plugin logs <插件键> --json`；另 E73b 用不存在的键 | `result` 三键 `pluginKey`/`lines`/`cursor`；正常键 `lines` 为空数组；E73b 不存在的键退出码 `0`、`ok: true`、`lines` 空数组 | 插件日志的形状与「查不到不报错」的负观测 |
| E74 | `orca automations runs --json`；另 E74b `project setups --json` | E74 `result` 单键 `runs`（空）；E74b 12 行、每行 14 键，`hostId` 全 `"local"` | 运行历史的空状态；setup 是每机一行的账 |
| E75 | `skills installed`、`plugin list`、`automations list`、`project list` 各加 `--environment local` | 四条均退出码 `0`，`result` 与不加旗标同源 | `local` 在运行时组上放行 |
| E76 | `orca skills list --environment local --json` | 退出码 `0`，输出与不加旗标逐字节相同 | 旗标对随包数据形同虚设 |
| E77 | `orca skills get orca-cli --environment local --json` | 同 E76，逐字节相同 | 指南正文亦随包，旗标形同虚设 |
| E78 | `orca artifacts list --environment local --json` | 退出码 `1`，`error.code: invalid_argument`，消息原文 「`--environment` does not retarget artifact commands; artifacts use the signed-in desktop account.」，`_meta.runtimeId` 为 `null` | 账号侧拒绝旗标；拒绝发生在 CLI 内 |
| E79 | `orca repo list --json` | `result` 单键 `repos`，12 行；行键不齐：11 个打底键全行都有，`upstream`/`repoIcon`/`projectHostSetupMethod` 各 11 行、`projectGroupId`/`projectGroupOrder` 各 7 行、`folderUpgradeGitRootPath`/`sourceControlAi` 各 1 行；`kind` 全 `git`，`path` 两种分隔形态（1 行反斜杠、11 行正斜杠），退出码 `0` | 仓库行的打底键与条件键；无树级字段；行键与行数随登记变化 |
| E80 | `orca worktree list --json` | `result` 四键 `hostScope`/`totalCount`/`truncated`/`worktrees`；18 行、每行 38 键，`id` 复合格 `<repoId>::<path>`；`isMainWorktree` 12 行 `true`、6 行 `false`，主检出全在 `D:`、链接树全在 `C:` 的 workspaces 下，退出码 `0` | 树列表行的形状与当次行数；行数随登记的工作树数目走 |
| E81 | `orca worktree current --json`（在未登记的写作目录 barreleye 里） | `selector_not_found`「No Orca workspace contains the current directory: <路径>」，退出码 `1` | 与 E19 同码：git 工作树不等于 Orca 登记；本章动词须显式 `--repo` |
| E82 | `orca worktree create --repo "id:<GUID>"`（缺 `--name`） | `invalid_argument`「Missing required --name」，`_meta.runtimeId: null`，退出码 `1` | 必填参数先校验；拒绝发生在 CLI 内 |
| E83 | `orca worktree create --name <名> --no-parent --setup skip`（在未登记目录里、无 `--repo`） | `invalid_argument`「Missing repo selector. Pass --repo or run from inside an Orca-managed worktree.」，退出码 `1` | 修法写在消息里；目录推断不成立时必须点名仓库 |
| E84 | `orca worktree create --repo "id:<GUID>" --name <探针名> --branch <探针名> --no-parent --setup skip --json` | 退出码 `0`；`result` 五键：`worktree`（42 键，含 `identity.key: wt2:local:<uuid>`、`projectId: github:<owner>/<repo>`、`baseRef: refs/remotes/origin/main`、`cliProvenance` 带 `callerTerminalHandle: term_<uuid>`、`parentWorktreeId: null`、`lineage: null`）、`lineage`、`workspaceLineage`、`warnings: []`、`catalogVersion`（`sequence: 534`）；git 侧 `branch --list` 出现带 `+` 的探针行、`worktree list` 多一行；当次 15.14 s | 登记的字段形状与 `--no-parent`/`--setup skip` 的直接效果；键值与耗时是当次值 |
| E85 | `orca worktree current --json`（在探针目录里） | 退出码 `0`，46 键记录——E84 的严格超集（多 `address`/`environment`/`linkedItems`/`parent`） | 新树即刻可寻址；单读视角多出的四个键 |
| E86 | `orca worktree rm --worktree current --json` | `invalid_argument`，消息原文「orca worktree rm needs an explicit workspace; --worktree current is not accepted for removal. Here, current is --worktree <复合格>; pass that instead.」；`data.current` 带 `resolution: resolved`、`selectors`、`nextSteps`，退出码 `1` | 删除必须点名；拒绝消息自带解析结果与修法 |
| E87 | `orca worktree rm --worktree "<复合格>" --delete-branch --json` | 退出码 `0`；`result` 两键 `removed: true`、`catalogVersion`（`sequence: 542`）；无分支证据；当次 10.17 s | rm 只对删树背书；答案只覆盖动词的字段 |
| E88 | rm 之后的四路核验（`git branch --list`、`git worktree list`、磁盘目录、`worktree list --json`） | 分支 0 行（两处检出）、git 树回到两行、探针目录消失、Orca 列表回 18 行无探针行 | `--delete-branch` 删了分支这一事实由 git 侧证明；零残留的核验方法 |
| E89 | `orca workspace cleanup preview --json` | `result` 两键 `evaluatedAt`/`rows`；18 行、行 7 键，`evaluation` 全部 `{action: keep, cause: rules-off}`，退出码 `0` | 沙盘的行形状；`cause` 是当次值（与 E47 的 11+5 分布不同，只记观测） |
| E90 | `orca workspace cleanup run --json` | 退出码 `0`；`result` 即运行记录八键：`id`、`trigger: cli`、`startedAt`/`finishedAt`（相等）、`counts` 四个 0、`freedBytes: 0`、`rows: []` | 规则全关时 run 的空账本；与 preview 的 18 行对照 |
| E91 | `orca workspace cleanup run --environment local --json` | 退出码 `0`，`result` 与 E90 同八键同形 | `local` 在清理执行上放行 |
| E92 | `orca workspace cleanup report --json` | `result` 三键 `running`/`nextRunAt`/`runs`；`runs` 两条，均为 CLI 触发的运行记录，条目形状与 E90 的 `result` 一致 | E48 的空历史被本章两次执行填上 |
| E93 | `orca agent hooks off --environment local --json` | `invalid_argument`「`--environment` does not retarget agent hooks; run this command on the machine whose hooks you want to manage.」，`_meta.runtimeId: null`，退出码 `1` | 本机配置不路由；与 E44、E78 同款拒绝 |
| E94 | `orca agent hooks off --json` 随即 `on`，末次 `status` 与基线比对 | off：`enabled: false`、23 行全 `not_installed`、claude 行 `managedHooksPresent: false`；on：`enabled: true`、4 行 `installed` + 19 行 `not_installed`；末次 `status` 与基线（E45 同形）`statuses` 逐行一致、其余字段一致，`appliedBy` 全程 `runtime`；两次退出码均 `0` | 开关闭环与还原核验的方法；off 窗口仅数秒 |

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

第 7 章的观测（E42–E53；`ports` 的正常命令须在 Orca 工作树目录里跑，非工作区目录的失败对照见本节末，其余命令在任一目录）：

```powershell
& $orca diagnostics memory --json
& $orca account list --json
& $orca account list --environment local --json              # 期望：does not retarget，退出码 1
& $orca agent hooks status --json
& $orca ports --json                                         # 须在工作树目录，期望四键、ports 为空
& $orca workspace cleanup preview --json
& $orca workspace cleanup report --json
& $orca agent installed --json
& $orca agent list --json
& $orca ports --environment local --json
& $orca workspace cleanup preview --environment local --json
& $orca diagnostics memory --environment local --json
```

第 8 章的观测（E54–E64；`reference list` 须在工作树目录里跑，其余在任一目录；`<会话 ID>` 取自 `agent list` 的行，只在本机有效）：

```powershell
& $orca agent list --json
& $orca agent show --id "orca_session_id:<会话 ID>" --json
& $orca agent read --id "orca_session_id:<会话 ID>" --limit 10 --json
& $orca agent show --id "orca_session_id:00000000-0000-4000-8000-000000000000" --json   # 期望：agent_unknown，退出码 1
& $orca search --index-status --json
& $orca search --query "worktree" --limit 5 --json
& $orca search --query "worktree" --scope conversation --limit 5 --json
& $orca search --query "worktree" --environment local --limit 5 --json
& $orca reference list --worktree current --json      # 须在工作树目录
& $orca reference find STA-1234 --json
& $orca agent-context --json
```

E46 的失败对照：换到一个不是 Orca 工作区的目录（例如书稿目录）再跑同一句，期望 `selector_not_found`（「No Orca workspace contains the current directory」）、退出码 `1`：

```powershell
& $orca ports --json
```

第 9 章的观测（E65–E78；全部只读、任一目录可跑；`<插件键>` 取自 `plugin list` 行里的 `pluginKey`）：

```powershell
& $orca skills list --json
& $orca skills installed --json
& $orca skills get jira-tickets --json
& $orca skills get orca-cli --json
& $orca skills get orca-cli --full --json
& $orca skills get no-such-topic                           # 期望：Unknown skill topic，退出码 1
& $orca plugin list --json
& $orca plugin logs "<插件键>" --json
& $orca plugin logs no-such-plugin-key --json              # 期望：ok true、lines 空数组
& $orca artifacts list --json
& $orca automations list --json
& $orca automations runs --json
& $orca automations show no-such-id --json                 # 期望：runtime_error，退出码 1
& $orca project list --json
& $orca project setups --json
& $orca skills installed --environment local --json        # 期望：与不加同源
& $orca plugin list --environment local --json
& $orca automations list --environment local --json
& $orca project list --environment local --json
& $orca skills list --environment local --json             # 期望：逐字节相同
& $orca skills get orca-cli --environment local --json
& $orca artifacts list --environment local --json          # 期望：does not retarget，退出码 1
```
第 10 章的观测（E79–E94；E81 与 E85 有目录前提，E84–E88、E90–E91 与 E94 是写侧、做完即还原；`<GUID>` 取自 `repo list` 行，`<探针名>` 自取）：

```powershell
& $orca repo list --json
& $orca worktree list --json
& $orca worktree current --json                                   # 未登记目录：selector_not_found，退出码 1（E81）
& $orca worktree create --repo "id:<GUID>"                        # 期望：Missing required --name，退出码 1（E82）
& $orca worktree create --name <探针名> --no-parent --setup skip # 未登记目录且无 --repo：Missing repo selector，退出码 1（E83）
& $orca worktree create --repo "id:<GUID>" --name <探针名> --branch <探针名> --no-parent --setup skip --json   # E84：开探针树
& $orca worktree current --json                                   # 在探针目录里：46 键记录（E85）
& $orca worktree rm --worktree current --json                     # 期望：拒绝并给出复合格修法，退出码 1（E86）
& $orca worktree rm --worktree "<GUID>::<探针路径>" --delete-branch --json    # E87：removed true
# E88 的核验尾巴（rm 之后逐条跑）：
& git -C <主检出> branch --list <探针名>                          # 期望：0 行
& git -C <主检出> worktree list                                   # 期望：无探针行
& $orca worktree list --json                                      # 期望：回到基线行数、无探针行
& $orca workspace cleanup preview --json                          # 闸门：任一行 action ≠ keep 就停——那是规则要删树，run 会真删
& $orca workspace cleanup run --json                              # 写侧：真实执行；preview 全 keep 才往下（本书观测时规则全关）
& $orca workspace cleanup preview --environment local --json    # 同一闸门再过一遍：全 keep 才跑下一行
& $orca workspace cleanup run --environment local --json
& $orca workspace cleanup report --json                           # 期望：runs 里有两条 cli 记录
& $orca agent hooks off --environment local --json                # 期望：does not retarget，退出码 1（E93）
& $orca agent hooks status --json                                 # 存基线：记下 enabled 与各行；基线 enabled 为 false 时，收尾用 off 还原
& $orca agent hooks off --json                                    # 期望：enabled false、23 行全 not_installed
& $orca agent hooks on --json                                     # 期望：enabled true（off/on 闭环的观测）
& $orca agent hooks status --json                                 # 末态须与 297 行基线逐字段一致（E94）；基线原为 off 的，先补一次 off 再比
```

## C.3 没有做的事

下列各项本章没有验证，读到相关说法时应视为未证实：

- `orca serve` 未单独启动，因此「无界面运行时能独立工作」只依据帮助文本的措辞。
- macOS 与 Linux 的安装目录结构未实测。
- `orcad-template/` 下的 worker 入口未逐个运行，职责划分是读文件名得出的。
- `skills/current-manifest.json` 中的 11 个技能只确认了清单与摘要字段存在，未逐字节校验摘要。
- `Diagnostics` 与 `Accounts` 在第 7 章执行了只读子命令（`diagnostics memory`、`account list`）；`account add/select/rm` 与 `--agent` 过滤未执行；`Hosts` 与 `Environments` 见第 6 章。
- `worktree create` 与 `worktree rm` 的受控闭环在第 10 章执行过一次（探针树、`--no-parent`、`--setup skip`、零提交分支、`--delete-branch`，做完即还原并四路核验）：默认谱系、`--setup` 默认链、删树留分支与 `--force` 均无样本；「创建在后台进行」按 `docs/site/content/docs/model/worktrees.mdx` 陈述。
- `--issue` / `--pr` 挂接后 `linkedWorkItem` 的自动填充、hooks（`--setup run`）的执行内容未实测。
- 远端 host 上的 worktree 与 parent/child lineage 未实测。
- 第 6 章的配对一次都没有完成：`environment add` 只跑到缺参校验（E39），未带真实 `orca://pair?code=...` 执行；`orca pair` 未运行，`environment rm` 与 `host rm` 未执行。
- SSH 连接未建立（`host list` 的 ssh 行全部 `connected: false`），因此 `platform` 缺席、`host name --environment <name>` 未观测；`orca serve` 未单独启动，`--pairing-address`、`--bind`、`--allow-public` 与 `--mobile-pairing` 均未实测。
- 托管服务器没有对真实的已保存服务器执行过任何动词：`status` 只跑到 `--environment local` 的拒绝（E35），`update`、`rollback`、`recover`、`stop`、`forget`、`cancel-stop` 六条未运行；`--force` 的推迟更新、`--accept-changed-state` 的恢复与 `stop` 的「主机证明退出」语义按帮助文本与 `src/cli/specs/managed-server.ts` 陈述。
- `Environment Recipes`（`vm recipe doctor`、`vm env doctor`）与 Cloud VM 的 `orca.yaml` 配方未运行；`remote-servers.mdx` 的令牌撤销与 `Shared Server Access` 未在界面核对。
- 远端 Orca Server 的 Linux 命名（`orca-ide`）与安装结构只在 `remote-servers.mdx` 里核对，未在 Linux 上实测。
- `orca.yaml`、`.worktreeinclude`、`.orca/issue-command` 的生效链路未实测：键、限制与三选按 `docs/site/content/docs/model/orca-yaml.mdx` 陈述；第 10 章的探针创建带 `--setup skip`，链路继续挂起。
- `.claude/`、`.codex/` 钩子的执行与 `CLAUDE.md`/`AGENTS.md` 的读取按 `docs/site/content/docs/agents/hooks-memory.mdx` 陈述，未造场景观察。
- `skills install/update/share`、Settings 各面板未执行、未截图；`agent hooks on|off` 在第 10 章受控执行过一回（off 后数秒内 on，末态与基线逐字段一致）；`agent hooks status` 的只读见第 7 章。
- `%APPDATA%\orca` 内的数据库与密钥文件只确认了名字，未打开内容。
- `worktree activate` 与 sleep/archive 未执行；删树留分支的复核（preserved branches）与 sidebar 的隐藏工作树卡按文档陈述。
- `ports --all` 未执行；`workspace cleanup run` 在第 10 章受控执行过两次（规则全关、`counts` 四个 0）；`ports`、`cleanup preview` 与 `cleanup report` 的只读观测见第 7 章（E46–E48、E51–E52）。
- `agent read` 只读了终端 agent 的 transcript（`source: transcript`）；chat 类会话本机没有样本。`state: working` 的行、sleeping 与 WSL 会话的读法按帮助文本陈述，未观测。
- `search` 只跑了单页与一个查询词：`--cursor` 翻页、`--fresh`、`--since`、`--sort newest`、`--agent`/`--path` 过滤与 `--debug` 未执行；`truncated` 四个布尔只见过全 `false`。
- `reference list` 只在本机一棵工作树上跑了 `--worktree current`，`references` 为空；有挂接的行、其他选择器与 `--repo` 未观测。`reference find` 只用一个不存在的 issue key 测了空结果；真实 URL/key、`--include-archived` 与 `--limit` 未测。
- `agent show` 未观测到「两窗格恢复」与「关闭后无 places」；`agent list` 里 `orcaSessionId: null` 的行无法用 `show`/`read` 验证。`agent-context` 的 417 条未逐条核对。
- `--environment` 在第 8 章四组命令上只验证了 `local` 放行（agent show 与 agent read 的 `local` 对照、E61、E62）：未知环境名与 `--pairing-code` 未测；「a paired server withholds them」按帮助文本陈述。
- 三条通道（Worktree Shared Paths、`sharedDirectories`、`.worktreeinclude`）的链接与副本效果按 `worktrees.mdx` 与 `orca-yaml.mdx` 陈述，未实测改动互通；`worktree ps` 只固定了输出形状。
- 编排闭环未执行：`run-create`、`task-create`、`worker-start`、`send`、`reply`、`worker-read` 无一运行，worker 的终端与 transcript 没有样本。
- `deny`、`worker-abandon`、`worker-release`、`worker-keep-open`、`dispatch --inject`、`task-update` 的状态迁移与 `reset` 未执行。
- 内置技能指南的行为口径按原文陈述、未实测：约 4 个的并发、三次失败的熔断、`--retry-of` 链、effort 档位数字、worktree 放置决策树、远端按 Dispatch ID 寻址。
- `--on` 远端服务器、`ORCA_ENVIRONMENT` 与配对码未设置、未验证；第 5 章引用的四份 `src/cli/specs/` 规格文件只按钉住提交的目录清单指认，未逐行读实现。
- 第 9 章五组的写侧一条未执行：`skills install/update/share`、`plugin install/enable/disable/restart`、`plugin system on|off`、`plugin dev` 全组、`artifacts share/update/unshare/delete`、`automations create/edit/run/remove`、`project setup-existing-folder/setup-clone/setup-create/setup-update/setup-delete`。
- `plugin list` 六种状态只观测到 `idle`：`pending`、`errored`、`invalid` 与 dev 行、`needsReconsent: true` 的行无样本；第三方插件未装，`plugin logs` 只见过空数组。
- `automations list` 的 `automations` 与 `items` 双键并存只记观测，未核对二者关系；有真实定时与运行历史（`runs` 非空）的行未观测。
- `skills installed` 的 153 条描述与 `plugin list` 两行的插件自述只记字段名、计数与标签名，未引内容、未逐字节核对源码；`skills get` 只逐字核对了 `jira-tickets` 一条 description。
- `project setups` 只观测了本机行（`hostId` 全 `"local"`）：远端 host 上的 setup、`setupState` 取值集合、`hookSettings` 与 `sourceControlAi` 的内容均未展开。
- `--environment` 在第 9 章五组上只验证了 `local`（E75–E77 放行、E78 拒绝）：未知名在这五组上的报错未测，`--pairing-code` 一条没跑；`artifacts` 组不提供该旗标，按帮助文本陈述。
- 第 10 章的 `--environment` 只验证了 `local`（cleanup run 放行、hooks 拒绝）：未知名的报错未测；`cause` 分布与第 7 章不同（全 `rules-off` 对 11+5 混合）只记观测未查原因；off 窗口里 agent 启动的钩子行为、`callerTerminalHandle` 指向的终端、远端 host 上的 create/rm 均未观测。

## C.4 本篇的边界

观测表是可复现的最小集合，不构成对 Orca 行为的全面验证。E2 与 E7–E10 的输出依赖当次进程与登记状态；E12–E53 的目录条目、技能集合、Run 账本、工作区瞬时状态、主机行数、配对存储、账号表、钩子状态、端口、清理预览行与 agent 会话随机器与时间变化，E16–E19 依赖当次两棵树的提交与路径；E22–E30 在无绑定 Run 的目录里观测，`recordedSince` 只保留字段名；E32–E33 的 `machineName`、目标名与 UUID 是当次值，E40–E41 的 `knownSshTargets` 行与其 `generation` 序号同样随机器变化；E42 与 E53 的进程数值、E47 与 E52 的行序只代表当次，书里只留字段形状与集合关系；E54–E56 的会话行、条目数与 E58 的索引计数、E59–E61 的命中集合随机器与时间变化，E62–E64 的挂接与命令面是当次结构；E65 与 E71 的随包指南文字在同版本 CLI 上可逐字节复验，E66–E67 的技能与插件集合、E70 与 E74b 的项目与 setup 行随机器与时间变化，E68–E69 与 E74 的空状态、E72 的查不到报错只代表本机当次无登记；E79–E94 的写侧闭环在零提交的探针树上完成、已四路核验删除，18 行树、`catalogVersion` 序号、耗时与 cause 分布是当次值。可比较的是字段名与就绪值的含义，不是具体数值。
