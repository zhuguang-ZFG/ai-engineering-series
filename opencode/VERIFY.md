# OpenCode 启动阶段验证

日期：2026-11-09。基线 v1.19.5，完整提交与来源见 [锁文件](../docs/agent-series/sources.lock.json)。

## 已完成

- 读取钉版 V1 类型、加载器、trigger、请求准备与子任务执行路径，核对共享 output、顺序调用、dispose 和缺失结果路径。
- 使用 Node 24.14.0 运行 `node --test opencode/examples/check-review-trace.mjs`：8 项通过。
- 将原创样例复制到临时依赖目录，使用 TypeScript 5.9.3、真实 @opencode-ai/plugin 1.19.5 类型执行 strict/noEmit：通过。skipLibCheck 只跳过依赖声明内部检查。
- 依赖安装使用 ignore-scripts；没有加载上游 CLI 运行时。安装时一个间接依赖报告 Node engines 警告，不能据此声称宿主可在本机 Node 上完整运行。

## 未完成

完整 CLI 的安装、项目插件发现、V1/V2 默认选择、真实服务器日志、TUI、模型请求、权限决策、自动重载、退出清理和性能评估均未验证。本轮测试的 SDK 为替身，dispose 为显式调用，最后一个调度器为教学实现。

本册尚未注册产品，尚无整书 HTML/PDF/EPUB。接入与本地成品交付属于后续任务。

## 复现与证据

[示例说明](examples/README.md)包含离线命令和类型核对步骤。[机器可读摘要](facts/plugin-sample-20261109.json)记录版本、结果与样例 SHA-256。临时依赖与原始上游文件在 .scratch，不进入 Git；源码事实可直接通过样章末尾的固定提交链接复核。

仓库整体检查：执行 `python scripts/bookctl.py check --fast`，8 个步骤全部通过，包括通用测试 225 项、构建器测试 556 项、内容与 Mermaid 检查，以及衍生页面重复构建的一致性检查。新增处理器测试另接入 Book CI 的 Fast job。

本机 npm ci 两次因下载访问失败未完成；复用了同一锁文件、同一基线工作树中已有的 Node 依赖后运行上述检查。没有修改依赖锁或绕过检查；干净安装由 PR CI 另行验证。
