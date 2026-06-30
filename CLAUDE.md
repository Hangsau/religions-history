# religions-history — AI 工作守則

> 給未來接手的 Claude / m3 / 其他 AI agent。
> 對外說明見 [`README.md`](./README.md)，狀態快照見 [`HANDOFF.md`](./HANDOFF.md)。

## 一句話

跨宗教**經文原文資料庫**：先收齊全本（每部一個 `translations/<slug>/`），再做 AI 翻譯 + 標籤 + 索引 + 網站。

## 當前階段

**P3 收集階段尾聲 → P4 翻譯階段過渡**

- ~1900 部已收（全部 GitHub 版本控制）
- 補核心缺口中（神道 / 兩河 / 古埃及 / 現代新興 / Nag Hammadi 全 52 篇）
- 補完後切到 P4 AI 翻譯

## 工作守則

### 1. 收集任何新經文前

- 查 [`methodology/per-religion-scriptures.md`](./methodology/per-religion-scriptures.md) v3 — 該宗教應有什麼？
- 查 [`00-overview/INDEX.md`](./00-overview/INDEX.md) — 已收哪些？
- 該宗教有專屬 catalog `scripts/catalog/<religion>.json` 嗎？沒有就新建
- 該來源已有 downloader 嗎？沒有就寫一個

### 2. 寫新 downloader 的標準形式

仿 `scripts/download-sacred-texts.py`（最完整）：
- 從 `_polite import USER_AGENT, polite_sleep`（共用 UA + jitter + 100-req 休息）
- catalog 式：`scripts/catalog/<religion>.json` 列每部 entry
- skip-if-verified（不重抓）
- 5 次指數 backoff（10s → 480s）處理 429/403/503
- 每部產出 `translations/<slug>/{meta.json, raw/original.txt, raw/source-urls.txt, raw/checksums.sha256}`
- meta.json 用 `scripts/meta_template.json` schema（含 `is_original_language` 欄位）

### 3. 區分原文 vs 譯文

`meta.json` 必填 `is_original_language: bool`：
- **true**：原文（巴利、Sanskrit、Greek、Hebrew、Arabic、古典漢語、藏文、阿維斯塔語、Pahlavi 等）
- **false**：譯文（CBETA 漢譯佛經、和合本、Mahabharata Ganguli 英譯、Iliad Butler 英譯等）

**P4 翻譯只能從原文翻**，譯文只作 cross-check。違規會被推回。

### 4. m3 派工原則

詳見 [`tools/m3-executor-role.md`](./tools/m3-executor-role.md)。

- 適合派 m3：跑既有 downloader 抓資料、跑 verify、commit + push
- 不適合派 m3：寫 downloader logic、設計 catalog 結構、debug 複雜錯誤、解釋給用戶
- 派 m3 用 `claude-m3 -p --permission-mode bypassPermissions "..."` 從 Bash 起 background
- m3 跑時不要主 session 同步跑同一個 source（避免 rate limit 翻倍）

### 5. 爬蟲倫理（**強制**）

所有 downloader **必須**：
- 用 `_polite.py` 提供的 `USER_AGENT`（含 contact email + GitHub repo）
- 用 `_polite_sleep_inline()` 或同效 helper（jitter + 每 100 req 自動休 30s）
- 處理 429/403/503 退避
- 不繞 robots.txt / 不偽裝成 search bot / 不用 proxy rotation

被站方明確 ban → **不重試**，切換來源（如 ctext → GitHub mirror）。

### 6. commit + push 紀律

- 每完成一個小批（5-30 部）即 commit + push
- commit message 中英都可，重點寫**做了什麼**而非「修了 bug」（細節留 git diff）
- push 前一定跑 `verify.py --all` 確保全綠
- 完成大階段後跑 `generate-index.py` 重生 INDEX，再 commit

### 7. 文件對齊（**重要**）

結構性改動後**主動更新**：
- `README.md` — 對外狀態 / 統計
- `HANDOFF.md` — 給下次接手的狀態快照
- `00-overview/INDEX.md` — 自動生（`generate-index.py`）
- `methodology/per-religion-scriptures.md` — 若新增宗教 / 來源

不要等到用戶問才改文件。

---

## 環境

