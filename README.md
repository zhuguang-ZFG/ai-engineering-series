# Vibe Coding 101

> 不会写代码，也能从一句需求出发，做出第一个可用作品。

![课程封面](book/assets/cover.webp)

本仓库汇集一套面向零基础学习者的 Vibe Coding 课程交付物：完整中文书籍、横版课程视频、竖版短视频，以及两套可继续编辑的 HyperFrames 源码。

## 内容

| 内容 | 文件 |
| --- | --- |
| 完整书籍 | [`book/book.md`](book/book.md) |
| 横版成片 | [`deliverables/vibe-coding-101-landscape.mp4`](deliverables/vibe-coding-101-landscape.mp4) |
| 竖版成片 | [`deliverables/vibe-coding-101-vertical.mp4`](deliverables/vibe-coding-101-vertical.mp4) |
| 横版源码 | [`videos/landscape/`](videos/landscape/) |
| 竖版源码 | [`videos/vertical/`](videos/vertical/) |

## 本地检查

需要 Node.js 22+ 与 FFmpeg：

```bash
npm test
```

检查会验证书籍封面、标题、Markdown 围栏、视频源码结构，以及 MP4 的编码、分辨率、帧率、音轨和时长。

如需编辑视频，在对应目录运行：

```bash
cd videos/landscape   # 或 videos/vertical
npm run dev
npm run check
```

## 来源说明

书籍内容整理自开源项目 [datawhalechina/easy-vibe](https://github.com/datawhalechina/easy-vibe)。图片使用上游仓库的公开资源链接；课程封面、视频编排和本仓库的交付结构为本项目制作。

> 上游仓库当前未提供可由 GitHub API 识别的许可证文件。转载或再分发前，请自行确认原始内容授权范围。
