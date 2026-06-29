# 經文下載計畫

> 怎麼下載、存哪、用什麼工具、自動化、授權、驗證
> 啟動：2026-06-29

## 1. 目標

把 75+ 部經典的原文 / 重要版本**下載到本機**，作為：
- 翻譯工作流的輸入
- 研究基礎
- 可離線使用的本地資料庫

**不**包含：翻譯（之後用 `translation-workflow.md` SOP 做）

## 2. 來源平台（已驗證可用）

| 語言 | 平台 | 取得方式 | 授權 |
|------|------|---------|------|
| 古典漢語 | **ctext.org** | API (legacy API) + 網頁 | CC BY-SA 4.0 |
| 古典漢語 | **Chinese Text Project (ctext)** | API (ctext.org/tools/api) | CC BY-SA 4.0 |
| 漢譯佛典 | **CBETA** | API + XML 線上閱讀 | 開源（限非商業研究）|
| 漢譯佛典 | **SAT大正藏（東大）** | https://21dzk.l.u-tokyo.ac.jp/SAT2018/ | 學術用 |
| 漢譯佛典 | **CBETA Online** | https://cbetaonline.dila.edu.tw/ | 開源 |
| 梵文 | **GRETIL** | http://gretil.sub.uni-goettingen.de/ | 學術用 |
| 梵文 | **Wisdomlib** | https://www.wisdomlib.org/ | CC BY-SA |
| 梵文 | **Sanskrit Library** | https://sanskritlibrary.org/ | 學術用 |
| 巴利 | **suttacentral** | API (sc-api.suttacentral.net) | CC BY-NC |
| 巴利 | **VRI** | 商業 | 商業 |
| 巴利 | **accesstoinsight** | https://accesstoinsight.org/ | 公共領域（英文）|
| 希臘（新約）| **SBLGNT** | https://sblgnt.com/ | CC BY 4.0 |
| 希臘（古典）| **Perseus** | https://www.perseus.tufts.edu/hopper/ | CC BY-SA |
| 阿拉伯 | **Quran.com API** | https://quran.com/api | 開源 |
| 阿拉伯 | **Tanzil** | https://tanzil.net/ | 開源 |
| 希伯來 | **Sefaria** | API (https://www.sefaria.org/api) | CC BY-NC |
| 希伯來 | **Mechon Mamre** | https://mechon-mamre.org/ | 公共領域 |
| 阿維斯塔 | **avesta.org** | https://www.avesta.org/ | 學術用 |
| 蘇美 / 阿卡德 | **ETCSL** | https://etcsl.orinst.ox.ac.uk/ | 學術用 |
| 古埃及 | **Pyramid Texts 數位** | 多 | 學術用 |
| 多語古蘭 | **Quran.com** | API | 開源 |

## 3. 工具選擇

### 3.1 命令列

| 工具 | 用於 |
|------|------|
| `wget` | 簡單靜態檔下載 |
| `curl` | API 互動 + POST |
| `aria2` | 多連線加速 |

### 3.2 Python（推薦）

| 套件 | 用於 |
|------|------|
| `requests` | HTTP 請求 |
| `beautifulsoup4` | HTML 解析 |
| `lxml` | XML 解析（CBETA 用）|
| `json` | API 回應處理 |
| `hashlib` | 校驗碼 |

### 3.3 各站 API 端點

```python
# ctext.org
https://ctext.org/api.pl?if=zh&json=1&req=...

# CBETA
https://cbetaonline.dila.edu.tw/api/v1/...

# suttacentral
https://sc-api.suttacentral.net/api/...

# Quran.com
https://api.quran.com/api/v4/...

# Sefaria
https://www.sefaria.org/api/texts/...

# SBLGNT
https://sblgnt.com/download/...
```

## 4. 存檔結構

```
translations/
├── [經典-slug]/
│   ├── 00-version.md          ← 版本說明（先寫）
│   ├── meta.json              ← metadata
│   ├── raw/                   ← 原始檔（不編輯）
│   │   ├── original.txt       ← 主原文
│   │   ├── original.json      ← 結構化版（章節）
│   │   ├── cross-check-1.txt  ← 對照文本
│   │   ├── cross-check-2.txt
│   │   ├── source-urls.txt    ← 下載 URL 記錄
│   │   └── checksums.sha256   ← 校驗碼
│   ├── 01-translation.md      ← AI 翻譯（之後做）
│   └── 02-variants.md         ← 重要章節交叉驗證（之後做）
```

## 5. Metadata Schema

```json
{
  "name_zh": "道德經",
  "name_en": "Tao Te Ching",
  "name_original": "道德經",
  "religion": "道教",
  "language": "古典漢語",
  "version": "王弼本",
  "version_date": "3 世紀",
  "source_platform": "ctext.org",
  "source_id": "dao-jing",
  "source_url": "https://ctext.org/dao-jing",
  "downloaded_at": "2026-06-29T13:00:00Z",
  "downloaded_by": "Hang",
  "downloader_script": "scripts/download-ctext.py",
  "license": "CC BY-SA 4.0",
  "size_bytes": 5230,
  "checksum_sha256": "abc123...",
  "chapter_count": 81,
  "verified": true
}
```

## 6. 下載批次計畫

### 批次 1（小、易驗證）

| # | 經典 | 來源 | 預估大小 |
|---|------|------|---------|
| 1 | 道德經 | ctext.org | ~5 KB |
| 2 | 心經（鳩摩羅什）| CBETA T250 | ~1 KB |
| 3 | 心經（玄奘）| CBETA X0220 | ~1 KB |
| 4 | 古蘭經 Al-Fatiha | Quran.com | ~1 KB |

### 批次 2（中等）

| # | 經典 | 來源 | 預估大小 |
|---|------|------|---------|
| 5 | 道德經（帛書本）| ctext 對照 | ~5 KB |
| 6 | 金剛經 | CBETA + GRETIL | ~5 KB |
| 7 | 莊子內篇 | ctext.org | ~50 KB |
| 8 | 薄伽梵歌 | wisdomlib / GRETIL | ~100 KB |
| 9 | 梨俱吠陀選 | GRETIL | ~200 KB |

### 批次 3（大部頭）

| # | 經典 | 來源 | 預估大小 |
|---|------|------|---------|
| 10 | 巴利三藏（PTS）| suttacentral / VRI | ~10 MB |
| 11 | 古蘭經全 | Tanzil | ~600 KB |
| 12 | 新約 SBLGNT | sblgnt.com | ~2 MB |
| 13 | 舊約 WLC | mechon-mamre | ~3 MB |
| 14 | 阿維斯塔 | avesta.org | ~500 KB |
| 15 | 道德經 9 版本對照 | ctext + 多源 | ~50 KB |

## 7. 自動化腳本

位置：`scripts/`

### 7.1 scripts/download-ctext.py

抓 ctext.org 文本（含道德經、四書、莊子等）

### 7.2 scripts/download-cbeta.py

抓 CBETA 漢譯佛典

### 7.3 scripts/download-quran.py

抓 Quran.com 古蘭經（多語）

### 7.4 scripts/download-sefaria.py

抓 Sefaria 希伯來文 / 塔木德

### 7.5 scripts/download-suttacentral.py

抓 suttacentral 巴利經

### 7.6 scripts/verify.py

- 計算 SHA-256
- 對照預期大小 / 章節數
- 標記差異

## 8. 驗證策略

每部下載完做：

1. **完整性**：檔案大小在預期範圍
2. **章節數**：道德經 81 章、古蘭經 114 章等
3. **校驗碼**：SHA-256 存到 `checksums.sha256`
4. **內容抽樣**：隨機抽 3-5 段對照來源頁
5. **metadata**：填 `meta.json`

## 9. 授權 / 引用

每部檔案需標明：

- 來源平台
- 來源 URL
- 授權狀態
- 引用格式

範例：
```
本文本來自 ctext.org，採 CC BY-SA 4.0 授權。
引用：中國哲學書電子化計劃. 道德經 [Data set]. https://ctext.org/dao-jing
```

## 10. 資料量估算

| 類別 | 部數 | 估總大小 |
|------|------|---------|
| 古典漢語（儒道漢傳佛）| 15 | ~2 MB |
| 梵文 / 巴利（印度系）| 20 | ~15 MB |
| 一神經典（基督伊斯蘭猶太）| 10 | ~10 MB |
| 大型（吠陀、阿維斯塔）| 10 | ~10 MB |
| 邊緣 / 口述文字化 | 20 | ~3 MB |
| **總計** | **75** | **~40 MB** |

## 11. 風險

- **API 變更**：網站改 API 會失效 → 抓後存 raw 文字備份
- **連結腐爛**：URL 失效 → 用 archive.org snapshot
- **授權改變**：CC 改其他 → 立即標記
- **大檔下載**：10 MB 級需斷點續傳

## 12. 不做

- ❌ 抓後直接翻譯（先純下載、metadata、驗證）
- ❌ 抓來路不明來源（只用 A/B 級公開資料庫）
- ❌ 不存校驗碼
- ❌ 抓取後不對 metadata

## 13. 啟動順序

```
Step 1: 寫 meta.json schema + 一個範例
Step 2: 寫 scripts/download-ctext.py（先做最有用的）
Step 3: 抓道德經 + 心經（批次 1 前 2 部）
Step 4: 驗證（SHA-256 + 章節數 + 抽樣對照）
Step 5: commit + push
Step 6: user 看過 → 啟動批次 1 全部
```

## Sources

- 各平台官網（見 §2）
- GitHub 上類似宗教文本資料庫（cross-check 流程）