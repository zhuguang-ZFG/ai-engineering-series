# 十卷合订本（2026-11-12 首建，2026-11-13 四次重建）

合订命令、书架入口与测试经 [PR #7](https://github.com/zhuguang-ZFG/ai-engineering-series/pull/7) 合入 `main`；本记录随该 PR 提交，成品哈希以 `dist/yuyu-collected-zh.json` 为准。

把系列十册已发布成品合订为一份 PDF 与一份 EPUB，按卷编号。合订只读取 `agent-books/yuyu-book/dist/` 与 `model-course/deliverables/` 中已存在的成品，不改写任何源稿，也不重新排版卷内正文。

## 命令

```bash
python series.py collected                    # 日期取当天
python series.py collected --date 2026-11-12  # 固定版本记录用
```

成品：

| 文件 | 内容 | 大小与 SHA-256 |
| --- | --- | --- |
| `dist/yuyu-collected-zh.pdf` | 卷首、总目、十卷分隔页，加十册原有页面；2367 页 | 117 MB（122 626 954 B）· `6460e04005a0ca3620961ec67d5a766680d09cad3b2df2e05aa7ec03cc0b4f55` |
| `dist/yuyu-collected-zh.epub` | 合订包：封面、总目、十卷分隔页，加十册原有 spine；70 项（783 个条目） | 60 MB（60 214 031 B）· `9d3b8b315ccaf023fa177588574a39977de369afc83b0fa20a2e9204064905bb` |
| `dist/yuyu-collected-zh.json` | 页数、每卷起止页、来源与成品 SHA-256、读回校验结果 | — |

## 卷次与来源

| 卷 | 册 | 来源成品 | 原页数 |
| --- | --- | --- | --- |
| 卷一 | 大模型：从入门到精通 | `model-course/deliverables/llm-course.pdf` | 469 |
| 卷二 | 提示词工程：从提问到 Agent 协作 | `yuyu-prompt-zh.pdf` | 118 |
| 卷三 | 御舆：解码 Agent Harness | `yuyu-agent-harness-zh.pdf` | 521 |
| 卷四 | Omp 从入门到精通：原理与实战 | `yuyu-omp-zh.pdf` | 432 |
| 卷五 | Pi Agent：从原理到实战 | `yuyu-pi-zh.pdf` | 174 |
| 卷六 | OpenCode：从原理到实战 | `yuyu-opencode-zh.pdf` | 148 |
| 卷七 | DeepSeek Harness：插件化运行时 | `yuyu-deepseek-zh.pdf` | 129 |
| 卷八 | Hermes Agent：记忆、技能与持续任务 | `yuyu-hermes-zh.pdf` | 130 |
| 卷九 | Codex CLI：执行边界与工程实践 | `yuyu-codex-zh.pdf` | 146 |
| 卷十 | Kimi Code：从插件到审查助手 | `yuyu-kimi-zh.pdf` | 84 |

卷内顺序沿用课程先行、工具册在后的读法；八本 Agent 分册保持 `series.json` 的登记次序。页数合计 2351。

## 四次重建（2026-11-13，视觉统一与七幅插图后）

课程册对齐系列令牌并把插图换到同一套暖墨之后，页数由 455 增至 469：七幅新图各占一页，另有长宽比 ≥1.4 的旧图改用 146mm 图框（标签从约 7pt 回到约 10pt），所以增量大于新图数。合订随之重出：`2367 pages, 10 volumes, 802 outline entries`，总目链接 10 行、内部链接重映射 3305 处、删除指向构建机文件的外链 115 处。EPUB 70 项 spine / 783 个条目，重新绑定 EPUBCheck 5.3.0（0 fatal / 0 error / 0 warning，`dist/yuyu-collected-zh-epubcheck.json` 按新 EPUB SHA-256 记录）。同轮 `python -m unittest discover -s tests` 48 项通过，`python series.py check --project all --structure-only` 通过（书架 10 册、20 个入口链接）。

本轮哈希：PDF `6460e04005a0ca3620961ec67d5a766680d09cad3b2df2e05aa7ec03cc0b4f55`（122 626 954 B）、EPUB `9d3b8b315ccaf023fa177588574a39977de369afc83b0fa20a2e9204064905bb`（60 214 031 B）。卷一来源成品的 SHA-256 以 `dist/yuyu-collected-zh.json` 的 `volumes[0].source_sha256` 为准，本轮为 `d03552ea…`（469 页）。

## 三次重建（2026-11-13，C05–C10 重写与导读后）

课程册在机制六章重写并新增《第零章 导读》后由 416 页增至 455 页（`llm-course.pdf`，PDF outline 499 条），合订随之重出：`2353 pages, 10 volumes, 802 outline entries`，总目链接 10 行、内部链接重映射 3305 处、删除指向构建机文件的外链 115 处。EPUB 70 项 spine / 776 个条目，重新绑定 EPUBCheck 5.3.0（0 fatal / 0 error / 0 warning，`dist/yuyu-collected-zh-epubcheck.json` 按新 EPUB SHA-256 记录）。同轮 `python -m unittest discover -s tests` 48 项通过，`python series.py check --project all --structure-only` 通过（书架 10 册、20 个入口链接）。

本轮哈希：PDF `b5950f4275a295bd1ce24829b493f6db125659467be541a6267e54755833e507`（121 167 526 B）、EPUB `2e70d7308e0ad6b0a19e90fc7fcce80ca4e67491669b5b6fc10684db9f07a4de`（59 090 509 B）。卷一来源成品 `llm-course.pdf` 的 SHA-256 以 `dist/yuyu-collected-zh.json` 的 `volumes[0].source_sha256` 为准，本轮为 `3e6515d3…`。

## 二次重建（同日，插图整改后）

课程册在插图整改后由 414 页增至 416 页（`llm-course.pdf` SHA-256 `1307b438…`），合订随之重出：2314 页、10 卷、769 条书签；EPUB 69 项 spine / 775 个条目，重新绑定 EPUBCheck 5.3.0（0 fatal / 0 error / 0 warning，`dist/yuyu-collected-zh-epubcheck.json` 按新 EPUB SHA 记录）。根测试 48 项与 `series.py check --project all --structure-only` 同轮通过。

## 结构

- 卷首 1 页：系列名、十卷题名与日期。
- 总目 5 页：十卷行加各册一级标题，页码指向该卷分隔页；卷行可点击跳转。
- 每卷 1 页分隔页，然后原样合入该册全部页面；书签为「卷一…卷十」两级目录，卷内保留原书签层级再降一级。
- 合计 2367 页（2351 + 10 页分隔 + 6 页卷首与总目）。

EPUB 采用包级合并：十册各自保留原有 `XHTML`、样式、图片与相对路径，放在 `EPUB/vNN/` 下；合订包新增封面、导航与十卷分隔页，spine 为 70 项（十册原有 57 项，加合订新增 13 项——导读页使课程册章节页由 48 增至 49）。每册原有 `nav` 标记降为普通文档，合订包只保留一个 `nav`。总目只链接十卷分隔页；各卷自己的 `nav.xhtml` 保留在包内但不再从总目链接——EPUBCheck RSC-011 不允许导航指向 spine 之外的资源，`verify_epub` 也把这条钉成契约。

九本 Agent 分册的 EPUB 原本就把整册正文放在一个 `content.xhtml` 中（卷三 206、卷四 277 个 manifest 项），合订后保持这一形态；阅读器打开这三册时会加载较大的单页文档。课程册为 49 个独立章节页（新增第零章导读）。

## 已做的验证

- `python -m unittest discover -s tests`：48 项通过（含临时根目录上的十卷合成、页数与书签、总目链接、EPUB spine 解析、导航只指 spine 项的回归、缺册报错、字节稳定与合订入口）。
- `python series.py collected --date 2026-11-13`：输出 `2367 pages, 10 volumes, 802 outline entries`，读回校验核对页数、书签、总目链接与每卷首页文本（首建时为 `2314 / 10 / 769`，三次重建为 `2353 / 10 / 802`）。
- `python series.py check --project all --structure-only`：通过，书架页面重建后 `index.html` 无差异。
- 书架：`dist/index.html` 在合订包存在时增加「十卷合订本」入口，链接只指向 `dist/` 内的成品。
- EPUBCheck 5.3.0（与 CI 同一 pinned 版本，SHA-256 校验通过）：合订包 **0 fatal / 0 error / 0 warning**，报告按 EPUB SHA-256 绑定在 `dist/yuyu-collected-zh-epubcheck.json`。修复过程：首版总目链接了各卷自己的 `nav.xhtml`（spine 之外），EPUBCheck 报 9 个 RSC-011；改为只链接分隔页后清零。

## 范围说明

卷内链接按合订页码重建：各册原有的书签式内部链接改指合订本对应页，只指向构建机文件的外链删除；总目十行与全书书签保持可点。

本轮不产出单文件 HTML 合订本。九本 Agent 分册的 HTML 是各自整册的单文件，而课程册只提供多页站点（`course.html` 是导航页，章节各自成页并依赖外部样式与脚本）。把两种文档模型塞进一个 HTML 需要另一种装配器，不在本次合并内；PDF 与 EPUB 已覆盖全部十卷。

## 未验证

- 卷十（课程）原书为 A5（420 × 595 pt），其余九册为 A4；合订保留各自页面尺寸，未缩放，打印时需按页适配。此取舍保证卷内版式不变。
- 合订本的视觉检查覆盖卷首、总目与抽样分隔页；未逐页复核 2367 页的渲染，也未做纸样或独立读者验收。
- 远端 CI 的 root 任务会运行同一组根测试（含合订装配回归），但不产出合订本：九本 Agent 分册的成品 PDF 尚无 CI 构建，`series.py collected` 仍只在本机执行。
- 合订本不改变各册的版本、许可与验证范围；合订成功不代表模型质量、教学效果或跨平台可用性通过。
