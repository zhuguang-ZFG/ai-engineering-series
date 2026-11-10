# 驭者第04章 · 制作/发布状态
> 时区：America/Adak  
> 更新：2026-10-29 18:56 America/Adak（视频号元数据已补全）

## 章节

| 项 | 值 |
|----|-----|
| 章节 | 第04章：权限管线 -- Agent 的护栏 |
| 源码路径 | 第一部分-基础篇/04-权限管线-Agent的护栏.md |
| 短片钩子 | 万能钥匙 vs 四道闸 |

## 成片

| 形态 | 文件 | 状态 |
|------|------|------|
| 抖音/小红书短片 | video/ch04/out/ch04-short-v1.mp4 | 已过片 · ~39s · 1080×1920 |
| B站长讲 v2 | video/ch04/out/ch04-long-v2.mp4 | 已过片（t202u 同意继续）· densify v2 · ~453s · ~175MB · 1920×1080 |

## 封面（均已 staged）

- B站横版：`C:\Users\zhugu\yuzhe-publish\ch04-cover.png`（及 video/ch04/out/）
- 抖音 9:16：`ch04-cover-916.png`
- 小红书 3:4：`ch04-cover-34.png`

## 三平台

### B站 · 小电讲电路 · DONE
- bvid：BV1Kkso6MEvv
- aid：117523139857029
- cid：43148247416
- 标题：驭者·Agent Harness 04｜万能钥匙不够用：Agent 的护栏是权限管线
- tid：231 · copyright：1
- 合集：season_id 9436416「驭者·Agent Harness」· ep4（add_ep code=0 OK）
- 封面：投稿时 `--cover` 挂设计稿；archive cover `http://i0.hdslb.com/bfs/archive/ab2ef62148a8f7ec222d9dd6dcd835d15bc745f6.png`
- CDN：`--line tx`（默认线路 TLS 过期）
- 日志：`C:\Users\zhugu\biliup\upload_yuzhe_ch04.log`
- meta：`C:\Users\zhugu\biliup\meta\yuzhe-ch04.json`
- URL：https://www.bilibili.com/video/BV1Kkso6MEvv

### 抖音 · 本机实跑 · DONE（封面已二次修正）
- mid：7701997723788037386
- 标题：万能钥匙不够用 · 你要的是闸｜驭者·04
- 封面：发布后内容管理缩略图不对 → `fix_ch04_douyin_cover.py` 改竖版设计稿 `ch04-cover-916.png`
- 修封面结果：cover_fixed=true · api cover id `5028323a16e74b0a8227a699c7ae1486`
- 结果：`C:\Users\zhugu\yuzhe-publish\ch04-douyin-result.json`

### 小红书 · BLOCKED（账号禁发）
- 目标标题：万能钥匙 vs 四道闸｜驭者开源讲义 04 钩子
- 素材/封面：短片 + `ch04-cover-34.png`（hover→编辑封面→image input→完成 **已验证成功**）
- 账号：创作端登录为「本机实跑」（小红书号 4947744565）。首页「理工搬砖狗」是成长旅程角标，**不是**可切换的第二账号；Edge 配置未登录；omp chrome 同号。
- 阻塞：点击 `XHS-PUBLISH-BTN`（坐标约 760,940）后弹出 **「因违反社区规范禁止发笔记」**，笔记管理无新稿。
- 已重试：upload_ch04_xhs.py / xhs2 / xhs3 / xhs4 / xhs5；封面链路已通，发布被平台拦截。
- 结果：`C:\Users\zhugu\yuzhe-publish\ch04-xhs-result.json`（published=false）
- 需要：用户解禁本机实跑，或另行登录可发笔记的小红书号后再发。



### 视频号 · 小电讲电路 · DONE（元数据已补全，未重传视频）

- 时间：2026-10-29 18:56 America/Adak（18:48 提交，约 7 分钟后列表生效）
- exportId：`export/UzFfBgAAxL6JcBtBRweEk8zT4DCaahathsOJeIGdGYYk9nu9uQ`（2026-10-29 17:08:12 · status=1 · visibleType=1）
- 描述：`驭者04｜权限管线：Agent 的护栏`（改前为空 → 现 len=19）
- 短标题：`驭者04 权限管线护栏`（未改动，保持原值）
- 封面：设计稿仍在 —— coverUrl `encfilekey=KGDRibp2w…4TcDtOMAQ` 与改前 `initialInfo.coverUrl` 一致，本次未提交 coverUrl
- 列表确认：视频管理 17:08 行标题已显示，并带「作者修改过视频信息」标记（`ch04-sph-verify30-list.png`）
- 接口：`svrkit/MmFinderAssistantBroker/finderModFeed` → `errCode:0 / request successful`，UI 提示「修改成功」
- **平台硬限制**：已发布作品的「修改描述和封面」是查找替换，总预算 **20 字**、**仅可修改一次、不可撤回**、修改记录会展示在视频上。草稿里 413 字完整 desc 不可能补上（411/200/120/60 字均被拒），本次用掉了唯一一次额度。
- 教训：长描述与话题标签必须在**发表前**写进发布表单。
- 链路：宿主页 `/platform/post/coverEdit` → 匿名 iframe `/micro/content/post/coverEdit` → 选中文字 → 弹窗「修改」→「修改为」输入 →「修改」→ 底部「完成」→「确认修改」
- 脚本/证据：`ch04_sph_edit26.py`、`ch04-sph-edit26-{log.txt,reqs.json}`、`ch04_sph_verify30.py`、`ch04-sph-verify30-{log.txt,api.json,list.png}`
- 结果：`C:\Users\zhugu\yuzhe-publish\ch04-sph-final-result.json`（success=true）


## densify v2 要点（已发布用此版）
- 修 hold 插值泄漏；233 beats；huashu 16 slots；vs_auto 万能钥匙 vs 四道闸
