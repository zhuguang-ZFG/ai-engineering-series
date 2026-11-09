# Cordis 组件实验

这里的两个 JavaScript 文件是本书原创示例。它们直接加载 DeepSeek Harness 固定提交 `fcc0ad462172522aaf5c93a7b2e01f6b9f0b0159` 中的 Cordis TypeScript 源码，检查插件生命周期与事件协议。没有使用教学调度器代替 Cordis，也没有启动完整 dsh 应用。

需要 Node.js 24.9.0 或更新版本、npm、Python 3 和可访问 GitHub 的 `gh`。本次环境是 Windows、Node.js 24.14.0、tsx 4.23.13。准备与运行命令都在书仓根目录执行：

```powershell
.\deepseek\examples\prepare-cordis.ps1
node --import ./.scratch/deepseek-runtime/node_modules/tsx/dist/loader.mjs deepseek/examples/check-cordis.mjs --source .scratch/deepseek-runtime/pinned-cordis/src/index.ts
```

准备脚本下载固定提交的 9 个 `vendor/cordis/src/*.ts` 文件，从 GitHub API 的 base64 字段还原原始字节，避免控制台编码损坏非 ASCII 字符；校验事实文件中的摘要后，再把精确版本依赖装入忽略目录 `.scratch/deepseek-runtime/`。npm 安装禁用脚本，不改全局包。实际执行入口是下载源码的 `index.ts`；npm 中的 Cordis 包用于准备依赖，并未替代该入口。

如果已有固定源码，可以跳过下载，单独校验并运行：

```powershell
python deepseek/examples/verify-evidence.py --source-root .scratch/deepseek-runtime/pinned-cordis/src
node --import ./.scratch/deepseek-runtime/node_modules/tsx/dist/loader.mjs deepseek/examples/check-cordis.mjs --source .scratch/deepseek-runtime/pinned-cordis/src/index.ts
```

`review-observer.mjs` 导出依赖 `bookCounter` 的观察插件及环绕中间件。`check-cordis.mjs` 使用 Node 原生断言执行七个场景：

1. 缺依赖时停在 PENDING，服务出现后激活，卸载后不再接收事件。
2. 移除提供者使依赖者停用，新提供者触发重新激活。
3. 初始化失败清理受管资源，未经管理的外部写入保留。
4. 两层 waterfall 依次进入、逆序返回，并保留结果。
5. veto 不执行主体，同一层第二次调用 next 抛错。
6. 父插件清理等待异步子清理，重复 dispose 不重复效果。
7. 两个服务隔离域各自持有计数器。

全部断言通过时，进程退出码为 0，输出七行 `PASS` 和一行 JSON 汇总。失败会直接抛断言错误，不能把“打印了几行日志”当作通过。初始化失败场景可能打印预期的错误诊断，判断以断言和退出码为准。

本次结果与源码、示例摘要保存在 [cordis-20261110.json](../facts/cordis-20261110.json)。文本摘要去掉 UTF-8 BOM、统一 LF，并把结尾规范为一个 LF 后计算 SHA-256，以消除 PowerShell 写入格式差异。上游代码采用 MIT 许可证；准备目录不会提交到书仓。

这组实验没有调用模型、没有创建 Harness Agent、没有连接 Session 存储，也没有验证 Web 重连或操作系统沙箱。完整宿主的练习路径见第 17 章与附录 C。
