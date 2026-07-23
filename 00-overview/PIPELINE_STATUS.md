# Pipeline B+C 自動執行狀態

> 由 `scripts/auto-pipeline.py` 自動產生，勿手改。

- 更新時間：2026-07-23 14:45:25 +0800
- 佇列 tier：**核心**
- 進度：**180 / 518** 已翻譯+標籤
- 目前處理：`(本輪完成)`
- P0 尚未完整翻譯：19 部
- 一般失敗待重試：71 部 — eyrbyggja-saga-on, plato-phaedo-el, yajnavalkya-smrti, avesta-sbe31-ae, plato-timaeus-el, quran, numbers, deuteronomy, plato-phaedrus-el, samaveda
- 已阻塞待人工處理：2 部 — jain-uttaradhyayana-pkt, sutta-nipata
- M3 執行狀態：**waiting_provider** — `avesta-sbe31-ae` (translate chunk 13/89)
- 限制偵測：2026-07-23T14:43:37.618333+08:00；下次重試：2026-07-23T14:48:37.618333+08:00
- 最後錯誤：`timeout after 360s`


流程：每部 `01-translation.md`（經文式翻譯）→ `semantic_tags`/`psych_tags`/`keywords` 回填 `meta.json`
→ 每批重生三份獨立反向索引 → commit + push。
