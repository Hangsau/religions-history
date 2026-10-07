# Pipeline B+C 自動執行狀態

> 由 `scripts/auto-pipeline.py` 自動產生，勿手改。

- 更新時間：2026-10-08 01:28:35 +0800
- 佇列 tier：**標籤補齊**
- 進度：**225 / 2382** 已完成雙標籤
- 本輪任務：雙標籤
- 目前處理：`cbeta-T14n0469`
- P0 尚未完整翻譯：0 部
- 一般失敗待重試：10 部 — cbeta-T32n1684, cbeta-X12n0273, cbeta-T20n1156B, cbeta-T55n2166, cbeta-T21n1241, cbeta-T55n2162, cbeta-T19n0941, cbeta-T20n1176, cbeta-T21n1296, cbeta-T01n0089
- 已阻塞待人工處理：10 部 — cbeta-T19n1021, cbeta-T55n2168B, cbeta-T18n0858, cbeta-T55n2174B, cbeta-T17n0806, cbeta-T21n1213, cbeta-X02n0184, cbeta-T32n1677, cbeta-T55n2171, cbeta-T20n1196
- M3 執行狀態：**running** — `cbeta-T14n0469` (tag)


流程：選定來源文本 → `semantic_tags`/`psych_tags`/`keywords` 回填 `meta.json`；翻譯完成度獨立計算。
→ 每批重生三份獨立反向索引 → commit + push。
