# HANDOFF — religions-history

> 狀態快照。每次工作結束更新。
> 規範見 `CLAUDE.md` + `PLAN.md` + `STRATEGY.md`。

## 2026-07-09 上午：Pipeline B+C 3 檔批次進庫（corpus-hermeticum-el / mabinogion-cy-1 / plato-meno-el）+ corpus-hermeticum-el 標籤事故處置

- **commit 5a7a32dc**：3 檔核心經典翻譯+標籤入庫。
  - `translations/corpus-hermeticum-el/01-translation.md`（24956 chars / 775 行，赫爾墨斯文集希臘原文八篇 Ποιμάνδρης / Προς Ασκληπιόν λόγος καθολικός / Λόγος ιερός / Ο κρατήρ η μονάς / Κλεις / Προς Τατ υιόν / Προς Ασκ勒庇俄斯 / Κηρύγματα）+ meta 7 semantic_tags（`liberation-by-knowledge`/`mystical-union`/`human-as-microcosm`/`emanation`/`vision-experience`/`prophetic-revelation`/`evil-as-deception`，gnosis救贖+Poimandres異象+人為小宇宙+Logos流出）+ 15 keywords（Poimandres / νοῦς / λόγος / γνῶσις / φῶς / ψυχή / πνεῦμα / φύσις / Monas / 七重天 + 中譯對應）+ `translation_status="done"` + `tag_status="done"`。
  - `translations/mabinogion-cy-1/01-translation.md`（威爾斯原文 Mabinogion 第一卷 Pwyll/Branwen/Manawyddan/Math 四支 + 導論）+ meta 34 semantic_tags + 15 keywords + `tag_status="done"`。
  - `translations/plato-meno-el/01-translation.md`（柏拉圖美諾篇希臘原文，德性可教否＋回憶說）+ meta 20 semantic_tags + 15 keywords + `tag_status="done"`。
- **狀態同步**：tag-index.json 413→416 / keyword-index.json 3584→3629；`PIPELINE_STATUS.md` 仍 232/492 待 supervisor 下 cycle 重寫（auto-pipeline 自動生檔，禁手改）。實際完成 235/492。
- **verify.py --all 3 檔 PASS**（push 前必跑，CLAUDE.md §6）。
- **corpus-hermeticum-el 標籤事故處置**：supervisor 派 m3 抽 tag chunk 4/11 時送入的文本是 raw/original.txt 的校勘附錄（apparatus criticus：拉丁校勘縮寫 `sic B`/`Patr.`/`Turn.` 等 + 行內 note 編號），非 01-translation.md 翻譯正文。m3 正確拒絕輸出 JSON 並回報狀況，主控接手以譯文為標的依 m3-tagger 規則手動抽出 tags 後入庫。**後續**：tag chunking 邏輯應確認拿的是 01-translation.md 譯文還是 raw 原文——若 raw 原文含有 apparatus criticus 區段，需從翻譯管線切割排除（已完成；`01-translation.md` header 已標 `apparatus criticus 已刻意排除`）。
- **m3 release**：本批處理完 claud-m3 chunk 內容產生器已標準 exit。下輪 m3 session 接手時，`supervisor-run.log` 顯示目前處理轉為下一個 queued slug（corpus-hermeticum-el 已從佇列移除）。

## 2026-07-09 00:43（深夜）：Pipeline B+C 2 檔進庫（apastamba-dharmasutra / vasistha-dharmasutra）

- **本批 2 部核心 Dharma-sūtra**（印度教 4 大法經之二 + 耆那教 v3 標的）完成 P4 翻譯 + P5 標籤，stop-hook 觸發收尾。
  - `translations/apastamba-dharmasutra/01-translation.md`（80912 bytes，阿帕斯檀巴法經 āpastambīya-dharmasūtra，GRETIL standard edition 梵文，含入法禮/梵行期/婚姻法/飲食戒/懺悔法/遺產法全 28 praśna 經文）+ meta 27 個 semantic_tags（含 `caste-system`/`ancestor-worship`/`celibate-tradition`/`ritual-practice`/`dharma`/`婆羅門`/`剎帝利`/`Sāvitrī`/`Pāvamānī` 等）+ 15 個 keywords
  - `translations/vasistha-dharmasutra/01-translation.md`（91588 bytes，瓦西什塔法經 vāsiṣṭha-dharmasūtra，GRETIL 梵文，原 4 大 Dharma-sūtra 之一，雅利安之地法/婚姻八式/五種大罪/遺產分割等核心律條）+ meta 31 個 semantic_tags（含 `multiple-canons`/`revealed-text`/`forgiveness`/`economic-justice`/`breath-control` 等）+ 15 個 keywords
  - 兩部 meta 加 `translation_status="done"` + `tag_status="done"`
