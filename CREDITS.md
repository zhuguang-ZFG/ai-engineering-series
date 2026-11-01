# 来源与致谢

本书的每一项外部依据都登记在 [`yuyu-book/sources.json`](yuyu-book/sources.json)（55 条），整书构建时渲染为书内的「来源与许可」页（HTML/PDF 均可从目录跳转）。本书**不转载任何第三方正文或代码**：GitHub 条目钉到 tag 或完整 commit，社区条目一律标注访问日期并降级为非规范来源，`snapshot`/`scope` 字段只记录「何时以何种方式读到什么」。

以下核实动作均于 **2026-10-25** 完成（HTTPS 抓取 + GitHub API 认证查询）；为第 4 章 §4.3.6 的对照面另读的三家非 Anthropic 文档，以及那两个开源仓库的 tag 解析，于 **2026-11-01** 以同一方式完成，各条目的 `accessed` 分别记账。

## 一、版本锚点

全书技术叙述的时间基准：

| 事实 | 取值 | 取证方式 |
| --- | --- | --- |
| Claude Code 最新 GitHub release | `v2.1.310`（2026-10-23T23:39Z） | Releases API `releases/latest` |
| `v2.1.310` tag 指向的 commit | `b70dc4113ad72e0ee44f7b1b95afaf510b53ee98` | `git/ref/tags/v2.1.310` |
| `anthropics/claude-code` main HEAD | `318b7e6ac4e726e88a4ad326214866a93c373b1b`（2026-10-24T02:18Z） | `commits/main` |
| 该 HEAD 下 CHANGELOG 首条版本 | `2.1.310`（与 release tag 一致） | raw.githubusercontent 按 commit 取文件，HTTP 200 |
| npm `@anthropic-ai/claude-code` | latest/next `2.1.310`，stable `2.1.308`，累计 550 个版本，`engines.node >= 22` | registry.npmjs.org 包元数据 |
| Agent SDK Python | `v0.2.174` → commit `0e89b298e771259378a6cd3734e00d323dff5703` | Releases API + `commits/<tag>` |
| Agent SDK TypeScript | `v0.3.310` → commit `019515d3268e6f94946eb2d8e9edc1ea79c5a6aa` | Releases API + `git/ref/tags` |
| MCP 规范最新定版 | `2026-07-28`（上一版 `2025-11-25`） | 规范页 HTTP 200 + 规范仓库 tags 序列 |
| 本书仓库 main HEAD | `12e29d6697993f5f6809c6d01755ff61dc6bb755`（2026-10-16） | `lintsinghua/claude-code-book` API |

SDK TypeScript 的版本尾号（`0.3.310`）与 CLI 版本尾号（`2.1.310`）同步递增，说明 SDK 与 CLI 同属一条发布列车——本书讨论「SDK 能力 vs CLI 内部机制」时以此为依据。

## 二、官方文档（25 条）

前 21 条来自站点 `code.claude.com/docs`，是正文技术叙述的依据；后 4 条来自 Cursor、Qoder、Kimi Code 各自的文档站，只作第 4 章 §4.3.6 的**对照面**，不支撑任何关于 Claude Code 的论断。两组的核实方式相同：先用官方 `sitemap.xml`（Anthropic 侧 2,713 个 `<loc>`，其中 `en/` 页面 227 个；Cursor 文档侧 426 个；Qoder 没有 `sitemap.xml`，只能逐个 URL 试探）与 `llms.txt` 确认页面存在，再对每个入选 URL 单独 GET 并记录 `<title>`，以排除单页应用的「软 404」。

