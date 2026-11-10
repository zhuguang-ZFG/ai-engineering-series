---
name: review
description: 审查指定的库存函数，只报告缺陷与证据
---

审查目标：$ARGUMENTS

按 chengming-review 插件的 review-inventory Skill 核对业务规则，只读取文件。报告每条缺陷的位置、触发输入、实际结果、预期结果和证据来源；不要自动修改实现。未运行的检查明确标为静态分析。
