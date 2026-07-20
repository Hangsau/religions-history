# Pipeline B+C 自動執行狀態

> 由 `scripts/auto-pipeline.py` 自動產生，勿手改。

- 更新時間：2026-07-20 13:03:35 +0800
- 佇列 tier：**核心**
- 進度：**1 / 1** 已翻譯+標籤
- 目前處理：`heart-sutra-kumarajiva`
- 失敗待重試：31 部 — eyrbyggja-saga-on, plato-phaedo-el, yajnavalkya-smrti, avesta-sbe31-ae, mozi, plato-timaeus-el, quran, numbers, deuteronomy, plato-phaedrus-el
- M3 執行狀態：**running** — `samkhya-karika` (tag)


流程：每部 `01-translation.md`（經文式翻譯）→ `semantic_tags`/`psych_tags`/`keywords` 回填 `meta.json`
→ 每批重生三份獨立反向索引 → commit + push。