| 登记 ID | 页面 | 支撑章节 |
| --- | --- | --- |
| `docs-how-it-works` | How Claude Code works | 前言、第 1、2 章、附录 D |
| `docs-best-practices` | Best practices for Claude Code | 前言、第 1 章 |
| `docs-interactive-mode` | Interactive mode | 第 2、14 章 |
| `docs-cli-reference` | CLI reference | 第 15 章、附录 C |
| `docs-tools-reference` | Tools reference | 第 3、14 章、附录 B |
| `docs-permissions` | Configure permissions | 第 3、4、8 章、附录 B |
| `docs-permission-modes` | Choose a permission mode | 第 4、14 章 |
| `docs-settings` | Settings files and precedence | 第 5 章、附录 A、C |
| `docs-env-vars` | Environment variables | 第 4、5、11 章、附录 C |
| `docs-memory` | How Claude remembers your project | 第 6、7 章 |
| `docs-context-window` | Explore the context window | 第 7、13 章 |
| `docs-hooks` | Hooks reference | 第 8 章 |
| `docs-sub-agents` | Create custom subagents | 第 9、10 章 |
| `docs-agent-teams` | Orchestrate teams of Claude Code sessions | 第 10 章 |
| `docs-skills` | Extend Claude with skills | 第 11 章 |
| `docs-plugins` | Plugins overview | 第 11、12 章 |
| `docs-mcp` | Connect Claude Code to tools via MCP | 第 12 章 |
| `docs-prompt-caching` | How Claude Code uses prompt caching | 第 7、13 章 |
| `docs-headless` | Run Claude Code programmatically | 第 4、15 章 |
| `docs-agent-sdk-overview` | Agent SDK overview | 第 9、13、15 章 |
| `docs-glossary` | Glossary | 第 2、6、7 章、附录 D |
| `docs-cursor-cli-headless` | Using Headless CLI | 第 4 章 §4.3.6（对照面） |
| `docs-cursor-cli-permissions` | Permissions | 第 4 章 §4.3.6（对照面） |
| `docs-qoder-cli-permissions` | Permissions | 第 4 章 §4.3.6（对照面） |
| `docs-kimi-code-command` | kimi Command | 第 4 章 §4.3.6（对照面） |

第 14 章原本想钉 `/docs/en/plan-mode`，实测 **404**：Plan 模式已并入 `/docs/en/permission-modes`（该页讲 Shift+Tab 切模式与模式选择器），故改钉后者，不虚构链接。

三家对照面站点也各有一处实测 **404**，同样按跳转后可读的规范 URL 记，不照抄索引里的字符串：Cursor 的 `llms.txt` 给的链接带 `.md` 后缀，`/docs/cli/reference/parameters.md` 与 `/docs/cli/reference/permissions.md` 都是 **404**，去掉后缀才 200；`docs.qoder.com/cli` 与 `docs.qoder.com/cli/reference` 这两个看起来最该存在的入口页都是 **404**，真正在的是 `/cli/permissions`、`/cli/commands`、`/cli/quickstart`、`/cli/settings` 这一层。Kimi Code 的文档站在 GitHub Pages 上，`llms.txt` 索引的 `.md` 路径反而是规范地址，取回 200。

## 三、GitHub 仓库与钉版（22 条）

