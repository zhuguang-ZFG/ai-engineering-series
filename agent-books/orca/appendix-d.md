# 附录 D：术语与常见误解

<!-- block: orca-apxd.b-opening -->
本篇把容易混淆的名字排成对照表，每条给出误解与正确读法。

## D.1 三个程序

| 名字 | 指什么 | 常见误解 |
| --- | --- | --- |
| `Orca.exe` | 桌面应用，界面与工作区在这里 | 以为它同时是命令行 |
| `orca` | 命令行启动器，装在 `resources/bin/` | 以为装了桌面版就没有命令行 |
| `orcad` | 运行时，会话与工作树跑在里面 | 以为关掉窗口它就停了 |

`orca status` 里的 `appRunning` 与 `runtimeState` 是两个字段，正好对应第一行与第三行：应用可以关掉而运行时仍在，反过来也成立。

## D.2 会话与工作树

`worktree`（工作树）是同一个仓库切出来的独立目录，让并行的 Agent 各改各的。它不是分支的同义词：切工作树通常伴随一个分支，但两者不是一回事。

`graphState` 说的是工作树与依赖图是否就绪，不是模型是否可用。模型问题与工作树问题在状态字段上分得开，排查时不要混在一起。

## D.3 技能与插件

| 一组命令 | 管什么 | 不要混用 |
| --- | --- | --- |
| `skills installed/list/get/install/update/share` | 随包技能与分发 | 不是插件 |
| `plugin create/validate/inspect/test/check/list` | 插件的开发与校验 | 不是技能商店 |

随包技能清单在安装目录 `skills/current-manifest.json`，字段 `schemaVersion` 为 `3`，逐项带 `packageDigest` 与文件的 `exactSha256`。这份清单的作用是判断技能是否被换过，不是列出你能装什么。

## D.4 版本号

三个数字各指一处：`app.asar` 的版本是你正在跑的，发布 tag 是发布流水线打的，仓库 `package.json` 的 `version` 只是主干上一次提交留下的字段。三者不一致时，以 `app.asar` 或 `orca --version` 为准。

不要把仓库 `package.json` 的版本当成「最新版」。想知道最新发布了什么，看发布页的 tag。

## D.5 本篇的边界

本篇只收第 1 章出现过的术语。编排、bot、计算机操作等后续章节的名词在对应章节的术语小节里补出，此处不预判定义。
