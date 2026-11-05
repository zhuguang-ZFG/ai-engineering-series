# yuyu-book products

| product | 书 | manifest | 产物前缀 | bookctl |
|---------|----|----------|----------|---------|
| `book` | 《御舆：解码 Agent Harness》 | `manifest.json` | `yuyu-agent-harness-*` | `build --product book`（现网；`make book`） |
| `omp` | 《Omp 从入门到精通：原理与实战》 | `manifest-omp.json` | `yuyu-omp-*` | `build --product omp --lang zh`（`make book-omp` / `make book-omp-pdf`） |

两个 product 各有一套通俗层登记表：`plain.registry_names()` 按 manifest 的 `product` 字段
取同名兄弟文件——御舆用裸名（`glosses.json` / `notes.json` / `reading-paths.json`），
omp 用 `-omp` 后缀（`glosses-omp.json` / `notes-omp.json` / `reading-paths-omp.json`），
写第二分册的通俗层不会顺手改到第一分册。`omp` 过去走 `--no-plain` 整层跳过，M2 之后已不传该
开关；`--no-plain` 仍是 `build.py` 的正式开关，留着出「无通俗层」对照排版。插画双轨：正文
`omp/images/` 手绘嵌入 + Mermaid 管道。不要用 `make book` 编 omp。
