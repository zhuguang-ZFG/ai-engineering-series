# 附录 A：固定版本与源码导航

<!-- block: codex-apxa.b-opening -->
本书固定 Codex CLI 0.167.0 与完整源码提交；导航按问题组织，帮助读者从行为回到实现。

## A.1 版本身份

上游仓库为 `openai/codex`，发布标签 `rust-v0.167.0`。实际提交是 `086ccc833bc9cf01024ad2dd6af7dbd421b6bf9a`；annotated tag 对象为 `cb41599ccbe371272892f156286a236aa097bada`。正文实现链接使用前者，不把标签对象当作可以浏览源码的提交。

本机 npm 包与 CLI 输出均为 0.167.0。Windows x64 原生程序 SHA-256 为 `edfdd48f8b458af0906e507b4cb05217b326c3d6e515e9f024e05e3b8d650f70`。它是本机已安装文件的测量值，用于识别文件，不是上游发布站点提供的签名或摘要。

上游代码采用 Apache-2.0。本书提供原创讲解、规则、技能与检查驱动，引用固定源码链接；上游大份源码与二进制只缓存在忽略目录，没有打包进书仓。

## A.2 按问题找文件

| 要查的问题 | 固定源码位置 |
| --- | --- |
| 命令如何分发 | `codex-rs/cli/src/main.rs` |
| exec 支持哪些参数 | `codex-rs/exec/src/cli.rs` |
| 无交互请求与审批怎样处理 | `codex-rs/exec/src/lib.rs` |
| AGENTS.md 怎样发现 | `codex-rs/core/src/agents_md.rs` |
| 配置与管理要求如何进入运行时 | `codex-rs/core/src/config/mod.rs` |
| 规则语法与匹配语义 | `codex-rs/execpolicy/README.md` |
| app-server 特定协议约束 | `codex-rs/app-server/README.md` |
| 插件可以携带哪些资源 | `codex-rs/plugin/src/manifest.rs` |
| Hook 事件名称 | `codex-rs/hooks/src/lib.rs` |
| Hook 来源如何合并 | `codex-rs/hooks/src/engine/discovery.rs` |
| 插件 Hook 如何核对信任 | `codex-rs/hooks/src/engine/plugin_trust.rs` |
| 技能注入的运行入口 | `codex-rs/core/src/skills.rs` |

以上路径已在固定提交下读取核对，各章另附具体实现位置。目录链接供继续阅读，平台运行范围见附录 C。

## A.3 滚动官方文档怎么用

官方 CLI 文档位于 `developers.openai.com/codex/cli/`，学习文档包括 `learn.chatgpt.com/docs/app-server` 和 `learn.chatgpt.com/docs/hooks`。页面内容通过 Context7 读取，访问日期为 2026-11-10；直接网页下载在当时的网络环境中失败，因此未将本地 HTML 作为依据。

滚动文档说明当前产品用法，固定源码对应本书版本。遇到审批值、Hook 事件或历史分页字段不同，先核对各自版本，再选择与运行程序一致的接口。

## A.4 升级时更新哪些记录

先解析新标签对应提交，再确认二进制版本；然后复跑规则与 schema 实验，比较输出。涉及平台沙箱、真实模型或外部服务时，另建运行记录，不把旧结果复制过去。最后更新正文、来源注册表、验证记录和书籍版本。

如果只更新其中一处，会出现正文说新版本、实验仍来自旧程序的情况。维护书稿时应让每条技术结论能找到版本与证据，避免把“当前”当成没有日期的永久事实。

## 固定入口

技能、插件、Hook 和 JSONL 的具体入口如下：

| 研究问题 | 固定源码路径 |
| --- | --- |
| 技能元数据与目录扫描 | `codex-rs/skills/src/parser.rs`、`codex-rs/ext/skills/src/loader/discovery.rs` |
| 原始插件路径如何解析 | `codex-rs/core-plugins/src/manifest.rs` |
| Hook 精确候选与正则 | `codex-rs/hooks/src/engine/matcher.rs` |
| schema 之后的输出语义 | `codex-rs/hooks/src/engine/output_parser.rs` |
| 多 Hook 拒绝与改写汇总 | `codex-rs/hooks/src/events/pre_tool_use.rs` |
| 并发、超时与进程 | `codex-rs/hooks/src/engine/dispatcher.rs`、`command_runner.rs` |
| 包内容变化怎样影响信任 | `codex-rs/hooks/src/engine/plugin_fingerprint.rs`、`plugin_trust.rs` |
| exec JSONL 的真实字段 | `codex-rs/exec/src/exec_events.rs` |

[源码根](https://github.com/openai/codex/tree/086ccc833bc9cf01024ad2dd6af7dbd421b6bf9a)、[发布标签](https://github.com/openai/codex/releases/tag/rust-v0.167.0)、[本册验证](appendix-c.md)。
