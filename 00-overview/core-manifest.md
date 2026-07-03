# 核心經文清單（core-manifest）

> 由 `scripts/audit-core.py` 自動產生。核心 = `meta.json` 的 `tier == 核心`。

- 核心總數：**384** 部
- 已翻譯：**77** / 384
- 已標籤：**376** / 384

## 各宗教核心進度

| 宗教 | 核心數 | 已譯 | 已標籤 |
|------|-------|------|-------|
| 基督教 | 159 | 19 | 159 |
| 佛教 | 61 | 18 | 61 |
| 猶太教 | 45 | 17 | 45 |
| 印度教 | 26 | 9 | 25 |
| 古希臘羅馬 | 17 | 0 | 12 |
| 道教 | 14 | 9 | 14 |
| 儒教 | 9 | 4 | 9 |
| 瑣羅亞斯德 | 8 | 0 | 8 |
| 古埃及 | 8 | 0 | 8 |
| 凱爾特 | 6 | 0 | 4 |
| 諾斯底 | 5 | 0 | 5 |
| 美洲 | 4 | 0 | 4 |
| 伊斯蘭 | 4 | 1 | 4 |
| 兩河 | 3 | 0 | 3 |
| 北歐 | 3 | 0 | 3 |
| 現代新興 | 2 | 0 | 2 |
| 錫克教 | 2 | 0 | 2 |
| 非洲 | 2 | 0 | 2 |
| 耆那教 | 2 | 0 | 2 |
| 斯拉夫 | 2 | 0 | 2 |
| 神道 | 1 | 0 | 1 |
| 巴哈伊 | 1 | 0 | 1 |

## 缺口分析

### A. 語料庫完全沒有（真內容缺口，需補抓 / 寫爬蟲）

> schema enum 有此宗教但語料庫一部都沒有。神道需另寫 NDL 爬蟲。
> 註：schema 把美洲細分為瑪雅/阿茲特克/印加、赫爾墨斯獨立，但語料庫用較粗的『美洲』『諾斯底』歸類，故此清單含分類折疊項，非全為真缺口。

- **赫爾墨斯**
- **瑪雅**
- **阿茲特克**
- **印加**

### B. 有經文但無核心標記（只需補標 tier，不需下載）

- （無）

## text_role 分類覆蓋

> `original`/`translation`/`transliteration`/`contested`；`(未標)` = 尚未判定，翻譯管線按 `language` 走安全預設（原文原樣保留 / 外語直譯），不臆測。

| text_role | 核心部數 |
|-----------|---------|
| original | 184 |
| translation | 197 |
| contested | 2 |
| (未標) | 1 |

### 疑似音譯 / 咒語，待人工確認 text_role

> 標題含 咒 / 陀羅尼 / 真言 / mantra 等且尚未標 text_role。音譯文本禁意譯，需人工確認後標 `text_role: transliteration`，翻譯管線才會原樣保留。

- （無）

## 唯一英譯本核心（政策已定，非待決缺口）

> 這些宗教的核心語料**目前只有英譯本、語料庫無原文**。政策：**先英→中翻譯**（`m3-translator-role.md` English 列，二手翻譯）讓它有中文可讀；**原文另列 `original-text-todo.md` 追蹤補抓**。此為已定政策，audit 不再視為不明缺口。

- 唯一英譯本宗教：**14** 個 / 核心 **46** 部
- 名單：古埃及、瑣羅亞斯德、諾斯底、美洲、兩河、凱爾特、北歐、非洲、斯拉夫、古希臘羅馬、耆那教、錫克教、神道、巴哈伊

### 內容檢查：原文已在庫但 text_role 標錯（改標，非缺口）

> `original.txt` 實測含 ≥15% 非拉丁原生文字，卻未標 `text_role=original`。改標即可，勿重複下載。詳見 `original-text-todo.md` 末段。

- `homeric-hymns-st` 荷馬諸頌 (33 篇)（古希臘羅馬，原生文字 44%）

## 各宗教核心明細

### 基督教（159 部）

