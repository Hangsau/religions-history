# 待補原文清單（original-text-todo）

> 由 `scripts/audit-core.py` 自動產生。列出**核心語料只有英譯本、且原文有乾淨來源可收但尚未收**的部。
> 政策：先英→中翻譯（過渡），原文取得後重譯。這是 Pipeline A 的補抓待辦，非阻塞。
> 已查明「無乾淨原文來源」的部另列文末分區（來源狀態表 `scripts/catalog/original-source-status.json`）。

- 可收待補原文核心：**0** 部，橫跨 **0** 宗教

---

## 已查明無乾淨原文來源（附探查記錄，非未查的待辦）

> 這些核心經過實際探查，確認目前無乾淨可收的原文來源。分三類，逐部附理由與已探來源。
> 出現乾淨來源即收——移除 `original-source-status.json` 對應條目即回到可收待補。

- 已查明無乾淨來源：**28** 部

### 來源受牆／無乾淨匯出（原文存於已知數位語料庫但存取受阻）（16 部）

- `book-of-am-tuat` 阿姆杜阿特之書（幽冥界之書）（古埃及）
  - 理由：Budge 英譯；連續埃及原文／音譯僅存於 TLA（thesaurus-linguae-aegyptiae.de），無對應此彙編之逐篇文本匯出。本檔實測 0 連續音譯，僅散見英文中夾用神名。
  - 已探來源：sacred-texts(Budge,英)；TLA(無乾淨逐篇匯出)
- `book-of-gates` 門之書（古埃及）
  - 理由：同 book-of-am-tuat：Budge 英譯，TLA 未提供對應此彙編的乾淨逐篇原文。
  - 已探來源：sacred-texts(Budge,英)；TLA
- `bundahishn` Bundahishn + Bahman Yasht + Shayast la-Shayast（瑣羅亞斯德）
  - 理由：avesta.org 僅 West／Anklesaria 英譯（grb.htm 實測 2115 英文詞）。Pahlavi 轉寫僅存 TITUS（結構性存取阻力）／Pakzad 2005（受版權）。
  - 已探來源：avesta.org(英譯)；TITUS(受阻)
- `burden-of-isis` 伊西斯的悲歌（奧西里斯讚歌）（古埃及）
  - 理由：Budge 英譯（Isis/Osiris 讚歌）；原文散於各神廟銘文，TLA 無對應單一乾淨文本。
  - 已探來源：sacred-texts(Budge,英)；TLA
- `code-of-hammurabi-st` 漢摩拉比法典（兩河）
  - 理由：阿卡德楔形；ORACC 可存取專案不含此文本，eBL 需登入，SEAL 為 JS SPA 無法乾淨抽取，ETCSL 僅蘇美語（語言不符）。
  - 已探來源：ORACC(不含)；eBL(登入牆)；SEAL(JS-SPA)；ETCSL(蘇美語)
- `dadestan-i-denig` Dadestan-i Denig (宗教裁判)（瑣羅亞斯德）
  - 理由：West 英譯（SBE 18）。Pahlavi 轉寫僅 TITUS／Jaafari-Dehaghi（受版權）。
  - 已探來源：avesta.org(英譯)；TITUS(受阻)
- `denkard-3-bahman-yasht` Pahlavi Texts Part III（瑣羅亞斯德）
  - 理由：West 英譯（SBE 37）。Denkard Pahlavi 轉寫僅 TITUS／Madan 版影印。
  - 已探來源：avesta.org(英譯)；TITUS(受阻)
- `denkard-bk-5` Pahlavi Texts Part V (Contents of the Nasks)（瑣羅亞斯德）
  - 理由：West 英譯（Nasks 內容）。Pahlavi 轉寫僅 TITUS／Madan。
  - 已探來源：avesta.org(英譯)；TITUS(受阻)
- `denkard-bk-7-8` Dinkard Books 8-9（瑣羅亞斯德）
  - 理由：West 英譯（Dinkard 8-9）。Pahlavi 轉寫僅 TITUS／Madan。
  - 已探來源：avesta.org(英譯)；TITUS(受阻)
- `egyptian-book-of-dead` 古埃及死者之書（古埃及）
  - 理由：Budge Papyrus of Ani 英譯（975KB）；實測僅散見神名，無連續埃及音譯。連續原文需 TLA／Faulkner 版（受牆或無乾淨匯出）。
  - 已探來源：sacred-texts(Budge,英)；TLA
- `egyptian-heaven-and-hell` 埃及的天堂與地獄（古埃及）
  - 理由：Budge 英譯；原文散於 Am-Tuat／Gates 銘文，TLA 無對應乾淨文本。
  - 已探來源：sacred-texts(Budge,英)；TLA
- `enuma-elish-stc` 創世七碑（埃努瑪·埃利什）（兩河）
  - 理由：阿卡德楔形；同 Hammurabi，各阿卡德語料庫皆存取受阻或語言不符。
  - 已探來源：ORACC(不含)；eBL(登入牆)；SEAL(JS-SPA)
- `epic-of-gilgamesh-st` 吉爾伽美什史詩（兩河）
  - 理由：標準巴比倫語阿卡德；ORACC/eBL/SEAL 皆受阻。
  - 已探來源：ORACC(不含)；eBL(登入牆)；SEAL(JS-SPA)
