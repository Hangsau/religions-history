# religions-history — AI 工作守則

> 給未來接手的 Claude / m3 / 其他 AI agent。
> 對外說明見 [`README.md`](./README.md)，狀態快照見 [`HANDOFF.md`](./HANDOFF.md)。

## 一句話

跨宗教**經文原文資料庫**：先收齊全本（每部一個 `translations/<slug>/`），再做 AI 翻譯 + 標籤 + 索引 + 網站。

## 當前階段

**P3 收集 + P4 翻譯 + P5 標籤 並行（不分先後）**

- 4683 部已收（27 宗教，約 644 MB）；148 部有完整翻譯，143 部翻譯＋雙標籤軸齊全
- Pipeline A：繼續收集（補核心缺口 + CBETA T18+ + Sefaria 深挖 + 教父全集 + 道藏 + 藏文等）
- Pipeline B：AI 翻譯（從核心經典開始）
- Pipeline C：語義標籤 + 跨宗教概念表
- 三條 pipeline 並行，互不等候

防遺漏：`scripts/track-progress.py` 對照 v3 inventory 自動算「該抓但沒抓」per 宗教，失敗進重試隊列。

運維入口見 `MAP.md`：生成前保留 MiniMax 5h/週額度各 10%，全域 quota/provider 等待只寫 `pipeline-runtime.json`，不可灌入 `pipeline-failed.json`；HALT、checkpoint、watcher 與桌面刊版共同保證後續可接手。

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

`meta.json` 兩層分類：

**粗分 `is_original_language: bool`**（歷史欄位，288/365 核心尚未回填）：
- **true**：原文（巴利、Sanskrit、Greek、Hebrew、Arabic、古典漢語、藏文、阿維斯塔語、Pahlavi 等）
- **false**：譯文（CBETA 漢譯佛經、和合本、Mahabharata Ganguli 英譯、Iliad Butler 英譯等）

**細分 `text_role`（2026-07-03 新增，enum，優先於粗分）**：
- `original`：成書原典文本。
- `translation`：從他語譯來（和合本＝`古典中文`、Vulgate＝`Latin`、19c 英譯等）。P4 只從 `original` 翻，此類僅作對照，不重譯。
- `transliteration`：音譯（大悲咒 / 陀羅尼類，漢字記梵音非表意）。**P4 禁意譯**，`translate.py` 短路原樣保留 + 附註，不呼叫 M3；梵文還原與釋義歸 `02-annotation.md`。
- `contested`：成書語言有學術爭議（如心經，Nattier 1992 疑梵本為漢譯回譯）。以 `composition_note` 說明，依主流傳統處理（心經＝漢傳主文本，古典漢語原樣保留）。
- **未標（null）＝安全預設**：不臆測。翻譯管線按 `language` 走（`古典漢語`/`古典中文` 原樣保留；外語直譯）；`load_slugs_by_tier` 排序把未知語言當 original-priority（原樣保留無損）。**不確定的一律不自動標**，交 `audit-core.py` 的「疑似音譯 / 待人工確認」清單人工判。

**判斷語言的關鍵訊號**：`古典中文`＝和合本中譯（translation）；`古典漢語`＝佛/道/儒漢傳原典（original）。兩者都是中文但角色相反，勿混。

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

## 既有下載器矩陣（15 個）

