# Pipeline B+C 自動執行狀態

> 由 `scripts/auto-pipeline.py` 自動產生，勿手改。

- 更新時間：2026-10-02 05:14:28 +0800
- 佇列 tier：**核心**
- 進度：**488 / 518** 已翻譯+標籤
- 目前處理：`carmina-gadelica-1`
- P0 尚未完整翻譯：0 部
- 一般失敗待重試：30 部 — bud-lankavatara-sa, apuleius-metamorphoses-la, augustine-confessiones-la, an4-fours, ovid-metamorphoses-la, chandogya-upanishad, markandeya-purana, aristotle-nicomachean-ethics-el, bud-lalitavistara-sa, apollodorus-bibliotheca-el
- 已阻塞待人工處理：0 部
- M3 執行狀態：**running** — `carmina-gadelica-1` (tag)


流程：每部 `01-translation.md`（經文式翻譯）→ `semantic_tags`/`psych_tags`/`keywords` 回填 `meta.json`
→ 每批重生三份獨立反向索引 → commit + push。
