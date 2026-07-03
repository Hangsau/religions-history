#!/usr/bin/env python
"""
桌面狀態看板（刊版）：雙擊開一個視窗，每 30 秒自動刷新，隨時看三條 pipeline 進度。

不用開終端、不用記指令。資料計算沿用 status.py 的 helper（load_all / filled / ...），
所以這裡只管畫畫面。進度條用 Canvas 畫（非 ascii），避開 CJK 等寬對齊問題。

啟動：雙擊 狀態看板.bat（背景用 pythonw，無主控台視窗）。
或： PYTHONIOENCODING=utf-8 pythonw scripts/status_gui.py
"""

import tkinter as tk
from datetime import datetime, timezone, timedelta

import status  # 同目錄；沿用其資料 helper

REFRESH_MS = 30_000

# ---- 配色：departure board / NOC 監控牆（深色面板 + 琥珀/綠燈號）----
BG    = "#15181c"
PANEL = "#1e2228"
FG    = "#d7dae0"
MUTED = "#7c828c"
DONE  = "#5b8a52"   # 綠：已完成
PROG  = "#d9a441"   # 琥珀：進行中
TRACK = "#2b3038"   # 進度條底槽
HEAD  = "#c8956c"   # 標題暖色

FONT   = "Microsoft JhengHei"  # CJK 安全、無 italic 偽斜
F_TITLE = (FONT, 17, "bold")
F_BIG   = (FONT, 22, "bold")
F_SEC   = (FONT, 11, "bold")
F_ROW   = (FONT, 10)
F_SMALL = (FONT, 9)


def collect() -> dict:
    """跑一次全庫掃描，回傳畫面需要的所有數字。"""
    metas = status.load_all()
    n = len(metas) or 1
    d = {"n": len(metas)}
    d["religions"] = len({m.get("religion") for m in metas})
    d["mb"] = sum(m.get("size_bytes") or 0 for m in metas) / 1024 / 1024

    d["coverage"] = []
    for key, label in status.ALIGN_FIELDS:
        c = sum(1 for m in metas if status.filled(m.get(key)))
        d["coverage"].append((label, key, c, len(metas), 100 * c / n))

    tiers = []
    from collections import Counter
    tot = Counter(m.get("tier") for m in metas)
    for t in ["核心", "次要", "總集"]:
        tt = tot.get(t, 0)
        done = sum(1 for m in metas if m.get("tier") == t
                   and status.filled(m.get("era")) and status.filled(m.get("genre"))
                   and status.filled(m.get("semantic_tags")))
        tiers.append((t, done, tt, 100 * done / tt if tt else 0))
    d["tiers"] = tiers

    d["tr_done"] = sum(1 for m in metas if m.get("translation_status") == "done")
    d["classify_ok"] = status.log_ok_count("classify-core.log")
    d["classify_last"] = status.log_tail("classify-core.log")
    return d


class Board:
    def __init__(self, root: tk.Tk):
        self.root = root
        root.title("religions-history 狀態看板")
        root.configure(bg=BG)
        root.geometry("660x720")
        root.minsize(560, 600)

        self.rows = {}   # key -> (canvas, count_label)
        self._build_static()
        self.refresh()

    def _section(self, parent, text):
        tk.Label(parent, text=text, bg=BG, fg=HEAD, font=F_SEC,
                 anchor="w").pack(fill="x", padx=18, pady=(14, 2))

    def _bar_row(self, parent, key, label):
        row = tk.Frame(parent, bg=BG)
        row.pack(fill="x", padx=18, pady=2)
        tk.Label(row, text=label, bg=BG, fg=FG, font=F_ROW,
                 width=16, anchor="w").pack(side="left")
        cv = tk.Canvas(row, height=16, bg=TRACK, highlightthickness=0)
        cv.pack(side="left", fill="x", expand=True, padx=(4, 8))
        cnt = tk.Label(row, text="", bg=BG, fg=MUTED, font=F_SMALL,
                       width=14, anchor="e")
        cnt.pack(side="left")
        self.rows[key] = (cv, cnt)

    def _build_static(self):
        head = tk.Frame(self.root, bg=BG)
        head.pack(fill="x", pady=(14, 0))
        tk.Label(head, text="religions-history 刊版", bg=BG, fg=HEAD,
                 font=F_TITLE, anchor="w").pack(fill="x", padx=18)
        self.big = tk.Label(head, text="—", bg=BG, fg=FG, font=F_BIG, anchor="w")
        self.big.pack(fill="x", padx=18)
        self.stamp = tk.Label(head, text="", bg=BG, fg=MUTED, font=F_SMALL, anchor="w")
        self.stamp.pack(fill="x", padx=18)

        self._section(self.root, "對齊覆蓋率（欄位回填進度）")
        for label, key in [(l, k) for (k, l) in status.ALIGN_FIELDS]:
            self._bar_row(self.root, "cov:" + key, label)

        self._section(self.root, "M3 分類進度（era + genre + tags 三者齊全）")
        for t in ["核心", "次要", "總集"]:
            self._bar_row(self.root, "tier:" + t, "tier " + t)

        self._section(self.root, "翻譯進度")
        self.tr_label = tk.Label(self.root, text="—", bg=BG, fg=FG,
                                 font=F_ROW, anchor="w")
        self.tr_label.pack(fill="x", padx=18)

        self._section(self.root, "背景分類管線（classify）")
        self.cls_label = tk.Label(self.root, text="—", bg=BG, fg=FG, font=F_SMALL,
                                  anchor="w", wraplength=600, justify="left")
        self.cls_label.pack(fill="x", padx=18)

        foot = tk.Frame(self.root, bg=BG)
        foot.pack(side="bottom", fill="x", pady=10)
        tk.Button(foot, text="立即重新整理", command=self.refresh,
                  bg=PANEL, fg=FG, font=F_SMALL, relief="flat",
                  activebackground=TRACK, activeforeground=FG,
                  padx=12, pady=4).pack()

    def _draw_bar(self, key, count, total, pct):
        cv, cnt = self.rows[key]
        cv.delete("all")
        w = cv.winfo_width() or 360
        fill = DONE if pct >= 99.5 else PROG
        fw = int(w * min(pct, 100) / 100)
        if fw > 0:
            cv.create_rectangle(0, 0, fw, 16, fill=fill, width=0)
        cv.create_text(6, 8, text=f"{pct:.0f}%", anchor="w",
                       fill="#12151a" if fw > 30 else MUTED, font=F_SMALL)
        cnt.config(text=f"{count} / {total}")

    def refresh(self):
        d = collect()
        ts = datetime.now(timezone(timedelta(hours=8))).strftime("%Y-%m-%d %H:%M:%S")
        self.big.config(text=f"{d['n']} 部 · {d['religions']} 宗教 · {d['mb']:.0f} MB")
        self.stamp.config(text=f"更新於 {ts} +0800　（每 30 秒自動刷新）")

        for label, key, c, tot, pct in d["coverage"]:
            self._draw_bar("cov:" + key, c, tot, pct)
        for t, done, tot, pct in d["tiers"]:
            self._draw_bar("tier:" + t, done, tot, pct)

        self.tr_label.config(
            text=f"translation_status == done：{d['tr_done']} / {d['n']} 部已翻譯")
        self.cls_label.config(
            text=f"日誌已分類 {d['classify_ok']} 部\n最新：{d['classify_last']}")

        self.root.after(REFRESH_MS, self.refresh)


def main():
    root = tk.Tk()
    Board(root)
    root.mainloop()


if __name__ == "__main__":
    main()
