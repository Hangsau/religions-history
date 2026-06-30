# Strategy — 蒐集 / 網站 / 標籤

## 1. 蒐集策略（最大覆蓋）

### 1.1 已實作下載器（8 個）

| Script | 來源 | 對應宗教 |
|--------|------|---------|
| download-ctext.py | api.ctext.org | 道教 / 儒教 漢系 |
| download-wikisource.py | zh/ja/en/la/sa Wikisource | 道教 / 儒教 / 基督教中譯 / 神道 / 世界古典英譯 |
| download-cbeta.py | GitHub cbeta-org/xml-p5 | 漢譯佛經 (TEI P5) |
| download-quran.py | api.quran.com | 古蘭經 |
| download-sefaria.py | sefaria.org/api | 猶太教 + 部分基督教 OT |
| download-suttacentral.py | suttacentral.net/api | 巴利三藏 |
| download-gretil.py | gretil.sub.uni-goettingen.de | 梵文印度教 + 部分佛教 |
| verify.py | local | SHA-256 + chapter count + size |

### 1.2 待加下載器（覆蓋剩 15%）

| Script | 來源 | 對應 | 優先 |
|--------|------|------|------|
| download-sblgnt.py | GitHub LogosBible/SBLGNT | 希臘新約 | A |
| download-cbeta-full.py | github cbeta-org/xml-p5 | 大正藏全部 + 卍續藏 | A |
| download-sefaria-full.py | sefaria API recursive | 巴比倫塔木德全 / Mishneh Torah / Zohar | A |
| download-suttacentral-deep.py | suttacentral per-samyutta | 巴利 SN/AN/KN 全展開 | A |
| download-sacred-texts.py | sacred-texts.com | 1500+ 各宗教（Avesta、Mandaean、Bahai 等 catch-all）| B |
| download-avesta.py | avesta.org | 瑣羅亞斯德 | B |
| download-etcsl.py | etcsl.orinst.ox.ac.uk | 兩河蘇美 | B |
| download-perseus.py | perseus.tufts.edu | 古希臘羅馬 | B |
| download-ndl.py | dl.ndl.go.jp | 神道 NDL 全文 | C |
| download-bahai-ref.py | reference.bahai.org | 巴哈伊核心 | C |

### 1.3 階段化目標

- **Phase A** ✓ 完成：~234 部 / 9 宗教覆蓋核心
- **Phase B**（接下來）：補齊主要宗教原文 + 中型總集 → ~500 部
- **Phase C**：大型總集（大正藏 / 道藏 / 塔木德 / Mishneh Torah / 教父全集）→ ~3,000 部
- **Phase D**：邊緣 + 現代新興補完 → ~5,000 部
- **Phase E**：全本逐部展開（道藏 5305 卷 / 大正藏 2200 部 / 等）→ ~30,000+ 部

---

## 2. 網站架構

### 2.1 技術選型

**Astro + Pagefind + Cloudflare Pages**

理由：
- 全靜態 → 1ms 級回應、零 server 成本
- Astro 對大量 markdown 友善（每部經文 = 1 page）
- Pagefind 客戶端全文搜尋（不依賴 server）
- Cloudflare Pages 免費部署

### 2.2 資料流

```
translations/<slug>/meta.json  →  Astro 頁面 frontmatter
translations/<slug>/raw/original.txt  →  Astro 頁面 body
                                       →  Pagefind index
```

每部經文一頁。頁面顯示：
- 原文文本（含章節分隔）
- meta（religion / tradition / language / era / source）
- 對照英譯（若有 translation-en.txt）
- 跨宗教 link（相同主題 / 概念）— 需標籤完成才有

### 2.3 站內導航

- **/index**：23 宗教總覽 + 統計
- **/religion/<id>**：該宗教概覽 + 該宗教所有經文列表
- **/text/<slug>**：單部經文頁
- **/search?q=...**：Pagefind 全文搜尋
- **/theme/<theme>**：主題索引（如 救贖 / 創世 / 戒律）— 待 P4 完成
- **/about**：方法論、來源、引用

### 2.4 開發時程

- 啟動：等所有 Phase B 完成 (Phase C 之前)
- 框架 + 第一版（無語義標籤）：1-2 週
- 加語義搜尋（標籤完成後）：再 1 週

---

## 3. 標籤 + 索引架構

### 3.1 兩層標籤

**Layer 1 — 結構標籤（meta.json 內，下載時即填）**

已有：
- `religion`：23 宗教 enum
- `language`：原語言
- `version`：版本
- `version_date`：成書年代
- `source_platform`
- `tier`：核心 / 次要 / 總集