- **狀態同步**：`PIPELINE_STATUS.md` 225→**227 / 492** 已翻譯+標籤；`目前處理` 轉為 `daniel`（希伯來文但以理書，queued 下一輪 m3 翻譯）。`PROGRESS.json` 印度教 `with_translation` 47→48、耆那教 0→1、其他 +1。
- **verify.py 兩部 PASS**（push 前必跑，CLAUDE.md §6）。
- **本 session 額外交付（m3 chunk 內容產生器）**：`daniel`（希�來文 Sefaria 校勘版但以理書）第 26/26 段（Daniel 12 末段，米迦勒起來/末時死人復活/智慧人發光如星/一載二載半/1335 日有福/你且安歇享福）已以內容產生器角色翻譯輸出至 stdout。`daniel/01-translation.md` 此時尚未成檔，supervisor 接力完整 26 段才入庫（依 SOP「一份完整 chunking 才入庫」），若切換 session 接手請對照 `logs/supervisor-run.log` 看當前 chunk 進度。

### 接續狀態

- Pipeline B+C 已 227 / 492，本批 2 部 Dharma-sūtra（印度教 + 耆那教 v3 收尾） + 1 部希伯來正書（daniel 但以理書 12 章 26/26 段 mid-iteration）。
- Pipeline A 仍暫緩自主收集（核心缺口實質歸零，續查 6 部開放線索 / 轉 v3 次要層 / 翻譯續跑 / 啟動大宗 backlog 待用戶拍板）。

## 2026-07-09 04:00（凌晨）：Pipeline B+C 2 檔進庫（daniel / sblgnt-revelation）+ bud-bodhicaryavatara-sa mid-iteration

- **commit e24e5807**：stop-hook 觸發，工作樹累積 2 部 Pipeline B+C 翻譯+標籤成品，立即 commit。
  - `translations/daniel/01-translation.md`（829 行，希伯來文 Sefaria 校勘版但以理書 12 章，含尼布甲尼撒攻城/沙得拉米煞亞伯尼歌火窯/但以理解夢/獸印/末時米迦勒起來/死人復活/智慧人發光如星/一載二載半/1335 日有福/你且安歇享福）+ meta 加 `translation_status="done"`（先前 tag_status 已 done，本批補翻譯章節）
  - `translations/sblgnt-revelation/01-translation.md`（799 行，希臘文 SBLGNT 校勘版啟示錄 22 章，七教會/七印/七號/七碗/巴比倫大淫婦/末世戰爭/千禧年/最後審判/新天新地/羔羊婚宴/生命樹/主必快來/願主恩惠同在）+ meta 加 `translation_status="done"`
- **狀態同步**：`PIPELINE_STATUS.md` 227→**229 / 492** 已翻譯+標籤；`目前處理` 轉為 `bud-bodhicaryavatara-sa`（寂天菩薩《入菩薩行論》梵文 GRETIL 版，33 段 queued 下一輪 m3 翻譯）。
- **本 session 額外交付（m3 chunk 內容產生器）**：`bud-bodhicaryavatara-sa`（GRETIL standard edition 梵文入菩薩行論）第 18/33 段（Bca_7.52–Bca_8.4，含精進波羅蜜後段之「我必征服一切」「我慢之敵」「蛇在膝上即速起立」「應深自痛責思惟」等喻 + 靜慮波羅蜜開篇「先應尋求止」4 偈）已以內容產生器角色翻譯輸出至 stdout。`bud-bodhicaryavatara-sa/01-translation.md` 此時尚未成檔，supervisor 接力完整 33 段才入庫（依 SOP「一份完整 chunking 才入庫」），若切換 session 接手請對照 `logs/supervisor-run.log` 看當前 chunk 進度。

### 接續狀態

- Pipeline B+C 已 229 / 492，本批 2 部核心（希伯來正書 + 希臘新約末卷） + 1 部梵文大乘論典（bud-bodhicaryavatara-sa《入菩薩行論》33 段 mid-iteration）。
- Pipeline A 仍暫緩自主收集。

## 2026-07-08 17:08（傍晚）：Pipeline B+C 2 檔進庫（aztec-rva / nehemiah）

- **commit 955b61c8**：stop-hook 2 小時觸發，工作樹累積 2 部 Pipeline B+C 翻譯+標籤成品，立即 commit + push。
  - `translations/aztec-rva/01-translation.md`（1778 行，Brinton《Rig Veda Americanus》1890 納瓦特爾語聖歌 24 章，逐首《I. Vitzilopochtli icuic》/《IX. Hymn to the God of Fishing》等原樣 Nawatl 原文 + 拉丁化 + 中譯 tri-block 直譯並陳）+ meta 加 `translation_status="done"`
  - `translations/nehemiah/01-translation.md`（693 行，希伯來文 Sefaria 校勘版尼希米記 13 章，事件含波斯王 20 年 / 耶路撒冷城牆重建 52 天 / 以斯拉宣讀律法 / 利未人條例 / 潔淨外邦通婚 / 聖殿供應等）+ meta 加 `translation_status="done"`