- `legends-of-the-gods-egypt` 諸神傳說（古埃及文本）（古埃及）
  - 理由：Budge 英譯諸神傳說；原文散於多紙草，TLA 無對應此選集之乾淨匯出。
  - 已探來源：sacred-texts(Budge,英)；TLA
- `liturgy-funerary-offerings` 葬祭供養儀軌（古埃及）
  - 理由：Budge 英譯葬祭儀軌；TLA 無對應乾淨文本。
  - 已探來源：sacred-texts(Budge,英)；TLA
- `pyramid-texts-mercer` 金字塔銘文（古埃及）
  - 理由：Mercer 英譯金字塔銘文（536KB）；實測含散見音譯詞（smin、sḥ-n-t-r 等 649 附標字元）但非連續轉寫，僅為 apparatus。連續轉寫需 TLA／Sethe（受牆）。
  - 已探來源：sacred-texts(Mercer,英)；TLA(無乾淨匯出)

### 英/西譯為學術彙編或選集，無單一底本（9 部）

- `chilam-balam` 契倫·巴蘭之書 (Chumayel)（美洲）
  - 理由：Roys 英譯 Chumayel（實測英文為主，僅散見馬雅曆法／神名詞）。尤卡坦馬雅語轉寫（Chumayel 手稿）無乾淨全文數位來源（Gordon 1913 為影印非文本）。
  - 已探來源：sacred-texts(Roys,英)；es/en.wikisource(無)
- `fragments-of-faith-forgotten` 被遺忘信仰的碎片 (Mead)（諾斯底）
  - 理由：Mead 19c 學術散文著作（諾斯底研究概論），非單一底本經文；無對應原文可收。
  - 已探來源：sacred-texts(Mead,英著作)
- `gnostics-and-their-remains` 諾斯底與其遺存 (King)（諾斯底）
  - 理由：C.W. King 19c 學術著作（諾斯底遺存考），非經文底本。
  - 已探來源：sacred-texts(King,英著作)
- `sikh-religion-macauliffe` 錫克教（Macauliffe）（錫克教）
  - 理由：Macauliffe 六卷《The Sikh Religion》為學術彙編（史傳＋選譯），非單一底本；Gurbani 原文已另收於 guru-granth-sahib-pa（古木基旁遮普原文）。
  - 已探來源：sacred-texts(Macauliffe,英彙編)
- `songs-of-russian-people` 俄羅斯人民之歌（斯拉夫）
  - 理由：Ralston《Songs of the Russian People》為 19c 英文民俗彙編（民歌＋評註），非單一斯拉夫底本；散引之俄文民歌無單一原典。
  - 已探來源：sacred-texts(Ralston,英彙編)
- `splendour-of-god` 上帝的光輝 (巴哈歐拉著作節錄)（巴哈伊）
  - 理由：Hammond 1909《Splendour of God》為巴哈歐拉著作英文節錄選集；阿拉伯／波斯原文散於各原著（Íqán／Hidden Words 等），無對應此選集之單一底本。
  - 已探來源：sacred-texts(Hammond,英選集)；bahai.org(原文散於各書)
- `thrice-greatest-hermes-1` 三度偉大的赫爾墨斯 Vol 1 (Mead)（諾斯底）
  - 理由：Mead《Thrice-Greatest Hermes》Vol 1 為 Prolegomena（Mead 自撰導論），非原典；Corpus Hermeticum 希臘原文已另收於 corpus-hermeticum-el（對應 Vol 2）。
  - 已探來源：sacred-texts(Mead,英導論)
- `thrice-greatest-hermes-3` 三度偉大的赫爾墨斯 Vol 3（諾斯底）
  - 理由：Mead Vol 3 為 Excerpts/Fragments（Stobaeus 選錄＋殘篇）；希臘殘篇散於 Stobaeus Anthologium，無乾淨 1:1 底本可收。
  - 已探來源：sacred-texts(Mead,英選錄)；Stobaeus(散篇)
- `yucatan-before-after-conquest` 尤卡坦征服前後 (Landa)（美洲）
  - 理由：Gates 英譯 Landa《Relación de las cosas de Yucatán》（實測純英文）。西班牙文原文為公版但乾淨數位版僅存於 2002 現代校訂本（含受版權編輯 apparatus，OCR 無法乾淨切分）；archive.org 無乾淨 PD 西文版索引。
  - 已探來源：sacred-texts(Gates,英)；es.wikisource(無)；archive.org(僅2002受版權OCR/1898為他書)

### 口傳傳統，無文字書寫系統（採錄本即最早可及形式）（3 部）

- `ife-mythology` 伊費神話 (約魯巴)（非洲）
  - 理由：約魯巴口傳傳統，前文字社會無音位書寫系統；英文採錄本即最早可及形式，無書面原文可收。
  - 已探來源：sacred-texts(英採錄)
- `inca-rites` 印加儀禮與法律（美洲）
  - 理由：印加用結繩（quipu）記事，無表音文字；Markham 由西班牙編年史家（Molina/Salcamayhua）英譯整理，無單一書面原典。部分克丘亞語祈禱（Molina）存殘篇但非此彙編底本。
  - 已探來源：sacred-texts(Markham,英彙編)
- `yoruba-religion` 約魯巴宗教與神話（非洲）
  - 理由：約魯巴宗教口傳，無文字原典；英文本為採錄／整理。
  - 已探來源：sacred-texts(英採錄)

