# 跨宗教概念受控詞彙表

> 給 Pipeline C 標籤系統使用。每部經文的 `meta.json` 加 `semantic_tags: []` 欄位，從以下詞彙表中選詞。
> 設計原則：**避免單一宗教中心化**。詞彙先列「現象描述」，各宗教對該現象的特殊術語放在備註。
> 維護：新增詞前在 GitHub Issue 或對話中討論，避免膨脹失控。

---

## 14 大類

### 1. 終極實在 / 本體（Ultimate Reality）

| 標籤 | 描述 | 各宗教對應 |
|------|------|-----------|
| `ultimate-reality` | 終極存在 / 第一因 / 本源 | 道、Brahman、YHWH、Allāh、One（Plotinus）|
| `creator-deity` | 創造神 | YHWH、Allāh、Brahmā、Marduk |
| `non-dual` | 不二論 | Advaita、Madhyamaka、Cabbalah |
| `emptiness` | 空 / 無 | śūnyatā、apophatic theology |
| `divine-immanence` | 神在萬物中 | pantheism、panentheism、神道八百萬神 |
| `divine-transcendence` | 神超越世界 | Abrahamic 三教 |

### 2. 創世 / 宇宙論（Cosmogony）

| 標籤 | 描述 |
|------|------|
| `creation-ex-nihilo` | 無中生有 |
| `emanation` | 流溢說（Plotinus / Kabbalah） |
| `cyclic-cosmos` | 循環宇宙（印度 yuga、希臘四代論） |
| `dualistic-cosmos` | 二元宇宙（瑣羅亞斯德善惡神對抗） |
| `cosmic-egg` | 宇宙卵 / 渾沌 | 
| `chaos-to-order` | 渾沌到秩序 |

### 3. 人類起源 / 性論（Anthropology）

| 標籤 | 描述 |
|------|------|
| `created-in-image` | 人按神的形象造 |
| `human-as-microcosm` | 人是宇宙縮影 |
| `original-sin` | 原罪 / 墮落 |
| `essentially-good` | 性本善（孟子 / Pelagius） |
| `essentially-flawed` | 性本惡（荀子 / Augustine） |
| `tabula-rasa` | 性可塑（告子 / Locke） |
| `multiple-souls` | 多重靈魂（古埃及 ka/ba、道教三魂） |

### 4. 救贖 / 解脫（Soteriology）

| 標籤 | 描述 |
|------|------|
| `liberation-by-knowledge` | 智慧解脫（般若 / gnosis / jñāna） |
| `liberation-by-devotion` | 信仰 / 奉愛解脫（bhakti / faith） |
| `liberation-by-works` | 行為 / 戒律解脫（karma-yoga / Halakhah） |
| `grace-from-god` | 神恩拯救 |
| `salvation-by-faith` | 因信稱義 |
| `self-effort` | 自力（小乘佛教） |
| `other-power` | 他力（淨土宗） |

### 5. 倫理 / 戒律（Ethics）

| 標籤 | 描述 |
|------|------|
| `commandments-law` | 律法 / 十誡 / 五戒 |
| `golden-rule` | 己所不欲勿施於人（孔子 / Hillel / Jesus） |
| `non-violence` | 不殺生（ahimsā / 五戒） |
| `compassion` | 慈悲（karuṇā / agape / chesed） |
| `dietary-restrictions` | 飲食戒律 |
| `sexual-ethics` | 性倫理 |
| `economic-justice` | 經濟倫理 / 反高利貸 / 反剝削 |
| `truthfulness` | 不妄語 |
| `humility` | 謙卑 |
| `forgiveness` | 寬恕 |

### 6. 修行 / 工夫（Praxis）

| 標籤 | 描述 |
|------|------|
| `meditation` | 禪定 / dhyāna / contemplative prayer |
| `ritual-practice` | 儀式 |
| `chanting` | 誦經 / mantra / dhikr / 禮拜 |
| `asceticism` | 苦行 |
| `pilgrimage` | 朝聖 |
| `fasting` | 禁食 |
| `prayer` | 祈禱 |
| `breath-control` | 調息（prāṇāyāma / 內丹）|
| `study` | 學習 / 誦經 / Torah study |

### 7. 末世 / 死後（Eschatology）

