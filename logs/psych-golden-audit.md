# psych_tags 黃金抽驗稽核報告

> 稽核日期：2026-07-21
> 稽核範圍：`translations/*/meta.json` 中 `psych_tag_status == "done"` 的 155 部
> 白名單依據：`00-overview/concepts-psychology.md`（45 細群 + 3 跨界支流 = 48 slugs）
> 黃金種子依據：`11-psychology/reference-analects.md`
> 判準：錯標（主題不存在，須附譯文引文證據；無法舉證則列待查）／過標（主題僅邊緣擦到，不符「1–5 個最相關」原則）／漏標（僅建議，不計入錯誤率）
> 錯誤率 =（錯標 + 過標 tag 數）÷ 20 部總 tag 數；> 10% = FAIL

---

## Part A — 白名單機械檢查

- 掃描 `psych_tag_status=="done"` 作品數：**155**
- psych_tags 總數：**761**（平均 4.9 tags/部）
- 白名單外違規 tag 數：**0**

**違規清單：0（無）**

### 附帶觀察：標籤分布高度聚集（Part B 系統性偏誤的量化背景）

| tag | 出現部數 | 佔比 |
|-----|---------|------|
| death | 93 | 60.0% |
| change-transformation | 82 | 52.9% |
| calling-vocation | 49 | 31.6% |
| courage | 49 | 31.6% |
| body-mind | 48 | 31.0% |
| faith-doubt | 47 | 30.3% |
| fear-uncertainty | 43 | 27.7% |

死亡與轉化兩標各覆蓋過半作品；48 個標籤中另有多個近乎未用。分布本身即暗示 tagger 傾向套用一組「泛用宗教標籤」而非逐部判斷。

---

## Part B — 20 部人工核對

選樣：黃金種子 8 部（analects、mengzi、bhagavad-gita、katha-upanishad、brihadaranyaka-upanishad、prashna-upanishad、ecclesiastes、job）+ 12 部按宗教多樣性補足（儒 2、猶太 3、基督 3、佛 3、道 2、印度 4、古希臘羅馬 2、錫克 1，共 8 傳統）。20 部皆為 5 tags，合計 100 tags。

### 1. analects（儒教）— 5 tags，全數成立

- tags：aging-time / calling-vocation / change-transformation / communication-being-understood / courage
- 錯標：無。過標：無。
- aging-time（「吾十有五而志於學…七十而從心所欲」年歲敘事）、courage（「見義不為，無勇也」）、communication（問答教學、因材施教）皆有本文支撐。
- 漏標建議：marriage-family（問孝多章，黃金種子域 IV）、justice-power／responsibility-leadership（問政，域 V）、honesty-hypocrisy（「巧言令色」，域 VII）、gratitude-contentment（「不改其樂」，域 XIII——concepts-psychology.md 明列論語為此細群代表）。黃金種子六域僅命中約半。

### 2. mengzi（儒教）— 5 tags，1 過標

- tags：aging-time / body-mind / boundaries-self-worth / calling-vocation / change-transformation
- **過標：aging-time** — 抽樣所見涉老年者為「老吾老以及人之老」「大孝終身慕父母，五十而慕」等孝養／仁政脈絡，屬奉養與孝道，非細群定義之「老與時間、身體與容顏的流逝」的存在性課題。
- 其餘成立：body-mind（「志，氣之帥也；氣，體之充也」養氣章）、boundaries-self-worth（「說大人則藐之」）、calling-vocation（「天將降大任於是人也」「舍我其誰」）、change-transformation（「人皆可以為堯舜」、擴充四端）。
- 漏標建議：justice-power（王道、民貴君輕——孟子黃金種子核心域 V，竟未標）、responsibility-leadership、marriage-family。

### 3. bhagavad-gita（印度教）— 5 tags，全數成立

- tags：beauty-wonder-transcendent-moment / body-mind / calling-vocation / change-transformation / courage
- 錯標：無。過標：無。
- calling-vocation 強支撐（18.47「己法雖劣，猶勝他法之行」svadharma 論，concepts-psychology.md 明列薄伽梵歌為此細群代表）；courage（18.43 剎帝利之德「英勇…不退於戰」）；beauty-wonder（第 11 章宇宙形相顯現）。
- 漏標建議：**freewill-fate-choice**——黃金種子域 XI 且 concepts-psychology.md 於該細群明列薄伽梵歌為代表經典；18.59–61（「本性所生之業縛汝」「如置於機關上之傀儡」）正是自由意志與命運的核心文本。此為黃金種子域直接落空。另 death（2.20 不生不滅）亦可考慮。

