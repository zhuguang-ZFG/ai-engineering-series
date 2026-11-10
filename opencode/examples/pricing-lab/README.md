# 发票金额练习

这是本书原创、可以独立运行的小项目。它有一个已知错误版本和一份参考修复；两者使用同一组行为要求，不调用模型。

在书仓根目录执行：

```bash
python opencode/examples/pricing-lab/check_pricing.py
```

输出列出 19 个案例的结果。`broken_failures` 应非空，`reference_failures` 应为空，退出码为 0。这表示练习具备有效的失败基线与通过的参考实现，不表示 Agent 自动完成了修改。

自己练习时，把整个目录复制到新建的临时 Git 仓库，保存初始提交，再用 `pricing_broken.py` 的内容替换练习副本中的 `pricing.py`。先确认检查报告出现 reference_failures，然后请求 Agent 按 AGENTS.md 修复 pricing.py。不要删除已知错误基线，也不要让 Agent 修改检查脚本来消除失败。最后对照 diff、检查报告和任务要求。
