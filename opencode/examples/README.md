# OpenCode 插件实验

基线：OpenCode v1.19.5 的 V1 Plugin/Hooks 接口。示例为本书原创。[样章](../ch08.md)解释行为，[验证记录](../VERIFY.md)记录实际运行范围。

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

将 review-trace.ts 原样复制到该临时目录，再用其中的 TypeScript 对副本执行：

```bash
node .scratch/plugin-types/node_modules/typescript/bin/tsc --noEmit --strict --skipLibCheck --target ES2022 --module ESNext --moduleResolution Bundler --types node --typeRoots .scratch/plugin-types/node_modules/@types .scratch/plugin-types/review-trace.ts
```

skipLibCheck 跳过依赖自身声明文件的内部检查，示例仍做严格类型检查。安装可能提示当前 Node 低于某个间接依赖的 engines；这里未导入上游运行时，不能用类型通过证明整个宿主兼容该 Node。

## 后续宿主验证

固定版本的 CLI 加载、项目插件发现、服务器日志、真实取消和卸载时序还需要独立验证。本轮不自动安装全局 CLI、不修改个人配置，也不调用模型。实验里的 dispose 由测试显式调用。
