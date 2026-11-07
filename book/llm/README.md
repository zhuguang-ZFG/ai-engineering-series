# 把大模型拆开看

先看一句话怎样生成，再追到向量、注意力和参数更新，最后用检索、工具与证据核验完成一份资料报告。十二课已经可以离线阅读和操作，无需账号、API 密钥或 GPU。

下载 [手绘 PDF](../../deliverables/llm-explained-handdraw.pdf) 或 [EPUB](../../deliverables/llm-explained-handdraw.epub)：收录四十八张手绘图、纸上实验、结果与自测答案。PDF 适合打印，EPUB 适合在阅读器里调整字号。当前 0.13.0 用杯中饮料、通知冲突和执行回执带出问题，每课穿插两张新手绘，再用逐步算例与反例解释原因，展开教师/学生蒸馏、软硬标签、温度和错误继承，并提供可操作的蒸馏实验。书内保留结构、缓存/专家/成本、应用和系统四个精选附录；另有多模态、向量检索、MCP/A2A 回查及十二张讲义和图卡。

在项目根目录双击 [开始阅读.html](../../开始阅读.html)，即可找到网页、PDF 和 EPUB。两份电子书位于 `deliverables/`。

网页支持三档正文字号、课内目录、本机续读和手绘放大。手机目录默认收起，桌面可沿小节回查；不启用脚本也能读全文、展开目录和打开原图。手机读到正文中段后，可用“本课目录”直接回查；目录标出当前小节，大图保留原图注。PDF 目录标明本轮排版的实际页码，独立公式与解释保持相邻；EPUB 在章首和各节提供返回本课目录的链接。

书末新增六道[换材料练习](../../exports/llm/check-understanding.html)。需要写画时下载 [A4 练习 PDF](../../deliverables/llm-reading-tasks.pdf)，做完再看[核对依据与陪读记录](../../exports/llm/review-guide.html)或[陪读 PDF](../../deliverables/llm-reading-guide.pdf)。题目与参考答案分开；通知、概率和回执均为人工练习材料，真实试读尚未进行。

- [十二张手绘讲义](../../exports/llm/deck.html) · [复习图卡](../../exports/llm/cards.html)
- [多模态输入](../../exports/llm/multimodal-reference.html) · [Embedding 与检索](../../exports/llm/embedding-reference.html) · [MCP/A2A](../../exports/llm/protocols-reference.html)
- [打开学习页](../../exports/llm/index.html)
- [L01 文字怎样变成模型的输入？](lessons/tokens.md)
- [L02 为什么同一句话能接出不同结果？](lessons/generation.md)
- [L03 一串数字怎么表示语言？](lessons/vectors.md)
- [L04 模型怎样利用前文？](lessons/attention.md)
- [L05 模型是怎样学会的？](lessons/training.md)
- [L06 会续写为什么还要学听指令？](lessons/assistant.md)
- [L07 怎样把一件事交代清楚？](lessons/context.md)
- [L08 怎样发现一个看似合理的错误？](lessons/evidence.md)
- [L09 怎样让它用上自己的资料？](lessons/retrieval.md)
- [L10 怎样让模型调用工具？](lessons/tools.md)
- [L11 什么时候需要搭系统？](lessons/approaches.md)
- [L12 做一个能交付的资料助手](lessons/project.md)

第一次来，可以先做 L02，再回看 L01，最后完成 L07 的通知核验。想追问内部机制，接着读 L03–L06；要应用到工作，继续 L08–L12。课程尚未经过真实初学者试读。

实际模型案例使用 DeepSeek V4.1 Flash 与 Kimi K3。页面给出可复做的同题任务，记录日期、版本、模式和回答依据；没有编造模型输出或比较跑分。官方资料与版本边界维护在 [models.json](models.json)，主张来源见 [sources.json](sources.json)。

想继续追问显存、专家和长上下文，可以看[缓存、MoE 与计算成本](../../exports/llm/advanced.html)。完整的[原理回查页](../../exports/llm/principles-reference.html)与旧书“大语言模型的工作原理”一章来自同一修订稿，纠正了固定语义维度、模板即能力、学科专家路由、无遗忘和恒定总显存等说法；分词表保留原混合输入并附可复算的 ID 与字节。对应公开报告只支持所述版本，不据 V3 或 R1 推断 V4.1 Flash 与 Kimi K3。

## 内容维护

课文维护在 `lessons/`，路线和自测维护在 `course.json`，来源范围在 `sources.json`。手绘图在 `../assets/handdraw/llm/`。`npm run build:llm` 生成网页，输出页可直接用浏览器打开；数据内嵌，交互脚本随页附带，不依赖服务器。主首页的课程和实验数量也由这次构建更新。

`npm run fixtures:llm` 使用锁定的 `js-tiktoken@1.0.21` 重算分词快照；`npm run check:fixtures:llm` 比对快照与编码器，`npm run test:llm` 检查数学与核验行为。网页不打包词表，只带四组示例。

正文使用 Markdown，构建解析器为 `marked@18.1.3`。两项依赖的许可证均为 MIT；分词快照附完整许可与 [来源说明](fixtures/NOTICE.md)。`package-lock.json` 锁定构建依赖，已生成页面无需安装这些包即可使用。

