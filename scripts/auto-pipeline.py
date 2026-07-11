#!/usr/bin/env python
"""
Pipeline B+C orchestrator: for each scripture in a tier queue, run
translate (01-translation.md) then tag (semantic_tags/keywords in meta.json),
rebuild reverse indexes, commit + push per batch, refresh status file.

Design goals:
    - Idempotent / resumable: --skip-done skips slugs already translated + tagged,
      so re-launching after laptop sleep continues where it left off.
    - Fault-tolerant: a failed slug goes to failed.json and the loop continues.
    - Safe git: only `git add` the specific paths this run touched (never -A),
      `git pull --rebase` before push so it coexists with Pipeline A collection.
    - No Claude quota: translation/tagging run on MiniMax-M3 (monthly sub) via translate.py.

Usage:
    # Small-batch validation: 3 core scriptures, don't push
    python scripts/auto-pipeline.py --tier 核心 --limit 3 --no-push

    # Full autonomous run over all core scriptures
    python scripts/auto-pipeline.py --tier 核心

    # Resume (skips already done)
    python scripts/auto-pipeline.py --tier 核心   # --skip-done is default
"""

import argparse
import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import translate  # noqa: E402  (same-dir module)

ROOT = Path(__file__).resolve().parent.parent
TRANSLATIONS_DIR = ROOT / "translations"
OVERVIEW_DIR = ROOT / "00-overview"
FAILED_PATH = ROOT / "logs" / "pipeline-failed.json"
STATUS_PATH = OVERVIEW_DIR / "PIPELINE_STATUS.md"


# ---------- status / failed bookkeeping ----------

