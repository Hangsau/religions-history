# Pipeline B+C 自動執行狀態

> 由 `scripts/auto-pipeline.py` 自動產生，勿手改。

- 更新時間：2026-08-05 21:03:58 +0800
- 佇列 tier：**核心**
- 進度：**207 / 518** 已翻譯+標籤
- 目前處理：`ramanuja-vedarthasamgraha`
- P0 尚未完整翻譯：8 部
- 一般失敗待重試：26 部 — ramanuja-vedarthasamgraha, snorra-edda-on, avesta-sbe23-ae, isaiah, an8-eights, lucretius-de-rerum-natura-la, sn22-khandha, bud-buddhacarita-sa, ezekiel, marcus-aurelius-meditations-el
- 已阻塞待人工處理：20 部 — eyrbyggja-saga-on, yajnavalkya-smrti, avesta-sbe31-ae, quran, numbers, samaveda, ovid-fasti-la, jain-uttaradhyayana-pkt, sutta-nipata, chronicles-1
- M3 執行狀態：**waiting_quota** — `ramanuja-vedarthasamgraha` (translate chunk 45/85)
- 限制偵測：2026-08-05T21:03:58.328881+08:00；下次重試：2026-08-10T08:00:15+08:00
- 最後錯誤：`proactive quota reserve: 5h=20% (reserve 5%) weekly=2% (reserve 2%)`


流程：每部 `01-translation.md`（經文式翻譯）→ `semantic_tags`/`psych_tags`/`keywords` 回填 `meta.json`
→ 每批重生三份獨立反向索引 → commit + push。
