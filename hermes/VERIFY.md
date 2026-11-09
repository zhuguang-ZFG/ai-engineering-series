# Hermes 本地验证记录

基线：NousResearch/hermes-agent v0.23.0，提交 `2bd378ed1b8d6bf2192cb26e0a55ff3091e6bd19`。日期：2026-11-10。

## 实际运行

在 Windows、Python 3.13.14 上执行 `examples/check_memory_components.py`，8 组检查通过。记录在 [memory-components-20261110.json](facts/memory-components-20261110.json)：冻结提示快照、重复添加与 patch、超预算拒绝、歧义删除、batch 原子性、双目标恢复、损坏编码保护，以及技能 BOM 和目录排除。

存储、扫描、原子写入及技能函数来自上述提交。脚本跳过完整包初始化，替换 `tools.memory_tool` 的目录与操作系统锁入口，并从原文件 AST 提取目标校验函数原样执行。这些是组件测试接缝，未加载完整 Agent。

本机没有完成 `ruamel.yaml` 安装，运行时使用 `--without-yaml`。skill frontmatter 进入真实的简单 key:value 降级分支，复杂 YAML 未验证。MemoryStore 实验不调用 YAML。

原创插件的检查命令：

```powershell
python -m unittest discover -s hermes/examples -p "test_*.py" -v
```

7 项全部通过，其中符号链接创建与排除检查也实际运行通过。它只运行 `book-inventory` 处理器与 FakeContext 注册参数，不启动 PluginManager。运行结果见 [inventory-tests-20261110.json](facts/inventory-tests-20261110.json)。符号链接测试取决于本机创建链接的权限，报告会区分通过与跳过。

## 没有运行的部分

未执行完整 CLI 安装、真实模型任务、完整会话数据库迁移、插件宿主加载/卸载、MCP 服务重连、cron 调度与投递、gateway 平台消息、终端后端矩阵、委派取消和多进程竞争。相应章节以固定源码解释机制，并给出读者可继续执行的实验，未声称这些实验已经完成。

## 整书装配

书稿包含前言、18 章与附录 A–D，采用 `yuyu-book/manifest-hermes.json` 以及 Hermes 专属来源、阅读路径、术语索引和修订记录。装配检查命令为：

```powershell
python scripts/bookctl.py build --product hermes --lang zh --check --mermaid source
```

最终 HTML、PDF、EPUB 由主任务统一构建。仅有书稿或装配检查通过，不能据此声称成品已经生成；具体文件以主工作区 `yuyu-book/dist/` 为准。


## 本地成品

2026-11-10 已生成 HTML、PDF（90 页）和 EPUB，并校验复制到主工作区 `yuyu-book/dist/`。PDF 包含 29 个书签，EPUBCheck 5.4.0 零错误、零警告。[交付摘要与文件校验值](../docs/agent-series/local-publication-20261110.json)记录这次成品。
