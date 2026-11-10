# 澄明库存：从离线案例到 Kimi 审查插件

以下前三条命令在书籍仓库根目录运行，只需 Python 标准库：

```powershell
python kimi/examples/check_inventory.py
python kimi/examples/check_inventory.py --fixed
python -m unittest discover -s kimi/examples -p "test_*.py" -v
```

第一条故意失败：8 个场景中 3 个通过，退出码 1。第二条运行参考实现，8 个全部通过。unittest 对未修改的随书材料运行，验证预期缺陷、参考实现、Hook 子进程和规则服务；读者修复练习副本后，用 `check_inventory.py` 验收自己的实现。

## 文件

- `inventory.py`：故意保留比较符号、输入范围与类型问题。
- `inventory_fixed.py`：参考答案，首次审查先不读。
- `check_inventory.py`：相同 8 个输入检查两份实现。
- `review-plugin/`：完整清单、Skill、只读 Agent、命令、Hook 与规则服务。
- `configure_mcp.py`：在练习副本创建项目 MCP 配置；已有配置时拒绝覆盖。
- `probe_cli.py`：真实 CLI 参数与 ACP 握手，不调用模型。
- `verify_source.mjs`：编译并调用固定上游解析器与 Hook 执行器。

## 跟做

按[第 4 章](../ch04.md)复制一个新练习目录。在副本中运行 `kimi --agent-file ./review-plugin/agents/inventory-reviewer.md`，提供规则路径并要求只读报告。需要自己的模型配置；正文没有将这个完整模型流程记为已实跑。

插件安装步骤见[第 11 章](../ch11.md)。在 Kimi 界面中运行 `/plugins install ./review-plugin`，查看 `/plugins info chengming-review`，随后重载或创建新会话。插件中的 Hook 调用 `python`，因此 Kimi 子进程的 PATH 必须能够找到实际解释器。

本地安装会复制插件文件。更新源目录之后需要重新同步安装副本，不能仅保存原文件就期待已安装插件变化。

## 源码组件与 CLI 探针

真实 CLI 检查：`python kimi/examples/probe_cli.py --output .scratch/kimi-cli-proof.json`。不在 PATH 时加 `--binary`。该脚本仅创建隔离临时数据，不导入用户会话。

源码组件复现命令、依赖与验证范围见[附录 C](../appendix-c.md)。12 项上游组件结果覆盖清单优先级、路径诊断、Agent 字段与 Hook 结果解释；不代表交互安装或完整 Agent 宿主已经测试。
