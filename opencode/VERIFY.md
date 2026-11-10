# OpenCode 插件验证记录

基线 v1.19.5，完整提交与来源见 [锁文件](../docs/agent-series/sources.lock.json)。两次实验分别记录，保留各自的证据边界。

## 2026-11-09：处理器与类型

- 读取钉版 V1 类型、加载器、trigger、请求准备与子任务执行路径，核对共享 output、顺序调用、dispose 和缺失结果路径。
- 使用 Node 24.14.0 运行 `node --test opencode/examples/check-review-trace.mjs`：8 项通过。
- 将原创样例复制到临时依赖目录，使用 TypeScript 5.9.3、真实 @opencode-ai/plugin 1.19.5 类型执行 strict/noEmit：通过。skipLibCheck 只跳过依赖声明内部检查。
- 依赖安装使用 ignore-scripts；没有加载上游 CLI 运行时。安装时一个间接依赖报告 Node engines 警告，不能据此声称宿主可在本机 Node 上完整运行。

这次没有加载完整 CLI：SDK 为替身，dispose 为显式调用，最后一个调度器为教学实现。[当日摘要](facts/plugin-sample-20261109.json)保留原始结论，不用后来的实跑结果回填历史。

仓库整体检查：执行 `python scripts/bookctl.py check --fast`，8 个步骤全部通过，包括通用测试 225 项、构建器测试 556 项、内容与 Mermaid 检查，以及衍生页面重复构建的一致性检查。新增处理器测试另接入 Book CI 的 Fast job。

本机 npm ci 两次因下载访问失败未完成；复用了同一锁文件、同一基线工作树中已有的 Node 依赖后运行上述检查。没有修改依赖锁或绕过检查；干净安装由 PR CI 另行验证。

## 2026-11-10：Windows 发布程序与真实插件宿主

从官方 v1.19.5 release 下载 Windows x64 ZIP，核对官方 asset SHA-256 后解压。CLI 的 --version 为 1.19.5；ZIP、exe 与实验脚本摘要见[宿主结果](facts/host-plugins-20261110.json)。

命令：

```powershell
python opencode/examples/check-host-plugins.py --binary .scratch/opencode-bin/opencode.exe --dependency-dir .scratch/plugin-types
```

四个场景全部通过：

| 场景 | 观察结果 |
| --- | --- |
| 显式 B 与目录发现 A | init/config/工具 before/after/dispose 为 B → A；系统提示词进入请求，真实 read 正文进入下一轮请求，reviewTrace 关联成功 |
| 同进程清理后重建实例 | 初始化再次执行，模块级计数从 1 到 2；修改后的源码没有生效；坏插件初始化失败后 B/A 仍完成任务 |
| 重启进程 | 模块级计数回到 1，修改后的提示词生效 |
| --pure | 外部插件无初始化或回调，read 任务仍完成 |

真实 SDK 的 app.log 消息出现在服务端日志中。fixture.txt 的内容在所有场景结束后保持不变；实验事件文件会追加写入。实例清理通过真实 HTTP 端点触发，并等待插件 dispose 事件。

模型协议由本地替身提供，不调用外部模型。宿主环境、配置、缓存、数据库和临时文件均隔离；通过 debug paths 核对路径。依赖目录来自预先安装的真实发布包，本轮未验证首次在线安装。

本次验证的入口是 Windows serve 下的 V1。V2 的 add/remove/wait 和 Scope 仅做钉版源码核对，不据此推断所有客户端或启动选项的默认值。

加入第 9 章后重新运行仓库 Fast：8 步通过，包含通用测试 225 项、构建器测试 556 项、247 份 Markdown 与 360 张 Mermaid，以及衍生页面重复构建一致性检查。8 项处理器测试和中英文结构检查也通过。

## 2026-11-10：原创工具与真实权限队列

使用相同官方 Windows 二进制，加载原创 read-fixture.ts，由本地模型替身发起 book_probe。工具在读取临时 fixture.txt 前调用真实 context.ask；脚本操作真实 permission HTTP 队列，并用 entered/approved/read-done 事件验证执行顺序。

```powershell
python opencode/examples/check-tool-permissions.py --binary .scratch/opencode-bin/opencode.exe --dependency-dir .scratch/plugin-types
```

10 个场景全部通过：allow、deny、ask-once、ask-reject、hidden、once-first、once-new-session、always-first、always-new-session、always-after-dispose。once 在新会话重问；always 在同实例新会话沿用，实例 dispose 后重问。拒绝与隐藏工具时没有读取 fixture。

read-fixture.ts 使用 TypeScript 5.9.3 与真实 plugin 1.19.5 类型执行 strict/noEmit，通过。公开版本、场景与脚本摘要见 [权限实验结果](facts/tool-permissions-20261110.json)。模型协议仍由本地替身提供，不证明真实模型的工具选择能力。

## 仍未验证

TUI、其他平台、自动热重载、异常退出、取消与并发清理、真实模型效果与费用、性能和 V2 运行时。文件监听在本轮被关闭；第 8 章提到的子任务失败后 after 收到 undefined 的整条链仍只有源码与处理器实验。

本册已注册独立产品 opencode，前言、18 章和附录 A–D 均进入装配。产物构建与交付记录见四册任务表。

## 复现与证据

[示例说明](examples/README.md)包含下载校验、依赖准备与两类实验命令。原始请求和日志留在忽略的 .scratch；公开结果只提交版本、摘要、事件名称及已测/未测范围。源码事实可通过两章末尾的固定提交链接复核。


## 本地成品

2026-11-10 已生成 HTML、PDF（99 页）和 EPUB，并校验复制到主工作区 `yuyu-book/dist/`。PDF 包含 29 个书签，EPUBCheck 5.4.0 零错误、零警告。[交付摘要与文件校验值](../docs/agent-series/local-publication-20261110.json)记录这次成品。


## 1.1.0 深化版

正文、前言与附录共约 56,458 个汉字、26 张 Mermaid 图。完整扩写配置合并、会话压缩、SSE、工具适配、审批队列、共享 output、状态归属、MCP/LSP、委派、撤销、SDK 与连续工程练习。

原创 pricing-lab 实际执行 19 项输入案例，已知错误版本有 18 项失败，参考实现零失败。结果与源码摘要见 [价格练习记录](facts/pricing-lab-20261110.json)。它不调用模型。此前 99 页成品属于 1.0.0 初稿，深化版页数以重新构建的交付记录为准。


## 深化版成品交付

v1.1.0 已在本机重建：PDF 150 页、29 个书签；EPUBCheck 5.4.0 零错误、零警告。四册封面、章节排版、目录、示例页与索引已抽查。文件已校验复制到 `D:\Users\claude\claude-code-book-main\yuyu-book\dist`，旧初稿另存 `.ebook-validation-tools/agent-drafts-20261110`。[交付摘要](../docs/agent-series/local-publication-20261110-revised.json)保留大小与 SHA-256。

## 1.1.1 阅读修订

本次修改正文表达与导读，保留既有实验范围。重新生成的 PDF 为 148 页、29 个书签；EPUBCheck 5.4.0 零错误、零警告。代码围栏、图示、行内代码、表格、标题、链接和显式 ID 均与修订前比对一致。[当前交付记录](../docs/agent-series/local-publication-20261110-reading.json)对应主 dist 文件；前述记录保留为历史版本。