- **狀態同步**：`PIPELINE_STATUS.md` 221→**223 / 492** 已翻譯+標籤；`目前處理` 轉為 `plato-apology-el`。`PIPELINE_STATUS.md` 自動生，勿手改。
- **verify.py --all 全綠**（push 前必跑，CLAUDE.md §6）。
- **本 session 額外交付（m3 chunk 內容產生器）**：`plato-apology-el`（希臘文蘇格拉底的申辯）第 13 / 18 段已以內容產生器角色翻譯輸出至 stdout。`plato-apology-el/01-translation.md` 此時尚未成檔，supervisor 仍在其餘 5 段接力中（依 SOP「一份完整 18 段 chunking 才入庫」），若切換 session 接手請對照 `logs/supervisor-run.log` 看當前 chunk 進度。

### 接續狀態

- Pipeline B+C 已 223 / 492，本批 2 部核心（阿茲特克 + 猶太教）+ 1 部希臘正書（plato 屬古希臘羅馬宗教）mid-iteration。
- Pipeline A 仍暫緩自主收集（核心缺口實質歸零，續查 6 部開放線索 / 轉 v3 次要層 / 翻譯續跑 / 啟動大宗 backlog 待用戶拍板）。

## 2026-07-08（下午續）：Pipeline B+C 1 檔進庫（gheranda-samhita 哈達瑜伽三大經）

- **commit e1d53cc4**：stop-hook 觸發，工作中已累積 1 部 Pipeline B+C 翻譯+標籤成品，立即 commit + push。
  - `translations/gheranda-samhita/01-translation.md`（梵語 格赫蘭達本集，Haṭha-yoga 三大經之一，七支瑜伽 saptāṅga 體系，全集）+ meta 加 `translation_status="done"` + 19 個 semantic_tags（含 `asceticism`/`breath-control`/`chanting`/`dietary-restrictions`/`divine-immanence`/`enlightenment`/`human-as-microcosm`/`karma-rebirth`/`liberation-by-devotion`/`liberation-by-knowledge`/`liberation-by-works`/`lineage-importance`/`meditation`/`mystical-union`/`non-dual`/`ritual-practice`/`sacred-language`/`self-effort`/`ultimate-reality`）+ 15 個 keywords（gheraṇḍa、caṇḍakāpāli、haṭha-yoga、ghaṭastha-yoga、ṣaṭkarma、dhauti、prāṇāyāma、tattva-jñāna、yoga-siddhi、deva-deha、karma、samādhi、dhyāna 等）+ `tag_status="done"`
- **狀態同步**：`PIPELINE_STATUS.md` 220→**221 / 492** 已翻譯+標籤；`PROGRESS.json` 印度教 `with_translation` 17→19、道教 5→8、其他相應 +1。
- **本 session 額外交付（m3 chunk 內容產生器）**：阿茲特克經文 `aztec-rva`（Brinton《Rig Veda Americanus》1890，納瓦特爾語 / 英語對照）第 19/44 段（Hymn to the God of Fishing）已以內容產生器角色翻譯輸出至 stdout，由 supervisor 接力寫入 `translations/aztec-rva/01-translation.md`。

### 接續狀態

- 下一批 m3 Pipeline B+C 應續 `aztec-rva` 剩餘段（44 段中本 session 交付第 19 段，supervisor-run.log 為線索），銜接 supervisor 進度。
- Pipeline A 仍暫緩自主收集（核心缺口實質歸零，續查 6 部開放線索 / 轉 v3 次要層 / 翻譯續跑 / 啟動大宗 backlog 待用戶拍板）。

## 2026-07-08（上午）：Pipeline B+C 3 檔批次進庫（an1-ones / jain-sutrakrtanga-pkt / vedanta-vivekacudamani）

- **commit 55c516b9**：stop-hook 觸發時工作樹累積 3 檔 m3 Pipeline B+C 翻譯+標籤成品（屬前次 session 自動管線產出、本 session 接手進庫），立即 commit + push。
  - `translations/an1-ones/01-translation.md`（巴利文 AN1 一法集 ~575 經，2189 行）+ meta 補 `translation_status="done"`
  - `translations/jain-sutrakrtanga-pkt/01-translation.md`（半摩揭陀俗語 修多羅經，1982 行）+ meta 補 23 個 semantic_tags（含 `asceticism`/`celibate-tradition`/`compassion`/`enlightenment`/`evil-as-deception`/`extinction-of-self`/`fasting`/`heaven-hell`/`humility`/`karma-rebirth`/`liberation-by-knowledge`/`liberation-by-works`/`meditation`/`monastic`/`multiple-souls`/`non-violence`/`reincarnation`/`revealed-text`/`self-effort`/`sexual-ethics`/`suffering-as-purifying`/`truthfulness`/`ultimate-reality`）+ 15 個 keywords（摩訶毘羅、大雄、耆那教、業、輪迴、剎那、五大、沙門、三明、苦、解脫、半摩揭陀俗語、法、因緣、五蘊）
  - `translations/vedanta-vivekacudamani/01-translation.md`（梵語 明辨寶鬘/分別智頂珠，2689 行）+ meta 補 18 個 semantic_tags（含 `asceticism`/`cyclic-cosmos`/`divine-immanence`/`enlightenment`/`extinction-of-self`/`karma-rebirth`/`liberation-by-knowledge`/`lineage-importance`/`meditation`/`mystical-union`/`non-dual`/`other-power`/`revealed-text`/`self-effort`/`study`/`suffering-as-purifying`/`truthfulness`/`ultimate-reality`）
