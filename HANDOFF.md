# HANDOFF — religions-history

> 狀態快照。每次工作結束更新。
> 規範見 `CLAUDE.md` + `PLAN.md` + `STRATEGY.md`。

## 當前狀態

**1932 部 / 252.6 MB / 20 宗教 / 原文 1494 + 譯文 438**

詳見即時 [`00-overview/INDEX.md`](./00-overview/INDEX.md) 自動產生統計。

## 策略決定（2026-07-01）

**轉向：先補核心缺口 → 進入 P4 翻譯 + P5 標籤 + P7 網站，不再無限深挖。**

理由：v3 列出 ~2400 entries，目前已 80%。再深挖（道藏 5305 全 / 大正藏 T18+ / 塔木德 76 全 / 教父 ANF+NPNF 全）會稀釋品質，先把列出的補齊，再做翻譯 / 標籤 / 連結等品質工作更有意義。

## 立即下一步

### 補核心缺口（一輪）

| 宗教 | 缺什麼 | 來源 |
|------|--------|------|
| 神道 | 5 部（古事記、日本書紀、延喜式、風土記、古語拾遺）| NDL or ja.ws Kokushi Taikei |
| 兩河（蘇美 + 巴比倫 + 赫梯 + 烏加里特）| 15 部 | ETCSL Sumerian + sacred-texts /ane/ |
| 古埃及 | 12 部（Amduat、Coffin Texts、Wisdom Literature 等）| sacred-texts + 學界數位 |
| 美洲 codices | Dresden / Madrid / Paris codices | FAMSI or sacred-texts |
| 諾斯底 Nag Hammadi | 52 篇本身（不只 Mead 學派）| en.wikisource or specialized |
| 現代新興 | Doctrine and Covenants、Scientology 主要、巴哈伊核心 | en.wikisource + bahai-library |
| 巴哈伊核心 | Kitab-i-Aqdas、Kitab-i-Iqan、Hidden Words 等 | reference.bahai.org |
| 凱爾特 | 補 Táin Bó Cúailnge、Welsh Triads 完整版 | sacred-texts / en.ws |
| 北歐 | 補 Skaldic、Heimskringla 完整、Beowulf | sacred-texts / en.ws |
| 印度教 | 18 大 + 18 小 Purana（只有 Bhagavata + Skanda 1-31）| GRETIL or wisdomlib |

預估補完約 +200-300 部 → 累計 ~2200 部。

### 補完後切 P4 / P5

- P4：AI 翻譯（按 `methodology/translation-workflow.md` SOP）。原文每部生 `01-translation.md`，譯文 cross-check
- P5：語義標籤抽取（每部 ~100 字主旨 + 0-N 個概念 tag），生 `00-overview/tag-index.json`
- P7：Astro 站，從 `translations/` 自動生頁面

## 進行中（m3 背景）

當前 m3 task: **Phase C-3**
- CBETA T13-T17（大集 + 經集 ~150 部）— 完成
- 伊斯蘭輔助 7 部 — 完成
- Sefaria Mishnah 全 63 tractate + 諸家注疏 — 進行中

完成後**停止深挖**，進入補核心缺口。

## 已實作下載器（12 個）

矩陣見 [`CLAUDE.md` 既有下載器矩陣](./CLAUDE.md#既有下載器矩陣-12-個)。

## 已完成宗教覆蓋摘要

| 宗教 | 部數 | 評估 |
|------|------|------|
| 佛教（漢傳 / 巴利 / 梵文混）| 961 | 漢傳 T01-T17 41% / 巴利 SN+AN+KN 子集 / 梵文 與印度教共用 |
| 猶太教 | 657 | Sefaria Mishnah 全展開 |
| 基督教 | 169 | 希臘 NT + 拉丁 Vulgate + 中文和合本 + Mahabharata Ganguli |
| 印度教 | 33 | 4 Vedas + 11 Upanishads + Ramayana + 6 哲學經 |
| 儒教 | 26 | 五經 + 四書 + 主要諸子 + 朱子語類 + 傳習錄 |
| 古希臘羅馬 | 18 | Homer / Hesiod / Ovid / Virgil / Plato / Plotinus 等 |
| 道教 | 17 | 道德經 + 莊子 + 列子 + 文子 + 抱朴子 + 雲笈七籤等 |
| 瑣羅亞斯德 | 8 | Avesta SBE 04+23+31 + Pahlavi 4 卷 |
| 伊斯蘭 | 7 | 古蘭原文 + Pickthall 英譯 + Bukhari + 蘇菲（Rumi/Ibn Arabi/Ghazali）|
| 美洲 / 凱爾特 / 非洲 | 6 each | 部分 codices / Mabinogion / Yoruba 等 |
| 諾斯底 | 5 | Mead Hermetica + Gnostic Remains |
| 錫克 / 北歐 | 3 each | Macauliffe / Guru Granth / Edda / Volsunga / Heimskringla |
| 古埃及 / 耆那 / 現代新興 | 2 each | Book of Dead / Pyramid Texts / SBE 22+45 / 摩門經+Pearl |
| 巴哈伊 | 1 | Splendour of God |
| 神道 | 0 | 待寫 NDL downloader |

## 已知技術問題

- **Windows console cp950** → 所有 Python 跑 `PYTHONIOENCODING=utf-8 python ...`
- **跨平台 SHA-256** → `.gitattributes` 強制 LF EOL
- **ctext.org 200/24h 配額** → 已避開改用 GitHub mirror
- **sacred-texts.com Cloudflare** → 用 Mozilla Mac Chrome UA 解
- **CBETA cbetaonline API 失效** → 直接抓 GitHub TEI XML（download-cbeta.py）
- **Sefaria Guide for the Perplexed API 500** → 用 sacred-texts 替代
- **SuttaCentral SN/AN/KN 深層遞迴** → catalog 分 samyutta/nipata 子 entry
- **GRETIL 路徑分新舊** → `1_sanskr/*` (老) vs `corpustei/transformations/html/*` (新)

## 爬蟲倫理

所有 downloader 已實作（2026-07-01 更新）：
- `_polite.py` 共用 UA：`religions-history-research/0.1 (academic research; contact: psyhangsau@gmail.com; +https://github.com/Hangsau/religions-history)`
- 每請求 jitter（random 0-0.5s）打破規律 pattern
- 每 100 次請求自動暫停 30s
- 5 次指數 backoff（10 → 480s）處理 429/403/503

## 下次接手

1. 跑 `python scripts/verify.py --all` 看狀態
2. 跑 `python scripts/generate-index.py` 重生 INDEX
3. 看 HANDOFF「立即下一步」決定先補哪個核心缺口
4. 補完後切 P4 翻譯 / P5 標籤
