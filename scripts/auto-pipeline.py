#!/usr/bin/env python
"""
Pipeline B+C orchestrator: for each scripture in a tier queue, run
translate (01-translation.md) then tag (semantic_tags/psych_tags/keywords in meta.json),
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
import pipeline_failures  # noqa: E402
import pipeline_priority  # noqa: E402
from pipeline_lock import acquire_run_lock, release_run_lock  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
TRANSLATIONS_DIR = ROOT / "translations"
OVERVIEW_DIR = ROOT / "00-overview"
STATUS_PATH = OVERVIEW_DIR / "PIPELINE_STATUS.md"
RUNTIME_PATH = ROOT / "logs" / "pipeline-runtime.json"
HALT_PATH = ROOT / "logs" / "pipeline-HALT.flag"


# ---------- status / failed bookkeeping ----------

def set_meta_status(slug: str, key: str, value: str) -> None:
    meta_p = TRANSLATIONS_DIR / slug / "meta.json"
    if not meta_p.exists():
        return
    meta = json.loads(meta_p.read_text(encoding="utf-8"))
    if meta.get(key) != value:
        meta[key] = value
        translate._atomic_write_text(
            meta_p, json.dumps(meta, ensure_ascii=False, indent=2) + "\n")


def write_status(tier: str, done: int, total: int, current: str, failure_state: dict) -> None:
    now = datetime.now(timezone.utc).astimezone().strftime("%Y-%m-%d %H:%M:%S %z")
    try:
        runtime = json.loads(RUNTIME_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        runtime = {}
    runtime_lines = ""
    if runtime.get("status") == "waiting_quota":
        chunk = runtime.get("chunk")
        total_chunks = runtime.get("chunks_total")
        chunk_text = f" chunk {chunk}/{total_chunks}" if chunk and total_chunks else ""
        runtime_lines = (f"- M3 執行狀態：**waiting_quota** — `{runtime.get('slug', current)}`"
                         f" ({runtime.get('task', '?')}{chunk_text})\n"
                         f"- 限制偵測：{runtime.get('detected_at', '?')}；下次重試：{runtime.get('next_retry_at', '?')}\n"
                         f"- 最後錯誤：`{runtime.get('last_error', '?')}`\n")
    elif runtime.get("status") == "running":
        runtime_lines = (f"- M3 執行狀態：**running** — `{runtime.get('slug', current)}`"
                         f" ({runtime.get('task', '?')})\n")
    failures = failure_state.get("failures", {})
    retryable = [slug for slug, entry in failures.items()
                 if entry.get("tier") == tier and entry.get("status") == "retryable"]
    blocked = [slug for slug, entry in failures.items()
               if entry.get("tier") == tier and entry.get("status") == "blocked"]
    priorities = pipeline_priority.priority_map()
    p0_pending = sum(
        1 for slug in translate.load_slugs_by_tier(tier)
        if priorities.get(slug) == "P0"
        and not translate.has_complete_translation(TRANSLATIONS_DIR / slug / "01-translation.md"))
    STATUS_PATH.write_text(
        f"""# Pipeline B+C 自動執行狀態

> 由 `scripts/auto-pipeline.py` 自動產生，勿手改。

- 更新時間：{now}
- 佇列 tier：**{tier}**
- 進度：**{done} / {total}** 已翻譯+標籤
- 目前處理：`{current}`
- P0 尚未完整翻譯：{p0_pending} 部
- 一般失敗待重試：{len(retryable)} 部{' — ' + ', '.join(retryable[:10]) if retryable else ''}
- 已阻塞待人工處理：{len(blocked)} 部{' — ' + ', '.join(blocked[:10]) if blocked else ''}
{runtime_lines}

流程：每部 `01-translation.md`（經文式翻譯）→ `semantic_tags`/`psych_tags`/`keywords` 回填 `meta.json`
→ 每批重生三份獨立反向索引 → commit + push。
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
    # --only prevents unrelated paths that were already staged by the user or
    # another pipeline from leaking into this batch commit.
    code, out = run_git(["commit", "--only", "-m", message, "--", *rels])
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
        OVERVIEW_DIR / "psych-tag-index.json",
        OVERVIEW_DIR / "PROGRESS.md",
        OVERVIEW_DIR / "core-manifest.md",
        OVERVIEW_DIR / "original-text-todo.md",
        STATUS_PATH,
    ]