| 登记 ID | 对象 | 钉到什么 |
| --- | --- | --- |
| `cc-changelog` | `anthropics/claude-code/CHANGELOG.md` | commit `318b7e6a…`（main 是分支不是快照，必须钉 HEAD） |
| `cc-release-v2-1-310` | 该 tag 的 Release 页 | tag `v2.1.310` + commit `b70dc411…`（防 tag 被移动） |
| `cc-issues` | Issue 列表 | 基线 commit `318b7e6a…`；列表流动，具体编号在引用时另记 |
| `gh-agent-sdk-python` | `anthropics/claude-agent-sdk-python` | tag `v0.2.174` + commit（MIT） |
| `gh-agent-sdk-typescript` | `anthropics/claude-agent-sdk-typescript` | tag `v0.3.310` + commit |
| `gh-cc-action` | `anthropics/claude-code-action` | tag `v1` + commit `925afb53…`（MIT）：官方把线束搬进 GitHub Actions |
| `gh-dxt` | `anthropics/dxt` | tag `v2.1.2` + commit `2a788100…`（MIT → Apache-2.0 过渡，均宽松）：插件分发包规范 |
| `gh-cc-router` | `musistudio/claude-code-router` | tag `v3.1.3` + commit `3b0aebf3…`（MIT）：在 Claude Code 前插一层模型/工具路由 |
| `gh-cc-templates` | `davila7/claude-code-templates` | tag `v1.29.7` + commit `ad49b119…`（MIT）：成批真实 agents / skills / hooks / MCP 配置 |
| `gh-opencode` | `anomalyco/opencode`（原 `sst/opencode`） | tag `v1.19.4` + commit `148842ef…`（MIT）：另一套从零搭的终端编码线束，仓库已改名迁移 |
| `gh-openhands` | `OpenHands/OpenHands` | tag `v1.33.0` + commit `b968abef…`（MIT）：把智能体全过程写成可回放事件流 |
| `gh-acp` | `zed-industries/agent-client-protocol` | tag `schema-v1.26.0` + commit `e2d83349…`（Apache-2.0）：编辑器与智能体进程之间的第二份协议 |
| `gh-playwright-mcp` | `microsoft/playwright-mcp` | tag `v0.0.83` + commit `f183dad4…`（Apache-2.0）：把浏览器能力摊成工具 schema 的 MCP 服务器 |
| `gh-mcp-servers` | `modelcontextprotocol/servers` | tag `v2.1.0` + commit `ef9808f7…`（MIT → Apache-2.0 过渡）：官方参考实现目录 |
| `gh-codex` | `openai/codex` | tag `rust-v0.164.0` + commit `6aaac694…`（Apache-2.0）：本地沙箱与审批独立成层；第 4 章 §4.3.6 引用的旗标取自本机 `codex-cli 0.166.0` 的 `--help`，比该 tag 新两个 minor，故只引两家都有的写法 |
| `gh-kimi-code` | `MoonshotAI/kimi-code` | tag `@moonshot-ai/kimi-code@2.4.1` + commit `2c73f3f5…`（MIT）：审批折进启动档位的那一套，tag 是附注标签，经 `/git/tags` 解引用 |
| `gh-oh-my-pi` | `can1357/oh-my-pi` | tag `v18.14.2` + commit `7efd7721…`（MIT）：`--approval-mode` 四值那一套，本机跑的就是该 tag 的 `omp/18.14.2` |
| `gh-gemini-cli` | `google-gemini/gemini-cli` | tag `v0.65.0` + commit `6006c14a…`（Apache-2.0）：README 已声明官方入口迁往 Antigravity CLI |
| `gh-superpowers` | `obra/superpowers` | tag `v7.0.1` + commit `2ce8aa15…`（MIT）：方法论装成 skills / 子智能体，多宿主分发 |
| `gh-claude-mem` | `thedotmack/claude-mem` | tag `v15.2.1` + commit `35e24ba7…`（Apache-2.0）：插件形态的跨会话记忆层 |
| `gh-learn-cc` | `shareAI-lab/learn-claude-code` | main HEAD `ce8f9f18…`（MIT，无 release，故钉当时分支头并在 `snapshot` 说明）：从零重建线束的双语教材 |
| `gh-book-repo` | `lintsinghua/claude-code-book` | commit `12e29d66…`：自我引用锚点，便于日后 diff 复盘哪些结论已过期 |

**摄取姿态**：这 16 条生态条目是**对照面，不是依据**。正文的每条技术论断仍只由官方文档、Anthropic 研究博客、MCP 规范与 Claude Code 仓库本身支撑；生态仓库回答的是另一类问题——同一层边界在别人手里会长成什么形状（可换的路由层、另一种上下文路线、第二份协议、无人值守时的权限退化、能力封装单位能长多大）。所以 `scope` 一律写明「第几章的对照面」，`snapshot` 记下 star 量级、最近推送日期与是否归档，日后一眼能看出某个对照面是否已经停摆。候选里 `Aider-AI/aider`（最后一次推送 2026-05-22，已偏旧）、`github/github-mcp-server` 与 `modelcontextprotocol/typescript-sdk`（与已登记条目重合）经比对后未纳入。全部 16 条的 tag→commit 解析走 GitHub API（引用式 tag 再经 `/git/tags` 解引用取完整 40 位 SHA），许可按各仓库 LICENSE 原文核对，仅收 MIT / Apache-2.0 一类的宽松许可。