- `bible-1-chronicles` 歷代志上（古典中文）譯– 標✓
- `bible-1-corinthians` 哥林多前書（古典中文）譯– 標✓
- `bible-1-john` 約翰一書（古典中文）譯– 標✓
- `bible-1-kings` 列王紀上（古典中文）譯– 標✓
- `bible-1-peter` 彼得前書（古典中文）譯– 標✓
- `bible-1-samuel` 撒母耳記上（古典中文）譯– 標✓
- `bible-1-thessalonians` 帖撒羅尼迦前書（古典中文）譯– 標✓
- `bible-1-timothy` 提摩太前書（古典中文）譯– 標✓
- `bible-2-chronicles` 歷代志下（古典中文）譯– 標✓
- `bible-2-corinthians` 哥林多後書（古典中文）譯– 標✓
- `bible-2-john` 約翰二書（古典中文）譯– 標✓
- `bible-2-kings` 列王紀下（古典中文）譯– 標✓
- `bible-2-peter` 彼得後書（古典中文）譯– 標✓
- `bible-2-samuel` 撒母耳記下（古典中文）譯– 標✓
- `bible-2-thessalonians` 帖撒羅尼迦後書（古典中文）譯– 標✓
- `bible-2-timothy` 提摩太後書（古典中文）譯– 標✓
- `bible-3-john` 約翰三書（古典中文）譯– 標✓
- `bible-acts` 使徒行傳（古典中文）譯– 標✓
- `bible-amos` 阿摩司書（古典中文）譯– 標✓
- `bible-colossians` 歌羅西書（古典中文）譯– 標✓
- `bible-daniel` 但以理書（古典中文）譯– 標✓
- `bible-deuteronomy` 申命記（古典中文）譯– 標✓
- `bible-ecclesiastes` 傳道書（古典中文）譯– 標✓
- `bible-ephesians` 以弗所書（古典中文）譯– 標✓
- `bible-esther` 以斯帖記（古典中文）譯– 標✓
- `bible-exodus` 出埃及記（古典中文）譯– 標✓
- `bible-ezekiel` 以西結書（古典中文）譯– 標✓
- `bible-ezra` 以斯拉記（古典中文）譯– 標✓
- `bible-galatians` 加拉太書（古典中文）譯– 標✓
- `bible-genesis` 創世記（古典中文）譯– 標✓
- `bible-habakkuk` 哈巴谷書（古典中文）譯– 標✓
- `bible-haggai` 哈該書（古典中文）譯– 標✓
- `bible-hebrews` 希伯來書（古典中文）譯– 標✓
- `bible-hosea` 何西阿書（古典中文）譯– 標✓
- `bible-isaiah` 以賽亞書（古典中文）譯– 標✓
- `bible-james` 雅各書（古典中文）譯– 標✓
- `bible-jeremiah` 耶利米書（古典中文）譯– 標✓
- `bible-job` 約伯記（古典中文）譯– 標✓
- `bible-joel` 約珥書（古典中文）譯– 標✓
- `bible-john` 約翰福音（古典中文）譯– 標✓
- `bible-jonah` 約拿書（古典中文）譯– 標✓
- `bible-joshua` 約書亞記（古典中文）譯– 標✓
- `bible-jude` 猶大書（古典中文）譯– 標✓
- `bible-judges` 士師記（古典中文）譯– 標✓
- `bible-lamentations` 耶利米哀歌（古典中文）譯– 標✓
- `bible-leviticus` 利未記（古典中文）譯– 標✓
- `bible-luke` 路加福音（古典中文）譯– 標✓
- `bible-malachi` 瑪拉基書（古典中文）譯– 標✓
- `bible-mark` 馬可福音（古典中文）譯– 標✓
- `bible-matthew` 馬太福音（古典中文）譯– 標✓
- `bible-micah` 彌迦書（古典中文）譯– 標✓
- `bible-nahum` 那鴻書（古典中文）譯– 標✓
- `bible-nehemiah` 尼希米記（古典中文）譯– 標✓
- `bible-numbers` 民數記（古典中文）譯– 標✓
- `bible-obadiah` 俄巴底亞書（古典中文）譯– 標✓
- `bible-philemon` 腓利門書（古典中文）譯– 標✓
- `bible-philippians` 腓立比書（古典中文）譯– 標✓
- `bible-proverbs` 箴言（古典中文）譯– 標✓
- `bible-psalms` 詩篇（古典中文）譯– 標✓
- `bible-revelation` 啟示錄（古典中文）譯– 標✓
- `bible-romans` 羅馬書（古典中文）譯– 標✓
- `bible-ruth` 路得記（古典中文）譯– 標✓
- `bible-song-of-songs` 雅歌（古典中文）譯– 標✓
- `bible-titus` 提多書（古典中文）譯– 標✓
- `bible-zechariah` 撒迦利亞書（古典中文）譯– 標✓
- `bible-zephaniah` 西番雅書（古典中文）譯– 標✓
- `sblgnt-1-corinthians` 哥林多前書（希臘原文）（Koine Greek）譯– 標✓
- `sblgnt-1-john` 約翰一書（希臘原文）（Koine Greek）譯✓ 標✓
- `sblgnt-1-peter` 彼得前書（希臘原文）（Koine Greek）譯✓ 標✓
- `sblgnt-1-thessalonians` 帖撒羅尼迦前書（希臘原文）（Koine Greek）譯✓ 標✓
- `sblgnt-1-timothy` 提摩太前書（希臘原文）（Koine Greek）譯✓ 標✓
- `sblgnt-2-corinthians` 哥林多後書（希臘原文）（Koine Greek）譯– 標✓
- `sblgnt-2-john` 約翰二書（希臘原文）（Koine Greek）譯✓ 標✓
- `sblgnt-2-peter` 彼得後書（希臘原文）（Koine Greek）譯✓ 標✓
- `sblgnt-2-thessalonians` 帖撒羅尼迦後書（希臘原文）（Koine Greek）譯✓ 標✓
- `sblgnt-2-timothy` 提摩太後書（希臘原文）（Koine Greek）譯✓ 標✓
- `sblgnt-3-john` 約翰三書（希臘原文）（Koine Greek）譯✓ 標✓
- `sblgnt-acts` 使徒行傳（希臘原文）（Koine Greek）譯– 標✓
- `sblgnt-colossians` 歌羅西書（希臘原文）（Koine Greek）譯✓ 標✓
- `sblgnt-ephesians` 以弗所書（希臘原文）（Koine Greek）譯✓ 標✓
- `sblgnt-galatians` 加拉太書（希臘原文）（Koine Greek）譯✓ 標✓
- `sblgnt-hebrews` 希伯來書（希臘原文）（Koine Greek）譯– 標✓
- `sblgnt-james` 雅各書（希臘原文）（Koine Greek）譯✓ 標✓
- `sblgnt-john` 約翰福音（希臘原文）（Koine Greek）譯✓ 標✓
- `sblgnt-jude` 猶大書（希臘原文）（Koine Greek）譯✓ 標✓
- `sblgnt-luke` 路加福音（希臘原文）（Koine Greek）譯– 標✓
- `sblgnt-mark` 馬可福音（希臘原文）（Koine Greek）譯– 標✓
- `sblgnt-matthew` 馬太福音（希臘原文）（Koine Greek）譯✓ 標✓
- `sblgnt-philemon` 腓利門書（希臘原文）（Koine Greek）譯✓ 標✓
- `sblgnt-philippians` 腓立比書（希臘原文）（Koine Greek）譯✓ 標✓
- `sblgnt-revelation` 啟示錄（希臘原文）（Koine Greek）譯– 標✓
- `sblgnt-romans` 羅馬書（希臘原文）（Koine Greek）譯– 標✓
- `sblgnt-titus` 提多書（希臘原文）（Koine Greek）譯✓ 標✓
- `vulgate-1-chronicles` 歷代志上（武加大）（Latin）譯– 標✓
- `vulgate-1-corinthians` 哥林多前書（武加大）（Latin）譯– 標✓
- `vulgate-1-john` 約翰一書（武加大）（Latin）譯– 標✓
- `vulgate-1-kings` 列王紀上 (武加大稱 列王紀三)（Latin）譯– 標✓
- `vulgate-1-peter` 彼得前書（武加大）（Latin）譯– 標✓
- `vulgate-1-samuel` 撒母耳記上 (武加大稱 列王紀一)（Latin）譯– 標✓
- `vulgate-1-thessalonians` 帖撒羅尼迦前書（武加大）（Latin）譯– 標✓
- `vulgate-1-timothy` 提摩太前書（武加大）（Latin）譯– 標✓
- `vulgate-2-chronicles` 歷代志下（武加大）（Latin）譯– 標✓
- `vulgate-2-corinthians` 哥林多後書（武加大）（Latin）譯– 標✓
- `vulgate-2-john` 約翰二書（武加大）（Latin）譯– 標✓
- `vulgate-2-kings` 列王紀下 (武加大稱 列王紀四)（Latin）譯– 標✓
- `vulgate-2-peter` 彼得後書（武加大）（Latin）譯– 標✓
- `vulgate-2-samuel` 撒母耳記下 (武加大稱 列王紀二)（Latin）譯– 標✓
- `vulgate-2-thessalonians` 帖撒羅尼迦後書（武加大）（Latin）譯– 標✓
- `vulgate-2-timothy` 提摩太後書（武加大）（Latin）譯– 標✓
- `vulgate-3-john` 約翰三書（武加大）（Latin）譯– 標✓
- `vulgate-acts` 使徒行傳（武加大）（Latin）譯– 標✓
- `vulgate-amos` 阿摩司書（武加大）（Latin）譯– 標✓
- `vulgate-colossians` 歌羅西書（武加大）（Latin）譯– 標✓
- `vulgate-daniel` 但以理書（武加大）（Latin）譯– 標✓
- `vulgate-deuteronomy` 申命記（武加大）（Latin）譯– 標✓
- `vulgate-ecclesiastes` 傳道書（武加大）（Latin）譯– 標✓
- `vulgate-ephesians` 以弗所書（武加大）（Latin）譯– 標✓
- `vulgate-esther` 以斯帖記（武加大）（Latin）譯– 標✓
- `vulgate-exodus` 出埃及記（武加大）（Latin）譯– 標✓
- `vulgate-ezekiel` 以西結書（武加大）（Latin）譯– 標✓
- `vulgate-ezra` 以斯拉記（武加大）（Latin）譯– 標✓
- `vulgate-galatians` 加拉太書（武加大）（Latin）譯– 標✓
- `vulgate-genesis` 創世記（武加大）（Latin）譯– 標✓
- `vulgate-habakkuk` 哈巴谷書（武加大）（Latin）譯– 標✓
- `vulgate-haggai` 哈該書（武加大）（Latin）譯– 標✓
- `vulgate-hebrews` 希伯來書（武加大）（Latin）譯– 標✓
- `vulgate-hosea` 何西阿書（武加大）（Latin）譯– 標✓
- `vulgate-isaiah` 以賽亞書（武加大）（Latin）譯– 標✓
- `vulgate-james` 雅各書（武加大）（Latin）譯– 標✓
- `vulgate-jeremiah` 耶利米書（武加大）（Latin）譯– 標✓
- `vulgate-job` 約伯記（武加大）（Latin）譯– 標✓
- `vulgate-joel` 約珥書（武加大）（Latin）譯– 標✓
- `vulgate-john` 約翰福音（武加大）（Latin）譯– 標✓
- `vulgate-jonah` 約拿書（武加大）（Latin）譯– 標✓
- `vulgate-joshua` 約書亞記（武加大）（Latin）譯– 標✓
- `vulgate-jude` 猶大書（武加大）（Latin）譯– 標✓
- `vulgate-judges` 士師記（武加大）（Latin）譯– 標✓
- `vulgate-lamentations` 耶利米哀歌（武加大）（Latin）譯– 標✓
- `vulgate-leviticus` 利未記（武加大）（Latin）譯– 標✓
- `vulgate-luke` 路加福音（武加大）（Latin）譯– 標✓
- `vulgate-malachi` 瑪拉基書（武加大）（Latin）譯– 標✓
- `vulgate-mark` 馬可福音（武加大）（Latin）譯– 標✓
- `vulgate-matthew` 馬太福音（武加大）（Latin）譯– 標✓
- `vulgate-micah` 彌迦書（武加大）（Latin）譯– 標✓
- `vulgate-nahum` 那鴻書（武加大）（Latin）譯– 標✓
- `vulgate-nehemiah` 尼希米記（武加大稱 2 Esdras）（Latin）譯– 標✓
- `vulgate-numbers` 民數記（武加大）（Latin）譯– 標✓
- `vulgate-obadiah` 俄巴底亞書（武加大）（Latin）譯– 標✓
- `vulgate-philemon` 腓利門書（武加大）（Latin）譯– 標✓
- `vulgate-philippians` 腓立比書（武加大）（Latin）譯– 標✓
- `vulgate-proverbs` 箴言（武加大）（Latin）譯– 標✓
- `vulgate-psalms` 詩篇（武加大）（Latin）譯– 標✓
- `vulgate-revelation` 啟示錄（武加大）（Latin）譯– 標✓
- `vulgate-romans` 羅馬書（武加大）（Latin）譯– 標✓
- `vulgate-ruth` 路得記（武加大）（Latin）譯– 標✓
- `vulgate-song-of-songs` 雅歌（武加大）（Latin）譯– 標✓
- `vulgate-titus` 提多書（武加大）（Latin）譯– 標✓
- `vulgate-zechariah` 撒迦利亞書（武加大）（Latin）譯– 標✓
- `vulgate-zephaniah` 西番雅書（武加大）（Latin）譯– 標✓

