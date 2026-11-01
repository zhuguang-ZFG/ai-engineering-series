# 驭者第05章 · 制作/发布状态

> 时区：America/Adak
> 更新：2026-11-01（短片已出片 · 待过片）

## 章节

| 项 | 值 |
|----|-----|
| 章节 | 第5章：设置与配置 -- Agent 的基因 |
| 源码路径 | 第二部分-核心系统篇/05-设置与配置-Agent的基因.md |
| 短片钩子 | 改了怎么不生效：一个文件 vs 六层岩 |
| 叙事线 | 痛点 → 六层沉积岩 → 盖住≠删掉 → 钥匙圈只增不减 → 收刀：那一层不算 |

## 文案

| 文件 | 状态 |
|------|------|
| long-outline.md | 已出（7 块 · 36 条动画/代码/互动） |
| short-script.md | 已出（154 汉字 ≈ 53s） |
| long-script.md | 已出（3368 汉字 · 非空白 5561 字符） |
| voice.md / gate-checklist.md / README.md | 已出 |
| 口播 `video/ch05/assets/vo/` | 已合成：53 片 · `total_duration_s` 1055.5s ≈ 17:36 · 字幕 53/53 非空 |

## 成片

| 形态 | 文件 | 状态 |
|------|------|------|
| 抖音/小红书短片 | video/ch05/out/ch05-short-v1.mp4 | **已出片** · 待过片 |
| B站长讲 | video/ch05/out/ch05-long-v1.mp4 | **未开渲** |

## 短片：一条脚本把口播时间戳灌进画面

`video/ch05/hf-remake/build_short.py` 是唯一入口，跑一次产出 `short/` 整个工程：
edge-tts 合成整条口播（云扬 -10% / -5Hz，`boundary="SentenceBoundary"`）→ 按中文标点切句 →
以关键词在句窗里找拍子 → 把 12 个 `$T_*$` 锚点代入 `tpl/dense-short-v3.tpl.html` →
写 `short/index.html` + `compositions/*.html` + `SYNC-MAP.md`，SFX 用 `struct` 现算 WAV。

- 找不到关键词直接 `SystemExit` 并列出全部拍子——时间戳不许是编的。
- 重建四次逐字节一致：`total=50.936s caps=26 sents=10 sfx=32`，锚点
  `T_ROCK 10.76 / T_PRIO 18.33 / T_COVER 19.91 / T_RING 24.45 / T_ANS 28.51 / T_RINGBOX 29.63 /
  T_KEYRULE 32.37 / T_DENY 35.85 / T_CUT 38.67 / T_GREY 41.22 / T_SIGN 44.46 / T_CTA 46.77`。
- 成片实测（ffprobe）：1080×1920、30 fps、1529 帧、`Duration 00:00:50.97`、13,068,147 B、
  H.264 + AAC 48 kHz 立体声、2051 kb/s、`mean_volume -25.7 dB / max_volume -1.5 dB`；`blackdetect` 无黑场。
  口播 mp3 与 `data-duration` 同为 50.936s，尾帧不静音也不被截。
- `hyperframes check` 全绿：lint 0 error（1 条 `composition_file_too_large` 350 行，生成式密集场景固有），
  runtime / layout / motion / contrast / craft / audio 各 0 findings。

本轮从第一次 check 与首帧目视里修掉的：字幕药丸占 y1680..1770，场景 4/5 正文压在那条带上被判
`content_overlap` → 正文整体上移；27 个元素字号低于 28px 地板 → 逐条抬高；`#mb3` 与灰带重叠 →
改成灰带落下时那一层的文字淡掉（语义也对，那层被替换了）；浅色英文副标签实测对比 1.07:1 → 改
`#eaf2ff` + 阴影；首帧空 → `#series`/`#filecard` 第 0 秒就满不透明；`#guess` 被钥匙圈入场顶掉导致
答案行读不满 → 让它留到 38.5s；结尾 4 秒空屏 → 补六条岩层色块签名图形；花字与字幕逐字重复 →
punch 只收 ≤9 字的片段且不出现在 CTA 之后；片尾卡与字幕同句逐字重复 → 片尾改成
「驭者 · Agent Harness / 小电讲电路」的署名锁版，句子只留在字幕里。

## 时长标定（四章实测）

ch01–ch04 的门禁都写「长讲 15–20 min」，但 ch03 实发 9.9 min、ch04 实发 7.6 min，这条实际被跳过了。
下表按各章 `vo-manifest.json` 的 `total_duration_s` 与 `full-script.txt` 现量：

