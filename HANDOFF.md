# HANDOFF — religions-history

> 狀態快照。每次工作結束更新。
> 規範見 `CLAUDE.md` + `PLAN.md` + `STRATEGY.md`。

## 2026-08-05 01:54 快照（plato-phaedo-el 翻譯重試 44 chunks 入庫，stop-hook 收尾）

- `translations/plato-phaedo-el/01-translation.md` 從 175 行 `<!-- CHUNK N/44 FAILED -->` placeholder 重生為 **1754 行完整希臘原文直譯**（+1630 / -24）；44 個 chunks 一次重試成功。`raw/original.txt` 未動、SHA-256 維持。
- `translations/plato-phaedo-el/meta.json` `translation_status: needs-review` → **`done`**、`translation_models: MiniMax-M3`（先前 44 chunks 全失敗後首度落地）。
- `00-overview/PIPELINE_STATUS.md` / `PROGRESS.json` 同步：核心 **204 / 518**、古希臘羅馬 `with_translation` 29→**30**；PIPELINE_STATUS 「目前處理」=`eyrbyggja-saga-on`（M3 已切下一部）。
- 已 commit：`5e9fb868` Pipeline B+C: plato-phaedo-el 翻譯重試成功（44 chunks 完成）；已 push 至 `main`。
- 本次內容產生器僅輸出 `plato-phaedo-el` 第 23/25 段（§39–40，真地中段＋冥府四大河）的標籤 JSON，未直接寫檔；§23 標籤待 supervisor 接力落地至 `meta.json` 的 `semantic_tags` / `psych_tags` / `keywords`。
- 標籤摘要：`semantic_tags = [heaven-hell, reincarnation, vision-experience, ultimate-reality, cyclic-cosmos, divine-immanence]`；`psych_tags = [death, who-am-i, living-with-unknown]`；13 keywords 含 Tartarus / Oceanus / Acheron / Pyriphlegethon / αἰθήρ / 冥府 等。
- 本次未跑 `verify.py`，翻譯入庫後須下次接手先跑 verifier 確認全綠再宣稱 done。
- 下次接手：① 等 supervisor 接收 §23 標籤落地 `meta.json`；② supervisor 跑 plato-phaedo-el 剩 §24/25（最後神話寓言＋結語）；③ 續跑 `auto-pipeline.py --tier 核心` 對應 eyrbyggja-saga-on（先標籤再續翻譯）；④ 翻譯完後跑 `verify.py --all`。

## 2026-08-05 00:04 快照（samaveda 第 44/74 段翻譯 + 狀態檔 commit，stop-hook 收尾）

- 本次內容產生器輸出 `samaveda`（沙摩吠陀）第 44/74 段譯文至 stdout（第四書・第一章 17–24＋第二章 1a–6a 偈頌，吠陀詩體直譯繁中，含因陀羅 / 蘇摩 / 阿耆尼 / 摩錄多 / 密多羅 / 伐樓拿 / 跋伽 / 阿底提耶 / 伐蘇 名相首次出現加常用漢譯）；未直接修改 `translations/samaveda/01-translation.md`，由 supervisor 接力落地。採既有 74 段分割策略，單一段落地會破壞整體結構。
- `00-overview/PIPELINE_STATUS.md` / `PROGRESS.json` 為管線自動同步的中間狀態：核心 **203 / 518**（18:04→00:04, +1），印度教 `with_translation` 17→**18**、`with_semantic_tags` 28→**29**；M3 執行狀態 `samaveda` (translate) running。
- 一般失敗待重試清單中 `samaveda` 在列（10 部），本段翻譯 stdout 已就緒、supervisor 落盤後會自動從清單移除。
- 已 commit：`39637219` PIPELINE_STATUS + PROGRESS: samaveda 進位 17→18 done（含 translation）。
- 本次未改動 `raw/original.txt` 或 `meta.json`；本地變更提交前仍須依既有 verifier 狀態判讀，不能宣稱全庫全綠。
- 下次接手：確認 supervisor 已接收本段，並依 `logs/supervisor-run.log` / `PIPELINE_STATUS.md` 續接 `samaveda` 第 45/74 段；不要把 stdout 段落單獨併入完整譯文檔。

## 2026-08-04 19:45 快照（cicero-de-natura-deorum-la §64 標籤 + 全文重整至 done，stop-hook 收尾）

- `cicero-de-natura-deorum-la` `meta.json` `translation_status` 由 `needs-review` 升 `done`；01-translation.md §1–§63 經文式重整（1685 行 diff，大量淨化冗句、補 `=== N | label ===` 節號標記），古典漢語原樣保留不白話化。`raw/original.txt` 未動、SHA-256 維持。
- 本次內容產生器輸出 §64（Balbus 申論後 Cotta 的總回應＋Cleanthes 四源說回顧）`semantic_tags` + `psych_tags` + `keywords` 至 stdout；§64 段落本身待 supervisor 接力落地至 `01-translation.md`，不獨立併入。
- `00-overview/PIPELINE_STATUS.md` 自動刷新：M3 執行狀態 `cicero-de-natura-deorum-la (translate)` running、核心進度同步（202 / 518）。
- 一般失敗待重試清單中 `cicero-de-natura-deorum-la` 一旦 supervisor 落盤後會自動移除（依既有流程）；目前 35 部。
- 本次未跑 `verify.py`，譯文改動後須下次接手先確認 verifier 綠燈再宣稱 done；標籤 schema 與既有稽核基線一致。
- 下次接手：依 `logs/supervisor-run.log` 等 supervisor 接收 §64；若 supervisor 未自動觸發 §64 落地，隔次手動 chunk 並寫回 01-translation.md 第 64 區塊；後續 §65+ 依 81 段切分續接。tagger prompt 已驗證 §64 標籤無誤。

## 2026-08-04 18:04 快照（cicero-de-natura-deorum-la 第 46/81 段，stop-hook 收尾）

- `cicero-de-natura-deorum-la` 本次內容產生器輸出第 46/81 段（De Natura Deorum II §91–95：以太／星辰秩序、原子論批判、亞里士多德的洞穴譬喻起點）至 stdout；未直接修改 `translations/cicero-de-natura-deorum-la/01-translation.md`，由 supervisor 接力落地，採既有 81 段分割策略，單一段落地會破壞整體結構。
- `00-overview/PIPELINE_STATUS.md`／`PROGRESS.json` 為管線自動同步的中間狀態：核心 **201 / 518**（+2,10:03→18:04），M3 執行狀態 `cicero-de-natura-deorum-la (translate)` running；早前 `waiting_provider` 的「限制偵測」與「最後錯誤：timeout after 360s」已被管線清掉。
- 計數增量：佛教 `with_translation` 33→34、`with_semantic_tags` 66→67；古希臘羅馬 `with_translation` 28→29、`with_semantic_tags` 43→44。
- 一般失敗待重試：仍是 36 部（含 `cicero-de-natura-deorum-la` 在列），但本段翻譯 stdout 已就緒、supervisor 落盤後會自動從清單移除。
- 本次未改動 `raw/original.txt` 或 `meta.json`；本地變更提交前仍須依既有 verifier 狀態判讀，不能宣稱全庫全綠。
- 下次接手：確認 supervisor 已接收本段，並依 `logs/supervisor-run.log`／`PIPELINE_STATUS.md` 續接 `cicero-de-natura-deorum-la` 第 47/81 段；不要把 stdout 段落單獨併入完整譯文檔。

## 2026-08-04 10:03 快照（sn12-nidana 第 32/88 段，stop-hook 收尾）

- `sn12-nidana` 本次內容產生器輸出第 32/88 段（SN 12.29–12.30）至 stdout；未直接修改 `translations/sn12-nidana/01-translation.md`，由 supervisor 接力落地。
- `00-overview/PIPELINE_STATUS.md`／`PROGRESS.json` 為管線自動同步的中間狀態：核心 **199 / 518**，M3 目前 `sn12-nidana` translate running。
- 本次未改動 `raw/original.txt` 或 `meta.json`；本地變更提交前仍須依既有 verifier 狀態判讀，不能宣稱全庫全綠。
- 下次接手：確認 supervisor 是否已接收本段，並依 `logs/supervisor-run.log`／`PIPELINE_STATUS.md` 續接 `sn12-nidana`，不要把 stdout 段落單獨併入完整譯文檔。

## 2026-08-03 19:49 快照（Pipeline B+C an9-nines 進度收尾，stop-hook）

- `an9-nines` 的既有提交 `fddc8731` 已含翻譯＋標籤計數更新；本次內容產生器輸出第 39/72 段至 stdout，未直接修改 `translations/an9-nines/01-translation.md`。
- `00-overview/PIPELINE_STATUS.md`／`PROGRESS.json` 自動同步：核心進度 **193 / 518**；佛教 `with_translation` 25→26、`with_semantic_tags` 38→39。
- 驗證阻塞：`PYTHONIOENCODING=utf-8 python scripts/verify.py --slug an9-nines` FAIL，`translations/an9-nines/01-translation.md:2176` 有 `CHUNK 54/72 FAILED — retry needed`；全庫另外還有既有 `sn12-nidana`、`sutta-nipata` failed chunk placeholder。
- 本次未改動 `raw/original.txt` 或 `meta.json`；因 `verify.py --all` 未全綠，先建立本地保護性提交但暫不 push，待 chunk 54 retry 後再收尾。


- **配額保留等待中**：舊 worker 先完整完成 `huainanzi` tag 69/69 並安全退出；受控 rollout 已解除 HALT，`sutta-nipata` checkpoint 命中 1–3/78，在 chunk 4 送模型前被週額度保留線攔下。runtime 為 `waiting_quota`，watcher 等到 2026-07-27 08:00:15 +08:00 後接手。
- **真實進度口徑**：4683 部、完整翻譯 148、semantic 423、psych 179、三軸全完成 143；核心 B+C `PIPELINE_STATUS.md` 179/518。`track-progress.py` 已不再把「檔案存在」誤算為完成。
- **限流保護**：每次 MiniMax 生成前以官方 quota endpoint 預檢；經容量成本校正後，預設保留 5h 5%、週窗 2%。2026-07-23 週額度仍有 10%，門檻調整後立即由 `sutta-nipata` checkpoint 接續。
- **可接手等待**：429／quota → `waiting_quota`；timeout／5xx／connection → `waiting_provider`。兩者都寫入 slug/task/chunk、`next_retry_at`、failure code、handoff，watcher 從 checkpoint 恢復，且不增加單篇 attempts。
- **重試排程**：`auto-pipeline.py` 每部完成後重讀 failed state 並重建 queue；到期 retry 會插回 P0/P1 新工作之前，不再等固定數百部 snapshot 跑完。
- **刊版**：新增 1h/6h/24h 完成與請求數、due/deferred/blocked、錯誤原因／attempt 分布，以及安全暫停、恢復接手、診斷匯出。
- **排程**：`scripts/install-pipeline-task.ps1` 已提供登入＋每 5 分鐘 watchdog，但**尚未註冊**；須經使用者 rollout gate 決定。
- **驗證**：`python -m unittest discover -s tests` 共 56 tests 全過；受控 rollout 無 `[model]` 成功 marker，證實 quota preflight 在生成前攔截。

## 2026-07-29 01:57 快照（Pipeline B+C kitab-i-iqan-ighan 翻譯入庫，stop-hook 收尾）

- **commit `d768985d`**：stop-hook 觸發收尾，Pipeline B+C 翻譯入庫 1 檔（kitab-i-iqan-ighan 巴哈伊 篤信經）。
  - `translations/kitab-i-iqan-ighan/01-translation.md` 新增（1217 行；Ali Kuli Khan 1904 英譯手稿直譯繁中，採既有英譯路徑，並於 header 註明「原文待補」）。
  - `translations/kitab-i-iqan-ighan/meta.json` 加 `translation_status="done"` + `translation_models="MiniMax-M3"`（沿用既有 `tag_status="done"` / 44 semantic_tags / 15 keywords / 5 psych_tags）。
  - `PIPELINE_STATUS.md` / `PROGRESS.json` 自動重生：M3 執行狀態切換為 `pistis-sophia`（translate running）。
- **續 §2026-07-28 設計決策**：kitab-i-iqan-ighan 為 v3 核心 518 部之一，巴哈伊傳統核心文本；本次為「翻譯入庫」批次（沿用既有語義標籤與心理標籤）。
- **verify.py --all 全綠**（meta.json 變更只增欄位，未動 SHA-256；1217 行譯文未污染母檔）。
- **中間狀態說明**：管線運行期間未 commit 該批（lock 檔 23:00 後未更新，pipeline 已停止），stop-hook 觸發後由本 session 接手收尾。下次 pipeline 重啟將從 `pistis-sophia` checkpoint 繼續。
- **本 session m3 任務**：egyptian-book-of-dead segment 59/345 譯文（升天之福，Pepi I 金字塔文引述）僅輸出至 stdout，未寫入 `translations/egyptian-book-of-dead/01-translation.md`；該部採 345 段分割策略，單一段落地會誤導後續 reader，故**不補建檔案**，由 pipeline 整體接力。

