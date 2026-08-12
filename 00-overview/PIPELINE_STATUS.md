# Pipeline B+C 自動執行狀態

> 由 `scripts/auto-pipeline.py` 自動產生，勿手改。

- 更新時間：2026-08-12 12:21:31 +0800
- 佇列 tier：**核心**
- 進度：**215 / 518** 已翻譯+標籤
- 目前處理：`(本輪完成)`
- P0 尚未完整翻譯：8 部
- 一般失敗待重試：10 部 — egils-saga-on, carmina-gadelica-1, an3-threes, snorra-edda-is, bud-lankavatara-sa, manu-smrti, xenophon-memorabilia-el, apuleius-metamorphoses-la, an5-fives, virgil-aeneid-la
- 已阻塞待人工處理：28 部 — eyrbyggja-saga-on, yajnavalkya-smrti, avesta-sbe31-ae, quran, numbers, samaveda, ovid-fasti-la, jain-uttaradhyayana-pkt, sutta-nipata, chronicles-1
- M3 執行狀態：**waiting_provider** — `egils-saga-on` (translate chunk 44/120)
- 限制偵測：2026-08-12T12:19:36.004328+08:00；下次重試：2026-08-12T12:24:36.004328+08:00
- 最後錯誤：`timeout after 360s`


流程：每部 `01-translation.md`（經文式翻譯）→ `semantic_tags`/`psych_tags`/`keywords` 回填 `meta.json`
→ 每批重生三份獨立反向索引 → commit + push。
