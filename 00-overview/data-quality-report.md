# 資料完整性稽核報告

> 自動產生：`scripts/audit-data-quality.py`　2026-07-05 06:22 +0800
> 掃描 4411 部

## 摘要

| 問題 | 數量 |
|------|------|
| 空 / 截斷 original.txt | 18 |
| U+FFFD 編碼損壞 | 4 |
| mojibake 疑似 | 0 |
| checksum 不符 | 0 |
| 重複內容(同 SHA) | 48 組 |
| meta 缺關鍵欄 | 0 |
| 缺章節分隔符 | 0 |
| 語言標籤不一致 | 0 |
| 外語字集占比過低 | 13 |

## 空 / 截斷 original.txt（18）

- `cbeta-T46n1943` — 有效內容僅 31 字
- `cbeta-T55n2168A` — 有效內容僅 48 字
- `cbeta-T55n2178` — 有效內容僅 12 字
- `cbeta-T55n2179` — 有效內容僅 11 字
- `cbeta-T55n2180` — 有效內容僅 23 字
- `cbeta-T55n2181` — 有效內容僅 19 字
- `cbeta-X05n0230` — 有效內容僅 14 字
- `cbeta-X10n0265` — 有效內容僅 32 字
- `sefaria-german-commentary-on-mishnah-orlah` — 有效內容僅 42 字
- `sefaria-hagahot-chavot-yair-on-bava-batra` — 有效內容僅 36 字
- `sefaria-hagahot-chavot-yair-on-beitzah` — 有效內容僅 20 字
- `sefaria-hagahot-chavot-yair-on-gittin` — 有效內容僅 20 字
- `sefaria-hagahot-habach-on-rif-bava-kamma` — 有效內容僅 24 字
- `sefaria-hagahot-habach-on-rif-beitzah` — 有效內容僅 10 字
- `sefaria-hagahot-mealfas-yashan-on-bava-metzia` — 有效內容僅 46 字
- `sefaria-haggahot-ya-avetz-on-mishnah-sheviit` — 有效內容僅 25 字
- `sefaria-matnot-kehunah-on-ruth-rabbah` — 有效內容僅 9 字
- `sefaria-rashi-on-chagigah` — 有效內容僅 26 字

## U+FFFD 編碼損壞（4）

- `chunqiu-fanlu` — 1 個置換字
- `yi-li` — 2 個置換字
- `yunji-qiqian` — 3 個置換字
- `zhuzi-yulei` — 8 個置換字

## mojibake 疑似（0）

_無_

## checksum 不符（meta vs 實檔）（0）

_無_

## 外語字集占比過低（疑亂碼 / 抓錯）（13）

- `cbeta-T18n0854` lang=古典漢語 期望CJK 實占22% 分布[('other', 3904), ('CJK', 1096)]
- `cbeta-T18n0875` lang=古典漢語 期望CJK 實占12% 分布[('other', 3319), ('CJK', 459)]
- `cbeta-T19n0944B` lang=古典漢語 期望CJK 實占0% 分布[('other', 2716)]
- `cbeta-T19n0983B` lang=古典漢語 期望CJK 實占2% 分布[('other', 4915), ('CJK', 85)]
- `cbeta-T19n1005B` lang=古典漢語 期望CJK 實占20% 分布[('other', 1097), ('CJK', 275)]
- `cbeta-T20n1062B` lang=古典漢語 期望CJK 實占0% 分布[('other', 247)]
- `cbeta-T20n1072B` lang=古典漢語 期望CJK 實占11% 分布[('other', 279), ('CJK', 34)]
- `cbeta-T20n1120B` lang=古典漢語 期望CJK 實占3% 分布[('other', 850), ('CJK', 24)]
- `cbeta-T20n1168B` lang=古典漢語 期望CJK 實占27% 分布[('other', 615), ('CJK', 230)]
- `cbeta-T20n1177B` lang=古典漢語 期望CJK 實占0% 分布[('other', 2122)]
- `cbeta-T21n1213` lang=古典漢語 期望CJK 實占15% 分布[('other', 252), ('CJK', 43)]
- `cbeta-T21n1226` lang=古典漢語 期望CJK 實占0% 分布[('other', 720)]
- `cbeta-T54n2133A` lang=古典漢語 期望CJK 實占22% 分布[('other', 3728), ('CJK', 1122), ('Latin', 150)]

## 缺章節分隔符（0）

_無_

## meta 缺關鍵欄（0）

_無_

## 重複內容（同 SHA-256，48 組）

