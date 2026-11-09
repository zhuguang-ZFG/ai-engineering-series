# OpenCode 插件实验

基线：OpenCode v1.19.5 的 V1 Plugin/Hooks 接口。示例为本书原创。[第 8 章](../ch08.md)讲处理器，[第 9 章](../ch09.md)讲真实宿主，[验证记录](../VERIFY.md)记录实际运行范围。

## 离线运行

Node.js 22.19.0 或更新版；不需要 API key。回调使用 TypeScript 的纯类型 import，Node 的类型擦除执行不需要安装 OpenCode。

```bash
node --test opencode/examples/check-review-trace.mjs
```

实验调用真实示例，但 SDK client 是替身。它验证提示词追加、参数保持、日志内容、跨会话调用关联、缺失回调、日志失败、dispose 和共享 output 的教学语义。最后一项调度器是教学实现，不是完整宿主。

## 对照发布包类型

在仓库根安装隔离的类型检查依赖：

```bash
npm install --prefix .scratch/plugin-types --ignore-scripts --no-audit --no-fund @opencode-ai/plugin@1.19.5 typescript@5.9.3 @types/node@24
```

将 review-trace.ts 原样复制到该临时目录，再用其中的 TypeScript 对副本执行。Windows PowerShell 中安装命令使用 npm.cmd；复制命令如下：

```powershell
Copy-Item opencode/examples/review-trace.ts .scratch/plugin-types/review-trace.ts
```

```bash
node .scratch/plugin-types/node_modules/typescript/bin/tsc --noEmit --strict --skipLibCheck --target ES2022 --module ESNext --moduleResolution Bundler --types node --typeRoots .scratch/plugin-types/node_modules/@types .scratch/plugin-types/review-trace.ts
```

skipLibCheck 跳过依赖自身声明文件的内部检查，示例仍做严格类型检查。安装可能提示当前 Node 低于某个间接依赖的 engines；这里未导入上游运行时，不能用类型通过证明整个宿主兼容该 Node。

## Windows 真实宿主实验

需要 Python 3.10 或更新版、Git，以及上一步安装的真实依赖目录。脚本只使用 Python 标准库。以下命令均在书仓根目录的 PowerShell 执行。

先下载固定的 Windows x64 发布包并核对 SHA-256。下载需要网络，脚本本身不会替你安装或更新全局 CLI。

```powershell
New-Item -ItemType Directory -Force .scratch/opencode-bin | Out-Null
curl.exe --fail --location --output .scratch/opencode-bin/opencode-windows-x64.zip https://github.com/anomalyco/opencode/releases/download/v1.19.5/opencode-windows-x64.zip
if ($LASTEXITCODE -ne 0) { throw "OpenCode download failed" }
$opencodeZipHash = (Get-FileHash .scratch/opencode-bin/opencode-windows-x64.zip -Algorithm SHA256).Hash.ToLowerInvariant()
if ($opencodeZipHash -ne '09a6e693157f0887e504f2cf4357a8cbddc5ead5d0dffb9a269dcc47c48640f5') { throw "OpenCode ZIP checksum mismatch" }
Expand-Archive -LiteralPath .scratch/opencode-bin/opencode-windows-x64.zip -DestinationPath .scratch/opencode-bin -Force
$opencodeExeHash = (Get-FileHash .scratch/opencode-bin/opencode.exe -Algorithm SHA256).Hash.ToLowerInvariant()
if ($opencodeExeHash -ne 'd7b473388cb62555970e400ce54cdfb6d6573608beea6f8fdf382cd1a698a3fa') { throw "OpenCode executable checksum mismatch" }
```

ZIP 的摘要与官方 release asset 元数据核对过；exe 摘要来自该 ZIP 解压后的本地文件。来源、大小和摘要保存在[宿主实验记录](../facts/host-plugins-20261110.json)。

如果还没准备依赖，运行：

```powershell
npm.cmd install --prefix .scratch/plugin-types --ignore-scripts --no-audit --no-fund @opencode-ai/plugin@1.19.5 typescript@5.9.3 @types/node@24
if ($LASTEXITCODE -ne 0) { throw "Plugin dependency installation failed" }
python opencode/examples/check-host-plugins.py --binary .scratch/opencode-bin/opencode.exe --dependency-dir .scratch/plugin-types
```

不要用 Python 的 -O 模式运行：脚本通过 assert 检查结果。它核对 CLI 和插件依赖版本，将真实 package.json、package-lock.json 和 node_modules 复制进临时全局配置目录及项目 .opencode，再运行宿主。没有伪造依赖元数据，也没有把首次在线安装当成已测行为。

四项成功输出分别是：

```text
PASS discovery, real read, ordered hooks and disposal
PASS failed plugin isolation and cached module after reinitialization
PASS new process observes edited source
PASS --pure skips external plugins
```

每次运行都在 `.scratch/agent-series/host-plugins-*` 创建独立目录。脚本使用 OPENCODE_TEST_HOME、XDG 路径、独立数据库和临时目录，并通过 debug paths 检查它们确实落在实验目录内；个人账号、API key 和代理变量不传给宿主。两个 HTTP 服务仅绑定 127.0.0.1，OpenCode 服务使用临时随机密码。

模型替身返回 OpenAI-compatible SSE，让真正的内置 read 读取临时文件。外部模型没有参与；插件发现、调用、SDK 服务端日志和实例 dispose 使用官方二进制。默认插件、文件监听、模型列表拉取、更新和相关自动下载被关闭。这里没有做外网流量审计，也没有验证真实模型效果。

证据目录包含 `report.json`、`events.jsonl`、`model-requests.json` 以及 initial/restart/pure 三份服务端日志。宿主在 finally 中终止，本地模型服务也会关闭；实验文件保留供排错，均在 Git 忽略范围内。不要把原始请求和机器路径复制进公开记录，提交脱敏摘要即可。

尚未覆盖 TUI、自动热重载、异常退出清理、真实取消、权限拒绝/询问和 V2 运行时。`--pure` 只用于最后一项对照；正常的外部插件实验不能加这个参数。
