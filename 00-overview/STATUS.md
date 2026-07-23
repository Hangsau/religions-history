# STATUS — religions-history 統一看板

> 由 `scripts/status.py` 產生（pull-based 快照，勿手改）。更新：2026-07-23 09:20:21 +0800

**4683 部 / 27 宗教 / 644 MB**

## 對齊覆蓋率（欄位回填進度）

| 欄位 | 已填 | 覆蓋率 | |
|------|------|--------|---|
| 文本角色 `text_role` | 4622/4683 |  98.7% | `████████████████████████` |
| 原文/譯文 `is_original_language` | 4660/4683 |  99.5% | `████████████████████████` |
| 成書時期 `era` | 375/4683 |   8.0% | `██······················` |
| 文類 `genre` | 1699/4683 |  36.3% | `█████████···············` |
| 語義標籤 `semantic_tags` | 423/4683 |   9.0% | `██······················` |
| 心理讀經標籤 `psych_tags` | 179/4683 |   3.8% | `█·······················` |
| 關鍵詞 `keywords` | 423/4683 |   9.0% | `██······················` |

## M3 分類進度（era+genre+semantic+psych 齊全）

| tier | 完成 | 總數 | |
|------|------|------|---|
| 核心 | 123 | 518 | `██████··················`   24% |
| 次要 | 0 | 279 | `························`    0% |
| 總集 | 0 | 0 | `························`    0% |

## 翻譯進度

- metadata done 且完整檔案通過：**148 / 4683** 部已翻譯（`01-translation.md`）

## 收集 / 下載（Pipeline A）

- 最新收錄：`huainanzi`（14 分前）· 近 30 分 **+1** 部
- 下載日誌 `pipeline-a-talmud.log`：`  [book] Benayahu on Moed Katan`

## 背景管線快照

- **分類（classify-metadata）**：日誌已分類 374 部
  - 最新：`[summary] done=374 skipped=2 failed=1`
- **翻譯管線**：進度：**179 / 518** 已翻譯+標籤
- **翻譯管線**：目前處理：`sutta-nipata`
- **翻譯管線**：P0 尚未完整翻譯：19 部
- **翻譯管線**：一般失敗待重試：74 部 — eyrbyggja-saga-on, plato-phaedo-el, yajnavalkya-smrti, avesta-sbe31-ae, plato-timaeus-el, quran, numbers, deuteronomy, plato-phaedrus-el, samaveda
- **翻譯管線**：已阻塞待人工處理：0 部

## 最近 git 提交

- `9146703f Pipeline B+C: 核心 翻譯+標籤 收尾 (processed 24)`
- `7e7bc357 Pipeline B+C: 核心 翻譯+標籤 批次 (+10 檔)`
- `54d8e2b6 Pipeline B+C: 核心 翻譯+標籤 批次 (+10 檔)`
- `61f4a09d HANDOFF: 2026-07-22 16:00 psych_tags 補 2 檔快照 (commit 0f45dc0f)`
- `0f45dc0f Pipeline B+C: psych_tags 補 2 檔 (baudhayana-dharmasutra, judges)`
- `db06ee15 Pipeline B+C: 核心 翻譯+標籤 批次 (+10 檔)`

