# Pipeline B+C 自動執行狀態

> 由 `scripts/auto-pipeline.py` 自動產生，勿手改。

- 更新時間：2026-08-05 04:50:00 +0800
- 佇列 tier：**核心**
- 進度：**205 / 518** 已翻譯+標籤
- 目前處理：`(本輪完成)`
- P0 尚未完整翻譯：8 部
- 一般失敗待重試：30 部 — yajnavalkya-smrti, plato-timaeus-el, numbers, an6-sixes, ramanuja-vedarthasamgraha, snorra-edda-on, avesta-sbe23-ae, isaiah, an8-eights, lucretius-de-rerum-natura-la
- 已阻塞待人工處理：18 部 — eyrbyggja-saga-on, avesta-sbe31-ae, quran, samaveda, ovid-fasti-la, jain-uttaradhyayana-pkt, sutta-nipata, chronicles-1, an9-nines, mimamsa-sutra-jaimini
- M3 執行狀態：**running** — `yajnavalkya-smrti` (translate)


流程：每部 `01-translation.md`（經文式翻譯）→ `semantic_tags`/`psych_tags`/`keywords` 回填 `meta.json`
→ 每批重生三份獨立反向索引 → commit + push。
