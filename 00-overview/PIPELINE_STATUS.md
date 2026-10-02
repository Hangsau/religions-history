# Pipeline B+C 自動執行狀態

> 由 `scripts/auto-pipeline.py` 自動產生，勿手改。

- 更新時間：2026-10-02 22:04:15 +0800
- 佇列 tier：**核心**
- 進度：**506 / 518** 已翻譯+標籤
- 目前處理：`(本輪完成)`
- P0 尚未完整翻譯：0 部
- 一般失敗待重試：12 部 — kn-jataka, rigveda, brahma-purana, valmiki-ramayana, majjhima-nikaya, mahabharata, gnostics-and-their-remains, science-and-health-1906, mahabharata-ganguli, guru-granth-sahib-st
- 已阻塞待人工處理：0 部
- M3 執行狀態：**waiting_provider** — `kn-jataka` (translate chunk 229/301)
- 限制偵測：2026-10-02T22:02:29.981468+08:00；下次重試：2026-10-02T22:07:29.981468+08:00
- 最後錯誤：`http 529: {"type":"error","error":{"type":"overloaded_error","message":"overloaded_error (529)"},"request_id":"070eec75a129810721663d459e56b4ba"}`


流程：每部 `01-translation.md`（經文式翻譯）→ `semantic_tags`/`psych_tags`/`keywords` 回填 `meta.json`
→ 每批重生三份獨立反向索引 → commit + push。
