# Pipeline B+C 自動執行狀態

> 由 `scripts/auto-pipeline.py` 自動產生，勿手改。

- 更新時間：2026-10-11 23:21:34 +0800
- 佇列 tier：**標籤補齊**
- 進度：**2356 / 2382** 已完成雙標籤
- 本輪任務：雙標籤
- 目前處理：`cbeta-T19n1005B`
- P0 尚未完整翻譯：0 部
- 一般失敗待重試：13 部 — cbeta-T21n1298, cbeta-T18n0864B, cbeta-T20n1068, cbeta-T21n1209, cbeta-T55n2147, cbeta-T24n1449, cbeta-T14n0473, cbeta-T20n1194, cbeta-T16n0662, cbeta-T12n0367
- 已阻塞待人工處理：13 部 — cbeta-T02n0113, cbeta-T17n0735, cbeta-T28n1557, cbeta-T15n0603, cbeta-T17n0817, cbeta-T33n1694, cbeta-T14n0481, cbeta-T15n0624, cbeta-X12n0279, cbeta-T46n1911
- M3 執行狀態：**running** — `cbeta-T19n1005B` (tag)


流程：選定來源文本 → `semantic_tags`/`psych_tags`/`keywords` 回填 `meta.json`；翻譯完成度獨立計算。
→ 每批重生三份獨立反向索引 → commit + push。