新加（已加部分）：
- `tradition`：佛教傳統（巴利 / 漢傳 / 藏傳 / 梵文原典 / 其他）
- `genre`：經典類型（神話史詩 / 法典 / 哲學論 / 詩歌讚頌 / 祈禱儀軌 / 注疏 / 史傳）
- `region`：地理（南亞 / 東亞 / 中亞 / 西亞 / 歐洲 / 美洲 / 非洲 / 大洋洲）
- `era`：時代（前軸心期 / 軸心期 / 古代 / 中古 / 近代 / 現代）
- `author`：作者（已知者）
- `translator`：譯者（譯文者）
- `is_original_language`：bool（true = 原文 / false = 譯文）

**Layer 2 — 語義標籤（LLM 抽取，P4 翻譯後做）**

跨宗教概念表（受控詞彙 controlled vocabulary）：
- 神論：一神 / 多神 / 泛神 / 神秘主義神論 / 無神 / 不可知
- 創世：太初 / 流溢 / 戰爭 / 從蛋 / 從話語 / 不創而有
- 終末：審判 / 涅槃 / 回歸 / 永恆輪迴 / 末日 / 無終
- 救贖路徑：信 / 行 / 知 / 愛 / 苦 / 入定
- 倫理規範：黃金律 / 五戒 / 十誡 / 道德律 / 自然法
- 神聖體驗：合一 / 異象 / 啟示 / 入神 / 化身相見
- 死後：天堂地獄 / 輪迴 / 中陰 / 復活 / 投胎
- 性別：母權 / 父權 / 雙性同體
- 階級：種姓 / 平等 / 階序救贖
- 政教：神權 / 政教分離 / 政教合一
- 時間觀：線性 / 循環 / 永恆現在
- 物質觀：實在 / 幻 / 流變
- 心理：自我 / 無我 / 靈魂不滅
- 修煉：禪定 / 冥想 / 苦行 / 朝聖 / 祭祀

每部經文標 0-N 個語義標籤 + 1 條 LLM 寫的 100 字主旨。

### 3.2 索引設計

**Pagefind**: 全文索引（每部經文）。提供：搜尋詞 → 命中經文清單 + context snippet。

**Tag index**: JSON 文件 `00-overview/tag-index.json`，結構：
```json
{
  "創世": ["genesis", "rigveda-10-129", "popol-vuh", "enuma-elish", ...],
  "救贖": ["bible-john", "lotus-sutra", "bhagavad-gita", ...],
  ...
}
```

從每部 meta.json 的 `semantic_tags` 欄位反向構建。

### 3.3 何時做

- **現在**：擴 meta_template.json schema 加 genre / region / era / is_original_language / semantic_tags（空 array）
- **下載時**：填結構標籤（自動由 catalog 預填）
- **P4 翻譯做完後**：LLM 抽取語義標籤填 semantic_tags
- **網站完成前**：用 Pagefind + tag-index 雙索引

不需要等下載完才規劃 — schema 現在就定好，未來填料時不會反工。

---

## 4. m3 派工策略

當前流程：主 Claude 寫下載器 + catalog 後，m3 跑下載 + verify + commit。

派工 prompt 範本：
```
You are an executor for religions-history project.
Run: PYTHONIOENCODING=utf-8 python scripts/download-X.py --religion Y --all
Then run: python scripts/verify.py --all 2>&1 | grep -v PASS
If no FAIL: git add -A && git commit -m '<auto-msg>' && git push origin main
Report:
- batch name
- summary (ok / error / skipped count)
- any FAIL details
- commit hash
```

m3 不寫 catalog / 不寫 logic / 不改 schema — 那些主 Claude 做。
m3 不做判斷 — 只執行 + 回報 + verify 通過才 push。

---

## 5. 階段 B 任務清單（接下來執行）

| # | 任務 | 工具 | 派誰 | 預計 entry |
|---|------|------|------|-----------|
| 1 | 寫 download-sblgnt.py + SBLGNT NT 全 27 卷 | 自寫 + run | 主 | 27 |
| 2 | 擴 Wikisource 拉丁 Vulgate catalog + 跑 | catalog + run | 自跑 | 66 |
| 3 | 擴 GRETIL catalog 加 Sama/Yajur/Atharva Veda + 餘奧義書 | catalog + run | m3 | 30 |
| 4 | 寫耆那教 Jainism catalog（GRETIL + SBE Vol 22/45）+ 跑 | catalog + run | m3 | 30 |
| 5 | 寫巴哈伊 catalog（bahai-library raw）+ 跑 | 寫下載器 + catalog + m3 跑 | 主 + m3 | 15 |
| 6 | 寫 download-avesta.py + 跑 | 寫 + catalog + m3 跑 | 主 + m3 | 15 |
| 7 | 寫 download-suttacentral-deep.py SN samyutta 逐一 | 寫 + run | 主 + m3 | ~3000 entries |
| 8 | 寫 download-cbeta-full.py 大正藏全 vol crawl | 寫 + m3 跑 | 主 + m3 | ~2200 |
| 9 | 寫 download-sefaria-full.py 含塔木德全 | 寫 + m3 跑 | 主 + m3 | ~500 |

每完成一項：commit + push。
