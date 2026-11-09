# 附录 B：配置与命令速查

<!-- block: deepseek-apxb.b-opening -->
这份速查只保留本册已经解释过的入口。运行命令之前先检查版本和当前工作目录，涉及完整应用的命令需要已安装并构建好的 dsh；它们不是本册组件实验的一部分。

## B.1 应用命令

```powershell
dsh --version
dsh --help
dsh --profile web --dump-config
dsh web --no-open
dsh --profile headless "读取 fixture.txt，报告首行，不修改文件"
dsh --profile sdk
dsh --profile sdk-minimal
dsh --profile acp
```

启动参数属于启动器还是应用，要看它出现的位置和选定 profile。不要把 Web 端口参数套到 headless，也不要把 SDK stdio 的输出当成人可读控制台文本。自动化包装器应保留 stderr、退出码与协议结束状态。

## B.2 插件编写要点

| 操作 | 入口 | 容易遗漏的条件 |
| --- | --- | --- |
| 声明必需服务 | inject | 名称与有效 realm 必须匹配 |
| 注册同步观察 | ctx.on + emit 事件 | emit 不等待 Promise |
| 环绕一次操作 | waterfall 的 next | 原样委派并返回，最多一次 |
| 管理外部资源 | ctx.effect | 创建中途失败也要清理 |
| 移除某次挂载 | fiber.dispose | 等待异步清理完成 |
| 观察启动失败 | fiber.await | 稳定 PENDING 不等于 ACTIVE |
| 服务解析隔离 | ctx.isolate | 不是进程或文件系统沙箱 |
| 注册模型工具 | ctx.tools.register | schema、规范值、呈现分开 |
| 添加提示词 | ctx.systemPrompt.section | 名称、排序、作用域和接纳 |

## B.3 配置排错顺序

先确认 profile 名称与 Harness home，再导出最终树，定位对应 row id。接着检查后层补丁是否替换了 config，插件是否只是被安装而未选中，服务是否进入正确隔离域。最后才分析模型行为。

package 安装成功、bundle 被选择、row 被启用、fiber ACTIVE 和功能实际发生，是五个不同阶段。任何一个界面只显示一个绿色标记时，都值得继续查它表达的究竟是哪一层。

在公开问题报告中保留版本、row id、错误码、脱敏配置片段和最小复现。不要贴完整 home 目录或请求日志；工具正文和代理地址可能含私有信息。用一个临时 fixture 复现同样问题，往往比分享真实项目更容易让别人定位。

## 固定版本来源

- [apps/cli/README.md](https://github.com/deepseek-ai/deepseek-harness/blob/fcc0ad462172522aaf5c93a7b2e01f6b9f0b0159/apps/cli/README.md)
- [packages/boot/plugin-manager/README.md](https://github.com/deepseek-ai/deepseek-harness/blob/fcc0ad462172522aaf5c93a7b2e01f6b9f0b0159/packages/boot/plugin-manager/README.md)
- [docs/cordis-primer.md](https://github.com/deepseek-ai/deepseek-harness/blob/fcc0ad462172522aaf5c93a7b2e01f6b9f0b0159/docs/cordis-primer.md)
