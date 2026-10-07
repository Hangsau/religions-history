# Pipeline B+C 自動執行狀態

> 由 `scripts/auto-pipeline.py` 自動產生，勿手改。

- 更新時間：2026-10-07 11:17:56 +0800
- 佇列 tier：**核心**
- 進度：**517 / 518** 已翻譯+標籤
- 目前處理：`mahabharata`
- P0 尚未完整翻譯：0 部
- 一般失敗待重試：0 部
- 已阻塞待人工處理：0 部
- M3 執行狀態：**running** — `mahabharata` (tag)
- 標籤待審段落：1 段（525）；內容遭拒，未計入完成


流程：每部 `01-translation.md`（經文式翻譯）→ `semantic_tags`/`psych_tags`/`keywords` 回填 `meta.json`
→ 每批重生三份獨立反向索引 → commit + push。