§4.3.6 用到的另外两家的处境不同：**Cursor 与 Qoder 没有可登记的公开仓库**，本机装的 `agent 2026.10.22-27dcf5f` 与 `qodercli 1.1.81` 都是发行物而非源码，因此这两家只能以 §二 的官方文档页登记，进不了本节——专有文档的许可本来也不符合本节「仅收宽松许可」的口径。它们的旗标语义由此分成两级：文档页写着的（`-p` 与 `--force` 的关系、`ask` 在 headless 下变 Auto-deny）是 B 级；`--yolo` 是 `--force` 的别名、`--sandbox` 只有 enabled/disabled 两值这类只有二进制自己知道的，是本机 `--help` 的 A 级实测，正文里凡引原文都加了引号，读者可以对着同一版本的 `--help` 逐字复核。同一家 Cursor 的两页在「无人值守的写」这一格上并不对齐：headless 页写 "Without `--force`, changes are only proposed, not applied"，permissions 页写 "Print mode can use write and shell tools"。§4.3.6 取前一句，因为它说的是不加旗标时实际发生的事（改动不落盘），后一句只说明工具集没被裁掉——两句可以同真，能核对的只有前一句；这条取舍写在 `docs-cursor-cli-permissions` 的 `scope` 里，Cursor 哪天把两页对齐，这一格就该重写。

## 四、协议规范与工程博客（5 条）

| 登记 ID | 对象 | 发布日期 | 支撑章节 |
| --- | --- | --- | --- |
| `mcp-spec-2026-07-28` | `modelcontextprotocol.io/specification/2026-07-28` | 2026-07-28 | 第 12 章协议基线 |
| `blog-building-effective-agents` | Building Effective AI Agents | 2024-12-19 | 第 1 章、附录 D（workflow / agent 之辨） |
| `blog-multi-agent-research` | How we built our multi-agent research system | 2025-06-13 | 第 9、10 章（编排者—工作者、上下文隔离的代价） |
| `blog-writing-tools-for-agents` | Writing effective tools for AI agents | 2025-09-11 | 第 3、12 章（工具粒度与选择准确率） |
| `blog-context-engineering` | Effective context engineering for AI agents | 2025-09-29 | 第 6、7 章（上下文预算、compaction 的定位） |

MCP 规范以规范仓库的 tags 序列（`2026-07-28`、`2026-07-28-RC`、`2025-11-25`、`2025-06-18`、`2025-03-26`）确认它是定版而非草案；上一版 `…/specification/2025-11-25` 也已核实为 200，作为第 12 章三类原语与 `initialize` 能力协商术语的对照基线（第 12 章不涉及协议版本协商本身）。这些日期是**规范定版日**，不是协议发布日：MCP 由 Anthropic 于 2024-11-25 开源发布，第 1 章时间线按后者取位，两者不可混用。

四条博客在抓取时均发生一次 `/engineering/*` → `/research/*` 的 301，登记时使用**跳转后的规范 URL**。早年的《Claude Code Best Practices》博客现已 301 到 `code.claude.com/docs/en/best-practices`，即内容已并入官方文档；为避免同一内容出现两个条目，只在 docs 族登记一次，重定向关系写进 `snapshot`。

## 五、npm（1 条）

`npm-claude-code` 指向 `registry.npmjs.org/@anthropic-ai/claude-code` 的包元数据（`www.npmjs.com` 页面被 Cloudflare 人机验证拦截，取不到可核实的正文）。注意 `stable` 与 `latest` 当时相差一个 patch：涉及「某行为从哪个版本开始」时必须区分安装渠道。

## 六、社区材料（非规范）

