# Pipeline B+C 自動執行狀態

> 由 `scripts/auto-pipeline.py` 自動產生，勿手改。

- 更新時間：2026-10-08 04:23:49 +0800
- 佇列 tier：**標籤補齊**
- 進度：**585 / 2382** 已完成雙標籤
- 本輪任務：雙標籤
- 目前處理：`cbeta-T32n1651`
- P0 尚未完整翻譯：0 部
- 一般失敗待重試：5 部 — cbeta-T18n0881, cbeta-T32n1658, cbeta-T19n1005B, cbeta-T21n1298, cbeta-T18n0864B
- 已阻塞待人工處理：28 部 — cbeta-T19n1021, cbeta-T55n2168B, cbeta-T18n0858, cbeta-T55n2174B, cbeta-T17n0806, cbeta-T21n1213, cbeta-X02n0184, cbeta-T32n1677, cbeta-T55n2171, cbeta-T20n1196
- M3 執行狀態：**running** — `cbeta-T32n1651` (tag)


流程：選定來源文本 → `semantic_tags`/`psych_tags`/`keywords` 回填 `meta.json`；翻譯完成度獨立計算。
→ 每批重生三份獨立反向索引 → commit + push。
