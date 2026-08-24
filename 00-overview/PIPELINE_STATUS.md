# Pipeline B+C 自動執行狀態

> 由 `scripts/auto-pipeline.py` 自動產生，勿手改。

- 更新時間：2026-08-24 14:00:35 +0800
- 佇列 tier：**核心**
- 進度：**223 / 518** 已翻譯+標籤
- 目前處理：`huangdi-neijing`
- P0 尚未完整翻譯：8 部
- 一般失敗待重試：2 部 — sibylline-oracles-el, ovid-metamorphoses-la
- 已阻塞待人工處理：33 部 — eyrbyggja-saga-on, yajnavalkya-smrti, avesta-sbe31-ae, quran, numbers, samaveda, ovid-fasti-la, jain-uttaradhyayana-pkt, sutta-nipata, chronicles-1
- M3 執行狀態：**running** — `ovid-metamorphoses-la` (translate)


流程：每部 `01-translation.md`（經文式翻譯）→ `semantic_tags`/`psych_tags`/`keywords` 回填 `meta.json`
→ 每批重生三份獨立反向索引 → commit + push。
