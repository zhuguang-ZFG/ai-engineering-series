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
| 抖音/小红书短片 | video/ch05/out/ch05-short-v1.mp4 | **已出片（真采样音效 + bed）** · 待过片 |
| 同上，换音频前的一版 | video/ch05/out/ch05-short-v1-pre-audio-fix.mp4 | 留着做 A/B，听完可删 |
| B站长讲 | video/ch05/out/ch05-long-v1.mp4 | **未开渲** |

## 短片：一条脚本把口播时间戳灌进画面

`video/ch05/hf-remake/build_short.py` 是唯一入口，跑一次产出 `short/` 整个工程：
edge-tts 合成整条口播（云扬 -10% / -5Hz，`boundary="SentenceBoundary"`）→ 按中文标点切句 →
以关键词在句窗里找拍子 → 把 12 个 `$T_*$` 锚点代入 `tpl/dense-short-v3.tpl.html` →
写 `short/index.html` + `compositions/*.html` + `SYNC-MAP.md`，音效取媒体库的真采样，背景音乐是一条本地生成的 bed。

- 找不到关键词直接 `SystemExit` 并列出全部拍子——时间戳不许是编的。
- 重建逐字节一致：改过 `BGM_GAIN` 再建一次，`index.html` / `SYNC-MAP.md` / `short-meta.json`
  加两个 `compositions/*.html` 五个产物 md5 与上一份全同（`md5sum -c` 五行 OK）——edge-tts 每次重新联网取流，
  拍子却没漂，所以下面那支成片和当前工程文件是对得上的，不必重渲。
  `total=50.936s caps=26 sents=10 sfx=32 bgm=yes`，锚点
  `T_ROCK 10.76 / T_PRIO 18.33 / T_COVER 19.91 / T_RING 24.45 / T_ANS 28.51 / T_RINGBOX 29.63 /
  T_KEYRULE 32.37 / T_DENY 35.85 / T_CUT 38.67 / T_GREY 41.22 / T_SIGN 44.46 / T_CTA 46.77`。
- 成片实测（ffprobe）：1080×1920、30 fps、1529 帧、`Duration 00:00:50.97`、11,509,465 B、
  H.264 + AAC 48 kHz 立体声、1807 kb/s、`mean_volume -25.0 dB / max_volume -1.4 dB`；`blackdetect` 无黑场。
  口播 mp3 与 `data-duration` 同为 50.936s，尾帧不静音也不被截。
- 混音前后对照（同一支 `loudnorm`）：旧片（合成嘟声、无 bed）−21.9 LUFS / −1.5 dBTP / LRA 4.5 LU，
  新片（真采样音效 + bed）−21.9 LUFS / −1.4 dBTP / LRA 3.7 LU。整片一点没变响、真峰不动，
  LRA 掉 0.8 LU 是 bed 把口播之间的空隙填上了——人声没被抬，也没被压。
- bed 真在片子里，用 `hyperframes audio --only silence --silence-db=-45` 量：旧片 33 段落在 −45 dBFS 以下
  （含 27.885–28.505、35.145–35.850、46.130–46.765 这些口播之间的缝），新片只剩 3 段：
  0.000–0.385、0.430–0.645（第一声 `click` 在 0.60s 之前）与 50.320–50.967（1.5s 淡出把 bed 拉到地板下）。
  也就是说口播一停，画面底下仍有音乐，直到片尾淡出。
- 开渲命令（在 `video/ch05/hf-remake/short` 里跑，`-o` 按 cwd 解析，别写成 `../out`，那会落进 `hf-remake/out`）：
  `npx --yes hyperframes@0.8.210 render -o ../../out/ch05-short-v1.mp4 --fps 30 --quality looks --workers 1 --low-memory-mode`
- `hyperframes check`：lint / runtime / layout / motion / contrast / craft / audio 零 error，
  只剩 1 条 warning：`composition_file_too_large`（350 行，生成式密集场景固有）。
  中间一次 check 还报过两条 craft `line_unread`，说片尾「驭者 · Agent Harness」「小电讲电路」只在场 0.50s
  （片尾地板 2s）；从成片抽帧到 49.5s 看，署名锁版（六条岩层 + 主标 + 副标）完整在场，
  tween 是 46.769s 入场 0.3s 走完、实际在场 3.87s，再跑一次 check 这两条也没了——按量法不稳处理，
  以成片帧为准，不为了哄工具去动画面时间轴。

本轮从第一次 check 与首帧目视里修掉的：字幕药丸占 y1680..1770，场景 4/5 正文压在那条带上被判
`content_overlap` → 正文整体上移；27 个元素字号低于 28px 地板 → 逐条抬高；`#mb3` 与灰带重叠 →
改成灰带落下时那一层的文字淡掉（语义也对，那层被替换了）；浅色英文副标签实测对比 1.07:1 → 改
`#eaf2ff` + 阴影；首帧空 → `#series`/`#filecard` 第 0 秒就满不透明；`#guess` 被钥匙圈入场顶掉导致
答案行读不满 → 让它留到 38.5s；结尾 4 秒空屏 → 补六条岩层色块签名图形；花字与字幕逐字重复 →
punch 只收 ≤9 字的片段且不出现在 CTA 之后；片尾卡与字幕同句逐字重复 → 片尾改成
「驭者 · Agent Harness / 小电讲电路」的署名锁版，句子只留在字幕里。

## 短片音频：音效换成真采样，补一条 bed

旧版 `build_short.py` 用 `struct` 现算 WAV，口播一句一下、共 32 下合成嘟声，听感被判废。现在两条都换了。

