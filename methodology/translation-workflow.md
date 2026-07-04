# 翻譯工作流 SOP

> 整個專案的翻譯原則：原文優先 → AI 翻譯 → 交叉比對
> 啟動：2026-06-29

## 1. 為什麼不要現成譯文

- **譯本有立場**：KJV（英王欽定本）為英國國教立場；LXX 七十士譯本與 MT 馬索拉抄本舊約結構不同；Legge 譯儒道帶 19 世紀基督教傳教士視角；Griffith 譯吠陀帶維多利亞時代東方主義
- **AI 翻譯是獨立第三方**：無教派歸屬、無時代偏見（雖然 LLM 也有 bias，但至少沒有「譯者自陳神學預設」的包袱）
- **交叉比對**：現有譯本只作「其他解讀可能性」對照，標明差異處

## 2. 工作流（每部經典）

### Step 1：取得原文

**來源優先序**（原文 → 校勘版 → 標準譯文對照）：

| 語言 | 推薦來源 |
|------|---------|
| 古典漢語 | ctext.org、wikisource、Chinese Text Project、四部叢刊 |
| 梵文 | GRETIL、WISDOMLIB、梵文電子文本（Sanskrit Library）、GRETIL |
| 巴利 | suttacentral.net、Vipassana Research Institute |
| 希臘（古典）| Perseus、first1kgreek、SOP |
| 希臘（新約）| SBLGNT、Textus Receptatus、WLC |
| 希伯來 | Sefaria、Mechon Mamre、Miqra |
| 阿拉姆 | Sefaria、Comprehensive Aramaic Lexicon |
| 阿拉伯 | Quran.com、Tanzil、Shamela |
| 波斯 | Ganjoor、avesta.org |
| 阿維斯塔 | avesta.org |
| 蘇美 / 阿卡德 | ETCSL（Oxford）、CDLI |

### Step 2：AI 翻譯（經文式，非白話化）

**權威規則見 [`tools/m3-translator-role.md`](../tools/m3-translator-role.md)** — 派 m3 跑翻譯前每次把該檔角色段塞進 prompt 開頭。核心原則（別在此重述細節，以角色檔為準）：

- **古典漢語原文（道德經、論語、CBETA 漢譯等）→ 原樣保留**，只做簡→繁 + 訛字修正，**禁止白話化重寫**（「子曰」不改「孔子說」）
- **外語原文 → 直譯繁中**，維持直譯不流暢化；名相保留原文 + 首次附一個常用漢譯（karma（業）、λόγος（道）、YHWH（耶和華）），後續只用原詞
- **不編造**：原文模糊標 `[歧義: A / B]`，並列兩說不自己選
- **詩體保詩體 / 偈頌保偈頌**：吠陀、詩篇、法句經行斷保留，不翻成散文
- **結構標記 `=== N | label ===` 原樣保留**，段落結構照原文不重編
- **翻譯 ≠ 解釋**：白話解釋、Sanskrit 對照、文化背景全歸 `02-annotation.md`

### Step 3：交叉比對

**不主用**現成譯本，但**對照**以下常見譯者，標出差異：

| 語言 | 對照譯者 |
|------|---------|
| 古典漢語 | James Legge、Arthur Waley、Wing-tsit Chan、Edward Slingerland（道德經）|
| 梵文 / 吠陀 | Ralph T.H. Griffith、Max Müller、Juan Mascaró |
| 巴利 | Thanissaro Bhikkhu、Bhikkhu Bodhi、PTS 譯 |
| 希臘（新約）| KJV、ESV、NIV（多版本對照）|
| 希伯來 | JPS 1917、Tanakh 1985 |
| 阿拉伯 | Pickthall、Yusuf Ali、Sahih International |

每個翻譯註腳寫：
- 原文詞 X
- AI 譯：「...」
- 現成譯 A 譯：「...」
- 現成譯 B 譯：「...」
- **差異原因**：語法 / 詞義歧義 / 文化背景

### Step 4：記錄差異與爭議

每一段翻譯都記：

```markdown
## [段落編號]

**原文**：
> [原語言]

**AI 翻譯**：
> [繁中白話]

**交叉驗證**：
| 譯者 | 譯法 | 差異原因 |
|------|------|---------|
| [A] | [...] | [...] |
| [B] | [...] | [...] |

**歧義註**：[如有]
```

### Step 5：語義標籤（Pipeline C，翻譯後即做）

