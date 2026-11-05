# Omp 插画验收清单

复核日期：2026-11-05（Asia/Shanghai；America/Adak 为 2026-11-04）。负责人：Codex。
本清单记录正文实际引用的资产。重绘过程与 SVG 源稿见 `visual-redesign/README.md`。

## Mermaid 覆盖

| ID | 章节 | 内容 | 状态 |
|---|---|---|---|
| MM01 | ch01 | 模型、工具与观察组成的循环 | fixed |
| MM02 | ch03 | 四种入口共用引擎；另有架构速览 | fixed |
| MM03 | ch04 | 安装路径选择 | fixed |
| MM04 | ch07 | 会话恢复与分支 | fixed |
| MM05 | ch09 | hashline 修改与重读 | fixed |
| MM06 | ch13 | 主任务与子任务 | fixed |
| MM07 | ch15 | 上下文压缩 | fixed |
| MM08 | ch16 | 记忆后端与 retain/recall/reflect | fixed |
| MM09 | ch19 | 技能发现与加载 | fixed |
| MM10 | ch20 | MCP 信任边界 | fixed |
| MM11 | ch28 | SDK、RPC 与 ACP 选型 | fixed |
| MM12 | ch31 | 扩展发现与无扩展复现 | fixed |

正文共 13 个 Mermaid 围栏，分布于 12 章，七篇均有覆盖。语法由
`npm run check:diagrams` 校验，成品渲染与 PDF 抽查见 `ACCEPTANCE.md`。

## 已知问题图

以下 16 张已在此前的插画提交中替换为手写 SVG 导出的 JPG；本轮复核源稿与正文引用。
这里的 fixed 指下表记录的问题已处理，不把缩略图检查当作全书所有文字的逐字 OCR。

| 正文文件（相对 `omp/images/`） | 复核重点 | 状态 | 负责人 |
|---|---|---|---|
| fig23-1-config-layers.jpg | 六层顺序；profile 不另占一层 | fixed | Codex |
| fig9-2-hashline-vs-replace.jpg | 相同文本的歧义；修改前核对位置 | fixed | Codex |
| fig12-3-web-github.jpg | 来源回查顺序；工具名与网址 | fixed | Codex |
| fig9-1-hashline-anchor.jpg | 行锚点与重新读取 | fixed | Codex |
| fig4-3-alpine-pitfall.jpg | Alpine 依赖与重试顺序 | fixed | Codex |
| fig4-4-completions.jpg | 补全命令拼写 | fixed | Codex |
| fig5-3-login-flow.jpg | 登录分支与凭据边界 | fixed | Codex |
| fig5-4-models-yml.jpg | 配置示意与验证命令 | fixed | Codex |
| fig17-1-model-roles.jpg | 模型角色标签 | fixed | Codex |
| fig19-2-skill-invoke.jpg | 元数据发现与正文按需读取 | fixed | Codex |
| fig20-2-mcp-transport.jpg | stdio、HTTP/SSE 传输方向 | fixed | Codex |
| fig21-1-custom-tool.jpg | 描述、实现与工具结果的关系 | fixed | Codex |
| fig22-2-ext-load.jpg | import、factory、initialize、events 顺序 | fixed | Codex |
| fig27-1-review-checklist.jpg | 范围、风险与人工合并检查 | fixed | Codex |
| fig28-1-sdk-embed.jpg | 创建、订阅、提问、释放顺序 | fixed | Codex |
| fig33-3-tool-registry.jpg | 工具注册与可用条件 | fixed | Codex |

本轮缩略图复核材料保存在忽略目录 `.scratch/spec-finish/repaired-figures.jpg`。
正式资产仍是 `omp/images/` 中的 JPG；未将临时预览加入书稿。