### 4. katha-upanishad（印度教）— 5 tags，全數成立

- tags：body-mind / death / existence-why-born / fear-uncertainty / living-with-unknown
- 錯標：無。過標：無。
- death 為全書骨架（Naciketas 問閻摩死後之事，concepts-psychology.md 明列迦塔奧義書為 death 代表）；body-mind 有車喻直接支撐（「知身為車、ātman 為車主、buddhi 為御者、manas 為韁」，行 203–212）；fear-uncertainty／living-with-unknown 對應「此疑惑：人死之後…」的追問。此部為 20 部中標得最貼合者。

### 5. brihadaranyaka-upanishad（印度教）— 5 tags，2 過標

- tags：body-mind / calling-vocation / change-transformation / courage / death
- **過標：calling-vocation** — 抽樣（1.1–1.4 祭馬與創世、3.9 Śākalya 問答、6.3–6.5 傳承譜系）未見「天賦、使命、這輩子為何而來」主題；全書主軸為梵我知識、祭祀奧義與不死。
- **過標：courage** — 最接近者為 1.4.2「彼畏，故獨者畏。彼思：『除我外無他，何畏？』是故其畏滅」，此為「由二元性生怖、由知一而怖滅」的形上論述，屬 fear-uncertainty 的消解而非「勇氣、面對該面對的」品格主題。
- 成立：death（「導我從死亡至不死 mṛtyor māmṛtaṃ gamaya」1.3.28）、change-transformation（同偈「從非有至有、從黑暗至光明」的轉化祈願）、body-mind（prāṇa 諸根與 ātman 關係為全書反覆論題，3.9 八 puruṣa 以身處為住）。
- 漏標建議：**who-am-i**——concepts-psychology.md 明列大林間奧義書為 who-am-i 細群代表經典；1.4.1「此初唯 ātman（我），為人形…彼初言『我是』。是故名『我』」正是「真我是什麼」的原型文本。黃金種子域直接落空。

### 6. prashna-upanishad（印度教）— 5 tags，1 過標

- tags：body-mind / calling-vocation / change-transformation / death / dreams-unconscious
- **過標：calling-vocation** — 六問（眾生從何生、prāṇa、睡與夢、oṃ、十六 kalā）皆為形上求知，抽樣未見天賦使命主題。
- 成立：dreams-unconscious（第四問專論睡夢：「此名為『意』之 deva，以見門之光焰不見夢」）、death（6.6「應知此所應知之 puruṣa，願死（mṛtyu）不擾汝等」）、body-mind（prāṇa 十六 kalā 遍全書）、change-transformation（kalā 消歸 puruṣa「以無 kalā 故即成 amṛta」）。
- 漏標建議：**faith-doubt**——concepts-psychology.md 明列問難奧義書為 faith-doubt 細群代表；六仙人以 tapas、brahmacarya、śraddhā（信心）住滿一年方許發問，正是信與求問的框架。另 wisdom-learning-curiosity（師徒問學體）。

### 7. ecclesiastes（猶太教）— 5 tags，全數成立

- tags：death / gratitude-contentment / living-with-unknown / meaning-of-suffering / nihilism-void
- 錯標：無。過標：無。
- nihilism-void（「虛空的虛空，凡事都是虛空」）、death（「智慧人和愚昧人一樣，永遠無人記念…都是死」）、living-with-unknown（「神從始至終的作為，人不能參透」）、gratitude-contentment（「人莫強如吃喝，且在勞碌中享福」）皆為主軸。concepts-psychology.md 三處明列傳道書（existence-why-born、nihilism-void、aging-time）。
- 漏標建議：aging-time（第 12 章衰老寓言「銀鏈折斷、金罐破裂」——concepts-psychology.md 明列傳道書為 aging-time 代表）、existence-why-born。

### 8. job（猶太教）— 5 tags，全數成立

- tags：death / faith-doubt / fear-uncertainty / guilt-atonement / honesty-hypocrisy
- 錯標：無。過標：無。
- faith-doubt（約伯抗辯與堅持）、guilt-atonement（三友「你必有罪」的控訴框架）、honesty-hypocrisy（42:7 神斥三友「你們議論我不如我的僕人約伯說的是」——誠實抗辯勝於虔誠套話）、death（「我知道你必使我臨到死地」）、fear-uncertainty（「我所恐懼的臨到我身」3:25）皆有支撐。
- 漏標建議：**meaning-of-suffering**——約伯記是神義論原型文本，concepts-psychology.md 明列約伯記為 meaning-of-suffering 代表經典（「壞事為何降在好人」即約伯記主題句），未標是 20 部中最嚴重的單一漏標。另 loss-grief（喪子女、喪產業）、living-with-unknown（38–41 章旋風答問「我立大地根基時你在哪裡」——concepts-psychology.md 亦列約伯記為此細群代表）。

