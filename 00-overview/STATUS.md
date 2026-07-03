# STATUS — religions-history 統一看板

> 由 `scripts/status.py` 產生（pull-based 快照，勿手改）。更新：2026-07-03 12:12:06 +0800

**4210 部 / 22 宗教 / 518 MB**

## 對齊覆蓋率（欄位回填進度）

| 欄位 | 已填 | 覆蓋率 | |
|------|------|--------|---|
| 文本角色 `text_role` | 4130/4210 |  98.1% | `████████████████████████` |
| 原文/譯文 `is_original_language` | 4134/4210 |  98.2% | `████████████████████████` |
| 成書時期 `era` | 62/4210 |   1.5% | `························` |
| 文類 `genre` | 1391/4210 |  33.0% | `████████················` |
| 語義標籤 `semantic_tags` | 62/4210 |   1.5% | `························` |
| 關鍵詞 `keywords` | 62/4210 |   1.5% | `························` |

## M3 分類進度（era+genre+tags 三者齊全）

| tier | 完成 | 總數 | |
|------|------|------|---|
| 核心 | 62 | 377 | `████····················`   16% |
| 次要 | 0 | 116 | `························`    0% |
| 總集 | 0 | 0 | `························`    0% |

## 翻譯進度

- `translation_status == done`：**32 / 4210** 部已翻譯（`01-translation.md`）

## 背景管線快照

- **分類（classify-metadata）**：日誌已分類 60 部
  - 最新：`  [ok] sn4-mara: era, genre, tags  era=axial-age genre=scripture-revealed`
- **翻譯管線**：進度：**38 / 365** 已翻譯+標籤
- **翻譯管線**：目前處理：`sblgnt-philippians`

## 最近 git 提交

- `ac8c95c5 align: M3 classify era/genre/tags (batch, +50)`
- `dd957643 Pipeline B+C: 核心 翻譯+標籤 批次 (+10 檔)`
- `4bd00164 align: M3 classify era/genre/tags (batch, +25)`
- `b359a75f align: 新增 classify-metadata.py（M3 從原文分類 era/genre/tags 單呼叫）`
- `21f1c661 docs: HANDOFF 記錄資料對齊 Layer 0-2 + 更新統計(4207/22)`
- `b29f8ab2 align: 定義 era/genre 受控詞彙 + 0-token 回補 genre 高信心子集`