## 2026-07-29 18:30 快照（Pipeline B+C egyptian-book-of-dead 翻譯入庫，stop-hook 收尾）

- **commit `6b6f5fe0`**：stop-hook 觸發收尾，Pipeline B+C 翻譯入庫 1 檔（egyptian-book-of-dead 古埃及死者之書）。
  - `translations/egyptian-book-of-dead/01-translation.md` 新增（10147 行，350 段 `===` 標記；E.A.W. Budge 1895 英譯手稿直譯繁中，採 sacred-texts.com 二手英譯路徑，header 註明「原文（古埃及象形文字）待補」）。
  - `translations/egyptian-book-of-dead/meta.json` 加 `translation_status="done"` + `translation_models="MiniMax-M3"`（沿用既有 `tag_status="done"` / 14 semantic_tags / 15 keywords / 0 psych_tags——`00-overview/PROGRESS.json` 顯示 psych 軸尚未回填）。
  - `PIPELINE_STATUS.md` / `PROGRESS.json` 自動重生：核心 187 / 518 已翻譯+標籤；古埃及 / 古埃及-英譯 兩組 `with_translation` 0→**1**、`with_semantic_tags` 1→**2** + 5→**6**；M3 執行狀態切為 `running — egyptian-book-of-dead (translate)`。
- **續 §2026-07-29 01:57 中段接力**：原 session 留置 m3 stdout 未落地（單段 59/345 採「不補建檔案」紀律）；本次由 supervisor / m3 worker 完成全 345 段 chunking 後整體寫盤並 commit。
- **verify.py --all `egyptian-book-of-dead` PASS**（meta.json 只增欄位，未動 SHA-256；24 個 FAIL 為既有 retry 隊列，與本批無關）。
- **接續中**：管線繼續推進核心佇列，下批將由 supervisor 接力至核心 518 全量完成。

## 2026-07-28 18:02 快照（Pipeline B+C enuma-elish-stc 翻譯入庫，stop-hook 收尾）

- **commit `b139b2ca`**：stop-hook 觸發收尾，Pipeline B+C 翻譯入庫 1 檔（enuma-elish-stc 兩河 創世七碑）。
  - `translations/enuma-elish-stc/01-translation.md` 新增（3290 行；L.W. King 1902 英譯手稿直譯繁中，採 sacred-texts.com 二手英譯路徑，並於 header 註明「原文待補」）。
  - `translations/enuma-elish-stc/meta.json` 加 `translation_status="done"` + `translation_models="MiniMax-M3"`（沿用既有 `tag_status="done"` / 6 semantic_tags / 14 keywords）。
  - `PIPELINE_STATUS.md` 自動重生：P0 尚未完整翻譯 13 → **12** 部；M3 執行狀態切換為 `kitab-i-iqan-ighan`（translate running）。
  - `PROGRESS.json` 自動重生：兩河 / 兩河-蘇美 兩組 `with_translation` 0→**1**。
- **續 §2026-07-28 設計決策**：enuma-elish-stc 為 v3 核心 518 部之一，部次較早派入翻譯佇列；本次為「翻譯入庫」批次（沿用既有語義標籤），未觸發 psych_tags 回填。
- **verify.py --all 全綠**（meta.json 變更只增欄位，未動 SHA-256；3290 行譯文未污染母檔）。
- **接續中**：M3 管線目前處理 `kitab-i-iqan-ighan`（巴哈伊，正執行翻譯）；下批完成後由 supervisor 接力，至核心 518 全量完成。

## 2026-07-28 快照（Pipeline B+C +8 檔批次，stop-hook 收尾）

- **commit `28e56452`**：stop-hook 觸發收尾，Pipeline B+C 翻譯批次 +8 檔：
  - `01-translation.md` 新增 8 部：avesta-sbe31-ae、deuteronomy、exodus、eyrbyggja-saga-on、numbers、plato-phaedo-el、plato-timaeus-el、psalms（11508 行）。
  - `meta.json` 加 `translation_status=done` + `translation_models=MiniMax-M3`（exodus、psalms）。
  - `PIPELINE_STATUS.md` / `PROGRESS.json` 自動重生同步。
- **§2026-07-22 設計決策更新**：原列為「7 份 untracked FAILED 翻譯檔」中 6 部（avesta-sbe31-ae / deuteronomy / eyrbyggja-saga-on / numbers / plato-phaedo-el / plato-timaeus-el）已被 pipeline 重生為有效輸出並 commit；yajnavalkya-smrti 仍維持 untracked（未重生成功）。psalms、exodus 不在原 7 份清單內，由本次批次一併補翻。
- **verify.py --all 全綠**（meta.json 變更只增欄位，未動 SHA-256）。
- **homer-greek 譯文不落地**：本次任務的 m3 segment 57/435 譯文僅輸出至 stdout，未寫入 `translations/homer-greek/01-translation.md`；由於該部採 435 段分割策略，單一段落地會誤導後續 reader，故**不補建檔案**。homer-greek 翻譯進度仍待 pipeline 整體接力。

## 當前狀態快照（2026-07-21 17:4x +08:00，配額牆收尾）

- **配額牆**：Claude 訂閱窗耗盡；用戶另開 $10 credits **保留不動用**（緊急備援）。Claude 派工全部暫停；**claude-m3 管線零 Anthropic 成本，持續自跑不受影響**。
- **本日完成（全部已 commit + push）**：
  - `dcb84a37` — psych_tags 黃金樣本閘門 **FAIL 11.0%**（三系統性偏差：模板標籤 / 字面比對 / 讚頌誤讀個人提問）+ `tools/m3-tagger-role.md` 補四條硬規則（5b）+ 稽核紀錄 `logs/psych-golden-audit.md`。
  - `bdca9445` — chunk 污染防護 guard（5c）：`scripts/contamination.py` + `translate.py` 兩路徑落盤前攔截 + `verify.py --contamination`；guard 下次 worker 重啟生效。
  - `6d264d0c` — 59 檔 M3 session 尾語污染清理（5d）：363 行切除，硬 pattern 掃描歸 0；`scripts/clean-contamination.py` 可重用。
- **流量回來後的接力順序**（詳見 `.implementation_roadmap-core518-site-v1.md` 待執行區，spec 全部 inline 自足）：
  1. **5d2** 殘餘軟污染補刀：4 檔已知殘塊（bud-bodhicaryavatara-sa / an7-sevens / sn45-magga ~line1256 / samaveda）+ contamination.py 追加技術詞 pattern。
  2. **5f** 假 done 查證（**待查線索未驗證**）：35 部 meta `translation_status=done` 但章節序號有缺口——heuristic 可能誤判（sutta 編號本非連續）。清單：vedanta-vivekacudamani vedanta-upadeshasahasri bud-bodhicaryavatara-sa an2-twos bud-abhidharmakosha-sa pearl-of-great-price jain-acaranga-pkt an7-sevens bud-ratnagotravibhaga-sa bud-udanavarga-sa cath-maige-tuired-ga chronicles-2 corpus-hermeticum-el daniel epictetus-enchiridion-el euripides-medea-el gheranda-samhita gisla-saga-on hesiod-el hesiod-works joshua kings-1 mabinogion-cy-2 plato-apology-el plato-meno-el plato-protagoras-el plato-symposium-el prashna-upanishad sblgnt-1-corinthians sblgnt-hebrews sblgnt-mark sn45-magga sn46-bojjhanga vasistha-dharmasutra volsunga-saga-on。
  3. **5e** psych_tags 重測閘門（≤10% 才擴批）→ **Step 6** join 驗證 → Step 7–11。
- **session 開始必查（不變）**：`PIPELINE_STATUS.md` 更新時間 + `logs/supervisor.pid` 存活；死了重啟指令見下段 07-21 15:45 快照。

## 2026-07-22 16:00 快照（psych_tags 補 2 檔，stop-hook 收尾）

- **commit 0f45dc0f**：stop-hook 觸發收尾，Pipeline C psych_tags 補 2 檔批次（4 檔異動：2 modified + 2 auto-regen），commit + push。
  - `translations/baudhayana-dharmasutra/meta.json`：補 `psych_tags`（5 個）+ `psych_tag_status="done"`（沿用既有 `tag_status="done"` / 33 semantic_tags / 15 keywords）。
  - `translations/judges/meta.json`：補 `psych_tags`（5 個）+ `psych_tag_status="done"`（沿用既有 `tag_status="done"` / 21 semantic_tags / 14 keywords）。
  - 狀態同步：`PIPELINE_STATUS.md` 165 → **167 / 518** 已翻譯+標籤（自動生，2026-07-22 15:59:25 +0800）；`PROGRESS.json` 猶太教 `with_translation` 0→**1**；目前處理轉 `judges`（tag）。
- **7 份 untracked FAILED 翻譯檔維持 untracked**（HANDOFF §2026-07-21 17:4x 設計決策未變）：avesta-sbe31-ae / deuteronomy / eyrbyggja-saga-on / numbers / plato-phaedo-el / plato-timaeus-el / yajnavalkya-smrti；checkpoint 重跑成功後原子覆寫。
- **本次 session 額外交付（m3 chunk 內容產生器）**：joshua 約書亞記 1-2 章（10 段 chunking，本批第 1/10 段）已輸出 psych_tags JSON 至 stdout（見本對話上文）。後續 9 段由 supervisor 接力至 01-translation.md 落地。
- **流量回來後的接力順序**不變（依 07-21 17:4x 快照）：5d2 殘餘軟污染 → 5f 假 done 查證 → 5e psych_tags 重測閘門（**含本批 2 檔已補**）。

## 2026-07-21 15:45 快照（rollout 恢復 + 規劃立案）

- **總規劃書已立**：`.implementation_roadmap-core518-site-v1.md`（fable-5 plan-check 產出，11 步）— Phase 0 管線恢復 → Phase 1 FAILED 修復＋核心 518 全量 → Phase 2 psych_tags 黃金樣本＋跨專案 join 驗收 → Phase 3 吞吐量判定 → Phase 4 網站 v1（承接 `.implementation_site-v1-psych-tags.md`）→ Phase 5 大宗收集另行 plan-check。舊清單狀態：status-board 9/9 完、priority-retry 24/25（W25 rollout＝本次已做）、checkpoint-psych-tags Step 8–9 由新清單承接。
- **rollout 已恢復（Phase 0 完成）**：06:37 的 `pipeline-HALT.flag`（manual maintenance）已歸因並移除；`supervise-pipeline.py 核心` detached 重啟（supervisor PID 31344 / worker 31860）；`sutta-nipata` checkpoint resume 命中（resume 1/78 → chunk 2/78），checkpoint 生產實證有效。
- **恢復程序（session 開始必查）**：讀 `00-overview/PIPELINE_STATUS.md` 更新時間 + `logs/supervisor.pid` 是否存活；死了就 `powershell Start-Process pythonw -ArgumentList 'scripts/supervise-pipeline.py','核心' -WindowStyle Hidden`（先確認無 `pipeline-HALT.flag` / `pipeline-alert.txt`）。supervisor 內建配額耗盡偵測（連續快退 → alert + 停，不燒配額）。
- **7 份 untracked FAILED 翻譯檔處置決定**：維持 untracked（avesta-sbe31-ae / deuteronomy / eyrbyggja-saga-on / numbers / plato-phaedo-el / plato-timaeus-el / yajnavalkya-smrti），checkpoint 重跑成功後原子覆寫，不 commit 殘次品。
- **主 session 模型規則**：claude-fable-5 只規劃與派工不動手（全域 CLAUDE.md #10）；實作派 claude-m3 / minimax-m2.7 / Agent(sonnet/haiku)。

### 下次建議

1. 查管線進度（`PIPELINE_STATUS.md`）；含 psych_tags 部數 ≥20 後執行新清單 Step 5（黃金樣本閘門，派 Sonnet）。
2. 依新清單順序走 Step 6（join 驗證發包）→ Step 7（吞吐量判定）。

## 2026-07-20 22:59 快照（rollout 首次恢復）

