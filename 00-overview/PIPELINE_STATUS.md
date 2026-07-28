# Pipeline B+C 自動執行狀態

> 由 `scripts/auto-pipeline.py` 自動產生，勿手改。

- 更新時間：2026-07-28 22:43:09 +0800
- 佇列 tier：**核心**
- 進度：**185 / 518** 已翻譯+標籤
- 目前處理：`(本輪完成)`
- P0 尚未完整翻譯：11 部
- 一般失敗待重試：57 部 — eyrbyggja-saga-on, plato-phaedo-el, yajnavalkya-smrti, plato-timaeus-el, numbers, deuteronomy, plato-phaedrus-el, samaveda, ovid-fasti-la, homeric-hymns-el
- 已阻塞待人工處理：11 部 — avesta-sbe31-ae, quran, jain-uttaradhyayana-pkt, sutta-nipata, exodus, psalms, tain-bo-cuailnge-ga, plato-republic-el, book-of-mormon-1830, homer-greek
- M3 執行狀態：**waiting_quota** — `kitab-i-iqan-ighan` (translate chunk 79/92)
- 限制偵測：2026-07-28T22:41:24.334397+08:00；下次重試：2026-07-28T23:00:15+08:00
- 最後錯誤：`5h=5% (reserve 5%) weekly=35% (reserve 2%)`


流程：每部 `01-translation.md`（經文式翻譯）→ `semantic_tags`/`psych_tags`/`keywords` 回填 `meta.json`
→ 每批重生三份獨立反向索引 → commit + push。
