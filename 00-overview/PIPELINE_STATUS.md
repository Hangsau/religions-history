# Pipeline B+C 自動執行狀態

> 由 `scripts/auto-pipeline.py` 自動產生，勿手改。

- 更新時間：2026-07-18 08:45:04 +0800
- 佇列 tier：**核心**
- 進度：**262 / 518** 已翻譯+標籤
- 目前處理：`mimamsa-sutra-jaimini`
- 失敗待重試：6 部 — eyrbyggja-saga-on, plato-phaedo-el, yajnavalkya-smrti, avesta-sbe31-ae, mozi, plato-timaeus-el


流程：每部 `01-translation.md`（經文式翻譯）→ `semantic_tags`/`keywords` 回填 `meta.json`
→ 每批重生 `tag-index.json`/`keyword-index.json` → commit + push。
