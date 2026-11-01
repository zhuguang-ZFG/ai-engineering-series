# 第 01 章口播音色锁定｜驭者·Agent Harness

> 状态：试音已出，**用户已确认 2026-10-27**后再批量合成全片配音。  
> 试音文件（本机，未进 git）：  
> - video/ch01/assets/voice-sample-long.mp3（长讲开场约 80 汉字样段，约 29s）  
> - video/ch01/assets/voice-sample-short.mp3（短片口播连贯稿全文，约 28s）

---

## 选定音色

| 项 | 值 |
|----|-----|
| **引擎** | edge-tts（Microsoft Edge neural） |
| **voice id** | zh-CN-YunyangNeural |
| **rate** | -10% |
| **pitch** | -5Hz |
| **语种/性别** | zh-CN · 男声 |
| **官方定位** | News · Professional, Reliable |
| **选用理由** | 新闻播报底子，偏沉稳、可靠，适合 15–20 分钟技术长讲与短片机制口播；略降速/降调后更稳，不飘不躁。 |

---

## 候选对比（同文案、同为沉稳向微调）

| voice id | rate / pitch | 观感 | 结论 |
|----------|--------------|------|------|
| zh-CN-YunyangNeural | -10% / -5Hz | 专业新闻感，稳 | **选用** |
| zh-CN-YunxiNeural | -12% / -8Hz | 小说/阳光活泼底 | **弃用** |
| zh-CN-YunjianNeural | -12% / -8Hz | 体育/激情底，偏冲 | 备选未用 |

对比样音（仅本机参考）：compare-Yunyang-long.mp3 / compare-Yunxi-long.mp3 / compare-Yunjian-long.mp3。

### 弃用理由（相对 Yunxi）

zh-CN-YunxiNeural 官方定位为 Novel · Lively, Sunshine，即便降速降调，仍偏轻快、带「阳光感」，不适合本系列「沉稳男声」技术讲解气质；故弃用，锁定 Yunyang。

---

## 试音文案来源

- **长讲样段**：docs/video/ch01/long-script.md 开场口播前约 80 个汉字（落在句号处略延长），见 video/ch01/assets/sample-long.txt。
- **短片样段**：docs/video/ch01/short-script.md「口播连贯稿（直接给 TTS）」全文，见 video/ch01/assets/sample-short.txt。

---

## 使用约定

- 未收到用户对试音的确认前，**不得**合成第 01 章全片口播。
- 确认后：长讲按 long-script.md 分镜切段合成；短片按连贯稿一次合成；字幕与成片流水线另任务处理。
- 大体积 mp3 默认不入库（见 .gitignore）；voice.md 与样本文本可入库。
