# Pipeline B+C 自動執行狀態

> 由 `scripts/auto-pipeline.py` 自動產生，勿手改。

- 更新時間：2026-10-01 20:35:52 +0800
- 佇列 tier：**核心**
- 進度：**473 / 518** 已翻譯+標籤
- 目前處理：`plato-republic-el`
- P0 尚未完整翻譯：3 部
- 一般失敗待重試：45 部 — eyrbyggja-saga-on, yajnavalkya-smrti, quran, samaveda, ovid-fasti-la, chronicles-1, book-of-mormon-1830, homer-greek, snorra-edda-on, avesta-sbe23-ae
- 已阻塞待人工處理：0 部
- M3 執行狀態：**running** — `plato-republic-el` (tag)


流程：每部 `01-translation.md`（經文式翻譯）→ `semantic_tags`/`psych_tags`/`keywords` 回填 `meta.json`
→ 每批重生三份獨立反向索引 → commit + push。
