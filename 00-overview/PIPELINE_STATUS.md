# Pipeline B+C 自動執行狀態

> 由 `scripts/auto-pipeline.py` 自動產生，勿手改。

- 更新時間：2026-07-20 12:23:55 +0800
- 佇列 tier：**核心**
- 進度：**25 / 518** 已翻譯+標籤
- 目前處理：`doctrine-of-the-mean`
- 失敗待重試：32 部 — eyrbyggja-saga-on, plato-phaedo-el, yajnavalkya-smrti, avesta-sbe31-ae, mozi, plato-timaeus-el, quran, numbers, deuteronomy, plato-phaedrus-el
- M3 執行狀態：**waiting_quota** — `lamentations` (translate chunk 5/8)
- 限制偵測：2026-07-20T12:23:47.426992+08:00；下次重試：2026-07-20T12:28:47.426992+08:00
- 最後錯誤：`timeout after 360s`


流程：每部 `01-translation.md`（經文式翻譯）→ `semantic_tags`/`psych_tags`/`keywords` 回填 `meta.json`
→ 每批重生三份獨立反向索引 → commit + push。
