# 运费审查插件包示例

对应固定 Codex CLI 0.167.0 的 `.codex-plugin/plugin.json` 兼容格式。
这是可查看的包结构；没有安装到本机用户配置，也未由真实宿主触发。

默认 `hooks/hooks.json` 使用 POSIX shell 的 `$PLUGIN_ROOT` 展开方式。
若实际 Hook shell 是 PowerShell，先在独立副本中将 `hooks.powershell.json`
的内容用作 `hooks.json`。选择依据是宿主实际 shell，不只看操作系统名称。

`scripts/hook_guard.py` 与上一级示例处理器内容一致，便于独立打包。
`check_workshop.py` 会检查两个文件相同并直接测试处理器；这不验证插件发现、
信任、安装、运行时控制效果或沙箱。它仅识别一个精确命令文本，不能作为完整安全策略。