def process_slug(slug: str, tasks: list[str], whitelist: set, psych_whitelist: set,
                 dry_run: bool) -> tuple[bool, list[Path]]:
    """Returns (ok, touched_paths)."""
    slug_dir = TRANSLATIONS_DIR / slug
    touched: list[Path] = []
    tr_role = translate.load_role("translate")
    tag_role = translate.load_role("tag")

    if "translate" in tasks:
        tr_path = slug_dir / "01-translation.md"
        if not translate.has_complete_translation(tr_path):
            ok = translate.translate_one(slug, "translate", tr_role, skip_done=True, dry_run=dry_run)
            if not ok:
                return False, touched
            if not dry_run:
                if not translate.has_complete_translation(tr_path):
                    print(f"  [error] {slug} (translate): output failed completeness check")
                    return False, touched
                set_meta_status(slug, "translation_status", "done")
                if translate.LAST_MODELS_USED:
                    set_meta_status(slug, "translation_models",
                                    "+".join(sorted(translate.LAST_MODELS_USED)))
        touched.append(tr_path)
        touched.append(slug_dir / "meta.json")

    if "tag" in tasks:
        if not translate.has_complete_translation(slug_dir / "01-translation.md"):
            print(f"  [error] {slug} (tag): translation is missing or incomplete")
            return False, touched
        ok = translate.tag_one(slug, tag_role, whitelist, psych_whitelist,
                               skip_done=True, dry_run=dry_run)
        if not ok:
            return False, touched
        touched.append(slug_dir / "meta.json")

    return True, touched


def tasks_complete(meta: dict, translation_path: Path, tasks: list[str]) -> bool:
    translation_done = translate.has_complete_translation(translation_path)
    tags_done = (meta.get("tag_status") == "done" and bool(meta.get("semantic_tags"))
                 and meta.get("psych_tag_status") == "done" and bool(meta.get("psych_tags")))
    return (("translate" not in tasks or translation_done)
            and ("tag" not in tasks or tags_done))