### 9. ruth（猶太教）— 5 tags，全數成立

- tags：ingroup-outgroup-prejudice / loss-grief / love-sex-intimacy / marriage-family / trust-vulnerability
- 錯標：無。過標：無。
- 摩押女子入以色列（ingroup-outgroup）、喪夫寡婦（loss-grief）、「你往哪裡去，我也往那裡去」（trust-vulnerability）、禾場求贖與波阿斯娶路得（love-sex-intimacy、marriage-family）皆為敘事主線。標得貼合。

### 10. sblgnt-romans（基督教）— 5 tags，1 過標

- tags：change-transformation / faith-doubt / fear-uncertainty / freewill-fate-choice / giving-generosity
- **過標：giving-generosity** — 施與僅見於勸勉附段（12:8 施捨、15:26 馬其頓亞該亞「為耶路撒冷聖徒中的窮人作了一些捐贈」），非會令人「因施與問題翻開羅馬書」的主題；相對之下全書核心的罪與救贖反而未標（見漏標）。
- 成立：freewill-fate-choice 強支撐（第 9 章揀選論：「窯匠難道沒有權柄，從同一團泥裏，拿一塊做成貴重的器皿…」「他要憐憫誰，就憐憫誰」）、faith-doubt（「義人必因信得生」因信稱義主軸）、change-transformation（12:2 心意更新而變化、第 6 章新生命）、fear-uncertainty（8:35–39「誰能使我們與基督的愛隔絕呢？是患難嗎…」對恐懼的總安慰）。
- 漏標建議：**guilt-atonement**——罪、稱義、救贖是羅馬書全書論證核心（1–8 章），未標為顯著缺漏。另 hope-reason-to-live（5:3–5、15:13「願盼望的神使你們充滿喜樂平安」）。

### 11. sblgnt-james（基督教）— 5 tags，全數成立

- tags：faith-doubt / honesty-hypocrisy / justice-power / meaning-of-suffering / work-money
- 錯標：無。過標：無。
- faith-doubt（「信心沒有行為是死的」「疑惑的人如海中波浪」）、honesty-hypocrisy（勒住舌頭、聽道行道）、justice-power／work-money（第 5 章斥富人「工人的工錢被你們剋扣」第 2 章勿重富輕貧）、meaning-of-suffering（1:2–4 百般試煉生忍耐）皆為書信主軸。標得貼合。

### 12. sblgnt-philemon（基督教）— 5 tags，1 過標

- tags：giving-generosity / guilt-atonement / love-sex-intimacy / responsibility-leadership / trust-vulnerability
- **過標：love-sex-intimacy** — 本信之愛為主內弟兄之愛與和解（收納逃奴歐尼西慕「不再是奴僕，乃是高過奴僕，是親愛的兄弟」），細群定義為「愛與性、什麼是愛、怎麼知道這是愛」的親密之愛；agape 式弟兄接納應歸 memory-reconciliation 或 trust-vulnerability，非本細群。
- 成立：guilt-atonement（「他若虧負你或欠你什麼，都歸在我的帳上」代償結構）、trust-vulnerability（保羅請求腓利門憑愛心接納）、giving-generosity、responsibility-leadership（保羅以權柄「本可吩咐你」卻選擇請求）。
- 漏標建議：memory-reconciliation（主奴和解正是本信全部內容）。

### 13. heart-sutra-xuanzang（佛教）— 5 tags，全數成立

- tags：fear-uncertainty / meaning-of-suffering / stillness-rest / who-am-i / wisdom-learning-curiosity
- 錯標：無。過標：無。
- fear-uncertainty（「心無罣礙，無罣礙故，無有恐怖」直接支撐）、meaning-of-suffering（「度一切苦厄」「能除一切苦」）、who-am-i（「照見五蘊皆空」）、wisdom（般若波羅蜜多）皆本文可徵。
- 漏標建議：nihilism-void（「色即是空」——concepts-psychology.md 明列般若類為 nihilism-void 代表，可換掉較弱的 stillness-rest）。

