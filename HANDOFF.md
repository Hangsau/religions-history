# HANDOFF — religions-history

> 狀態快照。每次工作結束更新。
> 規範見 `CLAUDE.md` + `PLAN.md` + `STRATEGY.md`。

## 當前狀態（2026-07-05 重生統計）

**4415 部 / 27 宗教 / 539.3 MB / 已 AI 譯註 23 部**（原文/譯文粗分見 INDEX；對齊後 text_role 更準）

> **原文補收（2026-07-03）：可收待補歸零。** 所有有乾淨來源的核心原文皆已收；剩 28 部經實際探查確認無乾淨來源，逐部附理由＋已探來源於 `original-source-status.json`（見下方「原文補收進度」段）。

詳見即時 [`00-overview/INDEX.md`](./00-overview/INDEX.md) 自動產生統計。
進度追蹤見 [`00-overview/PROGRESS.md`](./00-overview/PROGRESS.md)（`scripts/track-progress.py` 自動產生）。

**桌面刊版（狀態看板）= `scripts/status_gui.py`**
- 常駐 Tkinter GUI，視窗標題「religions-history 刊版」，每 30 秒自掃全庫刷新。**是進度監控牆，不是經文閱讀器。**
- 啟動：雙擊專案根 `狀態看板.bat`（背景 `pythonw`，無主控台）；或 `PYTHONIOENCODING=utf-8 pythonw scripts/status_gui.py`。
- 顯示：頂部總量（部/宗教/MB）＋ 對齊覆蓋率（各 meta 欄位回填 %）＋ M3 分類進度（tier×era+genre+tags 三齊全）＋ Pipeline A 收集動態（最新收錄/近 30 分/日誌尾）＋ 翻譯進度（translation_status==done）＋ classify 背景管線。
- 資料 helper 沿用 `scripts/status.py`（`load_all` / `filled` / `ALIGN_FIELDS` / `log_ok_count` / `log_tail`）；GUI 只管畫面。綠條＝≥99.5% 完成、琥珀＝進行中。
- **刊版兼任監督（2026-07-04）**：`ensure_supervisor()` 在開看板時＋每 30 秒刷新時檢查 `logs/supervisor.pid`（`_pid_alive` OpenProcess 判活），沒在跑就用 `pythonw + DETACHED_PROCESS + CREATE_NO_WINDOW` 脫離式拉起 supervisor。**關掉看板不會殺死管線**（不重演 07-04 停擺）。頂部紅字橫幅 `pipeline_health()` 仍是 human backstop。
- **`pipeline_health` 活性訊號改用 `supervisor-run.log`（2026-07-04 修假警報）**：舊版看 `PIPELINE_STATUS.md` mtime >20 分就紅字「疑停擺」，但該檔每部經典才更新一次，大部（如 `sn7-brahmana` 17 chunk ≈ 30+ 分）跑到一半必被誤報；supervisor 心跳 `supervisor.log` 只在兩輪之間跳、長 run 全程不跳也不能用。改以 `run.log`（每 chunk ~100 秒寫一行）為真心跳，`min(status_age, run_age) > 1200s` 才判停擺。真停擺（含 07-04 那種零活動）run.log 也會靜止 → 仍會紅字；系統性 quota 耗盡由 `pipeline-alert.txt` 另捕（優先判）。
- **刊版即時動作區（2026-07-04）**：`translation_activity()` 解析 log 顯示「正在翻哪部（含中文名）/ 動作（翻譯 vs 標籤）/ chunk X/Y / 模型（從 `[model]` marker 自動抓，退備援時紅字「本次退備援」）/ 本次速度 部/時 + ETA / 錯誤·待重試·最近完成」。模型欄不再 hardcode，換 primary 自動跟上（見下 LLM fleet）。

## 2026-07-04 事故：翻譯管線靜默停擺 + 修復

