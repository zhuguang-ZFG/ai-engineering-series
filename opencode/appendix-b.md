# 附录 B：配置与命令速查

<!-- block: opencode-apxb.b-opening -->
本附录按任务列出本书实际使用的命令与配置片段。运行路径以书仓根目录为基准；真实项目中的模型认证和目录选择需要按自己的环境配置，不能直接复制实验占位值。

## B.1 安装与版本

下载、ZIP 校验与解压的完整 PowerShell 命令见[示例说明](examples/README.md)。不要省掉校验就运行来源不明的同名程序。

```powershell
.scratch/opencode-bin/opencode.exe --version
.scratch/opencode-bin/opencode.exe --help
```

处理器实验使用 Node 22.19.0 或更新版本；本机记录为 Node 24.14.0。宿主实验需要 Python 3.10 以上和 Git。官方独立 exe 自带自己的运行时，不能拿开发目录 Node 的 engines 警告判断这个 exe 是否能运行。

## B.2 本书实验入口

```powershell
node --test opencode/examples/check-review-trace.mjs
python opencode/examples/check-host-plugins.py --binary .scratch/opencode-bin/opencode.exe --dependency-dir .scratch/plugin-types
python opencode/examples/check-tool-permissions.py --binary .scratch/opencode-bin/opencode.exe --dependency-dir .scratch/plugin-types
```

Python 不使用 `-O`，因为驱动的 assert 承担检查。失败时保留 Evidence 指向的目录，先看相应日志再改源码。不要把失败运行中只完成一部分的 report 当成全通过。

## B.3 常用配置字段

| 字段 | 用途 | 本书中的注意点 |
| --- | --- | --- |
| model | 主任务模型 | 提供者与模型 ID 都需存在 |
| small_model | 小任务模型 | 隔离实验同样指向本地替身 |
| enabled_providers | 启用提供者范围 | 不代替网络级阻断 |
| plugin | 显式插件声明 | 本地路径相对声明配置解析 |
| permission | 工具/操作规则 | allow、ask、deny；顺序影响匹配 |
| instructions | 补充指令来源 | 文本不会变成 OS 权限 |
| snapshot | 文件快照开关 | 关闭时不应依赖对应撤销 |
| mcp | 外部服务配置 | local 进程与 remote 认证分开检查 |

## B.4 宿主实验的隔离项

驱动使用 OPENCODE_TEST_HOME、独立 XDG 数据/配置/缓存/状态路径、OPENCODE_DB 和临时目录。只给子进程保留必要的 Windows 环境与 PATH，不继承个人模型账号、代理和配置变量。第九章实验还检查 debug paths 的输出。

绑定地址为 127.0.0.1，服务端密码随机生成。文件监听、默认插件、模型列表拉取、更新和自动下载等按实验需要关闭。这些设置是为了复现机制，不是替代网络抓包或操作系统隔离。

## B.5 三种本地书籍格式

本书接入公共构建器后，可运行：

```powershell
python scripts/bookctl.py build --product opencode --lang zh --pdf --epub
```

输出前缀为 `yuyu-opencode-zh`，HTML、PDF、EPUB 均位于 `yuyu-book/dist`。PDF 需要可用 Chromium/Edge 与中文字体；EPUB 使用同一份已装配 HTML 生成，正文来源仍为 Markdown。
