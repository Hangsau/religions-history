# Pipeline B+C 自動執行狀態

> 由 `scripts/auto-pipeline.py` 自動產生，勿手改。

- 更新時間：2026-08-18 13:49:01 +0800
- 佇列 tier：**核心**
- 進度：**220 / 518** 已翻譯+標籤
- 目前處理：`apuleius-metamorphoses-la`
- P0 尚未完整翻譯：8 部
- 一般失敗待重試：4 部 — apuleius-metamorphoses-la, an5-fives, virgil-aeneid-la, sibylline-oracles-el
- 已阻塞待人工處理：30 部 — eyrbyggja-saga-on, yajnavalkya-smrti, avesta-sbe31-ae, quran, numbers, samaveda, ovid-fasti-la, jain-uttaradhyayana-pkt, sutta-nipata, chronicles-1
- M3 執行狀態：**waiting_provider** — `apuleius-metamorphoses-la` (translate chunk 37/159)
- 限制偵測：2026-08-18T13:49:01.619881+08:00；下次重試：2026-08-18T13:54:01.619881+08:00
- 最後錯誤：`timeout after 360s`


流程：每部 `01-translation.md`（經文式翻譯）→ `semantic_tags`/`psych_tags`/`keywords` 回填 `meta.json`
→ 每批重生三份獨立反向索引 → commit + push。
