# HANDOFF — religions-history

> 狀態快照。每次工作結束更新。
> 規範見 `CLAUDE.md` + `PLAN.md`。

## 當前進度

- ✅ P0 框架（PLAN / CLAUDE / README / overview / methodology）
- ✅ P1 宗教總目錄 `00-overview/religions-inventory.md`
- ✅ P2 經文總目錄 `00-overview/scriptures-inventory.md`
- ✅ P2.5 每教經文清單 `methodology/per-religion-scriptures.md`（v2 ~575 部）
- 🟡 **P3 經文下載（進行中）**：
  - ✅ 工具驗證：道德經 王弼本 81 章 verify.py PASS
  - 🟡 P3-A 道教（35 部清單，**4 部完成**）：
    - ✅ tao-te-ching 道德經 81 章 20773 bytes
    - ✅ zhuangzi 莊子 33 章 242136 bytes
    - ✅ liezi 列子 8 章 114186 bytes
    - ✅ yinfu-jing 黃帝陰符經 11 段 1766 bytes
    - 🔴 wenzi 文子 12 章 — chapter_urns 已備（8/12 預先驗證），待 ctext API 配額重置才能跑
    - 🔴 huangdi-neijing / huainanzi / baopuzi / shenxian-zhuan / taiping-jing — defer，需 chapter URN 列表（待 HTML rate limit 冷卻或 API key）
    - 🔴 guanyinzi / wenshi-zhenjing — ctext_slug 待查證
    - 🔴 zhouyi-cantong-qi / huangting-jing / taishang-ganying-pian / qingjing-jing — 可能不在 ctext.org，需 Wikisource / 道藏電子版替代來源
  - 🟡 P3-B 儒教（26 部清單，**2 部完成**）：
    - ✅ analects 論語 20 篇 65450 bytes
    - ✅ mengzi 孟子 14 篇 135591 bytes
    - 🔴 其他 24 部 — 已寫好 catalog，待 ctext API 配額重置
  - 後續 P3-C~J 詳見 `methodology/sequencing-plan.md`

## ⚠️ ctext.org 限額狀態

**未認證 IP 限額：每 24 小時 200 次 API/HTML 請求**（per ctext.org/tools/api docs）

本機 IP 已耗用完當日配額：
- HTML（ctext.org/<slug>/zh）→ 403 Forbidden
- API（api.ctext.org/gettext）→ `ERR_REQUEST_LIMIT`

**解除方法**（任一）：
1. 等 24 小時自然重置（最簡單）
2. 在 ctext.org 註冊免費帳號 + 取得 API key → 更高配額（建議）
   - 註冊：https://ctext.org/account.pl?if=en
   - API 文件：https://ctext.org/tools/api
   - 取得後加到 `scripts/download-ctext.py` 的 `headers` 或 query 字串

## 下次接手

1. 確認 ctext 配額已重置：`curl -s "https://api.ctext.org/gettext?urn=ctp:liji/da-xue" | head -c 100` → 看是否有 fulltext
2. 跑 `python scripts/download-ctext.py --religion 儒教 --all`，繼續 P3-B
3. 完成後跑 `python scripts/download-ctext.py --religion 道教 --all`，續完剩餘道教 defer 條目
4. 全綠後規劃 P3-C（漢譯佛經，CBETA 下載器待寫）

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

## 已知技術問題

- Windows console cp950 → 所有 Python 跑 `PYTHONIOENCODING=utf-8 python ...`
- ctext.org API 對 multi-chapter book 的 top URN 部分要 auth（`ERR_REQUIRES_AUTHENTICATION`）
  - 解法：catalog 加 `chapter_urns` 列表（個別 chapter URN 不需 auth）
  - 已套用於：zhuangzi（33 章）、liezi（8 章）、wenzi（12 章）
- ctext API top URN 回 fulltext 時，每段 = 一章（DDJ 81 章 case），腳本已自動偵測
