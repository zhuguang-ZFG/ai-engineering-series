# Hermes 本地验证记录

基线：NousResearch/hermes-agent v0.23.0，提交 `2bd378ed1b8d6bf2192cb26e0a55ff3091e6bd19`。日期：2026-11-10。中文深化版 0.2.0。

## 上游组件：17 项通过

Windows、Python 3.13.14：

```powershell
python hermes/examples/check_memory_components.py --upstream .scratch/upstream/hermes/components --without-yaml
```

`--upstream` 也可指向附录 A 的完整固定提交检出。结果在 [memory-components-20261110.json](facts/memory-components-20261110.json)，包括初始八项，以及双对象先后写入、陈旧审批目标、精确匹配优先、重复片段拒绝、BOM/重复项规范化、超长条目备份、整理失败上限、写入异常与最终批处理预算。

MemoryStore、扫描、原子写入及技能函数来自固定源码。脚本绕过完整包初始化，给 `tools.memory_tool` 提供实验目录与真实操作系统锁入口；目标校验函数从原文件 AST 原样提取执行。本机未安装完整 YAML 依赖，`--without-yaml` 使 skill frontmatter 使用真实的简单 key:value 降级分支，复杂 YAML 未验证。

双对象测试是确定性交错，不是多进程同时争用。写入失败测试在 `atomic_write_text` 入口注入 OSError，实际观察到磁盘旧内容保留、对象活列表已变化，重新加载后恢复一致；不是断电实验。测试基础预算为 memory 100、user 70 字符，部分非预算场景使用 memory 500 字符。

## 原创程序：15 项测试与八步 CLI 流程

```powershell
python -m unittest discover -s hermes/examples -p "test_*.py" -v
python hermes/examples/check_aurora_workflow.py
```

测试分为 9 项 book-inventory 插件检查和 6 项 Aurora 项目检查，结果见 [example-tests-20261110.json](facts/example-tests-20261110.json)。符号链接用例本机实际运行通过，无跳过。注册检查使用 FakeContext，只覆盖原创插件传参与拒绝处理，不证明真实 PluginManager 加载/卸载。

八步驱动通过真实子进程调用原创检查器，覆盖正常输入、改名断链、修复、示例扫描、归档扫描、配置失败、恢复与相同输入重跑。结果在 [aurora-workflow-20261110.json](facts/aurora-workflow-20261110.json)，每步保存退出码、stdout 和磁盘报告，确认配置失败时旧报告未被覆盖。

## 未执行范围

没有运行完整 CLI 安装、真实模型三会话任务、会话数据库迁移、插件宿主生命周期、MCP 重连、cron 调度/投递、gateway 平台消息、终端后端矩阵、委派取消和多进程竞争。相关章节提供钉版源码解释与后续实验方案。原创程序仅处理所述简单 Markdown 与受控目录，不是完整 CommonMark 解析器或操作系统隔离方案。

## 整书检查

前言、18 章与附录 A–D 由 Hermes 专属 registry 装配。命令：

```powershell
python scripts/bookctl.py build --product hermes --lang zh --check --mermaid source
```

PDF/EPUB 由主任务统一生成；本轮子任务只修改书稿、示例、证据和专属元数据，保留已有初稿产物。

本轮直接模块装配检查使用 `python -m yuyu_book --manifest manifest-hermes.json --sources sources-hermes.json --lang zh --check --mermaid source`。17 张 Mermaid 图另用仓库钉版解析器逐张解析；源码与示例通过 `git diff --check`。


## 深化版成品交付

v0.2.0 已在本机重建：PDF 128 页、29 个书签；EPUBCheck 5.4.0 零错误、零警告。四册封面、章节排版、目录、示例页与索引已抽查。文件已校验复制到 `D:\Users\claude\claude-code-book-main\yuyu-book\dist`，旧初稿另存 `.ebook-validation-tools/agent-drafts-20261110`。[交付摘要](../docs/agent-series/local-publication-20261110-revised.json)保留大小与 SHA-256。
