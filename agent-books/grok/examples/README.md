# grok/examples：发布闸门

本书从头到尾只用这一个案例仓：一个发布前检查脚本，三个看起来都对、实际上会放过错误的判断。

## 现在就能跑

```powershell
python grok/examples/check_release.py          # 故障版：exit 1，5 个用例里 3 个与预期不符
python grok/examples/check_release.py --fixed  # 修好版：exit 0
python -m unittest discover -s grok/examples -p "test_*.py" -v
```

三条命令只用 Python 3.12 标准库，不调用模型，也不安装任何东西。

## 文件

| 文件 | 作用 |
| --- | --- |
| `release_gate.py` | 有三处缺陷的闸门：版本按字符串前缀比较、CHANGELOG 只看文件在不在、测试日志只要出现 `OK` 就算通过 |
| `release_gate_fixed.py` | 同一闸门，三处缺陷都关上：按数字段比较、要求版本小节存在、要求日志没有 `FAILED` 且有汇总行 |
| `check_release.py` | 用同一张用例表跑两个实现，输出 JSON，退出码表示「用例与预期是否一致」 |
| `test_release.py` | 把「故障版错哪三个用例」钉成断言 |

## 为什么案例长这样

三个缺陷分别对应发布前最容易跳过的三件事：版本号的排序规则、变更记录有没有为这一版写下什么、测试结果到底是哪一行在说话。它们都不需要模型参与就能复现，所以后面接入 Grok 时，能清楚区分「脚本判断错了」和「助手改错了」。
