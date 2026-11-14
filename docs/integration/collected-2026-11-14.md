# 十二卷合订本（2026-11-14）

上一版记录见[十卷合订本](collected-2026-11-12.md)。本轮把新成册的 Grok Build 与 Cursor CLI 两册登记进 `series.json`，合订版随之从十卷扩到十二卷；卷内正文仍按各册原有版式，合订命令只生成卷首、总目与分隔页。

## 命令

```bash
python series.py collected                    # 日期取当天
python series.py collected --date 2026-11-14  # 固定版本记录用
```

合订只读取 `agent-books/yuyu-book/dist/` 与 `model-course/deliverables/` 中已存在的成品。缺任何一册时命令报出待构建的书名，不做占位替换。

## 成品

| 文件 | 内容 | 大小与 SHA-256 |
| --- | --- | --- |
| `dist/yuyu-collected-zh.pdf` | 卷首、总目、十二卷分隔页，加各册原有页面；2463 页 | 122.5 MB（128 470 736 B）· `5a1e7a665b9fc393db3971294ca6ce184dcec7420ac1a7421aac93aab25a1864` |
| `dist/yuyu-collected-zh.epub` | 封面、总目、十二卷分隔页，加各册原有 spine；74 个 spine 项（833 个条目） | 60.5 MB（63 440 676 B）· `b473eacfbe6f51258eaf89f13c78752640b53ec811bdc831c5dbf820c92b006f` |
| `dist/yuyu-collected-zh.json` | 页数、每卷起止页、来源与成品 SHA-256、读回校验结果 | — |

## 卷次与来源

| 卷 | 册 | 来源成品 | 原页数 | 分隔页 | 正文起始 |
| --- | --- | --- | --- | --- | --- |
| 卷一 | 大模型：从入门到精通 | `model-course/deliverables/llm-course.pdf` | 478 | 7 | 8 |
| 卷二 | 提示词工程：从提问到 Agent 协作 | `yuyu-prompt-zh.pdf` | 118 | 486 | 487 |
| 卷三 | 御舆：解码 Agent Harness | `yuyu-agent-harness-zh.pdf` | 521 | 605 | 606 |
| 卷四 | Omp 从入门到精通：原理与实战 | `yuyu-omp-zh.pdf` | 432 | 1127 | 1128 |
| 卷五 | Pi Agent：从原理到实战 | `yuyu-pi-zh.pdf` | 174 | 1560 | 1561 |
| 卷六 | OpenCode：从原理到实战 | `yuyu-opencode-zh.pdf` | 150 | 1735 | 1736 |
| 卷七 | DeepSeek Harness：插件化运行时 | `yuyu-deepseek-zh.pdf` | 129 | 1886 | 1887 |
| 卷八 | Hermes Agent：记忆、技能与持续任务 | `yuyu-hermes-zh.pdf` | 130 | 2016 | 2017 |
| 卷九 | Codex CLI：执行边界与工程实践 | `yuyu-codex-zh.pdf` | 146 | 2147 | 2148 |
| 卷十 | Kimi Code：从插件到审查助手 | `yuyu-kimi-zh.pdf` | 84 | 2294 | 2295 |
| 卷十一 | Grok Build：开源编码 Agent 的 Harness | `yuyu-grok-zh.pdf` | 43 | 2379 | 2380 |
| 卷十二 | Cursor CLI：闭源 Agent 的可验证用法 | `yuyu-cursor-zh.pdf` | 40 | 2423 | 2424 |

卷内顺序仍是课程先行、工具册在后的读法；八本 Agent 分册之后接 Grok 与 Cursor 两册，序号由 `scripts/collected.py` 的 `ORDER` 决定，卷数文字由同一处的 `series.volume_count_cn()` 生成，不再把「十卷」写死在封面、元数据与书目卡片里。正文页数合计 2445，加十二张分隔页与六页前置，共 2463 页。

## 校验

- `verify_pdf` 读回 `{pages: 2463, volumes: 12, outline_entries: 830, contents_links: 12}`。
- `verify_epub` 读回 `{verified_spine: 74, verified_volumes: 12}`。
- EPUBCheck 5.3.0（Java 17）：0 fatals / 0 errors / 0 warnings / 0 infos。
- 逐条目比对合集 EPUB 与当前十二册分册 EPUB：831 个条目逐字节相同，差异 0，未嵌入 0。
- 两套单元测试：系列与书架 `tests` 全绿，构建器 `yuyu-book/tests` 全绿。
