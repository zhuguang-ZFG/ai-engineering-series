# 封面提示词（书封面 + 5 集视频封面）

> **落地状态（2026-10-31）**：第 3–5 组（EP.02–04）已按下文主题改为**代码绘制**的 HTML/SVG 实现，
> 源文件见 `covers/ep0X.html`、`covers/cover.css`，渲染脚本 `render_covers.py`。下面保留的生图提示词
> 供以后想换成生图模型出图时使用；第 0–2 组（书封面、EP.01 横/竖）仍未落地。

统一风格：`FA-013` Bold Flat Everyday Satire（Jean Jullien，名字即可激活，无需垫图、无需特征段）。
统一主色：`C-11` 祖母绿；点缀：`C-26` 柿子橙（只给苹果、CTA、箭头）。
提示词内部不写任何编号，编号只出现在本文件的说明里。中英文任选其一使用。

---

## 0. 书封面（`book/assets/cover.svg` / `cover.webp`，16:9）

主标题：`Vibe Coding 101`；副标题：`不会写代码，也能做出第一个作品`。

```text
书籍摘要：一门给零基础学习者的 Vibe Coding 课，从一句中文需求出发，做出能玩的小游戏，再迭代、调试、发布到公网。
受众：完全不会写代码、但想亲手做出作品的中文学习者。
业务场景：在线课程书籍封面（16:9 横版）。
画幅与构图规范：16:9。核心隐喻与主标题收拢在中央安全区，上下左右各留至少 12% 空白。
风格名称：Bold Flat Everyday Satire。参考作者与风格名称：Jean Jullien / Bold Flat Everyday Satire。
主题色：祖母绿（Emerald Green），点缀柿子橙（Persimmon Orange）。
主题：一张白色背景上，一个普通人随手说出的一句话气泡，气泡里掉出一条由绿色色块拼成的贪吃蛇，蛇正咬着一颗柿子橙色的苹果；主标题「Vibe Coding 101」用醒目粗体放在上方，副标题「不会写代码，也能做出第一个作品」一行小字放在标题下方，此外不要其他小字。
先设计隐喻再出图，主标题明显，小字少或者没有小字。其他你帮我设计。
请设计书籍封面。
```

```text
Book summary: a Vibe Coding course for absolute beginners — from one plain-Chinese sentence to a playable little game, then iterate, debug and publish it to the public web.
Audience: Chinese-speaking learners who cannot code but want to build something real.
Scenario: online course book cover, 16:9 landscape.
Framing: 16:9. Keep the central metaphor and the main title inside the central safe zone with at least 12% breathing room on every side.
Style name: Bold Flat Everyday Satire. Reference author and style name: Jean Jullien / Bold Flat Everyday Satire.
Theme color: Emerald Green, with Persimmon Orange accents.
Theme: on a white background, an ordinary person speaks a casual sentence in a speech bubble, and out of the bubble drops a snake built from flat green blocks, about to bite a persimmon-orange apple. Bold main title "Vibe Coding 101" on top, one small subtitle line "不会写代码，也能做出第一个作品" beneath it, no other small text.
Design a visual metaphor first, then generate the image. Make the main title bold and prominent, with few or no small text. Pick the rest of the design for me.
Please design the book cover.
```

---

## 1. EP.01 横版封面（`deliverables/landscape-cover.webp`，16:9）

主标题：`不会写代码 也能做软件`。

```text
视频摘要：3 分钟宣传片，证明一个不会写代码的人，只靠说清楚需求，就能让 AI 做出一条能玩的贪吃蛇。
受众：刷到视频、对 AI 编程好奇但从未写过代码的人。
业务场景：视频封面（16:9 横屏，B站/视频号）。
画幅与构图规范：16:9。隐喻主体与主标题集中在中央安全区，四周留白 ≥12%。
风格名称：Bold Flat Everyday Satire。参考作者与风格名称：Jean Jullien / Bold Flat Everyday Satire。
主题色：祖母绿（Emerald Green），点缀柿子橙（Persimmon Orange）。
主题：一个摊手耸肩、表情淡定的普通人站在左侧，右侧一条粗黑轮廓的绿色贪吃蛇自己从电脑屏幕里探出头来咬苹果；人物与蛇形成「我什么都没做，它自己跑出来了」的反差幽默。主标题「不会写代码 也能做软件」用超大粗体压在上方，除此之外不要小字。
视频封面设计，网感强，吸引人眼球。先设计隐喻再出图，主标题明显，小字少或者没有小字。其他你帮我设计。
```

