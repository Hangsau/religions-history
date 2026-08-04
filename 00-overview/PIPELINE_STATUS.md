# Pipeline B+C 自動執行狀態

> 由 `scripts/auto-pipeline.py` 自動產生，勿手改。

- 更新時間：2026-08-04 15:22:52 +0800
- 佇列 tier：**核心**
- 進度：**201 / 518** 已翻譯+標籤
- 目前處理：`(本輪完成)`
- P0 尚未完整翻譯：8 部
- 一般失敗待重試：36 部 — eyrbyggja-saga-on, plato-phaedo-el, yajnavalkya-smrti, plato-timaeus-el, numbers, deuteronomy, samaveda, cicero-de-natura-deorum-la, chronicles-2, an6-sixes
- 已阻塞待人工處理：16 部 — avesta-sbe31-ae, quran, ovid-fasti-la, jain-uttaradhyayana-pkt, sutta-nipata, chronicles-1, an9-nines, mimamsa-sutra-jaimini, exodus, psalms
- M3 執行狀態：**waiting_provider** — `cicero-de-natura-deorum-la` (translate chunk 19/81)
- 限制偵測：2026-08-04T15:21:07.408194+08:00；下次重試：2026-08-04T15:26:07.408194+08:00
- 最後錯誤：`timeout after 360s`


流程：每部 `01-translation.md`（經文式翻譯）→ `semantic_tags`/`psych_tags`/`keywords` 回填 `meta.json`
→ 每批重生三份獨立反向索引 → commit + push。
