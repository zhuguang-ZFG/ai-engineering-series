# 本地发布、校验与回退

这里为 [C29](../../lessons/c29.md) 和 [C30](../../lessons/c30.md) 提供可运行的交付工具。`check_package.py` 核对声明的文件；`release_store.py` 进一步要求目录内所有文件均被登记，制作独立版本目录，并通过原子替换 `current.json` 选择版本。它不执行清单里的命令，也不自动启动服务。

## 从明确的交付目录构建

先准备 `payload/`，只放这次需要交付的源码、授权资料、依赖锁定文件和说明：

```text
payload/
  requirements.lock
  runbook.md
  user-guide.md
  app/
    assistant.py
    documents.json
    docs/...
```

`requirements.lock`、`runbook.md`、`user-guide.md` 必须存在。模型权重、虚拟环境、输出、缓存、密钥与个人资料留在包外；不要把整个工作目录当成 payload。工具会复制其中全部普通文件，拒绝链接。运行时使用 `python -B`，并把结果写到包外，避免 `__pycache__` 或报告改变发布目录。

在仓库根目录运行（下例各为一行，可用于 PowerShell）：

```text
python book/llm/examples/delivery/release_store.py build --payload payload --store local-store --release trial-a --created 2026-11-09 --scope "local teaching trial" --start "python -B app/assistant.py serve: see runbook.md" --health "GET /health followed by a documented readiness query"
python book/llm/examples/delivery/check_package.py local-store/releases/trial-a
python book/llm/examples/delivery/release_store.py select --store local-store --release trial-a
python book/llm/examples/delivery/release_store.py current --store local-store
```

`build` 不覆盖已有版本；先在临时目录复制、计算每个文件的 SHA-256 并检查，再发布目录。`select` 先检查完整清单及所有哈希，成功才写当前指针；失败会保留原指针。`current` 再次验证文件与选中时的清单哈希，输出启动应使用的目录。调用者检查退出码后，按 runbook 手动启动。

## 锁定环境

[`requirements-windows-cpu.lock`](requirements-windows-cpu.lock) 固定 **Windows x64、CPython 3.13、CPU** 的 38 个运行包及各自 wheel 哈希，包含助手、微型 decoder 与 OCR 的基础依赖。它不是其他系统的通用锁文件。模型目录须另记仓库、revision、文件哈希及许可，不包含在 pip 锁中。

在可联网的同平台机器下载，再在不继承系统包的新虚拟环境中离线安装：

```text
python -m pip download --only-binary=:all: --require-hashes --dest wheelhouse --extra-index-url https://download.pytorch.org/whl/cpu -r book/llm/examples/delivery/requirements-windows-cpu.lock
python -m venv .venv-clean
.venv-clean/Scripts/python.exe -m pip install --no-index --find-links wheelhouse --require-hashes -r book/llm/examples/delivery/requirements-windows-cpu.lock
.venv-clean/Scripts/python.exe -m pip check
```

创建环境前核对 `python --version` 是 3.13；不要加 `--system-site-packages`。安装成功后还要执行真实查询，`pip check` 和 HTTP 健康检查均不能证明模型或引用质量达标。其他平台应单独冻结和重建，不通过去掉哈希来强装。

## 真实切换与回退

1. 保留旧版本 `trial-a`、旧依赖环境和模型/资料指纹。
2. 用新的 payload 构建 `trial-b`。记录首次健康检查、就绪查询和故障响应。
3. 停止当前服务，`select --release trial-b`，核对 `current`，从返回目录启动。
4. 若就绪检查失败，保留报告；停止新进程，`select --release trial-a`，核对 `current`，使用旧环境重启。
5. 重做同一组健康、查询与失败用例，按实际结果填写“已恢复 / 仍失败”。指针切回不等于服务已恢复。

这套工具适用于单人操作的本地教学目录；不提供并发发布锁、进程管理、远程认证或无停机部署。哈希用于发现文件变化，不认证发布者；拥有目录写权限的人可以同时修改代码与清单。发布期间停止其他写入，启动前复查，仍不能消除校验后文件被并发改写的风险。

课程内置资料与作者烟测不能充当 K5 的陌生题材项目或他人独立复做。必须另交冻结问题集、授权材料、真实模型/图片记录、失败与回退证据。
