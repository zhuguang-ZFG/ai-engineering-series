# 附录 B：配置与命令速查
<!-- block: hermes-apxb.b-opening -->
速查表的用途是把你带回正确的配置入口。它不能替代本机帮助，也不能证明模型、平台账户或终端后端已经可用。操作前先确认 profile，尤其是在同一台机器上既有日常助手，又有书中实验环境的时候。

## B.1 四个目录不要认成一个
| 位置 | 主要保存什么 | 操作时最容易混淆的事 |
| --- | --- | --- |
| 源码目录 | 程序与随项目发布的资源 | 检出新提交不等于迁移旧用户数据 |
| 当前工作目录 | 这次任务要读写的工程 | 改工作目录不自动切换全部用户配置 |
| Hermes home | 配置、记忆及其他持久状态 | 必须在初始化相关模块之前指定 |
| 工具后端工作目录 | 实际执行命令时的文件系统 | 远程或容器中的路径不一定存在于宿主 |

PowerShell 中可以为一个新终端会话设置独立实验目录：

```powershell
$env:HERMES_HOME = Join-Path $PWD ".hermes-book-lab"
hermes --help
```

这是进程环境设置；如果其他进程早已启动，它们不会因此自动改用新目录。实验完毕可以关闭该终端，也可以用 Remove-Item Env:HERMES_HOME 清除当前进程环境变量，再启动日常会话。不要把家目录或整个用户配置目录当成临时垃圾目录删除。

## B.2 原创插件的配置形状
第 9 章的 book-inventory 放在当前 Hermes home 下的 plugins/book-inventory 中。钉版 get_config 从 plugins.entries 中找到插件条目，再读取 settings；config 子树作为旧格式兼容路径存在。新示例使用 settings。

```yaml
plugins:
  enabled:
    - book-inventory
  entries:
    book-inventory:
      settings:
        root: D:/agent-labs/aurora
```

这个根目录要由你预先创建并放入测试 Markdown。示例故意不以空字符串或当前目录作为默认可读位置；缺少 root 时，注册应失败并说明原因。否则一次拼写错误可能让工具转而扫描启动目录，产生看似合理却来自错误工程的清单。

插件名单可能已经包含其他插件。把示例合并进已有配置，不要整段覆盖原文件。disabled 名单优先于 enabled，某插件同时在两边时不会因“已经启用”而强行加载。项目内 .hermes/plugins 还有 HERMES_ENABLE_PROJECT_PLUGINS 门控，本书示例使用用户插件目录，避免把两种来源混起来。

## B.3 Memory 工具与磁盘文件
memory 工具的 target 区分 memory 与 user。钉版默认预算分别为 2200 与 1375 字符；字符数不是 token 数，也不是文件字节数。存储层使用分隔符区分条目，批量编辑和精确匹配都依赖这种条目结构。

添加项目事实时先写出项目与适用条件，例如“Aurora 的公开文档以 release-notes.md 为准”。只写“以 release-notes.md 为准”会让这条记忆脱离来源，后续换一个项目时仍可能被误用。用户偏好也应保留条件，例如“讲解代码时先给可运行最小示例”，而不是无条件“回答越短越好”。

工具中的 patch 用于修改匹配文本；删除时先确认命中的是唯一条目。存储层的 replace 表面与当前工具公开 schema 不应混用，不能因为看到一个 Python 方法就臆造同名的模型工具动作。

## B.4 排错时保留的最小信息
| 症状 | 先记录什么 | 对应章节 |
| --- | --- | --- |
| 已保存但下一句没使用 | 写入结果、当前会话、新会话差异 | 第 4 章 |
| 找不到技能 | 搜索根、技能目录、元数据与排除目录 | 第 5 章 |
| 插件没出现 | 来源、有效插件键、启用与禁用名单、加载错误 | 第 9 章 |
| 定时结果重复 | job 标识、领取时间、运行记录、投递结果 | 第 11 章 |
| 消息进入错误对话 | 平台、账户、聊天、线程和会话键 | 第 12 章 |

共享排错记录时删去凭据、真实用户标识及不相关对话。保留结构和合成值，通常已经足够定位路由或匹配问题。

固定来源：[home 解析](https://github.com/NousResearch/hermes-agent/blob/2bd378ed1b8d6bf2192cb26e0a55ff3091e6bd19/hermes_constants.py)、[配置读取](https://github.com/NousResearch/hermes-agent/blob/2bd378ed1b8d6bf2192cb26e0a55ff3091e6bd19/hermes_cli/config.py)、[插件配置与注册](https://github.com/NousResearch/hermes-agent/blob/2bd378ed1b8d6bf2192cb26e0a55ff3091e6bd19/hermes_cli/plugins.py)、[发现门控](https://github.com/NousResearch/hermes-agent/blob/2bd378ed1b8d6bf2192cb26e0a55ff3091e6bd19/hermes_cli/plugins_discovery.py)。