- **事故**：07-03 21:24 auto-pipeline（Pipeline B+C）跑到 60/362 時，因掛在互動 session 背景 shell 下、session 一關被 OS 連進程樹收掉，**永久停擺 5 小時無人察覺**。GitHub 看似有進展，實為一支脫離式 Sefaria 全庫爬蟲在爬週邊拉比注疏（335 部冷僻超注），製造「只是多下載幾部經文」的假象。
- **止血**：停掉暴走爬蟲、落地積壓、啟動 supervisor，翻譯恢復（76/405 核心）。
- **根因修復（`scripts/supervise-pipeline.py`，脫離 session 的 supervisor）**：反覆啟動 auto-pipeline 直到佇列跑完（`this_run=0`）；異常退出自動重啟；連續 3 次「啟動後 <120s 即退」或連續 2 輪「一部都沒 processed」→ 判系統性問題（多半 M3 配額耗盡 / `claude -p` 端點異常），寫 `logs/pipeline-alert.txt` 並停止，不無限燒配額；每輪寫心跳 `logs/supervisor.log`。啟動：`Start-Process pythonw -ArgumentList 'scripts/supervise-pipeline.py','核心' -WindowStyle Hidden`（或直接開刊版，見上）。
- **黑框修復**：`translate.py` / `supervise-pipeline.py` 的 `claude -p` 子進程加 `CREATE_NO_WINDOW` creationflag —— 從無視窗父進程（pythonw）啟動 console 程式時不再彈出主控台黑框。
- **新增宗教「墨家」**：既然收儒 / 道，墨家具鮮明宗教性（天志＝天為道德立法者、明鬼＝鬼神監督善惡、兼愛出於天意、尚同上同於天）理應獨立成宗教。原本收集按宗教分桶（`儒教`/`道教` catalog），墨家不對映任一桶故整個漏掉。已加：`meta_template.json` religion enum +「墨家」、`scripts/catalog/mohism.json`、`download-ctext.py` name_map。收《墨子》原文（ctext，277,979 bytes / 53 篇，含兼愛/天志/明鬼/非命），verify PASS，`tier=核心 language=古典漢語`，已入核心翻譯佇列。

## 2026-07-04 WS1：全庫資料完整性稽核（免費本地）

等 MiniMax 週一（2026-07-06）期間的免付費工作。翻譯管線仍 HALT（`logs/pipeline-HALT.flag` 存在）。

- **新工具**：`scripts/audit-data-quality.py`（掃 9 類：空/截斷、U+FFFD、mojibake、checksum、重複 SHA、meta 缺欄、缺分隔、語言標籤不一致、外語字集占比）→ `00-overview/data-quality-report.md`。`scripts/fix_meta_labels.py`（只改 meta.json 的修復器）。
- **已修（245 部，僅動 meta.json，raw/checksums 未動，checksum 稽核全綠）**：
  - 語言標籤中→英標準名 60 部：希伯來→Hebrew 47、希臘→**Ancient Greek** 11（Homer/Plato/Herodotus 古典希臘，**非 Koine**；Koine 保留給 27 部 SBLGNT 新約）、拉丁→Latin 2。
  - 回填 `text_role`/`is_original_language` 185 部：Sefaria 拉比註釋+古典漢語原典（huangting-neijing/mozi）175 部 → original；Vulgate 10 部 → translation。
  - 稽核邏輯修正：羅馬轉寫 Sanskrit/Pali（IAST）不列字集檢查、譯本語言標籤子字串誤配排除 → 字集誤報 51→13。
- **已處理（2026-07-05 續）**：
  - **48 組同 SHA 重複 → 去重（`scripts/dedup_mark_aliases.py`）**：每組保留 meta 較完整（已翻/已標/tier 核心優先）的一份為 canonical，另一份標 `alias_of` + `dedup_note`（不刪檔、可逆）。`translate.py load_slugs_by_tier` 讀到 `alias_of` 即跳過，**已驗證 48 部 alias 在三佇列洩漏 0**，省掉重複翻譯/標籤成本。方向為混合（canonical 不一定是語意 slug，取決哪份有標籤）。
  - **2 部可救 U+FFFD 已修**：avesta-sbe23-ae（æ）、tain-bo-cuailnge-ga（í），重算 checksums + meta，verify PASS，`meta.repairs` 存審計註記。
