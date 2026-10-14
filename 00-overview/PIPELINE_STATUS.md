# Pipeline B+C 自動執行狀態

> 由 `scripts/auto-pipeline.py` 自動產生，勿手改。

- 更新時間：2026-10-14 12:47:03 +0800
- 佇列 tier：**標籤補齊**
- 進度：**748 / 3186** 已完成雙標籤
- 本輪任務：雙標籤
- 目前處理：`cbeta-T14n0451`
- P0 尚未完整翻譯：0 部
- 一般失敗待重試：0 部
- 已阻塞待人工處理：4 部 — book-of-changes, madhyamagama, mahabharata, cbeta-T15n0603
- M3 執行狀態：**running** — `cbeta-T14n0451` (tag)


流程：選定來源文本 → `semantic_tags`/`psych_tags`/`keywords` 回填 `meta.json`；翻譯完成度獨立計算。
→ 每批重生三份獨立反向索引 → commit + push。