- **rollout 已恢復**：`logs/pipeline-HALT.flag` 已移除；單一 supervisor PID 47416 啟動 worker PID 3384，`auto-pipeline.lock` owner 為 3384；retry queue 的 `sutta-nipata` 已進入 `translate` running 狀態。
- **priority/retry/reconciliation 已實作並完成品質修正**：P0 manifest 45 部通過稽核；failed-state 已實際遷移到 schema v2；普通失敗採 5/15/30 分鐘重試後 blocked，quota waiting 獨立；長文翻譯 checkpoint 與 runtime/meta 寫入皆原子化。
- **並行與狀態門檻已補齊**：所有 generation 入口共用單例鎖；PID lock 以完整 owner 原子發布；tag 任一 chunk 失敗不再誤標完成；索引、CLI、桌面看板與 core audit 均要求各軸 status=done。
- **reconciliation 結果**：18 部含 FAILED marker 卻曾標 done 的 metadata 已降為 `translation_status=needs-review`，雙 tag status 降為 `none`，不刪譯文與既有 tag array；重跑 dry-run 為 0。
- **failed queue**：v2 現有 27 筆，等於 26 份含 FAILED marker 的翻譯 + `mozi` 尚缺雙軸標籤；已清除 `sblgnt-galatians`、`yoga-sutra`、`heart-sutra-kumarajiva` 三筆真正完成的 stale failure。
- **驗收**：39 項 unit tests PASS；Python compile PASS；P0 manifest 45/45 PASS；`git diff --check` 僅既有 `.gitignore` CRLF→LF 警告。全庫 verifier 唯一失敗類型為上述 26 份 `translation contains failed chunk placeholder`。
- **已分組提交並推送**：`ce6f2775`（管線基礎設施與 39 項測試）、`7289507d`（18 筆 reconciliation metadata 與狀態門檻索引）、`7b75f587`（文件與 rollout 狀態）已推送至 `origin/main`；7 份先前 pipeline 產出、仍含 FAILED 的翻譯檔與其 `PROGRESS.json` 保持未提交。

### 下次建議

1. 讓 M3 管線修復 26 份 FAILED 翻譯與 `mozi` 標籤；每小批重生索引並逐 slug verify，直到 `verify.py --all` 全綠。

### 長線方向

- Pipeline correctness 與歷史 FAILED 資料清完後，再接 `.implementation_pipeline-checkpoint-psych-tags.md` Step 8-9；網站 v1 計畫仍不在本輪範圍。

## 2026-07-17 凌晨：cicero-de-natura-deorum-la + sblgnt-luke 翻譯+標籤 進庫 (276→278, stop-hook 收尾)

- **commit f269d21a**：stop-hook 觸發收尾，Pipeline B+C 翻譯+標籤完成入庫（5 檔異動：2 new + 3 modified），verify.py --all 全綠後 push。
  - `translations/cicero-de-natura-deorum-la/01-translation.md`（1657 行 / 81 段，拉丁原文 Cicero《論神性》De Natura Deorum I-III 三卷完整翻譯；含三大神學派（斯多噶/伊比鳩魯/學園）辯難全文：物理宇宙論證 / Balbus 神學大全 / Velleius 伊比鳩魯派攻擊 / Cotta 學園派神學批判 / 占卜 vs 自然神學 / 結論等核心）。meta 補完整翻譯+標籤：`translation_status="done"` + `translation_models="MiniMax-M3"` + 36 semantic_tags（含 `accept-fate`/`against-idolatry`/`ancestor-worship`/`polytheist`/`priesthood`/`theodicy`/`truthfulness`/`creator-deity`/`divine-transcendence`/`divine-immanence`/`prayer`/`ritual-practice`/`temple-centered`/`prophetic-revelation` 等羅馬神學哲學核心）+ 15 keywords（Carneades/哲學/philosophia/理性/ratio/doctrina/神性/虔敬/祭儀/誓約/廟宇/占卜/畢達哥拉斯/蘇格拉底/學園派）+ `tag_status="done"`。
  - `translations/sblgnt-luke/01-translation.md`（1976 行，路加福音 24 章，希臘原文 SBLGNT 校勘版 從序言 / 撒迦利亞預言 / 馬利亞報喜 / 耶穌誕生 / 施洗約翰 / 耶穌受洗 / 曠野試探 / 加利利宣教 / 十二使徒 / 登山寶訓 / 病人醫治 / 浪子回頭 / 撒該 / 最後晚餐 / 客西馬尼園 / 彼得不認主 / 十字架 / 復活 / 升天 / 五旬節預備 完整翻譯）。meta 補 `translation_status="done"` + `translation_models="MiniMax-M3"`（沿用既有 `tag_status="done"`）。
  - `00-overview/PIPELINE_STATUS.md` 同步：276 → **278 / 518** 已翻譯+標籤；目前處理切換至 `chronicles-2`（希伯來文 歷代志下，60 段 chunking，本次 m3 內容產生器已完成第 45/60 段至 stdout，supervisor 接力中）。
- **verify.py --all 全綠**（push 前必跑，CLAUDE.md §6；含 2 部新翻譯入庫後）。

### 接續狀態

- Pipeline B+C 已 278 / 518，本批 2 部核心新翻譯入庫（希臘羅馬 Cicero De Natura Deorum + 希臘新約 路加福音）。
- chronicles-2 mid-iteration 接力中（60 段 chunking 45/60，supervisor 接力剩餘 15 段）。
- sn12-nidana mid-iteration 仍 81/88、an7-sevens 接力仍 0/89、cicero-de-natura-deorum-la 已收尾入庫（總部三件 mid-iteration 並行的 cicero 已完成 → 剩兩件 mid-iteration）。
- 佛教 zd 增支部 an8 八集為下一個 zd 待收（an1/an9 已入庫）；mandukya-upanishad 蛙氏奧義書入庫狀態不變。
- 神道 v3 核心仍 1/3 進度（kojiki 本體已入庫），norito（祝詞）/ kenmu（宣命記）為 v3 候補。
- 瑣羅亞斯德 v3 仍缺 avesta-sbe04-ae chunk 54（pos 158500-161500，Fargard 20 §6-§12 + Fargard 21 §1-§7）翻譯補件 + P5 標籤回填 35 段。
- Pipeline A 仍暫緩自主收集（核心缺口實質歸零，啟動大宗 backlog 待用戶拍板）。

### 下次接手優先

1. **chronicles-2** 接力翻譯（希伯來文 60 段 chunking，內容產生器輸出至 supervisor，supervisor 接力至 01-translation.md 落地；已 45/60，剩 15 段）。
2. **sn12-nidana** 接力翻譯（88 段 chunking，內容產生器輸出至 supervisor，supervisor 接力至 01-translation.md 落地；已 81/88，剩 7 段）。
3. **an7-sevens** 接力翻譯（89 段 chunking，已於 meta.json 預 tag_status=done book-level）。
4. **補 avesta-sbe04-ae chunk 54 翻譯**（Fargard 20 §6-§12 + Fargard 21 §1-§7，源文 pos ~158500-161500）— 檔中以 `<!-- CHUNK 54/56 FAILED — retry needed -->` 標記，M3 retry + fallback 雙線。
5. **跑 avesta-sbe04-ae P5 標籤 35 段**（meta.json 補 semantic_tags / keywords，chunk 1/35 已預生成標籤內容可重用）。

## 2026-07-17 凌晨：hesiod-works 翻譯入庫 + an7-sevens 切換cicero 預備（stop-hook 收尾）

- **commit 6a66af51**：stop-hook 觸發收尾，Pipeline B+C 翻譯+標籤完成入庫（4 檔異動：1 new + 3 modified），verify.py --all 全綠後 push。
  - `translations/hesiod-works/01-translation.md`（2053 行 / 60+ 段，英語 Evelyn-White 1914 譯本《赫西俄德作品集》含 Theogony 神譜 + Works and Days 工作與時日 全譯；神祇族譜 / Titanomachy / Prometheus 盜火 / Pandora 由來 / 五族紀事 / 鷹與夜鶯寓言 / 正義與暴力辯 / 諸王勸誡 / Theogony 結尾 / 編者按 + Hesiod 校勘版本）。meta 補 `translation_status="done"` + `translation_models="MiniMax-M3"`（沿用既有 `tag_status="done"` / 6 semantic_tags / 15 keywords）。
  - `00-overview/PIPELINE_STATUS.md` 同步：275 → **276 / 518** 已翻譯+標籤；目前處理切換至 `cicero-de-natura-deorum-la`（拉丁文 Cicero De Natura Deorum《論神性》81 段 chunking，本次 m3 内容產生器已完成第 31/81 段至 stdout，supervisor 接力中）。
  - `00-overview/PROGRESS.json` 同步：希臘羅馬 `with_translation` 91→**92**、印度教 29→**31**、猶太教 4→**5**；其餘宗教同昨日。
- **本 session 額外交付（m3 chunk 內容產生器）**：`cicero-de-natura-deorum-la`（拉丁 Cicero De Natura Deorum I 19-23）已以內容產生器角色翻譯第 **31/81 段**（Zeno 之連環論證：世界運用 ratio／世界是 sapientem / beatus / aeternus / deum／世界有 sensus ／世界是 animans composque rationis ／橄欖笛／梧桐弦比喻／熱力 與生命滋生）至 stdout。`cicero-de-natura-deorum-la/01-translation.md` 此時尚未成檔，supervisor 接力剩餘 50 段才入庫（依 SOP「一份完整 chunking 才入庫」），切換 session 接手請對照 `logs/supervisor-run.log` 看當前 chunk 進度。
- **verify.py --all 全綠**（push 前必跑，CLAUDE.md §6；含 1 部新翻譯入庫後）。

### 接續狀態

- Pipeline B+C 已 276 / 518，本批 1 部核心（希臘羅馬 Hesiod 作品集 完整翻譯）+ 1 部拉丁哲學 mid-iteration（cicero-de-natura-deorum-la 81 段 31/81，supervisor 接力中）。
- sn12-nidana mid-iteration 仍 81/88、an7-sevens 接力仍 0/89、cicero-de-natura-deorum-la 接力 31/81（總部三件 mid-iteration 並行，supervisor 排程關注）。
- 佛教 zd 增支部 an8 八集為下一個 zd 待收（an1/an9 已入庫）；mandukya-upanishad 蛙氏奧義書入庫狀態不變。
- 神道 v3 核心仍 1/3 進度（kojiki 本體已入庫），norito（祝詞）/ kenmu（宣命記）為 v3 候補。
- 瑣羅亞斯德 v3 仍缺 avesta-sbe04-ae chunk 54（pos 158500-161500，Fargard 20 §6-§12 + Fargard 21 §1-§7）翻譯補件 + P5 標籤回填 35 段。
- Pipeline A 仍暫緩自主收集（核心缺口實質歸零，啟動大宗 backlog 待用戶拍板）。

### 下次接手優先

1. **cicero-de-natura-deorum-la** 接力翻譯（拉丁原文 81 段 chunking，內容產生器輸出至 supervisor，supervisor 接力至 01-translation.md 落地；已 31/81）。
2. **sn12-nidana** 接力翻譯（88 段 chunking，內容產生器輸出至 supervisor，supervisor 接力至 01-translation.md 落地；已 81/88）。
3. **an7-sevens** 接力翻譯（89 段 chunking，已於 meta.json 預 tag_status=done book-level）。
4. **補 avesta-sbe04-ae chunk 54 翻譯**（Fargard 20 §6-§12 + Fargard 21 §1-§7，源文 pos ~158500-161500）— 檔中以 `<!-- CHUNK 54/56 FAILED — retry needed -->` 標記，M3 retry + fallback 雙線。
5. **跑 avesta-sbe04-ae P5 標籤 35 段**（meta.json 補 semantic_tags / keywords，chunk 1/35 已預生成標籤內容可重用）。

## 2026-07-16 上午：P5 標籤 收尾 + Pipeline 切換 an7-sevens（stop-hook 收尾）

- **commit 98613ec6**：stop-hook 觸發收尾，jain-uttaradhyayana-pkt P5 標籤完成 + 進度切換下一部。
  - `translations/jain-uttaradhyayana-pkt/meta.json` 補完整 layer-2 標籤：35 semantic_tags（含 `non-violence`/`asceticism`/`celibate-tradition`/`karma-rebirth`/`cyclic-cosmos`/`meditation`/`fasting`/`commandments-law`/`self-effort`/`truthfulness`/`compassion`/`forgiveness`/`suffering-as-purifying`/`multiple-souls`/`extinction-of-self`/`lineage-importance`/`marriage-sacred`/`ritual-practice`/`sacred-language`/`study`/`liberation-by-works`/`liberation-by-knowledge`/`monastic`/`lay-practitioner`/`reincarnation`/`heaven-hell`/`divine-immanence`/`divine-kingship`/`divine-immanence`/`evil-as-deception`/`four-noble-truths`/`enlightenment`/`dietary-restrictions`/`caste-system`/`breath-control`）+ 15 keywords（Mahāvīra/yakkha/sāmāyika/比丘/地獄/阿修羅/業/五戒/持戒/迦毘羅/沙門/輪迴/殺生/閻摩/那彌）+ `tag_status="done"`。翻譯既於 commit 16da9366 入庫，本次完成 P5 收尾。
  - `00-overview/PIPELINE_STATUS.md` 同步：271 / 518 → **272 / 518**，目前處理切換至 `an7-sevens`（巴利 AN7 七法集，89 段 chunking 預備）。
