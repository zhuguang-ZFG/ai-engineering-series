# C12 答案与核对依据

## 1. `/health`、`/echo`、`/admin`

启动服务端后：

```bash
curl -i http://127.0.0.1:8765/health
```

预期状态行 `HTTP/1.1 200 OK`，正文含 `"service": "teaching-lab"`。

```bash
curl -i -X POST http://127.0.0.1:8765/echo \
  -H "Content-Type: application/json; charset=utf-8" \
  -H "Authorization: Bearer local-teaching-only" \
  -d '{"message":"地点缺失"}'
```

预期 `200`，正文把 `message` 原样回显，并给出实际字节数。`-i` 会显示响应头；只看正文会漏掉 `Content-Type`、`Content-Length` 和状态行，排错时这些信息很关键。

```bash
curl -i http://127.0.0.1:8765/admin
```

没有 `Authorization` 时预期 `403`（该分支先检查授权，而不是 `401`）；带错误 token 也是 `403`。`/echo` 缺少 token 则是 `401`。两者的区别由本教学服务的实现决定；真实服务可能采用不同策略，必须以服务文档为准。

## 2. `request_id` 校验

在 `do_POST` 中解析 JSON 后加入：

```python
request_id = data.get("request_id")
if not isinstance(request_id, str) or not (1 <= len(request_id) <= 40):
    self._send(422, {"status": "error", "error": "invalid-request-id"})
    return
```

三个请求：

```json
{"message": "x"}
```

→ `422 invalid-request-id`。

```json
{"message": "x", "request_id": 123}
```

→ `422 invalid-request-id`（类型不对，不是“自动转字符串”）。

```json
{"message": "x", "request_id": "notice-001"}
```

→ `200`，并回显 `request_id`。

“缺失”和“格式错误”都用 `422` 也可以，但错误字段必须能区分原因；若服务契约要求坏语法为 `400`、语义错误为 `422`，就按契约拆开。

## 3. 超时与服务端执行

把客户端超时改为 `3.0` 后，`/slow` 在约 2 秒返回 `200`。服务端确实执行了 `time.sleep(2.0)` 并发送响应；客户端在 0.2 秒时放弃等待，并不撤销服务端已经发生的动作。因此：

- 客户端超时只证明“等待窗口内没收到完整响应”；
- 不能推出“服务端没执行”；
- 对写入操作，客户端应带请求 ID，服务端提供查询或幂等机制。

## 4. 幂等键

服务端维护一个 `seen: dict[str, dict]`（真实服务应使用持久存储并加锁）。同一 `request_id` 第二次到达时，直接返回第一次的结果，不再执行副作用：

```python
if request_id in seen:
    self._send(200, {"status": "ok", "reused": True, "result": seen[request_id]})
    return
```

仅在客户端重试而不带幂等键，服务端无法区分“用户重复提交”和“网络重试”，可能重复扣款、重复发送或重复写入。幂等键必须由客户端生成、在重试时保持不变，并有足够熵避免碰撞。

## 5. 两处“失败被当成成功”的风险

第一处：`json.loads` 失败被 `except Exception` 吞掉，然后返回 `{"status":"ok"}`。应只捕获 `UnicodeDecodeError`/`json.JSONDecodeError`，返回 `400`。

第二处：只检查 `response.status == 200`，不检查响应体的 `status` 字段和字段类型。服务可能返回 `200` 加 `{"status":"error"}`；应同时校验状态码和业务字段。

另外，`urllib.error.URLError` 之外的连接中断、读取超时也可能发生；捕获后应保留 `status: null` 和错误原因，不能改写成 200。

## 核对清单

- 能区分 `401`、`403`、`404`、`422`、`5xx` 与连接超时。
- 坏 JSON 用原始字节测试，而不是用 `json.dumps()` 构造。
- 凭据来自环境变量，日志不打印请求头。
- 超时结果标记为“未知”，不写成成功或“未执行”。
- 幂等键在重试时保持不变，服务端有去重逻辑。

本章只验证本地回环服务；真实模型 API 的鉴权、状态码和计费字段仍需按服务方当前文档核对。