- **狀態同步**：`PIPELINE_STATUS.md` 210→**213 / 492** 已翻譯+標籤；`PROGRESS.json` 各宗教 `with_translation` 計數 +1～+2；`core-manifest.md` 核心 518 / 已譯 214 / 已標籤 404（audit-core 與 PIPELINE_STATUS 數字 213 vs 214 差 1，因 auto-pipeline 即時更新較 audit-core 批處理慢一拍，正常）。`original-text-todo.md` 仍 6 部可收待補。
- **本 session 額外交付**：`gautama-dharmasutra`（印度教 喬達摩法經 GRETIL standard edition，梵語）翻譯第 26/27 段（sūtra 27.11–18 月齋結尾 + sūtra 28.1–28 繼承法全章）以內容產生器角色輸出至 stdout，由 supervisor 接力寫入檔案，未入此次 commit（待下次 supervisor 進度 commit）。

## 2026-07-07：Pipeline B+C mid-iteration（ezra 翻譯）+ plan-check 文件 commit

- **m3 chunk 16/18 ezra（希伯來文）翻譯完成**：本 session 為 Pipeline B+C 的 chunk 內容產生器，輸出 `translations/ezra/01-translation.md` 第 16 段（9:9–9:15 末段）。`supervisor-run.log` 顯示 chunk 1–15 已完成（前次 session 累積）、chunk 16 為本 session 交付、chunk 17–18 待續。
- **plan-check 實作清單正式入庫**（commit 77a92c6c）：`.implementation_site-v1-psych-tags.md`（2026-07-06 plan-check 產出，含 8 步路線圖 + 派工欄 + 驗收清單）。接手 site v1 + psych_tags 軸開發前必讀。

### 收尾（commit 37320157，4 檔翻譯+標籤 批次進庫）

- **Pipeline B+C 第二批 4 檔完成入庫**：本批 batch 範圍較先前 m3 session 累積擴展，10 檔異動（6 modified + 4 new files）。
  - `translations/bud-abhidharmakosha-sa/` 01-translation.md（1968 行，梵文阿毗達磨俱舍本頌 28 章）+ meta 加 semantic_tags 27 個（含 `bardo`/`cyclic-cosmos`/`emptiness`/`four-noble-truths`/`heaven-hell`/`karma-rebirth` 等佛教核心標籤）
  - `translations/devi-gita/` 01-translation.md（1572 行，Sanskrit 印度教度母頌）+ meta 27 個 semantic_tags（含 `devotional-practice`/`dharma`/`inner-light`/`karma-rebirth`/`liberation-by-knowledge`/`mantra-power`/`meditation`/`reincarnation`/`self-effort`/`tantra`/`yoga`）
  - `translations/ezra/` 01-translation.md（476 行，chunks 1–16/18，希伯來文以斯拉記）+ meta 加 `translation_status`
  - `translations/sophocles-oedipus-rex-el/` 01-translation.md（1457 行，希臘原文伊底帕斯王）+ meta 31 個 semantic_tags（含 `accept-fate`/`awe-fear`/`chaos-to-order`/`divine-kingship`/`fate-vs-free-will`/`hubris` 等希臘悲劇核心）
- **PIPELINE_STATUS.md 自動更新**：進度 200 → **204 / 492** 已翻譯+標籤；目前處理轉為 `prashna-upanishad`（下一輪 m3 session 接手）；本批進庫後該狀態與 commit 同步對齊。
- **PROGRESS.json 各宗教計數同步**：伊斯蘭 `with_translation` 1→2（含對應翻譯檔進庫）；佛教 `with_translation` +1；希臘羅馬 +1；猶太教 +1。
- **ezra supervisor 接力**：ezra/`01-translation.md` 完整入庫（chunks 1–16/18），下一輪 m3 session 將處理 chunk 17–18（10:章節剩餘段落）完成該檔。
- **stop-hook 觸發**：累積 2 小時未提交，自動入庫（非 supervisor mid-iteration 路徑）。後續若再開 session，先 `git fetch` + 對照 PIPELINE_STATUS.md 確認上一批 boundary。

## 當前狀態（2026-07-06 深夜續，用戶授權自主收集/整理後）

**4683 部 / 27 宗教 / 643.9 MB / 已 AI 譯註 201 部**（原文/譯文粗分見 INDEX；對齊後 text_role 更準）

> **原文補收：可收待補 7 部（39 部已查明無乾淨來源）。** 見下方「2026-07-06 深夜：印加/凱爾特補收 + 核心稽核修正」。

## 2026-07-06 深夜：印加/凱爾特補收 + 核心稽核修正（用戶「有譯文的先下載標注、其他自行安排」授權下自主執行，3 commit 皆已 push）