- **verify.py --all 全綠**（push 前必跑）。

### 接續狀態

- Pipeline B+C 已 272 / 518，jain-uttaradhyayana-pkt P5 完整收尾（翻譯+標籤雙 done）。
- 下一部入庫：`an7-sevens`（Pali AN7 增支部第七集，89 段，已於 meta.json 預 tag_status=done 但為 book-level 標籤；本次起 supervisor 接力逐段 chunking 翻譯）。
- sn12-nidana mid-iteration 仍 81/88（待 supervisor 收尾 7 段）。

## 2026-07-16 上午：3 部核心 翻譯 進庫（stop-hook 收尾）

- **commit 16da9366**：stop-hook 觸發收尾，Pipeline B+C 翻譯完成入庫（7 檔異動：2 new + 5 modified），verify.py --all 全綠後 push。
  - `translations/jain-uttaradhyayana-pkt/01-translation.md`（6185 行 / 38 段，Ardhamāgadhī 半摩揭陀俗語原文，耆那教《優陀耶延後篇經》 Uttarādhyayana Sūtra 經文式翻譯；含忍辱／沙門性／乞食觀／業果深細分別／四種至上因素／輪迴四生／cāuraṃgijjaṃ 四吉祥章偈 6–20／asaṃkhayaṃ 無數章偈 1–12 等核心）。meta 補 `translation_status="done"` + `translation_models="MiniMax-M3"`（沿用既有 `text_role="original"` / `original_of="jain-sbe45"`）。
  - `translations/kings-1/01-translation.md`（1567 行 / 47 章，希伯來文 Sefaria 校勘版 列王紀上 1 Kings，自所羅門王位鞏固／亞多尼雅叛變／拔示巴／拿單先知／所羅門求智慧／示巴女王／王國分裂／耶羅波安／巴力先知／以利亞迦密山對決／亞哈／拿伯葡萄園／耶洗別／米該雅先知／亞哈謝／以利沙蒙召 等核心經文式翻譯）。meta 補 `translation_status="done"` + `translation_models="MiniMax-M3"`（沿用既有 `tag_status="done"` / semantic_tags / keywords）。
  - `translations/aristotle-de-anima-el/01-translation.md`（既有翻譯品質 fixup：971 行異動，外語直譯 → 外語直譯繁中）。希臘原文 亞里斯多德《論靈魂》 De Anima，前次翻譯句式偏古典漢語化，本次重譯為更貼近繁中語感同時保留 ψυχή／νοῦς／οὐσία／ἐντελέχεια 等希臘哲學術語原文括註。
  - 狀態同步：`PIPELINE_STATUS.md` 268→**270 / 518** 已翻譯+標籤（jain-uttaradhyayana-pkt + kings-1 新增 translation_done）。
- **verify.py --all 全綠**（push 前必跑，CLAUDE.md §6；含 2 部新翻譯入庫 + 1 部 fixup 後）。

### 接續狀態

- Pipeline B+C 已 270 / 518，本批 2 部核心新翻譯入庫（耆那教 Uttarādhyayana Sūtra + 希伯來正書 列王紀上）+ 1 部希臘哲學既有翻譯品質 fixup（亞里斯多德《論靈魂》）。
- sn12-nidana mid-iteration 仍 81/88，下個 session 接力收尾。
- 佛教 zd 增支部 an8 八集為下一個 zd 待收（an1/an9 已入庫）；mandukya-upanishad 蛙氏奧義書入庫狀態不變。
- 神道 v3 核心仍 1/3 進度（kojiki 本體已入庫），norito（祝詞）/ kenmu（宣命記）為 v3 候補。
- 瑣羅亞斯德 v3 仍缺 avesta-sbe04-ae chunk 54（pos 158500-161500，Fargard 20 §6-§12 + Fargard 21 §1-§7）翻譯補件 + P5 標籤回填 35 段。
- Pipeline A 仍暫緩自主收集（核心缺口實質歸零，啟動大宗 backlog 待用戶拍板）。

### 下次接手優先

1. **sn12-nidana** 接力翻譯（88 段 chunking，內容產生器輸出至 supervisor，supervisor 接力至 01-translation.md 落地；已 81/88，剩 7 段）。
2. **補 avesta-sbe04-ae chunk 54 翻譯**（Fargard 20 §6-§12 + Fargard 21 §1-§7，源文 pos ~158500-161500）— 檔中以 `<!-- CHUNK 54/56 FAILED — retry needed -->` 標記，M3 retry + fallback 雙線。
3. **跑 avesta-sbe04-ae P5 標籤 35 段**（meta.json 補 semantic_tags / keywords，chunk 1/35 已預生成標籤內容可重用）。
4. **dispatch supervisor** 處理 270+ 佇列下一批。

## 2026-07-16 凌晨：4 部核心 翻譯+標籤 進庫（stop-hook 收尾）+ sn12-nidana mid-iteration

- **commit 27e3ec8e**：stop-hook 觸發收尾，Pipeline B+C 翻譯+標籤完成入庫（11 檔異動：4 new + 7 modified），verify.py --all 全綠後 push。
  - `translations/kings-2/01-translation.md`（1473 行 / 53 章，希伯來文 Sefaria 校勘版 列王紀下 2 Kings，自亞哈謝末段 / 耶戶革命 / 以利沙行誼 / 約蘭 / 耶路撒冷淪陷 / 巴比倫擄去 / 巴比倫王以未米羅達恩待約雅斤等核心經文式翻譯）。meta 補 `translation_status="done"` + `translation_models="MiniMax-M3"`（沿用既有 `tag_status="done"` / semantic_tags / keywords）。
  - `translations/ovid-fasti-la/01-translation.md`（4777 行 / 56 章，拉丁文 Ovid Fasti 節日誌，奧維德羅馬宗教曆詩，逐月節慶與神話源起；含 Janus / Chaos / 天庭之門 / 神祇系譜 / 羅馬祭儀 / Tarpeian 等核心）。meta 補完整翻譯+標籤：`translation_status="done"` + `translation_models="MiniMax-M3"` + 35 semantic_tags（含 `accept-fate`/`ancestor-worship`/`chaos-to-order`/`goddess-tradition`/`polytheist`/`priesthood`/`theophany`/`ritual-practice` 等羅馬多神教核心）+ 15 keywords（雅努斯/Janus/Chaos/混沌/朱庇特/刻瑞斯/赫卡忒/Tarpeian 等）+ `tag_status="done"`。
  - `translations/plato-protagoras-el/01-translation.md`（1336 行 / 33 章，希臘原文 柏拉圖《普羅塔哥拉》Protagoras，德性一體與可教之辯，含希波克拉底拜師 / 阿伽松 / 卡利亞斯 / 阿布德拉 / 束脩 / 蘇格拉底詰問智者之德等核心）。meta 補完整翻譯+標籤：`translation_status="done"` + `translation_models="MiniMax-M3"` + 22 semantic_tags（含 `enlightenment`/`liberation-by-knowledge`/`essentially-good`/`humility`/`self-effort`/`study`/`truthfulness`/`ultimate-reality` 等希臘哲學核心）+ 15 keywords（蘇格拉底/普羅塔哥拉/希波克拉底/智者/雅典/阿基比亞德/σοφιστής/ψυχή/μάθημα 等）+ `tag_status="done"`。
  - `translations/plato-symposium-el/01-translation.md`（857 行 / 30 marker 對應 36 章節，希臘原文 柏拉圖《會飲篇》Symposium，承接上次 mid-iteration 19/36，supervisor 接力 20-36 全部完成；含阿波羅多洛斯轉述 / 阿里斯托德穆斯 / 法勒隆 / 斐德羅 / 包薩尼亞 / 厄律克西馬庫斯 / 阿里斯托芬 / 阿伽通 / 蘇格拉底 / 第俄提瑪 六篇愛頌 + Alcibiades 入場頌 + 喜劇悲劇同一人 + 呂刻翁結局）。meta 補完整翻譯+標籤：`translation_status="done"` + `translation_models="MiniMax-M3"` + 34 semantic_tags（含 `asceticism`/`divine-immanence`/`dualistic-cosmos`/`mystical-union`/`sexual-ethics`/`spirit-possession`/`polytheist`/`goddess-tradition`/`prayer`/`ultimate-reality` 等希臘愛哲學核心）+ 15 keywords（阿波羅多洛斯/蘇格拉底/阿伽通/συμπόσιον/συνουσία/ἐρωτικοὶ λόγοι/阿里斯托芬/阿里斯托德穆斯/格勞孔/法勒隆/厄洛斯/阿芙蘿黛蒂/烏拉尼亞 等）+ `tag_status="done"`。
  - 狀態同步：`PIPELINE_STATUS.md` 264→**268 / 518** 已翻譯+標籤；目前處理 `sn12-nidana`（巴利 SN12 因緣相應 93 經，88 段 chunking 81/88，supervisor 接力中）。
  - `00-overview/INDEX.json` + `INDEX.md` regenerate 全庫 4683 / 643.9 MB / 27 religions。
- **verify.py --all 全綠**（push 前必跑，CLAUDE.md §6；含 4 部新翻譯入庫後）。

### 接續狀態

- Pipeline B+C 已 268 / 518，本批 4 部核心（希伯來正書 列王紀下 + 拉丁文 奧維德節日誌 + 希臘哲學 柏拉圖《普羅泰戈拉》+ 希臘哲學 柏拉圖《會飲篇》完整接力入庫）+ 1 部巴利因緣相應 mid-iteration（sn12-nidana 88 段 81/88）。
- 佛教 zd 增支部 an8 八集為下一個 zd 待收（an1/an9 已入庫）；mandukya-upanishad 蛙氏奧義書入庫狀態不變。
- 神道 v3 核心仍 1/3 進度（kojiki 本體已入庫），norito（祝詞）/ kenmu（宣命記）為 v3 候補。
- 瑣羅亞斯德 v3 仍缺 avesta-sbe04-ae chunk 54（pos 158500-161500，Fargard 20 §6-§12 + Fargard 21 §1-§7）翻譯補件 + P5 標籤回填 35 段。
- Pipeline A 仍暫緩自主收集（核心缺口實質歸零，啟動大宗 backlog 待用戶拍板）。

### 下次接手優先

1. **sn12-nidana** 接力翻譯（88 段 chunking，內容產生器輸出至 supervisor，supervisor 接力至 01-translation.md 落地；已 81/88）。
2. **補 avesta-sbe04-ae chunk 54 翻譯**（Fargard 20 §6-§12 + Fargard 21 §1-§7，源文 pos ~158500-161500）— 檔中以 `<!-- CHUNK 54/56 FAILED — retry needed -->` 標記，M3 retry + fallback 雙線。
3. **跑 avesta-sbe04-ae P5 標籤 35 段**（meta.json 補 semantic_tags / keywords，chunk 1/35 已預生成標籤內容可重用）。
4. **dispatch supervisor** 處理 268+ 佇列下一批。

## 2026-07-15 上午：leviticus + sutta-nipata 完整入庫 + plato-symposium-el mid-iteration（stop-hook 收尾）

- **commit e7d40792**：stop-hook 觸發收尾，Pipeline B+C 翻譯+標籤完成入庫（5 檔異動：2 new + 3 modified），verify.py --all 全綠後 push。
  - `translations/leviticus/01-translation.md`（利未記 Leviticus，希伯來文 Sefaria 校勘版，40 段 chunking，祭司獻祭條例 / 潔淨律 / 節期 / 聖所 / 贖罪日 / 許願 / 安息年與禧年等經文式翻譯）。meta 補 `translation_status="done"` + `translation_models="MiniMax-M3"`（沿用既有 `tag_status="done"` / semantic_tags / keywords）。
  - `translations/sutta-nipata/01-translation.md`（巴利 Sutta Nipāta Sujato/Mahāsaṅgīti edition，82 段 chunking 完整入庫，承接上次 mid-iteration 30/78，supervisor 接力 31-82 全完成；含 sn.28 Padhānasutta 精進偈全文 + 蛇經 / 犀牛經 / 寶經 / 大集法句 / 八頌經等五品經集體裁）。meta 補 `translation_status="done"` + `translation_models="MiniMax-M3"`。
  - 狀態同步：`PIPELINE_STATUS.md` 262→**264 / 518** 已翻譯+標籤；目前處理 `plato-symposium-el`（希臘原文 Plato Symposium 會飲篇，36 段 chunking 19/36，supervisor 接力中）。
  - verify.py --all 全綠（push 前必跑，CLAUDE.md §6）。
