# R3 记忆点工程——执行计划

规格：`docs/superpowers/specs/2026-11-03-r3-memory-hooks.md`

- [x] Step 1：4 个 workpool 工人分章（W1 ch01–04、W2 ch05–08、W3 ch09–12、W4 ch13–15），每章六件内容（A 钩子 / B 难度 / C 回收 × zh/en）+ 三次锚点平移（dry-run 先行）+ 每章 `build.py --check` 绿
- [x] Step 2：主控复跑 measure_translationese（R2 战果不回退）+ 全量五道闸
- [x] Step 3：账本第 56 条（zh/en，末尾 `构建器测试 N 项全绿` / `N builder tests green`）
- [ ] Step 4：提交 → 推送 → PR → CI（预期一次 PDF 槽位 [STALE] → 按 CI 实测改槽位）→ 合并
- [ ] Step 5：本地重构建刷新 Windows 对照槽位；主 README 纪录更新
