# 《提示词工程》随书练习包

版本 0.1.4，中文技术试读版。青禾工作坊及其通知、人物、规则均为原创虚构教学材料。脚本在本地运行，不连接模型服务，不执行真实报名或消息发送。

将压缩包解压到一个新目录，在含有 `prompt/`、`tests/` 的解压根目录打开终端。安装 Python 3.11 或更新版本，不需要第三方依赖；Windows 的 `python` 可换成 `py -3`。

先确认版本，然后运行业务参考检查：

```bash
python --version
python prompt/examples/check_workshop.py --mode reference
```

预期通过 12/12。要做独立修复练习：

```bash
python prompt/examples/exercise.py prepare --out .scratch/my-repair
python prompt/examples/exercise.py check --project .scratch/my-repair --receipt .scratch/my-before.json
```

原始故障副本应通过 8/12，检查退出码 1 是预期业务失败。只修改副本中的 `registration.py`；规则、用例与检查器保持冻结。每次复查换一个回执文件名。

本包内的两组工具测试可独立运行：

```bash
python -m unittest discover -s tests -p "test_prompt_*.py" -v
```

除章节另有目录说明外，操作命令从解压根目录执行。材料、提示、开发/验证/留出题、人工判据和离线证据分目录保存。运行模型练习时，只将单次导出的 `request.txt` 交给待测模型；不要让它读取含判据的整个练习包。

PDF、EPUB 和 HTML 为独立书籍文件。本包附有同版 Markdown 正文和六张 SVG 图稿，供搜索、复制与放大查看；指向其他工具册、系列规划或完整仓库脚本的链接需要完整书籍仓库，离线练习运行不依赖那些链接。完整源仓库为 <https://github.com/zhuguang-ZFG/ai-engineering-series>，本册源稿位于其中的 `agent-books/prompt/`。

`package-manifest.json` 记录包内源文件的 SHA-256，可用于检查文件变化。模型 A/B、跨模型迁移、独立读者试读仍未完成。手写样稿与单元测试 fixture 不作为模型成绩。
