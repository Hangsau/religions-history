# HANDOFF — religions-history

> 狀態快照。每次工作結束更新。
> 規範見 `CLAUDE.md` + `PLAN.md` + `STRATEGY.md`。

## 當前狀態

**2062 部 / 20 宗教 / 原文 1500+ + 譯文 500+**

詳見即時 [`00-overview/INDEX.md`](./00-overview/INDEX.md) 自動產生統計。
進度追蹤見 [`00-overview/PROGRESS.md`](./00-overview/PROGRESS.md)（`scripts/track-progress.py` 自動產生）。

**Pipeline B（翻譯 + 註釋）啟動 2026-07-01**
- 翻譯（純翻譯，不解釋）→ `01-translation.md`
- 註釋（白話解釋 + 名相 + 學術爭議）→ `02-annotation.md`
- m3 角色：`tools/m3-translator-role.md` + `tools/m3-annotator-role.md`
- 派工腳本：`scripts/translate.py --task translate/annotate/both`
- 已實作 chunking（依 `=== N | ===` 章節分塊，>25k chars 自動切）

## 策略（2026-07-01）

**並行三 pipeline + 強追蹤防遺漏**：
- **A. 持續收集**（不中斷，繼續深挖 CBETA T18+ / 道藏 / 塔木德全 / 教父全集 等）
- **B. AI 翻譯**（已下載原文 → `01-translation.md`，邊收邊譯，不等收完）
- **C. 標籤 + 索引**（LLM 抽 semantic_tags、建跨宗教概念表、生 tag-index.json）

三條 pipeline 互不衝突（A 寫 `raw/`、B 寫 `01-translation.md`、C 寫 meta `semantic_tags`），可同時派工。

**防遺漏機制：** 寫 `scripts/track-progress.py`：
- 對照 v3 inventory 列出「該抓但還沒抓」清單，按宗教分類
- 識別「抓了但不在 v3」的部分（需補進 inventory）
- 失敗 batch 進 `failed.json` 隊列下次自動重試
- 每完成大批 → 重生 INDEX.md + 重跑 track-progress

## 並行任務優先順序

### Pipeline A（收集）— m3 持續跑

| 序 | 任務 | 量 |
|----|------|------|
| 1 | 補核心缺口：神道 + 兩河 + 古埃及 + 諾斯底 Nag Hammadi + 現代新興 + 巴哈伊 + 凱爾特 / 北歐 剩 + 印度教 Purana 18 | ~200 部 |
| 2 | CBETA T18-T55 全（密教 / 律 / 論 / 經疏 / 諸宗 / 史傳）| ~1300 部 |
| 3 | Sefaria Talmud Bavli 37 + Yerushalmi + Halakhah + Kabbalah 全 | ~600 部 |
| 4 | 教父全集 ANF + NPNF | ~38 卷 |
| 5 | 巴利 Vinaya / KN Jataka 547 故事 | ~1000 部 |
| 6 | 道藏精選按部類展開 ~500 部 | ~500 部 |
| 7 | 印度教 Sanskrit 缺漏（18 大 Purana 全、Itihasa 全、Tantra）| ~100 部 |
| 8 | 大正藏 T05-T07 大般若 600 卷（後期專項）| 600 部 |
| 9 | 韓國 / 日本 / 越南 / 蒙古 佛教祖師全集 | ~500 部 |
| 10 | 藏文 Kangyur 1100 + Tengyur 3400（後期專項）| ~5000 部 |

### Pipeline B（翻譯）— 從現在開始 m3 並行跑

優先翻譯：核心經典原文 → 繁中白話
- 道德經 ✓ 已抓 → 翻譯
- 心經（鳩摩羅什 + 玄奘）→ 翻譯
- 金剛經 → 翻譯
- 古蘭經（阿拉伯 → 繁中）
- 創世記（希伯來 → 繁中）
- 馬太福音（希臘 → 繁中）
- Bhagavad Gītā（Sanskrit → 繁中）
- Dhammapada（巴利 → 繁中）

每翻完一部 → commit + push。

### Pipeline C（標籤）— Sonnet 並行做

1. 訂跨宗教概念表（受控詞彙）→ `00-overview/concepts.md`
2. 每部 meta.json 加 `semantic_tags: []` + `summary_100w`
3. LLM 為已下載的核心經典先抽（道德經 / 論語 / 金剛經 / 創世記 / 古蘭開端 etc）
4. 反向索引：`00-overview/tag-index.json`


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
