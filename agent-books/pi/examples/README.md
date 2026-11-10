# 插件章节的可运行示例

`git-status.ts` 是第 15 章的完整扩展。它使用当前会话目录执行固定的只读 Git 命令，处理取消、失败和结果截断。通过 Pi 加载：

```bash
pi -ne -e ./pi/examples/git-status.ts --tools book_git_status
```

以下检查不启动模型。它们需要 Node.js 22.19.0 或更新版、Git，以及本机 Pi 1.5.0 安装包。`PI_PACKAGE` 是包含 `package.json`、`dist/`、`docs/` 的 `@earendil-works/pi-coding-agent` 目录；`PURGE_CHECKOUT` 是 pi-purge 固定提交的源码目录。

```bash
node pi/examples/check-git-status.mjs "$PI_PACKAGE"
node pi/examples/check-purge.mjs "$PURGE_CHECKOUT" "$PI_PACKAGE"
```

PowerShell 中可直接把两个参数写成引号包围的绝对路径，无需设置这些变量。受限 Windows 环境若 Node 的路径解析在用户目录报 `EPERM`，本书验证时使用 `node --preserve-symlinks ...`，不需要改变全局配置。

`check-git-status.mjs` 使用宿主的真实 TypeBox 和 `execCommand()`，在临时 Git 仓库检查 6 种情况。为了在普通 Node 里加载例子，脚本只在临时副本中把 `typebox` 的导入映射到宿主安装路径；不修改示例或宿主包。

`check-purge.mjs` 加载 pi-purge 0.2.1，模拟事件注册与 UI 通知，使用 Pi 1.5.0 的真实 `buildSystemPrompt()` 检查 12 组行为。对应插件提交为 `ffafeb940339d59fc6af4a05dc754019cef3a1ac`。它检查的范围是提示词变换和命令状态，不包含网络安装、真实 TUI、提供方请求或模型回答质量。

两个脚本只创建并清理各自的临时目录；不读取真实会话，不更改全局插件配置。源码与 MIT 许可见 [pi-purge 固定提交](https://github.com/ZiChuanLan/pi-purge/tree/ffafeb940339d59fc6af4a05dc754019cef3a1ac)。
