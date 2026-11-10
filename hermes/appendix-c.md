# 附录 C：实验复现与验证范围
<!-- block: hermes-apxc.b-opening -->
本书实际运行了上游记忆存储和技能元数据组件、原创插件的离线处理器，以及 Aurora 资料库的八步命令行流程。没有连接付费模型，也没有向真实聊天平台发消息。这使若干细节可以反复检查，但它不能证明完整 Hermes 宿主在当前机器上已经安装成功。

## C.1 准备源码与脚本
先按附录 A 检出固定提交，在本书仓库根目录运行：

```powershell
python hermes/examples/check_memory_components.py --upstream ../hermes-agent-reference --without-yaml
python -m unittest discover -s hermes/examples -p "test_*.py" -v
```

把 upstream 参数改成自己的检出目录。脚本使用仓库内新建的 .scratch/agent-series/hermes-memory-* 目录，不读取日常 profile。每次运行使用新目录，避免前一次留下的数据让一个错误实现碰巧通过。

本次执行环境是 Windows、Python 3.13.14。上游依赖下载未完成，因此采用 without-yaml 路径。该选项使技能元数据解析器走上游已有的简单 key:value 降级解析，只覆盖简单标题、名称和描述；它不证明复杂 YAML、嵌套结构或多行标量能够正确解析。安装好正常依赖后可去掉这个选项另跑一次，两个结果应分开记录。

## C.2 基础组件结果与新增场景
| 情况 | 实际观察 |
| --- | --- |
| 新增一条 memory | 磁盘文件包含新值，当前系统提示快照保持不变，新 store 重新加载后包含新值 |
| 重复添加并 patch | 完全重复的添加不增加条目，patch 保留条目中其余上下文 |
| 超出字符预算 | 返回失败，原文件的字节内容不变 |
| 用歧义子串删除 | 不擅自选择两个不同条目中的一个 |
| batch 的后一个操作失败 | 前一个操作也不落盘 |
| 精确删除后重新加载 | memory 和 user 两个目标恢复为预期内容 |
| 文件包含无效 UTF-8 | 拒绝新写入，原始文件没有被清空 |
| 技能正文带 BOM、支持目录带 SKILL.md | BOM 得到处理，references 等支持目录及 .git 不作为独立技能来源 |

为了触发预算边界，实验分别使用 100 和 70 字符的小预算。这是测试条件，不是产品默认配置。原始报告及每个上游文件的 SHA256 保存在 hermes/facts/memory-components-20261110.json；实验脚本的哈希也一并记录，便于区分后来修改的脚本。

## C.3 哪些代码原样运行，哪些地方作了适配
MemoryStore、威胁模式扫描、原子写入函数、home 解析和 skill_utils 来自固定提交，未修改其实现。实验建立 tools 与 agent 的包命名空间，跳过完整应用的包初始化。tools.memory_tool 由轻量入口代替，只提供实验目录与真实操作系统文件锁模块。

存储组件还依赖 memory_tool 中的目标校验函数。脚本从原文件 AST 中提取这一个函数，原样编译执行，避免连带导入工具注册、审批等无关入口。这样既保留了实际目标校验，又没有把几十个没有参与检查的应用依赖装成必要前提。读者应清楚，这仍然是一种组件测试接缝，完整包导入失败不在它的覆盖范围内。

without-yaml 注入的模块没有伪造 YAML 解析成功；它使 safe_load 导入失败，由上游技能函数进入自己的降级路径。记忆实验只使用纯文本存储和原子写入，没有调用 YAML 编解码。将这个结果写成“技能 YAML 全面兼容”会超出证据。

## C.4 插件示例验证什么
book-inventory 的处理器只接受空参数，扫描操作者配置的目录，返回相对路径清单。离线检查使用临时目录，覆盖正常文件、错误根目录、数量上限、参数拒绝和注册参数。环境允许创建符号链接时，还检查链接目录与链接文件不会被枚举；权限不允许时明确跳过这一项。

测试中的 FakeContext 只保存传给 register_tool 的参数。它没有模拟真实 PluginManager，不会执行发现门控、profile 路由、工具集装配或卸载。因而测试通过后，完整宿主实验仍需分别观察“插件被发现”“注册成功”“本轮请求可见”“调用得到结果”四个位置。

还没有执行的项目包括真实模型往返、完整会话数据库迁移、插件卸载与强制重载、MCP 断线恢复、cron 调度、gateway 投递、跨平台终端后端、委派取消和多进程竞争。相关章节给出了实验设计与源码依据，不能把设计中的预期结果当作本次实测。

## C.5 九项新增存储实验
深化版将组件驱动扩展到 17 项。新增部分没有换用一个重写的记忆实现，仍调用同一提交的 MemoryStore：两个旧对象先后追加时保留对方内容；审批目标在等待期间变化后拒绝旧修改；完整条目优先于子串；同一条目内重复片段拒绝 patch；BOM 和重复项在对象里规范化但只读解析不改磁盘；超长外部条目在删除前留下备份；连续整理失败达到终止响应；写入异常后磁盘与活列表分歧；batch 按最终内容判断预算。

双对象实验采用人为安排的顺序，能够验证锁内重读的效果，却没有同时启动多个进程争用文件。写入故障则明确在 atomic_write_text 入口注入 OSError，验证的是上层异常处理，不是断电或 rename 中途的文件系统耐久性。报告逐项写明了这些条件。

大部分边界实验使用 100 字符预算；双对象、匹配和写入故障等场景使用 500 字符，以免预算干扰被研究的行为。user 基础实验仍使用 70 字符。真实默认值不因测试条件而改变。

## C.6 Aurora 与插件的复现命令
```powershell
python hermes/examples/check_aurora_workflow.py
python -m unittest discover -s hermes/examples -p "test_*.py" -v
```

第一条执行八步真实本地 CLI 流程：初始检查、改名断链、修复索引、示例扫描、归档扫描、错误配置、恢复、重复相同输入。程序通过子进程运行检查器，核对 0、1、2 三种退出码，并确认配置错误时没有覆盖旧报告。完整合成输入与每步结果在 facts/aurora-workflow-20261110.json。

第二条包含 6 项 Aurora 行为测试与 9 项插件测试，合计 15 项。本机的符号链接测试实际运行通过，没有跳过。插件注册检查使用 FakeContext，真实 PluginManager、工具集装配和卸载仍在未执行范围内。

源码教材中的代码片段有三类：随书原创程序可直接运行；从真实驱动摘出的 MemoryStore 调用需要驱动的导入准备；cron 存储 API 片段需要完整上游环境与独立 profile。正文在各自位置说明前提，不把三类片段合成一个含糊的“复制即可运行”。

固定来源：[存储实现](https://github.com/NousResearch/hermes-agent/blob/2bd378ed1b8d6bf2192cb26e0a55ff3091e6bd19/tools/memory_tool_store.py)、[目标校验与工具入口](https://github.com/NousResearch/hermes-agent/blob/2bd378ed1b8d6bf2192cb26e0a55ff3091e6bd19/tools/memory_tool.py)、[技能解析](https://github.com/NousResearch/hermes-agent/blob/2bd378ed1b8d6bf2192cb26e0a55ff3091e6bd19/agent/skill_utils.py)。
