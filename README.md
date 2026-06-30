# religions-history

> 跨時空、跨文化、跨宗教的**世界宗教經文原文資料庫** —
> 從史前到現代，盡量收齊全本，建立可分析、可比對、可搜尋的研究基礎。

當前狀態：**~1900+ 部經文 / ~250 MB 原文 / 20 宗教傳統**，全部 git 版本控制 + SHA-256 校驗。

詳細索引見 [`00-overview/INDEX.md`](./00-overview/INDEX.md)（自動產生）。

---

## 專案目標

1. **蒐集所有宗教的經文原文** — 不只代表性精選，目標是逐部、逐卷展開
2. **用 AI 翻譯原文**，不沿用既有譯本（譯本只作 cross-check）
3. **跨宗教做主題分析** — 心理學 / 倫理 / 末世論 / 神聖體驗 比較
4. **建好標籤、索引、搜尋** — 未來可做查詢、比對、視覺化
5. **隨時可擴充** — 模組化架構，多源、多語言、多版本並行

不涉入：宗教比較優劣、護教 / 破教、單一立場宣揚。

---

## 涵蓋宗教（20 主要傳統）

| 宗教 | 主要傳統 / 來源 | 完成度（核心+次要）|
|------|-----------------|--------------------|
| 佛教 | 漢傳（CBETA）/ 巴利（SuttaCentral）/ 梵文（GRETIL）| 漢傳深挖中 41% / 巴利 主集完成 |
| 道教 | ctext + Wikisource | 核心 + 次要完成（道藏 5305 待） |
| 儒教 | ctext + Wikisource | 核心 + 次要完成 |
| 印度教 | GRETIL Sanskrit | 4 Vedas + 11 Upanishads + 史詩 + 6 哲學經 |
| 猶太教 | Sefaria | Tanakh + Mishnah 63 + 諸家注疏（深挖中）|
| 基督教 | 希臘 NT (SBLGNT) + 拉丁 (Vulgate) + 中文 (和合本) | 三語聖經完整 |
| 伊斯蘭 | Quran.com + sacred-texts | 古蘭原文 + 部分聖訓 + 蘇菲 |
| 瑣羅亞斯德 | sacred-texts SBE | Avesta + Pahlavi 主要 |
| 古希臘羅馬 | sacred-texts + en.ws | Homer / Hesiod / Ovid / Virgil / Plato / Plotinus |
| 北歐 | sacred-texts + en.ws | Edda + Volsunga + Heimskringla |
| 凱爾特 | sacred-texts + en.ws | Mabinogion + Cuchulain + Carmina Gadelica |
| 諾斯底 / 赫爾墨斯 | sacred-texts | Mead Hermetica + Gnostic Remains |
| 美洲 (瑪雅/阿茲/印加/北美) | sacred-texts | Chilam Balam + Codex + 北美各部落神話 |
| 非洲 (約魯巴/班圖/西非) | sacred-texts | Ife + Hausa + Dahomey + Yoruba |
| 耆那教 | sacred-texts | SBE 22 + 45 |
| 錫克教 | en.ws + sacred-texts | Macauliffe + Guru Granth Sahib |
| 巴哈伊 | sacred-texts | 部分（reference.bahai.org 待補）|
| 現代新興 | en.ws | 摩門經 + 無價珍珠（其他待補）|
| 神道 | — | 0（NDL 待寫下載器）|
| 古埃及 | sacred-texts | 死者之書 + Pyramid Texts（其他待補）|

---

## 倉庫結構

```
religions-history/
├── README.md                  ← 本檔
├── CLAUDE.md                  ← AI 工作守則
├── PLAN.md                    ← 階段規劃
├── HANDOFF.md                 ← 狀態快照（每次工作結束更新）
├── STRATEGY.md                ← 蒐集 / 網站 / 標籤 / 派工 策略
│
├── 00-overview/               ← 自動產生的索引 + 總覽
│   ├── INDEX.md                  ← 全經文清單 + 統計（自動生）
│   ├── INDEX.json                ← 同上 JSON 版
│   ├── religions-inventory.md    ← 宗教清單
│   ├── scriptures-inventory.md   ← 經文清單
│   ├── timeline.md
│   ├── classification.md
│   └── version-issues.md
│
├── methodology/               ← 方法論
│   ├── per-religion-scriptures.md    ← v3 全本目錄 (~2400 entries)
│   ├── per-religion-scriptures-v2-archive.md  ← 舊版 v2 精選版
│   ├── translation-workflow.md       ← AI 翻譯 SOP
│   ├── download-plan.md
│   ├── sequencing-plan.md
│   └── version-problems.md
│
├── tools/
│   └── m3-executor-role.md    ← m3 派工角色指令
│
├── scripts/                   ← 下載 + 驗證腳本
│   ├── _polite.py                ← 共用 UA + jitter + 自動休息
│   ├── download-ctext.py         ← api.ctext.org
│   ├── download-wikisource.py    ← Mediawiki API（zh/ja/en/la/sa）
│   ├── download-cbeta.py         ← CBETA TEI（單部）
│   ├── download-cbeta-full.py    ← CBETA 全卷自動爬
│   ├── download-quran.py         ← Quran.com API
│   ├── download-sefaria.py       ← Sefaria（catalog 式）
│   ├── download-sefaria-full.py  ← Sefaria 全圖書館遞迴
│   ├── download-sblgnt.py        ← 希臘新約 morphgnt
│   ├── download-suttacentral.py  ← 巴利三藏 Sujato
│   ├── download-gretil.py        ← 梵文 GRETIL
│   ├── download-sacred-texts.py  ← sacred-texts.com（多宗教 catch-all）
│   ├── verify.py                 ← SHA-256 + 章節數 + 大小驗證
│   ├── generate-index.py         ← 重生 INDEX.json + INDEX.md
│   ├── catalog/                  ← 各宗教 catalog JSON
│   └── meta_template.json        ← meta.json schema
│
├── translations/              ← 經文資料庫
│   └── <slug>/
│       ├── meta.json             ← 16 欄位 metadata（schema 見 meta_template.json）
│       ├── raw/
│       │   ├── original.txt         ← 原語言文本，每章 === N | <label> === 分隔
│       │   ├── source-urls.txt      ← 抓取 URL 紀錄
│       │   ├── checksums.sha256     ← SHA-256 校驗
│       │   └── translation-en.txt   ← 對照英譯（Sefaria/SuttaCentral 提供）
│       └── 01-translation.md     ← AI 翻譯（P4 階段才寫）
│
└── 11-psychology/             ← 宗教心理學專題（P6 階段才動）
```