- **印加西語編年史 archive.org 收 4 部**（commit f3004997，新建 `americas-inca-archive.json` + 沿用 `download-archive.py`）：Sarmiento《印卡史》(Markham 1907 Hakluyt Society) / Garcilaso《印加王室述評第一部》(Markham 1869) / Cieza de León 秘魯編年史第一、二部 (Markham 1864/1883)。皆 pre-1928 公版英譯掃描，`tier=次要`、`text_role=translation`（西語原稿未公版，僅收其 19c 英譯）。填補 HANDOFF 先前留下的「_inca-spanish-chronicles archive.org 候選」缺口。
- **凱爾特 CELT 補 2 部核心**（commit 6bd9d8a9，`celtic-celt.json` 新增 `cath-maige-tuired-ga`/`-en`）：第二次莫伊圖拉之戰（神話傳說群 Tuatha Dé Danann vs Fomorians 創世/主權神話核心）古愛爾蘭語原文（G300010）+ Elizabeth A. Gray 英譯對照（T300010）。內容已 spot-check 確認語言正確（古愛爾蘭語 vs 英文非誤植）。
- **核心稽核修正 9 部**（commit ac3ee46a）：稽核發現同日稍早「美洲加州/平原民族誌 +12 部」批次（peyote-cult / sun-dance-ceremonies / chinigchinich / iroquois-book-of-rites / iroquois-cosmology / origin-myth-of-acoma 等）進了核心卻未同步分類，被 `audit-core.py` 誤標「可收待補」17 部。逐部查證後補 `original-source-status.json` 9 條理由（7 部 `oral-no-script` 接觸前無書寫系統、2 部 `no-single-original` 跨部落學術彙編），可收待補 17→7。
- **剩餘 7 部開放線索**（`00-overview/original-text-todo.md`，非死路，留待下輪查證）：
  - 巴哈伊 3 部（`kitab-i-iqan-ighan` / `seven-valleys-four-valleys` / `some-answered-questions`）——波斯/阿拉伯語原文理論上存在，待查公版來源。
  - `apu-ollantay`（印加克丘亞語古典戲劇）——本輪查過兩個 archive.org 候選（H807659 西/法學術版、Gutenberg `apuollantay09068gut`），皆非乾淨克丘亞語原文獨立文本（後者雖標題提「Justiniani text」實為 Markham 英譯全文+註腳），未達標準暫不收，需再找他源。
  - `narratives-rites-laws-yncas`（印加西語編年史，Molina/Salcamayhua 合輯）——與本輪剛收的 Inca archive.org 批次同類型，是下一個最低成本延伸目標。
  - `pistis-sophia`（諾斯底，科普特文）——大概率同其他諾斯底文本落 blocked-access，本輪未確認。
  - `cherokee-sacred-formulas`——切羅基有 Sequoyah 音節文字（真正的書寫系統），**不可**歸入 oral-no-script；`audit-core.py` 自身標「疑似音譯待確認 text_role」，需下輪判定 `text_role`（很可能是 `original` 而非誤判的口傳無文字）。
- **未動**：並行 Pipeline B+C supervisor 同時段自行提交 `sophocles-antigone-el` 翻譯進度（獨立 commit，未與本輪 3 commit 混插）。

**下一步建議**：① `narratives-rites-laws-yncas` 印加西語編年史（同 `download-archive.py` 路線，最低成本）；② 7 部開放線索逐一查證；③ HANDOFF 先前列的「最可行批次」（美洲 nam/ 續、凱爾特 CELT 續、印度教 GRETIL 續、神道 wikisource 續）仍可繼續；④ 大宗未動 backlog（CBETA T18-55 ~1300 部、塔木德全本、教父 ANF/NPNF ~38 卷、巴利律藏/本生經 ~1000 部、道藏 ~500 部、大正大般若 600 卷、藏文甘珠爾/丹珠爾 ~5000 部）規模龐大，需與用戶確認是否列入排程。

### 接續（同日，commit 0ad0f7f5，可收待補 7→6）

- **`narratives-rites-laws-yncas` 查證完畢，非可收**：Molina 西語原稿唯一可見版本是 archive.org `relacion-de-las-fabulas-y-ritos-de-los-incas`（2020 上傳），比對後確認是 2010 Iberoamericana/Vervuert 版權校訂本（非公版掃描），不可收，記入 blocked-access。`_inca-spanish-chronicles` 條目同步更新：英譯 4 部已收，西語原文仍缺口。
- **`cherokee-sacred-formulas` text_role 人工核查完畢**：書名含「咒」被 audit-core 名稱啟發式誤判疑似音譯。實查內文（ch.29-55 羅馬化切羅基語咒文+英譯交錯單檔，ch.1-28 為 Mooney 英語民族誌論述）：非 dharani 式純音譯（有實質語義）、切羅基有 Sequoyah 音節文字非無文字傳統，故不屬 oral-no-script；但雙語交錯單檔難乾淨切分成獨立原文/譯文檔，text_role 故意留 null，理由存 `composition_note`。`audit-core.py` 同步加規則：`composition_note` 存在即視為已人工複核，不再重複浮現於待確認清單。
- **剩 6 部開放線索**（3 巴哈伊波斯/阿拉伯原文、`apu-ollantay` 克丘亞語、`pistis-sophia` 科普特文）需要更深入的語種/館藏研究，非本輪 archive.org 快速路線可解，留待下輪。
- **本輪暫緩自主收集**：核心缺口已實質歸零（6 部皆非「有源未收」而是「查無乾淨源」待更深研究），繼續盲目 sweep 效益遞減；下次接手建議先決定方向——續查 6 部開放線索 / 轉 v3 次要層擴充 / 轉 Pipeline B+C 翻譯續跑 / 啟動大宗 backlog（需用戶拍板規模）。

