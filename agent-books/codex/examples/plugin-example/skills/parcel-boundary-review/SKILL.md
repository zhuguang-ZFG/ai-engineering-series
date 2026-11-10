---
name: parcel-boundary-review
description: 检查整数克计费函数的边界与类型行为，修复前先复现失败。
---

# 运费边界检查

读取项目 AGENTS.md、parcel.py 与 test_parcel.py。
运行 `python -B -m unittest -v`，记录失败的输入与实际价格。
按 1、1000、1001、2000、2001、30000 克检查区间。
保留整数分和整数克，不增加依赖，不删除现有类型检查。
修复后重跑同一命令，检查 Git 差异，再解释公式变化。