翻譯完成後**同一部立刻抽標籤**，供跨經文搜尋與連結。**權威規則見 [`tools/m3-tagger-role.md`](../tools/m3-tagger-role.md)**：

- `semantic_tags`：**受控詞彙**（closed set），只能填 [`00-overview/concepts.md`](../00-overview/concepts.md) 14 大類白名單內的英文 tag，挑真正切題的 3–8 個。白名單外的詞一律進 `keywords`。orchestrator 會用白名單過濾，違規 tag 自動丟棄。
- `keywords`：**自由詞**（open set）5–15 個，神名 / 人名 / 地名 / 關鍵術語 / 核心主題，保留原文術語原樣（karma 不寫「業力」）。
- 兩者回填 `meta.json` 的 `semantic_tags` / `keywords` 欄位（**不動 `raw/original.txt`**，SHA-256 是對原文算的，不會破 verify）。
- 全批跑完 `scripts/build-tag-index.py` 生反向索引 `00-overview/{tag-index.json, keyword-index.json}`（tag/keyword → 共享它的經文清單 = 跨經文連結結構）。

### Step 6：自動化協調（tier 佇列驅動）

`scripts/auto-pipeline.py` 把 Step 2→5 串成可續跑管線：

```bash
# 小批驗證（3 部核心，不 push）
PYTHONIOENCODING=utf-8 python scripts/auto-pipeline.py --tier 核心 --limit 3 --no-push

# 全量自動跑核心（可隨睡眠中斷後重啟，--skip-done 是預設）
PYTHONIOENCODING=utf-8 python scripts/auto-pipeline.py --tier 核心
```

- **tier 佇列**：`meta.json` 的 `tier`（核心 / 次要 / 總集）決定順序；先跑核心。
- **續跑 / 容錯**：已翻+已標的 slug 自動跳過；失敗進 `logs/pipeline-failed.json` 不中斷整批。
- **git 安全**：只 `git add` 本次觸碰的路徑（絕不 `-A`），與 Pipeline A 收集並行不互踩；每批 `pull --rebase` 後 push。
- 進度寫 `00-overview/PIPELINE_STATUS.md`（自動生，勿手改）。

## 3. 檔案結構

每部翻譯獨立 .md：

```
translations/
├── tao-te-ching/
│   ├── 01-translation.md     ← AI 翻譯 + 交叉驗證
│   ├── 02-variants.md        ← 重要章節多解對比
│   └── 03-sources.md         ← 原文來源、版本說明
├── bhagavad-gita/
│   └── ...
```

## 4. AI 翻譯的已知限制

- **多義詞**：原語言一詞多義時，AI 傾向選最常見解
- **文化 load word**：印度教 / 佛教 / 道教概念在中文沒有完全對應
- **詩律**：原文押韻 / 節奏無法完整保留在中文白話
- **古文語法**：古典漢語 / 梵文 / 阿拉伯文的省略主詞、特殊語序難百分百還原

**對策**：以上情況必須交叉驗證 + 註明

## 5. 工作進度追蹤

每部翻譯建立 checklist：

- [ ] 抓原文（原文資料庫 URL）
- [ ] 確認版本（哪個抄本 / 校勘版）
- [ ] AI 翻譯全文
- [ ] 交叉比對（≥2 譯者）
- [ ] 標記歧義處
- [ ] commit + push

## 6. 順序建議（由短到長）

1. **道德經**（81 章，~5000 字）— 古典漢語，啟動最易
2. **薄伽梵歌**（18 章，~700 詩節）— 梵文
3. **心經**（260 字）— 梵文 / 中文
4. **金剛經**（~3000 字）— 梵文 + 鳩摩羅什漢譯
5. **古蘭經開端 + 第 1 卷**（Al-Fatiha + 部分）
6. **新約四福音**（希臘文）
7. **吠陀選粹**（梨俱吠陀頌選）
8. **奧義書**（核心 13 部）
9. **聖經舊約**（希伯來文）

優先做「短而完整」的典籍 → 建立工作流 → 處理大部頭。

## 7. 不做

- ❌ 全文僅靠現成譯本（即使「品質高」）
- ❌ AI 翻譯後不交叉驗證
- ❌ 跳過原文直接翻譯英譯
- ❌ 為了通順扭曲原文（增字 / 減字）
- ❌ AI 翻譯混入「我的註解」或「現代詮釋」