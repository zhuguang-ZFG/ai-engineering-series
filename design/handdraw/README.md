# 手绘风改造方案（handraw-style）

> 依据 [yang0/handraw-style](https://github.com/yang0/handraw-style) 的风格库与规则生成。
> 本目录只交付**提示词与点位方案**，未生成任何图片；把提示词粘进生图模型即可出图。
> 原始需求逐字存档于 `original-request.txt`。

## 一句话目标

把课程从「截图 + 代码海报」升级成一套统一的手绘语言：**封面靠一个隐喻抓住眼球，正文靠图解替读者减负**。

## 推荐组合

💡 智能推荐组合（本次由主题语义实时选定，可换编号）

| 用途 | 风格 | 主题色 | 为什么 |
| --- | --- | --- | --- |
| 书封面 + 5 集视频封面 | `FA-013` Bold Flat Everyday Satire（Jean Jullien） | `C-11` 祖母绿（主）+ `C-26` 柿子橙（点缀） | 粗黑轮廓 + 平涂色块在手机缩略图上依然一眼可辨；互联网生活讽刺的气质正合「不会写代码也能做软件」的反差幽默；祖母绿沿用课程品牌绿，柿子橙只给 CTA 和苹果用 |
| 书籍知识图解 | `FA-040` Minimalist 2D Hand-Drawn Doodle | `C-32` 炭黑（线稿）+ `C-11` 祖母绿（标注） | 轻柔线条、低细节、概括造型，图解的主角是结构与标签而不是质感；炭黑线稿配祖母绿标注，打印和夜间模式都不刺眼 |

风格激活核查（基线模型 gpt-image-2，`references/model_capabilities.json`）：

- `FA-013`：`name_activation=strong` → 提示词只写作者与风格名，**不写核心特征、不需要垫图**。
- `FA-040`：`name_activation=weak` + `traits_activation=strong` → 提示词带核心风格特征，**不需要垫图**。

因此本方案全部提示词均为纯文本直出，无参考图依赖。

## 资产改造清单

| 资产 | 现状 | 改造稿 |
| --- | --- | --- |
| 书封面 `book/assets/cover.svg` / `cover.webp` | 代码海报风 | `covers.md` 第 0 组 |
| EP.01 横版封面 `deliverables/landscape-cover.webp` | 绿蛇海报 | `covers.md` 第 1 组 |
| EP.01 竖版封面 `deliverables/vertical-cover.webp` | 绿蛇海报 | `covers.md` 第 2 组 |
| EP.02/03/04 封面 `deliverables/ep0X-cover.webp` | 绿蛇海报 | `covers.md` 第 3–5 组 |
| 书籍正文知识图解 | 截图为主，机制段落靠文字推演 | `book-illustrations.md` 首批 6 个点位 |

## 知识图解的四条红线（来自 article-illustration-planner，执行时必须遵守）

1. 不画微缩摆拍、书桌、咖啡杯、童话小精灵——画面 100% 给图表本身。
2. **不许把知识画丢**：公式、权重数字、判断阈值、关键台词必须作为图中标签保留；正文同步保留结论。
3. 必须用真图形隐喻：层级用金字塔、筛选用漏斗、对比用双列、流程用路径图，严禁把文字抄进方框就算图解。
4. 间距：相邻插图正文间隔 ≥400–500 字且跨标题；连续 1000–1200 字以上无图的段落优先补图。

## 出图与回填流程

1. 从 `covers.md` / `book-illustrations.md` 复制提示词到生图模型（中文或英文任一）。
2. 封面按既有规格导出：B站 1920×1080、抖音 1080×1440 / 1440×1080、视频号 3:4 资料卡。
3. 插图回填到 `book/book.md` 对应章节，图片放 `book/assets/images/handdraw/`，正文保留公式与结论。
4. 跑 `npm test`（会校验本地图片引用完整），再提交。

## 尚未做、需要时再点名的事

- 真出图（需要指定生图模型/通道）。
- 把视频正片场景也改成手绘风（要重渲染 HyperFrames，属另一档工程）。
- 全书 215 章的完整插图点位扫描（本包先交付学习路径上最关键的 6 张）。
