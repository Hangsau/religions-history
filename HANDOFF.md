# HANDOFF — religions-history

> 狀態快照。每次工作結束更新。
> 規範見 `CLAUDE.md` + `PLAN.md` + `STRATEGY.md`。

## 當前狀態（2026-07-03 重生統計）

**4207 部 / 22 宗教 / ~517 MB / 已 AI 譯註 23 部**（原文/譯文粗分見 INDEX；對齊後 text_role 更準）

詳見即時 [`00-overview/INDEX.md`](./00-overview/INDEX.md) 自動產生統計。
進度追蹤見 [`00-overview/PROGRESS.md`](./00-overview/PROGRESS.md)（`scripts/track-progress.py` 自動產生）。

**桌面刊版（狀態看板）= `scripts/status_gui.py`**
- 常駐 Tkinter GUI，視窗標題「religions-history 刊版」，每 30 秒自掃全庫刷新。**是進度監控牆，不是經文閱讀器。**
- 啟動：雙擊專案根 `狀態看板.bat`（背景 `pythonw`，無主控台）；或 `PYTHONIOENCODING=utf-8 pythonw scripts/status_gui.py`。
- 顯示：頂部總量（部/宗教/MB）＋ 對齊覆蓋率（各 meta 欄位回填 %）＋ M3 分類進度（tier×era+genre+tags 三齊全）＋ Pipeline A 收集動態（最新收錄/近 30 分/日誌尾）＋ 翻譯進度（translation_status==done）＋ classify 背景管線。
- 資料 helper 沿用 `scripts/status.py`（`load_all` / `filled` / `ALIGN_FIELDS` / `log_ok_count` / `log_tail`）；GUI 只管畫面。綠條＝≥99.5% 完成、琥珀＝進行中。

**Pipeline B（翻譯 + 註釋）啟動 2026-07-01**
- 翻譯（純翻譯，不解釋）→ `01-translation.md`
- 註釋（白話解釋 + 名相 + 學術爭議）→ `02-annotation.md`
- m3 角色：`tools/m3-translator-role.md` + `tools/m3-annotator-role.md`
- 派工腳本：`scripts/translate.py --task translate/annotate/both`
- 已實作 chunking（依 `=== N | ===` 章節分塊，>25k chars 自動切）

**Pipeline B+C 收斂：核心先行 + 標籤內建（2026-07-03）**
- **收斂策略**：目標不變（收全經文），但翻譯 + 標籤先集中跑各宗教**核心經文**（`meta.json` 的 `tier == 核心`，365 部）。
- **tier 佇列協調器 `scripts/auto-pipeline.py`**：每部 translate（`01-translation.md`，經文式）→ tag（`semantic_tags`/`keywords` 回填 `meta.json`）→ 批次重生反向索引 → commit + push。可續跑（`--skip-done` 預設）、容錯（`logs/pipeline-failed.json`）、只 add 本次路徑（不與 Pipeline A 互踩）。
  - `PYTHONIOENCODING=utf-8 python scripts/auto-pipeline.py --tier 核心`（全量核心）
  - `... --limit 3 --no-push`（小批驗證）
- **Pipeline C 標籤已實作**：`tools/m3-tagger-role.md`（角色）+ `00-overview/concepts.md`（14 類白名單）+ `scripts/build-tag-index.py`（生 `tag-index.json` / `keyword-index.json`）。標籤只改 `meta.json`，不動 `raw/original.txt`，不破 SHA-256。
- **核心稽核**：`scripts/audit-core.py` → `00-overview/core-manifest.md`（各宗教核心數 / 已譯 / 已標 + 缺口分析）。
- **即時進度**：`00-overview/PIPELINE_STATUS.md`（協調器自動生，勿手改）。
- **註釋（`02-annotation.md`）可延後**：收斂期先完成 譯 + 標，註釋另跑。
- **已知收集品質缺口**：部分核心 slug 的 `raw/original.txt` 只有目錄（如 `huangting-neijing` 僅 761 bytes 章目，現排在核心佇列第一），翻譯會偏薄 —— 屬 Pipeline A 下載不全，非翻譯機制問題，需回頭補抓正文。

