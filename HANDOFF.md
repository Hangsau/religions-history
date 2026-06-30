# HANDOFF — religions-history

> 狀態快照。每次工作結束更新。
> 規範見 `CLAUDE.md` + `PLAN.md`。

## 當前進度 — 234 部 / ~95 MB 原文

P0-P2.5 框架完整 (PLAN / CLAUDE / README / overview / methodology / per-religion 清單)。

### P3 經文下載 — 8 主要 + 4 部分宗教覆蓋

| 宗教 | 部數 | 主要來源 | 約大小 |
|------|------|---------|--------|
| 道教 | 17 | ctext API + Wikisource | 5 MB |
| 儒教 | 28 | ctext API + Wikisource | 12 MB |
| 漢譯佛經 | 48 | CBETA TEI XML (GitHub) | 35 MB |
| 巴利佛經 | 8 | SuttaCentral (Sujato) | 5 MB |
| 伊斯蘭古蘭經 | 1 (114 surahs) | Quran.com API | 1.4 MB |
| 猶太教 | 47 | Sefaria API | 8 MB |
| 基督教 (和合本) | 66 | zh.wikisource | 14 MB |
| 印度教梵文 | 14 | GRETIL | 5 MB |
| 古希臘羅馬 | 2 (Iliad/Odyssey) | en.wikisource Butler | 2 MB |
| 北歐 | 1 (Heimskringla) | en.wikisource Laing | ~1 MB |
| 凱爾特 | 1 (Welsh Triads) | en.wikisource | 30 KB |
| 摩門教 | 2 (BoM 1830 + Pearl) | en.wikisource | 1.6 MB |
| 錫克教 | 1 (Sikh Religion Macauliffe) | en.wikisource | 846 KB |
| 印度教英譯 | 1 (Mahabharata 進行中) | en.wikisource Ganguli | 大 |
| **總計** | **~234** | | **~95 MB** |

### 待做（按優先序）

1. **完成 Mahabharata** (進行中, 634 sections, ~25 min)
2. **巴利補完**: SN/AN/KN 子集 (約 3000 leaves, 分 samyutta/nipata 個別下載)
3. **耆那教**: Acharanga / Sutrakritanga / Kalpa Sutra (in SBE Volumes 22, 45 等)
4. **古希臘宗教**: Hesiod Theogony, Homeric Hymns (en.wikisource)
5. **諾斯底**: Nag Hammadi Library (en.wikisource 部分)
6. **巴哈伊**: bahai-library.com (寫專屬下載器)
7. **瑣羅亞斯德**: avesta.org / sacred-texts.com (寫下載器, 需瀏覽器 UA)
8. **神道**: NDL 國立国会图书館 (寫下載器)
9. **兩河 / 古埃及 / 美洲 / 非洲**: 各專門學界 source
10. **羅摩衍那 / 往世書 / 印度史詩**: en.wikisource SBE Volumes

## 已實作的下載器（8 種）

| Script | 來源 | 對應宗教 | 完成 |
|--------|------|---------|-----|
| `download-ctext.py` | api.ctext.org | 道教/儒教漢系 | 6 部 |
| `download-wikisource.py` | Wikisource Mediawiki API (--lang zh/ja/en/la/sa) | 道教/儒教/基督教/世界古典 | 90+ 部 |
| `download-cbeta.py` | raw.githubusercontent.com/cbeta-org/xml-p5 | 漢譯佛經 TEI | 48 部 |
| `download-quran.py` | api.quran.com | 古蘭經 | 1 部 (114 surahs) |
| `download-sefaria.py` | sefaria.org/api | 猶太教 | 47 部 |
| `download-suttacentral.py` | suttacentral.net/api | 巴利三藏 | 8 部 |
| `download-gretil.py` | gretil.sub.uni-goettingen.de | 梵文印度教 | 14 部 |
| `verify.py` | local | SHA-256 + chapter count + size 三層驗證 | — |

## 資料庫設計

每部經文獨立目錄 `translations/<slug>/`：

```
translations/<slug>/
├── meta.json                # 16 欄位 schema (見 scripts/meta_template.json)
├── raw/
│   ├── original.txt         # 原語言文本, 每章 `=== N | <label> ===` 分隔
│   ├── source-urls.txt      # 抓取 URL 紀錄
│   ├── checksums.sha256     # SHA-256 校驗
│   └── translation-en.txt   # 對照英譯 (Sefaria/SuttaCentral 提供)
```

跨平台 SHA-256 一致：`.gitattributes` 強制 LF EOL。

## 工作流（後續階段）

P3 → P4 (AI 翻譯) → P5 (專題交叉) → P6 (心理學) → P7 (視覺化)

P3 階段標準流程:
1. 寫 `scripts/catalog/<religion>.json` catalog
2. `python scripts/download-<source>.py --religion <name> --all`
3. `python scripts/verify.py --all` → PASS 才 commit
4. 每 5-10 部 push 一次

P4 翻譯階段 (`methodology/translation-workflow.md`):
- AI 翻譯各部 (m3 派工合適)
- Cross-check with existing translations
- Output to `translations/<slug>/01-translation.md` etc

## 已知技術問題與解法

- Windows console cp950 → `PYTHONIOENCODING=utf-8 python ...`
- ctext.org 未認證 IP 每 24h 200 次 → API + chapter_urns
- Wikisource prefixsearch fuzzy → allpages 嚴格 prefix
- Wikisource disambiguation → 探索具體版本子頁
- CBETA cbetaonline API 失效 → 直接抓 GitHub TEI XML
- Sefaria 部分文本結構複雜 → defer (Zohar, Guide for the Perplexed)
- SuttaCentral SN/AN/KN 深層遞迴 → 分 dn/mn/dhp/snp/ud/iti/thag/thig 子集
- GRETIL 路徑分新舊兩種 → corpustei/transformations/html/ 為新位置
- sacred-texts.com 需 browser-like UA → Mozilla Mac Chrome

## 派工原則 (tools/m3-executor-role.md)

當前下載階段以主 session 直接執行為主。P4 翻譯量大時派工合適：
- m3: 跑 LLM 翻譯
- Claude: 跑 verify + cross-check + 派工管理

## 下次接手

1. `python scripts/verify.py --all` 看整批狀態
2. 完成 Mahabharata 後 commit
3. 繼續未覆蓋宗教 (見「待做」清單)
4. 全 P3 完成後進 P4 AI 翻譯