| 章 | 片数 | 口播秒数 | 汉字 | 汉字/秒 | 非空白字符/秒 |
|----|------|---------|------|--------|--------------|
| ch02 | 31 | 627.6 | 1811 | 2.89 | 5.20 |
| ch03 | 31 | 597.0 | 1768 | 2.96 | 5.13 |
| ch04 | 24 | 453.1 | 1263 | 2.79 | 5.21 |
| ch05 | 53 | 1055.5 | 3368 | 3.19 | 5.27 |

- 汉字/秒 的跨度是 2.79–3.19：同一台嗓子，快慢差在标点和英文词的占比上。本章按 2.89 推 19.4 min，实配 17.6 min，估长了一成。
- 非空白字符/秒 稳在 5.13–5.27。写稿阶段用 `字符数 ÷ 5.2 ≈ 口播秒数`：本章 5561 ÷ 5.2 = 1069s，与实测 1055.5s 差 1.3%。
- ch01–ch04 的「成片时长 ÷ 纯口播时长」在 0.97–1.03 之间 → 动画压在口播之下跑，不额外占时长。

配音合成后以 `vo-manifest.json` 的 `total_duration_s` 复核；超 20 min 则从块 3/块 4 收。

## 字幕：四章脚本一起踩到的坑

`synth_long_vo.py` 按 `chunk["type"] == "WordBoundary"` 收词级时间，可 edge-tts 7.x 的 `Communicate`
默认 `boundary="SentenceBoundary"`，只回句级事件。脚本不报错，把 112 个 `.srt` 全写成 0 字节。
现量对照：同一段 80 字，默认只回 `SentenceBoundary` 5 条、`WordBoundary` 0 条；显式传
`boundary="WordBoundary"` 后回 `WordBoundary` 38 条，音频分片数不变（142）。

已改：四章脚本都显式传这个词边界开关；`.srt` 为空不再算作「已合成」；ch03–ch05 收尾处发现空字幕直接
`SystemExit`。本章重跑后 53/53 有字幕。ch02–ch04 的音频是已发布片的配音，重跑会换音频，所以那三章的
`.srt` 留着不动，真要烧字幕时整章重来。

## 配音引擎：MiMo 试了 6 条，暂不接

小米 MiMo TTS（`mimo-v2.5-tts`）能接通：密钥放在 `~/.config/ai-teardown/mimo.env`，项目外，不进仓库。
拿本章 `chunks.json` 里三段最长口播（覆盖开头、中段、结尾）同文比对，两把男声各跑一遍：

| 段 | 云扬 -10% / -5Hz | 白桦 | 苏打 |
|----|-----------------|------|------|
| s1 | 25.27s | 28.16s（+11.4%） | 24.64s（−2.5%） |
| s2 | 18.60s | 20.64s（+11.0%） | 19.52s（+4.9%） |
| s3 | 28.01s | 28.64s（+2.3%） | 30.72s（+9.7%） |

- 同一段文字，MiMo 比云扬慢 2.3%–11.4%，本章 17.6 min 换过去约 18.0–19.5 min——换引擎不动时长模型，`字符数 ÷ 5.2` 仍能用，只是要按引擎各留一档。
- 回读相似度 87.9%–92.6%，全在 95% 这条线以下。差的到底是念歪还是 ASR 听歪，需要拿同一条 ASR 过一遍云扬的音频做对照——对照那一步没跑成：账户余额在第 13 次调用时见底（`402 Insufficient account balance`），两条 key 都是这个账户。
- 所以本章仍用云扬出片，MiMo 的 6 条试听 wav 在 `.scratch-pass3/mimo-audition/`（仓库外），等账户有钱再判。

## 下一步

1. 搭 `video/ch05/` 工程脚手架（镜像 ch04：tools junction + hf-remake）—— 已完成
2. edge-tts 分片合成配音（云扬 -10% / -5Hz），用 `vo-manifest.json` 复核时长 —— 已完成，1055.5s
3. 渲短片 —— 已完成 `out/ch05-short-v1.mp4`（50.97s）→ **等用户过片**
4. 过片后 densify 长讲（`build_dense_v2.py` 那条线），再渲 `ch05-long-v1.mp4`
5. 过片后出三平台封面与发布元数据（描述必须发布前写全）

## Blockers

- 未授权发布；按系列规则「先过片，再发布」
- 长讲 densify 等短片过片确认后再开