感谢 [Linux.Do](https://linux.do/) 社区对本书的讨论、勘误与网页版衍生项目。帖级落点：

- [`ld-topic-1870593`](https://linux.do/t/topic/1870593) —— 【开源千星】《御舆：解码 Agent Harness——Claude Code 架构深度剖析》，板块「文档共建」，2026-03-31/04-01。
- [`ld-topic-1871393`](https://linux.do/t/topic/1871393) —— [开源] 基于站内项目构建的网页版 book，2026-04-01。

两条帖子的直连均为 **403**（Cloudflare 反爬，HTML 与 Discourse JSON 接口都封锁，换 UA 无效），标题/板块/作者/日期经搜索引擎索引的多个结果交叉确认。因此它们只记录来源谱系与社区脉络，`normative: false`，**不支撑任何技术事实**；技术事实一律由文档、GitHub、规范与博客条目承担。

## 七、未能核实，故不登记

| 尝试的 URL | 结果 |
| --- | --- |
| `code.claude.com/docs/en/plan-mode` | 404，改钉 `permission-modes` |
| `modelcontextprotocol.io/docs/getting-started/introduction` | 404，第 12 章只钉规范正文页 |
| `anthropic.com/engineering/managing-instruction-memory-hierarchical-technique` | 404，第 6 章改由 `docs-memory` + 上下文工程博客支撑 |
| `…/specification/2026-07-28/basic/lifecycle` | 301 → `/basic/versioning`，引用时用跳转后 URL |
| `www.npmjs.com/package/@anthropic-ai/claude-code` | 403，改用 registry JSON |
| `www.reddit.com/r/ClaudeAI/*.json`、`old.reddit.com/...` | 403；后者虽 200 但正文是登录墙页 —— 状态码 200 不等于内容可核实，故不登记 |
| `api.github.com` 匿名请求 | 403（速率限制），改用已认证的 `gh api`，不影响 URL 有效性 |

## 八、图形资产

- **封面**：仓库根 `cover.png` 由 [`scripts/typeset_cover.py`](scripts/typeset_cover.py) 在未署名版画 [`scripts/assets/cover-art.png`](scripts/assets/cover-art.png) 上排版生成，只用于 README。2026-10-31 起与整书设计系统对齐：原洋红题头块改为墨漆炭黑（C-32），版画经纸面→炭墨双色调（duotone）重上墨到书的暖纸上，分隔线用朱砂（C-15），字体按平台探测（macOS Songti/STHeiti/Hiragino，Windows SimSun/微软雅黑）。整书的扉页不借用这张位图：它用的是 [`yuyu-book/illustrations/cover.svg`](yuyu-book/illustrations/cover.svg)——四马单辕、圆盖三十辐（与第一篇题刻同数）、车厢内立戈的一乘古车白描，与章徽同一支笔法、同样只以 `currentColor` 上色，因此屏幕、暗色与纸面三种情形下都是同一套墨色，也不需要裁切、滤镜或 base64 内嵌。
- **图版**：全书 320 张图（中英各 160）源自正文内的 Mermaid 代码块，构建时用 Mermaid `11.17.2`（`package.json` 的 devDependency）在无头 Edge/Chromium 中预渲染为 SVG 并内嵌，套用统一的「舆」主题变量；渲染缓存位于 `yuyu-book/.cache/mermaid/`，缓存键含 Mermaid 版本、浏览器版本与图源哈希。
- **装饰与插图**：车轮（辐）纹样、分隔符与章节印章均为 `yuyu_book/style.py` 内联生成的矢量图形。每单元一枚章徽、每篇一幅题刻、扉页一幅车图（共 26 份，[`yuyu-book/illustrations/`](yuyu-book/illustrations/)）是本书自绘的单线白描，只用 `currentColor` 上色、不含 id 与任何外部引用，由 [`yuyu_book/art.py`](yuyu-book/yuyu_book/art.py) 在装配前逐个把关（体积上限、`viewBox`、禁用 `id=`/`href=`/`url()`/`<style>`/`<script>`）；车图铺满整个版面，故单独享有比章徽高数倍的体积上限。章眉之下另有一条按单元 id 定种的手绘走线（`trace()`，中文 20 枚、英文 20 枚，两两不同），章末收在两轮压出、渐次散成短划的双线上（`rut()`，中文 20 枚），分部过渡页的目标与章表之间横一条手绘道路——起点一枚辐轮，一站一圈正对应该部的一章（`route_map()`，4 条，4/4/4/3 站各不相同），提示块开头是手写墨记（`ink_mark()`，中文 74 处），小节之间的分隔线收在一对焊盘之间的耦合线（`knot()`，中文 111 处），目录之后另起一页把全书画成一条路（`itinerary()`，中英各 1 幅：路头一枚辐轮、15 枚站圈、4 个岔线点，由种子定形），它的图例与侧栏入口用同三支笔的三枚小标记（`key_mark()`，每版 4 枚），章末那行按语左边坐着同一位戴斗笠、提灯笼的老驿卒（`keeper()`，中英各 20 枚）——八者都走 `currentColor`，因此暗色与纸面上自动换成对应墨色。这些图形都不引用外部图标、字体或图片素材。
- **Star History**：`docs/images/star-history-{light,dark}.svg` 由 [`scripts/star_history.py`](scripts/star_history.py) 从 star-history.com 取数生成，仅用于 README，不进入整书产物。
- **画风体系**：26 份插图（章徽、篇题刻、老驿卒、扉页车图）的画风选型与方法论基于开源项目 [yang0/handraw-style](https://github.com/yang0/handraw-style)（367 种编号画风与 36 种经典单色主题色库，MIT with Attribution）。本次手绘化改造选定的基准组合为 `FD-001 · Dynamic East-Asian Ink Editorial` 画风 + `C-32 炭黑` / `C-15 朱砂红` 主题色，由该项目 skill 的实时研判流程选出；适配层安装在 `.claude/skills/handdraw-style-prompter/`（仅目录文本，不含上游参考图）。依其许可要求在此保留原作者 yang0 与仓库链接的署名。2026-10-31 的设计系统转译沿用同一配方：原「青铜配件」三色令牌整体转译为 C-32 炭墨三阶（浓墨/次墨/淡墨，明暗双版各自调值），朱砂（C-15）成为全书唯一点缀色并落到章印——章印一律朱砂手盖章（轻微歪斜 + 印泥内环），卡片/印章/代码块的两种圆角令牌改为手裁不对称四角（仍保持全书只有两种圆角的设计契约），滚动自绘动画（ink-draw）覆盖章徽、驿卒、篇题、封面与 trace/route/itinerary 全部程序生成图形，打印/PDF 与减动效环境自动落回静态成品图。

## 九、引用姿态与准确性

1. **分析基准**：技术描述以 Claude Code `2.1.310`（tag commit `b70dc411…`）与仓库 main HEAD `318b7e6a…` 为核对基线，外部来源统一访问日期 2026-10-25。版本更新后，凡正文写「默认值/事件名/旗标拼写」的段落都应重新比对该三处锚点。
2. **许可姿态**：`anthropics/claude-code` 的 LICENSE 为「© Anthropic PBC. All rights reserved.」，npm 包内 license 字段为 `SEE LICENSE IN README.md`——均为专有。故对 Anthropic 的源码与文档一律**只链接、只摘录最小必要的字段名/事件名等事实性标识**；Agent SDK Python 为 MIT，TS 仓库以其自身 LICENSE 为准；MCP 规范以其自身声明为准。本书文字为 CC BY-NC-SA 4.0，第三方资料保留原许可。
3. **文档在快速改写**：同一能力可能从博客迁到文档（best-practices）、从独立页并入上级页（plan-mode → permission-modes；lifecycle → versioning）。凡引用「官方怎么说」，优先指向现行文档页，并把历史 URL 的重定向关系记在 `snapshot` 里。
4. **流动内容不作规范源**：issue 列表、论坛帖、星标数（本书仓库当日 `stargazers_count` 为 4324）只用于时间脉络。
5. **可复现性**：`sources.json` 对 GitHub 条目钉 tag + 完整 SHA，文档/博客条目记访问日期与页面标题，社区条目额外标 `normative:false`；`manifest.json` 的 `guides[*].sources` 把 20 个单元各自映射到 3–9 条来源，任何一条正文论断都能回溯到「当时可见的哪个快照」。
6. **文风校准**（2026-10-31）：按开源项目 [Nanako0129/sepia](https://github.com/Nanako0129/sepia)（MIT）的「去 AI 味」方法论做了一轮最小原位改写——只删元话语脚手架（「值得注意的是」「影响是深远的」「如果说……那么」）、换掉空泛宣告与匀速排比，不新增任何技术断言；所有修改逐行原地等行，`manifest.json`/`glosses.json` 的行号证据锚点因此逐一仍然指得回原散文。

## 十、构建与校验

`yuyu-book/build.py` 在每次构建时执行契约校验：manifest 引用的文件必须存在、磁盘上的单元必须被 manifest 收录、罗盘（本章问题/读完交付/本章边界）中英双全、每条来源已登记且过许可门禁、通俗层的每一句白话都带指得回书稿的行号证据、磁盘上的每一枚插图都必须真的上了页面、HTML 产物零断链、零重复 id、零外部资源引用。CI 见 [`.github/workflows/book.yml`](.github/workflows/book.yml)。
