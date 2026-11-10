# 离线练习：青禾工作坊报名助手

要求 Python 3.11 或更新版本，无第三方依赖。命令均从仓库根目录执行；终端里的 `python` 应指向你安装的 Python。Windows 可用 `py -3` 代替。先运行 `python --version` 确认。

这些命令只读取教学材料、计算结果和写本地练习文件。输入活动是虚构的，没有真实报名服务。将自己的练习输出放在 `.scratch/`，不要覆盖材料和证据文件。

## 看一次满额申请

打开 [full-request.json](full-request.json)：容量为 2，正式名单已经有 Q01、Q02，Q03 想加入。`confirmed` 是正式名单，`waiting` 是按顺序保存的候补名单。

```bash
python prompt/examples/workshop.py prompt/examples/full-request.json --mode faulty
python prompt/examples/workshop.py prompt/examples/full-request.json --mode reference
```

故障版本把 Q03 加入正式名单，参考版本把 Q03 放入候补。这两个命令本身都能正常执行；结果是否符合业务，要用另一个检查入口判断：

```bash
python prompt/examples/check_workshop.py --mode faulty --output .scratch/prompt-business-faulty.json
python prompt/examples/check_workshop.py --mode reference --output .scratch/prompt-business-reference.json
```

前者预期通过 8/12，退出码为 1；后者预期通过 12/12，退出码为 0。退出码是程序告诉终端的完成状态，检查命令的 1 表示发现业务不符合，不是安装失败。完整输入与独立预期在[业务用例](../evaluation/business-cases.json)，规则在 [R01-v1](../materials/rules-v1.md)。预期直接依据规则编写，没有调用参考实现生成。

`workshop.py` 故意保留 faulty 模式供审查练习，reference 模式展示本地业务范围内的修正。若要练修复，可复制脚本再改；不要让修复任务把所有模式直接改成 reference 后就宣称找到原因。没有真实身份、并发或持久化功能，不能作为上线报名系统。

## 导出实际输入

```bash
python prompt/examples/lab.py context D02 --mode full --out .scratch/prompt-context-full
python prompt/examples/lab.py context D02 --mode selected --out .scratch/prompt-context-selected
python prompt/examples/lab.py context D02 --mode summary --out .scratch/prompt-context-summary
```

每个目录有 `request.txt` 和 `context.json`。前者是需要完整复制给待测模型的文字；后者保存实际提供的来源、未选来源、原文指纹和字符数。输出目录已存在时命令拒绝覆盖，复做时换一个新目录名。

模式 `selected` 和 `summary` 目前只为 D02 编写。其他题默认使用 full。开发、验证、留出题分别通过 `--split development`、`--split validation`、`--split holdout` 选择；默认 development，不会把留出题自动混入。

## 检查一份输出

在对应目录中新建 `response.txt`，原样保存模型响应。打开 `request.txt` 可以看到四个字段的输出约定。不要为让检查通过先删除围栏、补字段或修引文。

```bash
python prompt/examples/lab.py check .scratch/prompt-context-full/context.json .scratch/prompt-context-full/response.txt
```

`mechanical_ok: true` 只说明字段与类型符合要求、引文确实在提供的材料中、动作数组为空。**它不等于回答正确。** 比如回答写“收费 500 元”，引文却逐字引用“活动免费”，仍然需要人发现语义冲突。检查命令始终返回 `manual_review_required: true`。

## 准备与登记对照

以下命令只准备输入，不调用模型。真实运行前将 `--environment` 换成实际产品与版本、模型标识、可控制的采样参数、输出上限、工具开关；不支持的参数写明不可设置。若已经开始运行，不修改冻结环境描述，另建实验。

```bash
python prompt/examples/lab.py prepare --repeats 2 --environment "offline preparation only; model not selected" --out .scratch/prompt-comparison-practice
python prompt/examples/lab.py compare .scratch/prompt-comparison-practice
```

默认验证集 7 题，每题 A、B 各 2 次，共准备 28 份输入。`plan.json` 固定题目、顺序、重复次数、环境说明和文件指纹，`criteria.json` 是冻结的人工判据，只给评审者。每个运行目录名如 `V01-01-a`，表示 V01、第 1 次、A 版。

运行时为每个目录开干净会话，只提供该目录的 `request.txt`，保存原始输出为 `response.txt`。按同一判据审阅，然后登记。例如，下列命令是**语法示例**，只有实际发生了服务错误才登记 error：

```bash
python prompt/examples/lab.py review .scratch/prompt-comparison-practice V01-01-a --outcome error --note "记录实际错误信息与发生时间"
python prompt/examples/lab.py compare .scratch/prompt-comparison-practice
```

有效评审为 pass、fail 或 error，均必须附具体依据。pass 要先通过机械检查；fail 保留原始响应；没有响应的服务故障可记 error 并附错误信息。缺评、重复评审、响应被修改和输入版本变化会被发现。此工具统计操作者提交的记录，无法证明响应出自哪个模型，也无法替人判断语义。

不要把尚未运行的项目记为 error。尚未运行保持 missing；只要有 missing，汇总就保持 `complete: false`，不计算两版通过数之差。详细解释见[第 16 章](../ch16.md)。

## 检验工具本身

```bash
python -m unittest discover -s tests -p "test_prompt_*.py" -v
```

测试覆盖业务边界、不改变输入、材料选择、答案隔离、格式错误、伪引文、配对遗漏、重复行和记录修改。单元测试中的合成输出只验证程序行为，不作为模型成绩。

## 独立审查与修复

`workshop.py` 同时提供故障版与参考版，适合观察规则；想独立练修复时，生成一份不带参考实现的副本：

```bash
python prompt/examples/exercise.py prepare --out .scratch/prompt-repair
python prompt/examples/exercise.py check --project .scratch/prompt-repair --receipt .scratch/prompt-before.json
```

副本里的 `registration.py` 是唯一待修改文件。`check.py`、`cases.json`、`rules.md` 与 `exercise-lock.json` 保留原样。初始通过 8/12，修复后使用新的回执名复查：

```bash
python prompt/examples/exercise.py check --project .scratch/prompt-repair --receipt .scratch/prompt-after.json
```

包装器真实启动子进程并保存输出、退出码、候选指纹与耗时；支持 `--timeout` 指定等待秒数，默认 10。已有目录和回执会拒绝覆盖。副本也能独立执行 `python check.py`，但该命令不保存完整外层回执。

这套工具用于可信的本地练习代码，不提供恶意代码沙箱。实测包括故障版 8/12、人工修正 12/12，以及缺项目、语法错误和超时，见[独立练习记录](../evidence/exercise-verification.json)。这些都没有模型参与。具体审查和交付方法见[第 10 章](../ch10.md)与[第 11 章](../ch11.md)。
