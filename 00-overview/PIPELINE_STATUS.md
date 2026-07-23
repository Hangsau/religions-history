# Pipeline B+C 自動執行狀態

> 由 `scripts/auto-pipeline.py` 自動產生，勿手改。

- 更新時間：2026-07-23 09:19:34 +0800
- 佇列 tier：**核心**
- 進度：**179 / 518** 已翻譯+標籤
- 目前處理：`sutta-nipata`
- P0 尚未完整翻譯：19 部
- 一般失敗待重試：74 部 — eyrbyggja-saga-on, plato-phaedo-el, yajnavalkya-smrti, avesta-sbe31-ae, plato-timaeus-el, quran, numbers, deuteronomy, plato-phaedrus-el, samaveda
- 已阻塞待人工處理：0 部
- M3 執行狀態：**waiting_quota** — `sutta-nipata` (translate chunk 4/78)
- 限制偵測：2026-07-23T09:19:34.290958+08:00；下次重試：2026-07-27T08:00:15+08:00
- 最後錯誤：`proactive quota reserve: 5h=81% (reserve 10%) weekly=10% (reserve 10%)`


流程：每部 `01-translation.md`（經文式翻譯）→ `semantic_tags`/`psych_tags`/`keywords` 回填 `meta.json`
→ 每批重生三份獨立反向索引 → commit + push。
