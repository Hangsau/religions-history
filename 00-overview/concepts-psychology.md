# 人問領域受控詞彙表（心理學讀經軸）

> 給心理學讀經層使用，與 [`concepts.md`](./concepts.md) **正交並存**。
>
> **兩張表的差別（關鍵）**：
> - `concepts.md`（14 大類）＝**教義內容軸**：這部經「講什麼道理」（終極實在 / 救贖論 / 末世觀…）。給比較宗教學、給學者精確標。
> - 本表（13 領域）＝**人的問題軸**：這部經「回應哪個人生提問」（我為何在此 / 怎麼面對死 / 什麼是愛…）。給一般人從自己的處境入口找經文。
> - 一部經**兩軸都可標**。例：《薄伽梵歌》教義軸標 `liberation-by-devotion`＋`karma-rebirth`；人問軸標 `calling-vocation`＋`freewill-fate-choice`＋`existence-why-born`。
>
> **方法來源**：不是理論預設，而是由下而上——先造 500 題「人實際會問的問題」（`11-psychology/human-questions-corpus.md`），讓分類自己浮現、收斂成 13 領域（`11-psychology/question-themes.md`，已用極端人格 100 題壓力測試、零新增大類）。真實問答經典對照見 `11-psychology/reference-analects.md`。
>
> **存哪個欄位**：新增 `meta.json` 欄位 `psych_tags: []`（**不併進 `semantic_tags`**，避免兩軸混淆）。目前只使用下列表格正式定義的 48 個細群／跨界支流標籤；領域層代碼尚未定義，不可自行創造。維護紀律同 `concepts.md`：新增詞先討論，勿膨脹。

---

## 13 領域（← 45 細群）＋ 3 跨界支流

### I. 存在與意義（Existence & Meaning）

| 標籤 | 描述 | 代表題／對應經典 |
|------|------|-----------------|
| `existence-why-born` | 我為何在此、沒答應被生下卻得活著 | Q1；傳道書 |
| `nihilism-void` | 一切是不是空、真與假、意義是否存在 | 傳道書；般若類 |
| `living-with-unknown` | 與想不通、沒有答案的問題共處 | Q389；約伯記 |
| `insignificance-history` | 在歷史洪流／宇宙尺度中的渺小 | 詩篇；莊子 |

### II. 自我與認同（Self & Identity）

| 標籤 | 描述 | 代表題／對應經典 |
|------|------|-----------------|
| `who-am-i` | 我到底是誰、真我是什麼 | Q17；大林間奧義書、唱讚奧義書 |
| `gender-body` | 身體與性別、與身體的關係 | 雅歌 |
| `boundaries-self-worth` | 界線、我值不值得、自我價值 | Q244 |
| `perfectionism-self-criticism` | 完美主義、自我批判、覺得自己不夠好 | Q244 |
| `dreams-unconscious` | 夢、潛意識、內在未知的聲音 | 創世記約瑟解夢 |
| `childhood-wounds` | 童年如何形塑我、早年的傷 | Q50 |

### III. 愛與親密（Love & Intimacy）

| 標籤 | 描述 | 代表題／對應經典 |
|------|------|-----------------|
| `love-sex-intimacy` | 愛與性、什麼是愛、怎麼知道這是愛 | Q25；會飲篇、雅歌 |
| `trust-vulnerability` | 信任、脆弱、敢不敢被看見 | — |
| `communication-being-understood` | 溝通、渴望被理解卻沒人真懂 | Q301 |

### IV. 家庭與傳承（Family & Legacy）

| 標籤 | 描述 | 代表題／對應經典 |
|------|------|-----------------|
| `marriage-family` | 婚姻與家庭、原生家庭的愛恨 | Q40；論語（問孝） |
| `parenthood` | 為人父母、怕把傷傳給孩子 | Q50 |
| `memory-reconciliation` | 記憶、和解、留下什麼給後代 | — |

### V. 群體·社會·公義（Community, Society & Justice）

| 標籤 | 描述 | 代表題／對應經典 |
|------|------|-----------------|
| `loneliness-belonging` | 孤獨與歸屬、友誼 | Q155 |
| `ingroup-outgroup-prejudice` | 我群他群、偏見 | — |
| `justice-power` | 公義、權力、世界為何不公 | Q113；理想國、孟子 |
| `responsibility-leadership` | 責任與領導、被賦予的擔子 | 論語（問政） |

### VI. 情緒與內在生活（Emotion & Inner Life）

| 標籤 | 描述 | 代表題／對應經典 |
|------|------|-----------------|
| `emotions-passions` | 七情六慾、怒／喜／哀如何生滅 | Q63；中部經典 |
| `fear-uncertainty` | 恐懼、焦慮、怕的其實是背後更深的東西 | Q125 |
| `addiction-self-destruction` | 癮、明知不好卻停不下來、自我破壞 | Q165 |
| `body-mind` | 情緒如何住在身體裡、身心關係 | — |