```text
Video summary: a 3-minute trailer proving that someone who cannot code can still get AI to build a playable snake game just by stating the requirement clearly.
Audience: casual viewers curious about AI coding who have never written code.
Scenario: video cover, 16:9 landscape for Bilibili / Channels.
Framing: 16:9, central safe zone, at least 12% margin on all sides.
Style name: Bold Flat Everyday Satire. Reference author and style name: Jean Jullien / Bold Flat Everyday Satire.
Theme color: Emerald Green with Persimmon Orange accents.
Theme: a deadpan person shrugging on the left while a thick-outlined green snake pokes its own head out of a laptop screen on the right to bite an apple — the joke is "I did nothing, it came out by itself". Huge bold title "不会写代码 也能做软件" across the top, no other small text.
Video cover design, strong internet-native appeal, eye-catching. Design a visual metaphor first, then generate the image. Make the main title bold and prominent, with few or no small text. Pick the rest of the design for me.
```

---

## 2. EP.01 竖版封面（`deliverables/vertical-cover.webp`，9:16，另裁 3:4）

主标题：`不会写代码 也能做软件`；徽章：`39″ 看完`。

```text
视频摘要：39 秒竖版短片，同一件事——一句话需求，AI 做出能玩的贪吃蛇。
受众：抖音/视频号竖屏信息流的零基础观众。
业务场景：视频封面（9:16 竖屏，另需 3:4 版本）。
画幅与构图规范：9:16。主标题、蛇与徽章全部收在中央 70% 安全区内，上下各留 15% 空白，防止平台标题栏和头像遮挡。
风格名称：Bold Flat Everyday Satire。参考作者与风格名称：Jean Jullien / Bold Flat Everyday Satire。
主题色：祖母绿（Emerald Green），点缀柿子橙（Persimmon Orange）。
主题：竖构图，上方超大粗体主标题「不会写代码 也能做软件」，中央一条绿色块贪吃蛇绕成一个问号形状，蛇头咬着柿子橙色苹果，问号下方一个摊手的极简人物；右上角一枚柿子橙色圆形徽章写「39″ 看完」。除主标题与徽章外不要其他文字。
视频封面设计，网感强，吸引人眼球。先设计隐喻再出图，主标题明显，小字少或者没有小字。其他你帮我设计。
```

```text
Video summary: a 39-second vertical short — one plain sentence in, a playable snake game out.
Audience: vertical-feed viewers on Douyin / Channels with zero coding background.
Scenario: vertical video cover, 9:16 (a 3:4 variant is also needed).
Framing: 9:16. Keep the title, snake and badge inside the central 70% safe area, with 15% clear space top and bottom so platform UI never covers them.
Style name: Bold Flat Everyday Satire. Reference author and style name: Jean Jullien / Bold Flat Everyday Satire.
Theme color: Emerald Green with Persimmon Orange accents.
Theme: vertical composition. Huge bold title "不会写代码 也能做软件" at the top; in the middle a green block snake curls into the shape of a question mark, its head biting a persimmon-orange apple; below the question mark a minimal shrugging figure; a persimmon-orange round badge in the upper right reads "39″ 看完". No text other than the title and the badge.
Video cover design, strong internet-native appeal, eye-catching. Design a visual metaphor first, then generate the image. Make the main title bold and prominent, with few or no small text. Pick the rest of the design for me.
```

---

## 3. EP.02 封面（`deliverables/ep02-cover.webp`，16:9）

主标题：`会写诗的贪吃蛇`。

```text
视频摘要：上一集做好的贪吃蛇，这一集接上真实 AI 能力，蛇不只是会动，还会开口写诗。
受众：看完 EP.01、想知道「接下来还能加什么」的零基础学习者。
业务场景：视频封面（16:9 横屏）。
画幅与构图规范：16:9，中央安全区，四周留白 ≥12%。
风格名称：Bold Flat Everyday Satire。参考作者与风格名称：Jean Jullien / Bold Flat Everyday Satire。
主题色：祖母绿（Emerald Green），点缀柿子橙（Persimmon Orange）。
主题：绿色贪吃蛇盘坐在一台打字机前，神情严肃像位诗人，打字机里吐出的纸带上不是代码而是几行中文诗句，蛇尾还卷着一颗苹果；画面幽默但不幼稚。主标题「会写诗的贪吃蛇」超大粗体置于上方，不要其他小字。
视频封面设计，网感强，吸引人眼球。先设计隐喻再出图，主标题明显，小字少或者没有小字。其他你帮我设计。
```

