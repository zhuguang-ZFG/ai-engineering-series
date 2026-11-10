# Codex CLI 原创示例

固定版本：codex-cli 0.167.0，源码提交 `086ccc833bc9cf01024ad2dd6af7dbd421b6bf9a`。示例围绕一份运费边界错误，连接项目说明、技能/插件、规则、Hook、exec 日志与 app-server 消息。

## 规则与真实 CLI 检查

需要 Python 3.10 或更新版和固定版本原生 Codex 二进制。使用 `--binary` 传原生程序路径，不能传 npm 的 `.cmd` 启动器：

```powershell
python codex/examples/check-local-cli.py --binary PATH_TO_CODEX_EXE
```

本机使用已经安装的 `@openai/codex@0.167.0` Windows x64 平台包。可以先用 `codex.cmd --version` 核对，再定位平台包 vendor 中的原生程序。若自行准备独立安装：

```powershell
npm.cmd install --prefix .scratch/codex-cli --ignore-scripts @openai/codex@0.167.0
```

安装命令需要网络，本轮没有重新验证首次安装。程序摘要是本机测量值，见 [facts](../facts/local-cli-20261110.json)，不冒充官方签名。

驱动先核对版本，再运行六种规则输入、一项错误规则正例，以及一项静态协议生成，共八项。`git push` 等命令只作为策略检查器的输入 token，没有实际执行 Git 操作。schema 生成写入临时目录，不启动 app-server 会话。

脚本仅保留必要子进程环境，不传账号、API key 或代理变量，不修改用户配置。未使用 Python -O；assert 必须保留。证据写到 `.scratch/agent-series/codex-local-*`，包含 report.json、帮助文本和生成 schema。公开 facts 只保存必要结果与摘要。

## 单独检查规则

```powershell
codex.cmd execpolicy check --rules codex/examples/review.rules --pretty git status --short
```

`review.rules` 是教学规则，不是完备的 Git 安全策略。它只覆盖文件中列出的 token 前缀；参数位置、别名、包装脚本和不同可执行文件仍需另外设计。无匹配会省略 decision，不能把它当作 allow。

## 审查技能

[review-change/SKILL.md](review-change/SKILL.md) 是原创方法示例，讲解技能的描述与正文分工。它没有在本轮启动模型会话验证发现或触发，不应被标为已经通过宿主生命周期实验。

## 未覆盖

OS 沙箱执行、真实模型、账号认证、实际审批界面、由 Codex 宿主发现/信任/触发 Hook、MCP 连接、会话恢复和其他平台均未验证。下面直接运行处理器的结果，不替代宿主生命周期实验。

## 运费、Hook 和 JSONL 离线练习

```powershell
python -B codex/examples/check_workshop.py
```

需要 Python 标准库。脚本把 [workshop](workshop/AGENTS.md) 复制到临时目录：先运行错误版测试，确认 1001 克失败，再修正取整并确认通过；不会修改教材模板或读者仓库。随后直接运行 [hook_guard.py](hook_guard.py)，检查正常输入、明确拒绝与损坏 JSON；再检查四种 JSONL/进程组合、坏事件和失败补丁。

[plugin-example](plugin-example/README.md) 提供真实清单、技能、两种 shell 的 Hook 配置和独立处理器文件。驱动核对声明资源存在、打包处理器与已测试脚本一致，不声称完成插件安装或宿主测试。

所有 [fixtures](fixtures/app-server-requests.json) 都是手工编写的教学数据。`fixture-thread` 和零 token 不指向真实模型会话。

```powershell
python -B codex/examples/inspect_exec.py codex/examples/fixtures/exec-success.jsonl --exit-code 0
python -B codex/examples/inspect_exec.py codex/examples/fixtures/exec-command-failed.jsonl --exit-code 0
```

第一条退出 0；第二条保留失败命令并要求审阅，退出 1。完整事件不等于项目任务达成；真实交付还要检查当前差异和项目测试。

## 静态协议与 Hook schema

```powershell
python -m pip install -r codex/examples/requirements.txt
codex.cmd app-server generate-json-schema --out .scratch/codex-schema
python -B codex/examples/check_protocol.py --schema .scratch/codex-schema --hooks-schema PATH_TO_PINNED_SOURCE/codex-rs/hooks/schema/generated
```

额外依赖固定为 jsonschema 4.26.0。检查七份 app-server 参数/结果、错误字段名、两份 Hook 输入/输出和缺少 turn_id 的反例；校验器不会启动连接或模型。固定 Hook schema 从源码提交中获取，脚本不自动下载。

本地实跑结果见 [离线练习](../facts/workshop-20261110.json)与[静态协议](../facts/protocol-20261110.json)。它们分别记录检查项、输入或 schema 摘要及未启动宿主/模型的范围。