### 佛教（61 部）

- `abhidharmakosa` 阿毘達磨俱舍論（古典漢語）譯– 標✓
- `amitabha-sutra` 佛說阿彌陀經（古典漢語）譯✓ 標✓
- `an1-ones` AN1 一法集 (~575 經)（Pali）譯– 標✓
- `an10-tens` AN10 十法集（Pali）譯– 標✓
- `an11-elevens` AN11 十一法集（Pali）譯– 標✓
- `an2-twos` AN2 二法集（Pali）譯– 標✓
- `an3-threes` AN3 三法集（Pali）譯– 標✓
- `an4-fours` AN4 四法集（Pali）譯– 標✓
- `an5-fives` AN5 五法集（Pali）譯– 標✓
- `an6-sixes` AN6 六法集（Pali）譯– 標✓
- `an7-sevens` AN7 七法集（Pali）譯– 標✓
- `an8-eights` AN8 八法集（Pali）譯– 標✓
- `an9-nines` AN9 九法集（Pali）譯– 標✓
- `avatamsaka-sutra` 大方廣佛華嚴經（八十華嚴）（古典漢語）譯– 標✓
- `awakening-of-faith` 大乘起信論（古典漢語）譯✓ 標✓
- `contemplation-sutra` 佛說觀無量壽佛經（古典漢語）譯✓ 標✓
- `dhammapada` 法句經（Pali）譯✓ 標✓
- `diamond-mulamadhyamaka` 中論（古典漢語）譯– 標✓
- `diamond-sutra-kumarajiva` 金剛般若波羅蜜經（古典漢語）譯✓ 標✓
- `digha-nikaya` 長部經典（Pali）譯– 標✓
- `dirghagama` 長阿含經（古典漢語）譯– 標✓
- `ekottarikagama` 增一阿含經（古典漢語）譯– 標✓
- `fortytwo-chapters-sutra` 四十二章經（古典漢語）譯✓ 標✓
- `heart-sutra-kumarajiva` 摩訶般若波羅蜜大明咒經（古典漢語）譯✓ 標✓
- `heart-sutra-xuanzang` 般若波羅蜜多心經（古典漢語）譯✓ 標✓
- `infinite-life-sutra` 佛說無量壽經（古典漢語）譯– 標✓
- `kn-jataka` 小部·本生 (547 故事)（Pali）譯– 標✓
- `kn-milindapanha` 小部·彌蘭王問經（Pali）譯– 標✓
- `ksitigarbha-sutra` 地藏菩薩本願經（古典漢語）譯– 標✓
- `lotus-sutra` 妙法蓮華經（古典漢語）譯✓ 標✓
- `madhyamagama` 中阿含經（古典漢語）譯– 標✓
- `mahaparinirvana-sutra-northern` 大般涅槃經（北本）（古典漢語）譯– 標✓
- `mahaprajnaparamita-shastra` 大智度論（古典漢語）譯– 標✓
- `mahayanasamgraha` 攝大乘論（古典漢語）譯– 標✓
- `majjhima-nikaya` 中部經典（Pali）譯– 標✓
- `medicine-buddha-sutra` 藥師琉璃光如來本願功德經（古典漢語）譯✓ 標✓
- `perfect-enlightenment-sutra` 大方廣圓覺修多羅了義經（古典漢語）譯– 標✓
- `samyuktagama` 雜阿含經（古典漢語）譯– 標✓
- `shurangama-sutra` 大佛頂如來密因修證了義諸菩薩萬行首楞嚴經（古典漢語）譯– 標✓
- `sn1-devata` SN1 天人相應 (81 經)（Pali）譯– 標✓
- `sn10-yakkha` SN10 夜叉相應（Pali）譯✓ 標✓
- `sn11-sakka` SN11 帝釋相應（Pali）譯✓ 標✓
- `sn12-nidana` SN12 因緣相應 (93 經)（Pali）譯– 標✓
- `sn2-devaputta` SN2 天子相應（Pali）譯✓ 標✓
- `sn22-khandha` SN22 蘊相應 (159 經)（Pali）譯– 標✓
- `sn3-kosala` SN3 拘薩羅相應（Pali）譯– 標✓
- `sn35-salayatana` SN35 六入相應 (248 經)（Pali）譯– 標✓
- `sn4-mara` SN4 魔羅相應（Pali）譯✓ 標✓
- `sn45-magga` SN45 道相應 (180 經)（Pali）譯– 標✓
- `sn46-bojjhanga` SN46 覺支相應 (184 經)（Pali）譯– 標✓
- `sn47-satipatthana` SN47 念處相應 (104 經)（Pali）譯– 標✓
- `sn5-bhikkhuni` SN5 比丘尼相應（Pali）譯✓ 標✓
- `sn56-sacca` SN56 諦相應 (131 經)（Pali）譯– 標✓
- `sn6-brahma` SN6 梵天相應（Pali）譯✓ 標✓
- `sn7-brahmana` SN7 婆羅門相應（Pali）譯– 標✓
- `sn8-vangisa` SN8 婆耆舍相應（Pali）譯✓ 標✓
- `sn9-vana` SN9 林相應（Pali）譯✓ 標✓
- `sutta-nipata` 經集（Pali）譯– 標✓
- `vijnaptimatratasiddhi` 成唯識論（古典漢語）譯– 標✓
- `vimalakirti-sutra` 維摩詰所說經（古典漢語）譯– 標✓
- `yogacarabhumi` 瑜伽師地論（古典漢語）譯– 標✓

