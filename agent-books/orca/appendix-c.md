# 附录 C：实验记录与复现边界

<!-- block: orca-apxc.b-opening -->
本篇按实验编号记录第 1–3 章用到的每一次观测，写清命令、当时的输出与这次观测证明不了什么。

## C.1 观测表

E1–E6 的观测日期为 2026-11-22；E7–E15 为 2026-11-23。环境同为 Windows，已安装 Orca 1.4.269。

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
- `orca.yaml`、`.worktreeinclude`、`.orca/issue-command` 的生效链路未实测：键、限制与三选按 `docs/site/content/docs/model/orca-yaml.mdx` 陈述，要等一次真实的 `worktree create`。
- `.claude/`、`.codex/` 钩子的执行与 `CLAUDE.md`/`AGENTS.md` 的读取按 `docs/site/content/docs/agents/hooks-memory.mdx` 陈述，未造场景观察。
- `skills install/update/share`、`agent hooks status|on|off`、Settings 各面板未执行、未截图。
- `%APPDATA%\orca` 内的数据库与密钥文件只确认了名字，未打开内容。

## C.4 本篇的边界

观测表是可复现的最小集合，不构成对 Orca 行为的全面验证。E2 与 E7–E10 的输出依赖当次进程与登记状态；E12–E15 的目录条目与技能集合随机器与时间变化。可比较的是字段名与就绪值的含义，不是具体数值。
