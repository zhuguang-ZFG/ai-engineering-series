# 附录 B：配置字段与权限令牌

<!-- block: cursor-apxb.b-opening -->
全局文件装设置，项目文件装权限；令牌是纯字符串，deny 永远排在 allow 前面。

## B.1 配置文件的必填字段

`cli-config.json` 标为必填的只有四项：`version`（当前为 `1`）、`editor.vimMode`、`permissions.allow`、`permissions.deny`。缺失字段由 CLI 自行补齐，文件损坏时 CLI 会把它备份成 `.bad` 再重建。

最小可用形态：

```json
{
  "version": 1,
  "editor": { "vimMode": false },
  "permissions": { "allow": ["Shell(ls)"], "deny": [] }
}
```

## B.2 常用可选字段

| 字段 | 取值 | 影响 |
| --- | --- | --- |
| `approvalMode` | `allowlist`、`auto-review`、`unrestricted` | 审批基线 |
| `sandbox.mode` | 沙箱开关 | 命令是否进沙箱 |
| `sandbox.readBoundary` | `system`、`workspace` | 可读范围 |
| `rewind` | 布尔 | 会话内 `/rewind` 是否可用 |
| `notifications` | 布尔 | 轮次结束或等待输入时发终端通知 |
| `model` | 对象 | 默认模型 |
| `network.useHttp1ForAgent` | 布尔 | 走 HTTP/1.1 + SSE，企业代理常见需求 |

## B.3 五类权限令牌

<!-- block: cursor-apxb.b-tokens -->
| 令牌 | 匹配对象 | 写法示例 |
| --- | --- | --- |
| `Shell(cmd)` | 命令行第一个词，支持 glob 与 `cmd:args` | `Shell(git)`、`Shell(curl:*)` |
| `Read(glob)` | 读路径 | `Read(src/**/*.ts)` |
| `Write(glob)` | 写路径 | `Write(package.json)` |
| `WebFetch(domain)` | 抓取域名 | `WebFetch(docs.github.com)` |
| `Mcp(server:tool)` | MCP 服务器与工具 | `Mcp(datadog:*)` |

规则细节：`*` 匹配所有域名，`*.example.com` 匹配子域但不匹配 `example.com` 本身；相对路径以工作区为根，绝对路径可以指到项目之外；**deny 压过 allow**。

## B.4 三档审批基线

- `allowlist`：只放行 allow 规则覆盖的动作。
- `auto-review`：由自动审查判断哪些动作放行。
- `unrestricted`：等同于非交互模式加 `--force`。

`unrestricted` 也压不住 `permissions.deny` 与团队策略；团队关掉 Run Everything 时，非交互运行会直接失败。
