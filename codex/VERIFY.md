# Codex CLI 验证记录

日期：2026-11-10。基线：rust-v0.167.0，提交 `086ccc833bc9cf01024ad2dd6af7dbd421b6bf9a`。

## 已完成

读取固定提交的 CLI、exec 参数与运行入口、项目指令、配置、execpolicy、app-server、插件清单、Hook 发现/信任与技能入口。官方当前文档通过 Context7 读取，和钉版事实分开引用；直接网页抓取失败，未声称保存了官网快照。

本机 npm 与 Windows x64 原生程序版本均为 0.167.0。真实 CLI 运行八项检查全部通过：

| 检查 | 结果 |
| --- | --- |
| git status 前缀 | allow |
| git diff 前缀 | allow |
| git push 前缀 | prompt |
| git push --force 前缀 | forbidden，保留两条命中 |
| 未列出的 git commit | matchedRules 为空、无 decision |
| 绝对路径 git.exe | 默认检查无匹配 |
| 错误的 match 正例 | CLI 非零退出 |
| app-server 静态 schema | 生成 322 份 JSON，包含四个关键方法 |

运行命令和驱动见 [examples](examples/README.md)，脱敏结果见 [facts](facts/local-cli-20261110.json)。程序与输入文件摘要记录在结果中。没有执行示例中的 Git 推送，没有创建代理任务会话，没有调用外部模型。

## 未验证

首次在线安装、真实认证与模型请求、完整代码修复任务、审批 UI/自动审查、平台沙箱文件和网络边界、Hook 运行与取消、MCP、resume/fork、跨平台行为。正文中的这类内容分别以源码解释、官方说明和读者实验设计呈现。

## 书稿与构建

中文正文包含前言、18 章及附录 A–D，共 23 个阅读单元。专属 manifest、来源、阅读路径、索引与修订表已准备。整书装配检查通过：23 个单元、11 幅图、69 条引用链接，内部链接和脚注 ID 检查通过。

装配命令：`python scripts/bookctl.py build --product codex --lang zh --check --mermaid source`。本地 HTML/PDF/EPUB 由统一构建主线生成并检查，最终文件位于主工作区 `yuyu-book/dist/`；实际产物状态以主线交付记录为准。


## 本地成品

2026-11-10 已生成 HTML、PDF（96 页）和 EPUB，并校验复制到主工作区 `yuyu-book/dist/`。PDF 包含 29 个书签，EPUBCheck 5.4.0 零错误、零警告。[交付摘要与文件校验值](../docs/agent-series/local-publication-20261110.json)记录这次成品。
