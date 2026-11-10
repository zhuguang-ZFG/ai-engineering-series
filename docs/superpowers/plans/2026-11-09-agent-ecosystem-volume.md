# 实施计划：四本 Agent 分册

[规格](../specs/2026-11-09-agent-ecosystem-volume.md) · [任务状态](../../agent-series/tasks.json) · [分册入口](../../agent-series-research.md)

2026-11-10 按用户要求改为并行：主代理负责 OpenCode 与公共出版流程，三位子 agent 分别负责 DeepSeek、Hermes、Codex。原先的阅读顺序不再阻塞后续分册写作。

## 正文与实验

- [x] 固定四册实际 commit、许可证与来源，不混淆 tag object。
- [x] OpenCode：前言、18 章、A–D；8 项处理器检查、4 个 Windows V1 宿主场景、10 个工具权限场景。
- [x] DeepSeek：前言、18 章、A–D；真实 vendored Cordis 的 7 个注入、失败、卸载与重挂场景。
- [x] Codex：前言、18 章、A–D；固定 CLI 的 execpolicy 与 app-server schema 实验。
- [x] Hermes：前言、18 章、A–D；隔离记忆/会话实验与插件示例收尾。

每册明确区分源码观察、组件实验、真实宿主和供读者练习的任务。取消、跨平台沙箱、外部 MCP/LSP、完整模型改码和长期 cron/gateway 运行等未实跑项目保留在各册 VERIFY，不计入首版已验证结果。

## 出版与交付

- [x] 注册四册产品、配置独立元数据及输出前缀。
- [x] 支持源 Markdown 相对链接转书内跳转、18 章自动交叉引用及重复引用脚注。
- [x] CI 增加四册独立 PDF/EPUB 构建和成品 artifact，PR 同样执行。
- [x] 四册实际生成 HTML、PDF、EPUB，检查目录、书签、代码、图示和 EPUBCheck。
- [x] 验证后复制 12 份成品到主工作区 yuyu-book/dist。
- [x] 仓库 Fast、内容和元数据检查通过；同步任务记录。
- [ ] 提交、推送、PR CI 全绿后合并，核对 main 的 Book CI 与 Pages。

旧 P6 视频媒体验收仍未完成，不由书籍构建代替。


## 2026-11-10 深化修订

- [x] 根据用户对内容与视觉的反馈，四册全章扩写连续实例、源码机制与失败恢复，保留真实证据范围。
- [x] 四册各自设计架构封面，更新章节排版与配色，增加时序和状态图。
- [x] 重新生成并检查全部 HTML/PDF/EPUB，旧初稿另存，新版复制至主 dist。
- [ ] 深化版提交后完成 CI 与合并。
