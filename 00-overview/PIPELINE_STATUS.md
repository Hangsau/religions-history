# Pipeline B+C 自動執行狀態

> 由 `scripts/auto-pipeline.py` 自動產生，勿手改。

- 更新時間：2026-10-13 10:00:56 +0800
- 佇列 tier：**標籤補齊**
- 進度：**388 / 3186** 已完成雙標籤
- 本輪任務：雙標籤
- 目前處理：`(等待供應商恢復)`
- P0 尚未完整翻譯：0 部
- 一般失敗待重試：0 部
- 已阻塞待人工處理：1 部 — book-of-changes
- M3 執行狀態：**waiting_provider** — `mabinogion-st` (tag chunk 68/153)
- 限制偵測：2026-10-13T10:00:54.358944+08:00；下次重試：2026-10-13T10:05:54.358944+08:00
- 最後錯誤：`http 529: {"type":"error","error":{"type":"overloaded_error","message":"overloaded_error (529)"},"request_id":"071cc3d5f68a9997e3d9f34543e084b4"}`


流程：選定來源文本 → `semantic_tags`/`psych_tags`/`keywords` 回填 `meta.json`；翻譯完成度獨立計算。
→ 每批重生三份獨立反向索引 → commit + push。