### 14. dhammapada（佛教）— 5 tags，1 過標

- tags：addiction-self-destruction / aging-time / change-transformation / communication-being-understood / death
- **過標：communication-being-understood** — 全文 grep 僅一處近似（行 39「他人不了知我等」），且其語境是「不知死之將至」的無常警醒（雙品 6 偈），非「渴望被理解卻沒人真懂」；法句經的語言諸品（千品、刀杖品之語）屬言語倫理，亦非本細群。
- 成立：death／aging-time（老品「此形骸衰老」、「不放逸是不死路」）、addiction-self-destruction（愛欲品「其欲如蔓草蔓延」）、change-transformation（「自為自依怙」自調御）。
- 漏標建議：emotions-passions（忿怒品、愛欲品正對「七情六慾如何生滅」）、freewill-fate-choice（自業自受）。

### 15. amitabha-sutra（佛教）— 5 tags，1 過標

- tags：death / faith-doubt / hope-reason-to-live / meaning-of-suffering / stillness-rest
- **過標：meaning-of-suffering** — 經文明言「彼土何故名為極樂？其國眾生，無有眾苦，但受諸樂」；本經內容是離苦得樂的淨土描述與執持名號，並無「受苦的意義、神義論」的探問。
- 成立：death（「臨命終時，阿彌陀佛與諸聖眾現在其前…即得往生」死亡關懷核心）、faith-doubt（「汝等眾生，當信是稱讚不可思議功德」「為一切世間說此難信之法」）、hope-reason-to-live（極樂願景）。

### 16. tao-te-ching（道教）— 5 tags，1 過標

- tags：change-transformation / courage / death / justice-power / living-with-unknown
- **過標：courage** — 僅 67 章「慈故能勇」與 73 章「勇於敢則殺，勇於不敢則活」擦邊，且後者正是對「敢」的批判；全書基調是不爭、柔弱勝剛強，非「勇氣、面對該面對的」主題。
- 成立：change-transformation（「反者道之動」「禍兮福之所倚」）、living-with-unknown（「道可道，非常道」「玄之又玄」）、justice-power（「以正治國」「民之飢，以其上食稅之多」治道諸章）、death（「死而不亡者壽」「民不畏死」）。
- 漏標建議：stillness-rest（「致虛極，守靜篤」「歸根曰靜」——全書核心工夫，未標是明顯缺漏）、gratitude-contentment（「知足者富」「知足不辱」）。

### 17. qingjing-jing（道教）— 5 tags，全數成立

- tags：change-transformation / emotions-passions / stillness-rest / who-am-i / wisdom-learning-curiosity
- 錯標：無。過標：無。
- stillness-rest（「人能常清靜，天地悉皆歸」全經主旨）、emotions-passions（「遣其欲而心自靜，澄其心而神自清」六欲三毒）、who-am-i（「內觀其心，心無其心」）皆直接支撐。標得貼合。

### 18. plato-apology-el（古希臘羅馬）— 5 tags，全數成立

- tags：calling-vocation / courage / death / evil-cruelty-empathy / faith-doubt
- 錯標：無。過標：無。
- calling-vocation（神托付的省察使命「只要一息尚存，我絕不停止愛智」）、courage（「一個人應當只考慮行事是對是錯，而非生死」）、death（「死或是無夢之眠，或是遷往彼處」結尾長論）、faith-doubt（神諭與 daimonion 之辯）、evil-cruelty-empathy（「作惡比受惡更可恥」、控告者之惡）皆本文可徵。

### 19. epictetus-enchiridion-el（古希臘羅馬）— 5 tags，全數成立

- tags：boundaries-self-worth / courage / death / emotions-passions / fear-uncertainty
- 錯標：無。過標：無。
- boundaries-self-worth（第 1 章權內／權外之分即界線原型）、death（「死亡並不可怕…可怕的是關於死亡的判斷」）、emotions-passions／fear-uncertainty（「擾動人的不是事物，而是對事物的看法」）、courage（面對困難「回轉向自身，問自己有何能力對付它」）皆有支撐。
- 漏標建議：freewill-fate-choice（黃金種子域 XI：控制二分法、「願事如其所是地發生」正是自由與命運課題，reference-analects.md 對此部即對域 XI）。

### 20. japji-sahib-pa（錫克教）— 5 tags，2 過標

