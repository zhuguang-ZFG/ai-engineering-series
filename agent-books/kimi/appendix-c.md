# 附录 C：实验记录与复现边界

<!-- block: kimi-apxc.b-opening -->
实验记录区分原创样例、上游组件和真实 CLI；每种结果只证明它实际覆盖的范围。

## C.1 已完成的检查

| 层次 | 实际操作 | 结果记录 |
| --- | --- | --- |
| 业务案例 | 错误与参考实现执行同一组 8 个输入 | `examples/check_inventory.py` |
| 原创组件 | Hook 子进程、MCP stdio 往返与库存性质检查 | `examples/test_workshop.py` |
| 上游组件 | 编译固定解析器和 Hook 执行器，运行 12 个场景 | `facts/source-probes.json` |
| 发布 CLI | 2.5.2 参数核对、ACP initialize、未知方法错误 | `facts/cli-2.5.2.json` |

上游组件实验读取原始 TypeScript 文件，由 esbuild 编译后调用，没有用手写解析器替代。Hook 实验使用本地进程适配器启动子进程，验证执行器对结果的解释。

本机组件探针运行于 Node `24.14.0`，编译器为 esbuild `0.28.2`。上游完整工程要求 Node 至少 `24.15.0`，因此本结果仅代表这几个选定组件的独立实验，不作为完整工程受支持环境的证明。

## C.2 重跑源码组件实验

先把固定源码放在忽略的实验目录中。可从上游仓库检出完整提交，再准备独立依赖目录：

```powershell
npm.cmd install --prefix .scratch/kimi-deps --ignore-scripts --no-audit --no-fund `
    esbuild@0.28.2 zod@4.3.6 js-yaml@4.1.1 smol-toml@1.6.1
node kimi/examples/verify_source.mjs .scratch/kimi-source .scratch/kimi-deps `
    .scratch/kimi-source-result.json
```

命令中的 `.scratch/kimi-source` 必须是固定源码根目录。探针先检查三个被测模块的 SHA-256，再编译和运行。它不会修改原始模块；临时编译文件在完成后清理。

一次通过不覆盖整个依赖图的所有行为。升级时应重新检出明确提交，核对依赖和输入，再更新基线，不能为了让探针通过而直接删掉摘要检查。

## C.3 尚未实跑的部分

完整模型审查、TUI 插件安装与重载、模型经 MCP 查询规则、真实 IDE 的 ACP 会话与反向调用，以及跨平台完整宿主行为，本次没有计入已通过结果。对应章节提供了操作和观察方法。

本机没有用用户现有模型凭据完成书中任务，也没有导入或导出用户真实会话。协议探针使用独立临时数据目录，未发送模型请求。

## C.4 结果怎样进入正文

“解析成功”仅说明文件符合解析契约；“Hook 执行器阻断”说明结果解释为 block；“ACP 声明支持 loadSession”说明握手返回该能力。它们分别不能代替完整插件加载、系统沙箱和会话恢复实跑。

后续补做某项实验时，应保存输入版本、命令、实际结果与范围，再修改正文中的状态。这样读者能够知道一个结论来自源码、组件还是完整宿主。
