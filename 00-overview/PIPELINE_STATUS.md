# Pipeline B+C 自動執行狀態

> 由 `scripts/auto-pipeline.py` 自動產生，勿手改。

- 更新時間：2026-10-09 21:16:34 +0800
- 佇列 tier：**標籤補齊**
- 進度：**2320 / 2382** 已完成雙標籤
- 本輪任務：雙標籤
- 目前處理：`(等待供應商恢復)`
- P0 尚未完整翻譯：0 部
- 一般失敗待重試：0 部
- 已阻塞待人工處理：57 部 — cbeta-T19n1021, cbeta-T55n2168B, cbeta-T18n0858, cbeta-T55n2174B, cbeta-T17n0806, cbeta-T21n1213, cbeta-X02n0184, cbeta-T32n1677, cbeta-T55n2171, cbeta-T20n1196
- M3 執行狀態：**waiting_provider** — `cbeta-T53n2122` (tag chunk 198/448)
- 限制偵測：2026-10-09T21:16:33.148673+08:00；下次重試：2026-10-09T21:21:33.148673+08:00
- 最後錯誤：`http 529: {"type":"error","error":{"type":"overloaded_error","message":"overloaded_error (529)"},"request_id":"07181c30f6e2585f54e1cc61fcd54e51"}`


流程：選定來源文本 → `semantic_tags`/`psych_tags`/`keywords` 回填 `meta.json`；翻譯完成度獨立計算。
→ 每批重生三份獨立反向索引 → commit + push。