```text
Video summary: the snake built in episode one now gets real AI capability — it does not just move, it writes poetry.
Audience: beginners who finished EP.01 and wonder what can be added next.
Scenario: video cover, 16:9 landscape.
Framing: 16:9, central safe zone, at least 12% margin on all sides.
Style name: Bold Flat Everyday Satire. Reference author and style name: Jean Jullien / Bold Flat Everyday Satire.
Theme color: Emerald Green with Persimmon Orange accents.
Theme: a green snake sits at a typewriter with the solemn expression of a poet; the paper strip coming out carries a few lines of Chinese verse instead of code, and the snake's tail still holds an apple. Humorous but never childish. Huge bold title "会写诗的贪吃蛇" across the top, no other small text.
Video cover design, strong internet-native appeal, eye-catching. Design a visual metaphor first, then generate the image. Make the main title bold and prominent, with few or no small text. Pick the rest of the design for me.
```

---

## 4. EP.03 封面（`deliverables/ep03-cover.webp`，16:9）

主标题：`这条蛇，住进项目里`。

```text
视频摘要：离开浏览器，把贪吃蛇搬进本地项目：装 AI IDE、加文件、加依赖、学会调试。
受众：准备从「玩一下」走向「认真做个项目」的学习者。
业务场景：视频封面（16:9 横屏）。
画幅与构图规范：16:9，中央安全区，四周留白 ≥12%。
风格名称：Bold Flat Everyday Satire。参考作者与风格名称：Jean Jullien / Bold Flat Everyday Satire。
主题色：祖母绿（Emerald Green），点缀柿子橙（Persimmon Orange）。
主题：绿色贪吃蛇拖着一只小行李箱，正搬进一栋由文件夹图标搭成的房子，房门是一块终端窗口，门口挂着「git」门牌；蛇的表情像搬新家一样期待。主标题「这条蛇，住进项目里」超大粗体置于上方，除门牌与主标题外不要其他文字。
视频封面设计，网感强，吸引人眼球。先设计隐喻再出图，主标题明显，小字少或者没有小字。其他你帮我设计。
```

```text
Video summary: leave the browser and move the snake into a real local project — install an AI IDE, add files, add dependencies, learn to debug.
Audience: learners ready to go from "playing around" to "running a real project".
Scenario: video cover, 16:9 landscape.
Framing: 16:9, central safe zone, at least 12% margin on all sides.
Style name: Bold Flat Everyday Satire. Reference author and style name: Jean Jullien / Bold Flat Everyday Satire.
Theme color: Emerald Green with Persimmon Orange accents.
Theme: a green snake dragging a tiny suitcase moves into a house built from folder icons; the front door is a terminal window and the door plate reads "git"; the snake looks as excited as someone moving into a new home. Huge bold title "这条蛇，住进项目里" across the top, no text other than the title and the door plate.
Video cover design, strong internet-native appeal, eye-catching. Design a visual metaphor first, then generate the image. Make the main title bold and prominent, with few or no small text. Pick the rest of the design for me.
```

---

## 5. EP.04 封面（`deliverables/ep04-cover.webp`，16:9）

主标题：`把这条蛇，放到公网上`。

```text
视频摘要：打包、托管、真机验收、回滚——把本地项目发布成一条任何人用手机就能打开的 https 链接。
受众：作品已经能在自己电脑上跑、想让朋友也能打开的学习者。
业务场景：视频封面（16:9 横屏）。
画幅与构图规范：16:9，中央安全区，四周留白 ≥12%。
风格名称：Bold Flat Everyday Satire。参考作者与风格名称：Jean Jullien / Bold Flat Everyday Satire。
主题色：祖母绿（Emerald Green），点缀柿子橙（Persimmon Orange）。
主题：绿色贪吃蛇从一台笔记本电脑屏幕里纵身跃起，跳进一朵云，云的下方几只手机同时亮起同一条蛇；一根柿子橙色箭头从笔记本指向手机，暗示「发布上线」。主标题「把这条蛇，放到公网上」超大粗体置于上方，不要其他小字。
视频封面设计，网感强，吸引人眼球。先设计隐喻再出图，主标题明显，小字少或者没有小字。其他你帮我设计。
```

```text
Video summary: build, host, verify on a real phone, roll back — turn a local project into one https link anyone can open on their phone.
Audience: learners whose project already runs on their own computer and who want friends to open it too.
Scenario: video cover, 16:9 landscape.
Framing: 16:9, central safe zone, at least 12% margin on all sides.
Style name: Bold Flat Everyday Satire. Reference author and style name: Jean Jullien / Bold Flat Everyday Satire.
Theme color: Emerald Green with Persimmon Orange accents.
Theme: a green snake leaps out of a laptop screen into a cloud, and below the cloud several phones light up with the very same snake; a persimmon-orange arrow points from the laptop to the phones, meaning "shipped". Huge bold title "把这条蛇，放到公网上" across the top, no other small text.
Video cover design, strong internet-native appeal, eye-catching. Design a visual metaphor first, then generate the image. Make the main title bold and prominent, with few or no small text. Pick the rest of the design for me.
```
