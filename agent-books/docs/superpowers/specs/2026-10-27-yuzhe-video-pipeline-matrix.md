# 驭者视频流水线选型（矩阵落地）

日期：2026-10-27  
依据：用户选型矩阵 + 规格 `2026-10-27-yuzhe-video-series-design.md`  
状态：已确认，自 Task 4 起生效

## 对号入座

| 业务场景 | 选用 | 备注 |
|----------|------|------|
| B 站长讲（长文→边画边讲） | sweety-handdraw-video | 主轴 |
| 底层代码视频框架 | HyperFrames | HTML/CSS/JS，Apache-2.0 |
| 讲解语法 / 艺术动效 | huashu-art-motion | 嵌于长讲段落 |
| 短片快出片 + Opus 风格钩子 | lemo-opuscar | 抖音/小红书主轴 |
| 极速短片备选 | explainroo | 要更快时切换 |
| 镜头配方补强 | video-shotcraft | 不够用时 |
| 粗剪后精修 | OpenChatCut / BaoCut | 按需 |
| Git 历史可视化彩蛋 | Raven | 可选 |
| 口播 | edge-tts zh-CN-YunyangNeural rate -10% pitch -5Hz | 用户已确认；不用数字人 |

## 不变

- 账号小电讲电路；系列「驭者·Agent Harness」
- Task 1–3 脚本与音色锁定保留
- 样片先行第 01 章；过片前不发布