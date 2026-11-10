# Cordis 组件实验与连续审查实例

这些原创示例直接加载 DeepSeek Harness 提交 `fcc0ad462172522aaf5c93a7b2e01f6b9f0b0159` 中的 Cordis TypeScript 源码。`review-observer.mjs` 用七项基础场景解释依赖、资源清理和 waterfall；`review-lab.mjs` 把同一套机制组合成文本审查服务，再用十三项场景检查正常调用和失败路径。它们不需要模型凭据。

运行环境需要 Node.js 24.9.0 或更新版本、npm、Python 3 和能访问 GitHub 的 `gh`。本次使用 Windows、Node.js 24.14.0、tsx 4.23.13。所有命令在书仓根目录执行：

```powershell
.\deepseek\examples\prepare-cordis.ps1
python deepseek/examples/verify-evidence.py --source-root .scratch/deepseek-runtime/pinned-cordis/src
node --import ./.scratch/deepseek-runtime/node_modules/tsx/dist/loader.mjs deepseek/examples/check-cordis.mjs --source .scratch/deepseek-runtime/pinned-cordis/src/index.ts
node --import ./.scratch/deepseek-runtime/node_modules/tsx/dist/loader.mjs deepseek/examples/check-review-lab.mjs --source .scratch/deepseek-runtime/pinned-cordis/src/index.ts --trace
```

准备脚本从 GitHub API 的 base64 字段还原九个源码文件的原始字节，校验摘要，再把精确版本依赖安装到 `.scratch/deepseek-runtime/`。安装禁用脚本，不改全局包。实际运行入口是下载源码的 `index.ts`，不是 npm 包的构建入口。本机执行策略禁止 `.ps1`，准备脚本只完成静态语法检查；两组实验使用已经取得且核对过 Git blob 身份的源码运行。

七项基础场景保留原有记录：必需依赖等待与激活、提供者替换、初始化失败清理、两层 waterfall 顺序、veto 与重复 next、父子异步卸载、服务域隔离。连续实例增加以下检查：

| 场景 | 关键观察 |
| --- | --- |
| 双服务依赖 | 只装日志服务时仍为 PENDING，工具服务出现后才 ACTIVE |
| 非法输入 | 业务主体尚未进入就拒绝，日志没有 tool:start |
| 策略拒绝 | veto 阻止主体，策略卸载后恢复调用 |
| 注册后初始化失败 | 工具条目和 note 监听一起撤销 |
| 活跃任务卸载 | 先取消任务，再等待人为延迟的 close |
| 提供者替换 | 旧工具表清空，同一插件挂载重新激活 |
| 同名冲突 | 第二次失败不能删除第一拥有者的工具 |
| 策略延迟后卸载 | 已进入中间件的调用也不能晚到旧插件主体 |
| 共享服务标签 | 同一个 realm symbol 有意共享日志 |
| once 递归触发 | 监听先撤销，所以只运行一次 |
| serial 返回值 | false 继续，0 截断 |
| parallel 失败 | 等全部监听完成后以 AggregateError 拒绝 |
| 死上下文注册 | 卸载后的 ctx.on 抛 INACTIVE_EFFECT |

两组实验都使用 Node 原生断言。只有退出码为 0 且汇总 `passed:true` 才算通过；初始化失败场景可能打印预期错误诊断。`--trace` 额外输出首个正常场景的七条业务事件，输入 `TODO\n校对` 得到两行、七个 code point、`todo:true`。

`createReviewLab(cordis)` 接收调用方的 Cordis 导出，返回 ReviewJournal、ReviewTools、reviewPlugin 和 policy。ReviewTools 是本书业务服务，并非官方 dsh-tools；ReviewJournal 仅在内存保存记录，并非 Session 存储。完整 dsh 宿主、Agent、模型、Web、持久化与平台沙箱没有参与这些实验。

## 本地包入口

`package.json` 只导出 `review-lab.mjs`，`private:true` 防止误发 npm。生成并解开本地包后，可让同一实验驱动加载包内代码：

```powershell
New-Item -ItemType Directory -Force .scratch/deepseek-pack | Out-Null
npm.cmd pack ./deepseek/examples --offline --ignore-scripts --cache .scratch/npm-cache --pack-destination .scratch/deepseek-pack
New-Item -ItemType Directory -Force .scratch/deepseek-package-check | Out-Null
tar -xzf .scratch/deepseek-pack/book-deepseek-review-lab-0.2.0.tgz -C .scratch/deepseek-package-check
node --import ./.scratch/deepseek-runtime/node_modules/tsx/dist/loader.mjs deepseek/examples/check-review-lab.mjs --source .scratch/deepseek-runtime/pinned-cordis/src/index.ts --lab .scratch/deepseek-package-check/package/review-lab.mjs
```

这项检查验证包内导出能被消费者加载，没有验证完整 dsh 的包管理器加载，也没有对外发布。包内只有 README.md、package.json、review-lab.mjs，不包含上游源码、测试驱动或临时数据。

历史七项记录在 [cordis-20261110.json](../facts/cordis-20261110.json)，连续实例记录在 [review-lab-20261110.json](../facts/review-lab-20261110.json)。摘要先去 UTF-8 BOM，统一 LF，并将末尾规范为一个 LF，再计算 SHA-256。上游代码采用 MIT 许可证；本书原创示例按仓库的 CC BY-NC-SA 4.0 许可证提供。
