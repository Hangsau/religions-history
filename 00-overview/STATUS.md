# STATUS — religions-history 統一看板

> 由 `scripts/status.py` 產生（pull-based 快照，勿手改）。更新：2026-09-13 08:13:29 +0800

**4683 部 / 27 宗教 / 644 MB**

## 對齊覆蓋率（欄位回填進度）

| 欄位 | 已填 | 覆蓋率 | |
|------|------|--------|---|
| 文本角色 `text_role` | 4622/4683 |  98.7% | `████████████████████████` |
| 原文/譯文 `is_original_language` | 4660/4683 |  99.5% | `████████████████████████` |
| 成書時期 `era` | 375/4683 |   8.0% | `██······················` |
| 文類 `genre` | 1699/4683 |  36.3% | `█████████···············` |
| 語義標籤 `semantic_tags` | 453/4683 |   9.7% | `██······················` |
| 心理讀經標籤 `psych_tags` | 233/4683 |   5.0% | `█·······················` |
| 關鍵詞 `keywords` | 453/4683 |   9.7% | `██······················` |

## M3 分類進度（era+genre+semantic+psych 齊全）

| tier | 完成 | 總數 | |
|------|------|------|---|
| 核心 | 151 | 518 | `███████·················`   29% |
| 次要 | 0 | 279 | `························`    0% |
| 總集 | 0 | 0 | `························`    0% |

## 翻譯進度

- metadata done 且完整檔案通過：**206 / 4683** 部已翻譯（`01-translation.md`）

## 收集 / 下載（Pipeline A）

- 最新收錄：`studies-in-the-scriptures-1`（4709 分前）· 近 30 分 **+0** 部
- 下載日誌 `pipeline-a-talmud.log`：`  [book] Benayahu on Moed Katan`

## 背景管線快照

- **分類（classify-metadata）**：日誌已分類 374 部
  - 最新：`[summary] done=374 skipped=2 failed=1`
- **翻譯管線**：進度：**233 / 518** 已翻譯+標籤
- **翻譯管線**：目前處理：`studies-in-the-scriptures-1`
- **翻譯管線**：P0 尚未完整翻譯：8 部
- **翻譯管線**：一般失敗待重試：3 部 — sibylline-oracles-el, huangdi-neijing, studies-in-the-scriptures-1
- **翻譯管線**：已阻塞待人工處理：49 部 — eyrbyggja-saga-on, yajnavalkya-smrti, avesta-sbe31-ae, quran, numbers, samaveda, ovid-fasti-la, jain-uttaradhyayana-pkt, sutta-nipata, chronicles-1

## 最近 git 提交

- `0be1cb15 Pipeline B+C: 核心 翻譯+標籤 收尾 (processed 1)`
- `e9764237 HANDOFF: 2026-09-10 00:01 stop-hook 收尾（studies-in-the-scriptures-1 m3 翻譯接力 chunk 281/308 dispatched、auto-pipeline 2h tick PIPELINE_STATUS 23:37 更新、retryable 4 / blocked 49 維持、stage interval 90% / weekly 12% 警示、模式不衝突）`
- `e7474d29 HANDOFF: 2026-09-09 19:59 stop-hook 收尾（chun-qiu-zuo-zhuan tag chunk 43 失敗 invalid_tag_json 進 retry pool 3→4、retry 後 supervisor 退回 chunk 33 續跑 running、auto-pipeline 2h tick PIPELINE_STATUS 19:41 更新、studies-in-the-scriptures-1 翻譯 M3 running 維持、stage interval 71% / weekly 16%、模式不衝突）`
- `ff48adca HANDOFF: 2026-09-09 15:59 stop-hook 收尾（chun-qiu-zuo-zhuan m3 翻譯完成切 tag chunk 43/114 running、shiva-purana 跨週 chunks 88-251 接力完成從 retry pool 移除、studies-in-the-scriptures-1 接手翻譯 M3 running、auto-pipeline 2h tick PIPELINE_STATUS 15:21 更新、一般失敗待重試 3 (shiva-purana → studies-in-the-scriptures-1) / blocked 47→49、stage interval 66% / weekly 21%、模式不衝突）`
- `bc81e8ba HANDOFF: 2026-09-09 06:05 stop-hook 收尾（shiva-purana parent session 落地 chunk 88/251 + manifest 同步、auto-pipeline 2h tick PIPELINE_STATUS 05:47 更新、kn-jataka m3 接手 chunk 33/301 running、stage interval 65% / weekly 40%、模式不衝突）`
- `de742cbf HANDOFF: 2026-09-08 23:57 stop-hook 收尾（shiva-purana chunk 19/251 落地 + manifest 同步、auto-pipeline 2h tick PIPELINE_STATUS 23:25 更新、kn-jataka m3 完成清出 queue、linga-purana 從失敗待重試移除 (4→3)、blocked (46→47)、stage interval 91% / weekly 49%、模式不衝突）`