## 2026-07-05 WS1 續（免付費，全程 Opus 自主 + Sonnet 派工）

MiniMax 週一（2026-07-06）回來前的免付費工作。翻譯管線仍 HALT。

- **[完成] 92 部核心漢語 verbatim 回填 + 修 huangting 竄改**（commit cc48a284）：核心古典漢語/古典中文經典走 verbatim 短路，`01-translation.md` 原樣複製 `raw/original.txt`（0 LLM 呼叫、0 計費、0 竄改）。huangting-neijing 舊 `01-translation.md` 仍帶 LLM 竄改變體字（疊→叠），依 raw 重生。全 116 部 verbatim 檔內文逐字核對 raw：0 內容不符。
- **[完成] 修 Sefaria downloader 巢狀漏抓 + 重抓 10 部截斷**（commit 77366bac + 52187405）：`download-sefaria-full.py` `fetch_book_text` 改「整本抓一次 + 遞迴攤平」（`_chapterize`/`_flatten_strings`）。**根因**：舊版靠 `index.lengths` 逐章 iterate，註釋類經文 lengths 缺失（回 None）時被當 1 章，漏抓 99%（Matnot Kehunah 523 段只抓 1）。新增 `--titles` 針對性重抓旗標。10 部全還原（rashi-on-chagigah 55→89509 字等）。verify.py --all 全綠；順帶 1515 部標 verified。
- **[判定] 8 部 CBETA「截斷」非 bug**：多為 parser 正確排除夾註（`<note place="inline">` 交錯註）後主文本本就短（如 T46n1943 主文「初運香華…」49 字，其餘皆夾註運想文）。**不改資料**（夾註是註解非正文，排除合理）。等 P4 到密教部再議是否併夾註。
- **[判定] 13 部 CBETA 梵字/悉曇 dharani**：SMP 為 CBETA 缺字（gaiji）私用區碼位非亂碼；已被古典漢語 verbatim 短路保護不會亂翻。改標非急務。T54n2133A 是「中文解說悉曇」論著非咒語，不可標 transliteration。
- **[完成] 4 部 CJK-FFFD 復查（派 Sonnet，commit a1d46857）**：14 個 U+FFFD 逐一比對 zh.wikisource `?action=raw` + ctext。**復原 3**（yi-li「肂」U+8082；zhuzi-yulei 2× 全形問號＝wikisource `{{？}}` 未知記錄者標記）；**11 為真缺字**（wikisource 本身標 `{{?|外囗內巷}}`/`{{?|地地地}}`/`{{?|門耑}}` 等 Unicode 未編碼字形，或源檔亦 FFFD）——不臆造、保留缺字守 provenance。yi-li/zhuzi-yulei SHA 三方一致 verify PASS，`meta.repairs` 存註記。
- **[完成] WS2 收集（派 Sonnet，commit 00d96c46）**：諾斯底 5 + 巴哈伊 1 + 古埃及 14 部（sacred-texts.com 19c 英譯本）先前 session 已全下載，本次 all-skip；重生 INDEX（已驗證 2436→**4411** 全庫、27 宗教、537.4 MB）。
- **本輪全綠**：全庫 verify.py --all 0 FAIL，1515 部標 verified:true（commit 52187405）。

### 週一（2026-07-06）MiniMax 回來後
1. 刪 `logs/pipeline-HALT.flag`。2. 確認 `translate.py` PRIMARY_MODEL 指回 MiniMax。3. 開刊版 / 拉 supervisor 續跑核心翻譯佇列。4. Sefaria downloader 已修（整本抓+遞迴攤平），未來全庫爬蟲不再漏抓巢狀註釋。

