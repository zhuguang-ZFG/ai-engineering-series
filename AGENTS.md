# Repository Guidelines

本仓是“大模型与智能体工程”系列的统一项目。只在根目录维护一个 Git 仓库；`agent-books/` 与 `model-course/` 是普通子目录，不创建嵌套 `.git` 或子模块。进入子目录前，读取其中适用的 `AGENTS.md`。

## 源文件与职责

- `agent-books/`：Agent 书籍、提示词册、原有 Python 构建器与测试。Markdown 正文和 `yuyu-book/` 登记表是内容来源。
- `model-course/`：大模型五阶段三十章及 Vibe Coding 补充内容。主课文在 `book/llm/lessons/cNN.md`，先修关系与版本在 `book/llm/course.json` 的 `curriculum` 中。
- 根 `series.py`：统一命令入口；根 `index.html`：系列阅读入口；`docs/`：跨项目阅读路线与整合记录。
- `docs/integration/import-manifest.json`：导入来源与文件指纹；`legacy-main-snapshot.zip`：旧主工作区独有文件的历史快照。

各册保留独立版本。全系列目前以中文为主；修改《御舆》共有事实时同步维护 `agent-books/en/`。其他册没有英文稿时，不将中文完成状态写成双语完成。

## 检查与构建

以下命令从根目录执行：

```bash
python series.py list
python series.py check --project all --structure-only
python series.py check --project agent-books
python series.py check --project model-course
python series.py build --product prompt --lang zh --pdf --epub
python series.py build --product llm --lang zh --pdf --epub
python series.py collect
```

按修改范围执行对应检查。提交整合改动前运行 `python series.py check --project all`；结构检查不能代替内容、程序和成品检查。安装依赖与专项验证沿用两侧 README。根命令负责选择项目和传递参数，不另写一套内容判据。

不要直接修改 `dist/`、`agent-books/yuyu-book/dist/`、缓存及课程构建器生成的 `exports/`、`deliverables/`。修改源稿或生成器后重建；需要提交哪些成品，以对应项目规则为准。不要顺手清理其他作者的工作或回退已有改动。

## 编辑与证据

Python 使用四空格缩进、`snake_case` 命名；测试沿用所在项目的组织方式。中文正文用全角标点，中文与英文之间留半角空格，代码围栏注明语言。保留章节 H1、显式 block ID、现有链接与被登记的标题；Mermaid 换行用 `<br/>`。

阅读路线必须保留课程先修范围。提示词册与工具分册可供选读，不能据此宣称完成了 C01–C30 或 K1–K5。模型结果、程序检查、电子书版式和真人学习效果分别记录。测试通过不得改写为模型质量达标、跨平台通过或独立读者验收。

技术断言引用固定 tag 或完整 commit SHA，使用 HTTPS。记录实际环境、命令和失败；旧证据绑定原版本，不挪作新版本验证。禁止写入凭据、私有配置或未脱敏的服务响应。

## 提交与许可

沿用 Conventional Commits，例如 `docs(series):`、`feat(series):`、`fix(book):`。提交或 PR 说明列出改动范围、实际运行的验证及尚未完成的事项。不要声称远端 CI 已通过，除非已核对本次提交的运行结果。

保留两侧作者、来源、许可与限制，参见根 [LICENSES.md](LICENSES.md)。导入和统一排版不改变第三方内容的授权范围；不能为未明确授权的内容补写统一开源许可。