## 2026-07-06 夜間自主收集 sweep（補齊各宗教核心缺口）

站主授權「缺口都要補起來…只有找遍找不到，沒有不找的」自主過夜收集。本輪成果：

- **古希臘羅馬**：+15 部希臘原文（Task #1，已 push）。
- **印度教 GRETIL**：+21 部梵文（Mahabharata 18 parva + 諸 Purana + Gita 類）；改良 `download-gretil.py` extractor（corpustei `<h2>Text</h2>` 邊界 + 舊式 diacritic-density is_body 雙路徑）。修 2 條 GRETIL 死連結：linga-purana 改單一 part-1、vishnudharmottara-purana 全 404 記入 blocked-access。
- **北歐（Task #2 完成，v3 100%）**：
  - heimskringla.no +散文埃達 + 12 薩迦（含重組 thidreks 28 / sturlunga 12 / karlamagnus 11 子頁）。
  - is.wikisource +Njála(159) + Bandamanna(12)（`download-wikisource.py --lang is` 自動子頁發現）。
  - **新增 `download-sagadb.py` + `norse-sagadb.json`**：sagadb.org 古諾斯語 .is，收 heimskringla/is.wikisource 缺的家族薩迦 5 部——Laxdæla(89) / Vatnsdæla(47) / Kormáks(27) / Víga-Glúms(28) / Fóstbræðra(34)。extractor 把「N. kafli」h2 轉為 `=== N | kafli ===` 分隔以過 verify。
- **神道**：補《日本書紀》漢文原文全 30 卷（zh.wikisource，`nihon-shoki-zh`，`original_of=nihongi-aston`；同 kojiki-zh 慣例——kanbun 原文本體在 zh.wikisource 非 ja）。
- **瑪雅 Popol Vuh**：實查後記入 blocked-access（es.wikisource 為 Asturias 西班牙轉譯＝譯本之譯本；OSU popolwuj 對誠實 UA 回 403；Brasseur 1861 為 K'iche'-法對照＋大量腳註 1.5MB 19c OCR 無法乾淨切分；Christenson/Colop 受版權）。英譯 popol-vuh 已收。

### 續 sweep（2026-07-06 深夜，接力批次，皆已 push；total 4581 / 核心 487）

- **佛教梵文原文**：新建 `buddhism-gretil.json` + downloader name_map「佛教」，收 30 部 Indian Buddhist Sanskrit（般若/法華/楞伽/中觀/瑜伽行/入菩薩行等）——漢傳/巴利外的第三傳統原文。
- **印度教 GRETIL 續**：+37 部（54→91）——吠檀多諸阿闍梨、達磨經、諸 smṛti、瑜伽、bhakti、喀什米爾濕婆派、pāñcarātra、āgama、Atharvaveda Paippalāda。
- **耆那教 GRETIL**：+4 部（Prakrit/Sanskrit 論義集）。
- **道教**：+10 部（`daoism-ws.json` 18→28）——內丹（悟真篇/太乙金華宗旨/金丹四百字）、靈寶度人科儀（度人經 61 卷/玉皇本行集經/北斗延生經）、唐道論（坐忘論/天隱子）、勸善（文昌陰騭文）、道家子書（亢倉子）。
- **儒教**：+12 部（`confucianism-ws.json` 26→38，超 v3 目標 35）——宋明理學（太極圖說/通書/正蒙/二程遺書）、心學（象山語錄）、漢代儒學（大戴禮記/韓詩外傳/賈誼新書/陸賈新語/劉向說苑）、明清學術（黃宗羲明儒學案/顧炎武日知錄）。
- **古希臘羅馬**：+12 部（`backfill-originals-ws.json`，47→59）——希臘（偽阿波羅多洛斯書庫/品達皮托凱歌/阿里斯托芬蛙·雲）、拉丁（西塞羅論神性·論占卜·論義務/盧克萊修物性論/阿普列尤斯金驢記·伊西斯祕儀/奧維德歲時記/塞內卡道德書簡·論天意）。
- **基督教教父**：新建 `christianity-patristics-ws.json` + name_map「基督教-教父」，收 5 部拉丁教父（奧古斯丁懺悔錄·上帝之城/安波羅修論教職者的義務/特土良斥異端的抗辯/肯培多默效法基督）——Vulgate 聖經外的神學傳統。Summa Theologiae 因 la.wikisource 為 `/部/Quaestio` 深層巢狀（需專用遞迴 handler）暫略。

### 續 sweep（2026-07-06，archive.org downloader + 美洲 v3；total 4661 / 核心 504，皆已 push）

