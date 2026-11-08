# pi/facts：原始输出切片

这些文件是 `pi/VERIFY.md` 第 1–4 节的原始证据，2026-11-08 在 Windows、
Pi `1.5.0` 上采集。文件名对应 `VERIFY.md` 的小节顺序。

| 文件 | 采集命令 |
| --- | --- |
| `pi-1.5.0/version.txt` | `pi --version` |
| `pi-1.5.0/help-builtin-tools.txt` | `pi --help \| sed -n '/Built-in Tool Names:/,$p'` |
| `pi-1.5.0/print-mode-online.txt` | `pi --print --no-tools --no-session "只回复两个字：在线"` |
| `pi-1.5.0/json-head.txt` | 同上加 `--mode json`，取前三行 |
| `pi-1.5.0/list-models-nvidia.txt` | `pi --offline --list-models nvidia \| head -5` |
| `pi-1.5.0/errors.txt` | 四个命令行错误用例，逐条记退出码 |
| `pi-1.5.0/thinking-invalid.txt` | `--thinking bogus` 的 warning 与后续输出 |

约定：

- 不存凭据、cookie、会话全文或用户目录的绝对路径；session ID 与 cwd 是协议字段，保留原样。
- 切片是**当时**的输出，不是规范。复跑结果不同时，先记新输出和版本，再决定改正文还是改钉版。
- 新增章节需要新的证据时，放进对应版本目录（例如 `pi-1.6.0/`），不要覆盖旧切片——
  旧切片是"当时确实如此"的记录，改了就说不清了。