def load_failed() -> dict:
    if FAILED_PATH.exists():
        try:
            return json.loads(FAILED_PATH.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return {}
    return {}


def save_failed(failed: dict) -> None:
    FAILED_PATH.parent.mkdir(exist_ok=True)
    FAILED_PATH.write_text(json.dumps(failed, ensure_ascii=False, indent=2) + "\n",
                           encoding="utf-8", newline="\n")


def set_meta_status(slug: str, key: str, value: str) -> None:
    meta_p = TRANSLATIONS_DIR / slug / "meta.json"
    if not meta_p.exists():
        return
    meta = json.loads(meta_p.read_text(encoding="utf-8"))
    if meta.get(key) != value:
        meta[key] = value
        meta_p.write_text(json.dumps(meta, ensure_ascii=False, indent=2) + "\n",
                          encoding="utf-8", newline="\n")


def write_status(tier: str, done: int, total: int, current: str, failed: dict) -> None:
    now = datetime.now(timezone.utc).astimezone().strftime("%Y-%m-%d %H:%M:%S %z")
    STATUS_PATH.write_text(
        f"""# Pipeline B+C 自動執行狀態

> 由 `scripts/auto-pipeline.py` 自動產生，勿手改。

- 更新時間：{now}
- 佇列 tier：**{tier}**
- 進度：**{done} / {total}** 已翻譯+標籤
- 目前處理：`{current}`
- 失敗待重試：{len(failed)} 部{' — ' + ', '.join(list(failed)[:10]) if failed else ''}

流程：每部 `01-translation.md`（經文式翻譯）→ `semantic_tags`/`keywords` 回填 `meta.json`
→ 每批重生 `tag-index.json`/`keyword-index.json` → commit + push。
""", encoding="utf-8", newline="\n")


# ---------- git ----------

def run_git(args: list[str]) -> tuple[int, str]:
    r = subprocess.run(["git", *args], cwd=ROOT, capture_output=True,
                       text=True, encoding="utf-8", errors="replace",
                       creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
    return r.returncode, ((r.stdout or "") + (r.stderr or "")).strip()


def commit_batch(paths: list[Path], message: str, push: bool) -> None:
    rels = [str(p.relative_to(ROOT)) for p in paths if p.exists()]
    if not rels:
        return
    run_git(["add", "--", *rels])
    code, out = run_git(["commit", "-m", message])
    if code != 0:
        if "nothing to commit" in out:
            return
        print(f"  [git] commit failed: {out[:200]}")
        return
    print(f"  [git] committed {len(rels)} paths")
    if not push:
        return
    run_git(["pull", "--rebase"])
    for attempt in range(3):
        code, out = run_git(["push"])
        if code == 0:
            print("  [git] pushed")
            return
        print(f"  [git] push attempt {attempt + 1} failed: {out[:120]}")
        run_git(["pull", "--rebase"])
    print("  [git] push failed after 3 tries — local commits kept, continuing")


# ---------- main loop ----------

def rebuild_indexes() -> list[Path]:
    child_env = os.environ.copy()
    child_env["PYTHONIOENCODING"] = "utf-8"
    # audit-core last: it reads meta/text_role that this batch just updated, so its
    # reports (core-manifest / original-text-todo) never go stale between runs.
    for script in ("build-tag-index.py", "track-progress.py", "audit-core.py"):
        subprocess.run([sys.executable, str(ROOT / "scripts" / script)],
                       cwd=ROOT, capture_output=True, text=True,
                       encoding="utf-8", errors="replace", env=child_env,
                       creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
    return [
        OVERVIEW_DIR / "tag-index.json",
        OVERVIEW_DIR / "keyword-index.json",
        OVERVIEW_DIR / "PROGRESS.md",
        OVERVIEW_DIR / "core-manifest.md",
        OVERVIEW_DIR / "original-text-todo.md",
        STATUS_PATH,
    ]


def process_slug(slug: str, tasks: list[str], whitelist: set, dry_run: bool) -> tuple[bool, list[Path]]:
    """Returns (ok, touched_paths)."""
    slug_dir = TRANSLATIONS_DIR / slug
    touched: list[Path] = []
    tr_role = translate.load_role("translate")
    tag_role = translate.load_role("tag")

    if "translate" in tasks:
        tr_path = slug_dir / "01-translation.md"
        if not (tr_path.exists() and tr_path.stat().st_size > 100):
            ok = translate.translate_one(slug, "translate", tr_role, skip_done=True, dry_run=dry_run)
            if not ok:
                return False, touched
            if not dry_run:
                set_meta_status(slug, "translation_status", "done")
                if translate.LAST_MODELS_USED:
                    set_meta_status(slug, "translation_models",
                                    "+".join(sorted(translate.LAST_MODELS_USED)))
        touched.append(tr_path)
        touched.append(slug_dir / "meta.json")

    if "tag" in tasks:
        ok = translate.tag_one(slug, tag_role, whitelist, skip_done=True, dry_run=dry_run)
        if not ok:
            return False, touched
        touched.append(slug_dir / "meta.json")

    return True, touched


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tier", default="核心", help="tier queue (核心/次要/總集)")
    ap.add_argument("--slugs", help="comma list of explicit slugs (overrides --tier queue)")
    ap.add_argument("--limit", type=int, default=0, help="max slugs this run (0=all)")
    ap.add_argument("--batch-size", type=int, default=5, help="commit+push every N slugs")
    ap.add_argument("--tasks", default="translate,tag", help="comma list: translate,tag")
    ap.add_argument("--no-push", action="store_true", help="commit but don't push")
    ap.add_argument("--dry-run", action="store_true", help="don't call m3 / don't commit")
    args = ap.parse_args()

    tasks = [t.strip() for t in args.tasks.split(",") if t.strip()]
    whitelist = translate.load_tag_whitelist()
    if args.slugs:
        queue = [s.strip() for s in args.slugs.split(",") if s.strip()]
    else:
        queue = translate.load_slugs_by_tier(args.tier)
    failed = load_failed()

    # Resume filter: skip slugs already fully done
    pending = []
    for slug in queue:
        meta_p = TRANSLATIONS_DIR / slug / "meta.json"
        if not meta_p.exists():
            continue
        meta = json.loads(meta_p.read_text(encoding="utf-8"))
        tr_done = (TRANSLATIONS_DIR / slug / "01-translation.md").exists()
        tag_done = meta.get("tag_status") == "done" and meta.get("semantic_tags")
        need_tr = "translate" in tasks and not tr_done
        need_tag = "tag" in tasks and not tag_done
        if need_tr or need_tag:
            pending.append(slug)

    total = len(queue)
    already = total - len(pending)
    if args.limit:
        pending = pending[:args.limit]
    print(f"tier={args.tier}  queue={total}  already_done={already}  this_run={len(pending)}  tasks={tasks}")

    batch_paths: list[Path] = []
    processed = 0
    for i, slug in enumerate(pending, 1):
        print(f"[{i}/{len(pending)}] {slug}")
        write_status(args.tier, already + processed, total, slug, failed)
        try:
            ok, touched = process_slug(slug, tasks, whitelist, args.dry_run)
        except Exception as e:  # noqa: BLE001 — never let one slug kill the run
            print(f"  [exception] {slug}: {e}")
            ok, touched = False, []
        if ok:
            processed += 1
            failed.pop(slug, None)
            batch_paths.extend(touched)
        else:
            failed[slug] = {"at": datetime.now(timezone.utc).isoformat(), "tier": args.tier}
            if not args.dry_run:
                save_failed(failed)

        if not args.dry_run and processed and processed % args.batch_size == 0 and batch_paths:
            idx_paths = rebuild_indexes()
            write_status(args.tier, already + processed, total, slug, failed)
            commit_batch(batch_paths + idx_paths,
                         f"Pipeline B+C: {args.tier} 翻譯+標籤 批次 (+{len(set(batch_paths))} 檔)",
                         push=not args.no_push)
            batch_paths = []

    # final flush
    if not args.dry_run and batch_paths:
        idx_paths = rebuild_indexes()
        write_status(args.tier, already + processed, total, "(完成)", failed)
        commit_batch(batch_paths + idx_paths,
                     f"Pipeline B+C: {args.tier} 翻譯+標籤 收尾 (processed {processed})",
                     push=not args.no_push)

    print(f"\ndone: processed {processed}/{len(pending)}  failed {len(failed)}")
    if failed:
        print(f"failed slugs: {', '.join(list(failed)[:20])}")


if __name__ == "__main__":
    main()
