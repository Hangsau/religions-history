#!/usr/bin/env python
"""
桌面狀態看板（刊版）：雙擊開一個視窗，每 30 秒自動刷新，隨時看三條 pipeline 進度。

不用開終端、不用記指令。資料計算沿用 status.py 的 helper（load_all / filled / ...），
所以這裡只管畫畫面。進度條用 Canvas 畫（非 ascii），避開 CJK 等寬對齊問題。

啟動：雙擊 狀態看板.bat（背景用 pythonw，無主控台視窗）。
或： PYTHONIOENCODING=utf-8 pythonw scripts/status_gui.py
"""

import os
import re
import subprocess
import sys
import time
import tkinter as tk
from datetime import datetime, timezone, timedelta
from pathlib import Path

import status  # 同目錄；沿用其資料 helper

REFRESH_MS = 30_000
SCRIPTS = Path(__file__).resolve().parent
PIDFILE = status.LOGS / "supervisor.pid"


def _pid_alive(pid: int) -> bool:
    """Windows：不依賴 psutil，用 OpenProcess + GetExitCodeProcess 判進程是否還在跑。"""
    try:
        import ctypes
        k = ctypes.windll.kernel32
        h = k.OpenProcess(0x1000, False, pid)  # PROCESS_QUERY_LIMITED_INFORMATION
        if not h:
            return False
        code = ctypes.c_ulong()
        k.GetExitCodeProcess(h, ctypes.byref(code))
        k.CloseHandle(h)
        return code.value == 259  # STILL_ACTIVE
    except Exception:
        return False


def ensure_supervisor() -> None:
    """刊版兼任監督：發現 supervisor 沒在跑就（無視窗、脫離本進程地）拉起來。

    用戶要求「不要額外跳黑框、讓刊版去做監視」→ 這裡用 pythonw + DETACHED_PROCESS
    + CREATE_NO_WINDOW 起 supervisor：關掉刊版不會連帶殺死管線（不重演 07-04 靜默停擺）。
    """
    try:
        if PIDFILE.exists():
            pid = int(PIDFILE.read_text(encoding="utf-8").strip() or 0)
            if pid and _pid_alive(pid):
                return  # 已有活著的 supervisor，別重複拉起（重複＝雙倍燒 M3 配額）
        pyw = Path(sys.executable).with_name("pythonw.exe")
        exe = str(pyw) if pyw.exists() else sys.executable
        flags = 0x00000008 | 0x00000200 | getattr(subprocess, "CREATE_NO_WINDOW", 0)
        subprocess.Popen(
            [exe, str(SCRIPTS / "supervise-pipeline.py"), "核心"],
            cwd=str(SCRIPTS.parent),
            env={**os.environ, "PYTHONIOENCODING": "utf-8", "PYTHONUNBUFFERED": "1"},
            creationflags=flags, close_fds=True,
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, stdin=subprocess.DEVNULL)
    except Exception:
        pass  # 拉起失敗不擋看板；停擺仍會由紅色橫幅現形


def fmt_ago(sec: float) -> str:
    if sec < 90:
        return "剛剛"
    if sec < 3600:
        return f"{int(sec / 60)} 分前"
    if sec < 86400:
        return f"{int(sec / 3600)} 時前"
    return f"{int(sec / 86400)} 天前"

# ---- 配色：departure board / NOC 監控牆（深色面板 + 琥珀/綠燈號）----
BG    = "#15181c"
PANEL = "#1e2228"
FG    = "#d7dae0"
MUTED = "#7c828c"
DONE  = "#5b8a52"   # 綠：已完成
PROG  = "#d9a441"   # 琥珀：進行中
BAD   = "#c0504d"   # 紅：停擺 / 警報
TRACK = "#2b3038"   # 進度條底槽
HEAD  = "#c8956c"   # 標題暖色

FONT   = "Microsoft JhengHei"  # CJK 安全、無 italic 偽斜
F_TITLE = (FONT, 17, "bold")
F_BIG   = (FONT, 22, "bold")
F_SEC   = (FONT, 11, "bold")
F_ROW   = (FONT, 10)
F_SMALL = (FONT, 9)


