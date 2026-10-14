# Pipeline B+C 自動執行狀態

> 由 `scripts/auto-pipeline.py` 自動產生，勿手改。

- 更新時間：2026-10-15 03:26:10 +0800
- 佇列 tier：**標籤補齊**
- 進度：**1379 / 3186** 已完成雙標籤
- 本輪任務：雙標籤
- 目前處理：`(等待供應商恢復)`
- P0 尚未完整翻譯：0 部
- 一般失敗待重試：0 部
- 已阻塞待人工處理：7 部 — book-of-changes, madhyamagama, mahabharata, cbeta-T15n0603, cbeta-T17n0817, cbeta-T14n0481, cbeta-T15n0624
- M3 執行狀態：**waiting_quota** — `cbeta-T21n1341` (tag chunk 24/56)
- 限制偵測：2026-10-15T03:26:08.240440+08:00；下次重試：2026-10-15T04:00:15+08:00
- 最後錯誤：`proactive quota reserve: 5h=5% (reserve 5%) weekly=39% (reserve 2%)`


流程：選定來源文本 → `semantic_tags`/`psych_tags`/`keywords` 回填 `meta.json`；翻譯完成度獨立計算。
→ 每批重生三份獨立反向索引 → commit + push。