**text_role 分類 + 佇列排序（2026-07-03）**
- **`meta.json` 新增 `text_role`（enum：original / translation / transliteration / contested）+ `composition_note`**（additive，不破 SHA-256）。細分優先於粗分 `is_original_language`（後者 288/365 核心未回填）。分類規則見 `CLAUDE.md §3`。
- **音譯短路**：`translate.py` 對 `text_role == transliteration` 原樣保留 + 附註、**不呼叫 M3**（大悲咒 / 陀羅尼類禁意譯）。角色檔 `m3-translator-role.md` 規則 0 已加音譯 / contested / 和合本(古典中文) 路由。
- **佇列排序**：`load_slugs_by_tier` 改「原文優先 + 短經優先」。核心 365＝177 原文（小→大先跑）+ 188 譯本（和合本 `古典中文` + Vulgate `Latin`，殿後）。關鍵訊號：`古典中文`＝和合本譯本，`古典漢語`＝漢傳原典。
- **安全網**：沒把握不自動標；`audit-core.py` 新增「疑似音譯 / 咒語，待人工確認 text_role」清單（標題含 咒 / 陀羅尼 / 真言 / mantra）+ `text_role` 覆蓋統計。語料庫 250+ 陀羅尼文本幾乎全在 `tier=總集逐部`，非核心，待跑到該 tier 時人工確認再標。
- **已分類**：`heart-sutra-kumarajiva` + `heart-sutra-xuanzang` → `contested`（Nattier 假說，漢傳主文本古典漢語原樣保留）。

**Pipeline A：古代宗教核心英譯收集（2026-07-03，本 session 共 +27 部）**
- **原則**：原文優先，但原文難尋時先收英譯 fallback（誠實標 `is_original_language=false`），原文待 Phase 2 補。用戶明示「拿到英譯再補原文，也是沒辦法中的辦法」。全走 `download-sacred-texts.py`（Cloudflare-bypass UA + 禮貌節奏），逐部 verify PASS。
- **兩河（+7）** `mesopotamia-st.json`：核心＝創世七碑(Enuma Elish)/吉爾伽美什史詩/漢摩拉比法典；次要 4。
- **神道（+2）** `shinto-st.json`：核心＝古事記(Chamberlain 英譯,192 章)；次要＝古語拾遺。（日文原文條目仍在 `shinto-ws.json` deferred 待 NDL。）
- **古埃及（+12，核心 2→8）** `egypt-st.json`：新核心＝諸神傳說/門之書/阿姆杜阿特之書/埃及天堂地獄/伊西斯悲歌/葬祭儀軌；次要＝魔法/智慧書/羅塞塔石碑等。
- **斯拉夫（+6，核心 0→2）** `slavic-st.json`：異教無成文經典，以史詩＋民族誌為主要來源。核心＝伊戈爾遠征記/俄羅斯人民之歌(Ralston)；次要 4 部民間故事。
- **CATALOG_MAP** 已加：兩河/神道/斯拉夫 三 catalog。核心數 365→377。跑著的翻譯管線 `--skip-done` 下輪重算佇列時自動接手（本次已在跑的 run 佇列在啟動時就固定，故要等下一輪或重啟才翻到這 27 部）。
- **爬蟲節奏**：本 session 已做 4 次 sacred-texts 拉取，之後暫停爬取讓 rate 冷卻（用戶提醒「別撞攔截」）。