### 猶太教（45 部）

- `amos` 阿摩司書（希伯來）譯✓ 標✓
- `chronicles-1` 歷代志上（希伯來）譯– 標✓
- `chronicles-2` 歷代志下（希伯來）譯– 標✓
- `daniel` 但以理書（希伯來）譯– 標✓
- `deuteronomy` 申命記（希伯來）譯– 標✓
- `ecclesiastes` 傳道書（希伯來）譯✓ 標✓
- `esther` 以斯帖記（希伯來）譯– 標✓
- `exodus` 出埃及記（希伯來）譯– 標✓
- `ezekiel` 以西結書（希伯來）譯– 標✓
- `ezra` 以斯拉記（希伯來）譯– 標✓
- `genesis` 創世記（希伯來）譯✓ 標✓
- `guide-for-the-perplexed-st` 迷途指津 (Maimonides)（English (translation)）譯– 標✓
- `habakkuk` 哈巴谷書（希伯來）譯✓ 標✓
- `haggai` 哈該書（希伯來）譯✓ 標✓
- `hosea` 何西阿書（希伯來）譯– 標✓
- `isaiah` 以賽亞書（希伯來）譯– 標✓
- `jeremiah` 耶利米書（希伯來）譯– 標✓
- `job` 約伯記（希伯來）譯✓ 標✓
- `joel` 約珥書（希伯來）譯✓ 標✓
- `jonah` 約拿書（希伯來）譯✓ 標✓
- `josephus-works` 約瑟夫斯著作（English (translation)）譯– 標✓
- `joshua` 約書亞記（希伯來）譯– 標✓
- `judges` 士師記（希伯來）譯– 標✓
- `kabbalah-unveiled` 卡巴拉揭示 (Mathers)（English (translation)）譯– 標✓
- `kings-1` 列王紀上（希伯來）譯– 標✓
- `kings-2` 列王紀下（希伯來）譯– 標✓
- `kitab-al-khazari` 庫薩里 (Judah Halevi)（English (translation)）譯– 標✓
- `lamentations` 耶利米哀歌（希伯來）譯✓ 標✓
- `legends-of-the-jews` 猶太人的傳說 (Ginzberg)（English (translation)）譯– 標✓
- `leviticus` 利未記（希伯來）譯– 標✓
- `malachi` 瑪拉基書（希伯來）譯✓ 標✓
- `micah` 彌迦書（希伯來）譯✓ 標✓
- `nahum` 那鴻書（希伯來）譯✓ 標✓
- `nehemiah` 尼希米記（希伯來）譯– 標✓
- `numbers` 民數記（希伯來）譯– 標✓
- `obadiah` 俄巴底亞書（希伯來）譯✓ 標✓
- `proverbs` 箴言（希伯來）譯✓ 標✓
- `psalms` 詩篇（希伯來）譯– 標✓
- `ruth` 路得記（希伯來）譯✓ 標✓
- `samuel-1` 撒母耳記上（希伯來）譯– 標✓
- `samuel-2` 撒母耳記下（希伯來）譯– 標✓
- `song-of-songs` 雅歌（希伯來）譯✓ 標✓
- `talmud-rodkinson` 塔木德 (Rodkinson 選譯)（English (translation)）譯– 標✓
- `zechariah` 撒迦利亞書（希伯來）譯– 標✓
- `zephaniah` 西番雅書（希伯來）譯✓ 標✓

