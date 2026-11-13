# 专题图解审查

日期：2026-11-07。课程 0.10.0；32.4 秒、1920×1080、30fps。采用纸上逐步追踪，拒绝整页列表和逐字弹跳。备选的倒查答案、双屏对照保留在 STORYLINES.md，本轮未制作。

本片按配音图解交付：屏幕文字保留，另加入中文解说音轨（本地 zh-CN SAPI 合成，48 kHz 立体声 AAC）。未调用收费配音或音乐服务；未做人工听感审校。标题、纸框、曲线箭头和变化中的数值都来自可编辑源码。GSAP 3.14.2 在 assets/ 内保留版权与许可链接；没有新引入第三方音画素材。

## 已检查

- 项目 npm run check 已执行；报告 ok=true。lint、runtime、layout、motion、contrast 无错误。
- 复核每场开头、中段、切点前后和手机宽度联系表；开头有明确问题，纸框承载输入，随后才展开变化与结果。文字没有相互遮挡，末场保留行动入口。
- 数值不是手写的性能结论：概率由与网页相同的人工分数计算；通知来自人工材料；乘法来自同一固定请求的本地计算。本片未访问 DeepSeek V4.1 Flash 或 Kimi K3，没有展示它们的输出或内部概率。
- 阅读停留显式使用 data-hold，动画只用于选择、追加、证据连线和结果出现；无随机、定时器或无限循环。可以在 HyperFrames desktop app 继续编辑。

## 保留的警告

本次警告代码：connector_orphan, connector_orphan, connector_orphan, film_silent。历史渲染曾出现 film_silent；本批已加入解说音轨与连续进度/缩放动画后复渲。connector_orphan 出现在箭头绘制、后续结果尚未展开的时段；终态的输入、箭头和结果均已从实际截图核对。未用忽略标记隐藏这些检查。

## 验证范围

本批已复渲并加音轨：1920×1080、30 fps、32.4s、H.264 + 48 kHz 立体声 AAC；连续缩放/进度条使全片保持可见位移（相邻 0.1s 帧 PSNR≈35.9，非静止）。未抽取 MP4 关键帧做人工画面复核；未做人工听感审校；当前没有真实读者反馈或学习效果分数。

## 实际成片复核 — 2026-11-07（历史：旧静音渲染）

以下记录对应 2026-11-07 当时的静音图解成片（历史交付），**非当前文件**；保留用于追溯，不代表对本批复渲的画面复核。

- 文件：llm-applications.mp4（历史），1920×1080，30/1 fps，32.400000 秒，h264，无音轨。
- SHA-256（历史）：e942ae78793c6c64b2fe6f5b9b1d8fbed7421491044867e1c3a00c10abc41352
- 当时做法：已解码抽帧并对照浏览器画面，取样秒数 [0, 5.4, 16.2, 20, 27, 31.8]；本地原始截图位于 tmp/final-media-frames；不把只看源文件称为看过成片。

## 当前成片记录 — 2026-11-13（本批配音/动画复渲，自动化核对）

- 文件：llm-applications.mp4（当前），1920×1080，30/1 fps，32.400000 秒，h264 + aac (48000 Hz, stereo, 48 kHz)，响度归一化 loudnorm I=-16 LUFS（实测整片 -16.8 LUFS）。
- SHA-256（当前）：7fabd930de4daaa4ce1f4382815a44e7da834a7f3e33dd30e85b13a48f55ed35
- 自动化核对（已执行）：`ffprobe` 确认视频/音频流与时长；相邻帧 `3.0s vs 3.1s` PSNR≈35.87 dB、跨场 `1s vs 6s` PSNR≈14.33 dB；`freezedetect n=-60dB,d=0.3` 记录 1 条；`node scripts/llm/media-manifest.mjs --update` 重绑 sourceHash/deliverySha256；`node scripts/llm/build-media.mjs --check` 与 `node scripts/validate.mjs` 通过（均 exit 0）。
- 未做：未抽取 MP4 关键帧做人工画面复核；未做人工听感审校；未做实际读者测试。**以上不构成“已目视/已试听确认”。**