| Script | 來源 | 對應 |
|--------|------|------|
| `_polite.py` | — | 共用 UA + 禮貌睡眠 helper |
| `download-ctext.py` | api.ctext.org | 道教 / 儒教 漢系 |
| `download-wikisource.py --lang zh/ja/en/la/sa/el/ru/he/de/is/cy/pa` | Wikisource API | 漢系 / Vulgate / 世界古典原文（希臘/拉丁/古諾斯/威爾斯/古東斯拉夫/旁遮普古木基…）。per-entry `lang`＋`wikisource_titles`；backfill catalog `backfill-originals-ws.json` |
| `download-cbeta.py` | raw.githubusercontent.com cbeta-org/xml-p5 | 漢譯佛經（catalog 式單部）|
| `download-cbeta-full.py` | 同上 + GitHub Contents API | 漢譯佛經全卷自動爬 |
| `download-quran.py` | api.quran.com | 古蘭經 |
| `download-sefaria.py` | sefaria.org/api | 猶太教 catalog 式 |
| `download-sefaria-full.py` | sefaria.org/api 遞迴 | Sefaria 全圖書館 |
| `download-suttacentral.py` | suttacentral.net/api | 巴利三藏 Sujato |
| `download-gretil.py` | gretil.sub.uni-goettingen.de | 梵文印度教 + 部分佛教 |
| `download-sblgnt.py` | morphgnt/sblgnt GitHub | 希臘新約 |
| `download-avesta.py` | avesta.org | 瑣羅亞斯德 Avestan 原文（catalog `zoroastrian-avesta.json`）|
| `download-heimskringla.py` | heimskringla.no（HTML 爬，api.php 停用）| 北歐古諾斯語（詩體埃達逐篇 / Heimskringla / Völsunga；catalog `norse-heimskringla.json`）|
| `download-celt.py` | celt.ucc.ie（TEI，錨最後含「Author:」標題切檔頭）| 凱爾特古/中愛爾蘭語（catalog `celtic-celt.json`）|
| `download-sacred-texts.py` | sacred-texts.com | 13 個 catalog（瑣羅 / 耆那 / 古埃 / 古希臘羅馬 / 北歐 / 凱 / 諾 / 美洲 / 非洲 / 猶輔 / 錫輔 / 伊輔 / 巴哈伊）|
| `verify.py` | 本地 | SHA-256 + chapter count + size |
| `generate-index.py` | 本地 | 重生 INDEX.json + INDEX.md |
| `audit-core.py` | 本地 | 核心稽核；待補原文拆「可收」vs「已查明無乾淨來源」（`original-source-status.json`）|

## 後續階段（P4-P7）規則

### P4 AI 翻譯（經文式）

按 [`methodology/translation-workflow.md`](./methodology/translation-workflow.md) SOP，**權威翻譯規則見 [`tools/m3-translator-role.md`](./tools/m3-translator-role.md)**：
1. 讀 `raw/original.txt`（必是原文，不能是譯文）
2. 經文式翻譯：**古典漢語原樣保留**（禁白話化）、外語直譯保留名相原文、詩體保詩體、歧義標 `[歧義: A / B]`、`=== N | label ===` 原樣保留
3. 寫到 `translations/<slug>/01-translation.md`
4. 白話解釋 / 交叉比對 / 文化背景另歸 `02-annotation.md`（可延後做）

m3 適合大量跑翻譯。

### P5 語義標籤 + 索引（已實作）

- Layer 1 結構標籤（已有）：religion / tradition / language / era / genre
- Layer 2 語義標籤（**已實作**）：翻譯後即抽，權威規則見 [`tools/m3-tagger-role.md`](./tools/m3-tagger-role.md)
  - `semantic_tags`：受控詞彙，只填 [`00-overview/concepts.md`](./00-overview/concepts.md) 14 大類白名單（orchestrator 過濾違規 tag）
  - `keywords`：自由詞 5–15 個（神名 / 地名 / 術語 / 主題）
  - 兩者回填 `meta.json`（不動 `raw/original.txt`，不破 SHA-256）
- 反向索引：`scripts/build-tag-index.py` → `00-overview/{tag-index.json, keyword-index.json}`

### 自動化：tier 佇列協調器

`scripts/auto-pipeline.py` 串 P4→P5，tier 佇列驅動（核心先跑），可續跑（`--skip-done`）、容錯（`logs/pipeline-failed.json`）、只 add 本次路徑不與 Pipeline A 收集互踩。狀態見 `00-overview/PIPELINE_STATUS.md`（自動生）。核心稽核見 `scripts/audit-core.py` → `00-overview/core-manifest.md`。

```bash
PYTHONIOENCODING=utf-8 python scripts/auto-pipeline.py --tier 核心          # 全量核心
PYTHONIOENCODING=utf-8 python scripts/auto-pipeline.py --tier 核心 --limit 3 --no-push  # 小批驗證
```

### P6 宗教心理學

- 跨宗教比較：信仰 / 行為 / 心流 / 神聖體驗 / 靈性心理學
- 寫到 `11-psychology/`
- **方法＝由下而上，不從理論預設分類**：先造「人實際會問的問題」語料，讓分類自己浮現。組織軸＝**人從生到死的問題**（非宗教、非心理學流派），經文＝歷代對這些問題的回答，心理學＝解讀透鏡（非第三種答案）。**已收斂在 13 個大領域**（見 `11-psychology/question-themes.md`，已用極端人格 100 題壓力測試、零新增大類）。
- 心理學領域受控詞彙未來寫 `00-overview/concepts-psychology.md`，**與比較宗教學 `concepts.md` 14 類並存**（後者給學者精確標，前者給一般人入口）；標經文允許多標籤。現況與待辦見 `11-psychology/README.md`。

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