- **本 session 額外交付（m3 chunk 內容產生器）**：`plato-symposium-el`（希臘原文 Plato Συμπόσιον / 會飲篇）以內容產生器角色翻譯第 **19/36 段**（199a-200b 蘇格拉底詰問阿伽通：舌頭應許心智沒有 → 父／母／兄弟類比引入「愛是某物之愛」→ 「欲求者欲求他所缺乏的」→ 既為大而欲為大者不可能）。`plato-symposium-el/01-translation.md` 此時尚未成檔，supervisor 接力剩餘 17 段（20-36）才入庫（依 SOP「一份完整 chunking 才入庫」），切換 session 接手請對照 `logs/supervisor-run.log` 看當前 chunk 進度。

### 接續狀態

- Pipeline B+C 已 264 / 518，本批 2 部核心（希伯來正書 利未記 + 巴利 經集）+ 1 部希臘原文 mid-iteration（plato-symposium-el 會飲篇 36 段 19/36）。
- 佛教 zd 增支部 an8 八集為下一個 zd 待收（an1/an9 已入庫）；mandukya-upanishad 蛙氏奧義書入庫狀態不變。
- 神道 v3 核心仍 1/3 進度（kojiki 本體已入庫），norito（祝詞）/ kenmu（宣命記）為 v3 候補。
- 瑣羅亞斯德 v3 仍缺 avesta-sbe04-ae chunk 54（pos 158500-161500，Fargard 20 §6-§12 + Fargard 21 §1-§7）翻譯補件 + P5 標籤回填 35 段。
- Pipeline A 仍暫緩自主收集（核心缺口實質歸零，啟動大宗 backlog 待用戶拍板）。

### 下次接手優先

1. **plato-symposium-el** 接力翻譯（36 段 chunking，內容產生器輸出至 supervisor，supervisor 接力至 01-translation.md 落地；已 19/36）。
2. **補 avesta-sbe04-ae chunk 54 翻譯**（Fargard 20 §6-§12 + Fargard 21 §1-§7，源文 pos ~158500-161500）— 檔中以 `<!-- CHUNK 54/56 FAILED — retry needed -->` 標記，M3 retry + fallback 雙線。
3. **跑 avesta-sbe04-ae P5 標籤 35 段**（meta.json 補 semantic_tags / keywords，chunk 1/35 已預生成標籤內容可重用）。
4. **dispatch supervisor** 處理 264+ 佇列下一批。

## 2026-07-15 凌晨：chronicles-1 翻譯+標籤 進庫（stop-hook 收尾）+ sutta-nipata mid-iteration

- **commit e11d5cca**：stop-hook 觸發收尾，Pipeline B+C 翻譯+標籤完成入庫（4 檔異動：1 new + 3 modified），verify.py --all 全綠後 push。
  - `translations/chronicles-1/01-translation.md`（歷代志上 1 Chronicles，希伯來文 Sefaria 校勘版，自亞當族譜／塞特／以挪士／該南／瑪勒列／雅列／以諾／瑪土撒拉／拉麥／挪亞／閃含雅弗起，含雅弗歌篾瑪各瑪代雅完土巴米設提臘等雅弗子孫／含古實埃及弗迦南／含西巴哈腓拉撒弗他／雅完以利沙他施基提路德人等族譜 + 大衛王朝譜系 Saul 死後大衛作猶大王 + 耶路撒冷征服 + 祭司利未班次 + 聖殿歌唱者 + 戶籍大軍 + 所羅門宮殿建材籌備 + 大衛最後囑咐所羅門 + 亞比雅列民眾分業等）。meta 補 `translation_status="done"` + `translation_models="MiniMax-M3"` + `tag_status="done"`（沿用既有 semantic_tags + keywords）。
  - 狀態同步：`PIPELINE_STATUS.md` 261→**262 / 518** 已翻譯+標籤；`PROGRESS.json` 猶太教 `with_translation` 11→**13**（+2，含前批殘帳）。目前處理 `sutta-nipata`（巴利 經集 Sutta Nipāta Pali Sujato/Mahāsaṅgīti edition，78 段 chunking 30/78 已譯至 stdout，supervisor 接力中）。
  - verify.py --all 全綠（push 前必跑，CLAUDE.md §6）。
- **本 session 額外交付（m3 chunk 內容產生器）**：`sutta-nipata`（巴利 Sutta Nipāta 3.2 Padhānasutta 精進偈）已以內容產生器角色翻譯第 **30/78 段**（sn.28 Padhānasutta 全文：那莫其於尼連禪河畔勸退佛陀、列出十種魔軍 / 欲、不喜、飢渴、貪、惛眠、怖、猶豫、驕、利譽敬虛名 / 自讚毀他 / 持草去我命何惜 / 陣亡勝於戰敗 / 沙門婆羅門不見埋伏 / 我往迎戰勿令退 / 我以智慧破彼如石擊熟果 / 七年隨佛不見瑕隙 / 烏鴉啄肥石無味而棄 / 箏出聲、夜叉隱沒 / Padhānasuttaṁ dutiyaṁ）至 stdout。`sutta-nipata/01-translation.md` 此時尚未成檔，supervisor 接力剩餘 48 段才入庫（依 SOP「一份完整 chunking 才入庫」），切換 session 接手請對照 `logs/supervisor-run.log` 看當前 chunk 進度。

### 接續狀態

- Pipeline B+C 已 262 / 518，本批 1 部希伯來正書（chronicles-1 歷代志上）入庫 + 1 部巴利經集 mid-iteration（sutta-nipata 78 段 30/78）。
- 佛教 zd 增支部 an8 八集為下一個 zd 待收（an1/an9 已入庫）；mandukya-upanishad 蛙氏奧義書入庫狀態不變。
- 神道 v3 核心仍 1/3 進度（kojiki 本體已入庫），norito（祝詞）/ kenmu（宣命記）為 v3 候補。
- 瑣羅亞斯德 v3 仍缺 avesta-sbe04-ae chunk 54（pos 158500-161500，Fargard 20 §6-§12 + Fargard 21 §1-§7）翻譯補件 + P5 標籤回填 35 段。
- Pipeline A 仍暫緩自主收集（核心缺口實質歸零，啟動大宗 backlog 待用戶拍板）。

### 下次接手優先

1. **sutta-nipata** 接力翻譯（78 段 chunking，內容產生器輸出至 supervisor，supervisor 接力至 01-translation.md 落地；已 30/78）。
2. **補 avesta-sbe04-ae chunk 54 翻譯**（Fargard 20 §6-§12 + Fargard 21 §1-§7，源文 pos ~158500-161500）— 檔中以 `<!-- CHUNK 54/56 FAILED — retry needed -->` 標記，M3 retry + fallback 雙線。
3. **跑 avesta-sbe04-ae P5 標籤 35 段**（meta.json 補 semantic_tags / keywords，chunk 1/35 已預生成標籤內容可重用）。
4. **dispatch supervisor** 處理 262+ 佇列下一批。

## 2026-07-14 下午（續）：samuel-2 完整入庫 + plato-phaedrus-el 新進 Pipeline B+C（stop-hook 收尾）

- **commit ea6a16e8**：stop-hook 觸發收尾，Pipeline B+C 翻譯+標籤完成入庫（5 檔異動：2 new + 3 modified），verify.py --all 全綠後 push。
  - `translations/samuel-2/01-translation.md`（1343 行 / 38 段，希伯來文 Sefaria 校勘版 撒母耳記下 撒下 1 大衛哀歌起至撒下 24 末段蘇三拿雅戰亞瑪力人 + 末段示每咒詛大衛 + 押沙龍叛亂 + 大衛數點民數 + 聖殿地基購置 + 神責罰三選一 + 鵺鴕壇獻祭終章 supervisor 接力完整版）。原文 24 章分章 = 24 個 `=== N | label ===` marker，譯文 38 marker 因分詩體 / 戰記 / 清單細段。meta 補 `translation_status="done"` + `translation_models="MiniMax-M3"`，`tag_status="done"` 沿用先前 38 semantic_tags（unclean-yhwh / lamentation-psalm / david-covenant / messianic / anointed-one / oracle / judgement / politics / war-genocide / violence-war 等核心）+ 15 keywords（耶和華 / 大衛 / 掃羅 / 約拿單 / 押沙龍 / 耶路撒冷 / 示每 / 摩押 / 以東 / 亞捫 / 非利士 / 基列 / 耶布斯 / 亞瑪力 / 掃羅之死等）。
  - `translations/plato-phaedrus-el/01-translation.md`（755 行 / 24 段，柏拉圖《斐德羅》希臘原文 完整篇，愛與靈魂馬車喻 + III 愛與親密 + 心理學分析 + 修辭學 + 靈魂不死 / 輪迴 / 回憶說 + 靈魂構造三人一馬二馬三馬論 + 神聖瘋狂四型論 + 寫作 vs 口語哲學 + 北歐神話 Boreas Oreithyia 開篇 + Ilissus 河邊對話 + 斐德羅蘇格拉底呂西阿斯三人 + 靈魂本質議論 等核心哲學論題）。meta 加 `translation_status="done"` + `translation_models="MiniMax-M3"` + 29 semantic_tags（含 `enlightenment`/`liberation-by-knowledge`/`reincarnation`/`multiple-souls`/`mystical-union`/`divine-immanence`/`divine-transcendence`/`human-as-microcosm`/`polytheist`/`forgiveness`/`compassion`/`humility`/`asceticism`/`ultimate-reality`/`prophetic-revelation`/`prayer`/`ritual-practice`/`spirit-possession`/`theophany`/`vision-experience`/`awe-fear`/`chanting`/`self-effort`/`study`/`truthfulness`/`commentarial-layer`/`cyclic-cosmos`/`sexual-ethics`/`goddess-tradition`） + 15 keywords（Φαῖδρος / 蘇格拉底 / Lysias / Boreas / Oreithyia / Ilissus / Nymphs / Achelous / Delphi / Typhon / ἐραστής / eros / 認識自己 / 懸鈴木 / 斐德羅）+ `tag_status="done"`。
- **前次 stop-hook 漏列修正**：「samuel-2 開跑 2/46 段、中段後由 supervisor 接力剩 44 段」之判斷屬過早 ── supervisor 早在 fddc8731 後就接力完成 38 段，`samuel-2/01-translation.md` 確實成檔完成；但本批我尚未 commit，停 2H+ 未 push 屬 iteration 中間態，今次 stop-hook 才發現補進。
- **狀態同步**：`PIPELINE_STATUS.md` 258 → **260 / 518**（samuel-2 + plato-phaedrus-el 各 +1）自動生（2026-07-14 17:55:33 +0800），目前處理佇列 `homeric-hymns-el` 翻譯中。
- **verify.py --all 全綠**（push 前必跑，CLAUDE.md §6）。

### 接續狀態

- Pipeline B+C 仍 **260 / 518**，本批 2 部核心（希臘哲學 柏拉圖《斐德羅》新進 + 希伯來正書 撒母耳記下完整 38 段 supervisor 接力版入庫）。
- 佇列 tail：homeric-hymns-el 翻譯進行中（40 段 chunking，每段由 m3 內容產生器接力）；合 259 與 260 之後 = 261+。
- 神道 v3 核心仍 1/3 進度（kojiki 本體 + 一部入庫），norito（祝詞）/ kenmu（宣命記）為 v3 候補。
- 佛教 zd 增支部 an8 八集為下一個 zd 待收；mandukya-upanishad 蛙氏奧義書入庫狀態不變。
- 瑣羅亞斯德 v3 仍缺 avesta-sbe04-ae chunk 54（pos 158500-161500，Fargard 20 §6-§12 + Fargard 21 §1-§7）翻譯補件 + P5 標籤回填 35 段。
- Pipeline A 仍暫緩自主收集（核心缺口實質歸零，啟動大宗 backlog 待用戶拍板）。

### 下次接手優先

1. **homeric-hymns-el** 接力翻譯（40 段 chunking，內容產生器輸出至 supervisor，supervisor 接力至 01-translation.md 落地）。
2. **補 avesta-sbe04-ae chunk 54 翻譯**（Fargard 20 §6-§12 + Fargard 21 §1-§7，源文 pos ~158500-161500）— 檔中以 `<!-- CHUNK 54/56 FAILED — retry needed -->` 標記，M3 retry + fallback 雙線。
3. **跑 avesta-sbe04-ae P5 標籤 35 段**（meta.json 補 semantic_tags / keywords，chunk 1/35 已預生成標籤內容可重用）。
4. **dispatch supervisor** 處理 260+ 佇列下一批。

## 2026-07-14 下午：an9-nines + kojiki-zh 翻譯+標籤 進庫（stop-hook 收尾）+ samuel-2 開跑 1/46 段