### 印度教（26 部）

- `aitareya-upanishad` 愛多列雅奧義書（含注）（Sanskrit）譯– 標✓
- `atharvaveda-saunaka` 阿闥婆吠陀（Śaunaka）（Sanskrit）譯– 標✓
- `bhagavad-gita` 薄伽梵歌（Sanskrit）譯✓ 標–
- `bhagavata-purana` 薄伽梵往世書（Sanskrit）譯– 標✓
- `brahma-sutra` 梵經（Sanskrit）譯✓ 標✓
- `brihadaranyaka-upanishad` 大林間奧義書（Sanskrit）譯✓ 標✓
- `chandogya-upanishad` 唱讚奧義書（含注）（Sanskrit）譯– 標✓
- `isha-upanishad` 伊舍奧義書（Sanskrit）譯✓ 標✓
- `katha-upanishad` 迦塔奧義書（Sanskrit）譯✓ 標✓
- `mahabharata-ganguli` 摩訶婆羅多（Ganguli 英譯）（English (translation from Greek/Latin/Old Norse/etc)）譯– 標✓
- `maitrayani-samhita` 梅特拉雅尼本集（黑耶柔吠陀）（Sanskrit）譯– 標✓
- `mandukya-upanishad` 蛙氏奧義書（Sanskrit）譯– 標✓
- `manu-smrti` 摩奴法典（Sanskrit）譯– 標✓
- `mimamsa-sutra-jaimini` 彌曼差經（闍彌尼）（Sanskrit）譯– 標✓
- `nyaya-sutra-gautama` 正理經（喬達摩）（Sanskrit）譯– 標✓
- `prashna-upanishad` 問難奧義書（Sanskrit）譯– 標✓
- `rigveda` 梨俱吠陀（Sanskrit）譯– 標✓
- `samaveda` 沙摩吠陀（Sanskrit）譯– 標✓
- `samkhya-karika-ishvarakrshna` 數論頌（自在黑）（Sanskrit）譯✓ 標✓
- `samkhya-sutra-kapila` 數論經（迦毗羅）（Sanskrit）譯– 標✓
- `shatapatha-brahmana-1` 百道梵書（Sanskrit）譯– 標✓
- `shvetashvatara-upanishad` 白騾奧義書（Sanskrit）譯✓ 標✓
- `taittiriya-upanishad` 鷓鴣氏奧義書（含商羯羅注）（Sanskrit）譯– 標✓
- `vaisheshika-sutra-kanada` 勝論經（迦那陀）（Sanskrit）譯✓ 標✓
- `valmiki-ramayana` 羅摩衍那（Valmiki, critical）（Sanskrit）譯– 標✓
- `yoga-sutra` 瑜伽經（Sanskrit）譯✓ 標✓

