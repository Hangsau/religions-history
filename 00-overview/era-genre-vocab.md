# era / genre 受控詞彙表

> 給 Pipeline C 的結構標籤（Layer 1）使用。每部 `meta.json` 的 `era`（成書時期）與
> `genre`（文類）**只能**填下列封閉詞彙之一，或 `null`（不臆測）。
> 設計原則：跨宗教可比、粒度夠粗以便撈取、年代不確定時用誠實的 `undated-traditional`，
> 不強加假精確（守 CLAUDE.md §3「不確定的一律不自動標」）。

---

## era — 成書時期（7 桶，依**成書年代**非抄本/譯本年代）

| 值 | 中文 | 大致範圍 | 代表 |
|----|------|----------|------|
| `bronze-age` | 青銅時代 | ~3000–1200 BCE | 早期兩河（Enuma Elish 源頭）、古埃及金字塔銘文、吠陀早期 |
| `axial-age` | 軸心時代 | ~800–200 BCE | 先秦諸子、早期佛教巴利、Upaniṣads、希伯來先知、希臘哲學、瑣羅亞斯德 Gathas |
| `classical-antiquity` | 古典晚期 | ~200 BCE–600 CE | 新約、大乘佛經、塔木德、教父、往世書、羅馬宗教 |
| `medieval` | 中古 | ~600–1500 CE | 伊斯蘭經注、藏傳密教、宋明理學、中世紀基督教、卡巴拉 |
| `early-modern` | 近世 | ~1500–1800 CE | 錫克經典、宗教改革文獻、新儒學 |
| `modern` | 近現代 | 1800 CE– | 巴哈伊、摩爾門、現代新興、19–20c 學術校勘 |
| `undated-traditional` | 年代不定 / 口傳 | 不可考 | 多數部落信仰、民俗神話、民族誌採集（斯拉夫/美洲/非洲口傳） |

**規則**：以文本**成書 / 定型**年代為準，不看抄本或現代譯本年代。跨數期者取**核心成書期**（如 Mahābhārata 取 `classical-antiquity`）。真不可考 → `undated-traditional`，不硬塞。

---

## genre — 文類（11 類，封閉集）

| 值 | 中文 | 描述 | 代表 |
|----|------|------|------|
| `scripture-revealed` | 經典 / 啟示 | 神啟或核心正典經文 | 古蘭、Torah 五經、佛經 sūtra、吠陀本集 |
| `law-code` | 律法 / 戒律 | 律法典、戒律規範 | Halakhah、律藏 Vinaya、Hammurabi、摩奴法典 |
| `commentary` | 註疏 / 論 | 註釋、義理論書 | Abhidharma 論藏、Mishnah/Talmud、教父註經、三家詩、理學註 |
| `epic-myth` | 史詩 / 神話 | 敘事史詩與神話 | Mahābhārata、Gilgamesh、Edda、Popol Vuh、記紀神話 |
| `hymn-liturgy` | 讚歌 / 禮儀 | 讚美詩、祈禱、儀軌 | Psalms、吠陀讚歌、葬祭儀軌、禮拜文 |
| `wisdom-aphorism` | 智慧 / 箴言 | 格言智慧文學 | Proverbs、論語、Ptahhotep、法句經 |
| `prophecy-apocalypse` | 預言 / 啟示錄 | 先知書、末世啟示 | Isaiah、Revelation、但以理 |
| `philosophy-doctrine` | 哲學 / 教義 | 系統義理、哲學論述 | Upaniṣads、道德經、Stoics、教義大全 |
| `hagiography-history` | 傳記 / 史傳 | 聖徒行傳、教史、傳記 | Gospels（敘事部分）、高僧傳、宗教史著 |
| `incantation-magic` | 咒術 / 魔法 | 咒語、陀羅尼、魔法文本 | 大悲咒、Egyptian magic、希臘魔法紙草 PGM |
| `folk-ethnography` | 民俗 / 民族誌 | 民間故事、民族誌記錄 | 斯拉夫民間故事、部落神話採集 |

**規則**：取**主導文類**單值。混合體（如福音書含敘事+訓誨）取篇幅/功能主軸。填不出高信心值 → `null`，交 M3 或人工。

---

## 回補策略（分層，對應兩個受限配額池）

- **0-token 規則子集（高信心）**：`genre` 由 `tradition`/`source_platform` 推：
  Sefaria `Halakhah`→`law-code`、`Midrash`→`commentary`、`Mishnah`→`law-code`、`Talmud`→`commentary`；
  巴利 slug `vinaya/pli-tv`→`law-code`、`abhidhamma`→`commentary`、其餘 nikāya→`scripture-revealed`。
- **M3 小輸出（其餘）**：讀 `raw/original.txt` 前 N 段 + 標題，回單一 `era` + `genre`（白名單過濾，違規丟棄）。
  與 `semantic_tags`/`keywords` 同一次 M3 呼叫抽出，省配額。
- **保守**：任何不確定一律 `null`，不臆測。