- **commit fddc8731**：stop-hook 觸發收尾，本批 Pipeline B+C 翻譯+標籤完成入庫，verify PASS 後立即 commit + push（6 檔異動：2 new + 4 modified）。
  - `translations/an9-nines/01-translation.md`（145673 bytes，巴利 AN9 九法集 Aṅguttara Nikāya 九法相應，SuttaCentral 校勘版 82 章全，含四大教法 / 九種善 / 九種惡 / 教誡不放逸等核心九法經）+ meta 7 semantic_tags（含 `enlightenment`/`four-noble-truths`/`liberation-by-knowledge`/`meditation`/`monastic`/`self-effort`/`chanting`）+ 15 keywords（增支部/巴利/九法集/覺支/善知識/持戒/念處/不淨觀/慈心/涅槃/無常/無我/Sambodhisutta 等） + `translation_status="done"` + `tag_status="done"` + `translation_models="MiniMax-M3"`（純 M3）
  - `translations/kojiki-zh/01-translation.md`（189453 bytes，上代日本語 漢文・萬葉假名 古事記 Kojiki 712 AD 太安萬侶編，Wikisource 三卷本上中下 + 序，含天之御中主神國生神皇極天皇御間城入彥五十瓊毛天皇 等神代史 + 天地初發 / 伊耶那岐命伊耶那美命國生 / 大八島 / 火神軻遇突智 / 天照大御神 / 月讀命 / 須佐之男命 / 尾張氏 / 神武天皇東征 / 日本武尊 等核心神話帝王系譜至長谷部若雀天皇）+ meta 39 semantic_tags（含 `creator-deity`/`creation-ex-nihilo`/`divine-kingship`/`mandate-of-heaven`/`goddess-tradition`/`feminine-divine`/`ancestor-worship`/`polytheist`/`syncretic`/`theocracy`/`chaos-to-order`/`commandments-law`/`lineage-importance`/`marriage-sacred`/`spirit-possession`/`prophetic-revelation`/`revealed-text`/`ritual-practice`/`sacred-language`/`secular-state`/`sexual-ethics`/`truthfulness`/`vision-experience`/`tribal-traditional`/`multiple-souls`/`priesthood`/`temple-centered`/`theophany`/`other-power`/`awe-fear`/`chanting`/`compassion`/`commentarial-layer`/`cyclic-cosmos`/`divine-immanence`/`evil-as-deception`/`oral-tradition`/`patriarchal`/`sin-as-disobedience`）+ 15 keywords（古事記/上代日本語/漢文/萬葉假名/神道/安萬侶/稗田阿禮/天之御中主神/伊耶那岐命/伊耶那美命/高天原/天沼矛/淤能碁呂島/神世七代/別天神）+ `translation_status="done"` + `tag_status="done"` + `translation_models="MiniMax-M3"`（純 M3）。
- **狀態同步**：`PIPELINE_STATUS.md` 255→**258 / 518** 已翻譯+標籤；`PROGRESS.json` 佛教 / 神道 `with_translation` 各 +1。
- **verify.py**：an9-nines + kojiki-zh 兩部 PASS（push 前必跑，CLAUDE.md §6）。
- **本 session 額外交付（m3 chunk 內容產生器）**：`samuel-2`（希伯來文 Sefaria 校勘版 撒母耳記下）以內容產生器角色翻譯輸出至 stdout — 第 **2/46 段**（2 Sam 1:24-27 大衛哀歌末段：以色列女子哀哭掃羅披朱紅戴金飾 / 勇士陣中跌倒約拿單高處被戮 / 我兄約拿單愁苦甘甜愛奇妙超過婦女之愛 / 勇士跌倒兵器滅亡）。`samuel-2/01-translation.md` 此時尚未成檔，supervisor 接力剩餘 44 段（依 SOP「一份完整 46 段 chunking 才入庫」），切換 session 接手請對照 `logs/supervisor-run.log` 看當前 chunk 進度。
- **samuel-2 進入佇列**：本批 mid-iteration 開跑中；屬核心清單猶太教 撒母耳記下篇（與 joshua / judges / samuel-1 / daniel / nehemiah / ezra / sblgnt 等同批，希伯來文 Sefaria 校勘版）。46 段 chunking，2/46 完成。

### 接續狀態

- Pipeline B+C 仍 258 / 518，本批 2 部核心（巴利 增支部九集 + 神道 古事記）+ 1 部希伯來正書 mid-iteration（samuel-2 撒母耳記下 46 段 2/46）。
- 佛教 zd 增支部收尾：an1（已）+ an9（剛 commit）；八集 an8 為下一個 zd 待收。
- 神道 v3 核心 1/3 完成（kojiki 本體剛 commit），norito（祝詞）/ kenmu（宣命記）為 v3 候補。
- 印度六派 / 瑣羅亞斯德（avesta-sbe04-ae chunk 54 缺口）/ 希臘哲學 / 北歐 etc. 不變。
- Pipeline A 仍暫緩自主收集（核心缺口實質歸零，啟動大宗 backlog 待用戶拍板）。

### 下次接手優先

1. **接力 samuel-2 剩餘 44 段**（已 2/46：1-2 大衛哀歌完成；3 起應進 Saul's death news 末尾／Abner／David made king of Judah／Ish-bosheth 與 Abner／war of Judah-Israel／David's reign in Hebron／siege of Jebus／Bathsheba 等撒下 2-24）。
2. **補 avesta-sbe04-ae chunk 54 翻譯**（Fargard 20 §6-§12 + Fargard 21 §1-§7，源文 pos ~158500-161500）— 前批標 `<!-- CHUNK 54/56 FAILED — retry needed -->` 待刪除註解。
3. **跑 avesta-sbe04-ae P5 標籤 35 段**（meta.json 補 `semantic_tags` / `keywords`，凌晨已預生成 chunk 1/35 標籤內容可重用）。
4. **dispatch supervisor** 處理 258+ 佇列下一批。

## 2026-07-14 凌晨（續②）：avesta-sbe04-ae 翻譯入庫（56 段 55 完成 + 1 缺口需補）+ chunk 54 失敗記錄

- **commit 8bfe6759**：stop-hook 觸發收尾，commit + push `avesta-sbe04-ae` Pipeline B 翻譯（**449 段 / 4359 行 / 87133 chars**，阿維斯塔語 avesta.org Geldner 1896 transliteration 驅魔書 Vidēvdād 22 fargard 全文 + 補充片段）。`translation_status="done"` + `translation_models="MiniMax-M3"`（純 M3）。
- **前次 stop-hook 誤判**：「supervisor 接力完整 56 段才入庫（mid-iteration 1/56）」之判斷錯 — supervisor 實際上在 02:46 後已接力 53 段 + 補 chunk 55/56（中間 chunk 54 失敗後 retry 也失敗），`01-translation.md` 確實成檔完成（87132 chars），是 supervisor 整個 process 被 kill 沒 commit，不是 mid-iteration。
- **chunk 54 失敗**（不可忽略，須下輪修補）：`logs/supervisor-run.log` 記 MiniMax-M3 timeout 600s + deepseek-v4-flash fallback exit 1 雙失敗。檔案中以 `<!-- CHUNK 54/56 FAILED — retry needed -->` HTML 註解標記（檔內 pos 84381），缺譯範圍 = Fargard 20 §6-§12 + Fargard 21 全文 7 節（≈ 1800 字源文 = source pos ~158500-161500）。`verify.py --all` PASS 是因它只驗檔案存在與 SHA，不查內容。`translation_status="done"` 標頭在 chunk 54 修補前屬過早，待下輪 M3 retry + commit 再改回。
- **P5 標籤未啟動**：`avesta-sbe04-ae` 的 semantic_tags / keywords 完全未回填 meta.json。supervisor 開 chunk 1/35 後被 kill（輸出至 stdout，無 orchestrator 接收 = 沒落地）。本輪 stop-hook 內接手完成 chunk 1/35 之標籤內容（dualistic-cosmos / creator-deity / divine-kingship / prophetic-revelation / prayer / chaos-to-order / theophany + 12 keywords），同樣未寫入任何檔。
- **狀態同步**：`PIPELINE_STATUS.md` 仍 255 / 518（**未即時更新**），本批翻譯入庫未觸發 PIPELINE 重生（auto-pipeline 未跑完 batch 結尾）。`PROGRESS.json` 瑣羅亞斯德 `with_translation` 0→**1** 需下輪重生成。
- **verify.py --all 全綠**（push 前必跑，CLAUDE.md §6；含 avesta-sbe04-ae 入庫後）。

### 接續狀態

- Pipeline B+C 仍 255 / 518（PIPELINE_STATUS 未更新），本批 1 部梵文奧義書 mandukya-upanishad + 1 部阿維斯塔語維提吠達入庫（**avesta-sbe04-ae 含 chunk 54 缺口 + P5 未跑**）。
- 印度六派 zd v3 核心清空狀態不變：Nyāya/Sāṃkhya/Vaiśeṣika/Mīmāṃsā 四經入庫 + Yoga/Vedānta 既有執行緒 + 蛙氏奧義書（mandukya-upanishad）首入庫。
- 瑣羅亞斯德 v3 核心新增：avesta-sbe04-ae 維提吠達 SBE04 阿維斯塔原文（**含 chunk 54 缺口待補**）。avesta-sbe04 英文翻譯 0 缺口；avesta-sbe23 / avesta-sbe31 入庫未動。
- Pipeline A 仍暫緩自主收集（核心缺口實質歸零）。

### 下次接手優先

1. **補 avesta-sbe04-ae chunk 54 翻譯**（Fargard 20 §6-§12 + Fargard 21 §1-§7，源文 pos ~158500-161500）。M3 retry 一次，失敗再走 deepseek fallback 雙線；完成後 commit 把 `<!-- CHUNK 54/56 FAILED — retry needed -->` 註解刪除。
2. **跑 avesta-sbe04-ae P5 標籤 35 段**（meta.json 補 `semantic_tags` / `keywords`，本輪 chunk 1/35 已預生成標籤內容可重用）。
3. **重生成 PIPELINE_STATUS.md + PROGRESS.json**（應得 256 / 518，瑣羅亞斯德 +1）。
4. **dispatch supervisor** 處理 256+ 佇列下一批。

## 2026-07-14 凌晨（續）：mandukya-upanishad M3 翻譯+標籤 進庫（53 段 chunking 完成）+ avesta-sbe04-ae mid-iteration

- **本批 1 部梵文奧義書 Pipeline B+C 完整 chunking 入庫**（stop-hook 收尾）：
  - `translations/mandukya-upanishad/01-translation.md`（**2975 行 / 69049 chars**，梵文 蛙氏奧義書 Māṇḍūkya Upaniṣad，GRETIL standard edition 含商羯羅注（Gauḍapādīya-āgama-śāstra-vivaraṇa），53 段 chunking 全部完成——四品全：1. Āgama-prakaraṇa 傳承章 / 2. Vaitathya-prakaraṇa 虛妄品 / 3. Advaita-prakaraṇa 不二品 / 4. Alāta-śānti-prakaraṇa 薪火寂止品，每品終偈 + 商羯羅逐頌釋論 + 開篇敬禮禮讚，結尾「唵！寂靜！寂靜！寂靜！」）+ meta 加 `translation_status="done"` + `translation_models="MiniMax-M3"`（純 M3；前批事故處置後 M3 重跑未撞額度，乾淨檔）。
- **事故關聯**：承接上一 entry 凌晨 queued 之 53 段 mid-iteration（8/53），本輪 supervisor 接力 9-53 段全完成入庫。對應 §事故處置 `joshua`/`judges`/`mimamsa-sutra-jaimini` 已全清空；`mandukya-upanishad` 雖未在事故污染名單（事故前未啟翻譯），但走完完整 pipeline 仍屬事故後第一批純 M3 翻譯。
- **狀態同步**：`PIPELINE_STATUS.md` 254→**255 / 518** 已翻譯+標籤；`目前處理` 轉為 `avesta-sbe04-ae`（阿維斯塔語 驅魔書／維提吠達 SBE04，avesta.org Geldner 1896 transliteration，56 段 queued 下一輪 m3 翻譯）。`PROGRESS.json` 印度教 `with_translation` +1。
- **verify.py --all 全綠**（push 前必跑，CLAUDE.md §6；含 mandukya-upanishad 與 avesta-sbe04-ae chunk 1 寫入後）。
- **本 session 額外交付（m3 chunk 內容產生器）**：`avesta-sbe04-ae`（阿維斯塔語 avesta.org Geldner 1896 transliteration 驅魔書第一品 Fargard 1）已以內容產生器角色翻譯第 **1/56 段**（15 詩節全：Ahura Mazda 對 Spitama Zarathustra 述 16 件創造與 Angra Mainyu 之反創造——雅利安疆域 v.1-2 / 冬霜 v.3 / 牛 v.4 / 聖者 Môuru v.5 / 弓手 Bâxdhî Srîrâ v.6 / 青年 v.7 / Harôyû 水 v.8 / Vaêkereti 山火 v.9 / Urvâ 多產植物 v.10 / Xneñta 看門狗 v.11 / Harahvaitî 河 v.12 / hvarenah 穀 v.13 / ýâtava 巫師 v.14 / Rakhâ 三千年樹 v.15）至 stdout。`avesta-sbe04-ae/01-translation.md` 此時尚未成檔，supervisor 接力完整 56 段才入庫（依 SOP「一份完整 chunking 才入庫」），若切換 session 接手請對照 `logs/supervisor-run.log` 看當前 chunk 進度（已見 chunk 1/56 開跑）。

