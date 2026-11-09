# Codex CLI 原创示例

固定版本：codex-cli 0.167.0，源码提交 `086ccc833bc9cf01024ad2dd6af7dbd421b6bf9a`。本目录包含命令策略规则、真实 CLI 检查器，以及一个用于讲解的审查技能。

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

OS 沙箱执行、真实模型、账号认证、实际审批界面、Hook 执行、MCP 连接、会话恢复和其他平台均未在这组实验中验证。静态 schema 与帮助输出不能替代这些运行证据。