**原文補收進度（2026-07-03，sibling-original 管線）**
- 用戶指令「補阿 還有要加的也去加一加 可以不要便宜行事」→ 開始真收原文，非只標籤。
- **模型**：原文以「新 sibling slug（`<英譯slug>-<lang>`，`text_role=original`，`original_of` 反向連結英譯 slug）」入庫，英譯留作對照；`audit-core.py` 見 `original_of` 即把對應英譯移出待補。`original_of` 可為 list（一原典對多英譯，如 homer-greek→4 荷馬英譯）。
- **download-wikisource.py 擴充**：per-entry `lang`（entry 自帶語言，不靠全域 --lang）、`text_role`/`is_original_language`/`original_of` 寫入 meta；新增 el/ru/he/de/is/cy 端點。catalog＝`scripts/catalog/backfill-originals-ws.json`（religion key「原文補收」）。
- **本 session 已收 + verify PASS（待補 54→46）**：Ovid 變形記(la,15卷)、Virgil 伊尼德(la,12卷)、Plato 理想國/會飲/斐多(el)、Mabinogion 威爾斯兩卷(cy)；並將既在庫的 homer-greek(希臘伊利亞德+奧德賽,48卷) 連結 4 荷馬英譯 slug、language 由誤標 English 改「希臘」。
- **反 便宜行事 做法**：每部先 live API 探 title/subpages/實際內容（`get_page_text`）確認是原生文字才入 catalog，不猜標題。
- **Wikisource 已探明但緩收**：Kojiki（ja `古事記 (原文)` 是紅連結，全文不在 WS，需 NDL）；Heimskringla（is 852 巢狀子頁，需 saga 級 curated catalog）；Slovo（ru `/Текст` 可取但頁首有「Другие переводы」導航塊需加強 strip）；Snorra Edda（is 散文埃達，子頁乾淨，非待補 slug 但值得加）。

**Phase 2 原文層待辦（需新寫 downloader / 專屬來源，剩 46 部）**
- **可續收（Wikisource，需 curated catalog / strip 強化）**：斯拉夫 Slovo(ru)、北歐 Snorra/Poetic Edda 逐篇(is)。
- **需新 downloader（專屬 repo）**：耆那 Prakrit→GRETIL（downloader 已存在，缺 catalog+URL 探查）；瑣羅亞斯德 Avestan/Pahlavi→avesta.org/TITUS；諾斯底/赫爾墨斯 Coptic/Greek→Perseus/Coptic SCRIPTORIUM；希臘 Plotinus/Sibylline→Perseus（不在 el.WS）；錫克 Gurmukhi→SriGranth。
- **象形/楔形（觸及用戶「象形文取最早或最新來處理」決策）**：古埃及→TLA 轉寫；兩河→ETCSL 蘇美語轉寫。
- **無書寫系統→改標非待補**：非洲(口傳)、印加(無文字)、部分阿茲特克/瑪雅——應 `text_role=original`（口傳英譯即現存最早文本）脫離待補。
- **兩河原文**：ETCSL（Oxford 蘇美語轉寫）— 無 downloader。
- **神道原文**：NDL / ja.wikisource 日文全文（古事記 / 日本書紀 / 延喜式）— ja.wikisource 多僅目錄，全文在 NDL，無 downloader。
- **Popol Vuh（瑪雅）**：**不在 sacred-texts**（nam/maya 僅 cbc/ybac/mhw 三部已收），需另找專屬來源（Ximénez 手稿 K'iche' 原文 / 公版英譯）。
- **北歐**：散文埃達（Prose Edda, Snorri）為主要缺項；sacred-texts neu/ice 為 landing page，路徑未清，需再查（詩體埃達 neu/pre 已收）。
- **分類折疊（非真缺口）**：瑪雅/阿茲特克/印加 收在 `美洲` 傘下（`美洲` 已為合法 enum 值）、赫爾墨斯 收在 `諾斯底` 傘下，均已在翻譯佇列中；如要作為獨立宗教瀏覽需另議 religion 欄位重分類（影響 INDEX/tag-index，未做）。

**LLM fleet 擴充（討論中，2026-07-03）**：用戶考慮加便宜 worker 分攤 MiniMax-M3 流量。關鍵發現：`translate.py:206 call_m3` 靠 `claude -p` + `ANTHROPIC_BASE_URL/AUTH_TOKEN/MODEL` 打 MiniMax Anthropic-相容端點 → 任何有 Anthropic 端點的廠商（DeepSeek/智譜 GLM-4.6/Moonshot Kimi K2，皆中文母語且便宜）換三行 env 即 drop-in，加 profile pool 約十幾行。建議分工：英譯 fallback→便宜 worker；難古典原文→留強模型；漢傳/和合本 原樣保留不耗 LLM。待用戶決定 provider + 辦 key。

