# 附录 C：实验记录与复现边界

<!-- block: grok-apxc.b-opening -->
哪些结论来自实测、哪些来自源码、哪些只是文档这么说，这本书分开记，免得把三者混成一种证据。

## C.1 三类证据

| 类别 | 怎么得到的 | 能支撑什么 |
| --- | --- | --- |
| 实测 | 在本机运行 `python grok/examples/...` 并保留输出 | 脚本行为、用例判定、退出码 |
| 源码 | 读固定 `SOURCE_REV` 下的 Rust 文件 | 目录分工、配置层实现、会话落盘字段名 |
| 文档 | 读仓内 `docs/user-guide/` 与 `docs.x.ai` | 命令形式、配置项含义、支持范围 |

三类都不能互相顶替。文档说某个开关存在，不等于它在你这个版本上生效；源码里有某个函数，不等于发布程序调用了它。

## C.2 本机实测过的部分

```powershell
python grok/examples/check_release.py          # exit 1
python grok/examples/check_release.py --fixed  # exit 0
python -m unittest discover -s grok/examples -p "test_*.py" -v
```

故障版有 3 个用例与预期不符（`numeric_order`、`missing_section`、`failed_suite`），修好版 0 个；单元测试 3 条全绿。这些结果只依赖 Python 3.12 标准库，与 Grok 是否安装无关。

## C.3 没有实测的部分

| 项目 | 原因 | 书中怎么写 |
| --- | --- | --- |
| `grok` 命令的实际输出 | 写作机器上没有安装该程序 | 只写文档给出的命令形式，并注明未运行 |
| TUI 快捷键与鼠标行为 | 同上 | 只写用户手册列出的键位 |
| 沙箱在三大平台上的具体隔离 | 需要真实宿主 | 只写配置项与文档声明的范围 |
| 无头模式的退出码约定 | 文档未给出完整表 | 不写推断值，需要时自己跑一次记录 |

## C.4 复现他人的结果时

先固定三件事：`SOURCE_REV`（源码版本）、`grok --version`（发布版本）、运行日期。三者对齐之后，再看别人写的输出是否成立。缺少其中任何一个，结论只能算「某人某天的机器上这样」。

版本变化最常改的是默认值：某个模式默认放行什么、压缩阈值是多少、哪个工具默认需要审批。读到与本文不同的默认行为时，先怀疑版本，再怀疑自己。

## C.5 缺陷与讨论去哪找

`xai-org/grok-build` 是只读镜像：Issues 与 Pull requests 都已关闭，仓库页只剩 Code、Security and quality、Insights 三个页签，`/issues/new` 返回 404。`plugin-marketplace` 的 issue #562 正文里有一句现成的说明：「`xai-org/grok-build` has GitHub Issues disabled (`has_issues=false`)」。`CONTRIBUTING.md` 另外写着：

> This repository does not accept external pull requests or unsolicited patches.

安全报告走 `SECURITY.md` 指定的 HackerOne，并明确要求不要开公开 issue。于是想知道缺陷的人得换地方：

| 想知道什么 | 去哪 | 一条真实例子（2026-11-13 打开） |
| --- | --- | --- |
| 行为变没变 | `https://x.ai/changelog/build` | 1.0.75 条目：权限规则加载失败时，现在会在会话打开时给出警告，而不是静默跳过 |
| 插件、hook、无头模式的问题 | `xai-org/plugin-marketplace`、`xai-org/grok-build-plugin-cc` | #209（打开）非默认权限模式下特权工具全部失败；#236（已关闭）插件 hooks 显示已信任却从不派发；#31（打开）无头模式加 `--model` 卡在 `user_intake`；#2013（打开）1.0.77 在 Windows PowerShell 下 `/personas` 挂起 |
| 社区怎么看 | Hacker News | 48926590（2026-07-15，590 分）开源公告；48877371（2026-07-12，539 分）线缆级流量分析 |

两个相邻仓库自己也开着 Issues（`grok-build-plugin-cc` 页头显示 Issues 28、Pull requests 23），所以「不接受外部 PR」只针对主仓镜像，不是整个组织。

三类东西的可信度不同：changelog 是官方条目，相邻仓库的 issue 是官方项目里的用户报告，Hacker News 是社区帖。写报告时标出类别；也别把「已关闭」读成「已修复」，这类仓库关 issue 可能只是关了讨论。
