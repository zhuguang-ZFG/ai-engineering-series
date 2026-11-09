# Hermes 书中实验

这些示例不需要模型凭据，也不向外发送请求。`check_memory_components.py` 运行固定版本的真实组件；`book-inventory` 是本书原创插件，离线测试不启动 Hermes 宿主。

## 记忆组件

检出 `NousResearch/hermes-agent` 的 `2bd378ed1b8d6bf2192cb26e0a55ff3091e6bd19`，然后在本书仓库根目录运行：

```powershell
python hermes/examples/check_memory_components.py --upstream ../hermes-agent-reference --without-yaml
```

本次采用 `--without-yaml`，技能元数据只验证上游的简单降级解析。装齐上游依赖后可去掉该选项，单独验证正常 YAML 路径。脚本绕过完整包初始化，并为 `tools.memory_tool` 提供目录与锁入口；目标校验函数从原源码提取后原样执行。详情见[验证记录](../VERIFY.md)和[附录 C](../appendix-c.md)。

输出写入本仓库 `.scratch/agent-series/hermes-memory-*`。不要把这个临时 profile 改成日常账户数据目录。报告给出上游文件哈希、测试预算、解释器与逐项结果。

## 资料清单插件

运行离线检查：

```powershell
python -m unittest discover -s hermes/examples -p "test_*.py" -v
```

handler 只接受 `{}`，最多返回 100 个 Markdown 相对路径，最多扫描 10000 个目录项。它跳过隐藏子目录、符号链接和 Windows junction，拒绝根路径经过链接；不读取文件正文，不运行命令。目录若在扫描期间被其他进程恶意替换，本示例不提供操作系统级竞态隔离；测试库应由当前操作者独占。

准备完整宿主实验时，将 `book-inventory` 目录复制到当前 Hermes home 的 `plugins/` 下，保留两个文件。先建立测试资料目录，再将以下片段合并到实验 profile 的配置：

```yaml
plugins:
  enabled:
    - book-inventory
  entries:
    book-inventory:
      settings:
        root: D:/agent-labs/aurora
```

配置读取和目录发现依据 Hermes v0.23.0。有效 ID 来自该目录布局；多层分类目录的 ID 不一定等于 manifest 的裸名称。已有 `plugins.disabled` 时也要检查其中是否禁用了本插件。

本次仅验证处理器与传入 FakeContext 的注册参数，没有运行宿主发现、模型工具选择或插件卸载。完整宿主里，应另行记录发现日志、注册工具名、当前请求中的可用工具和实际调用结果。插件不创建线程、不持有长连接，所以没有示范额外的 `on_unload` 清理；将来增加后台资源时，应在获取后立即登记释放动作。