**資料對齊 Alignment（2026-07-03，用戶要求「把所有資料都對齊以利撈取」）**
> MiniMax M3 同有 5H/7D 限制（約 Claude Pro 5×，非無限）。對齊按 token 成本分層：0-token 規則優先做滿，M3 只留給小輸出分類。
- **Layer 0（0-token 規則，已完成 push）**：
  - `scripts/align-metadata.py`：由 `language` 回補 `text_role`（0%→4128）+ `is_original_language`（缺 366→缺 76）。高信心語言映射，`Latin`(76，Vulgate/古典拉丁歧義) 留白交人工。
  - religion enum 違規修正：`佛教-巴利`(39)→`佛教`+tradition`巴利`（同步改 `buddhism-pali.json` / `download-suttacentral.py` 防回歸）；`美洲`(6，americas umbrella) 加入 `meta_template` enum。現 enum 違規 0，22 宗教。
  - `genre` 0-token 子集：猶太 `Halakhah`/`Mishnah`→`law-code`、`Commentary`/`Midrash`/`Talmud`→`commentary`，共 1329 部(31.6%)。
- **Layer 1（詞彙已定義，已 push）**：`00-overview/era-genre-vocab.md`：`era` 7 桶 + `genre` 11 類，加入 `meta_template` enum。
- **Layer 2（待跑，M3 小輸出，因配額暫緩等用戶過目詞彙）**：
  - `era`（全 4207 皆 null，version_date 僅 3% 且異質，幾乎不可規則化）→ M3 讀原文首段+標題分類。
  - `genre` 其餘 2879 null（CBETA 漢傳 2429 混經/律/論、Greek NT、Pali、古代宗教）→ M3。
  - `semantic_tags`/`keywords`（0.8%）→ M3 從**原文**抽（不必等全文翻譯），與 era/genre 同一次 M3 呼叫省配額。
  - **建議**：Layer 2 三項合併成單一 M3 classify 呼叫/部（讀原文首 N 段 → 回 era+genre+tags+keywords，白名單過濾），核心 tier 先跑。

**唯一英譯本核心政策寫死 + huangting 補抓（2026-07-03）**
- **huangting-neijing 補抓**：舊 catalog `wikisource_title=黃庭內景經` 只是章目錄頁（761B）；正文在 `太上黃庭內景玉經/<章>` 子頁面。已改標題重抓（15251B / 37 章）+ 重譯 + 重標。掃過全核心，`raw<2KB` 僅此一部是真薄譯，其餘 6 部（心經 / 2-3 約翰 / 陰符經）本就短，正常。
- **止血復發的「分類問題」**：英譯本核心（古埃及 / 兩河 / 北歐 / 希臘 / 神道 等，`text_role=translation` 且語料庫無原文）政策從沒寫進工具，每次 audit 都被當開放缺口重問。三層根因對應解法：
  1. **報表過時** → `auto-pipeline.py:rebuild_indexes` 每批加跑 `audit-core.py`，`core-manifest.md` / `original-text-todo.md` 納入 commit，永不過時。（舊 core-manifest 顯示已譯 53/已標 33，實為 77/376）
  2. **英譯本無政策** → `m3-translator-role.md` 加 English 列＝**英→中二手翻譯**，header 標「原文待補」。落實用戶「真的沒辦法先用英文」。
  3. **「補原文」無落腳處** → `audit-core.py` 生持久 `00-overview/original-text-todo.md`（59 部核心 / 15 宗教）＝ Pipeline A 補抓待辦。落實「還是要補原文」。
