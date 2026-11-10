# 提示词工程分册验证记录

当前中文技术试读版为 **0.1.1（2026-11-11）**。本轮加入第 7、8、16 章的三张原创解释图，调整相邻文字，并重新构建 HTML、PDF、EPUB 与独立练习 ZIP。新结果见 [0.1.1 成品记录](evidence/release-0.1.1.json)；下面的 0.1.0 记录保留为历史，不能用来证明当前文件已经通过检查。两轮均未调用模型服务。

## 0.1.1 本轮成品检查

| 对象 | 实际结果 | 范围 |
| --- | --- | --- |
| HTML | 1280 与 390 像素、浅色与深色共四种场景，无全页横向溢出、失效内部锚点或外部运行资源请求 | 三图文字、背景和颜色完整；窄屏细字仍需浏览器放大阅读，不把无溢出等同于手机字号验收 |
| PDF | 109 页、29 个书签；全文件未发现空白页、替换字符或超出页面的文本 | 三张新图在第 39、46、84 页，图内文字均留在同页；逐张查看截图无截断，另抽看封面和末页索引 |
| EPUB | EPUBCheck 5.4.0：0 个致命错误、0 个错误、0 个警告；6 张图均有替代文字 | [本轮报告](evidence/epubcheck-0.1.1.json)；尚未在多个实体阅读器上试读 |
| 独立练习包 | 从验证用 ZIP 解压后运行 31 项测试，全部通过；最终包另核对文件清单与 SHA-256 | 包含三张 SVG、书稿、材料、代码、测试和本轮证据；没有模型调用 |

成品记录保存本轮 HTML、PDF、EPUB 和 EPUBCheck 报告的指纹。为避免循环引用，它不保存包含自身的最终 ZIP 哈希；ZIP 内的 `package-manifest.json` 单独核对包内文件。截图和逐项浏览器记录来自本机 Edge，不表示已完成独立读者或辅助技术验收。

## 0.1.0 历史检查

以下结果对应 2026-11-10 的中文技术试读版 0.1.0。当时已完成前言、十八章和附录 A–D，提供 HTML、PDF、EPUB 与独立练习 ZIP。

| 对象 | 实际结果 | 记录 |
| --- | --- | --- |
| 仓库完整检查 | 8 步通过；通用测试 259 项，构建器测试 573 项；当时检查 426 个 Markdown 文件和 436 个 Mermaid 图，无错误 | [机器报告](evidence/repository-check-full.json) |
| 独立练习工具 | 两组共 31 项测试通过；故障版 8/12，人工修复后 12/12；缺项目、语法错误与超时各有真实回执 | [修复练习记录](evidence/exercise-verification.json) |
| 最终 PDF | 107 页、29 个书签；未发现空白页、替换字符或文字超出页面 | [排版报告](evidence/layout-final.json) |
| HTML | 390 像素浅色、1280 像素深色、665 像素打印模式均无横向溢出、失效内部锚点或索引重叠；代码最低对比度分别为 6.07、6.80、6.12 | [排版报告](evidence/layout-final.json) |
| EPUB | EPUBCheck 5.4.0：0 个致命错误、0 个错误、0 个警告 | [校验报告](evidence/epubcheck-final.json) |

最终调整索引打印分页及来源条目后，另跑产品、封面和示例页面相关测试 30 项，全部通过，并重新构建三种书籍文件。人工抽看 PDF 第 1、56、60、68、77、107 页，确认索引标题与条目同页；这不等于逐页人工校对。

全稿按 humanizer-zh 的编辑约束审读，修改空泛铺垫、重复总结和无用对比；核对跨章说明、业务规则、授权范围与未测状态。保留代码、判据、引文和实测数字，不用检测器分数评价文风。

## 复做命令

使用 Python 3.11 或更新版本。练习只依赖标准库，解压后的随书包可运行：

```bash
python -m unittest discover -s tests -p "test_prompt_*.py" -v
python prompt/examples/check_workshop.py --mode reference
python prompt/examples/exercise.py prepare --out .scratch/prompt-repair
python prompt/examples/exercise.py check --project .scratch/prompt-repair --receipt .scratch/prompt-before.json
```

参考版预期 12/12；故障副本预期 8/12，最后一条命令退出码 1 表示教学用业务失败。每次使用新目录和新回执名，避免覆盖已有练习。

安装完整仓库的构建依赖后，在仓库根目录运行：

```bash
python scripts/bookctl.py check --fast
python scripts/bookctl.py build --product prompt --lang zh --pdf --epub
python scripts/package_prompt.py --output yuyu-book/dist/yuyu-prompt-zh-examples.zip
java -jar /path/to/epubcheck.jar yuyu-book/dist/yuyu-prompt-zh.epub
```

`bookctl check --fast` 是 `make check` 使用的入口。PDF 构建需要本地浏览器与中文字体。本次环境为 Windows、Python 3.13.14；EPUBCheck 使用 Java 17。校验时使用与最终 EPUB 字节一致的临时副本。

## 尚未验证的范围

新册的模型 A/B、跨模型迁移、实际宿主权限组合、独立读者试读和学习效果验收尚未完成。28 份模型请求只是已准备的输入。第 16 章引用 DMX 的固定版本实验，未在本轮复跑；单元测试中的人工响应也不计作模型成绩。

工具处理可信教学代码，不提供恶意代码隔离。业务检查只覆盖公开定义的 12 个用例，不覆盖真实身份、并发、持久化或通知发送。英文版尚未编写。

0.1.0 的源文件指纹见 [provenance-release.json](evidence/provenance-release.json)，历史书籍和 ZIP 哈希见 [2026-11-10 交付记录](../docs/series/prompt-publication-20261110.json)。0.1.1 的源文件与书籍指纹见 [本轮成品记录](evidence/release-0.1.1.json)；当前练习 ZIP 内的 `package-manifest.json` 对包内源文件另列哈希。