| 標籤 | 描述 |
|------|------|
| `reincarnation` | 輪迴 |
| `heaven-hell` | 天堂地獄 |
| `bardo` | 中陰 / 過渡狀態 |
| `messianism` | 彌賽亞 / 救世主 |
| `apocalypse` | 末日大災 |
| `universal-resurrection` | 普世復活 |
| `extinction-of-self` | 滅度 / nirvāṇa |
| `ancestor-worship` | 祖先崇拜 |

### 8. 神聖體驗（Numinous Experience）

| 標籤 | 描述 |
|------|------|
| `theophany` | 神顯 |
| `mystical-union` | 與神合一 |
| `enlightenment` | 覺悟（bodhi / satori） |
| `prophetic-revelation` | 預言啟示 |
| `vision-experience` | 異象 / 觀想 |
| `spirit-possession` | 神靈附身 |
| `awe-fear` | 敬畏 / mysterium tremendum |

### 9. 社群 / 組織（Community）

| 標籤 | 描述 |
|------|------|
| `priesthood` | 祭司 / 僧團 / clergy |
| `monastic` | 修道 / 出家 |
| `lay-practitioner` | 在家修行 |
| `congregational` | 會眾 |
| `temple-centered` | 聖殿中心 |
| `synagogue-mosque-style` | 共讀 / 講經為核心 |
| `tribal-traditional` | 部落傳統 |

### 10. 政治 / 國家（Religion-State）

| 標籤 | 描述 |
|------|------|
| `theocracy` | 神權政治 |
| `caesaropapism` | 政教合一（拜占庭、伊斯蘭）|
| `secular-state` | 政教分離 |
| `divine-kingship` | 神聖王權（埃及、日本天皇） |
| `mandate-of-heaven` | 天命（中國） |
| `caste-system` | 種姓 / 階級制 |
| `prophetic-critique` | 先知批判政治 |

### 11. 性別 / 家庭（Gender）

| 標籤 | 描述 |
|------|------|
| `patriarchal` | 父權結構 |
| `goddess-tradition` | 女神傳統 |
| `celibate-tradition` | 守貞傳統 |
| `marriage-sacred` | 婚姻聖事 |
| `lineage-importance` | 宗族血脈 |
| `feminine-divine` | 女性神格 |

### 12. 與其他宗教關係（Inter-religious）

| 標籤 | 描述 |
|------|------|
| `monotheist-exclusive` | 排他一神 |
| `inclusive-monotheism` | 包容性一神（蘇菲、Bhakti）|
| `polytheist` | 多神 |
| `syncretic` | 融合主義 |
| `against-idolatry` | 反偶像 |
| `proselytizing` | 傳教導向 |
| `non-proselytizing` | 不傳教（猶太教 / 神道） |

### 13. 經典 / 啟示（Scripture）

| 標籤 | 描述 |
|------|------|
| `revealed-text` | 神啟經典（古蘭 / Torah） |
| `oral-tradition` | 口傳傳統 |
| `commentarial-layer` | 注疏體系（Mishnah / 三家詩） |
| `sacred-language` | 神聖語言（梵 / 古蘭阿拉伯 / Pali） |
| `vernacular-translation` | 鼓勵 vs 反對譯本 |
| `multiple-canons` | 多重經典體系 |

### 14. 苦 / 罪 / 障礙（Suffering）

| 標籤 | 描述 |
|------|------|
| `four-noble-truths` | 四聖諦 / 苦集滅道 |
| `sin-as-disobedience` | 罪 = 違命 |
| `karma-rebirth` | 業報輪迴 |
| `evil-as-deception` | 惡 = 迷惑（瑣羅亞斯德 / 諾斯底） |
| `theodicy` | 神義論（為何義人受苦） |
| `suffering-as-purifying` | 受苦使人純淨 |
| `accept-fate` | 安命（Stoic / 道家 / Sufi） |

---

## 使用方式

1. m3 讀 `01-translation.md` + `02-annotation.md`
2. 從上述詞彙表選**最相關 3-10 個**標籤，填回 `meta.json` 的 `semantic_tags` 欄
3. **不允許**自創標籤；發現必要的新概念 → 提 issue / 對話討論加入本表
4. 自動產生反向索引：`00-overview/tag-index.json`（每 tag 對應有哪些經文）

詳細 SOP 見 `tools/m3-tagger-role.md`（Pipeline C 啟動時撰寫）。