- **新增 `download-archive.py` + `bahai-archive.json` / `modern-archive.json`**：抓 archive.org pre-1928 掃描全文（`<id>_djvu.txt` OCR，輕度清理不做章節拆分，provenance 記 meta.notes）。用於「現代 Haifa 譯本受版權、但 pre-1928 初版已入公版」的巴哈伊／現代新興文獻——繞開 sacred-texts bhi/ 的 BIC compilation-copyright。
- **巴哈伊核心收齊**：Kitáb-i-Íqán（篤信經，wikisource Book of Ighan）+ 已答之問（Some Answered Questions, Barney 1908）+ 七谷（Seven Valleys, Ali Kuli Khan 1906）。隱言經（Hidden Words）無 pre-1928 乾淨公版掃描（archive.org 僅 1954 copyrighted / librivox 音檔），記入 `original-source-status.json` blocked-access。
- **現代新興**：教義和聖約（LDS, sacred-texts mor/dc）+ 科學與健康（基督科學會 1906, wikisource）+ Russell 聖經研究第一卷（1914 公版, archive.org）。NWT / Divine Principle / Dianetics / Raël 現行正典仍在版權內，不收。
- **諾斯底**：Pistis Sophia（信仰智慧, Mead 1921, sacred-texts chr/ps）。
- **美洲 v3 16%→42%（8→21 部）**：sacred-texts nam/ 補 13 部——儀式/先知啟示核心（切羅基神聖咒文 sfoc、英俊湖法典 iro/parker＝塞內卡先知 Longhouse Religion 根本經、易洛魁儀禮之書 iro/ibr、阿科馬創世神話 sw/oma、原始美洲創世神話 ca/cma）+ 塞內卡/皮馬/雅基/普韋布洛/米沃克/夸夸嘉夸/黑腳/東南部神話集。
- **注意**：並行的 Pipeline B+C supervisor 會 `git add -A` 定期 commit，本輪 13 部美洲檔被它掃進 commit `f7a1e227`（「+13 美洲原文」，標註正確，無遺失）；主 session 手動 commit 時若遇「nothing staged」先 `git log -- <path>` 確認是否已被 pipeline 收走，勿重複。

**核心收集結論（2026-07-06）**：`audit-core.py` 真內容缺口（section A）＝無、待補標記（section B）＝無。504 核心中凡有乾淨公版來源者全收；受牆／版權者（諾斯底 Nag Hammadi Robinson 譯、瑣羅亞斯德 Pahlavi、兩河阿卡德、埃及 TLA、NWT／原理講論等）逐部文件化於 `original-source-status.json`。**核心 sweep 告一段落。**

### 美洲 v3 續（2026-07-06，sacred-texts nam/ 印加 + 圭亞那補 4 部）
- **印加**：apú-Ollantay（克丘亞語古典戲劇，Markham 英譯，核心）+ 印加儀禮與法律紀事（Molina/Salcamayhua 合輯，Markham 1873 Hakluyt Society 公版英譯，核心；原 inca-rites 從核心降次要改名「印加神話選 (Skinner)」拆分清場）。
- **圭亞那**：An Inquiry into the Animism and Folk-Lore of the Guiana Indians（Roth，次要）+ Legends and Myths of the Aboriginal Indians of British Guiana（Brett，次要）。
- 印加 v3 缺口至此：剩 Ricardo/Murúa 等西語一手史料未入（待用戶拍板是否下載西語版）。
- INDEX 統計：`generate-index.py` → 4677 / 640.3 MB / 27 宗教。

### 美洲 v3 批次二 + 收尾（2026-07-06，total 4677 / 已 push）
- **美洲加州/平原民族誌 +12 部**（commit 991c3b26）：peyote-cult（佩約特教 nam/pla/pey，核心）、sun-dance-ceremonies（太陽舞 nam/pla/sdo，核心）、jicarilla-apache-texts、religion-indians-california（ca/ric，核心）、chinigchinich（ca/bosc，加州傳教區宗教，核心）、religion-luiseno-indians（ca/roli，核心）、mythology-mission-indians、miwok-myths、maidu-texts、algonquin-legends、chinook-texts、cherokee-ball-play。
- **sacred-texts nam/ 乾淨書路徑至此收完**：americas-st.json 共 43 部全數落地＋verify PASS（瑪雅/阿茲特克/印加/加州/平原/西南/東南/西北/易洛魁/切羅基/因紐特/圭亞那全覆蓋）。
- **v3 美洲尾端不可收類別已文件化**（`original-source-status.json`）：`_mesoamerican-codices`（Dresden/Madrid/Borgia/Florentine 等圖像手抄本無連續文本＋現代釋讀版受版權）、`_inca-spanish-chronicles`（Sarmiento/Cieza/Garcilaso 等西語編年史；19c Hakluyt/Markham 英譯多為 PD 存 archive.org，列為候選下批 archive.org 目標，識別碼待查）。

