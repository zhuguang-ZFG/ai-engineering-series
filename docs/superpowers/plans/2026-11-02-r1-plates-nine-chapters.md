# R1 内容图版九章铺开 —— 执行计划

前置：spec `2026-11-02-r1-plates-nine-chapters.md` ｜ 分支 `feat/skill-suite-transform`

- [ ] Step 1：九幅 SVG 按 art.py 硬契约绘制入 `yuyu-book/illustrations/`
- [ ] Step 1b：`scripts/build_illustration_gallery.py` 登记 9 版（ORDER 与磁盘强相等 + WIDE 宽度 + PLAIN/PLAIN_EN 白话注）；beginner_reader 的 @@PLATES@@ 由文档重建刷新
- [ ] Step 2：zh/en 十八章各插 1 个 ` ```ill ` 块（各 +3 行，行号同步）
- [ ] Step 3：`shift_anchors.py` 平移受影响锚点（先 dry-run）
- [ ] Step 4：五道闸全绿（build --check/--mermaid、unittest×2、check_book、check:diagrams）
- [ ] Step 5：账本 54 条注记（zh+en，含构建器测试实数）+ 全量复跑
- [ ] Step 6：提交 → 推送 → PR → CI 绿 → 合并 → README CI 槽位
