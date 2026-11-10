# ch01–ch05 迁移对照审阅记录

对应计划 P6.4 / P6 Gate，以及规格 7.5「ch01–ch05 迁移后画面、字幕和时长允许的差异有审阅记录」。记录日期 2026-11-07，对照基线标签 `legacy/pre-platform-2026-11-03`。

## 结论

| 项目 | 结果 | 判定 |
|---|---|---|
| 时间线 | `ch01/compat-report.json` 的长版、短版均为 `match` | 通过 |
| 尺寸 / fps | 1920×1080 / 1080×1920，30 fps，与旧 `index.html` 一致 | 通过 |
| 时长 | 长版 1148.352 s，短版 32.624 s，与旧 `index.html` 和音频时长一致 | 通过 |
| 字幕文本 | 归一化后 5021 字完全一致，相似度 1.0 | 通过 |
| 字幕切分 | 旧 147 条，新 389 条；由 16 字上限的字幕策略重新切分 | 允许差异 |
| 画面来源 | ch01–ch05 的 115 个已跟踪渲染输入与基线逐字节一致（仅换行符归一）；0 个修改 | 通过 |
| 关键帧 | 仓库与基线标签中都没有旧 `.mp4` / `.mov` / `.webm`，无帧可比 | 不适用（N/A），不声明通过 |
| 音频 / 成片质量 | 未运行真实录音与渲染质量门 | 仍然 unverified |

## 字幕比较

旧字幕在基线标签中位于 `video/ch01/assets/build/merged.srt`，工作树清理前 SHA-256 为
`2323f9ccaca6dc63dd118465c4716b7d8e8096de6a103ded287d0a51629e98d0`。

复现命令：

```bash
git show legacy/pre-platform-2026-11-03:video/ch01/assets/build/merged.srt > /tmp/ch01-legacy.srt
python - <<'PY'
import sys
from pathlib import Path
sys.path.insert(0, "video")
from pipeline import model, timeline, voice

chapter = Path("video/chapters/ch01")
episode = model.read_yaml(chapter / "episode.yaml")
current = voice.cues(
    episode, chapter, "long",
    total_s=episode["formats"]["long"]["duration_s"],
    audio_path=chapter / "full.mp3",
)
legacy = timeline.parse_captions(Path("/tmp/ch01-legacy.srt"))
left = voice.normalized("".join(cue["text"] for cue in legacy))
right = voice.normalized("".join(cue["text"] for cue in current))
print(len(legacy), len(current), len(left), len(right), left == right)
PY
```

结果：`147 389 5021 5021 True`。旧文件把多句并成一条长字幕，新轨道按
`video/chapters/ch01/episode.yaml` 的 `captions.max_chars: 16`、`max_lines: 2`
重新切分，因此条数和逐条时间不能一一对应；文本内容没有增删。逐条时间比较
会让这个策略差异淹没真实漂移，所以采用「归一化全文 + 音频总时长」作为字幕
一致性证据。渲染时字幕由 `voice.cues` 从同一份口播脚本生成，不存在维护两份文本。

## 画面比较

已跟踪的渲染输入（`index.html`、`compositions/`、组件、`hyperframes*.json`、
`meta.json` 与 `assets/huashu-specs/*.json`）在 ch01–ch05 共 115 个文件上与基线
标签逐字节一致；比较前把 CRLF 归一为 LF，结果 0 个修改、0 个删除。五个
`short/compositions/dense-short.html` 是旧构建脚本的本机生成物，被 `.gitignore`
排除，从未进入 Git；它们不参与这项比较。

这意味着长版画面由与迁移前相同的输入文件渲染。短片的差异仅限这五个本机
生成场景，不来自对旧场景源的改写。

复现命令：

```bash
python - <<'PY'
import subprocess
from pathlib import Path

tag = "legacy/pre-platform-2026-11-03"
same = modified = 0
for number in range(1, 6):
    base = Path("video") / f"ch{number:02d}" / "hf-remake"
    for path in sorted(base.rglob("*")):
        if not path.is_file() or path.suffix not in {".html", ".css", ".js", ".json"}:
            continue
        old = subprocess.run(["git", "show", f"{tag}:{path.as_posix()}"],
                             capture_output=True).stdout
        if not old:
            continue
        if old.replace(b"\r\n", b"\n") == path.read_bytes().replace(b"\r\n", b"\n"):
            same += 1
        else:
            modified += 1
print(same, modified)
PY
```

结果：`115 0`。

## 关键帧与允许差异

`timeline.keyframe_report()` 只比较两个真实视频文件；缺少旧片或新片时返回
`{"status": "unverified"}`，不会伪造相同。本仓库和基线标签都没有视频文件，
因此关键帧比较在本次迁移中不适用，也没有被纳入兼容报告或发布声明。若以后
拿到旧片与一次新渲染，可直接调用：

```bash
python - <<'PY'
import sys
from pathlib import Path
sys.path.insert(0, "video")
from pipeline import timeline
print(timeline.keyframe_report(Path("old.mp4"), Path("new.mp4")))
PY
```

## ch02–ch05 补充审阅

长版时间线、尺寸、fps、时长和音频时长在 `compat-report.json` 中均为 `match`；
画面来源按上一节同一比较脚本覆盖，115 个已跟踪输入 0 修改。

| 章节 | 旧字幕证据 | 结果 |
|---|---|---|
| ch02 | `assets/vo/c*.srt` 31 个，全部 0 字节 | 无可读字幕，N/A |
| ch03 | `assets/vo/c*.srt` 31 个，全部 0 字节 | 无可读字幕，N/A |
| ch04 | `assets/vo/c*.srt` 24 个，全部 0 字节 | 无可读字幕，N/A |
| ch05 | `assets/vo/c*.srt` 53 个，339 条 cue | 归一化后 4956 字与当前一致；仅 `「」`、`/`、`·` 标点差异 |

ch02–ch04 的旧 SRT 是空的中间产物，无法作为字幕对照；这不等于当前字幕已经过
人工审听。ch05 的标点差异来自旧 SRT 省略引号、斜杠与间隔号，文本没有增删。
这四章的旧 SRT 从未进入 Git，只在本次工作树中可见；记录保存的是本次审阅结果，
不把它伪装成干净克隆可复现的证据。

允许差异清单：

1. ch01 字幕切分：147 条长句 → 389 条 16 字上限的短句，文本归一化后相同。
2. ch05 字幕标点：旧 SRT 省略 `「」`、`/`、`·`，归一化后文本相同。
3. ch02–ch04 字幕：旧 SRT 为空，字幕对照 N/A，当前字幕仍需人工审听。
4. 短片画面：五个 `dense-short.html` 本机生成物未入库，迁移后不再依赖旧脚本生成；
   长版画面输入不变。
5. 渲染质量与音频：无真实录音 / 成片对照，保持 unverified，发布声明不得写成已验证。
