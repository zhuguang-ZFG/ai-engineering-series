# 附录 E 版本追踪

## E.1 当前钉版

<!-- block: pi-apxe.b-b8d4d3db -->
| 项目 | 值 |
| --- | --- |
| 写作钉 | `pi/1.5.0` |
| 提交 | `f9a26365568127461c47a07a37dcb42c140a3ac5` |
| npm | `@earendil-works/pi-coding-agent@1.5.0` |
| 运行时 | Node.js >= 22.19.0 |
| 核对日期 | 2026-11-08 |
| 证据 | `PIN.md`、`VERIFY.md`、`facts/pi-1.5.0/` |

## E.2 发布节奏（已核实）

| 版本 | 发布时间（UTC） |
| --- | --- |
| v1.1.0 | 2026-10-07 |
| v1.2.0 | 2026-10-12 |
| v1.3.0 | 2026-10-15 |
| v1.4.0 | 2026-10-21 |
| v1.5.0 | 2026-11-02 |

不到一个月五个 minor。读任何一章前先跑 `pi --version`。

## E.3 漂移处理

1. **先记录**：`pi --version`、`node --version`、`uname`/系统、日期。
2. **再定位**：这一章的结论依赖哪个文档/命令/默认值？
3. **复跑证据**：能跑的命令重跑；不能跑的标"未验证"。
4. **改三处**：正文 + 该章核对清单 + 本附录（必要时改 `PIN.md`）。
5. **不要**只改正文：只改一处等于制造第二份互相矛盾的"真相"。

## E.4 升级后优先复查的条目

| 条目 | 为什么容易变 |
| --- | --- |
| 默认工具集 | 上游调整 `DEFAULT_TOOL_NAMES` 会改所有工具章节 |
| `agent_end` / `agent_settled` | 生命周期语义一变，脚本与扩展都受影响 |
| 会话版本与条目类型 | v3 迁移、`context_edit` 等都是新机制 |
| `--tools` 语法 | 纯名字 vs `+`/`-` 的规则曾引发真实报错 |
| 压缩默认值 | `reserveTokens` / `keepRecentTokens` 直接影响行为 |
| 主题与 TUI 旗标 | 终端兼容性变动频繁 |
| npm/git 包安装语义 | 版本钉与缓存策略可能调整 |

## E.5 复验清单（每次改钉跑一遍）

```bash
pi --version
node --version
pi --help | sed -n '/Built-in Tool Names:/,$p'
pi --offline --list-models nvidia | head -5
pi --print --no-tools --no-session "只回复：在线"
pi --mode json --no-session --no-tools "只回复：在线" | head -3
pi --nope; echo "exit=$?"
pi --list-models zzzznotfound; echo "exit=$?"
```

期望与 `VERIFY.md` 一致；不一致就按 E.3 处理。

## E.6 改钉记录

| 日期 | 从 | 到 | 改动范围 |
| --- | --- | --- | --- |
| 2026-11-08 | — | `pi/1.5.0` | 首次钉版：PIN、VERIFY、正文试章 |

以后每次改钉在本表追加一行，并同步 `PIN.md` 的登记日期。