def count_completed(queue: list[str], tasks: list[str],
                    translations_dir: Path = TRANSLATIONS_DIR) -> int:
    completed = 0
    for slug in queue:
        meta_path = translations_dir / slug / "meta.json"
        try:
            meta = json.loads(meta_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if tasks_complete(meta, translations_dir / slug / "01-translation.md", tasks):
            completed += 1
    return completed


def build_pending(queue: list[str], tasks: list[str], failures: dict, tier: str,
                  now: datetime | None = None, translations_dir: Path = TRANSLATIONS_DIR,
                  priorities: dict[str, str] | None = None) -> list[str]:
    """Build a deterministic runnable queue; future retries and blocked items wait."""
    priorities = priorities if priorities is not None else pipeline_priority.priority_map()
    now = now or datetime.now(timezone.utc)
    rows = []
    for base_index, slug in enumerate(queue):
        meta_p = translations_dir / slug / "meta.json"
        if not meta_p.exists():
            continue
        meta = json.loads(meta_p.read_text(encoding="utf-8"))
        if tasks_complete(meta, translations_dir / slug / "01-translation.md", tasks):
            continue
        failure = failures.get(slug)
        if failure and (failure.get("status") == "blocked"
                        or not pipeline_failures.is_due(failure, now)):
            continue
        priority = pipeline_priority.priority_for(slug, tier, priorities)
        rows.append((pipeline_priority.RANK[priority], 0 if failure else 1, base_index, slug))
    rows.sort()
    return [row[-1] for row in rows]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tier", default="核心", help="tier queue (核心/次要/總集)")
    ap.add_argument("--slugs", help="comma list of explicit slugs (overrides --tier queue)")
    ap.add_argument("--limit", type=int, default=0, help="max slugs this run (0=all)")
    ap.add_argument("--batch-size", type=int, default=5, help="commit+push every N slugs")
    ap.add_argument("--tasks", default="translate,tag", help="comma list: translate,tag")
    ap.add_argument("--no-push", action="store_true", help="commit but don't push")
    ap.add_argument("--dry-run", action="store_true", help="don't call m3 / don't commit")
    ap.add_argument("--unblock", metavar="SLUG", help="reset one blocked/retryable slug for immediate retry")
    args = ap.parse_args()

    if args.unblock:
        pipeline_failures.unblock(args.unblock, TRANSLATIONS_DIR)
        print(f"[unblock] {args.unblock} is retryable now")
        return

    tasks = [t.strip() for t in args.tasks.split(",") if t.strip()]
    whitelist = translate.load_tag_whitelist()
    psych_whitelist = translate.load_psych_tag_whitelist()
    if args.slugs:
        queue = [s.strip() for s in args.slugs.split(",") if s.strip()]
    else:
        queue = translate.load_slugs_by_tier(args.tier)
    failure_state, migrated = pipeline_failures.load()
    if migrated and not args.dry_run:
        pipeline_failures.save(failure_state)
    failures = failure_state["failures"]

    # Resume filter: skip slugs already fully done
    priority_map = pipeline_priority.priority_map()
    now = datetime.now(timezone.utc)
    pending = build_pending(queue, tasks, failures, args.tier, now,
                            TRANSLATIONS_DIR, priority_map)

    total = len(queue)
    already = count_completed(queue, tasks)
    if args.limit:
        pending = pending[:args.limit]
    print(f"tier={args.tier}  queue={total}  already_done={already}  this_run={len(pending)}  tasks={tasks}")

    batch_paths: list[Path] = []
    processed = 0
    for i, slug in enumerate(pending, 1):
        if HALT_PATH.exists():
            print(f"[halt] {HALT_PATH.name} detected between slugs; stopping safely")
            break
        print(f"[{i}/{len(pending)}] {slug}")
        write_status(args.tier, already + processed, total, slug, failure_state)
        try:
            ok, touched = process_slug(slug, tasks, whitelist, psych_whitelist, args.dry_run)
        except Exception as e:  # noqa: BLE001 — never let one slug kill the run
            print(f"  [exception] {slug}: {e}")
            ok, touched = False, []
        if ok:
            processed += 1
            if slug in failures:
                failures.pop(slug, None)
                if not args.dry_run:
                    pipeline_failures.clear_failure(slug)
            batch_paths.extend(touched)
        else:
            if translate.is_waiting_quota():
                # 額度等待不是經文失敗：保留 slug/chunk，勿寫 failed、勿繼續下一部。
                write_status(args.tier, already + processed, total, slug, failure_state)
                print("[waiting_quota] M3 額度等待中；停止本輪，等待 watcher 自動從此 chunk 重跑")
                break
            if not args.dry_run:
                entry = pipeline_failures.record_failure(
                    slug, args.tier, "pipeline", "processing_failed",
                    "translation/tagging returned unsuccessful status")
                failures[slug] = entry
                print(f"  [retry] {slug}: {entry['status']} attempts={entry['attempts']} "
                      f"next={entry.get('next_retry_at')}")

        if not args.dry_run and processed and processed % args.batch_size == 0 and batch_paths:
            idx_paths = rebuild_indexes()
            write_status(args.tier, already + processed, total, slug, failure_state)
            commit_batch(batch_paths + idx_paths,
                         f"Pipeline B+C: {args.tier} 翻譯+標籤 批次 (+{len(set(batch_paths))} 檔)",
                         push=not args.no_push)
            batch_paths = []

    # final flush
    if not args.dry_run and batch_paths:
        idx_paths = rebuild_indexes()
        write_status(args.tier, already + processed, total, "(本輪完成)", failure_state)
        commit_batch(batch_paths + idx_paths,
                     f"Pipeline B+C: {args.tier} 翻譯+標籤 收尾 (processed {processed})",
                     push=not args.no_push)

    retry_delay = pipeline_failures.next_retry_delay(failure_state, args.tier)
    blocked_count = sum(1 for entry in failures.values()
                        if entry.get("tier") == args.tier and entry.get("status") == "blocked")
    print(f"\ndone: processed {processed}/{len(pending)}  retryable "
          f"{sum(1 for e in failures.values() if e.get('status') == 'retryable')}  blocked {blocked_count}")
    if retry_delay is not None and retry_delay > 0:
        print(f"[retry-wait] next ordinary retry in {int(retry_delay)}s")
    if not pending and blocked_count:
        print(f"[blocked-only] {blocked_count} blocked items require --unblock after repair")


if __name__ == "__main__":
    if not acquire_run_lock():
        sys.exit(0)
    try:
        main()
    finally:
        release_run_lock()
