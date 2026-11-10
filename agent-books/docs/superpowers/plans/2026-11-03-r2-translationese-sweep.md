# R2 译腔清扫——执行计划

前置：spec `2026-11-03-r2-translationese-sweep.md` ｜ 分支 `feat/skill-suite-transform`

- [x] Step 1：4 个 workpool 工人分 20 个 unit 双语改写（净行数不变，术语白名单不动）
- [x] Step 2：`measure_translationese.py` 复测对照基线，残留逐条可辩护
- [x] Step 3：五道闸全绿（build --check/--mermaid、unittest×2、check_book、check:diagrams）
- [x] Step 4：账本第 55 条双语注记（含构建器测试实数）+ 全量复跑
- [x] Step 5：提交 → 推送 → PR → CI 绿 → 合并（PR #4 → `9f967c1`）
