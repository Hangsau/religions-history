# Pipeline B+C 自動執行狀態

> 由 `scripts/auto-pipeline.py` 自動產生，勿手改。

- 更新時間：2026-10-02 07:18:09 +0800
- 佇列 tier：**核心**
- 進度：**493 / 518** 已翻譯+標籤
- 目前處理：`ovid-metamorphoses-la`
- P0 尚未完整翻譯：0 部
- 一般失敗待重試：25 部 — chandogya-upanishad, markandeya-purana, aristotle-nicomachean-ethics-el, bud-lalitavistara-sa, apollodorus-bibliotheca-el, abhinavagupta-tantraloka, kn-milindapanha, kurma-purana, vishnu-purana, bud-astasahasrika-prajnaparamita-sa
- 已阻塞待人工處理：0 部
- M3 執行狀態：**running** — `ovid-metamorphoses-la` (tag)


流程：每部 `01-translation.md`（經文式翻譯）→ `semantic_tags`/`psych_tags`/`keywords` 回填 `meta.json`
→ 每批重生三份獨立反向索引 → commit + push。