- tags：death / existence-why-born / faith-doubt / fear-uncertainty / freewill-fate-choice
- **過標：existence-why-born** — 相關段落為創世宇宙論頌讚（「依其旨意，形體生焉」hukam 諸節），是神如何造萬有的讚頌，非「我為何在此、沒答應被生下卻得活著」的個人存在探問。
- **過標：fear-uncertainty** — 「無畏（nirbhau）」出現於 Mūl Mantar，是神的屬性稱號；全篇未見以人的恐懼、焦慮為主題的段落。
- 成立：faith-doubt（「如何成為真理者？如何破除虛妄之牆？」為全篇主題句）、freewill-fate-choice（hukam 天命與「依其旨意而行」）、death（「業決定此生，恩典之目得解脫之門」輪迴脈絡）可支撐。
- 漏標建議：stillness-rest／gratitude-contentment（晨禱聆聽與憶念諸頌）、beauty-wonder-transcendent-moment（vismād 驚奇諸節「奇哉！」）。

---

## 結論

| 項目 | 數值 |
|------|------|
| Part A 白名單違規 | **0** |
| Part B 抽驗 tag 總數 | 100（20 部 × 5） |
| 錯標 | 0 |
| 過標 | **11** |
| 錯誤 tag 數合計 | 11 |
| **錯誤率** | **11.0%** |
| 門檻 | 10% |
| **判定** | **FAIL（邊緣超標）** |

過標明細：mengzi(aging-time)、brihadaranyaka(calling-vocation, courage)、prashna(calling-vocation)、romans(giving-generosity)、philemon(love-sex-intimacy)、dhammapada(communication-being-understood)、amitabha(meaning-of-suffering)、tao-te-ching(courage)、japji(existence-why-born, fear-uncertainty)。

### 系統性偏誤（給 tagger prompt 修正）

1. **泛用標籤套模板**：death(60%)、change-transformation(53%)、courage/calling-vocation/body-mind(各 ~31%) 高頻聚集；三部奧義書的五標近乎同一套（body-mind + calling-vocation + change-transformation + courage + death），calling-vocation 被當「修行經典萬用標」貼給無使命主題的形上論書（brihadaranyaka、prashna）。修正：prompt 應要求「每個 tag 附一句本文出處」並明示「奧義書式梵我論 ≠ calling-vocation」。
2. **字面關鍵詞比對取代主題判斷**：出現「勇／愛／施捨／不了知」等字樣即貼標——tao-te-ching 的 courage（實為批判「勇於敢」）、philemon 的 love-sex-intimacy（agape 弟兄愛）、dhammapada 的 communication-being-understood（單句且語境是無常）、romans 的 giving-generosity（附帶勸勉段）。修正：prompt 應強調判準是「帶著該困惑的人會為此翻開這部經嗎」，非詞面命中。
3. **讚頌／宇宙論誤讀為個人提問**：japji 把神之屬性「無畏」讀成 fear-uncertainty、把創世頌讚讀成 existence-why-born；amitabha 把「無有眾苦」的淨土描述讀成 meaning-of-suffering。讚歌體與淨土描述類文獻需明示「神的屬性 ≠ 人的困惑」。
4. **核心主題大面積漏標（advisory，未計入錯誤率但同源）**：job 漏 meaning-of-suffering（神義論原型、白名單表明列代表經典）、bhagavad-gita 漏 freewill-fate-choice、brihadaranyaka 漏 who-am-i、prashna 漏 faith-doubt、romans 漏 guilt-atonement、tao-te-ching 漏 stillness-rest——六處皆為 concepts-psychology.md／reference-analects.md 明列的黃金種子對應域。5 個 tag 名額被泛用標籤佔滿，擠掉了各書最核心的域。修正：可在 prompt 內附黃金種子對照表作 few-shot 錨點。
5. **一律標滿 5 個**：抽驗 20 部全數為 5 tags（全體平均 4.9），「最相關 1–5 個」被執行成「固定 5 個」，稀釋精度並直接製造過標。修正：prompt 明示「寧 3 個準，勿 5 個滿」。

### 附帶資料品質觀察（非 psych_tags 問題，不在本稽核修改範圍）

- `translations/epictetus-enchiridion-el/01-translation.md` 行 72–78 混入 pipeline commit 紀錄文字（「已 commit + push (f7a1e227)…」）。
- `translations/plato-apology-el/01-translation.md` 行 260–267 混入 commit 955b61c8 / c06dbce6 與 HANDOFF 備註文字。

兩者皆為翻譯管線輸出污染，建議另開任務清理（本稽核依約不動翻譯檔）。
