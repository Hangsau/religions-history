# Religions History — 宗教史研究專案

> 跨時空、跨文化的世界宗教結構化整理。
> 啟動：2026-06-29

## 目標

建立一份可引用、可延伸的宗教史資料庫，覆蓋：

- **時間**：史前 → 現代
- **地理**：兩河 / 埃及 / 印度 / 中國 / 日韓 / 亞伯拉罕 / 非洲 / 大洋洲 / 美洲
- **維度**：起源、神話、教義、儀式、組織、經典、傳播、當代現況

**不涉入**：宗教比較優劣、護教 / 破教、單一立場宣揚。

完整計畫見 [`PLAN.md`](./PLAN.md)。

## 技術棧

- **內容格式**：Markdown（GitHub Flavored）
- **版本控制**：git（本地 repo，user 後續可推 GitHub/GitLab）
- **引用管理**：行內 markdown link + Sources 段
- **未來規劃**：Hugo 站（Astro / Docusaurus 評估中）

## 內容來源

- A 級：學術專著、Stanford Encyclopedia of Philosophy、Encyclopaedia Britannica
- B 級：大學公開課、博物館資料
- C 級：中文百科 — 僅 cross-check
- D 級：教內自述 — 標明「教內視角」

詳見 PLAN.md §3.1。

## 維護機制

- 每完成一個 P 階段 → git commit
- 每篇交付前 → 跑 PLAN.md §6 自檢
- 重大更新 → 更新 `~/.claude/memory/INDEX.md` 專案地圖
- 反模式見 PLAN.md §7

## 目錄結構

```
religions-history/
├── CLAUDE.md              ← 本檔
├── PLAN.md                ← 完整研究計畫
├── README.md              ← 對外說明
├── 00-overview/           ← 總覽、時間軸、分類表
├── 01-prehistoric-mesopotamia/  ← 蘇美、巴比倫、波斯
├── 02-egypt/              ← 古埃及
├── 03-india/              ← 印度教、佛教、耆那、錫克
├── 04-china/              ← 儒、道、佛、民間
├── 05-japan-korea/        ← 神道、韓傳佛教
├── 06-abrahamic/          ← 猶太、基督、伊斯蘭、巴哈伊
├── 07-africa/             ← 非洲傳統 + 衣索比亞正教
├── 08-oceania/            ← 大洋洲原住民
├── 09-americas/           ← 瑪雅、阿茲特克、印加、北美
├── 10-modern/             ← 新興宗教
└── 99-sources/            ← bibliography
```

## 已知問題

- gh CLI 未安裝，無法直接 push GitHub（見 README.md「推送步驟」）
- P0 完成後待 user 確認 P1 優先順序

## Anti-pattern

（與 PLAN.md §7 同步）

- 單一立場來源引用
- 簡轉繁混用
- 一篇塞整個宗教（>3000 行）— 拆 sub-page
- 用 emoji 緩衝內容
- 「我不確定」當免責符
