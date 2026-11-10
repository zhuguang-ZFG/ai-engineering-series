# C11 答案与核对依据

先完成作业再读。下面的代码不是唯一写法；核对重点是行为：缺失不被补齐、错误有退出码、路径与编码有明确约定。

## 1. 通知2与 `line_count`

一份示例材料：

```text
课程通知

活动: 社区读书会
时间：周六 14:00
地点：邻里工坊
说明：请自带水杯
```

`line_count` 统计原文行数，包括空行；`fields` 只保留四个约定字段。材料有 6 行，字段仍是 4 个，所以两个数字不必相等。`说明` 行不会进入字段表，也不会被当成错误；它是未纳入约定的材料。若你希望“未知行”也进入报告的 `ignored_lines`，那是扩展功能，不是本章默认行为。

## 2. 显式格式参数

一种改法：

```python
parser.add_argument("--format", choices=("json", "markdown"), default="json")
...
if args.format == "markdown":
    payload = to_markdown(fields)
else:
    payload = json.dumps(report, ensure_ascii=False, indent=2)
```

`choices` 让非法值由 `argparse` 以退出码 2 拒绝，并打印可用值。不要在 `else` 里悄悄转成 JSON；调用方显式要求 Markdown 却收到 JSON，属于契约违背。

Markdown 版本示例：

```markdown
| 字段 | 状态 | 原文值 |
| --- | --- | --- |
| 活动 | found | 社区读书会 |
| 时间 | found | 周六 14:00 |
| 地点 | found | 邻里工坊 |
| 报名要求 | missing | （缺失） |
```

缺失值写“（缺失）”，但底层 JSON 仍保留 `null`。不要把 Markdown 的占位文字反写回数据结构。

## 3. 三类失败的记录

| 情形 | 典型输出 | 退出码 | 第一处定位 |
| --- | --- | --- | --- |
| 文件不存在 | `{"status":"error","error":"file-not-found",...}` | 2 | `path.is_file()` 为假 |
| GBK 编码 | `decode-failed`，含 `UnicodeDecodeError` 位置 | 3 | `read_text(encoding="utf-8")` |
| 权限不足 | 打开文件时 `PermissionError` | 建议 4 | `read_text()` 的 `open` 调用 |

权限不足时，正确做法是取得读取授权、复制到自己有权访问的目录，或让文件所有者调整权限。不要用 `except PermissionError: text = ""` 返回一份“空通知”并当作成功；那会把“没有读到”伪装成“材料为空”。如果程序要捕获它，应输出独立错误并保留非零退出码：

```python
except PermissionError as exc:
    print(json.dumps({"status": "error", "error": "permission-denied", "detail": str(exc)}, ensure_ascii=False))
    return 4
```

## 4. 只对四个字段生效的分隔符

```python
def extract_fields(text: str) -> dict[str, dict[str, str | None]]:
    result = {}
    for field in FIELDS:
        value = None
        for line in text.splitlines():
            stripped = line.strip()
            for sep in ("：", ":"):
                prefix = field + sep
                if stripped.startswith(prefix):
                    candidate = stripped[len(prefix):].strip()
                    if candidate:
                        value = candidate
                    break
            if value is not None:
                break
        result[field] = {"value": value, "status": "found" if value else "missing"}
    return result
```

测试输入：

```text
活动：读书会
备注：地点：不要把这行当地点
```

`备注` 行不以 `地点` 开头，所以不会被误收。若有一行 `地点: 邻里工坊`，半角冒号路径会取到值。注意 `地点：` 后面为空时，当前实现仍记 `missing`；这是有意的，因为“字段存在但空值”不能被当成已确认地点。

## 5. 为什么用脚本所在目录

`Path(__file__).resolve().parent` 让程序找到自己旁边的 `notices/`，与启动时的工作目录无关。用户可以从任意目录运行：

```bash
python C:\work\llm-practice\notice_report.py
```

仍然读到 `C:\work\llm-practice\notices\通知.txt`。直接写相对路径时，`notices/通知.txt` 会相对于终端当前目录解析；换一个目录启动就找不到文件。交付给别人的程序不能假设对方总在某个目录启动。

## 核对清单

- 程序运行成功时退出码为 0，失败时不伪装成功。
- `时间：周六 14:00` 和 `时间:周六 14:00` 都保留完整时间；只移除字段前缀，不继续分割值中的冒号。
- UTF-8 BOM 由文件头识别并在解码时去除；它不触发 UTF-8 解码异常，不能靠“先 utf-8，失败再 utf-8-sig”处理。
- 缺失字段在 JSON 中是 `null`，且进入 `missing` 列表。
- 文件路径与编码在输出中可回查。
- 只有四个约定字段会被提取；无关行不进入结果。
- 你能从 `Traceback` 最后一行说出错误类型和出错行。

本章没有调用模型、OCR 或网络，因此不需要模型输出证据；它验证的是本地程序、文件与错误处理。
