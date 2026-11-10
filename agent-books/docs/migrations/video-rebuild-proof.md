# Video intermediate rebuild proof

Regenerated from the chapter script by `video/pipeline/cli.py prove`.

| chapter | chunks | vo-manifest | captions | audio slices | transcript |
|---|---|---|---|---|---|
| ch01 | identical | text matches slices (no legacy manifest) | consistent | sum 1147.58s + 0.768s concat padding = full 1148.35s | deterministic |
| ch02 | identical | identical | consistent | sum matches | deterministic |
| ch03 | identical | identical | consistent | sum matches | deterministic |
| ch04 | identical | identical | consistent | sum matches | deterministic |
| ch05 | identical | identical | consistent | 53 slices, long not yet rendered | deterministic |

## 清理记录（P6.6 / P8.2）

2026-11-07 从 Git 移除 270 个已证明可重建或只服务旧脚本的中间文件：

| 类别 | 数量 | 内容 |
|---|---|---|
| 旧章节构建脚本 | 34 | `assets/**/*.py`、`hf-remake/build_*.py`、`assemble_proof_hf.py`、`fix_lint.py`、`synth_*_vo.py`、`make_bgm.py` |
| 口播切片 / 转写文本 | 229 | `assets/vo/`、`assets/vo-short/`、`assemble/`、`build/` 下的 `.txt` 与短片的 `vo-concat.txt` |
| 生成清单 | 7 | 五个 `short*/short-meta.json` 和两份旧短片变体清单 |

保留的输入：

- `video/chapters/ch01..ch15/` 的 episode、scene、脚本、content pack 与 compat 报告；
- 旧工程的 `index.html`、`compositions/`、`hyperframes*.json`、`meta.json`、审阅报告；
- 口播样稿 `sample-long.txt` / `sample-short.txt`、白板规格和 `assets/huashu-specs/*.json`；
- 媒体（mp3、wav、mp4、sfx）从未进入 Git，清理不改变这一点。

被删除的旧字幕 `video/ch01/assets/build/merged.srt` 仍可从
`legacy/pre-platform-2026-11-03` 取回；ch01–ch05 的字幕与画面对照记录见
`docs/migrations/video-compat-review.md`。清理后的 `video/` 跟踪 248 个文件，比基线
的 474 个少 226 个。

清理后复验：

```bash
python video/pipeline/cli.py check --config-only
python video/pipeline/cli.py prove --config-only
```

15 章配置全部通过，ch01–ch05 的 source/configuration 独立重建均为 `identical`。
`prove` 不加 `--config-only` 需要本机已有的未跟踪音频/媒体，不再是可以从干净克隆
复现的 Git 契约；媒体和成片质量仍为 unverified。