## 2026-07-05 WS3：心理學讀經層——由下而上分類（P6 前置，免付費）

翻譯管線仍 HALT 期間的規劃型工作。核心意圖見 memory `project_religions_history_psych_lens.md`：本專案終點不只原文庫，而是**用心理學透鏡讀經 + 跨宗教比較**。本輪把這條線推到「分類已收斂、對照真實經典」的雛型。

- **方法（關鍵）**：不從理論預設分類，而是先造「人實際會問的問題」，由下而上讓分類自己浮現。組織軸＝**人從生到死的問題**（生老病死、七情六慾、存在意義），經文＝歷代對這些問題的回答，心理學＝解讀透鏡（非第三種答案）。
- **[完成] `11-psychology/human-questions-corpus.md`**：500 題自問自答對話錄（Q001–Q500，5 批）。仿弟子問師／個案問治療師，跨語言文化、生到死，調性多變（禪門一句／直白／溫語／反問／詩）。第 5 批 100 題用**不同人格的極端處境**壓力測試分類。
- **[完成] `11-psychology/question-themes.md`**：由下而上從 400 題收斂出 **13 個大領域**（← 46 細群）＋3 條現代跨界支流（科技·比較／智慧·學習／人在自然）＋6 條反覆潛流。**收斂已驗證**：第 5 批極端人格 100 題全數落回既有 13 領域，零新增大類——極端處境只加深強度，不加寬分類。
- **[完成] `11-psychology/reference-analects.md`**：13 領域 ← `translations/` 內**已收的問答／對話體真實經典**對照（論語/孟子/傳習錄、彌蘭王問經、迦塔·大林間·唱讚·問難奧義書、薄伽梵歌、約伯記/傳道書/父輩之倫理/米示拿祝福章、斐多/會飲/理想國、長部/中部經典、聖訓手冊）。**13 領域全部找得到古代對應、無一落空**——分類為真的外部佐證；問答體是七傳統五語言共同的教學形式。
- **13 領域**：I 存在與意義 · II 自我與認同 · III 愛與親密 · IV 家庭與傳承 · V 群體·社會·公義 · VI 情緒與內在生活 · VII 善惡·良心·品格 · VIII 工作·成就·召喚 · IX 苦難·疾病·身體 · X 無常·老·死·失去 · XI 自由·命運·改變 · XII 信仰·神聖·超越 · XIII 安頓·修復·平安。
- **本輪不做網站**（用戶明確指示）。README.md（`11-psychology/`）已由「延後/預留」改為「已啟動」並列出三檔與收斂結論。

### 心理學讀經層進度／待辦
1. **[完成 2026-07-05，免付費]** 13 領域正式寫成 `00-overview/concepts-psychology.md` 受控詞彙（46 細群 + 3 跨界支流，每細群一個 kebab 標籤）——**與比較宗教學 `concepts.md` 14 類正交並存**（後者＝教義內容軸，前者＝人的問題軸，一部經兩軸都可標）。**設計決定：新增 `meta.json` 欄位 `psych_tags: []`，不併進 `semantic_tags`**（避免兩軸混淆）。→ 週一啟動標籤前需在 `meta_template.json` 加 `psych_tags` 欄、`m3-tagger-role.md` 補人問軸標法。
2. **[等 MiniMax]** 用 `reference-analects.md`（20 部黃金種子）當人工先驗，交 LLM 給經文標 `psych_tags`，**允許多標籤**（一部經常跨多域）。
3. `reference-analects.md` 經典指向從「整部」細化到「章節/段落」。
4. P4 翻譯**優先翻對照表那 20 部原文問答經典**（多為古典漢語/Sanskrit/Pali/Hebrew/Ancient Greek），讓讀經層先有中譯底。

## 2026-07-05 WS4：收集（Pipeline A，免付費，不吃 LLM）

