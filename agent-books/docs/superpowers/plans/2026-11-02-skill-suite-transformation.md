# Plan：skill 套件改造逐级迭代

Spec：`docs/superpowers/specs/2026-11-02-skill-suite-transformation.md`
节奏：每轮 = 实现 → 五道闸 → 账本双语追加 → 本计划勾选 → 提交 → PR → CI 绿 → merge → README CI 槽位对齐。

## R1 内容图版铺开（生动形象）

- [ ] 1. 用 article-illustration-planner 方法产出 ch01–ch15 插图规划表（插入点行号、隐喻、构图、风格研判），登记 `docs/illustration-prompts.md` 与 skill 的 `references/book-contract.md`。
- [ ] 2. 逐章产 SVG 图版（FD-001 基准 + 逐章实时研判；先 dry-run `art._read` 契约校验，再入 `yuyu-book/illustrations/`）。
- [ ] 3. 构建审计适配：图版数 33→48+，art 套件与 diagrams 审计通过。
- [ ] 4. 五道闸 + 账本双语追加 + 提交 + PR + merge + README CI 槽位对齐。

## R2 译腔清扫（简单易懂）

- [ ] 1. humanizer-zh 过 zh 全书：只修表达不动事实；术语/版本/页数/计数零漂移；标题层级不动。
- [ ] 2. 锚点影响评估：`scripts/shift_anchors.py --after N --delta M` dry-run 先行，确认后 `--write`。
- [ ] 3. en 全书同流程（维持 en 既有 1 行漂移约定）。
- [ ] 4. 五道闸 + 账本 + 提交 + PR + merge + README 槽位对齐。

## R3 记忆点工程（过目不忘 / 由浅入深）

- [ ] 1. 每章开头一句话钩子 + 章尾三句回收，双语同批落稿。
- [ ] 2. 术语首现与 glossary/keeper 联动检查；篇章导语写明前置依赖与难度梯度。
- [ ] 3. 本轮文字行数变化集中处理：manifest/gloss 锚点一次性平移，双语行级同步核对。
- [ ] 4. 五道闸 + 账本 + 提交 + PR + merge + README 槽位对齐。

## R4 衍生物料（趣味可读）

- [ ] 1. 每章 3:4 知识卡组图（guizang-social-card-skill，素材只用本书自有 SVG 元素）。
- [ ] 2. 代表性样章精排单页 HTML（guizang-page-skill，杂志风/瑞士风 + --embed 离线字体）。
- [ ] 3. 视频封面草案（article-cover-designer：摘要→受众→隐喻→网感封面）。
- [ ] 4. 物料落点 `docs/`（或仓外），不进 `yuyu-book/dist/`；账本记录；PR + merge。

## R5 复盘与终验（经典级）

- [ ] 1. 五道闸全绿复跑；双语行级同步终核。
- [ ] 2. 对照 spec 验收表逐项勾验（图版覆盖、译腔命中下降、钩子/回收覆盖、物料成套）。
- [ ] 3. 账本收官条目 + PR + merge。