### 古希臘羅馬（17 部）

- `hesiod-works` 赫西俄德 (神譜 + 工作與時日)（English (translation)）譯– 標✓
- `homer-greek` 伊利亞德 + 奧德賽 (希臘原文)（希臘）譯– 標✓
- `homer-iliad-pope` 伊利亞德 (Pope/Bryant 英譯)（English (translation)）譯– 標✓
- `homer-odyssey-st` 奧德賽 (Pope/Bryant 英譯)（English (translation)）譯– 標✓
- `homeric-hymns-st` 荷馬諸頌 (33 篇)（English (translation)）譯– 標✓
- `iliad-butler` 伊利亞德（Butler 譯）（English (translation from Greek/Latin/Old Norse/etc)）譯– 標✓
- `odyssey-butler` 奧德賽（Butler 譯）（English (translation from Greek/Latin/Old Norse/etc)）譯– 標✓
- `ovid-metamorphoses` 變形記 (奧維德)（English (translation)）譯– 標✓
- `ovid-metamorphoses-la` 變形記（拉丁原文）（拉丁）譯– 標–
- `plato-phaedo-el` 斐多篇（希臘原文）（希臘）譯– 標–
- `plato-republic-el` 理想國（希臘原文）（希臘）譯– 標–
- `plato-symposium-el` 會飲篇（希臘原文）（希臘）譯– 標–
- `plato-works` 柏拉圖對話集 (sacred-texts 選)（English (translation)）譯– 標✓
- `plotinus-enneads` 普羅提諾九章集（English (translation)）譯– 標✓
- `sibylline-oracles` 西比拉神諭集（English (translation)）譯– 標✓
- `virgil-aeneid` 伊尼德 (維吉爾)（English (translation)）譯– 標✓
- `virgil-aeneid-la` 伊尼德（拉丁原文）（拉丁）譯– 標–