- **唯一 vs 冗餘判定**（確定性）：宗教有 ≥1 `text_role=original` 核心 → 譯本冗餘對照（基督教有 sblgnt 希臘 / 印度教有梵文）；0 原文核心 → 全部唯一英譯，該翻+補原文。
- **已知 caveat（待修 text_role 誤標）**：`book-of-mormon-1830`（摩門經 1830）英文即原典（Joseph Smith 英文著作），被 heuristic 誤標 `translation` → 誤列入待補原文；`pearl-of-great-price` 部分同理。應改 `text_role=original` 使其脫離待補清單（英文仍需英→中翻譯）。homer-greek 名為「希臘原文」實為 Butler 英譯，命名待正。

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

### Pipeline C（標籤）— 已併入 auto-pipeline.py（2026-07-03）

1. 跨宗教概念表（受控詞彙）→ `00-overview/concepts.md` ✓
2. 翻譯後即抽 `semantic_tags`（白名單過濾）+ `keywords`（自由詞）回填 meta.json ✓
3. 協調器對核心 tier 逐部跑（translate→tag）✓
4. 反向索引：`scripts/build-tag-index.py` → `00-overview/{tag-index.json, keyword-index.json}` ✓


## 進行中（m3 背景，2026-07-03）

Pipeline A 仍在跑（logs/pipeline-a-*.log 持續變動）：
- CBETA T13-T17（大集 + 經集）— 完成
- CBETA T18-T55（密教/律/論/經疏/諸宗/史傳）— 已抓大批（佛教漢傳達 2429 部）
- 卍續藏 X01-X88 — downloader bug 已修，抓 111 部
- Sefaria Mishnah 63 + Talmud + Halakhah 88 + Midrash 36 + 諸家注疏 1103 — 進行中（猶太教達 1384 部）
- 伊斯蘭輔助 7 部 — 完成

Pipeline B 已 AI 譯註 23 部：analects, bhagavad-gita, brihadaranyaka-upanishad, dhammapada,
diamond-sutra-kumarajiva, doctrine-of-the-mean, ecclesiastes, genesis, great-learning,
heart-sutra-kumarajiva, heart-sutra-xuanzang, isha-upanishad, job, katha-upanishad, liezi,
lotus-sutra, mengzi, proverbs, quran, sblgnt-john, sblgnt-matthew, tao-te-ching, zhuangzi。

## 已實作下載器（12 個）

矩陣見 [`CLAUDE.md` 既有下載器矩陣](./CLAUDE.md#既有下載器矩陣-12-個)。

## 已完成宗教覆蓋摘要

> 分宗教即時明細見 `00-overview/INDEX.md`（`generate-index.py` 自動產生）。以下為 2026-07-03 快照。

| 宗教 | 部數 | 評估 |
|------|------|------|
| 佛教（漢傳）| 2437 | 漢傳 T01-T55 + 卍續藏 X 大批深挖中；含巴利 8 sub |
| 猶太教 | 1384 | Sefaria Tanakh + Mishnah 64 + Talmud 32 + Halakhah 88 + Midrash 36 + 諸家注疏 1103 |
| 基督教 | 169 | 希臘 NT 27 + 拉丁 Vulgate + 中文和合本 + Mahabharata Ganguli |
| 佛教-巴利 | 39 | SuttaCentral SN+AN+KN 子集 |
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

1. 看 `00-overview/PIPELINE_STATUS.md` — 核心翻譯+標籤跑到哪、失敗幾部
2. 續跑：`PYTHONIOENCODING=utf-8 python scripts/auto-pipeline.py --tier 核心`（`--skip-done` 預設，接著跑）
3. 看 `logs/pipeline-failed.json` 有無卡住的 slug；薄譯多半是 `raw/original.txt` 只有目錄 → Pipeline A 補抓正文
4. 核心跑完 → `--tier 次要` 往外延伸；並行 Pipeline A 繼續補收集缺口（神道 / 兩河 / 諾斯底 等）
5. 標籤索引最新度：`python scripts/build-tag-index.py`；核心稽核：`python scripts/audit-core.py`
