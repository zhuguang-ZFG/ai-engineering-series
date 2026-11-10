# Python 绘制的入门概念图

2026-11-05：使用 Pillow 从几何图形和字体直接绘图，先重绘六张入门插图，随后按
`HANDDRAWN-REWORK-SPEC.md` 的 B1–B6 批次补齐：`omp/images/` 的 92 张手绘 JPG 全部改由
`scripts/draw_omp_illustrations.py` 生成。正文仍引用原来的 JPG 路径。

另有 16 张维持 `visual-redesign/` 的 SVG 导出，4 张是上游 README 截图（`sources-omp.json`
的 `omp-readme-assets` 条目）；`tests/test_omp_overhaul.py` 会断言每张 JPG 都有来源，三类集合互不重叠。

## 每张图要讲清什么

| 文件（位于 `omp/images/`） | 主体比喻 | 阅读重点 |
|---|---|---|
| fig1-1-agent-loop.jpg | 人、模型与工具回路 | 需求进入一次，②→③→④→② 反复进行；结束或询问由模型判断 |
| fig1-2-chat-vs-agent.jpg | 同一任务、两种分工 | 谁来读文件、改代码、跑测试，结果怎样返回模型 |
| fig2-1-context-desk.jpg | 有边界的书桌与材料卡 | 规则、问题、文件、工具结果共享窗口；更早的记录可能不在本轮输入 |
| fig7-2-fork-resume.jpg | 复制新本、翻开旧本 | 裸 `/fork` 创建并切换新会话，`/resume` 接着已有记录 |
| fig15-1-compaction.jpg | 旧草稿变便签 | 下一轮材料是摘要加最近原文；重要细节需要回查 |
| fig16-1-memory-loop.jpg | 笔记、放大镜与归纳 | retain、recall、reflect 的用途；后端限制与现状核验 |

## 重绘命令

从仓库根执行，只需项目现有的 Pillow 依赖和本机中文字体：

```powershell
python scripts/draw_omp_illustrations.py --contact-sheet .scratch/python-illustrations/contact.jpg
python scripts/draw_omp_illustrations.py --out-dir omp/images
```

默认先生成到 `.scratch/python-illustrations/preview/`。通过 `--figure fig1-1-agent-loop` 可单张生成，
多张可重复传入 `--figure`；`--font` 与 `--bold-font` 支持指定字体文件。
Windows 自动查找微软雅黑，Linux 查找 Noto Sans CJK，macOS 查找 PingFang。
字体只在本机渲染时读取，不随图片分发。

默认画布 2400×1600，暖纸底、深墨字，橙色强调反馈，蓝绿区分材料和执行角色。
最终 JPG 质量 80、无色度抽样；标签用真实字形绘制，重要文字尽量保持 21–30 逻辑像素。
单张上限取构建器的内嵌预算 `PHOTO_BYTES`（`yuyu-book/yuyu_book/art.py`，300,000 字节）：
成品 HTML 是单文件，位图以 data URI 进正文，超预算的书本构建会直接失败。
同一字体和 Pillow 版本下可重复生成；换平台字体后字形与文件哈希可能不同，需重新检查排版。
脚本先绘完全部选中图片，检查标记了宽度的标签并编码到预算内，再写文件；
字体缺失、标签超宽或图片超预算都会在写盘前返回非零。

## 批次

| 批次 | 章节 | 张数 |
|---|---|---|
| B1 | 第 1–6 章 | 15 |
| B2 | 第 7–12 章 | 15 |
| B3 | 第 13–18 章 | 10 |
| B4 | 第 19–23 章 | 11 |
| B5 | 第 24–28 章（含 6 张原本未被引用的图） | 18 |
| B6 | 第 29–33 章与附录 E | 17 |

每批的画法约束、验收门禁与逐图要点见 `HANDDRAWN-REWORK-SPEC.md`。
B5 里 `fig23-4-profile`、`fig24-4..6`、`fig25-4..5` 是补引用后的重新编号，原编号文件已删除。

## 核对边界

- 工作循环的退出分支来自模型判断，不把工具结果画成能自行决定结束。
- 书桌只解释当前输入范围，不把旧会话画成已经从磁盘删除。
- 压缩保留摘要与近端原文，不承诺保留全部细节。
- 记忆按三种用途并列，不用箭头强加固定执行顺序，也不把全部后端画成同一工具集。

旧版对照、生成总览与 PDF 抽查保存在 `.scratch/python-illustrations/`，不进入正文资产目录。