---

## 工作流程

### Phase 已完成

| Phase | 工作 |
|-------|------|
| **P0-P2** | 框架、宗教 / 經文清單、方法論文件 |
| **P2.5** | v3 全本目錄改寫（`methodology/per-religion-scriptures.md`）|
| **P3 A-C** | 各宗教核心 + 次要下載，主流深挖（漢傳佛教 T01-T17、Sefaria Mishnah 全展開）|

### Phase 進行中

- **P3 D-E** 補核心缺口：神道、兩河、古埃及、現代新興、巴哈伊、Nag Hammadi 全 52 篇

### Phase 後續

| Phase | 工作 |
|-------|------|
| **P4** | AI 翻譯（按 `methodology/translation-workflow.md`：原文 → AI 譯 → 既有譯本 cross-check）|
| **P5** | 跨宗教交叉專題（救贖 / 創世 / 戒律 / 末世 / 神聖體驗）|
| **P6** | 宗教心理學分析（11-psychology/）|
| **P7** | 網站 / 視覺化（Astro + Pagefind + Cloudflare Pages，見 STRATEGY.md §2）|

---

## 如何使用本資料庫

### 取資料

```bash
git clone https://github.com/Hangsau/religions-history
cd religions-history

# 列出所有經文
ls translations/

# 看單部經文 metadata
cat translations/tao-te-ching/meta.json

# 看原文
cat translations/tao-te-ching/raw/original.txt
```

### 跑驗證

```bash
PYTHONIOENCODING=utf-8 python scripts/verify.py --all
```

### 重生索引

```bash
PYTHONIOENCODING=utf-8 python scripts/generate-index.py
```

### 跑新下載

```bash
# 從特定宗教 catalog 全跑
PYTHONIOENCODING=utf-8 python scripts/download-sacred-texts.py --religion 瑣羅亞斯德 --all

# 從 CBETA 補某卷
PYTHONIOENCODING=utf-8 python scripts/download-cbeta-full.py --volume T18
```

---

## 資料品質保證

- **SHA-256 校驗** — 每部經文 `checksums.sha256` 確保跨平台一致
- **`.gitattributes` 強制 LF EOL** — 防 Windows CRLF 破壞 SHA
- **chapter count / size 三層驗證** — `verify.py` 比對 meta.json 宣告
- **原文 vs 譯文標記** — meta.json `is_original_language` 欄位明確區分
- **版本識別** — meta.json `version` 欄位（王弼本 / Schøyen 抄本 / Pickthall 英譯 etc.）

---

## 爬蟲倫理

所有下載器：
- User-Agent 標明 `religions-history-research/0.1 (academic research; contact: psyhangsau@gmail.com)`
- 每請求間隔 + 隨機 jitter（不規律 pattern）
- 每 100 次請求自動暫停 30 秒（不集中 hammer）
- 5 次指數 backoff（10 → 480s）處理 429/403/503
- skip-if-verified 不重複請求

---

## 引用

若使用本資料庫，請註明：

```
religions-history (Hang Sau, 2026), https://github.com/Hangsau/religions-history
SHA-256 of original.txt + commit hash for reproducibility.
```

各部經文原始來源版權見 `meta.json` 的 `license` 欄位。

---

## 授權

- **程式碼**（`scripts/`、`tools/`、`methodology/`）：MIT
- **資料**（`translations/`、`00-overview/`）：依各部經文原始來源（CC BY-SA / CC BY-NC / Public Domain 等，見 meta.json）
- **整理結構與選編**：CC BY-SA 4.0

---

## 維護者

- Hang Sau（psyhangsau@gmail.com）
- 協作：Claude（Anthropic, Sonnet / Opus）、MiniMax-M3（minimax.io）