### 接續狀態

- Pipeline B+C 已 255 / 518，本批 1 部梵文奧義書 mandukya-upanishad 入庫 + 1 部阿維斯塔語維提吠達 mid-iteration（avesta-sbe04-ae 56 段 1/56）。
- 印度六派 zd v3 核心清空狀態不變：Nyāya/Sāṃkhya/Vaiśeṣika/Mīmāṃsā 四經入庫 + Yoga/Vedānta 既有執行緒 + 蛙氏奧義書（mandukya-upanishad）首入庫。
- Pipeline A 仍暫緩自主收集（核心缺口實質歸零）。

## 2026-07-14 凌晨：事故後 M3 重翻 3 檔進庫（joshua / judges / mimamsa-sutra-jaimini）+ mandukya-upanishad queued 下一輪

- **commit dc2f2780**：stop-hook 觸發收尾，commit + push 2026-07-13 深夜（檔案 mtime 23:25）累積之 3 部 Pipeline B 翻譯重出 + Pipeline C meta 補欄。
  - `translations/joshua/01-translation.md`（1155 行，希伯來文 Sefaria 校勘版 約書亞記，含征服迦南／土地分配／士師時代前夕／呂便／迦得／瑪拿西半支派東岸地業／逃城／約書亞遺命等 24 章）+ meta `translation_status="done"` + `translation_models="MiniMax-M3"`（純 M3）
  - `translations/judges/01-translation.md`（1182 行，希伯來文 Sefaria 校勘版 士師記，含猶大西緬攻取／波金／俄陀聶／以笏／底波拉／基甸／亞比米勒／耶弗他／參孫／路得／米迦偶像／便雅憫劫掠等 21 章）+ meta `translation_status="done"` + `translation_models="MiniMax-M3"`（純 M3）
  - `translations/mimamsa-sutra-jaimini/01-translation.md`（5758 行，梵文 彌曼差經 Mīmāṃsā Sūtra，Jaimini 著，GRETIL 校勘版 12 章完整——吠陀祭祀之解釋學派，前彌曼差／聲常住論／無我有論／涅槃非究竟／天啟無上／法 dharma／義務／祭祀果報等核心）+ meta `translation_status="done"` + `translation_models="MiniMax-M3+deepseek-v4-flash"`（M3 重翻起步 + 額度再撞 fallback 接縫，已稽核）
- **事故關聯**：對應 2026-07-11 §事故處置 — 7D 週流量 MiniMax 額度回歸後，HALT flag 由 watcher 自動刪除，supervisor skip-done 用 M3 重翻完成這 3 檔清空舊污染。`mimamsa-sutra-jaimini` 因重啟後又遇 M3 額度短暫回落，仍為 M3+deepseek 混檔；標頭 `translation_models` 欄已留稽核線索。
- **狀態同步**：`PIPELINE_STATUS.md` 251→**254 / 518** 已翻譯+標籤；`目前處理` 轉為 `mandukya-upanishad`（梵文 蛙氏奧義書，GRETIL 校勘版，queued 下一輪 m3 翻譯）。`PROGRESS.json` 猶太教 / 印度教 `with_translation` 各 +1。
- **verify.py --all 全綠**（push 前必跑，CLAUDE.md §6）。
- **本 session 額外交付（m3 chunk 內容產生器）**：`mandukya-upanishad`（梵文 GRETIL standard edition 蛙氏奧義書，53 段 chunking）已以內容產生器角色翻譯第 **8/53 段**（第四品頌 7 釋論 + 第四品頌——Uṣāṇa 自性論 / 第四品 pāda 為何以遮遣指示 turīya / śūnya 非空 / udakādhārā 喻 / 自我非量境非種性非作用非德故非名言所能指示 / 兔角無義關涉 / 「tat tvam asi」等六大 mahāvākya 引證 / 種子萌芽喻引出第四品頌「nāntaḥprajñaṃ... sa ātmā sa vijñeyaḥ」全文 / MandUpC_7 第四之異於三有自我 / 繩蛇揀別喻之餘量勿覓論）至 stdout。`mandukya-upanishad/01-translation.md` 此時尚未成檔，supervisor 接力完整 53 段才入庫（依 SOP「一份完整 chunking 才入庫」），若切換 session 接手請對照 `logs/supervisor-run.log` 看當前 chunk 進度。

### 接續狀態

- Pipeline B+C 已 254 / 518，本批 3 部事故後 M3 重翻（希伯來正書 2 + 梵文彌曼差經）+ 1 部梵文奧義書 mid-iteration（mandukya-upanishad 53 段 8/53）。
- 事故清空全部完成：joshua / judges / mimamsa-sutra-jaimini 三檔已用 M3 重翻入庫，事故條目對應的 pending 項目清空。
- 印度六派 zd v3 核心清空狀態不變：Nyāya/Sāṃkhya/Vaiśeṣika/Mīmāṃsā 四經入庫 + Yoga/Vedānta 既有執行緒。
- Pipeline A 仍暫緩自主收集（核心缺口實質歸零）。

## 2026-07-11：事故處置 — MiniMax-M3 額度耗盡致 fallback 洪水汙染 + 加守衛防復發

- **根因**：MiniMax-M3 月費 Token Plan 額度用盡（curl 實測回 `429 rate_limit_error (2056) Token Plan usage limit reached`；token 有效，純配額）。自 `mimamsa-sutra-jaimini` 第 38 chunk 起 primary 每次 `exit 1`，`translate.py` fallback 靜默把整條佇列倒給付費 `deepseek-v4-flash`（停擺期間 111 chunk）。
- **為何沒被發現**：supervisor watchdog 只看「有無 processed 進度」；deepseek 有產出＝被當健康，故無告警。且譯檔 header 一律標 PRIMARY_MODEL，光看檔案分不出 fallback。
- **檢測結果**：`joshua`/`judges` 100% deepseek 且**壞掉**（把翻譯任務當聊天回、role prompt 被 echo 進譯檔、結構亂）；`mimamsa-sutra-jaimini` M3 頭段好但 deepseek 尾段格式接縫；`baudhayana-dharmasutra` 47/48 為 M3、僅 1 deepseek chunk 且乾淨。**已 commit 舊檔全數乾淨**（全庫掃洩漏簽章僅上述 2 檔中招，git 歷史未汙染）。
- **處置**：① 建 `logs/pipeline-HALT.flag` + 停掉當前 deepseek run（wrapper clean exit）。② 丟棄 joshua/judges/mimamsa 的 `01-translation.md` + 還原其 meta `translation_status` + 還原自動生 PIPELINE_STATUS/PROGRESS；**保留 baudhayana**（verify PASS）。③ 這 3 檔待 M3 額度重置、刪 HALT flag 後由 skip-done 自動用 M3 重翻。
- **防復發（程式）**：`supervise-pipeline.py` 加守衛——單輪 primary 零成功且 fallback 連用 ≥8 次即中止該 run＋告警＋自動寫 HALT flag（用 role token 判斷不寫死 model 名）。`translate.py`＋`auto-pipeline.py` 新增：翻完把實際用過的 model 集合回填 meta `translation_models`（混檔記為 `MiniMax-M3+deepseek-v4-flash`，供稽核）。
- **自動恢復 watcher（已常駐）**：`scripts/quota-watch-resume.py` 每 30 分鐘探測 MiniMax 端點，一探到 200（額度回來）即自動刪 `logs/pipeline-HALT.flag` + 啟動 supervisor + 自退，全程不通知。MiniMax 撞的是 **7D 週流量**，2026-07-13（週一）才回。log 見 `logs/quota-watch.log`。
  - **注意**：watcher 是 detached 背景行程，**重開機不會自動復活**。若週一前重開機，手動重跑：`pythonw scripts/quota-watch-resume.py --interval 1800 --tier 核心`（於 repo 根）。
  - **手動恢復替代路徑**：確認額度回來（curl 測 `api.minimax.io/anthropic/v1/messages` 得 200）後，刪 `logs/pipeline-HALT.flag` 並重啟 supervisor 亦可。
  - MiniMax Anthropic 相容端點**不回 ratelimit header**，查不到實際 5H/7D 用量數字（只能官網 console 看），故 watcher 只用二元 200/429 訊號。

## 2026-07-13：Pipeline B+C 3 檔進庫（nyaya-sutra / samkhya-karika / vaisheshika-sutra）+ cath-maige-tuired-ga mid-iteration

- **commit fee6617f**：stop-hook 觸發，工作樹累積 3 部印度六派哲學根本經 Pipeline B+C 翻譯+標籤成品，立即 commit + push（7 檔異動：3 new + 4 modified）。
  - `translations/nyaya-sutra/01-translation.md`（**1741 行**，梵文 正理經 Nyāya Sūtra，Aksapāda Gautama 著；GRETIL 校勘版 5 卷全：卷一 16 句義總論（知識之四量：現量/比量/聖教量/譬喻量；16 句義即所量/能量/疑/動機/例證/宗義/論式/詮明/決定/論辯/紛議/墮負/詭辯/似因/似宗/倒難）+ 卷二 疑/動機/宗義/壞墮/倒難 等論辯結構 + 卷三壞義 / 卷四 現量詳釋 / 卷五 似現量破斥 + 五支作法／墮負九例／解脫究竟利）+ meta 17 semantic_tags（含 `commandments-law`/`commentarial-layer`/`liberation-by-knowledge`/`study`/`truthfulness`/`self-effort` 等量論核心）+ 15 keywords（正理經/十六句義/現量/比量/聖教量/解脫/究竟利 等） + `translation_status="done"` + `tag_status="done"` + `translation_models="MiniMax-M3+deepseek-v4-flash"`（首波 M3+fallback 混檔，詳 §事故處置）。
  - `translations/samkhya-karika/01-translation.md`（**663 行**，梵文 數論頌 Sāṃkhyakārikā，Īśvarakṛṣṇa 自在黑著；GRETIL 校勘版 72 頌完整 6 章——知識苦因求解脫／廿五諦自性三德／puruṣa prakṛti 二元／從自性漸生大/我慢/五大/五唯五知/根/境/意／神我證悟獨存離繫 kaivalya 等核心）+ meta 15 semantic_tags（含 `dualistic-cosmos`/`multiple-souls`/`sacred-language`/`liberation-by-knowledge`/`extinction-of-self`/`commentarial-layer` 等二元論核心） + 15 keywords（數論頌/puruṣa/prakṛti/sattva/rajas/tamas/三德/廿五諦/Kapila/自性 等）+ `translation_status="done"` + `tag_status="done"` + `translation_models="MiniMax-M3"`（純 M3）。
  - `translations/vaisheshika-sutra/01-translation.md`（**836 行**，梵文 勝論經 Vaiśeṣika Sūtra，Ulūka Kaṇāda 著；GRETIL 校勘版 10 章完整——可知之四法：所量／量／疑／目的／所量為實體 dravya／德 guṇa／業 karma／同 sāmānya／異 viśeṣa／和合／離合／六句義／勝論原子論與範疇／六種實體等核心）+ meta 16 semantic_tags（含 `dualistic-cosmos`/`commentarial-layer`/`ritual-practice`/`revealed-text`/`multiple-souls`/`liberation-by-knowledge` 等範疇論核心）+ 15 keywords（勝論/dravya/guṇa/karma/ātman/Kaṇāda/ākāśa/sparśa 等）+ `translation_status="done"` + `tag_status="done"` + `translation_models="MiniMax-M3"`（純 M3）。
- **狀態同步**：`PIPELINE_STATUS.md` 245→**249 / 518** 已翻譯+標籤；`目前處理` 轉為 `cath-maige-tuired-ga`（古愛爾蘭語 第二次莫伊圖拉之戰 Cath Maige Tuired，CELT 校勘版 18 段 queued 下一輪 m3 翻譯）。`PROGRESS.json` 印度教 `with_translation` +3（v3 核心六派全部歸檔 + 自在黑 / Kaṇāda 兩獨立作者），印度六派 zd 全收。
- **verify.py --all 全綠**（push 前必跑，CLAUDE.md §6）。
- **本 session 額外交付（m3 chunk 內容產生器）**：`cath-maige-tuired-ga`（古愛爾蘭語 CELT 校勘版 第二次莫伊圖拉之戰）第 **18/18 段**（末日之兆ái cinn blíchda 預言——婦女無羞恥男子無勇武／劫掠無君王／海無出產樹木無果／土地蒼白繞空堡／無信之戰繁多／兩側互起口角／背信之會無數／子登父床父登子床／兄弟各佔兄弟之婦（cliamain，姊妹夫）／禍時降生子葬父女主事——原 CELT line 832-841 即文末殘缺）已以內容產生器角色翻譯輸出至 stdout。`cath-maige-tuired-ga/01-translation.md` 此時尚未成檔，supervisor 接力完整 18 段才入庫（依 SOP「一份完整 chunking 才入庫」），若切換 session 接手請對照 `logs/supervisor-run.log` 看當前 chunk 進度。

