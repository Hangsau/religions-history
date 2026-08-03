# Pipeline B+C 自動執行狀態

> 由 `scripts/auto-pipeline.py` 自動產生，勿手改。

- 更新時間：2026-08-04 01:52:10 +0800
- 佇列 tier：**核心**
- 進度：**196 / 518** 已翻譯+標籤
- 目前處理：`(本輪完成)`
- P0 尚未完整翻譯：8 部
- 一般失敗待重試：43 部 — eyrbyggja-saga-on, plato-phaedo-el, yajnavalkya-smrti, plato-timaeus-el, numbers, deuteronomy, samaveda, ovid-fasti-la, homeric-hymns-el, chronicles-1
- 已阻塞待人工處理：14 部 — avesta-sbe31-ae, quran, jain-uttaradhyayana-pkt, sutta-nipata, an9-nines, mimamsa-sutra-jaimini, exodus, psalms, tain-bo-cuailnge-ga, plato-republic-el
- M3 執行狀態：**waiting_provider** — `chronicles-1` (translate chunk 7/51)
- 限制偵測：2026-08-04T01:50:24.418942+08:00；下次重試：2026-08-04T01:55:24.418942+08:00
- 最後錯誤：`timeout after 360s`


流程：每部 `01-translation.md`（經文式翻譯）→ `semantic_tags`/`psych_tags`/`keywords` 回填 `meta.json`
→ 每批重生三份獨立反向索引 → commit + push。