### 道教（14 部）

- `baopuzi` 抱朴子（內外篇）（古典漢語）譯– 標✓
- `huainanzi` 淮南子（古典漢語）譯– 標✓
- `huangdi-neijing` 黃帝內經（古典漢語）譯– 標✓
- `huangting-neijing` 黃庭內景經（古典漢語）譯✓ 標✓
- `huangting-waijing` 黃庭外景經（古典漢語）譯✓ 標✓
- `liezi` 列子（古典漢語）譯✓ 標✓
- `qingjing-jing` 太上老君說常清靜經（古典漢語）譯✓ 標✓
- `taiping-jing` 太平經（古典漢語）譯– 標✓
- `taishang-ganying-pian` 太上感應篇（古典漢語）譯✓ 標✓
- `tao-te-ching` 道德經（古典漢語）譯✓ 標✓
- `wenzi` 文子（古典漢語）譯– 標✓
- `yinfu-jing` 黃帝陰符經（古典漢語）譯✓ 標✓
- `zhouyi-cantong-qi` 周易參同契（古典漢語）譯✓ 標✓
- `zhuangzi` 莊子（古典漢語）譯✓ 標✓

### 儒教（9 部）

- `analects` 論語（古典漢語）譯✓ 標✓
- `book-of-changes` 周易（古典漢語）譯– 標✓
- `book-of-poetry` 詩經（古典漢語）譯– 標✓
- `chun-qiu-zuo-zhuan` 春秋左傳（古典漢語）譯– 標✓
- `doctrine-of-the-mean` 中庸（古典漢語）譯✓ 標✓
- `great-learning` 大學（古典漢語）譯✓ 標✓
- `liji` 禮記（古典漢語）譯– 標✓
- `mengzi` 孟子（古典漢語）譯✓ 標✓
- `shang-shu` 尚書（古典漢語）譯– 標✓

### 瑣羅亞斯德（8 部）

- `avesta-sbe04` 阿維斯塔 SBE 04 (Vendidad)（English (19c. translation)）譯– 標✓
- `avesta-sbe23` 阿維斯塔 SBE 23 (Yasht)（English (19c. translation)）譯– 標✓
- `avesta-sbe31` 阿維斯塔 SBE 31 (Yasna + Visperad + Khordah)（English (19c. translation)）譯– 標✓
- `bundahishn` Bundahishn + Bahman Yasht + Shayast la-Shayast（English (19c. translation)）譯– 標✓
- `dadestan-i-denig` Dadestan-i Denig (宗教裁判)（English (19c. translation)）譯– 標✓
- `denkard-3-bahman-yasht` Pahlavi Texts Part III（English (19c. translation)）譯– 標✓
- `denkard-bk-5` Pahlavi Texts Part V (Contents of the Nasks)（English (19c. translation)）譯– 標✓
- `denkard-bk-7-8` Dinkard Books 8-9（English (19c. translation)）譯– 標✓

### 古埃及（8 部）

- `book-of-am-tuat` 阿姆杜阿特之書（幽冥界之書）（English (Budge translation)）譯– 標✓
- `book-of-gates` 門之書（English (Budge translation)）譯– 標✓
- `burden-of-isis` 伊西斯的悲歌（奧西里斯讚歌）（English (Budge translation)）譯– 標✓
- `egyptian-book-of-dead` 古埃及死者之書（English (Budge translation)）譯– 標✓
- `egyptian-heaven-and-hell` 埃及的天堂與地獄（English (Budge translation)）譯– 標✓
- `legends-of-the-gods-egypt` 諸神傳說（古埃及文本）（English (Budge translation)）譯– 標✓
- `liturgy-funerary-offerings` 葬祭供養儀軌（English (Budge translation)）譯– 標✓
- `pyramid-texts-mercer` 金字塔銘文（English (Budge translation)）譯– 標✓

