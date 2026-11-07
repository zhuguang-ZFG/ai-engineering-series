# 架构决策记录

本文件对应平台计划 P8.4。以下记录描述当前实现的边界，不代替测试、受管验证或正式发布批准。源码路径相对于仓库根目录。

## ADR-001：证据定位使用稳定块 ID

**决定：** Markdown 保持唯一正文源，可引用块使用 `<!-- block: ch03.tool-generics -->` 这样的显式标记。登记表保存块 ID，不保存新行号。标记归属于具体语言的单元文件；一个 ID 只有在两语文件中都实际存在，才同时证明两语。

**原因：** 行号随正文插入而移动，维护者不应为一次解释性增补重写来源与术语证据。块存在与词形命中分别由 `blocks.validate_markers()`、`plain.validate_plain()` 校验。

**边界：** `yuyu_book/migrate.py` 负责离线转换历史行号与输出歧义报告；日常 `plain.validate_plain()` 只接受稳定块 ID，并拒绝围栏块充当散文证据。旧行号读取分支、`scripts/shift_anchors.py` 及其专属测试已退出。历史迁移脚本仍可读取旧登记表，但不再由构建器兼容旧语法。

## ADR-002：衍生阅读产品消费只读 BookModel

**决定：** reader、gallery、cards、sample、portal、静态索引及视频内容包通过 `yuyu_book/products/loader.py` 读取 Markdown 与登记表，使用 Edition、Unit、Section、Block、Term 和 Guide，不从 `dist` HTML 反向抓取正文。

**原因：** `dist` 是输出，不是内容 API。产品不应要求先排完整本书，才能生成入门页或一张卡片。

**边界：** 大书的 `app.build_edition()` 目前仍使用 `units.load_unit()` 与登记表装配；不能因此宣称所有产品已经走同一个 BookModel 入口。EPUB 是经过审计的 HTML 的格式后处理，不是第二套正文解析器。

## ADR-003：PDF 只通过 PrintManifest 接收结构元数据

**决定：** `app.pdf_meta()` 生成 `PrintManifest`，使用冻结的 OutlineEntry、IndexRow 与有序目标列表。`pdf.py` 独立负责 Chromium 打印、页码测量、目录盖章、书签和字体子集化。

**原因：** 错误目录目标应在启动浏览器之前报错。目录顺序、索引行与目标锚点必须一一对应，不能靠模糊搜索正文猜页码。

**边界：** HTML 屏幕阅读不依赖打印页码；PDF 分页依赖浏览器与字体。README 的 CI/Noto 页数不能用 Windows/微软雅黑产物冒充。成品仍须经过页码漂移与空白家具页检查。

## ADR-004：书籍无脚本，站点渐进增强

**决定：** 整书 HTML 保持单文件、无 JavaScript、无外部运行时资源。站点可以使用阅读进度、回读位置和重播等增强，但导航、正文与图注必须在禁用脚本时可用。

**原因：** 文件下载、离线阅读和打印是产品契约，不以用户登录、网络或脚本执行为前提。

**边界：** `audit.py` 负责整书输出契约；站点由产品适配器、`tests/test_site_accessibility.py` 与真实浏览器检查覆盖。静态搜索与语言映射的 JSON 存在不等于浏览器已经验证搜索或跳转行为。

## ADR-005：视频源、派生物与媒体验证分开

**决定：** `video/chapters/chNN/` 保存 episode、scene、脚本、内容包和兼容审阅清单；`video/pipeline/` 负责内容装配与检查，HyperFrames 版本集中在 `video/package.json`。可重建中间物写入 `video/.build/`，不加入 Git。

**原因：** 章节复制脚本会造成依赖漂移；将字幕或音频切片当源文件又会掩盖可重建性。独立进程重新读取输入并比较输出字节，才是确定性重建证据。

**边界：** `check --config-only` 只证明配置；`prove --config-only` 只证明源产品独立重建；`check --audio` 必须读取真实音频。它们不能替代逐帧、音画同步、听感或人工发布审阅。未经相应检查的媒体保持未验证，不能用静音、假音频或放宽门槛补一个绿色状态。

## 发布与审查

`bookctl` 是仓级入口，底层通过 `python -m yuyu_book` 运行。Fast、Full、Bootstrap、Omp 与 Release 的配置及执行结果分别核对，不能以配置存在代替远端成功。`build-report.json`、`artifact-manifest.json` 与 SHA-256 记录具体成品及环境；脏树产物不能冒称只由 HEAD 提交重建。

测试、runner 和策略变更需要独立审阅。`task_verify` 无配置或无基线时保持 **unverified**，手工命令通过不改变这个状态。
