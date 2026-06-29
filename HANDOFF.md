# HANDOFF — religions-history

> 狀態快照。每次工作結束更新。
> 規範見 `CLAUDE.md` + `PLAN.md`。

## 當前進度

- ✅ P0 框架（PLAN / CLAUDE / README / overview / methodology）
- ✅ P1 宗教總目錄 `00-overview/religions-inventory.md`
- ✅ P2 經文總目錄 `00-overview/scriptures-inventory.md`
- ✅ P2.5 每教經文清單 `methodology/per-religion-scriptures.md`（v2 ~575 部）
- 🟡 **P3 經文下載（進行中）**：
  - ✅ **P3-A 道教**：17 部（ctext 4 + Wikisource 13）— 約 5 MB 原文
  - ✅ **P3-B 儒教**：28 部（ctext analects + mengzi + Wikisource 26）— 約 12 MB 原文
  - ✅ **P3-C 漢譯佛經**：48 部 via CBETA TEI XML（GitHub）— 約 35 MB 原文
  - ✅ **P3-E 伊斯蘭**（古蘭經）：114 surahs Uthmani，1.4 MB Arabic
  - 🟡 **P3-F 猶太教**（Sefaria）：Tanakh + Mishnah / Talmud / Midrash 進行中
  - 🟡 **P3-D 巴利佛經**（SuttaCentral）：5 大尼柯耶並行下載
  - ⏳ P3-G 基督教（SBLGNT + Vulgate + LXX，~71 部）
  - ⏳ P3-H 印度教梵文（GRETIL + Wisdomlib，~45 部）
  - ⏳ P3-I 瑣羅亞斯德（avesta.org，~11 部）
  - ⏳ P3-J 神道（Wikisource 日 / NDL，~11 部）
  - ⏳ P3-K 其他（兩河 / 古埃及 / 希羅 / 北歐 / 凱爾特 / 諾斯底 / 美洲 / 非洲）
  - ⏳ P3-L 現代新興 + 巴哈伊 / 錫克 / 耆那（~50 部）

## 已實作的下載器

| Script | 來源 | 用途 |
|--------|------|------|
| `download-ctext.py` | api.ctext.org | 漢系經典（道德經、莊子、列子、論語、孟子等）|
| `download-wikisource.py` | zh.wikisource.org Mediawiki API | 道教 / 儒教 / 周易 / 其他補充 |
| `download-cbeta.py` | raw.githubusercontent.com/cbeta-org/xml-p5 | 漢譯佛經（TEI P5 XML 解析）|
| `download-quran.py` | api.quran.com | 古蘭經 Uthmani 校勘 |
| `download-sefaria.py` | sefaria.org/api | 猶太教 Tanakh / 米示拿 / 塔木德 |
| `download-suttacentral.py` | suttacentral.net/api | 巴利三藏 Sujato 校勘 |
| `verify.py` | local | SHA-256 + chapter count + size 三層驗證 |

## 資料庫設計

- 每部經文獨立目錄 `translations/<slug>/`
- 結構：
  ```
  translations/<slug>/
  ├── meta.json                # schema 見 scripts/meta_template.json (16 欄位)
  ├── raw/
  │   ├── original.txt         # 原語言文本，每章用 === N | <label> === 分隔
  │   ├── source-urls.txt      # 抓取 URL 紀錄
  │   ├── checksums.sha256     # 原文 SHA-256
  │   └── translation-en.txt   # （Sefaria/SuttaCentral）對照英譯
  ```
- meta.json 必填：slug、religion、language、version、source_url、size、checksum、chapter_count、verified
- 跨平台 SHA-256 一致：`.gitattributes` 強制 LF EOL

## 已下載總量

| 宗教 | 部數 | 約大小 |
|------|------|--------|
| 道教 | 17 | 5 MB |
| 儒教 | 28 | 12 MB |
| 漢譯佛經 | 48 | 35 MB |
| 伊斯蘭 | 1 | 1.4 MB |
| 猶太教 | 進行中 | — |
| 巴利佛經 | 進行中 | — |

**總計：~92 部已完成，~50 MB 原文。**

## 工作流（P3 階段）

1. 對某宗教，按 `methodology/per-religion-scriptures.md` 取核心 + 次要清單
2. 寫 `scripts/catalog/<religion>.json` catalog（slug + 源頭 ID + tier + expected）
3. 寫 `scripts/download-<source>.py`（若新 source）
4. `python scripts/download-<source>.py --religion <name> --all` 跑全 batch
5. `python scripts/verify.py --all` → PASS 才 commit
6. 每 5-10 部 push 一次；該宗教全綠才轉下宗教

## m3 派工原則（見 `tools/m3-executor-role.md`）

當前階段以主 session 直接執行為主。m3 可派工的場景：
- 翻譯（之後 AI 翻譯階段，跑量大時派出去）
- 批次校對（拿原文比對版本差異）
- 不適合派：下載腳本本身、驗證邏輯、catalog 維護

## 已知技術問題與解法

- Windows console cp950 → 所有 Python 跑 `PYTHONIOENCODING=utf-8 python ...`
- ctext.org 未認證 IP 每 24h 200 次 API 配額 → 改用 API gettext + chapter_urns catalog
- Wikisource prefixsearch 是 fuzzy → 改用 allpages 嚴格 prefix
- Wikisource 部分 disambiguation 頁 → 探索後使用具體版本子頁名
- CBETA cbetaonline.dila.edu.tw API 失效 → 直接抓 GitHub TEI XML
- Sefaria 部分文本結構複雜（如 Zohar 多分卷）→ defer_reason 暫緩

## 下次接手

1. 先 `python scripts/verify.py --all` 看整批狀態
2. 完成 P3-F / P3-D 後接 P3-G 基督教（需新寫 Wikisource 中文版 + SBLGNT 希臘文）
3. P3-G 後接 P3-H 印度教梵文（GRETIL）→ P3-I → P3-J → P3-K → P3-L
