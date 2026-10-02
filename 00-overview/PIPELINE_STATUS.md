# Pipeline B+C 自動執行狀態

> 由 `scripts/auto-pipeline.py` 自動產生，勿手改。

- 更新時間：2026-10-02 21:37:30 +0800
- 佇列 tier：**核心**
- 進度：**505 / 518** 已翻譯+標籤
- 目前處理：`(本輪完成)`
- P0 尚未完整翻譯：0 部
- 一般失敗待重試：13 部 — shiva-purana, kn-jataka, rigveda, brahma-purana, valmiki-ramayana, majjhima-nikaya, mahabharata, gnostics-and-their-remains, science-and-health-1906, mahabharata-ganguli
- 已阻塞待人工處理：0 部
- M3 執行狀態：**waiting_provider** — `kn-jataka` (translate chunk 219/301)
- 限制偵測：2026-10-02T21:35:45.278896+08:00；下次重試：2026-10-02T21:40:45.278896+08:00
- 最後錯誤：`http 529: {"type":"error","error":{"type":"overloaded_error","message":"overloaded_error (529)"},"request_id":"070ee62f1ca7bb281718fdea66459357"}`


流程：每部 `01-translation.md`（經文式翻譯）→ `semantic_tags`/`psych_tags`/`keywords` 回填 `meta.json`
→ 每批重生三份獨立反向索引 → commit + push。