### 凱爾特（6 部）

- `carmina-gadelica-1` Carmina Gadelica Vol 1（English (translation)）譯– 標✓
- `carmina-gadelica-2` Carmina Gadelica Vol 2（English (translation)）譯– 標✓
- `cuchulain-muirthemne` Cuchulain of Muirthemne (Ulster Cycle)（English (translation)）譯– 標✓
- `mabinogion-cy-1` 馬比諾吉昂 第一卷（威爾斯原文）（威爾斯）譯– 標–
- `mabinogion-cy-2` 馬比諾吉昂 第二卷（威爾斯原文）（威爾斯）譯– 標–
- `mabinogion-st` Mabinogion 馬比諾吉昂 (Welsh)（English (translation)）譯– 標✓

### 諾斯底（5 部）

- `fragments-of-faith-forgotten` 被遺忘信仰的碎片 (Mead)（English (G.R.S. Mead and other 19c. translations)）譯– 標✓
- `gnostics-and-their-remains` 諾斯底與其遺存 (King)（English (G.R.S. Mead and other 19c. translations)）譯– 標✓
- `thrice-greatest-hermes-1` 三度偉大的赫爾墨斯 Vol 1 (Mead)（English (G.R.S. Mead and other 19c. translations)）譯– 標✓
- `thrice-greatest-hermes-2` 三度偉大的赫爾墨斯 Vol 2 (Hermetica)（English (G.R.S. Mead and other 19c. translations)）譯– 標✓
- `thrice-greatest-hermes-3` 三度偉大的赫爾墨斯 Vol 3（English (G.R.S. Mead and other 19c. translations)）譯– 標✓

### 美洲（4 部）

- `aztec-rva` 阿茲特克儀禮（English (translation)）譯– 標✓
- `chilam-balam` 契倫·巴蘭之書 (Chumayel)（English (translation)）譯– 標✓
- `inca-rites` 印加儀禮與法律（English (translation)）譯– 標✓
- `yucatan-before-after-conquest` 尤卡坦征服前後 (Landa)（English (translation)）譯– 標✓

### 伊斯蘭（4 部）

- `masnavi-rumi-st` 瑪斯納維 (Rumi 蘇菲詩)（English (translation)）譯– 標✓
- `mishkat-al-anwar` Mishkat al-Anwar 光明壁龕 (Ghazali)（English (translation)）譯– 標✓
- `quran` 古蘭經（古典阿拉伯）譯✓ 標✓
- `quran-pickthall` 古蘭經 (Pickthall 英譯)（English (translation)）譯– 標✓

### 兩河（3 部）

- `code-of-hammurabi-st` 漢摩拉比法典（English (translation)）譯– 標✓
- `enuma-elish-stc` 創世七碑（埃努瑪·埃利什）（English (translation)）譯– 標✓
- `epic-of-gilgamesh-st` 吉爾伽美什史詩（English (translation)）譯– 標✓

### 北歐（3 部）

- `heimskringla` 赫姆斯克林格拉（English (translation from Greek/Latin/Old Norse/etc)）譯– 標✓
- `poetic-edda-bellows` 詩體埃達 (Bellows 譯)（English (translation)）譯– 標✓
- `volsunga-saga` 沃爾松傳奇（English (translation)）譯– 標✓

### 現代新興（2 部）

- `book-of-mormon-1830` 摩門經（1830 初版）（English (原典)）譯– 標✓
- `pearl-of-great-price` 無價珍珠（English (原典)）譯– 標✓

### 錫克教（2 部）

- `guru-granth-sahib-st` 錫克教根本經 Shri Guru Granth Sahib（English (translation, parts romanized Punjabi)）譯– 標✓
- `sikh-religion-macauliffe` 錫克教（Macauliffe）（English (translation from Greek/Latin/Old Norse/etc)）譯– 標✓

### 非洲（2 部）

- `ife-mythology` 伊費神話 (約魯巴)（English (translation)）譯– 標✓
- `yoruba-religion` 約魯巴宗教與神話（English (translation)）譯– 標✓

### 耆那教（2 部）

- `jain-sbe22` 耆那經典 SBE 22 (Acaranga + Kalpa)（English (Jacobi 19c translation)）譯– 標✓
- `jain-sbe45` 耆那經典 SBE 45 (Uttaradhyayana + Sutrakritanga)（English (Jacobi 19c translation)）譯– 標✓

### 斯拉夫（2 部）

- `songs-of-russian-people` 俄羅斯人民之歌（English (translation)）譯– 標✓
- `tale-of-igor-campaign` 伊戈爾遠征記（English (translation)）譯– 標✓

### 神道（1 部）

- `kojiki-chamberlain` 古事記（English (translation)）譯– 標✓

### 巴哈伊（1 部）

- `splendour-of-god` 上帝的光輝 (巴哈歐拉著作節錄)（English (translation)）譯– 標✓

