# HANDOFF — religions-history

> 狀態快照。每次工作結束更新。
> 規範見 `CLAUDE.md` + `PLAN.md`。

## 當前進度

- ✅ P0 框架（PLAN / CLAUDE / README / overview / methodology）
- ✅ P1 宗教總目錄、P2 經文總目錄、P2.5 每教經文清單（v2 ~575 部）
- 🟡 **P3 經文下載 — 227 部 / ~90 MB 原文（已完成大宗）**

### 完成（按宗教）

| 宗教 | 部數 | 主要來源 | 約大小 |
|------|------|---------|--------|
| 道教 | 17 | ctext / Wikisource | 5 MB |
| 儒教 | 28 | ctext / Wikisource | 12 MB |
| 漢譯佛經 | 48 | CBETA TEI XML (GitHub) | 35 MB |
| 巴利佛經 | 8 | SuttaCentral (Sujato) | 5 MB |
| 伊斯蘭古蘭經 | 1 (114 surahs) | Quran.com API | 1.4 MB |
| 猶太教 | 47 | Sefaria API | 8 MB |
| 基督教 (和合本) | 66 | Wikisource | 14 MB |
| 印度教梵文 | 14 | GRETIL | 5 MB |
| **總計** | **~227** | | **~90 MB** |

### 待做（按宗教）

| 宗教 | 預計 | 來源 | 備註 |
|------|------|------|------|
| 巴利補完 (SN / AN / KN 子集) | ~3000 | SuttaCentral | 分 samyutta / nipata 個別下載 |
| 瑣羅亞斯德 | ~11 | avesta.org / Wikisource | 路徑探索中 |
| 神道 | ~11 | ja.wikisource.org | 古事記 / 日本書紀 / 延喜式 |
| 兩河 (蘇美 / 巴比倫) | ~15 | ETCSL / CDLI | |
| 古埃及 | ~14 | 學界數位資源 | |
| 古希臘羅馬 | ~21 | Perseus | |
| 北歐 / 凱爾特 / 斯拉夫 | ~25 | 各別來源 | |
| 諾斯底 | ~18 | Nag Hammadi 英譯 | |
| 美洲 (瑪雅 / 阿茲特克 / 印加) | ~28 | 學界資源 | |
| 非洲 | ~8 | 學界資源 | |
| 現代新興 + 巴哈伊 / 錫克 / 耆那 | ~50 | 各官網 / Wikisource | |

## 已實作的下載器

| Script | 來源 | 對應宗教 |
|--------|------|---------|
| `download-ctext.py` | api.ctext.org | 道德經、論語、孟子等漢系 |
| `download-wikisource.py` | zh.wikisource.org Mediawiki API | 道教 / 儒教 / 基督教和合本 |
| `download-cbeta.py` | raw.githubusercontent.com/cbeta-org/xml-p5 | 漢譯佛經（TEI P5）|
| `download-quran.py` | api.quran.com | 古蘭經 Uthmani |
| `download-sefaria.py` | sefaria.org/api | 猶太教 / 部分基督教 OT |
| `download-suttacentral.py` | suttacentral.net/api | 巴利三藏 |
| `download-gretil.py` | gretil.sub.uni-goettingen.de | 梵文印度教 |
| `verify.py` | local | SHA-256 + chapter count + size 三層驗證 |

## 資料庫設計

每部經文獨立目錄 `translations/<slug>/`：

```
translations/<slug>/
├── meta.json                # 16 欄位 schema
├── raw/
│   ├── original.txt         # 原語言文本，每章 === N | <label> === 分隔
│   ├── source-urls.txt      # 抓取 URL 紀錄
│   ├── checksums.sha256     # SHA-256
│   └── translation-en.txt   # 對照英譯（Sefaria/SuttaCentral）
```

跨平台 SHA-256 一致：`.gitattributes` 強制 LF EOL。

## 工作流（P3 階段）

1. 寫 `scripts/catalog/<religion>.json` catalog（slug + 源頭 ID + tier）
2. `python scripts/download-<source>.py --religion <name> --all`
3. `python scripts/verify.py --all` → PASS 才 commit
4. 每 5-10 部 push 一次；該宗教全綠才轉下宗教

## m3 派工原則（見 `tools/m3-executor-role.md`）

當前階段以主 session 直接執行為主。下載屬 mechanical 任務適合 m3 派工但暫無必要。
未來 P4 翻譯階段會大量派工：m3 跑 LLM 翻譯（量大），Claude 跑 verify + cross-check。

## 已知技術問題與解法

- Windows console cp950 → `PYTHONIOENCODING=utf-8 python ...`
- ctext.org 未認證 IP 每 24h 200 次配額 → 用 API + chapter_urns catalog 繞 auth wall
- Wikisource prefixsearch fuzzy → 改用 allpages 嚴格 prefix
- Wikisource disambiguation 頁 → 探索具體版本子頁
- CBETA cbetaonline API 失效 → 直接抓 GitHub TEI XML
- Sefaria 部分文本結構複雜（Zohar）→ defer
- SuttaCentral SN/AN/KN 深層遞迴 → 分小子集 (dn/mn/dhp 等)
- GRETIL 路徑分新舊 → 兩種混用，新版在 `corpustei/transformations/html/`

## 下次接手

1. `python scripts/verify.py --all` 看整批狀態
2. 接 P3-I 瑣羅亞斯德、P3-J 神道（小，~20 部）
3. 然後 P3-K 古代邊緣 + P3-L 現代新興
4. 完成 P3 後進 P4：AI 翻譯（按 `methodology/translation-workflow.md` SOP）
