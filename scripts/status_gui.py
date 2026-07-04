#!/usr/bin/env python
"""
桌面狀態看板（刊版）：雙擊開一個視窗，每 30 秒自動刷新，隨時看三條 pipeline 進度。

不用開終端、不用記指令。資料計算沿用 status.py 的 helper（load_all / filled / ...），
所以這裡只管畫畫面。進度條用 Canvas 畫（非 ascii），避開 CJK 等寬對齊問題。

啟動：雙擊 狀態看板.bat（背景用 pythonw，無主控台視窗）。
或： PYTHONIOENCODING=utf-8 pythonw scripts/status_gui.py
"""

import json
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
HALT = status.LOGS / "pipeline-HALT.flag"  # 存在即人工暫停：刊版不復活 supervisor


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
        if HALT.exists():
            return  # 人工暫停中（如等 MiniMax 配額重置），不復活管線
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


ACTION_ZH = {"translate": "經文翻譯", "tag": "語義標籤", "annotate": "白話註釋"}

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
    """讀 PIPELINE_STATUS.md + supervisor-run.log + 警報檔，判斷翻譯管線是否真停擺。

    2026-07-04 事故：auto-pipeline 被 session 關閉靜默殺掉、無人察覺 5 小時。
    但活性必須以 **chunk 級 run.log** 為準——PIPELINE_STATUS.md 每部經典才更新一次，
    大部經典（如 sn7-brahmana 17 chunk ≈ 30+ 分）跑到一半就會被誤判停擺（假警報）；
    supervisor 心跳只在「兩輪之間」跳，長 run 全程不跳，也不能當活性訊號。
    run.log 每個 chunk（~100 秒）就寫一行，才是真正的心跳。
    """
    root = status.LOGS.parent
    status_md = root / "00-overview" / "PIPELINE_STATUS.md"
    alert_f = status.LOGS / "pipeline-alert.txt"
    run_log = status.LOGS / "supervisor-run.log"

    if HALT.exists():
        msg = HALT.read_text(encoding="utf-8").strip().replace("\n", "　") or "人工暫停中"
        return {"color": PROG, "text": f"⏸ 翻譯管線人工暫停中（刪除 pipeline-HALT.flag 即恢復）：{msg}"}
    if alert_f.exists():
        msg = alert_f.read_text(encoding="utf-8").strip().replace("\n", "　")
        return {"color": BAD, "text": f"⚠ 管線警報（supervisor 已報警並停手）：{msg}"}
    if not status_md.exists():
        return {"color": MUTED, "text": "翻譯管線：無狀態檔（未啟動過）"}

    txt = status_md.read_text(encoding="utf-8")
    m = re.search(r"進度：\*\*(\d+)\s*/\s*(\d+)", txt)
    done, total = (int(m.group(1)), int(m.group(2))) if m else (0, 0)
    cm = re.search(r"目前處理：`?([^`\n]+)`?", txt)
    current = cm.group(1).strip() if cm else "?"
    rm = re.search(r"失敗待重試：\*{0,2}(\d+)", txt)
    retry = int(rm.group(1)) if rm else 0
    base = {"done": done, "total": total, "current": current, "retry": retry}

    if (total and done >= total) or current.startswith("(完成"):
        return {**base, "color": DONE, "text": f"翻譯管線：核心已完成 {done}/{total}"}

    # 活性 = 最新工作訊號的年齡（run.log 每 chunk 更新，遠比 status.md 靈敏）。
    # 只有連 chunk 級都靜止才算真停擺。單次 M3 逾時上限 600 秒 + 部間 git，
    # 正常最壞間隔 <約 12 分；門檻放 20 分，零假警報。
    status_age = now - status_md.stat().st_mtime
    run_age = (now - run_log.stat().st_mtime) if run_log.exists() else status_age
    live_age = min(status_age, run_age)
    STALL_SECS = 1200

    if live_age > STALL_SECS:
        return {**base, "color": BAD,
                "text": f"⚠ 翻譯管線疑停擺：停在 {done}/{total} @ {current}，"
                        f"chunk 級 {fmt_ago(live_age)}無動作"}
    return {**base, "color": DONE,
            "text": f"翻譯管線運行中：{done}/{total} @ {current}"
                    f"（chunk {fmt_ago(run_age)}活動）"}


