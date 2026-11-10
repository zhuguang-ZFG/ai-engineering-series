# DeepSeek Harness 本地证据

2026-11-10，固定 Cordis 源码上的七项基础实验与十三项连续实例实验全部通过。书稿包含前言、18 章和附录 A–D；源码基线为 DeepSeek Harness 提交 `fcc0ad462172522aaf5c93a7b2e01f6b9f0b0159`，根包版本 `0.2.2-rc.1`，vendored Cordis `4.1.0`。

运行环境是 Windows、Node.js 24.14.0、tsx 4.23.13。两组实验加载上游 TypeScript 源码；原创服务只在内存中处理文本和记录事件。除了基础依赖、清理与 waterfall，连续实例还覆盖双服务等待、输入校验、策略拒绝、任务取消与延迟关闭、旧调用晚到、同名注册冲突、提供者替换、共享服务域、once 递归、serial 截断、parallel 聚合失败和卸载后的注册错误。

复现入口：[examples/README.md](examples/README.md)。原七项记录保留在 [cordis-20261110.json](facts/cordis-20261110.json)，新增十三项记录在 [review-lab-20261110.json](facts/review-lab-20261110.json)。两份记录包含版本、命令、退出码和逐项断言；新增记录另存七条正常业务事件以及本地包摘要。

九个源码文件已经逐一匹配固定提交树的 Git blob 身份。校验脚本同时验证九个源码、两个旧示例、三个新示例文件的规范化 SHA-256，共十四项。源码下载曾出现 logger.ts 编码差异，已经按 GitHub API 的 base64 原始字节修正，随后重新实跑通过。

本地 npm pack 的实际 tarball 只含 README.md、package.json 和 review-lab.mjs。将包解开后，同一实验驱动通过 --lab 加载包内代码，十三项全部通过。这验证分发入口及打包范围，没有向 npm 发布，也没有借此宣称完整 dsh 的插件管理器已经运行。

PowerShell 准备脚本通过静态语法检查；本机执行策略禁止 `.ps1`，所以包装脚本没有整体实跑。组件实验来自已取得并核对过的固定源码，不把脚本语法通过算成环境准备已端到端成功。

Agent、Session、提示词、官方工具执行管线与应用启动章节依据固定版本源码和契约。ReviewTools 与 ReviewJournal 是书中原创业务服务；它们分别帮助理解工具拥有权与事件记录，并没有冒充 dsh-tools 或持久 Session。第 17 章先完整跟读这组可运行实例，再解释接入真正 Agent 与 Session 的位置。

尚未实跑：完整 dsh Web/SDK/ACP 应用、真实模型、存储崩溃恢复、浏览器重连、远程审批、平台沙箱、npm 对外发布与完整插件升级。附录 C 保留对应范围。

本册的离线 source check 已通过：23 个阅读单元、14 张机制图、77 个正文来源链接；Mermaid 解析为 14 图、0 错误。PDF 与 EPUB 由公共出版流程统一重新生成，结果以主仓交付记录为准。


## 深化版成品交付

v1.1.0 已在本机重建：PDF 128 页、29 个书签；EPUBCheck 5.4.0 零错误、零警告。四册封面、章节排版、目录、示例页与索引已抽查。文件已校验复制到 `D:\Users\claude\claude-code-book-main\yuyu-book\dist`，旧初稿另存 `.ebook-validation-tools/agent-drafts-20261110`。[交付摘要](../docs/agent-series/local-publication-20261110-revised.json)保留大小与 SHA-256。

## 1.1.1 阅读修订

本次修改正文表达与导读，保留既有实验范围。重新生成的 PDF 为 125 页、29 个书签；EPUBCheck 5.4.0 零错误、零警告。代码围栏、图示、行内代码、表格、标题、链接和显式 ID 均与修订前比对一致。[当前交付记录](../docs/agent-series/local-publication-20261110-reading.json)对应主 dist 文件；前述记录保留为历史版本。

## 1.1.2 跟做路线与索引

正文补清执行目录、实例状态和首次阅读入口；原有代码与实验范围保持。新版 PDF 为 129 页，EPUBCheck 5.4.0 零错误、零警告。索引完成窄屏、深色和打印布局检查；本地文件摘要见[当前记录](../docs/agent-series/local-publication-20261110-reader-path.json)，前述构建记录为历史版本。
