# 基线（P0）

平台改造前的冻结快照。这里的内容是“旧构建器当时产出了什么”的证据，不是测试夹具；改造期间用来回答结构是否等价。

## 文件

| 文件 | 内容 |
|---|---|
| `baseline.json` | 20 单元的结构计数、导航锚点、登记表条目、Markdown 行数、HTML/PDF 体积、PDF 页数与书签、环境版本 |
| `fragments/{zh,en}/*.html` | 10 类关键块的原样 HTML 切片：封面、目录、章首、白话带、按语、新词卡、宽表、横版图、来源页、主题索引 |
| `screenshots/*.png` | 12 张关键页截图：封面、目录、正文、宽表、横版图、索引，含暗色窄屏 |
| `video-identity.json` | `video/` 下 474 个跟踪文件的身份：source/config/review/generated/cache/third_party |

## 重生成

先构建（或复用 `yuyu-book/dist/` 中的同名产物），再从仓库根目录运行：

    python scripts/baseline.py
    python scripts/baseline_snapshot.py
    python scripts/video_identity.py

`baseline.json` 与片段是确定性的：同一源码树上连续运行两次，字节应完全一致。可用

    python scripts/baseline.py --check
    python scripts/baseline_snapshot.py --check
    python scripts/video_identity.py --check

对照已提交版本。截图不做字节校验：浏览器版本与字体光栅化会带来像素差异，它们只作视觉对照。

## 环境

`baseline.json.environment` 记录生成时的 Python、Node、Playwright 与 PyMuPDF 版本。PDF 页数随浏览器、字体和平台变化（本机 Windows 与 CI Ubuntu 曾出现 2–22 页差异），比较 PDF 契约时先对齐环境。
