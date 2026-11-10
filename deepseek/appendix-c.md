# 附录 C：实验复现与未验证项

<!-- block: deepseek-apxc.b-opening -->
本册在固定提交内的 Cordis 源码上运行了两组实验：七项基础场景与十三项连续实例场景，合计二十项。模型、完整 dsh Web 应用、远端审批和平台沙箱没有参与。复现脚本与结果摘要分别在 examples 和 facts，正文中的成功表述只对应这些已运行场景。

## C.1 准备环境

需要 Node.js 24.9.0 或更新版本、npm、Python 和能访问 GitHub 的 gh。依赖装在书仓忽略目录，安装命令禁用脚本，不改全局包。准备脚本下载固定提交的 vendor/cordis/src，并校验来源摘要后安装精确版本依赖。

```powershell
.\deepseek\examples\prepare-cordis.ps1
node --import ./.scratch/deepseek-runtime/node_modules/tsx/dist/loader.mjs deepseek/examples/check-cordis.mjs --source .scratch/deepseek-runtime/pinned-cordis/src/index.ts
```

实际导入的是 pinned-cordis/src/index.ts，npm 发布包提供依赖准备与对照，不把发布包源码偷换成固定提交。TypeScript 由 tsx 转译运行。原始下载可能带 BOM 或 Windows 换行，事实文件的源码摘要采用去 BOM、统一 LF、结尾规范为一个 LF 的文本形式，便于跨平台比较。

## C.2 七项基础场景

| 场景 | 断言 |
| --- | --- |
| 缺依赖再提供 | PENDING 时无主体效果，服务出现后 ACTIVE |
| 移除并替换提供者 | 依赖者清理并等待，新服务触发重新初始化 |
| 初始化抛错 | 受管 effect 和监听被回收，不受管记录保留 |
| 两层 waterfall | A-before、B-before、body、B-after、A-after，结果保留 |
| veto 与重复 next | veto 不执行主体，第二次 next 抛错 |
| 父子异步清理 | 父 dispose 返回前子资源已关闭，重复清理不重复效果 |
| 两个服务 realm | 计数器各自从 1 开始 |

上述实验有明确的失败断言：移除 next 委派、删掉 effect disposer、让计数服务变成全局变量，都应让相应检查失败。这样测试检查的是可观察契约，而不是只证明示例函数被调用过。

## C.3 十三项连续实例场景

review-lab 把工具表、日志、策略和拥有资源的审查插件放在一起。第 17 章逐步跟读代码，examples/README.md 给出两组实验与本地包的完整命令。

| 路径 | 实际断言 |
| --- | --- |
| 双服务依赖与正常调用 | 两种服务都到齐才激活；输入 TODO、换行及“校对”得到两行、七个字符 |
| 输入校验与策略拒绝 | 两项场景分别确认业务主体未进入；撤销策略后恢复调用 |
| 初始化失败与同名冲突 | 两项场景确认只撤销自己取得的注册，不伤及已有工具 |
| 活跃任务与延迟策略 | 两项场景分别确认取消后等待 close，以及晚到的 next 不进入已卸载主体 |
| 提供者替换 | 同一个插件挂载重新激活，旧工具表已清理 |
| 共享 realm 标签 | 同一个 symbol 对应同一份日志服务 |
| once、serial、parallel | 三项场景分别确认递归只运行一次、false 与 0 的区别、聚合失败等待全部监听 |
| 卸载后注册 | 已停用上下文拒绝新受管监听 |

这组十三项在源码目录和本地 tarball 解包入口各运行一遍。两遍使用同一套断言，算十三种行为，不算二十六种。包入口实验只证明打包文件可运行，不证明完整 dsh 包管理器已经接入。

## C.4 证据范围

| 项目 | 当前证据 |
| --- | --- |
| Cordis 生命周期与事件协议 | 固定源码 + 本机二十项组件场景 |
| 审查服务本地打包 | tarball 文件白名单 + 解包入口十三项场景 |
| Agent/Session/工具/提示词机制 | 固定版本源码和官方契约阅读 |
| 全量 dsh 安装与 Web 启动 | 未实跑 |
| 模型提供者、费用与质量 | 未实跑 |
| 存储崩溃恢复与迁移 | 未实跑 |
| Web 断线重连、SDK/ACP 端到端 | 未实跑 |
| Linux/Windows 操作系统沙箱 | 未实跑 |
| npm 对外发布与完整插件升级 | 未执行 |

“未实跑”不使相应机制无法解释，但要求措辞停留在契约和复现步骤。不能把源码里存在一个方法写成已经在用户平台成功使用。日后补实验时保留日期、版本和命令，新增事实记录，不覆盖历史来制造从一开始就验证过的印象。

## C.5 扩展验证时的最小矩阵

下一步先用本地模型替身接完整 SDK profile，验证一个只读工具，再接 Session 存储，最后才加真实模型与浏览器。每步都留一个正常与一个失败场景。路径隔离、凭据隔离和子进程清理是实验驱动本身的责任，不应依赖模型听话。

对运行环境有要求的测试应失败或明确跳过，不能悄悄换成教学调度器。教学调度器适合解释概念，但它不是官方宿主，证据层级必须保留。

## 固定版本来源

- [vendor/cordis/src/fiber.ts](https://github.com/deepseek-ai/deepseek-harness/blob/fcc0ad462172522aaf5c93a7b2e01f6b9f0b0159/vendor/cordis/src/fiber.ts)
- [vendor/cordis/src/events.ts](https://github.com/deepseek-ai/deepseek-harness/blob/fcc0ad462172522aaf5c93a7b2e01f6b9f0b0159/vendor/cordis/src/events.ts)
- [vendor/cordis/src/context.ts](https://github.com/deepseek-ai/deepseek-harness/blob/fcc0ad462172522aaf5c93a7b2e01f6b9f0b0159/vendor/cordis/src/context.ts)