釐清一個框架錯誤：**HALT flag 只 gate 翻譯/標籤（Pipeline B+C），收集（Pipeline A）從未被 gate**。收集閒置的真正原因＝2026-07-03「核心可收待補歸零」＋ 07-04 暴走爬蟲後對無人看管遞迴爬蟲的謹慎，**與 LLM 無關**。

- **查明：儒教／道教具名經典已收完**。`confucianism-ws.json`（26/26）＋`daoism-ws.json`（13/13，+ctext 共 17 部）全綠。PROGRESS「待抓 9 儒/23 道」是 v3 用**總集級**估的（道藏 5305 卷、四庫經部、皇清經解那條大尾巴），無現成乾淨來源、非按播放鍵可補——**心理學對照層要的漢語問答經典早已在庫**。
- **[完成] 新收 4 部希臘原文（斯多噶／德性倫理，`backfill-originals-ws.json` 加 entry → download-wikisource el）**：`marcus-aurelius-meditations-el`（沉思錄 12 卷 354KB）、`epictetus-enchiridion-el`（手冊 60KB）、`aristotle-nicomachean-ethics-el`（尼各馬可倫理學 10 卷 650KB）、`epictetus-discourses-el`（談話錄 4 卷 913KB）。**古希臘羅馬原有 28 部但斯多噶派整組缺席**，這 4 部直接補強心理學讀經層（XI 自由·命運／XIII 安頓／VII 品格）。4 部 verify PASS，希臘文乾淨。
- **收集方法備忘（下次要補 v3 缺口時）**：多數 v3 缺口要先把書目對到來源 URL、擴 catalog（我的活、非 m3）；el.wikisource 原文用 `backfill-originals-ws.json` 加 entry（`lang:el` + `wikisource_title` 用**解析後無變音符**標題，多卷用 `wikisource_titles` 明列子頁）；跑 `download-wikisource.py --slug <slug>`；限定單一 catalog、勿放遞迴全庫爬（07-04 教訓）。
- **重生 INDEX**：全庫 4411 → **4415** 部 / **539.3 MB** / 27 宗教。

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

**原文補收進度（2026-07-03，sibling-original 管線）— 可收待補歸零**
- 用戶指令「補阿 還有要加的也去加一加 可以不要便宜行事」「能顯示的字就下載原文，既然抓的到有什麼理由繞過」→ 真收原文並收到底。
- **模型**：原文以「新 sibling slug（`<英譯slug>-<lang>`，`text_role=original`，`original_of` 反向連結英譯 slug）」入庫，英譯留作對照；`audit-core.py` 見 `original_of` 或 檔內含 ≥15% 非拉丁原生文字 或 `text_role=original` 即把對應核心移出待補。`original_of` 可為 list。
- **download-wikisource.py 擴充**：per-entry `lang`、`wikisource_titles`（多頁明列）、`text_role`/`is_original_language`/`original_of` 寫入 meta；端點含 el/ru/he/de/is/cy/pa。catalog＝`scripts/catalog/backfill-originals-ws.json`。
- **兩個新 downloader**：`download-heimskringla.py`（heimskringla.no HTML 爬，api.php 停用；catalog `norse-heimskringla.json`）、`download-celt.py`（celt.ucc.ie TEI，錨定最後含「Author:」標題切檔頭；catalog `celtic-celt.json`）。
- **本輪已收/改標（待補 54→46→…→0 可收）**：早段 Ovid/Virgil/Plato/Mabinogion/homer-greek 連結；後段 guru-granth-sahib-pa(Gurmukhi)、kojiki-zh(漢文,zh.WS)、poetic-edda-on/heimskringla-on/volsunga-saga-on(古諾斯語)、tain-bo-cuailnge-ga(古愛爾蘭語)、corpus-hermeticum-el(希臘8篇,→thrice-greatest-hermes-2)。**檔內已含原文、只改標**：carmina-gadelica-1/2(蘇格蘭蓋爾語facing)、aztec-rva(Brinton RVA 20首聖歌納瓦特爾語facing)。
- **反 便宜行事 做法**：每部先 live API/HTML 探 title/subpages/實際內容，數原生字比例確認才入庫；改標前 grep 檔內證實原文真存在（非猜）。

