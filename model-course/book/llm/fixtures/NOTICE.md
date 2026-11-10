# 分词与练习数据来源

`tokens.json` 和 `legacy-tokenization.json` 由 `scripts/llm/export-token-fixtures.mjs` 使用 `js-tiktoken@1.0.21` 的 `cl100k_base` 和 `o200k_base` 数据生成。前者保存四组课程输入，后者保存旧章的原始混合输入。原始 rank 字符串的 SHA-256 存于快照；复算会同时校验原文与 token 字节的无损还原。

js-tiktoken（JavaScript port of tiktoken）使用 MIT 许可，项目来源为 https://github.com/dqbd/tiktoken 。完整许可见本目录 `js-tiktoken-LICENSE`；快照只包含教学输入涉及的 token ID 与字节，没有完整词表。它不证明任何在线聊天产品当前使用的编码或内部状态。

`generation.json`、`materials.json` 和其中的语句是课程自建教学数据，不是线上模型输出，也不是现实活动通知。材料核验的事实字段由作者标注，页面始终说明这一点。