### VII. 善惡·良心·品格（Good, Evil, Conscience & Character）

| 標籤 | 描述 | 代表題／對應經典 |
|------|------|-----------------|
| `guilt-atonement` | 罪咎、贖罪、能否原諒自己 | Q145 |
| `evil-cruelty-empathy` | 惡、殘忍、同理，人為何對人這麼殘忍 | Q358 |
| `honesty-hypocrisy` | 誠實與虛偽、表裡不一 | 論語（問恥） |
| `courage` | 勇氣、面對該面對的 | — |

### VIII. 工作·成就·召喚（Work, Achievement & Calling）

| 標籤 | 描述 | 代表題／對應經典 |
|------|------|-----------------|
| `work-money` | 工作與金錢、賺多少才算夠 | Q52 |
| `calling-vocation` | 天賦、使命、這輩子為何而來 | Q367；薄伽梵歌 |

### IX. 苦難·疾病·身體（Suffering, Illness & Body）

| 標籤 | 描述 | 代表題／對應經典 |
|------|------|-----------------|
| `illness-body` | 疾病與身體、照顧與被照顧 | Q75 |
| `meaning-of-suffering` | 受苦的意義、神義論、壞事為何降在好人 | Q93；約伯記、中部經典（四聖諦） |

### X. 無常·老·死·失去（Impermanence, Aging, Death & Loss）

| 標籤 | 描述 | 代表題／對應經典 |
|------|------|-----------------|
| `aging-time` | 老與時間、身體與容顏的流逝 | 傳道書 |
| `loss-grief` | 失去、哀傷、最愛的人走了那個洞 | Q89 |
| `death` | 死亡、人死後去哪裡 | Q94；迦塔奧義書、斐多篇、長部（大般涅槃） |
| `patience-waiting` | 耐心、等待、熬過去 | — |

### XI. 自由·命運·改變（Freedom, Fate & Change）

| 標籤 | 描述 | 代表題／對應經典 |
|------|------|-----------------|
| `freewill-fate-choice` | 自由意志與命運、選擇與代價 | Q135；薄伽梵歌 |
| `change-transformation` | 改變、轉向、人能否真的變 | Q263；傳習錄（知行合一） |

### XII. 信仰·神聖·超越（Faith, Sacred & Transcendence）

| 標籤 | 描述 | 代表題／對應經典 |
|------|------|-----------------|
| `faith-doubt` | 神存在嗎、信與疑 | Q101；彌蘭王問經、問難奧義書、聖訓手冊 |
| `beauty-wonder-transcendent-moment` | 美、驚奇、站在大山大海前的渺小又舒暢 | Q184 |

### XIII. 安頓·修復·平安（Settling, Repair & Peace）

| 標籤 | 描述 | 代表題／對應經典 |
|------|------|-----------------|
| `stillness-rest` | 停、靜、安頓、休息 | 傳習錄（靜坐）；安息日 |
| `gratitude-contentment` | 感恩、知足、怎樣算「夠了」 | Q245；論語（不改其樂）、米示拿·祝福章 |
| `hope-reason-to-live` | 希望、活下去的理由 | Q253 |
| `giving-generosity` | 施與、慷慨 | — |
| `play-laughter-lightness` | 玩、笑、輕盈 | — |

### 跨界支流（橫跨多領域，另立追蹤）

| 標籤 | 描述 | 橫跨 |
|------|------|------|
| `modern-tech-comparison` | 科技、注意力、比較文化、FOMO、AI 焦慮 | II 自我 · VI 情緒 · XIII 安頓 |
| `wisdom-learning-curiosity` | 智慧、學習、好奇——如何活得明白 | 所有領域 |
| `nature-animals-ecology` | 人在自然萬物中、動物、生態 | I 存在 · XII 超越 · IX 身體 |

---

## 使用方式

1. 標經文者讀 `01-translation.md`（＋ `02-annotation.md` 若有），問：**「一個帶著人生困惑的人，會因為哪個問題而翻到這部經？」**
2. 從上表選**最相關 1–5 個** `psych_tags`，填回 `meta.json`；只用表格第一欄正式定義的標籤。
3. **允許多標籤且鼓勵跨領域**——問答體經典常一部橫跨數域（論語、薄伽梵歌、傳習錄）。
4. 兩軸分開存：教義內容標 `semantic_tags`（見 `concepts.md`），人的問題標 `psych_tags`（本表）。**不混欄**。
5. 反向索引未來由 `scripts/build-tag-index.py` 擴充產生 `psych-tag-index.json`（每領域 → 有哪些經文回應）。

> 人工先驗：`11-psychology/reference-analects.md` 已把 20 部問答經典對到領域，可當 LLM 標籤前的黃金種子與校驗集。