**Phase 2 原文層 — 已查明無乾淨來源（28 部，非未查待辦）**
- 新增 `scripts/catalog/original-source-status.json`：逐 slug 記 status＋理由＋已探來源；`audit-core.py` 據此把「已查明無乾淨來源」與「可收待補」拆開（現可收待補=0）。詳見 `00-overview/original-text-todo.md` 文末分區。
- **blocked-access（16）**：古埃及×8（Budge/Mercer 英譯，連續原文僅 TLA，實測檔內 0 連續音譯）、瑣羅Pahlavi×5（avesta.org 僅 West 英譯，轉寫僅 TITUS 受阻/Pakzad 版權）、兩河×3（阿卡德，ORACC 不含/eBL 登入牆/SEAL JS-SPA/ETCSL 蘇美語）。**若日後突破**：TLA 開放資料匯出、TITUS 結構化抓取、eBL 帳號 → 移除對應條目即回可收。
- **no-single-original（9）**：諾斯底 Mead/King 學術著作×2＋TGH-1(導論)/TGH-3(Stobaeus 散篇)、錫克 Macauliffe 彙編（Gurbani 原文已另收）、斯拉夫 Ralston 民俗彙編、巴哈伊 Hammond 選集（原文散於各原著）、美洲 Landa(西文僅 2002 受版權 OCR)/Chumayel(馬雅轉寫無乾淨全文)。
- **oral-no-script（3）**：非洲約魯巴 ife/yoruba（口傳無文字）、印加 inca-rites（quipu 無表音文字）。採錄英譯即最早可及形式，保留 text_role=translation（非 original，因確為英譯）。
- **赫爾墨斯 分類折疊（非缺口）**：赫爾墨斯 收在 `諾斯底`／`赫爾墨斯` 傘下；獨立宗教瀏覽需另議。
- **瑪雅/阿茲特克/印加 已拆為獨立宗教（2026-07-04 完成）**：原收在 `美洲` 傘下，已改 meta.json religion 欄 + catalog（`americas-st.json`）；北美部落神話（navajo/hopi/zuni…）仍歸 `美洲`。INDEX 重生後 27 宗教。