def pipeline_health(now: float) -> dict:
    """讀 PIPELINE_STATUS.md + supervisor 心跳 + 警報檔，判斷翻譯管線是否停擺。

    2026-07-04 事故：auto-pipeline 被 session 關閉靜默殺掉、無人察覺 5 小時。
    本檢查讓「狀態檔久未更新 / supervisor 報警」在看板上直接紅字現形。
    """
    root = status.LOGS.parent
    status_md = root / "00-overview" / "PIPELINE_STATUS.md"
    alert_f = status.LOGS / "pipeline-alert.txt"
    hb_f = status.LOGS / "supervisor.log"

    if alert_f.exists():
        msg = alert_f.read_text(encoding="utf-8").strip().replace("\n", "　")
        return {"color": BAD, "text": f"⚠ 管線警報：{msg}"}
    if not status_md.exists():
        return {"color": MUTED, "text": "翻譯管線：無狀態檔（未啟動過）"}

    txt = status_md.read_text(encoding="utf-8")
    m = re.search(r"進度：\*\*(\d+)\s*/\s*(\d+)", txt)
    done, total = (int(m.group(1)), int(m.group(2))) if m else (0, 0)
    cm = re.search(r"目前處理：`?([^`\n]+)`?", txt)
    current = cm.group(1).strip() if cm else "?"
    age = now - status_md.stat().st_mtime
    hb_age = now - hb_f.stat().st_mtime if hb_f.exists() else None

    if (total and done >= total) or current.startswith("(完成"):
        return {"color": DONE, "text": f"翻譯管線：核心已完成 {done}/{total}"}
    if age > 1200:  # 未完成卻 >20 分沒更新 → 疑靜默停擺
        note = f"，supervisor 心跳 {fmt_ago(hb_age)}" if hb_age is not None else "，無 supervisor 心跳"
        return {"color": BAD,
                "text": f"⚠ 翻譯管線疑停擺：停在 {done}/{total} @ {current}，"
                        f"{fmt_ago(age)}未更新{note}"}
    return {"color": DONE,
            "text": f"翻譯管線運行中：{done}/{total} @ {current}（{fmt_ago(age)}更新）"}


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

    # ---- 收集 / 下載（Pipeline A）動態 ----
    now = time.time()
    paths = list(status.TRANSLATIONS_DIR.glob("*/meta.json"))
    if paths:
        newest = max(paths, key=lambda p: p.stat().st_mtime)
        d["dl_newest"] = newest.parent.name
        d["dl_newest_ago"] = fmt_ago(now - newest.stat().st_mtime)
        d["dl_landed_30m"] = sum(1 for p in paths if now - p.stat().st_mtime < 1800)
    else:
        d["dl_newest"], d["dl_newest_ago"], d["dl_landed_30m"] = "—", "—", 0
    d["pipe"] = pipeline_health(now)

    dl_logs = list(status.LOGS.glob("pipeline-a*.log"))
    if dl_logs:
        active = max(dl_logs, key=lambda p: p.stat().st_mtime)
        d["dl_log_name"] = active.name
        d["dl_log_ago"] = fmt_ago(now - active.stat().st_mtime)
        d["dl_log_tail"] = status.log_tail(active.name)
    else:
        d["dl_log_name"], d["dl_log_ago"], d["dl_log_tail"] = "—", "—", "（無日誌）"
    return d


class Board:
    def __init__(self, root: tk.Tk):
        self.root = root
        root.title("religions-history 狀態看板")
        root.configure(bg=BG)
        root.geometry("660x800")
        root.minsize(560, 640)

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
        self.pipe = tk.Label(head, text="", bg=BG, fg=FG, font=F_SEC, anchor="w",
                             wraplength=620, justify="left")
        self.pipe.pack(fill="x", padx=18, pady=(6, 0))

        self._section(self.root, "對齊覆蓋率（欄位回填進度）")
        for label, key in [(l, k) for (k, l) in status.ALIGN_FIELDS]:
            self._bar_row(self.root, "cov:" + key, label)

        self._section(self.root, "M3 分類進度（era + genre + tags 三者齊全）")
        for t in ["核心", "次要", "總集"]:
            self._bar_row(self.root, "tier:" + t, "tier " + t)

        self._section(self.root, "收集 / 下載（Pipeline A）")
        self.dl_label = tk.Label(self.root, text="—", bg=BG, fg=FG, font=F_ROW,
                                 anchor="w", justify="left")
        self.dl_label.pack(fill="x", padx=18)
        self.dl_log = tk.Label(self.root, text="—", bg=BG, fg=MUTED, font=F_SMALL,
                               anchor="w", wraplength=600, justify="left")
        self.dl_log.pack(fill="x", padx=18)

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
        ensure_supervisor()  # 每次刷新順手確保管線活著（刊版兼監督）
        d = collect()
        ts = datetime.now(timezone(timedelta(hours=8))).strftime("%Y-%m-%d %H:%M:%S")
        self.big.config(text=f"{d['n']} 部 · {d['religions']} 宗教 · {d['mb']:.0f} MB")
        self.stamp.config(text=f"更新於 {ts} +0800　（每 30 秒自動刷新）")
        self.pipe.config(text=d["pipe"]["text"], fg=d["pipe"]["color"])

        for label, key, c, tot, pct in d["coverage"]:
            self._draw_bar("cov:" + key, c, tot, pct)
        for t, done, tot, pct in d["tiers"]:
            self._draw_bar("tier:" + t, done, tot, pct)

        self.dl_label.config(
            text=f"最新收錄：{d['dl_newest']}（{d['dl_newest_ago']}）"
                 f"　·　近 30 分 +{d['dl_landed_30m']} 部")
        self.dl_log.config(
            text=f"下載日誌 {d['dl_log_name']}（{d['dl_log_ago']}）：{d['dl_log_tail']}")

        self.tr_label.config(
            text=f"translation_status == done：{d['tr_done']} / {d['n']} 部已翻譯")
        self.cls_label.config(
            text=f"日誌已分類 {d['classify_ok']} 部\n最新：{d['classify_last']}")

        self.root.after(REFRESH_MS, self.refresh)


def main():
    ensure_supervisor()  # 開看板即確保管線在跑
    root = tk.Tk()
    Board(root)
    root.mainloop()


if __name__ == "__main__":
    main()
