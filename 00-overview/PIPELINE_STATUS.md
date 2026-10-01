# Pipeline B+C 自動執行狀態

> 由 `scripts/auto-pipeline.py` 自動產生，勿手改。

- 更新時間：2026-10-01 17:06:20 +0800
- 佇列 tier：**核心**
- 進度：**467 / 518** 已翻譯+標籤
- 目前處理：`nihon-shoki-zh`
- P0 尚未完整翻譯：8 部
- 一般失敗待重試：13 部 — sibylline-oracles-el, huangdi-neijing, rigveda, garuda-purana, brahma-purana, valmiki-ramayana, majjhima-nikaya, gnostics-and-their-remains, science-and-health-1906, mahabharata-ganguli
- 已阻塞待人工處理：40 部 — eyrbyggja-saga-on, yajnavalkya-smrti, avesta-sbe31-ae, quran, samaveda, ovid-fasti-la, jain-uttaradhyayana-pkt, sutta-nipata, chronicles-1, tain-bo-cuailnge-ga
- M3 執行狀態：**running** — `nihon-shoki-zh` (tag)


流程：每部 `01-translation.md`（經文式翻譯）→ `semantic_tags`/`psych_tags`/`keywords` 回填 `meta.json`
→ 每批重生三份獨立反向索引 → commit + push。