**LLM fleet：主力切 DeepSeek-V4-Pro（2026-07-04 晚，MiniMax 配額 99% 耗盡）**：`translate.py call_m3` 現主用 `deepseek-v4-pro`、失敗/逾時退 `deepseek-v4-flash`（皆 `api.deepseek.com/anthropic`，同 `~/.deepseek-token`；key 讀序 env `DEEPSEEK_API_KEY` → `~/.deepseek-token`，值源 `hermes-Hestia/hestia-credentials.env`）。**MiniMax-M3 已退出 chain**（月費配額 99%；且舊 fallback 用的 `deepseek-chat` 已在 DeepSeek API 下架，只剩 v4-flash/v4-pro）。待 MiniMax 5H 窗重置可考慮加回為跨家備援（不同 provider，非雙線同死）。
- **兩 v4 model 皆 reasoning model**（回應含 thinking + text 兩塊）：`/anthropic/v1/messages` 直打時 `max_tokens` 需 ≥4000（thinking 會吃光低預算 → text 空）；但走 `translate.py` 的 `claude -p` CLI 路徑不受此限，已實測回傳正常譯文（「道可道非常道」→「能夠用言語說出來的道…」）、假標題陷阱（〈北冥非馬〉）正確拒答。
- **flash 只作 fallback，不升 primary（2026-07-04 晚實測）**：用 `build_prompt` 實測 flash，它守不住輸出格式——吐前置散文、捏造完成回報（「已更新 2149 行」）、缺 header、本文亂碼；且 `bypassPermissions` 下會 agentic 暴走（測試中一度覆寫 `dhammapada/01-translation.md`，已 `git restore` 復原）。pro 嚴格照格式 → **primary 維持 pro**。
- **刊版自動抓取當前模型（2026-07-04 晚，commit 7bd73d2b）**：單一來源設計，換模型免手改。`translate.py` 常數 `PRIMARY_MODEL` / `FALLBACK_MODEL`；`call_m3` 成功時印 log marker `  [model] <name> (primary|fallback)`；譯文 header 用 `__TRANSLATION_MODEL__` placeholder 由 `PRIMARY_MODEL` 自動填。`status_gui.py` 的 `translation_activity()` 改用正則 `\[model\]\s+(\S+)\s+\((primary|fallback)\)` 從 log 抓 provider（拿掉 hardcode「MiniMax-M3」），`fallback_active` 時紅字「本次退備援」。**改 primary 只需動 translate.py 一個常數**，刊版與 header 自動跟上。
- **relaunch 已執行（本次含新碼）**：舊 worker kill 後，supervisor（未改，pid 6812）30s backoff relaunch 新碼 worker（`auto-pipeline.py` pid 於本 session 重啟為載入 7bd73d2b 的 marker 碼），log 已確認印出 `[model] deepseek-v4-pro (primary)`；刊版 `status_gui.py` 亦重啟載入新正則。續跑走 `--skip-done`，已完成 slug 不重跑。
- 分工原則未變：漢傳/和合本原樣保留不耗 LLM。若要「並行加速」（非只 fallback）需再加 profile pool 平行派工，待用戶決定。
- **⏸ 當前狀態：翻譯人工暫停中（2026-07-04 晚 → 預計 2026-07-06 週一早 MiniMax 配額重置）**。deepseek-v4-pro 按 token 現金計費、又是 reasoning model，跑大量佇列太貴（實測換上後短時間燒近 ¥2）；用戶決定**等 MiniMax（月費、限界成本零）回來再翻外語**。暫停機制＝`logs/pipeline-HALT.flag`（commit 783cf127）：supervisor 啟動/迴圈間偵測到即不跑，`status_gui.ensure_supervisor` 偵測到即不復活，刊版頂部琥珀橫幅「人工暫停中」。**週一恢復步驟：① 刪 `logs/pipeline-HALT.flag` ② `translate.py` `PRIMARY_MODEL` 改回 MiniMax（並確認 token 有效）③ 開刊版或起 supervisor**。
- **省錢短路：古典漢語/中譯本 verbatim 不呼叫 LLM（commit 9489cc9c）**：舊碼只短路 `transliteration`，古典漢語仍走付費 LLM 只為抄回中文（且 reasoning model 會竄改）。新增 `_CHINESE_LANGS` 短路，命中即原樣寫出、印 `[zh-verbatim] no LLM call`。全庫 2539 個中文語言 slug 從此翻譯零成本。
- **完整性修復：24 部漢語經典重生成 verbatim（commit 19f91ab3）**：檢查發現先前已翻的 24 部古典漢語 slug 全是 LLM 產物，12 部內文遭竄改（法華經漏 5805 字、莊子漏 1 字、道德經/地藏經等異體字 回→迴）。已全數重生成為 verbatim，內文與 `raw/original.txt` 完全一致（複驗 24/24 pass）。

**黑框全清（2026-07-04 補完）**：07-04「黑框修復」只補了 `translate.py` 的 `claude -p`；本次補齊 `auto-pipeline.py`（`run_git` + `rebuild_indexes` 起子腳本）、`classify-metadata.py`（git）、`status.py`（git log）四處遺漏 subprocess，全加 `CREATE_NO_WINDOW`。pythonw 背景管線 commit/push/建索引時不再彈主控台黑框。

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
