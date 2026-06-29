# Religions History

世界宗教史研究專案 — 從史前到現代的跨文化宗教結構化整理。

## 概述

這是一份以學術框架整理的世界宗教史資料庫，目標是：

- **結構化**：每個宗教條目固定格式（起源 → 教義 → 儀式 → 組織 → 爭議 → 當代）
- **可引用**：每篇標明資料來源（A/B/C/D 等級分流）
- **可延伸**：模組化結構，方便未來加入新主題 / 翻譯 / 視覺化
- **中性**：不護教、不破教、不比較優劣

詳細計畫見 [`PLAN.md`](./PLAN.md)，工作守則見 [`CLAUDE.md`](./CLAUDE.md)。

## 內容索引

| 區域 | 涵蓋 |
|------|------|
| [00-overview](./00-overview/) | 總覽、時間軸、分類 |
| [01-prehistoric-mesopotamia](./01-prehistoric-mesopotamia/) | 蘇美、巴比倫、亞述、瑣羅亞斯德 |
| [02-egypt](./02-egypt/) | 古埃及宗教 |
| [03-india](./03-india/) | 印度教、佛教、耆那、錫克 |
| [04-china](./04-china/) | 儒、道、佛、民間信仰 |
| [05-japan-korea](./05-japan-korea/) | 神道、韓日佛教 |
| [06-abrahamic](./06-abrahamic/) | 猶太、基督、伊斯蘭、巴哈伊 |
| [07-africa](./07-africa/) | 非洲傳統信仰 |
| [08-oceania](./08-oceania/) | 大洋洲原住民 |
| [09-americas](./09-americas/) | 瑪雅、阿茲特克、印加 |
| [10-modern](./10-modern/) | 新興宗教 |
| [99-sources](./99-sources/) | bibliography |

## 階段進度

- [x] **P0** 框架建立
- [ ] **P1** 12 大宗教骨架
- [ ] **P2** 古代 / 邊緣宗教
- [ ] **P3** 現代新興
- [ ] **P4** 交叉專題
- [ ] **P5** 開放資料 / 視覺化

## 引用

若使用本資料庫內容，請註明版本與來源段。研究引用規範見各篇末 Sources 段。

## 授權

待 user 確認（建議 CC BY-SA 4.0）。

## 推送步驟

本機已 init git，但 gh CLI 未安裝。若要推 GitHub：

```bash
# 方法一：裝 gh
# (user 自決 — 本機不裝 AUR helper，gh 在 extra repo：pacman -S github-cli)

# 方法二：手動建遠端
cd ~/projects/religions-history
git remote add origin <your-github-url>
git push -u origin main
```

## 維護者

- Hang（owner）
- Claude / Talos（協作記錄用）
