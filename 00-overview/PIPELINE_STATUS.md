# Pipeline B+C 自動執行狀態

> 由 `scripts/auto-pipeline.py` 自動產生，勿手改。

- 更新時間：2026-10-02 14:05:59 +0800
- 佇列 tier：**核心**
- 進度：**500 / 518** 已翻譯+標籤
- 目前處理：`(本輪完成)`
- P0 尚未完整翻譯：0 部
- 一般失敗待重試：18 部 — kurma-purana, vishnu-purana, bud-astasahasrika-prajnaparamita-sa, aristotle-metaphysics-el, linga-purana, shiva-purana, kn-jataka, rigveda, brahma-purana, valmiki-ramayana
- 已阻塞待人工處理：0 部
- M3 執行狀態：**running** — `kurma-purana` (translate)


流程：每部 `01-translation.md`（經文式翻譯）→ `semantic_tags`/`psych_tags`/`keywords` 回填 `meta.json`
→ 每批重生三份獨立反向索引 → commit + push。