- **Platform**：Windows 11 + Git Bash + Python 3.12
- **Encoding**：Windows console 是 cp950，所有 Python 必須 `PYTHONIOENCODING=utf-8 python ...`
- **EOL**：`.gitattributes` 強制 LF（防 CRLF 破壞 SHA-256）
- **GitHub**：https://github.com/Hangsau/religions-history（公開）

## 既有下載器矩陣（12 個）

| Script | 來源 | 對應 |
|--------|------|------|
| `_polite.py` | — | 共用 UA + 禮貌睡眠 helper |
| `download-ctext.py` | api.ctext.org | 道教 / 儒教 漢系 |
| `download-wikisource.py --lang zh/ja/en/la/sa` | Wikisource API | 道教 / 儒教 / 基督教中譯 / 拉丁 Vulgate / 神道 / 世界古典英譯 |
| `download-cbeta.py` | raw.githubusercontent.com cbeta-org/xml-p5 | 漢譯佛經（catalog 式單部）|
| `download-cbeta-full.py` | 同上 + GitHub Contents API | 漢譯佛經全卷自動爬 |
| `download-quran.py` | api.quran.com | 古蘭經 |
| `download-sefaria.py` | sefaria.org/api | 猶太教 catalog 式 |
| `download-sefaria-full.py` | sefaria.org/api 遞迴 | Sefaria 全圖書館 |
| `download-suttacentral.py` | suttacentral.net/api | 巴利三藏 Sujato |
| `download-gretil.py` | gretil.sub.uni-goettingen.de | 梵文印度教 + 部分佛教 |
| `download-sblgnt.py` | morphgnt/sblgnt GitHub | 希臘新約 |
| `download-sacred-texts.py` | sacred-texts.com | 13 個 catalog（瑣羅 / 耆那 / 古埃 / 古希臘羅馬 / 北歐 / 凱 / 諾 / 美洲 / 非洲 / 猶輔 / 錫輔 / 伊輔 / 巴哈伊）|
| `verify.py` | 本地 | SHA-256 + chapter count + size |
| `generate-index.py` | 本地 | 重生 INDEX.json + INDEX.md |

## 後續階段（P4-P7）規則

### P4 AI 翻譯

按 [`methodology/translation-workflow.md`](./methodology/translation-workflow.md) SOP：
1. 讀 `raw/original.txt`（必是原文，不能是譯文）
2. AI 翻成繁中白話
3. 寫到 `translations/<slug>/01-translation.md`
4. 對照既有譯本（CBETA 漢譯 / 和合本 / Mahabharata Ganguli / Iliad Butler 等）標差異
5. 標歧義處（`[歧義]`）

m3 適合大量跑翻譯。

### P5 標籤索引

- Layer 1 結構標籤（已有）：religion / tradition / language / era / genre
- Layer 2 語義標籤（待加）：跨宗教概念表（救贖 / 創世 / 戒律 / 末世 / 神聖體驗 等 14 大概念）
- LLM 抽 semantic_tags 填回 meta.json
- 反向索引：`00-overview/tag-index.json`

### P6 宗教心理學

- 跨宗教比較：信仰 / 行為 / 心流 / 神聖體驗 / 靈性心理學
- 寫到 `11-psychology/`

### P7 網站

按 [`STRATEGY.md §2`](./STRATEGY.md) — Astro + Pagefind + Cloudflare Pages 全靜態，從 `translations/` 自動生頁面。

## Anti-pattern（**禁止**）

- ❌ 用 `python-requests/2.x` 這種預設 UA（會被快速 ban）
- ❌ `time.sleep(N)` 不加 jitter（規律 pattern 易識別）
- ❌ 「漢譯佛教」「巴利佛教」「藏文佛教」當三個並列宗教（佛教是一個宗教，三個傳統）
- ❌ 把 CBETA 漢譯當佛教原文（漢譯是「漢傳佛教的傳統文本」+「對 Indian Buddhism 而言是譯文」，雙重身分要明標）
- ❌ 直接覆寫 meta.json 不跑 verify（破壞 SHA-256）
- ❌ 同源並行雙跑（rate limit 翻倍）
- ❌ 預先優化未證實的瓶頸（先做出來再說）
- ❌ 改 `.gitattributes` 把 LF 規則拿掉（會破 SHA-256 跨平台一致）
