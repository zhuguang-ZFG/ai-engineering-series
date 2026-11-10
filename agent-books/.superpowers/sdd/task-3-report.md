# Task 3 Report — 选定沉稳男声并出试音

**Status:** DONE (awaiting user voice confirmation before full-film TTS)  
**BASE:** fbf9d6cf88c0c5cb141f8eff468d7bd45385e7b0  
**Commit:** 4b8068f75c512239f225b1403f1aebe2cb3925e4 — docs(video): lock ch01 male narration voice settings  
**Machine:** ca3e8acb-383a-46c7-968d-a39e42832327

## What was done

1. Ensured video/ch01/assets/ exists.
2. Extracted sample texts:
   - Long: first ~80 Chinese spoken chars from docs/video/ch01/long-script.md (trimmed to sentence end → 101 CN chars) → video/ch01/assets/sample-long.txt
   - Short: full continuous VO under「口播连贯稿（直接给 TTS）」→ video/ch01/assets/sample-short.txt
3. Compared 3 zh-CN male edge-tts voices with 沉稳-tuned rate/pitch:
   - zh-CN-YunxiNeural @ -12% / -8Hz
   - zh-CN-YunjianNeural @ -12% / -8Hz
   - zh-CN-YunyangNeural @ -10% / -5Hz
4. Rendered locked samples:
   - video/ch01/assets/voice-sample-long.mp3 (~29.2s, 175KB)
   - video/ch01/assets/voice-sample-short.mp3 (~27.6s, 166KB)
5. Wrote docs/video/ch01/voice.md with chosen settings + rejection reason.
6. Updated .gitignore for video/**/*.mp3|wav|mp4 and video/**/out/ so binaries stay on disk.
7. **Did NOT** synthesize full long-film VO.

## Chosen voice

| Field | Value |
|-------|-------|
| voice id | zh-CN-YunyangNeural |
| rate | -10% |
| pitch | -5Hz |
| why | News / Professional / Reliable — best match for 沉稳 tech narration |

**Rejected (primary):** zh-CN-YunxiNeural — official Lively/Sunshine novel voice; still too light even after slowing/lowering pitch.

## Paths for user listen

- D:\Users\claude\claude-code-book-main\video\ch01\assets\voice-sample-long.mp3
- D:\Users\claude\claude-code-book-main\video\ch01\assets\voice-sample-short.mp3
- Compare refs: compare-Yunyang-long.mp3, compare-Yunxi-long.mp3, compare-Yunjian-long.mp3

## Next

User confirms or rejects voice in voice.md before any full-film TTS (Task later).
