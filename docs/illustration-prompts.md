# 插图再生手册 —— 御舆 26 份与第二分册 omp 7 幅篇题刻的双语生图提示词（附 omp 39 枚章徽的落成记录）

本书 26 份插图（章徽、篇题刻、老驿卒、扉页车图）以开源项目
[yang0/handraw-style](https://github.com/yang0/handraw-style) 的画风体系绘制：
另有 17 张章内插图不走「提示词 → 手写 SVG」这条管线，边界与名单见文末一节。
基准配方为 `FD-001 · Yuko Shimizu | Dynamic East-Asian Ink Editorial` 画风，
`C-32 炭黑（Charcoal Black）` 统领、`C-15 朱砂红（Cinnabar Red）` 点缀
（朱砂仅用于章印与书级点缀，不在画面内）。本手册按该项目的输出规范给出
每份插图的中英双语再生提示词：把它们整段粘贴进任意生图模型（gpt-image、
Midjourney、Flux 等），即可在别的媒介重制同一幅图，或为未来新增章节
以同一支笔续画。

> 规范要点（沿上游 skill）：提示词内不出现任何编号；只写正向特征；
> 参考作者/风格名称是索引标签而非模仿指令；默认不出图，由生图模型决定成败。

垫图（可选）：仅当生图模型对风格名不敏感时，垫入上游完整安装的 `images/individual/FD/FD-001.webp`（yang0/handraw-style 仓库），并附隔离指令：只提取画风，不沿用画面内容。

## 基准配方

- 风格：`FD-001 · Dynamic East-Asian Ink Editorial`（流动墨线、东方笔意、明显手绘笔压、
  停顿与轻微不齐整感、书写性与留白意识）
- 主题色：C-32 炭黑统领 + C-15 朱砂点缀（章印/首字）
- 画幅习惯：章徽 64×64、篇题刻 200×140、扉页 1000×470、章末驿卒 64×64

## 逐图提示词

### 前言 · `front.svg`

**隐喻**：折叠舆图上一条虚线驿路

<details>
<summary>中文提示词</summary>

```text
风格名称：Dynamic East-Asian Ink Editorial。主题色：炭黑（Charcoal Black）。
一幅对折再对折的古舆图摊开，纸面四道折痕，一条虚线驿路自左下蜿蜒至右上，尽头一枚实心墨点与一圈细环。
参考作者/风格名称：Yuko Shimizu —— Dynamic East-Asian Ink Editorial
核心风格特征：流动墨线、东方笔意、明显手绘笔压、停顿与轻微不齐整感，线条带书写性与留白意识，现代 Editorial 构图。
```

</details>

<details>
<summary>English prompt</summary>

```text
Style name: Dynamic East-Asian Ink Editorial. Theme color: Charcoal Black.
An old folded atlas map spreads open with four crease lines; a dotted post road winds from lower left to upper right, ending in a solid ink dot inside a fine ring.
Reference author/style name: Yuko Shimizu — Dynamic East-Asian Ink Editorial
Core style traits: flowing ink linework with an East-Asian brush spirit; visible pen pressure, pauses and slight irregularity; calligraphic lines with a strong sense of negative space; modern editorial composition.
```

</details>

### 第 1 章 · `ch01.svg`

**隐喻**：罗盘——重新瞄准的编程范式

<details>
<summary>中文提示词</summary>

```text
风格名称：Dynamic East-Asian Ink Editorial。主题色：炭黑（Charcoal Black）。
一只手绘罗盘：外环留缺口，内环虚线，四正四隅细辐，盘心一枚墨点套细环，像刚被指尖拨过。
参考作者/风格名称：Yuko Shimizu —— Dynamic East-Asian Ink Editorial
核心风格特征：流动墨线、东方笔意、明显手绘笔压、停顿与轻微不齐整感，线条带书写性与留白意识，现代 Editorial 构图。
```

</details>

<details>
<summary>English prompt</summary>

```text
Style name: Dynamic East-Asian Ink Editorial. Theme color: Charcoal Black.
A hand-drawn compass: the outer ring left open, a dotted inner ring, eight fine spokes, an ink dot at the center inside a thin ring, as if just flicked by a fingertip.
Reference author/style name: Yuko Shimizu — Dynamic East-Asian Ink Editorial
Core style traits: flowing ink linework with an East-Asian brush spirit; visible pen pressure, pauses and slight irregularity; calligraphic lines with a strong sense of negative space; modern editorial composition.
```

</details>

### 第 2 章 · `ch02.svg`

**隐喻**：对话循环——心跳回路

<details>
<summary>中文提示词</summary>

```text
风格名称：Dynamic East-Asian Ink Editorial。主题色：炭黑（Charcoal Black）。
两段弧线首尾相逐成环，各带一枚小箭头，中心一枚实心墨点，像心跳的两个半拍。
参考作者/风格名称：Yuko Shimizu —— Dynamic East-Asian Ink Editorial
核心风格特征：流动墨线、东方笔意、明显手绘笔压、停顿与轻微不齐整感，线条带书写性与留白意识，现代 Editorial 构图。
```

</details>

<details>
<summary>English prompt</summary>

```text
Style name: Dynamic East-Asian Ink Editorial. Theme color: Charcoal Black.
Two arcs chase each other into a circle, each carrying a small arrowhead; a solid ink dot at the center marks the beat between beats.
Reference author/style name: Yuko Shimizu — Dynamic East-Asian Ink Editorial
Core style traits: flowing ink linework with an East-Asian brush spirit; visible pen pressure, pauses and slight irregularity; calligraphic lines with a strong sense of negative space; modern editorial composition.
```

</details>

### 第 3 章 · `ch03.svg`

**隐喻**：工具系统——六角螺母

<details>
<summary>中文提示词</summary>

```text
风格名称：Dynamic East-Asian Ink Editorial。主题色：炭黑（Charcoal Black）。
一枚六角螺母，轮廓留笔势缺口，内孔一只圆环，盘心墨点，右上角一抹排线灰面。
参考作者/风格名称：Yuko Shimizu —— Dynamic East-Asian Ink Editorial
核心风格特征：流动墨线、东方笔意、明显手绘笔压、停顿与轻微不齐整感，线条带书写性与留白意识，现代 Editorial 构图。
```

</details>

<details>
<summary>English prompt</summary>

```text
Style name: Dynamic East-Asian Ink Editorial. Theme color: Charcoal Black.
A hexagonal nut with open corners, a round bore, an ink dot at the center, and a small patch of hatched shading at the upper right.
Reference author/style name: Yuko Shimizu — Dynamic East-Asian Ink Editorial
Core style traits: flowing ink linework with an East-Asian brush spirit; visible pen pressure, pauses and slight irregularity; calligraphic lines with a strong sense of negative space; modern editorial composition.
```

</details>

### 第 4 章 · `ch04.svg`

**隐喻**：权限管线——护栏勾选

<details>
<summary>中文提示词</summary>

```text
风格名称：Dynamic East-Asian Ink Editorial。主题色：炭黑（Charcoal Black）。
两道护栏立柱之间一道有力的勾选线，像验讫的封印，立柱上各一枚铆点。
参考作者/风格名称：Yuko Shimizu —— Dynamic East-Asian Ink Editorial
核心风格特征：流动墨线、东方笔意、明显手绘笔压、停顿与轻微不齐整感，线条带书写性与留白意识，现代 Editorial 构图。
```

</details>

<details>
<summary>English prompt</summary>

```text
Style name: Dynamic East-Asian Ink Editorial. Theme color: Charcoal Black.
A bold checkmark drawn between two guardrail posts like an approval seal, a rivet dot on each post.
Reference author/style name: Yuko Shimizu — Dynamic East-Asian Ink Editorial
Core style traits: flowing ink linework with an East-Asian brush spirit; visible pen pressure, pauses and slight irregularity; calligraphic lines with a strong sense of negative space; modern editorial composition.
```

</details>

### 第 5 章 · `ch05.svg`

**隐喻**：设置与配置——层叠菱面

<details>
<summary>中文提示词</summary>

```text
风格名称：Dynamic East-Asian Ink Editorial。主题色：炭黑（Charcoal Black）。
三层菱面自上而下叠落，顶层实、下两层渐淡，像配置在层层沉降。
参考作者/风格名称：Yuko Shimizu —— Dynamic East-Asian Ink Editorial
核心风格特征：流动墨线、东方笔意、明显手绘笔压、停顿与轻微不齐整感，线条带书写性与留白意识，现代 Editorial 构图。
```

</details>

<details>
<summary>English prompt</summary>

```text
Style name: Dynamic East-Asian Ink Editorial. Theme color: Charcoal Black.
Three diamond planes stack downward, the top one solid and the lower two fading, like configuration settling layer by layer.
Reference author/style name: Yuko Shimizu — Dynamic East-Asian Ink Editorial
Core style traits: flowing ink linework with an East-Asian brush spirit; visible pen pressure, pauses and slight irregularity; calligraphic lines with a strong sense of negative space; modern editorial composition.
```

</details>

### 第 6 章 · `ch06.svg`

**隐喻**：记忆系统——折角册页

<details>
<summary>中文提示词</summary>

```text
风格名称：Dynamic East-Asian Ink Editorial。主题色：炭黑（Charcoal Black）。
一页折角文档，三行墨迹行文，右下一笔小注与一枚墨点，像刚写完的记忆。
参考作者/风格名称：Yuko Shimizu —— Dynamic East-Asian Ink Editorial
核心风格特征：流动墨线、东方笔意、明显手绘笔压、停顿与轻微不齐整感，线条带书写性与留白意识，现代 Editorial 构图。
```

</details>

<details>
<summary>English prompt</summary>

```text
Style name: Dynamic East-Asian Ink Editorial. Theme color: Charcoal Black.
A document with a folded corner, three lines of ink writing, a small note and an ink dot at the lower right—a memory just written down.
Reference author/style name: Yuko Shimizu — Dynamic East-Asian Ink Editorial
Core style traits: flowing ink linework with an East-Asian brush spirit; visible pen pressure, pauses and slight irregularity; calligraphic lines with a strong sense of negative space; modern editorial composition.
```

</details>

### 第 7 章 · `ch07.svg`

**隐喻**：上下文管理——量器

<details>
<summary>中文提示词</summary>

```text
风格名称：Dynamic East-Asian Ink Editorial。主题色：炭黑（Charcoal Black）。
一只半圆量器，三枚刻度，指针斜指右上方，像工作记忆正被度量。
参考作者/风格名称：Yuko Shimizu —— Dynamic East-Asian Ink Editorial
核心风格特征：流动墨线、东方笔意、明显手绘笔压、停顿与轻微不齐整感，线条带书写性与留白意识，现代 Editorial 构图。
```

</details>

<details>
<summary>English prompt</summary>

```text
Style name: Dynamic East-Asian Ink Editorial. Theme color: Charcoal Black.
A semicircular gauge with three ticks, its needle swept toward the upper right, measuring working memory.
Reference author/style name: Yuko Shimizu — Dynamic East-Asian Ink Editorial
Core style traits: flowing ink linework with an East-Asian brush spirit; visible pen pressure, pauses and slight irregularity; calligraphic lines with a strong sense of negative space; modern editorial composition.
```

</details>

### 第 8 章 · `ch08.svg`

**隐喻**：钩子系统——生命周期挂钩

<details>
<summary>中文提示词</summary>

```text
风格名称：Dynamic East-Asian Ink Editorial。主题色：炭黑（Charcoal Black）。
一条基线上三枚节点，上方一道挂钩折线带垂弧，下方一行渐淡的回声，一枚箭头指向前方。
参考作者/风格名称：Yuko Shimizu —— Dynamic East-Asian Ink Editorial
核心风格特征：流动墨线、东方笔意、明显手绘笔压、停顿与轻微不齐整感，线条带书写性与留白意识，现代 Editorial 构图。
```

</details>

<details>
<summary>English prompt</summary>

```text
Style name: Dynamic East-Asian Ink Editorial. Theme color: Charcoal Black.
A baseline with three nodes; above it a bracketed hook line with a hanging swag; below, a fading echo; an arrow points ahead.
Reference author/style name: Yuko Shimizu — Dynamic East-Asian Ink Editorial
Core style traits: flowing ink linework with an East-Asian brush spirit; visible pen pressure, pauses and slight irregularity; calligraphic lines with a strong sense of negative space; modern editorial composition.
```

</details>

### 第 9 章 · `ch09.svg`

**隐喻**：子智能体——一源三枝

<details>
<summary>中文提示词</summary>

```text
风格名称：Dynamic East-Asian Ink Editorial。主题色：炭黑（Charcoal Black）。
一个源环向右上、右下各分出一枝，各落一枚歪圆环，分叉处一枚小墨点。
参考作者/风格名称：Yuko Shimizu —— Dynamic East-Asian Ink Editorial
核心风格特征：流动墨线、东方笔意、明显手绘笔压、停顿与轻微不齐整感，线条带书写性与留白意识，现代 Editorial 构图。
```

</details>

<details>
<summary>English prompt</summary>

```text
Style name: Dynamic East-Asian Ink Editorial. Theme color: Charcoal Black.
One source ring forks to the upper and lower right, each branch ending in its own lopsided ring; a tiny ink dot marks the fork.
Reference author/style name: Yuko Shimizu — Dynamic East-Asian Ink Editorial
Core style traits: flowing ink linework with an East-Asian brush spirit; visible pen pressure, pauses and slight irregularity; calligraphic lines with a strong sense of negative space; modern editorial composition.
```

</details>

### 第 10 章 · `ch10.svg`

**隐喻**：协调器——枢纽列站

<details>
<summary>中文提示词</summary>

```text
风格名称：Dynamic East-Asian Ink Editorial。主题色：炭黑（Charcoal Black）。
中心一枚墨环向四角各引一条细线，尽头四枚虚线小环，像列站的驿站。
参考作者/风格名称：Yuko Shimizu —— Dynamic East-Asian Ink Editorial
核心风格特征：流动墨线、东方笔意、明显手绘笔压、停顿与轻微不齐整感，线条带书写性与留白意识，现代 Editorial 构图。
```

</details>

<details>
<summary>English prompt</summary>

```text
Style name: Dynamic East-Asian Ink Editorial. Theme color: Charcoal Black.
A central ink ring sends four fine lines to the corners, each ending in a small dashed ring like way stations.
Reference author/style name: Yuko Shimizu — Dynamic East-Asian Ink Editorial
Core style traits: flowing ink linework with an East-Asian brush spirit; visible pen pressure, pauses and slight irregularity; calligraphic lines with a strong sense of negative space; modern editorial composition.
```

</details>

### 第 11 章 · `ch11.svg`

**隐喻**：技能系统——侧挂面板

<details>
<summary>中文提示词</summary>

```text
风格名称：Dynamic East-Asian Ink Editorial。主题色：炭黑（Charcoal Black）。
一页文档右侧挂一块面板，两根引线各连一枚墨点，面板下两笔排线灰面。
参考作者/风格名称：Yuko Shimizu —— Dynamic East-Asian Ink Editorial
核心风格特征：流动墨线、东方笔意、明显手绘笔压、停顿与轻微不齐整感，线条带书写性与留白意识，现代 Editorial 构图。
```

</details>

<details>
<summary>English prompt</summary>

```text
Style name: Dynamic East-Asian Ink Editorial. Theme color: Charcoal Black.
A document with a side panel attached; two leads each end in an ink dot; two hatch lines shade the panel's foot.
Reference author/style name: Yuko Shimizu — Dynamic East-Asian Ink Editorial
Core style traits: flowing ink linework with an East-Asian brush spirit; visible pen pressure, pauses and slight irregularity; calligraphic lines with a strong sense of negative space; modern editorial composition.
```

</details>

### 第 12 章 · `ch12.svg`

**隐喻**：MCP 集成——双杆一线

<details>
<summary>中文提示词</summary>

```text
风格名称：Dynamic East-Asian Ink Editorial。主题色：炭黑（Charcoal Black）。
两根立杆顶端各一枚绝缘墨点，一条垂弧双线跨接其间，两侧斜拉线落地，地面三段短划。
参考作者/风格名称：Yuko Shimizu —— Dynamic East-Asian Ink Editorial
核心风格特征：流动墨线、东方笔意、明显手绘笔压、停顿与轻微不齐整感，线条带书写性与留白意识，现代 Editorial 构图。
```

</details>

<details>
<summary>English prompt</summary>

```text
Style name: Dynamic East-Asian Ink Editorial. Theme color: Charcoal Black.
Two poles topped with insulator dots; a sagging double wire spans between them; guy lines brace to the ground of three dashes.
Reference author/style name: Yuko Shimizu — Dynamic East-Asian Ink Editorial
Core style traits: flowing ink linework with an East-Asian brush spirit; visible pen pressure, pauses and slight irregularity; calligraphic lines with a strong sense of negative space; modern editorial composition.
```

</details>

### 第 13 章 · `ch13.svg`

**隐喻**：流式架构——漏斗汇流

<details>
<summary>中文提示词</summary>

```text
风格名称：Dynamic East-Asian Ink Editorial。主题色：炭黑（Charcoal Black）。
三股墨流自左汇入一只漏斗，颈口一滴悬而未落，右侧罐体已积半管墨，双箭头向外流去。
参考作者/风格名称：Yuko Shimizu —— Dynamic East-Asian Ink Editorial
核心风格特征：流动墨线、东方笔意、明显手绘笔压、停顿与轻微不齐整感，线条带书写性与留白意识，现代 Editorial 构图。
```

</details>

<details>
<summary>English prompt</summary>

```text
Style name: Dynamic East-Asian Ink Editorial. Theme color: Charcoal Black.
Three ink streams pour into a funnel from the left; a drop hangs at the neck; the tank at right has filled halfway, two arrows flowing out.
Reference author/style name: Yuko Shimizu — Dynamic East-Asian Ink Editorial
Core style traits: flowing ink linework with an East-Asian brush spirit; visible pen pressure, pauses and slight irregularity; calligraphic lines with a strong sense of negative space; modern editorial composition.
```

</details>

### 第 14 章 · `ch14.svg`

**隐喻**：Plan 模式——虚线远路

<details>
<summary>中文提示词</summary>

```text
风格名称：Dynamic East-Asian Ink Editorial。主题色：炭黑（Charcoal Black）。
一条虚线远路自一枚墨点起伏而去，尽头旗杆上一面燕尾旗，路线越远越细。
参考作者/风格名称：Yuko Shimizu —— Dynamic East-Asian Ink Editorial
核心风格特征：流动墨线、东方笔意、明显手绘笔压、停顿与轻微不齐整感，线条带书写性与留白意识，现代 Editorial 构图。
```

</details>

<details>
<summary>English prompt</summary>

```text
Style name: Dynamic East-Asian Ink Editorial. Theme color: Charcoal Black.
A dotted road rises and falls away from an ink dot, ending at a swallow-tailed flag on its pole.
Reference author/style name: Yuko Shimizu — Dynamic East-Asian Ink Editorial
Core style traits: flowing ink linework with an East-Asian brush spirit; visible pen pressure, pauses and slight irregularity; calligraphic lines with a strong sense of negative space; modern editorial composition.
```

</details>

### 第 15 章 · `ch15.svg`

**隐喻**：构建 Harness——辘轳绕绳

<details>
<summary>中文提示词</summary>

```text
风格名称：Dynamic East-Asian Ink Editorial。主题色：炭黑（Charcoal Black）。
一架辘轳：人字架、轴上绕绳鼓、摇柄斜出，垂绳吊着一只小斗。
参考作者/风格名称：Yuko Shimizu —— Dynamic East-Asian Ink Editorial
核心风格特征：流动墨线、东方笔意、明显手绘笔压、停顿与轻微不齐整感，线条带书写性与留白意识，现代 Editorial 构图。
```

</details>

<details>
<summary>English prompt</summary>

```text
Style name: Dynamic East-Asian Ink Editorial. Theme color: Charcoal Black.
A well-windlass: an A-frame, a rope drum on its axle, a crank handle out to the side, a rope lowering a small bucket.
Reference author/style name: Yuko Shimizu — Dynamic East-Asian Ink Editorial
Core style traits: flowing ink linework with an East-Asian brush spirit; visible pen pressure, pauses and slight irregularity; calligraphic lines with a strong sense of negative space; modern editorial composition.
```

</details>

### 附录 A · `apxa.svg`

**隐喻**：源码导航——格上定位

<details>
<summary>中文提示词</summary>

```text
风格名称：Dynamic East-Asian Ink Editorial。主题色：炭黑（Charcoal Black）。
一张淡格舆图，中央一只歪圆定位环，四向短刻度伸出格外，环心一枚墨点。
参考作者/风格名称：Yuko Shimizu —— Dynamic East-Asian Ink Editorial
核心风格特征：流动墨线、东方笔意、明显手绘笔压、停顿与轻微不齐整感，线条带书写性与留白意识，现代 Editorial 构图。
```

</details>

<details>
<summary>English prompt</summary>

```text
Style name: Dynamic East-Asian Ink Editorial. Theme color: Charcoal Black.
A faint gridded map with a lopsided locator ring at the center, four short ticks reaching past the grid, an ink dot inside.
Reference author/style name: Yuko Shimizu — Dynamic East-Asian Ink Editorial
Core style traits: flowing ink linework with an East-Asian brush spirit; visible pen pressure, pauses and slight irregularity; calligraphic lines with a strong sense of negative space; modern editorial composition.
```

</details>

### 附录 B · `apxb.svg`

**隐喻**：工具清单——逐项核对

<details>
<summary>中文提示词</summary>

```text
风格名称：Dynamic East-Asian Ink Editorial。主题色：炭黑（Charcoal Black）。
三行勾选清单，勾线一笔写成、粗细不匀，行线渐短，像逐项核对的工具清单。
参考作者/风格名称：Yuko Shimizu —— Dynamic East-Asian Ink Editorial
核心风格特征：流动墨线、东方笔意、明显手绘笔压、停顿与轻微不齐整感，线条带书写性与留白意识，现代 Editorial 构图。
```

</details>

<details>
<summary>English prompt</summary>

```text
Style name: Dynamic East-Asian Ink Editorial. Theme color: Charcoal Black.
A three-row checklist, each check drawn in one uneven stroke, the ruled lines shortening, as if ticking off tools one by one.
Reference author/style name: Yuko Shimizu — Dynamic East-Asian Ink Editorial
Core style traits: flowing ink linework with an East-Asian brush spirit; visible pen pressure, pauses and slight irregularity; calligraphic lines with a strong sense of negative space; modern editorial composition.
```

</details>

### 附录 C · `apxc.svg`

**隐喻**：功能标志——拨杆开关

<details>
<summary>中文提示词</summary>

```text
风格名称：Dynamic East-Asian Ink Editorial。主题色：炭黑（Charcoal Black）。
一枚手绘拨杆开关，胶囊外壳歪圆，旋钮拨向右侧并带一圈虚线残影，像刚被拨动。
参考作者/风格名称：Yuko Shimizu —— Dynamic East-Asian Ink Editorial
核心风格特征：流动墨线、东方笔意、明显手绘笔压、停顿与轻微不齐整感，线条带书写性与留白意识，现代 Editorial 构图。
```

</details>

<details>
<summary>English prompt</summary>

```text
Style name: Dynamic East-Asian Ink Editorial. Theme color: Charcoal Black.
A hand-drawn toggle switch: a lopsided capsule, the knob thrown to the right with a dashed halo, as if just flipped.
Reference author/style name: Yuko Shimizu — Dynamic East-Asian Ink Editorial
Core style traits: flowing ink linework with an East-Asian brush spirit; visible pen pressure, pauses and slight irregularity; calligraphic lines with a strong sense of negative space; modern editorial composition.
```

</details>

### 附录 D · `apxd.svg`

**隐喻**：术语表——侧订册页

<details>
<summary>中文提示词</summary>

```text
风格名称：Dynamic East-Asian Ink Editorial。主题色：炭黑（Charcoal Black）。
一册侧订小书，右侧两枚书签耳，三行词条墨迹，书脊一道淡影。
参考作者/风格名称：Yuko Shimizu —— Dynamic East-Asian Ink Editorial
核心风格特征：流动墨线、东方笔意、明显手绘笔压、停顿与轻微不齐整感，线条带书写性与留白意识，现代 Editorial 构图。
```

</details>

<details>
<summary>English prompt</summary>

```text
Style name: Dynamic East-Asian Ink Editorial. Theme color: Charcoal Black.
A side-stitched booklet with two bookmark tabs, three lines of entry writing, a soft shadow along the spine.
Reference author/style name: Yuko Shimizu — Dynamic East-Asian Ink Editorial
Core style traits: flowing ink linework with an East-Asian brush spirit; visible pen pressure, pauses and slight irregularity; calligraphic lines with a strong sense of negative space; modern editorial composition.
```

</details>

### 章末按语·老驿卒 · `keeper.svg`

**隐喻**：老驿卒——章末按语伴立

<details>
<summary>中文提示词</summary>

```text
风格名称：Dynamic East-Asian Ink Editorial。主题色：炭黑（Charcoal Black）。
一位戴斗笠的老驿卒侧身而立，衣摆两笔，背一只行囊，手提一盏圆灯笼，灯笼里一线火苗。
参考作者/风格名称：Yuko Shimizu —— Dynamic East-Asian Ink Editorial
核心风格特征：流动墨线、东方笔意、明显手绘笔压、停顿与轻微不齐整感，线条带书写性与留白意识，现代 Editorial 构图。
```

</details>

<details>
<summary>English prompt</summary>

```text
Style name: Dynamic East-Asian Ink Editorial. Theme color: Charcoal Black.
An old courier in a bamboo hat stands in profile: two strokes for the robe, a satchel on his back, a round lantern in hand with a line of flame inside.
Reference author/style name: Yuko Shimizu — Dynamic East-Asian Ink Editorial
Core style traits: flowing ink linework with an East-Asian brush spirit; visible pen pressure, pauses and slight irregularity; calligraphic lines with a strong sense of negative space; modern editorial composition.
```

</details>

### 第 一 篇题刻 · `part-p1.svg`

**隐喻**：基础篇——大罗盘

<details>
<summary>中文提示词</summary>

```text
风格名称：Dynamic East-Asian Ink Editorial。主题色：炭黑（Charcoal Black）。
一面大罗盘铺满纸面，十六根长短不齐的辐条，双层环圈，盘心一枚墨点，地平线一笔拖过。
参考作者/风格名称：Yuko Shimizu —— Dynamic East-Asian Ink Editorial
核心风格特征：流动墨线、东方笔意、明显手绘笔压、停顿与轻微不齐整感，线条带书写性与留白意识，现代 Editorial 构图。
```

</details>

<details>
<summary>English prompt</summary>

```text
Style name: Dynamic East-Asian Ink Editorial. Theme color: Charcoal Black.
A great compass rose fills the sheet: sixteen uneven spokes, double rings, an ink dot at its heart, a single horizon stroke beneath.
Reference author/style name: Yuko Shimizu — Dynamic East-Asian Ink Editorial
Core style traits: flowing ink linework with an East-Asian brush spirit; visible pen pressure, pauses and slight irregularity; calligraphic lines with a strong sense of negative space; modern editorial composition.
```

</details>

### 第 二 篇题刻 · `part-p2.svg`

**隐喻**：核心系统篇——箱匣

<details>
<summary>中文提示词</summary>

```text
风格名称：Dynamic East-Asian Ink Editorial。主题色：炭黑（Charcoal Black）。
一只圆盖箱匣正面而立，两道革带勒紧，锁孔居中，右旁一面小罗盘相照。
参考作者/风格名称：Yuko Shimizu —— Dynamic East-Asian Ink Editorial
核心风格特征：流动墨线、东方笔意、明显手绘笔压、停顿与轻微不齐整感，线条带书写性与留白意识，现代 Editorial 构图。
```

</details>

<details>
<summary>English prompt</summary>

```text
Style name: Dynamic East-Asian Ink Editorial. Theme color: Charcoal Black.
A round-lidded chest stands front on, two straps cinched tight, a keyhole at center, a small compass rose beside it.
Reference author/style name: Yuko Shimizu — Dynamic East-Asian Ink Editorial
Core style traits: flowing ink linework with an East-Asian brush spirit; visible pen pressure, pauses and slight irregularity; calligraphic lines with a strong sense of negative space; modern editorial composition.
```

</details>

### 第 三 篇题刻 · `part-p3.svg`

**隐喻**：高级模式篇——山径

<details>
<summary>中文提示词</summary>

```text
风格名称：Dynamic East-Asian Ink Editorial。主题色：炭黑（Charcoal Black）。
两道山坡线夹出垭口，一条虚线山径串起三枚大小渐小的环，如驿站相望。
参考作者/风格名称：Yuko Shimizu —— Dynamic East-Asian Ink Editorial
核心风格特征：流动墨线、东方笔意、明显手绘笔压、停顿与轻微不齐整感，线条带书写性与留白意识，现代 Editorial 构图。
```

</details>

<details>
<summary>English prompt</summary>

```text
Style name: Dynamic East-Asian Ink Editorial. Theme color: Charcoal Black.
Two slope lines pinch a mountain pass; a dotted path strings three rings, each smaller than the last, like stations in sight of one another.
Reference author/style name: Yuko Shimizu — Dynamic East-Asian Ink Editorial
Core style traits: flowing ink linework with an East-Asian brush spirit; visible pen pressure, pauses and slight irregularity; calligraphic lines with a strong sense of negative space; modern editorial composition.
```

</details>

### 第 四 篇题刻 · `part-p4.svg`

**隐喻**：工程实践篇——牌坊驿道

<details>
<summary>中文提示词</summary>

```text
风格名称：Dynamic East-Asian Ink Editorial。主题色：炭黑（Charcoal Black）。
一座两柱横梁的小牌坊，檐口一道弧线，右旁一道直角驿道伸向远处。
参考作者/风格名称：Yuko Shimizu —— Dynamic East-Asian Ink Editorial
核心风格特征：流动墨线、东方笔意、明显手绘笔压、停顿与轻微不齐整感，线条带书写性与留白意识，现代 Editorial 构图。
```

</details>

<details>
<summary>English prompt</summary>

```text
Style name: Dynamic East-Asian Ink Editorial. Theme color: Charcoal Black.
A small two-post gateway with a curved lintel; beside it a right-angled post road runs toward the distance.
Reference author/style name: Yuko Shimizu — Dynamic East-Asian Ink Editorial
Core style traits: flowing ink linework with an East-Asian brush spirit; visible pen pressure, pauses and slight irregularity; calligraphic lines with a strong sense of negative space; modern editorial composition.
```

</details>

### 扉页·四马古车 · `cover.svg`

**隐喻**：扉页——四马古车

<details>
<summary>中文提示词</summary>

```text
风格名称：Dynamic East-Asian Ink Editorial。主题色：炭黑（Charcoal Black）。
一乘四马单辕古车：圆盖三十辐如伞张开，车厢内立戈，御者拱手执辔，车轮十八辐落地，两道云气自后掠过。
参考作者/风格名称：Yuko Shimizu —— Dynamic East-Asian Ink Editorial
核心风格特征：流动墨线、东方笔意、明显手绘笔压、停顿与轻微不齐整感，线条带书写性与留白意识，现代 Editorial 构图。
```

</details>

<details>
<summary>English prompt</summary>

```text
Style name: Dynamic East-Asian Ink Editorial. Theme color: Charcoal Black.
A four-horse chariot of antiquity: a round canopy of thirty ribs opens like an umbrella; a dagger-axe stands in the box; the driver holds the reins; an eighteen-spoke wheel meets the ground; two wisps of cloud sweep past behind.
Reference author/style name: Yuko Shimizu — Dynamic East-Asian Ink Editorial
Core style traits: flowing ink linework with an East-Asian brush spirit; visible pen pressure, pauses and slight irregularity; calligraphic lines with a strong sense of negative space; modern editorial composition.
```

</details>

## 手册不覆盖的另一类：17 张章内插图

本手册的 26 条提示词只覆盖**章徽、篇题刻、老驿卒、扉页车图**这一类——它们是靠生图提示词
起稿、再转成手写 SVG 的。盘上另有 **17 张章内插图**（正文里跟着小节走的那种）不属于这条管线，
它们没有中英双语提示词，也不必强行编一份，故在此登记边界，别让「43 张图 vs 26 条提示词」
这个差额看起来像漏项：

`ch01-five-pillars`、`ch02-turn-loop`、`ch02-cancel-chain`、`ch03-tool-bench`、`ch03-tool-pipeline`、
`ch04-gate-steps`、`ch05-trust-ladder`、`ch06-memory-funnel`、`ch07-four-levels`、
`ch08-hook-line`、`ch09-fork-pipeline`、`ch10-coordinator-fork`、`ch11-skill-stairs`、
`ch12-mcp-state-dial`、`ch13-concurrency-gate`、`ch14-plan-gate`、`ch15-harness-wheel`

（26 + 17 = 43，正好是 `yuyu-book/illustrations/*.svg` 的盘上计数。）

- 这 17 张的取舍与逐轮修订记录在 `.superpowers/sdd/2026-11-02-illustration-rollout/`
  里（`progress.md` 与 `fix-round-1-section.md`），不在本手册；要改画先读那两份。
- 两类图共用同一套硬契约，即上一节第 4 条：`yuyu-book/yuyu_book/art.py` 要求单 svg + viewBox、
  至少一处 `currentColor`、禁 id/href/url/script/style，质感只能来自几何笔触。
  2026-11-04 对 42 张全量复核：`currentColor` 齐、无 `id=`、无 `script`，违约 **0** 张
  （机器口径另有 `test_art.py` 15 测与 `test_illustrations.py` 18 测，同日实跑均 OK）。
- 若日后要为某一张章内插图补提示词（例如换媒介重制），按下一节的模板另起一条，
  并把它归进本手册的计数——那时标题里的「26 份」要一起改，不能只改正文。

---

## 为新增章节续画（模板）

1. 从章节标题提炼一个可入画的隐喻（一个物件，不画界面截图）；
2. 按实时研判从 [yang0/handraw-style](https://github.com/yang0/handraw-style)
   的 367 风格与 36 主题色中重新推荐组合（不写死映射），并附一句具象美学理由；
3. 把上面的基准配方换成新组合，场景句套用本模板；
4. 成图后转为手写 SVG 时遵守 `yuyu-book/yuyu_book/art.py` 硬契约：
   单 svg + viewBox、至少一处 `currentColor`、禁 id/href/url/script/style、
   单元图 ≤ 6000 字节（封面 ≤ 20000）、质感只能来自几何笔触。

---

画风体系来源：[yang0/handraw-style](https://github.com/yang0/handraw-style)
（MIT with Attribution，原作者 yang0）。本手册的提示词规范沿其 skill 输出约定。

## 第二分册 omp · 7 幅篇题刻（新增配方，**SVG 已落成于 `yuyu-book/illustrations-omp/`**；同目录另有 39 枚章徽，记在本节末尾）

本节的 7 条**不在**上面「26 份」的计数里：那 26 条钉的是御舆自己那本书（20 枚单元章徽 + 老驿卒 +
4 幅篇题刻 + 扉页车图），本节的 7 条属于第二分册。七幅已在 2026-11-04 落成，盘上实测 **7 个文件 /
6,222 B**，逐幅 771 / 961 / 847 / 1,099 / 1,020 / 806 / 718 B（单幅上限 6,000 B，最胖的一幅用了 18%）。

这一批走的是**独立目录** `yuyu-book/illustrations-omp/`，装载顺序先查它、查不到再回落共享目录
（`yuyu-book/yuyu_book/art.py`），所以它**没有**打穿御舆侧被测试盯住的张数：`test_docclaims.py` 数
`illustrations/*.svg` 的当前值是 **43**，`README.md` / `en/README.md` / `CREDITS.md` / `STRUCTURE.md` 那几句必须同轮改；
另有一条 `omp_drawings()` 数 `illustrations-omp/*.svg`，钉住 `STRUCTURE.md` 那一行的 **47** =
7 幅题刻 + 39 枚章徽 + 1 幅正文插图（`omp-session-disk.svg`）。
omp 的图也**不进** `docs/illustration-gallery.html`——那是御舆读者侧的成品。过程与本轮全部读数在
`docs/yuyu-overhaul/ILLUST-SYNC.md` 第九、十节。

单元 id 直接取 `manifest-omp.json` 的 7 个篇 id；七篇标题依次是 打地基 / 上手 / 工具箱 / 上下文与记忆 / 扩展 / 实战 / 精通。
装载契约与御舆同一套（`yuyu-book/yuyu_book/art.py`）：单 `<svg>` 带 `viewBox`、至少一处 `currentColor`、
禁 `id=` / `href=` / `url(` / `<style>` / `<script>`、篇题刻 ≤ 6,000 字节、质感只来自几何笔触。

### 为什么第二分册换一支笔（按当前主题实时研判，不写死映射）

- 画风取 `FA-010 · Tom Gauld | Geometric Literary Deadpan`：御舆已经把「流动墨线 + 舆图驿路」那支笔占住了，
  而 omp 是一本**终端里的书**——等距的机器、硬边的几何、极小的人站在极大的结构前面，
  正是「一个人对着一台不解释自己的机器干活」那种干幽默；铅笔几何的留白也比泼墨更贴 monospace 的呼吸。
- 主题色仍由 `C-32 炭黑（Charcoal Black）` 统领：两册要能并排站在同一层书架上，同一管墨是第一件共同语言。
- 第二层灰改 `C-35 石板灰（Slate Gray）`——「理性而利落 充满建筑感」，只落在机关、路面与插口上；
  御舆那枚 `C-15 朱砂红` 仍只作书级点缀（章印），**画面内不出现红**。
- 画幅沿用篇题刻的 200×140 小版画；七幅是一条线的七段，第三篇的空钩位、第五篇的空插口、
  第七篇磨亮的齿轮与第一篇的砖台互为呼应，读者翻到第七篇时才看见第一枚齿轮的下场。

### omp 第一篇 · 打地基 `part-omp-p1.svg`

**隐喻**：砌了一半的砖台，砖缝里咬着齿轮

<details>
<summary>中文提示词</summary>

```text
风格名称：Geometric Literary Deadpan。主题色：炭黑（Charcoal Black）配石板灰（Slate Gray）第二层。
一座砌到一半的砖台，横截面露出三层砖，砖缝里塞进两枚互相咬合的齿轮；一把泥刀随手搁在台面上，刃口朝外；一个极小的人站在台脚，仰头看这道缝。等距铅笔几何，硬边排线，大片留白，画面里没有任何文字。
参考作者/风格名称：Tom Gauld —— Geometric Literary Deadpan
核心风格特征：硬边铅笔几何、等距小机关、极小的人物站在极大的结构前、克制的干幽默、留白多、无文字
```

</details>

<details>
<summary>English prompt</summary>

```text
Style name: Geometric Literary Deadpan. Theme color: Charcoal Black with Slate Gray as the second tone.
A brick platform laid only halfway, its cross-section showing three courses; two meshing gears wedged between the joints; a trowel set down on the top with the edge out; one very small figure at the foot, looking up at the seam. Isometric pencil geometry, hard hatching, wide empty margins, no lettering anywhere.
Reference author/style name: Tom Gauld — Geometric Literary Deadpan
Core style traits: hard-edged pencil geometry, isometric small mechanisms, a tiny figure before an enormous structure, dry restraint, generous negative space, no lettering
```

</details>

### omp 第二篇 · 上手 `part-omp-p2.svg`

**隐喻**：一枚被拧到「一」的老式旋钮，线头打了个结

<details>
<summary>中文提示词</summary>

```text
风格名称：Geometric Literary Deadpan。主题色：炭黑（Charcoal Black）配石板灰（Slate Gray）第二层。
面板上一枚大旋钮，指针正正停在第一格；一根电缆从面板后垂下，中段被人手打了一个笨拙的结，结上又绕了两圈；极小的人一手扶着结，另一手还留着扳手的印子。硬边铅笔几何，第二层灰只落在机器上，留白充足，无文字。
参考作者/风格名称：Tom Gauld —— Geometric Literary Deadpan
核心风格特征：硬边铅笔几何、等距小机关、极小的人物站在极大的结构前、克制的干幽默、留白多、无文字
```

</details>

<details>
<summary>English prompt</summary>

```text
Style name: Geometric Literary Deadpan. Theme color: Charcoal Black with Slate Gray as the second tone.
A big knob on a panel, its pointer stopped exactly on the first notch; a cable hangs behind the panel, tied mid-run in one clumsy knot wrapped twice; a tiny figure steadies the knot with one hand while the other still carries the wrench mark. Hard-edged pencil geometry, a second grey reserved for the machine, ample blank space, no lettering.
Reference author/style name: Tom Gauld — Geometric Literary Deadpan
Core style traits: hard-edged pencil geometry, isometric small mechanisms, a tiny figure before an enormous structure, dry restraint, generous negative space, no lettering
```

</details>

### omp 第三篇 · 工具箱 `part-omp-p3.svg`

**隐喻**：一块钉板，七件家伙什各管一件事，其中一格空着

<details>
<summary>中文提示词</summary>

```text
风格名称：Geometric Literary Deadpan。主题色：炭黑（Charcoal Black）配石板灰（Slate Gray）第二层。
一面钉板，七个影子钩位排成两行，挂着扳手、锤子、卷尺、钳子、手锯、锉刀、螺丝刀，每件只干一件事；其中一格是空的，空位的轮廓线比别的更重；极小的人仰头看那个空位。等距硬边铅笔几何，石板灰只描机器，留白多，无文字。
参考作者/风格名称：Tom Gauld —— Geometric Literary Deadpan
核心风格特征：硬边铅笔几何、等距小机关、极小的人物站在极大的结构前、克制的干幽默、留白多、无文字
```

</details>

<details>
<summary>English prompt</summary>

```text
Style name: Geometric Literary Deadpan. Theme color: Charcoal Black with Slate Gray as the second tone.
A pegboard, seven silhouette hooks in two rows holding a wrench, a hammer, a tape measure, pliers, a hand saw, a file and a screwdriver, each good at exactly one job; one hook stands empty and its outline is drawn heavier than the rest; a tiny figure cranes up at the gap. Isometric hard-edged pencil geometry, slate grey reserved for the tools, generous white, no lettering.
Reference author/style name: Tom Gauld — Geometric Literary Deadpan
Core style traits: hard-edged pencil geometry, isometric small mechanisms, a tiny figure before an enormous structure, dry restraint, generous negative space, no lettering
```

</details>

### omp 第四篇 · 上下文与记忆 `part-omp-p4.svg`

**隐喻**：一只半满的玻璃罐，罐口塞着折角纸条，罐身刻着余量线

<details>
<summary>中文提示词</summary>

```text
风格名称：Geometric Literary Deadpan。主题色：炭黑（Charcoal Black）配石板灰（Slate Gray）第二层。
一只大口玻璃罐，里面塞着几叠对折再对折、边角起毛的纸条，堆到罐子的一半高；罐身上刻着一道清晰的满线，线上方全是空的；极小的人正往里头再塞一张，另一手比了比剩余的空间。硬边铅笔几何，玻璃只用排线表现，留白充足，无文字。
参考作者/风格名称：Tom Gauld —— Geometric Literary Deadpan
核心风格特征：硬边铅笔几何、等距小机关、极小的人物站在极大的结构前、克制的干幽默、留白多、无文字
```

</details>

<details>
<summary>English prompt</summary>

```text
Style name: Geometric Literary Deadpan. Theme color: Charcoal Black with Slate Gray as the second tone.
A wide-mouthed glass jar packed with folded, dog-eared slips of paper stacked to half its height; a clear fill line is scratched on the body, and above it the jar is empty; a tiny figure pushes in one more slip while the other hand measures the leftover room. Hard-edged pencil geometry, glass rendered only as hatching, ample negative space, no lettering.
Reference author/style name: Tom Gauld — Geometric Literary Deadpan
Core style traits: hard-edged pencil geometry, isometric small mechanisms, a tiny figure before an enormous structure, dry restraint, generous negative space, no lettering
```

</details>

### omp 第五篇 · 扩展 `part-omp-p5.svg`

**隐喻**：一条主线分出三个插口，两个插着自制木柄工具

<details>
<summary>中文提示词</summary>

```text
风格名称：Geometric Literary Deadpan。主题色：炭黑（Charcoal Black）配石板灰（Slate Gray）第二层。
一根粗主线横贯画面，从中分出三个同样的插口；左边两个插着看得出是车出来的木柄工具，第三个空着并挂了一小段绳子；主线在插口之后仍是一根，没有变粗。极小的人蹲在第三个插口前，手里捏着一件还没装的东西。等距铅笔几何，石板灰只给插口，留白多，无文字。
参考作者/风格名称：Tom Gauld —— Geometric Literary Deadpan
核心风格特征：硬边铅笔几何、等距小机关、极小的人物站在极大的结构前、克制的干幽默、留白多、无文字
```

</details>

<details>
<summary>English prompt</summary>

```text
Style name: Geometric Literary Deadpan. Theme color: Charcoal Black with Slate Gray as the second tone.
One thick main line running across the sheet, branching into three identical sockets; the left two hold clearly lathe-turned wooden handles, the third stays empty with a short cord hanging from it; past the sockets the main line is still a single line and no thicker. A tiny figure crouches at the third socket holding something not yet fitted. Isometric pencil geometry, slate grey only on the sockets, wide blank space, no lettering.
Reference author/style name: Tom Gauld — Geometric Literary Deadpan
Core style traits: hard-edged pencil geometry, isometric small mechanisms, a tiny figure before an enormous structure, dry restraint, generous negative space, no lettering
```

</details>

### omp 第六篇 · 实战 `part-omp-p6.svg`

**隐喻**：一条被踩实的小路，两道车辙，尽头一间亮灯的小工坊

<details>
<summary>中文提示词</summary>

```text
风格名称：Geometric Literary Deadpan。主题色：炭黑（Charcoal Black）配石板灰（Slate Gray）第二层。
一条从画面前景延伸到远处的小路，路面被踩出两种深浅不同的印子，中间两道车辙压得很实；路尽头一间矮小工坊，门开着，窗里亮一盏灯，灯下有人在搬一件比自己大的东西；路边一根指路石，箭头指向工坊。硬边铅笔几何，亮部只靠留白，石板灰铺路面，无文字。
参考作者/风格名称：Tom Gauld —— Geometric Literary Deadpan
核心风格特征：硬边铅笔几何、等距小机关、极小的人物站在极大的结构前、克制的干幽默、留白多、无文字
```

</details>

<details>
<summary>English prompt</summary>

```text
Style name: Geometric Literary Deadpan. Theme color: Charcoal Black with Slate Gray as the second tone.
A path running from the foreground into the distance, worn in two tones of footfall with two wheel ruts pressed hardest down the middle; at its end a low workshop with the door open and a lamp lit in the window, someone inside hauling an object bigger than themselves; a short stone milestone by the road, its arrow pointing at the workshop. Hard-edged pencil geometry, light made only of blank paper, slate grey on the road surface, no lettering.
Reference author/style name: Tom Gauld — Geometric Literary Deadpan
Core style traits: hard-edged pencil geometry, isometric small mechanisms, a tiny figure before an enormous structure, dry restraint, generous negative space, no lettering
```

</details>

### omp 第七篇 · 精通 `part-omp-p7.svg`

**隐喻**：同一枚齿轮被磨亮了边，一只猫在齿上打盹

<details>
<summary>中文提示词</summary>

```text
风格名称：Geometric Literary Deadpan。主题色：炭黑（Charcoal Black）配石板灰（Slate Gray）第二层。
第一篇里那两枚咬合的齿轮再次出现，但齿顶已经被磨得发亮，边缘只剩薄薄一道；其中一枚上面卧着一只猫，尾巴垂进齿缝，睡得很稳；极小的人坐在旁边，两手空着，没有工具。等距铅笔几何，磨亮处只靠留白表现，石板灰铺暗部，画面安静，无文字。
参考作者/风格名称：Tom Gauld —— Geometric Literary Deadpan
核心风格特征：硬边铅笔几何、等距小机关、极小的人物站在极大的结构前、克制的干幽默、留白多、无文字
```

</details>

<details>
<summary>English prompt</summary>

```text
Style name: Geometric Literary Deadpan. Theme color: Charcoal Black with Slate Gray as the second tone.
The same two meshing gears from the first part return, but their teeth have been worn to a thin bright edge; a cat lies asleep on one of them, tail dropping into the gap between teeth; the tiny figure sits nearby with both hands empty, no tool at all. Isometric pencil geometry, the polished shine suggested only by blank paper, slate grey in the shadows, a quiet picture, no lettering.
Reference author/style name: Tom Gauld — Geometric Literary Deadpan
Core style traits: hard-edged pencil geometry, isometric small mechanisms, a tiny figure before an enormous structure, dry restraint, generous negative space, no lettering
```

</details>

### 章徽那一层（39 枚：`omp-front` / `omp-ch01..33` / `omp-apxa..e`）——这一层没有生图配方

上面 7 条是**篇题刻**的配方：200×140 的小版画，值得先让模型出一张再照着描。章徽不是——它是 64×64、
单色描线、要内联 39 次进同一个离线文件的一枚记号，生图模型给不了这种受约束的几何（它会给出一张带文字的图、
一个 `id=`、一片不能 `currentColor` 的水墨）。所以这一层**直接写 SVG**，配方退化成两条：房规 + 一句隐喻。
下面那张表就是这 39 句隐喻，它是这一层唯一可复制的东西——重画一枚章徽，照抄它的隐喻、按房规落笔即可。

房规（与御舆那 20 枚同一套，`illustrations/front.svg`、`ch07.svg` 是样本）：
`<svg viewBox="0 0 64 64" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round"
stroke-linejoin="round">`；每个描线 `path` / `circle` 带 `pathLength="100"`（成品里的画出动画只认这个属性）；
灰阶靠 `opacity`，必要时配更细的 `stroke-width`；实心点写 `fill="currentColor" stroke="none"` 且**不**带
`pathLength`；单行、结尾 CRLF；不挂御舆那套 `a-*` 动画类。装载契约与门禁同上面 7 幅一条不差
（`art._read()`：≤6,000 B、带 `viewBox`、至少一处 `currentColor`、禁 `id=` / `href=` / `url(` / `<style>` / `<script>`）。

盘上实测（2026-11-04 19:3x）：**39 个文件 / 19,920 B**，最胖 766 B（`omp-ch29`，预算的 12.8 %），
最瘦 229 B（`omp-ch22` 一块拼图），中位 517 B。

| 单元 | 隐喻 | B |
|------|------|---|
| `omp-front` | 摊开的书 + 一行光标 | 404 |
| `omp-ch01` | 一个圈，圈心是提示符 | 303 |
| `omp-ch02` | 一台往外吐下一个 token 的机器 | 676 |
| `omp-ch03` | 三层等距台面，一根轴穿过去 | 429 |
| `omp-ch04` | 把东西放进一只敞口的箱子里 | 473 |
| `omp-ch05` | 插座与插头之间那道缝 | 511 |
| `omp-ch06` | 你说一句，它答一句，两条方向相反的箭头 | 531 |
| `omp-ch07` | 一叠会话，其中一条分岔出去 | 519 |
| `omp-ch08` | 一页纸，一个放大镜压在页角上 | 507 |
| `omp-ch09` | 一个 diff 块，减一行、加一行 | 553 |
| `omp-ch10` | 终端窗口里一个实心三角 | 452 |
| `omp-ch11` | 四个符号节点与它们的边 | 550 |
| `omp-ch12` | 一扇窗口，一个地球 | 517 |
| `omp-ch13` | 一张勾了两项的清单，一条派出去的线 | 602 |
| `omp-ch14` | 后面还压着一页 | 537 |
| `omp-ch15` | 上面摊开的四行，被压成下面两行粗的 | 634 |
| `omp-ch16` | 一只抽屉柜，其中一格亮着 | 534 |
| `omp-ch17` | 一个菱形，分给三种大小 | 733 |
| `omp-ch18` | 一行话里被框住的那个词，上方一颗八角火星 | 596 |
| `omp-ch19` | 一张能力卡，卡里一道闪电 | 400 |
| `omp-ch20` | 两个盒子中间架一个协议节点 | 376 |
| `omp-ch21` | 一枚螺母，一只带眼的钩 | 441 |
| `omp-ch22` | 一块拼图 | 229 |
| `omp-ch23` | 一块面板，三根滑杆停在不同位置 | 626 |
| `omp-ch24` | 一张折叠地图，上面画着一条路线 | 492 |
| `omp-ch25` | 一只虫，背甲中线，四条腿 | 480 |
| `omp-ch26` | 两条方向相反的粗箭头，整块换位置 | 421 |
| `omp-ch27` | 一个勾，落到主干上的一个节点 | 466 |
| `omp-ch28` | 一对尖括号，中间一次调用 | 365 |
| `omp-ch29` | 一只箱子，分发给三个人 | 766 |
| `omp-ch30` | 一张卡，一个感叹 | 525 |
| `omp-ch31` | 一面盾，盾里那一行被抹掉 | 342 |
| `omp-ch32` | 一只表盘，指针偏向贵的另一边 | 612 |
| `omp-ch33` | 一条线上四个节点，末尾一面旗 | 500 |
| `omp-apxa` | 一个提示符，一排开关 | 597 |
| `omp-apxb` | 三枚命令条，一道一道斜杠 | 610 |
| `omp-apxc` | 一把钥匙，下面两行索引 | 503 |
| `omp-apxd` | 一页，页边一条竖线，一个大大的 A | 535 |
| `omp-apxe` | 一枚图钉钉在页边 | 573 |

这一层的判据只有一句：**在 3.2rem（窄屏）和 2.4rem（纸上）还读得出隐喻，才算画完**。
`art._read()` 管不着读不读得出，所以上面 39 句里有 9 句是重画之后的版本
（`ch01` `ch04` `ch05` `ch06` `ch08` `ch09` `ch15` `ch18` `ch21`），改的每一条都是对着截图说的，
过程与字节账在 `docs/yuyu-overhaul/ILLUST-SYNC.md` 第十节。

画风体系来源：[yang0/handraw-style](https://github.com/yang0/handraw-style)。
本节引用的 `FA-010` 画风与 `C-32` / `C-35` / `C-15` 主题色编号，逐条核过该项目
`skills/handdraw-style-prompter/references/styles.json`（367 条）与 `colors.json`（36 条），
编号-名称-作者三列都对上；上游 `images/` 参考图库不复制进本仓。

## 新增解释性手绘：暂停、取消与磁盘状态

这两幅由本项目直接绘制 SVG 几何，不使用第三方图像或生成模型。沿用东方墨线与 `currentColor`，与既有手册的画风索引、署名边界相同；不增加外部字体、纹理或脚本。

| 文件 | 正文位置 | 读图任务 |
|---|---|---|
| `ch02-cancel-chain.svg` | 御舆第 2 章中英版 §2.1 | 左栏 PAUSE 只挡住 UI 的下一次取值，底部 API/tool 仍可能工作；右栏 CANCEL 把信号送到实际操作，再清理资源。不能把“屏幕不动了”当作“工作停止了”。 |
| `omp-session-disk.svg` | Omp 第 7 章 §7.2 | 左边 leaf 回到 A，右边 `file.ts` 仍保留 B 的内容；会话导航不是磁盘回滚。 |

English reading guide: PAUSE suspends event consumption, while CANCEL must reach the operation and cleanup. Moving a conversation leaf does not undo filesystem changes. Both drawings are static and retain the same meaning in dark mode, reduced motion and print.
