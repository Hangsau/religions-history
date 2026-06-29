# HANDOFF — religions-history

> 狀態快照。每次工作結束更新。
> 規範見 `CLAUDE.md` + `PLAN.md`。

## 當前進度

- ✅ P0 框架（PLAN / CLAUDE / README / overview / methodology）
- ✅ P1 宗教總目錄 `00-overview/religions-inventory.md`
- ✅ P2 經文總目錄 `00-overview/scriptures-inventory.md`
- ✅ P2.5 每教經文清單 `methodology/per-religion-scriptures.md`（v2 ~575 部）
- 🟡 **P3 經文下載（進行中）**：按宗教逐教深做，工具難度由低到高
  - ✅ 工具驗證：道德經 王弼本 81 章 20790 bytes，verify.py PASS
  - 🟡 P3-A 道教 — 卡 ctext.org IP rate-limit，背景 watcher 等冷卻；catalog 18 部待跑
  - 🟡 P3-B 儒教 — catalog 26 部已建，待 P3-A 完
  - P3-C 漢譯佛經（~60 部，CBETA）— 待
  - 後續 P3-D~J 詳見 `methodology/sequencing-plan.md` 待補表

## ctext.org rate limit 注意

抓 zhuangzi 36 個子章節後被 ctext.org IP 級 403，base UA 換瀏覽器 UA 仍擋。
腳本已加 5 次指數 backoff（30s 起跳，最高 480s），但等 IP rate limit 自然冷卻較有效。
規則：跑 `--religion 道教` 時用更大 `SLEEP_BETWEEN_REQUESTS`（目前 3s）；
若仍被擋，考慮註冊 ctext.org API key（個人使用免費）改用 `https://api.ctext.org/` endpoints。

## 工作流（P3 階段）

1. 對某宗教，按 `methodology/per-religion-scriptures.md` 取核心 + 次要清單
2. 逐部跑 `python scripts/download-ctext.py --slug <slug>`（或對應來源的下載器）
3. 跑 `python scripts/verify.py --slug <slug>` → PASS 才 commit
4. 每 5 部 push 一次；該宗教全綠才轉下宗教
5. 大型總集（道藏 5305 卷 / 大藏經 / 十三經注疏）獨立排到 P4，不卡 P3

## m3 派工原則（見 `tools/m3-executor-role.md`）

- m3 只 invoke 既有 script，不寫 logic
- 驗證在 Claude 這層，`verify.py` PASS/FAIL 不商量
- 1 W = 1 部，spec 明訂 URL / 預期章節數 / 檔名 / cmd
- m3 填的 metadata 全部待驗，verify.py 蓋過 m3 自填值

## 下次接手

讀本檔 → 跑 `python scripts/verify.py --all` 看整批狀態 → 進「當前進度」最頂的待辦。

## 已知問題

- ctext.org legacy API 失效（302 → /tools/api docs）→ 改用 HTML 爬蟲，已驗證 81 章解析正確
- ctext.org 不同經文結構不同（單頁 vs 多子頁），下載器需自動偵測
- Windows console cp950 → 所有 Python 跑 `PYTHONIOENCODING=utf-8 python ...`