`npm run check:reading:llm` 另行检查字号记忆、手动续读、目录焦点、大图关闭、存储拒绝和最大字号的窄屏布局。位置仅保存在本机，表示读到的小节，不代表掌握程度。

浏览器检查使用 `python scripts/llm/check_browser.py`，需要 Python Playwright 和本机 Chrome。它会离线检查 375、768、1440 三档布局、实验操作、键盘、200% CSS 缩放、减少动态效果与禁脚本阅读；截图和报告存到忽略的 `tmp/llm-review/`。这不能代替真实屏幕阅读器和初学者测试。

电子书通过 `npm run export:books:llm` 生成，`npm run check:books:llm` 检查源文件指纹及实际成品结构。Python 依赖锁在 `scripts/llm/requirements-books.txt`；PDF 中文字体由本机 Chrome 嵌入，EPUB 图解为同源 PNG，正文使用阅读器字体。临时 HTML、EPUB 预览、抽页截图保存在忽略的 `tmp/llm-book-review/`；正式 PDF、EPUB 和指纹清单在 `deliverables/`。

陌生材料题目维护在 `review/tasks.json`，核对依据在 `review/rubric.json`，陪读流程在 `review/facilitator.md`。同一批题目生成网页、主书附录和 A4 练习纸；参考答案只进入陪读页与陪读 PDF。`review-record.json` 是生成的空白模板，没有自动判分。实际记录请另存到被 Git 忽略的 `local-feedback/`，填写匿名编号，保留首次答案、原话、提示和修改后的表现。

旧章的修订源为 `legacy-principles.md`，其中相对路径以组装后的 `book/book.md` 为基准；阅读请用生成的回查页。`npm run build:llm` 从同源稿生成旧章、回查页与电子书进阶附录，同时复用生成回环到旧图路径。36 个原标题和顺序保持不变，用于旧目录定位。原始混合输入快照在 `fixtures/legacy-tokenization.json`，由 `npm run fixtures:llm` 与四组课程快照一起重算。

本批新增[提示词工程回查](../../exports/llm/prompt-reference.html)、[RAG 架构回查](../../exports/llm/rag-reference.html)和[应用回查精选](../../exports/llm/applications-guide.html)。完整回查保留原章 42/10 个标题与顺序，修订任务模板、少样本/自检边界、检索刷新、分块评估和方案选择。电子书收录精选附录，未把整份合订书重复塞入十二课。

应用旧章的修订源为 `legacy-prompt.md`、`legacy-rag.md`、`legacy-context.md` 与 `legacy-agent.md`，链接同样以 `book/book.md` 为基准；标题契约记录在 `legacy-application-headings.json`。`scripts/llm/legacy-applications.mjs` 只组装对应章节，保留中间多模态等非目标章原文，生成完整回查及精选附录；变更源稿后需重新构建和导出书籍。

新增[上下文完整回查](../../exports/llm/context-reference.html)、[Agent 与工具调用完整回查](../../exports/llm/agent-reference.html)及[系统回查精选](../../exports/llm/execution-guide.html)。上下文、Agent 分别保留 36/43 个标题，与 `legacy-context.md`、`legacy-agent.md` 同源；本批增加 G14，旧图入口也换成对应的课程手绘，去掉无来源效果数字。

运行 `node book/llm/examples/tool-workflow.mjs` 可以从仓库根目录执行本地查价与乘法流程。商品与价格来自 `fixtures/tool-workflow.json`；源码只使用 Node 标准库，固定工作流没有接入模型、联网或下单。正文中的函数摘录和书末回执结果由同一源码生成，修改后重建再导出，不手工维护第二份代码或结果。

新增 [Transformer 完整回查](../../exports/llm/transformer-reference.html)与[结构精选](../../exports/llm/architecture-guide.html)，保留原章 28 个标题；修订源为 `legacy-transformer.md`，标题契约单独记录。G15 画出多头的独立投影、汇总、拼接与输出投影，L04 深入图也可查看。原始 encoder-decoder 与 decoder-only、post/pre-norm、位置外推和 IO 优化分别说明，未公开模型规模保持未知。

运行 `node book/llm/examples/multihead.mjs` 查看两个一维头的 Q/K/V、掩码、权重和输出；输入和投影来自 `fixtures/multihead.json`。章内与电子书中的数值表由这份代码实际生成；更改未来/可见输入及输出矩阵有相应测试。例子没有训练、位置编码、残差、归一化或 FFN，不当作完整 Transformer。

蒸馏专题已接入 [L05 训练与推理](../../exports/llm/training.html)：教师/学生、软标签、温度、KL 与 T²、响应/推理文本蒸馏和错误迁移，附可更新学生参数的本地实验与纸上计算。

十二课均补充具体算例、失败原因或工作情境；[知识点核对表](../../specs/llm-learning-redesign/KNOWLEDGE-MAP.md)记录主线、深入解释和旧章回查的范围。图解保持可编辑 SVG，按实际手机字号和电子书成品检查。
