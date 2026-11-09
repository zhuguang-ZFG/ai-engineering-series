# DeepSeek Harness 本地证据

2026-11-10 完成固定源码的 Cordis 组件实验，七项断言全部通过。书稿包含前言、18 章和附录 A–D；正文机制说明固定于 DeepSeek Harness 提交 `fcc0ad462172522aaf5c93a7b2e01f6b9f0b0159`，根包版本 `0.2.2-rc.1`，vendored Cordis `4.1.0`。

运行环境是 Windows、Node.js 24.14.0、tsx 4.23.13，加载下载的上游 TypeScript 源码。实验涵盖必需依赖等待、提供者替换、初始化失败清理、waterfall 顺序、短路与重复 next、父子异步清理和服务域隔离。原创插件只在内存中记录效果，不向外部服务发送消息。

复现入口：[examples/README.md](examples/README.md)。机器可读记录：[facts/cordis-20261110.json](facts/cordis-20261110.json)，其中包含 9 个固定源码文件和 2 个原创运行文件的规范化 SHA-256 摘要、依赖版本、运行命令和逐项结果。

源码与示例的 11 个摘要校验通过，9 个规范化源码文件也逐一匹配固定提交树的 Git blob 身份；书中 30 个唯一源码链接均已与该树核对。核对时修正了最初下载的 logger.ts 编码差异，随后重新运行七项场景，全部通过。准备脚本已改为从 API 的 base64 字段还原原始字节，避免同类差异。

PowerShell 准备脚本通过静态语法检查；本机执行策略禁止运行 `.ps1`，因此该包装脚本没有整体实跑。七项组件结果来自已取得的固定源码，不把脚本语法通过算成端到端准备成功。

Agent、Session、提示词、工具执行管线及应用启动章节依据固定版本源码和上游契约。第 10 章教学工具的 schema 与 `packages/core/tools/src/schema.ts` 核对过，但没有在完整 dsh 宿主集成运行。第 17 章是逐步集成设计，不宣称整套审查助手已经验证。

尚未实跑：完整 dsh Web/SDK/ACP 应用、真实模型、存储崩溃恢复、浏览器重连、远程审批、平台沙箱、npm 对外发布与完整插件升级。这些边界也在书中附录 C 保留，不由成功生成 PDF、EPUB 推导为已验证。


## 本地成品

2026-11-10 已生成 HTML、PDF（92 页）和 EPUB，并校验复制到主工作区 `yuyu-book/dist/`。PDF 包含 29 个书签，EPUBCheck 5.4.0 零错误、零警告。[交付摘要与文件校验值](../docs/agent-series/local-publication-20261110.json)记录这次成品。
