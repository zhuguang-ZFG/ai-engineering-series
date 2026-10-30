# Vibe Coding 101

> 不会写代码，也能从一句需求出发，做出第一个可用作品。

![课程封面](book/assets/cover.webp)

本仓库汇集一套面向零基础学习者的 Vibe Coding 课程交付物：完整中文书籍、横版课程视频、竖版短视频，以及可继续编辑的 HyperFrames 源码。

## 内容

| 内容 | 文件 |
| --- | --- |
| 完整书籍 | [`book/book.md`](book/book.md) |
| 横版成片（宣传片） | [`deliverables/vibe-coding-101-landscape.mp4`](deliverables/vibe-coding-101-landscape.mp4) |
| 竖版成片（宣传片） | [`deliverables/vibe-coding-101-vertical.mp4`](deliverables/vibe-coding-101-vertical.mp4) |
| EP.02 成片（1080p） | [`deliverables/ep02-landscape.mp4`](deliverables/ep02-landscape.mp4) |
| EP.03 成片（1080p） | [`deliverables/ep03-landscape.mp4`](deliverables/ep03-landscape.mp4) |
| EP.04 成片（1080p） | [`deliverables/ep04-landscape.mp4`](deliverables/ep04-landscape.mp4) |
| EP.02–04 封面 | `deliverables/ep02-cover.webp`、`ep03-cover.webp`、`ep04-cover.webp` |
| 横版源码 | [`videos/landscape/`](videos/landscape/) |
| 竖版源码 | [`videos/vertical/`](videos/vertical/) |
| EP.02 源码 | [`videos/ep02/`](videos/ep02/) |
| EP.03 源码 | [`videos/ep03/`](videos/ep03/) |
| EP.04 源码 | [`videos/ep04/`](videos/ep04/) |
| 手绘风改造方案（封面 + 书籍图解提示词） | [`design/handdraw/`](design/handdraw/) |

系列正片按集数分目录（`videos/ep02`–`ep04`），宣传片沿用 `videos/landscape`、`videos/vertical`；各集 1080p 成片与 16:9 封面在 `deliverables/` 同名对应。

EP.04《把这条蛇，放到公网上》讲的是打包、托管、真机验收与回滚；源码目录结构与其他成片一致，改完可用 `npm run render:4k` 重出 4K 母版。

## 图片与大文件

书籍插图已全部镜像到 `book/assets/images/`（949 个文件，约 196 MB，Git LFS 存储），书本可离线阅读，不再依赖上游仓库的图片链接。克隆后如需在本地查看插图，执行：

```bash
git lfs install
git lfs pull
```

不拉取 LFS 对象时图片显示为指针文件，文字阅读与 `npm test` 校验不受影响。指向其他章节文档的链接仍指向 [easy-vibe](https://github.com/datawhalechina/easy-vibe) 上游仓库。

## 本地检查

需要 Node.js 22+ 与 FFmpeg：

```bash
npm test
```

检查会验证书籍封面、标题、Markdown 围栏、视频源码结构，以及 MP4 的编码、分辨率、帧率、音轨和时长。

如需编辑视频，在对应目录运行：

```bash
cd videos/landscape   # 或 videos/vertical、videos/ep02–ep04
npm run dev
npm run check
```

`videos/ep04` 的渲染脚本：`npm run render` 出默认分辨率预览，`npm run render:4k` 出 4K 母版，`npm run deliver -- renders/<母版>.mp4` 压出 1080p 交付版。

## 来源说明

书籍内容整理自开源项目 [datawhalechina/easy-vibe](https://github.com/datawhalechina/easy-vibe)。图片使用上游仓库的公开资源链接；课程封面、视频编排和本仓库的交付结构为本项目制作。

> 上游仓库当前未提供可由 GitHub API 识别的许可证文件。转载或再分发前，请自行确认原始内容授权范围。