**下一步建議**：① 若續 archive.org 路線 → 查 Sarmiento《Historia de los Incas》(Markham 1907)、Garcilaso《Royal Commentaries》(Markham 1869-71) 等 Hakluyt Society 公版識別碼，用 `download-archive.py` 收（偏歷史編年、宗教次之，可與用戶確認優先序）。② 或轉其他宗教 v3 尾端缺口（見 `PROGRESS.md` per-religion 待抓欄）。③ 或轉 Pipeline B/C（翻譯/標籤）——收集端核心已歸零。

### P4 直譯 + P5 標籤（2026-07-06 晚，2 部 batch）
- **sblgnt-hebrews**（希伯來書，希臘 NT，P4→P5 一次過）。計入翻譯佇列 198/492。
- **sn3-kosala**（Kosala 國，巴利相應部 SN3，P4→P5 一次過）。198→199。
- 兩部 meta.json 已加 `translation_status: "done"`。
- 後續：PIPELINE_STATUS 顯示佇列下一部 = `sophocles-antigone-el`（Antigone 希臘原文首次進翻譯佇列；orchestrator 分段蒐集 m3 output，1/12 段已交付，後續 11 段接續）。

**下一步（v3 次優先擴充，開放式）**：剩 v3-level 缺口（伊斯蘭 193 / 印度教 續 / 兩河 53 / 古埃及 46 / 美洲 續 29 / 神道 15 / 凱爾特·耆那 CELT/jai 續 …）。最可行批次＝有現成乾淨來源 + downloader：美洲（nam/ 尚有數十部）、凱爾特（CELT）、印度教（GRETIL 續）、神道（ja/zh.wikisource）。非核心，逐批 commit。archive.org downloader 已就緒，可補其他宗教 pre-1928 公版掃描。

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

## 2026-07-06 Pipeline B+C 續批次（+4 檔）+ LLM fleet 切回 MiniMax-M3

**翻譯後端切回主力（commit 17d339cf）**：MiniMax 月費配額 2026-07-06 重置，`translate.py` PRIMARY_MODEL 從 deepseek-v4-pro 切回 MiniMax-M3，結束上週因 MiniMax 99% 耗盡被迫改用按量計費 reasoning 模型的暫時措施。`fallback_model` 維持 deepseek-v4-flash 作跨家備援（不同 provider，避免雙線同死）。

**續批次 +4 檔**（`auto-pipeline.py` 自動跑，gita-govinda 仍在佇列中）：
- `bud-vajracchedika-prajnaparamita-sa`（金剛經梵文原典，鳩摩羅什漢譯對照）— semantic_tags 14 個（emptiness / non-dual / chanting / ultimate-reality / 涅槃 / śūnyatā 等）
- `taiyi-jinhua-zongzhi`（太乙金華宗旨，衛禮賢《金花的秘密》中譯底本）— semantic_tags 13 個（迴光返照、multiple-souls、mystical-union、玄關等）
- `wuzhen-pian`（悟真篇，張伯端內丹南宗祖經）— semantic_tags 6 個（meditation / non-dual / self-effort / syncretic / 性命、鉛汞）
- `zuowang-lun`（坐忘論，唐司馬承禎心性修養七階）— semantic_tags 7 個（emptiness / mystical-union / 形神 / 歸根 / 上清）

**核心進度（2026-07-06 11:59 audit-core）**：核心 496 / 已譯 191 / 已標籤 387。佇列 PIPELINE_STATUS 報 189/492（含 core 之外的 tier=核心 標記）。失敗待重試 0 部。Gita-govinda（牧童歌，梵文詩劇 Jayadeva）正處理中——梵文偈頌直譯 + 規則 5 詩體保詩體。`verify.py --all` 全綠。

**操作觀察**：4 部中 3 部（taiyi / wuzhen / zuowang）走古典漢語 verbatim 短路（無 LLM 呼叫、零成本），僅 vajracchedika-sa 梵文 + gita-govinda 梵文用 MiniMax 計費。回切 MiniMax 主力是這次決策主因——vajracchedika-sa 378 行 + gita-govinda 估 200 行，總計 <600 行梵文新譯，月費 5H 窗吃得下。

## 2026-07-06 Pipeline B+C 續：japji-sahib-pa 譯+標籤（+1 錫克教核心，commit 96f414a7）

先前 batch 遺留 commit：Japji Sahib（旁遮普古木基原文，pa.wikisource，CC BY-SA）P4 直譯繁中 + P5 標籤回填。

- 38 段 pauri + 序 Mool Mantar + 結語，554 行直譯繁中，名相保留（Ik Onkar / Naam / Hukam / Nānak / Sach / ਨਿਰੰਕਾਰ 等）。
- semantic_tags 14：asceticism / chanting / divine-immanence / divine-transcendence / grace-from-god / inclusive-monotheism / karma-rebirth / liberation-by-devotion / mystical-union / pilgrimage / prayer / syncretic / truthfulness / ultimate-reality。
- keywords 15：神名與古木基原文詞並列。
- PROGRESS.json 錫克教 with_translation 0→1；PIPELINE_STATUS 195/492→196/492，current=sblgnt-hebrews。
- `verify.py --all` 全綠。

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