- `3b00dcbd0c40` × 2：abhidharma-jnanaprasthana, cbeta-T26n1544
- `e8a146bfaea4` × 2：abhidharmakosa, cbeta-T29n1558
- `8f24a5fc975c` × 2：abhidharmasamuccaya, cbeta-T31n1605
- `9863d47e42cd` × 2：amitabha-sutra, cbeta-T12n0366
- `f67ffcdb95b6` × 2：avatamsaka-sutra, cbeta-T10n0279
- `e710b1a20abd` × 2：awakening-of-faith, cbeta-T32n1666
- `7e610c2fa4f0` × 2：cbeta-T01n0001, dirghagama
- `b295f09906dd` × 2：cbeta-T01n0007, tathagatagarbha-mahaparinirvana
- `a17643c69f51` × 2：cbeta-T01n0026, madhyamagama
- `fea954bccb61` × 2：cbeta-T02n0099, samyuktagama
- `7faebbae676c` × 2：cbeta-T02n0125, ekottarikagama
- `7dfe2d59f5cf` × 2：cbeta-T08n0223, prajnaparamita-25000
- `6948c6b948cb` × 2：cbeta-T08n0227, prajnaparamita-8000
- `60d9d2446fb9` × 2：cbeta-T08n0235, diamond-sutra-kumarajiva
- `d5237c5aa697` × 2：cbeta-T08n0245, humane-king-sutra
- `f8b557d9f08d` × 2：cbeta-T08n0250, heart-sutra-kumarajiva
- `5c76fbc02507` × 2：cbeta-T08n0251, heart-sutra-xuanzang
- `df34adc2586f` × 2：cbeta-T09n0262, lotus-sutra
- `268bf8f70858` × 2：cbeta-T09n0277, samantabhadra-meditation-sutra
- `a13648157799` × 2：cbeta-T11n0310, ratnakuta-sutra
- `e7f59fb9fa23` × 2：cbeta-T12n0353, srimaladevi-sutra
- `d91664b63f2e` × 2：cbeta-T12n0360, infinite-life-sutra
- `8eb743dc25bf` × 2：cbeta-T12n0365, contemplation-sutra
- `e3dc0bbe5539` × 2：cbeta-T12n0374, mahaparinirvana-sutra-northern
- `448bafa13d9d` × 2：cbeta-T13n0397, mahasannipata-sutra
- `2b5322082701` × 2：cbeta-T13n0412, ksitigarbha-sutra
- `667a9df6f404` × 2：cbeta-T14n0450, medicine-buddha-sutra
- `91f2a3471711` × 2：cbeta-T14n0475, vimalakirti-sutra
- `fa733387a91c` × 2：cbeta-T16n0666, tathagatagarbha-sutra
- `e4c609b378f0` × 2：cbeta-T16n0670, lankavatara-sutra
- `c6886ed6ee48` × 2：cbeta-T16n0676, samdhinirmocana-sutra
- `3495b3fa9d92` × 2：cbeta-T17n0784, fortytwo-chapters-sutra
- `8f348bacbe67` × 2：cbeta-T17n0842, perfect-enlightenment-sutra
- `b6baebafe676` × 2：cbeta-T18n0848, mahavairocana-sutra
- `56c95d9cf532` × 2：cbeta-T18n0865, vajrasekhara-sutra
- `127916082622` × 2：cbeta-T19n0945, shurangama-sutra
- `d34e2b2e839a` × 2：cbeta-T22n1421, wufenlu
- `da2b0ff1e48b` × 2：cbeta-T22n1425, mahasanghika-vinaya
- `21bc3ce77592` × 2：cbeta-T22n1428, sifenlu
- `14eba7a9863d` × 2：cbeta-T23n1435, shisonglu
- `e4da126f9797` × 2：cbeta-T25n1509, mahaprajnaparamita-shastra
- `74490ce0a4a2` × 2：cbeta-T30n1564, diamond-mulamadhyamaka
- `c86b74cdf563` × 2：cbeta-T30n1579, yogacarabhumi
- `4a7ef79f127e` × 2：cbeta-T31n1585, vijnaptimatratasiddhi
- `4e3a31caa87f` × 2：cbeta-T31n1586, trishika
- `3a57b98949dd` × 2：cbeta-T31n1590, vimsika
- `563275ea9326` × 2：cbeta-T31n1593, mahayanasamgraha
- `23909e76d67c` × 2：cbeta-T32n1646, satyasiddhi

## 語言標籤不一致

_無_

