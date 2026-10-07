# Pipeline B+C 自動執行狀態

> 由 `scripts/auto-pipeline.py` 自動產生，勿手改。

- 更新時間：2026-10-07 22:23:48 +0800
- 佇列 tier：**標籤補齊**
- 進度：**5 / 2382** 已完成雙標籤
- 本輪任務：雙標籤
- 目前處理：`neiguan-jing`
- P0 尚未完整翻譯：0 部
- 一般失敗待重試：0 部
- 已阻塞待人工處理：0 部
- M3 執行狀態：**running** — `neiguan-jing` (tag)


流程：選定來源文本 → `semantic_tags`/`psych_tags`/`keywords` 回填 `meta.json`；翻譯完成度獨立計算。
→ 每批重生三份獨立反向索引 → commit + push。