def translation_activity(now: float) -> dict:
    """解析 supervisor-run.log，回傳翻譯管線的即時動作：
    正在翻哪部、做什麼（翻譯/標籤）、第幾 chunk、用哪家模型、本次速度。
    看板據此顯示『現在正在做什麼』，直接回答『是不是沒在動』。
    """
    d = {"current": None, "name": None, "idx": None, "run_total": None,
         "action": None, "chunk": None, "provider": "—", "fallback_active": False,
         "fallbacks": 0, "errors": 0, "done_run": 0, "pace_hr": None,
         "eta_h": None, "last_ago": None, "last_done": None}
    run_log = status.LOGS / "supervisor-run.log"
    if not run_log.exists():
        return d
    try:
        lines = [l for l in run_log.read_text(encoding="utf-8", errors="replace").splitlines()
                 if l.strip()]
    except OSError:
        return d
    d["last_ago"] = fmt_ago(now - run_log.stat().st_mtime)

    # 取最後一個 run 區塊（避開上一輪殘留）
    start_idx, run_start = 0, None
    for i, l in enumerate(lines):
        if "supervisor run @" in l:
            start_idx = i
            tm = re.search(r"@ ([\d\-]{10} [\d:]{8}(?:\.\d+)?[+\-]\d{2}:\d{2})", l)
            if tm:
                try:
                    run_start = datetime.fromisoformat(tm.group(1)).timestamp()
                except ValueError:
                    run_start = None
    block = lines[start_idx:]

    for l in reversed(block):
        mm = re.match(r"\[(\d+)/(\d+)\]\s+(\S+)", l)
        if mm:
            d["idx"], d["run_total"], d["current"] = int(mm.group(1)), int(mm.group(2)), mm.group(3)
            break
    for l in reversed(block):
        mm = re.search(r"\[chunk (\d+)/(\d+)\]\s+\S+\s+\((\w+)\)", l)
        if mm:
            d["chunk"], d["action"] = f"{mm.group(1)}/{mm.group(2)}", mm.group(3)
            break
    for l in reversed(block):
        mm = re.search(r"\[done\]\s+(\S+)\s+\((\w+)\)", l)
        if mm:
            d["last_done"] = f"{mm.group(1)}（{ACTION_ZH.get(mm.group(2), mm.group(2))}）"
            break

    d["fallbacks"] = sum(1 for l in block if re.search(r"\[model\]\s+\S+\s+\(fallback\)", l))
    d["errors"] = sum(1 for l in block if "[error]" in l)
    d["done_run"] = sum(1 for l in block if re.search(r"\[done\]\s+\S+\s+\(translate\)", l))

    # 供應商：解析 translate.py 印的 `[model] <name> (<role>)` marker（唯一真相源，不寫死 model 名）。
    # 抓最後一個 marker → 顯示現用 model；role==fallback 時看板紅字提醒在燒備援。
    for l in reversed(block):
        mm = re.search(r"\[model\]\s+(\S+)\s+\((primary|fallback)\)", l)
        if mm:
            d["provider"] = mm.group(1)
            d["fallback_active"] = (mm.group(2) == "fallback")
            break

    # 速度 + ETA：本次 run 已翻部數 / 已耗時
    if run_start and d["done_run"] > 0:
        elapsed_h = (now - run_start) / 3600
        if elapsed_h > 0:
            d["pace_hr"] = d["done_run"] / elapsed_h

    # 當前 slug → 中文名
    if d["current"]:
        mp = status.TRANSLATIONS_DIR / d["current"] / "meta.json"
        if mp.exists():
            try:
                d["name"] = json.loads(mp.read_text(encoding="utf-8")).get("name_zh")
            except (OSError, json.JSONDecodeError):
                pass
    return d


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

    # ---- 翻譯即時動作（Pipeline B/C）----
    act = translation_activity(now)
    total, done, pace = d["pipe"].get("total"), d["pipe"].get("done"), act["pace_hr"]
    if total and done is not None and pace and done < total:
        act["eta_h"] = (total - done) / pace
    act["retry"] = d["pipe"].get("retry", 0)
    d["act"] = act

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
        root.geometry("680x900")
        root.minsize(560, 700)

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
                             wraplength=640, justify="left")
        self.pipe.pack(fill="x", padx=18, pady=(6, 0))

        self._section(self.root, "翻譯管線 · 現在正在做什麼")
        self.act_now = tk.Label(self.root, text="—", bg=BG, fg=PROG, font=(FONT, 12, "bold"),
                                anchor="w", wraplength=640, justify="left")
        self.act_now.pack(fill="x", padx=18)
        self.act_do = tk.Label(self.root, text="—", bg=BG, fg=FG, font=F_ROW,
                               anchor="w", wraplength=640, justify="left")
        self.act_do.pack(fill="x", padx=18, pady=(2, 0))
        self.act_meta = tk.Label(self.root, text="—", bg=BG, fg=MUTED, font=F_SMALL,
                                 anchor="w", wraplength=640, justify="left")
        self.act_meta.pack(fill="x", padx=18, pady=(2, 0))

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

    def _draw_activity(self, a: dict):
        """畫『現在正在翻什麼、做什麼』三行：正在處理 / 動作+模型 / 速度+ETA+異常。"""
        if not a.get("current"):
            self.act_now.config(text="目前無即時動作（批次間隔中，或管線未啟動）", fg=MUTED)
            self.act_do.config(text="—")
            last = f"最後動作 {a['last_ago']}" if a.get("last_ago") else ""
            self.act_meta.config(text=last)
            return

        name = a["current"] + (f"　·　{a['name']}" if a.get("name") else "")
        seq = f"（第 {a['idx']}/{a['run_total']} 部）" if a.get("idx") else ""
        self.act_now.config(text=f"正在處理：{name} {seq}", fg=PROG)

        act_zh = ACTION_ZH.get(a.get("action"), a.get("action") or "—")
        chunk = f"　·　chunk {a['chunk']}" if a.get("chunk") else ""
        # 退到備援 model 時紅字提醒（主力失敗、正在燒 fallback）
        prov = a.get("provider") or "—"
        self.act_do.config(text=f"動作：{act_zh}{chunk}　·　模型：{prov}",
                           fg=BAD if a.get("fallback_active") else FG)

        pace = f"{a['pace_hr']:.1f} 部/時" if a.get("pace_hr") else "計算中"
        eta = ""
        if a.get("eta_h"):
            h = a["eta_h"]
            eta = f"　·　預估剩餘 {h:.1f} 時" if h >= 1 else f"　·　預估剩餘 {h*60:.0f} 分"
        extra = []
        if a.get("fallbacks"):
            extra.append(f"本次退備援 {a['fallbacks']} 次")
        if a.get("errors"):
            extra.append(f"錯誤 {a['errors']}")
        if a.get("retry"):
            extra.append(f"待重試 {a['retry']} 部")
        if a.get("last_done"):
            extra.append(f"最近完成 {a['last_done']}")
        last = f"最後動作 {a['last_ago']}" if a.get("last_ago") else ""
        tail = ("　·　" + "　·　".join(extra)) if extra else ""
        self.act_meta.config(text=f"速度 {pace}{eta}　·　{last}{tail}")

    def refresh(self):
        ensure_supervisor()  # 每次刷新順手確保管線活著（刊版兼監督）
        d = collect()
        ts = datetime.now(timezone(timedelta(hours=8))).strftime("%Y-%m-%d %H:%M:%S")
        self.big.config(text=f"{d['n']} 部 · {d['religions']} 宗教 · {d['mb']:.0f} MB")
        self.stamp.config(text=f"更新於 {ts} +0800　（每 30 秒自動刷新）")
        self.pipe.config(text=d["pipe"]["text"], fg=d["pipe"]["color"])
        self._draw_activity(d["act"])

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
