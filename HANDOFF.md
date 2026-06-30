# HANDOFF — religions-history

> 狀態快照。每次工作結束更新。
> 規範見 `CLAUDE.md` + `PLAN.md` + `STRATEGY.md`。

## 當前進度 — ~510+ 部 / ~150 MB 原文

### 完成宗教覆蓋

| 宗教 | 部數 | 主要源 | 約大小 |
|------|------|--------|--------|
| 佛教 - 巴利 | 8 | SuttaCentral | 5 MB |
| 佛教 - 漢傳 | 48 (核心) + **165+ CBETA T01-T03+ 進行中** | CBETA TEI GitHub | 35+ MB |
| 佛教 - 梵文原典 | (與 Hindu 共用 GRETIL) | GRETIL | — |
| 道教 | 17 | ctext + Wikisource | 5 MB |
| 儒教 | 28 | ctext + Wikisource | 12 MB |
| 印度教 | 32 (Vedas 4 + Upanishads 11 + 史詩 + 哲學經 + Brahmana) | GRETIL Sanskrit + en.ws English | 12 MB |
| 猶太教 | 47 (Sefaria) + 10 (sacred-texts) = 57 | Sefaria + sacred-texts | 10 MB |
| 基督教 | 66 (和合本中譯) + 27 (SBLGNT 希臘) + 76 (Vulgate 拉丁) = 169 | en/zh/la Wikisource + SBLGNT GitHub | 16 MB |
| 伊斯蘭 | 1 (古蘭經 114 surah Uthmani) | Quran.com API | 1.4 MB |
| 瑣羅亞斯德 | 8 (Avesta + Pahlavi) | sacred-texts SBE | 6.4 MB |
| 耆那教 | 2 (SBE 22+45) | sacred-texts | 0.8 MB |
| 神道 | (defer, NDL 待) | — | — |
| 古埃及 | 2 (Book of Dead + Pyramid Texts) | sacred-texts | 0.5 MB |
| 古希臘羅馬 | 18+ (Homer/Hesiod/Ovid/Virgil/Plato/Plotinus etc) | sacred-texts + en.ws Butler | 5 MB |
| 北歐 | 3 (Heimskringla + Poetic Edda + Volsunga) | en.ws + sacred-texts | 2 MB |
| 凱爾特 | 6 (Mabinogion + Cuchulain + Carmina Gadelica + Welsh Triads) | sacred-texts + en.ws | 3 MB |
| 諾斯底 / 赫爾墨斯 | 5 (Mead) | sacred-texts | 4 MB |
| 美洲 | 6 (Chilam Balam + Aztec + Inca + Cherokee + Hopi + 等) | sacred-texts | 2 MB |
| 非洲 | 6 (Yoruba + Hausa + Dahomey + Rastafarian) | sacred-texts | 1 MB |
| 巴哈伊 | 1 (Splendour of God) | sacred-texts | 0.3 MB |
| 錫克教 | 1 (Sikh Religion Macauliffe) | en.wikisource | 0.8 MB |
| 現代新興 (摩門) | 2 (BoM 1830 + Pearl) | en.wikisource | 1.6 MB |
| 印度教英譯 | 1 (Mahabharata Ganguli 618 sections) | en.wikisource | 3.5 MB |

### Phase B 已完成
- 補齊基督教原文（希臘 SBLGNT 27 + 拉丁 Vulgate 76）
- 補齊印度教梵文（吠陀 / 奧義書 / 史詩 / 6 哲學經）
- 瑣羅亞斯德 SBE 8 部
- 耆那 + 古埃及 SBE
- 古希臘羅馬 + 北歐 + 凱爾特 + 諾斯底 + 美洲 + 非洲 + 巴哈伊

### Phase C 進行中
- ✅ CBETA T01 大正藏第 1 卷 98 經
- 🟡 CBETA T02-T04 by m3
- ⏳ Sefaria 全圖書館深爬
- ⏳ SuttaCentral 巴利全展開 (SN/AN/KN samyutta-by-samyutta)

### Phase D 規劃
- CBETA T05-T55 全大正藏 + 卍續藏
- Sefaria 巴比倫塔木德 37 tractate 全本
- Maimonides Mishneh Torah 14 卷
- 教父全集 (ANF + NPNF, 24+ 卷)

## 已實作下載器 (10 個)

| Script | 來源 | 對應 |
|--------|------|------|
| download-ctext.py | api.ctext.org | 道教/儒教漢系 |
| download-wikisource.py (--lang zh/ja/en/la/sa) | Wikisource Mediawiki API | 道教/儒教/基督教中譯/拉丁 Vulgate/世界古典英譯/神道日 |
| download-cbeta.py | raw.githubusercontent.com cbeta-org/xml-p5 | 漢譯佛經 catalog 式 |
| download-cbeta-full.py | 同上 + GitHub Contents API | 漢譯佛經全藏自動爬 |
| download-quran.py | api.quran.com | 古蘭經 |
| download-sefaria.py | sefaria.org/api | 猶太教 Tanakh/Talmud |
| download-suttacentral.py | suttacentral.net/api | 巴利三藏 |
| download-gretil.py | gretil.sub.uni-goettingen.de | 梵文印度教 + 佛教 |
| download-sblgnt.py | morphgnt/sblgnt GitHub | 希臘新約原文 |
| download-sacred-texts.py | sacred-texts.com | 13 catalogs (瑣羅/耆那/古埃/古希臘羅馬/北歐/凱/諾/曼/美洲/非洲/巴哈伊/猶太-輔/錫克-輔) |
| verify.py | local | SHA-256 + chapter count + size |

## 標記原文 vs 譯文

`meta.json` 加 `is_original_language` 欄位:
- true: 原文（巴利 / Sanskrit / Pali / Greek NT / Hebrew OT / Arabic Quran / Old Chinese / Tibetan etc）
- false: 譯文（和合本 / Mahabharata Ganguli / Iliad Butler / Avesta English / etc）

譯文僅作 cross-check 比對用，P4 AI 翻譯只能從原文翻。

## m3 派工狀態

當前 m3 跑：CBETA T02-T04 + 猶太教-輔助。
派工模式運作正常，每 batch 完成自動 commit + push.

## 下次接手

1. `python scripts/verify.py --all` 看狀態
2. 完成 CBETA T02-T04 後接 T08（般若部 + 心經系列）、T09-T10（法華+華嚴）、T11-T13（寶積+涅槃+大集）
3. T14-T17 經集部、T22-T24 律部、T25-T31 論部
4. T05-T07 大般若 600卷（巨型，獨立任務）
5. Phase D 啟動：sefaria-full / suttacentral-deep
6. 後續 P4 AI 翻譯

## 已知問題與解法

- ctext.org 配額限制 → 改用 GitHub mirror / Wikisource
- sacred-texts.com 需要 Mozilla Mac UA → 已 hardcoded
- Sefaria Guide for the Perplexed API 失敗 → 用 sacred-texts 替代
- SuttaCentral SN/AN/KN 深層遞迴 → 分 nipata 逐個下載
- GRETIL 路徑分新舊 (1_sanskr/* vs corpustei/*) → catalog 區分
- Windows console cp950 → 所有 Python 跑 `PYTHONIOENCODING=utf-8`
- 跨平台 SHA-256 一致 → .gitattributes 強制 LF EOL
