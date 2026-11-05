# 质量门禁改进记录

## 2026-11-05：按可见内容验收，并覆盖整册书稿

复现了交付审计的漏检：manifest 中前言或附录指向不存在的文件时，旧脚本仍返回空错误列表。
结构审计还会从 Markdown 示例或注释中读出图片与版本核对字样，并把它们计入正文要求；
另一篇文件也能替代缺失章节，只要目录内文件数仍为 33。

修复分为三处：

- 两个审计共用围栏与注释扫描，Mermaid 计数与构建器的 info 规则一致。
- 交付审计遍历 39 个单元，检查内联、引用式与 HTML 图片的本地路径；错误注册表和词条类型返回可读诊断。
- 结构门禁检查确切章节集合，翻车表需要 Markdown 分隔行，未闭合内容在严格模式下失败。

新增回归测试覆盖这些失败路径，也验证合法的波浪线围栏、嵌套示例和行内注释示例不会被误判。
只运行过部分实验的章节仍保留「未验证」说明；`mark_verified` 仅表示该章存在已记录的本机观察。

验证命令：

```powershell
python -m unittest tests.test_omp_overhaul -v
python omp/overhaul/audit_structure.py --csv --check
python omp/overhaul/audit_delivery.py
python scripts/bookctl.py check --fast
```

四项均通过：25 项定向测试，33 章结构齐全，交付审计 0 errors。
`check --fast` 六步通过，含 64 项通用测试、515 项构建器测试；184 份 Markdown 内容检查和
333 张 Mermaid 语法检查均为 0 errors。御舆双语与 Omp 中文源码装配通过，分别保留
20 与 39 个单元；Omp 仍有 13 张图版。`audit-current.tsv` 已与实时输出逐行核对。