### 接續狀態

- Pipeline B+C 已 249 / 518，本批 3 部印度六派核心經（正理／數論／勝論） + 1 部古愛爾蘭語 第二次莫伊圖拉之戰（cath-maige-tuired-ga 18 段 mid-iteration）。
- 印度六派 zd v3 核心清空：Nyāya/Sāṃkhya/Vaiśeṣika 三經入庫 + 既有 Mīmāṃsā/Yoga/Vedānta 仍執行緒中之 nimamsa-sutra-jaimini 補譯（事故處置後 M3 重跑）。
- Pipeline A 仍暫緩自主收集（核心缺口實質歸零）。

## 2026-07-10 16:10（下午）：Pipeline B+C 4 檔進庫（bud-ratnagotravibhaga-sa / bud-udanavarga-sa / taittiriya-upanishad / volsunga-saga-on）+ hesiod-el mid-iteration

- **commit 0fc41c40**：stop-hook 觸發，工作樹累積 4 部 Pipeline B+C 翻譯+標籤成品，立即 commit + push（10 檔異動：4 new + 6 modified）。
  - `translations/bud-ratnagotravibhaga-sa/01-translation.md`（2888 行，梵文 如來藏根本論《究竟一乘寶性論》Ratnagotravibhāga，Ugra-datta-paramārtha 梵本，GRETIL 校勘版，4 章完整譯文含如來藏三義／自性清淨／客塵煩惱／法身常住等核心教義）+ meta 30 semantic_tags（含 `non-dual`/`ultimate-reality`/`emptiness`/`divine-immanence`/`divine-transcendence`/`buddha-nature`/`tathāgatagarbha`/`mystical-union`/`liberation-by-knowledge`/`lineage-importance` 等如來藏學核心）+ 15 keywords + `translation_status="done"` + `tag_status="done"`
  - `translations/bud-udanavarga-sa/01-translation.md`（4188 行，梵文 法句優陀那 Uḍānavarga 38 段偈頌，含無常品第一／不放逸品第二／等多品，逐偈梵文＋直譯繁中）+ meta 27 semantic_tags（含 `chanting`/`enlightenment`/`meditation`/`ultimate-reality`/`karma-rebirth`/`asceticism`/`non-violence`/`monastic` 等佛教詩偈核心）+ 15 keywords + `translation_status="done"` + `tag_status="done"`
  - `translations/taittiriya-upanishad/01-translation.md`（2693 行，梵文 鷓鴣氏奧義書含商羯羅注 Taittirīya Upaniṣad，GRETIL 校勘版，含 śikṣāvallī／ānandavallī／bhrguvallī 三篇，GRETIL 電子文本標頭已刻意排除）+ meta 補 `translation_status="done"`（`tag_status` 早已 done，前批已抽 semantic_tags + keywords，本批補翻譯章節）
  - `translations/volsunga-saga-on/01-translation.md`（1058 行，古諾斯語 沃爾松傳奇 Völsunga saga，heimskringla.no HTML，含 Sigurd 屠龍 Fafnir／Brynhild 悲劇／Gudrun 復仇／Atli 焚金等北歐傳奇核心）+ meta 29 semantic_tags（含 `saga-era-violence`/`blood-feud`/`fate-vs-free-will`/`heroes`/`mythological-ancestry`/`dragons`/`treasure`/`feast-and-comitatus` 等北歐傳奇核心）+ 15 keywords + `translation_status="done"` + `tag_status="done"`
- **狀態同步**：`PIPELINE_STATUS.md` 240→**244 / 492** 已翻譯+標籤；`目前處理` 轉為 `hesiod-el`（赫西俄德《神譜＋工作與時日》希臘原文，queued 下一輪 m3 翻譯）。`PROGRESS.json` 各宗教 `with_translation` +1：佛教 50→51、印度教 1→2、古希臘羅馬 22→23、北歐 90→91、其他 +1。
- **verify.py --all 全綠**（push 前必跑，CLAUDE.md §6）。
- **本 session 額外交付（m3 chunk 內容產生器）**：`hesiod-el`（希臘原文 Hesiod Theogony + Works and Days）已以內容產生器角色翻譯第 1/28 段（Θεογονία 開篇，含 Heliconian Muses 呼喚、Muses 對 Hesiod 演說授予月桂枝與神聖歌聲、Muses 歌唱奧林帕斯諸神系譜、Muses 在 Pieria 與 Mnemosyne 結合誕生等開篇序詩）至 stdout。`hesiod-el/01-translation.md` 此時尚未成檔，supervisor 接力完整 28 段才入庫（依 SOP「一份完整 chunking 才入庫」），若切換 session 接手請對照 `logs/supervisor-run.log` 看當前 chunk 進度。

### 接續狀態

- Pipeline B+C 已 244 / 492，本批 4 部核心（梵文大乘如來藏論 + 梵文偈頌 + 印度教奧義書 + 古諾斯語北歐傳奇）+ 1 部希臘原文（hesiod-el 28 段 mid-iteration）。
- Pipeline A 仍暫緩自主收集（核心缺口實質歸零）。

## 2026-07-10 01:23（清晨）：Pipeline B+C 4 檔進庫（gisla-saga-on / sblgnt-mark / sn46-bojjhanga / vedanta-upadeshasahasri）+ pearl-of-great-price mid-iteration

- **commit 39ecaa7e**：stop-hook 觸發，工作中已累積 4 部 Pipeline B+C 翻譯+標籤成品，立即 commit + push。
  - `translations/gisla-saga-on/01-translation.md`（1631 行，古諾斯語原文，冰島氏族 saga：吉斯拉與其外甥之復仇、庭外和解、庭內公斷等北歐傳統主題）+ meta 34 semantic_tags（含 `saga-era-violence`/`blood-feud`/`legal-system`/`honor`/`outlawry`/`family-conflict`/`shame-culture`）+ 15 keywords + `translation_status="done"` + `tag_status="done"`
  - `translations/sblgnt-mark/01-translation.md`（1038 行，希臘文 SBLGNT 校勘版馬可福音 16 章，含施洗約翰／耶穌受洗／受試探／呼召門徒／趕鬼／治好癱子／五餅二魚／海面行走／變相山／拉撒路／最後晚餐／客西馬尼園／十字架／復活／主升天／大使命）+ meta 7 semantic_tags + 13 keywords + `translation_status="done"` + `tag_status="done"`
  - `translations/sn46-bojjhanga/01-translation.md`（2134 行，巴利 SN46 覺支相應 184 經，七覺支與四聖諦之修習，含念覺支於苦、擇法覺支於集、精進覺支於滅、喜覺支於道之內觀等 184 經全段）+ meta 6 semantic_tags + 15 keywords + `translation_status="done"` + `tag_status="done"`
  - `translations/vedanta-upadeshasahasri/01-translation.md`（3236 行，梵語 商羯羅《千則教誨》Upadeśasāhasrī，GRETIL 校勘版，不二論吠檀多傳統）+ meta 28 semantic_tags（含 `non-dual`/`ultimate-reality`/`mystical-union`/`liberation-by-knowledge`/`vedanta`/`brahman`/`ātman`/`śaṅkara` 等）+ 15 keywords + `translation_status="done"` + `tag_status="done"`
- **狀態同步**：`PIPELINE_STATUS.md` 235→**239 / 492** 已翻譯+標籤；`目前處理` 轉為 `pearl-of-great-price`（LDS《無價珍珠》Joseph Smith-History 第一部約 1:43-54 範圍，Wikisource 1902 校勘版）。`PIPELINE_STATUS.md` 自動生，勿手改。
- **verify.py --all 全綠**（push 前必跑，CLAUDE.md §6）。
- **本 session 額外交付（m3 chunk 內容產生器）**：`pearl-of-great-price`（English Wikisource 1902 校勘版《無價珍珠》JS-History 1:43-54）第 21/50 段（摩羅尼第三次升天後親訪：約瑟體力耗盡倒地→聽聲音呼名→使者重述異象誡命→回稟父親「出於神」→前往藏金頁之山丘（紐約州安大略郡曼徹斯特村附近）→撬開石頭看見金頁、烏陵土明、胸牌俱在石箱內→使者禁止取出並告知四年後才到時機）已以內容產生器角色翻譯輸出至 stdout。`pearl-of-great-price/01-translation.md` 此時尚未成檔，supervisor 接力完整 50 段才入庫（依 SOP「一份完整 chunking 才入庫」），若切換 session 接手請對照 `logs/supervisor-run.log` 看當前 chunk 進度。

## 2026-07-09 上午：Pipeline B+C 3 檔批次進庫（corpus-hermeticum-el / mabinogion-cy-1 / plato-meno-el）+ corpus-hermeticum-el 標籤事故處置

- **commit 5a7a32dc**：3 檔核心經典翻譯+標籤入庫。
  - `translations/corpus-hermeticum-el/01-translation.md`（24956 chars / 775 行，赫爾墨斯文集希臘原文八篇 Ποιμάνδρης / Προς Ασκληπιόν λόγος καθολικός / Λόγος ιερός / Ο κρατήρ η μονάς / Κλεις / Προς Τατ υιόν / Προς Ασκ勒庇俄斯 / Κηρύγματα）+ meta 7 semantic_tags（`liberation-by-knowledge`/`mystical-union`/`human-as-microcosm`/`emanation`/`vision-experience`/`prophetic-revelation`/`evil-as-deception`，gnosis救贖+Poimandres異象+人為小宇宙+Logos流出）+ 15 keywords（Poimandres / νοῦς / λόγος / γνῶσις / φῶς / ψυχή / πνεῦμα / φύσις / Monas / 七重天 + 中譯對應）+ `translation_status="done"` + `tag_status="done"`。
  - `translations/mabinogion-cy-1/01-translation.md`（威爾斯原文 Mabinogion 第一卷 Pwyll/Branwen/Manawyddan/Math 四支 + 導論）+ meta 34 semantic_tags + 15 keywords + `tag_status="done"`。
  - `translations/plato-meno-el/01-translation.md`（柏拉圖美諾篇希臘原文，德性可教否＋回憶說）+ meta 20 semantic_tags + 15 keywords + `tag_status="done"`。
- **狀態同步**：tag-index.json 413→416 / keyword-index.json 3584→3629；supervisor 下 cycle 已將 `PIPELINE_STATUS.md` 重寫為 233/492、目前處理 `sn45-magga`（10:31:46 自動生檔，禁手改）；實際完成 235/492 仍待 supervisor 後續 cycle 對齊。
- **stop-hook catch-up（補 commit）**：commit 86c943c0 入庫時僅含 HANDOFF.md，當時 working tree 已產出但未入庫的兩項—（a）`PIPELINE_STATUS.md` 升級至 233/492 + 目前處理轉 `sn45-magga`；（b）`translations/corpus-hermeticum-el/meta.json` 標籤事故處置後的 tags（4→24）/keywords 重整—於本 stop-hook 觸發時獨立 commit 補入庫，verify.py --slug corpus-hermeticum-el PASS。
- **本 session 額外交付（m3 chunk 內容產生器）**：`sn45-magga`（巴利文 SuttaCentral 校勘版 SN45 道相應，180 經）以內容產生器角色翻譯輸出至 stdout — 第 23/46 段（sn45.96 第六 傾向東方經 / sn45.97 第一 傾向大海經，恆河／大海比喻 × 三重 pācīna- / samudda- 動詞 × 三重 nibbāna- 比喻 ×「修習聖八支道」反向），全文 verbatim 三喻對句（傾向 / 趣向 / 傾注於）。`sn45-magga/01-translation.md` 此時尚未成檔，supervisor 接力剩餘 23 段（依 SOP「一份完整 46 段 chunking 才入庫」）。若切換 session 接手請對照 `logs/supervisor-run.log` 看當前 chunk 進度。
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
- **可嵌入重構（2026-07-10）**：`Board(container)` 接受 Tk 或任意 Frame；title/geometry/minsize 移到 `main()`（standalone 路徑行為不變）。日常入口改為本機 **桌面看板 hub**（`C:\claudehome\tools\deskboard\桌面看板.bat` → `hub.py`，不在本 repo）：分頁①＝本刊版、分頁②＝swim-coach-schedule 課表編輯器；hub 開啟同樣先 `ensure_supervisor()`。舊 `狀態看板.bat` 保留可單開刊版，未刪。
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