**音效**取 media-use 自带库（19 条，Pixabay Content License，免署名）：`stage_sfx()` 把本片用到的 14 条 `.mp3`
复制进 `short/assets/sfx/`，时长读库里的 `manifest.json`（离线的唯一时长来源，不猜），`CREDITS.md` 由脚本一并落笔。
条数按实数写：库自己的 `SKILL.md` 第 23 行写「21 bundled offline」，但磁盘与 `manifest.json` 都是 19 条。
授权出处要留一句：`manifest.json` 里只有 `file / duration / description`，**没有任何授权字段**，
「Pixabay、免署名」来自库自带的 `audio/assets/sfx/CREDITS.md`（写明 Pixabay Content License，允许商用与二次分发、
不要求署名）——以后审版权别去 manifest 找，那里没有。
库或某条曲目不在就 `SystemExit`——合成音没有替身，宁可不出片。每条的 `data-volume` 是线性增益（HyperFrames
按 `20*log10(volume)` 折算），先 `ffmpeg -af loudnorm` 逐条量积分响度与真峰，再按「人声之下 9 LU（点缀类）/
6 LU（低频与 riser）/ 10 LU（glitch）」换算，例如 `impact-bass-1` 实测 −6.5 LUFS → 0.07，`ping` −25.5 LUFS → 0.43。
`click`、`click-soft` 只有 0.37s，短于 ebur128 的门限，量不出 LUFS，按 −4.8 dBTP 定位。
点位不再跟着口播逐句走，改压在画面真看得见的动作上：`0.60 #b-edit`、`1.10 #mval`、`1.60 #b-restart`、
`2.30 #xmark`、`3.50 #ftitle`，六层岩 bd1–bd6 与钥匙圈每层各一下。`band_times()` 和 `key_times()` 同时供
GSAP tween 与音效点位，两边共用一份时间，不会漂。

**背景音乐**是 `short/assets/bgm/track.wav`，由本目录新增的 `make_bgm.py` 生成：51.000s、32 kHz、单声道、峰值 0.890，
实测 **−18.3 LUFS / −1.0 dBTP / LRA 4.1 LU**。取材走 media-use 的本地路线（`facebook/musicgen-small`，torch 2.14.1+cpu）：
`--seed 7` 固定采样种子（不固定就每次不同，上面这些数字也守不住），出 23.94s 种子实测 175.2–201.6s
（另加加载 5.3–5.9s，两次墙钟不一样），再按 2.0s 等功率交叉淡化铺到 51s，头尾 0.8s / 1.5s 淡入淡出。
种子真的锁住了：`make_bgm.py --out` 指到 scratch 重跑一遍，与工程里在用的这一份 md5 相同
（`8511a9a71ad36b49cf138c04cce7c434`），换机重跑也守得住上面那三个数。
口播 stem 实测 −24.9 LUFS，所以 `BGM_GAIN = 0.117`（−18.6 dB）把 bed 钉在人声之下 12 LU——这个数与
media-use 自己的 `BGM_BED_VOLUME = 0.12` 撞到了一起，算是独立复核。
没做逐句 ducking 轨道：stem 里 ≥0.6s 的静音只有 6 段、最长 0.8s（27.90 / 29.02 / 35.24 / 38.08 / 46.15 / 50.33），
一条 lane 只会让 bed 抽动，听不出「压低」；12 LU 这个间隔本身就是 duck。

三处坑，都在 `media-use/audio/scripts/lib/bgm.mjs` 那一层：

1. `resolve --only bgm` 做不出 51s——engine 的 `durationS` 取它自己那批 TTS 语音的总长，上限 30s。要长过 30s 只能直接调 `generateBgmDetached`。
2. 机器上有 `GOOGLE_API_KEY`，engine 的开关 `lyriaConfigured = key && recipe && existsSync(recipe)` 会为真，
   接着 `pip install google-genai` 花这笔 key 的额度去云端生成。把 `lyriaRecipe` 指到一个不存在的路径，它才落到本地免费路线。
   `heygen auth login --oauth` 才是那 1 万条现成曲库的入口，这台机器没有 `heygen` CLI、也没有 `HEYGEN_API_*`。
3. detached 生成连死三次，日志停在 `[musicgen] seed dur=` 之后，无 traceback、无产物；同参改到前台一次跑通。
   这条死因没有查到底，只确认「不再依赖 detached 这条路」能稳定出片——所以生成脚本入库为 `make_bgm.py`，
   前台、固定 `--seed`、`--out` 可指到 scratch 里验种子而不覆盖交付件。

音频二进制不进库：`.gitignore` 挡掉 `video/**/*.mp3`、`video/**/*.wav`、`video/**/out/`，所以 bed 与音效只能在
构建时就地取用——bed 现生成（`python3 video/ch05/hf-remake/make_bgm.py`，本机 3–3.5 min CPU），
工程重挂（`python3 build_short.py`）；缺库或缺 `track.wav` 会被 `SystemExit` 和 `bgm=no` 暴露出来。

守卫实测会红（把 `build_short.py` 当模块 import 进来直接调函数，不改工程文件）：`SFX_LIB` 指到不存在的路径
→ `sfx library not installed: expected C:\nonexistent\sfx-lib\manifest.json`；从 `manifest.json` 里删掉一条曲目
→ `sfx cue 'chime' is not in ...`；`BGM` 指空 → `bgm_tag()` 返回 `('', None)`，构建照跑、打印 `bgm=no`
——bed 是可选层，音效不是。当前 `short/index.html` 里 32 个音效点位（取自 14 条 `assets/sfx/` 曲目）、
`assets/bgm/track.wav` 1 条。再把 `index.html` 真引用的文件名逐条回查 manifest 与磁盘：14 个全部对得上、都在，
`mismatch: []`——扩展名写错、库改了文件名这类事不会等到渲染才暴露。

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
