# GitHub 书籍与教程参考研究

核对日期：2026-11-07。用途：为新版课程选择学习顺序、先修桥梁、项目组织及验收方式；不是推荐榜，也不是已复现全部代码的声明。本轮没有复制外部正文、插图、Notebook 或数据集。

## 1. 读取范围与采用决定

下列链接是本轮直接读取的上游材料。分支链接会变化，实施时若复制任何允许复用的材料，必须另记具体提交、文件、许可与修改范围；本表的访问日期不等于不可变版本。

| 编号 / 项目 | 本轮实际读取 | 有依据的结构观察 | 本项目采用 / 不采用 |
| --- | --- | --- | --- |
| R1 [动手学深度学习](https://github.com/d2l-ai/d2l-zh) | 仓库 README、[预备知识正文](https://github.com/d2l-ai/d2l-zh/blob/master/chapter_preliminaries/index.md)、[LICENSE](https://github.com/d2l-ai/d2l-zh/blob/master/LICENSE) | README 把概念、数学和可修改的代码放在一起；预备章先补数据操作、线代、微积分、自动微分、概率与查文档 | 采用“所需基础先补、公式对应代码、修改输入观察结果”；不搬入整套深度学习课程，不要求零基础先读完整数学附录 |
| R2 [Happy-LLM](https://github.com/datawhalechina/happy-llm) | README 的受众、学习方法、章节表及 [LICENSE.txt](https://github.com/datawhalechina/happy-llm/blob/main/LICENSE.txt) 中许可名称、授权与条件段；未逐章读完 | 从 NLP、Transformer、预训练语言模型、大模型基础，进入手搭模型、训练实践、评测/RAG/Agent；README 说明 Python 基础，并建议缺基础者先补环境与语法 | 采用“模型内部与应用都形成路线”；不以“零基础”掩盖编程前置，不把最新扩展目录全部列成本书必修 |
| R3 [LLM Universe](https://github.com/datawhalechina/llm-universe) | README 全部课程大纲、受众、环境及项目说明；未逐项复现 Notebook | 知识库项目串起 API、文档处理、向量库、RAG、部署与检索/生成分开评估；受众明确需要基础 Python；第二部分标为创作中 | 采用贯穿项目和分环节评估；补齐 Python/HTTP/JSON 桥梁；不照搬云平台、框架和供应商组合，不把上游计划当作完成内容 |
| R4 [Build a Large Language Model (From Scratch) 配套仓库](https://github.com/rasbt/LLMs-from-scratch) | README 的 Ch1–7、练习、先修与硬件说明；[LICENSE.txt](https://github.com/rasbt/LLMs-from-scratch/blob/main/LICENSE.txt) | 文本数据→注意力→GPT 结构→预训练→分类微调→指令微调；有练习与独立答案；要求扎实 Python，另补 PyTorch；仓库是商业书配套代码，不是开放全文 | 采用可运行部件逐层组装、先训练再微调的依赖；后段新增最小 decoder 与参数适配实验；不照抄书图，不把上游硬件说明当作本项目已测配置 |
| R5 [Hands-On Large Language Models 配套仓库](https://github.com/HandsOnLLM/Hands-On-Large-Language-Models) | README 的十二章、环境说明与 [LICENSE](https://github.com/HandsOnLLM/Hands-On-Large-Language-Models/blob/main/LICENSE)；未读商业书全文或逐章执行 | 先介绍模型、token/embedding、Transformer，再进入分类、聚类、提示、生成工具、语义搜索/RAG、多模态、embedding 训练与微调；建议 Colab 环境 | 采用“表示模型和生成模型用途有别”、多模态边界及图解配实操；不以图数量定义教学质量，不承诺外部免费 GPU 或平台持续可用 |

## 2. 许可证与素材边界

| 项目 | 实际核对到的声明 | 本轮及后续处理 |
| --- | --- | --- |
| R1 D2L 中文仓库 | 根 LICENSE 为 Apache License 2.0；本轮未完成逐文件、书籍出版文本及第三方图片的权利核对 | 只参考教学方法；不把英文版的许可声明直接套到中文版，也不把根许可当作全部第三方素材授权 |
| R2 Happy-LLM | LICENSE.txt 为 CC BY-NC-SA 4.0；README 同样声明署名、非商业、相同方式共享 | 不直接改编并混入可能商业发行的正文；若后续需使用，先审查 NC/SA 条件并取得适当授权，保留归属 |
| R3 LLM Universe | 本轮所读根目录与 README 未见明确许可证声明；这不是全仓无许可证的证明 | 仅引用结构与链接；复制代码、文案或图片前必须另查具体文件授权，未解决不得复制 |
| R4 LLMs-from-scratch | Apache 2.0 文本的 Source 定义明确排除与软件相关的书籍及图片，不能简单标成无限制 Apache 2.0 | 仅参考依赖顺序与练习方式；代码复用另核对条款与 NOTICE，商业书正文/图另需授权 |
| R5 Hands-On LLM | 仓库 LICENSE 为 Apache 2.0，README 明确为 O'Reilly 图书配套代码 | 不推定商业书全文和出版插图获得相同授权；本轮不复制素材，若复用代码则保留版权、许可与修改说明 |

以上是制作约束，不是法律意见。署名不自动解决授权；“在 GitHub 可见”不等于可以任意再出版。搜索结果与第三方聚合站的许可证标签不能替代原始条款。

## 3. 对本书的具体改变

| 原缺口 | 参考依据 | 新版落点 | 可检查结果 |
| --- | --- | --- | --- |
| 上来就进入抽象概念，缺一次完整任务 | R3 项目组织；本项目原 L07/L08/L12 | S1 / C01–C04 | 换材料完成证据报告，不先要求会代码或 KL |
| “零基础”与后续代码之间断层 | R1 预备知识；R2/R3/R4 明示 Python 前置 | C06/C07/C09 数学小桥；C11/C12 编程与请求小桥；C23 张量/自动微分 | 读者能手算小例子、修改程序输入、定位错误，不靠照抄运行截图 |
| 原理深入散在附录 | R2、R4 的部件依赖 | S2 / C05–C10，S4 / C23–C26 | 先解释、再计算、再组装最小 decoder；微调与蒸馏有实际参数变化和留出评测 |
| 预置演示替代真实开发 | R3 从 API 到部署；R5 实际模型 Notebook 的组织 | S3 / C13–C17 | 真实推理链路、真实文档、实际工具回执；无访问条件则阻塞实操验收而非填假结果 |
| 演示正常就算会了 | R3 检索/生成分别评估；R4 练习与答案分离 | C18–C22、C29/C30 | 留出集、失败定位、单变量改进、独立换题交付 |
| 专题越加越多，没有终点 | 各参考书均有明确范围，而非所有模型知识合订 | 五阶段三十章与五道阶段门 | 所有章节映射能力和任务；新技术进回查区，除非替换已有明确缺口 |

## 4. 证据限制

- 本轮研究覆盖仓库说明、公开目录、D2L 预备知识正文与上表许可段；不是对五套书籍全文的技术审校。
- 没有执行外部 Notebook、验证其依赖、取得收费模型访问或复现训练速度。不能引用上游宣传语作为本课程读者成效。
- 本书新目录、阶段门与通过条件是本项目的教学设计决定，不声称是参考作者提出或认可的统一方法。
- 具体 SDK/API、模型权重/数据许可、资源预算须在相应实现任务中查官方当前资料并实际验证，不从教学目录推断接口可用性。
