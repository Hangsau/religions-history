# Pipeline B+C 自動執行狀態

> 由 `scripts/auto-pipeline.py` 自動產生，勿手改。

- 更新時間：2026-07-29 12:05:38 +0800
- 佇列 tier：**核心**
- 進度：**187 / 518** 已翻譯+標籤
- 目前處理：`(本輪完成)`
- P0 尚未完整翻譯：9 部
- 一般失敗待重試：55 部 — eyrbyggja-saga-on, plato-phaedo-el, yajnavalkya-smrti, plato-timaeus-el, numbers, deuteronomy, plato-phaedrus-el, samaveda, ovid-fasti-la, homeric-hymns-el
- 已阻塞待人工處理：11 部 — avesta-sbe31-ae, quran, jain-uttaradhyayana-pkt, sutta-nipata, exodus, psalms, tain-bo-cuailnge-ga, plato-republic-el, book-of-mormon-1830, homer-greek
- M3 執行狀態：**waiting_provider** — `egyptian-book-of-dead` (translate chunk 162/345)
- 限制偵測：2026-07-29T12:03:49.014470+08:00；下次重試：2026-07-29T12:08:49.014470+08:00
- 最後錯誤：`timeout after 360s`


流程：每部 `01-translation.md`（經文式翻譯）→ `semantic_tags`/`psych_tags`/`keywords` 回填 `meta.json`
→ 每批重生三份獨立反向索引 → commit + push。
