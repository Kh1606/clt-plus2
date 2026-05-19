"""One-shot Supabase cleanup: delete rows from notices_v2 whose
(region, sub_entity) is NOT one of the 76 v2 pairs in src/data/regions.json.

These orphaned rows come from the very first scrape (before the allowlist
filter + metadata reconciler landed). The v2-only scraper will never
touch them again, so they sit forever as stale data.

Idempotent — re-running deletes 0 rows.

Loads SUPABASE_URL + SUPABASE_SECRET_KEY from C:/Users/Alex/CLT+/.env
(the clt-plus repo's .env, which already holds the v2 credentials).
"""
from __future__ import annotations
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REGIONS = ROOT / "src" / "data" / "regions.json"
CLT_PLUS_ENV = Path(r"C:\Users\Alex\CLT+\.env")


def _load_env() -> tuple[str, str]:
    try:
        from dotenv import load_dotenv
        if CLT_PLUS_ENV.exists():
            load_dotenv(CLT_PLUS_ENV)
    except ImportError:
        pass
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_SECRET_KEY")
    if not url or not key:
        print(f"ERROR: SUPABASE_URL and SUPABASE_SECRET_KEY not found in env or {CLT_PLUS_ENV}", file=sys.stderr)
        sys.exit(2)
    return url, key


def main() -> None:
    from supabase import create_client

    url, key = _load_env()
    client = create_client(url, key)

    pairs = sorted({
        (r["region"], s["name"])
        for r in json.loads(REGIONS.read_text(encoding="utf-8"))
        for s in r["subEntities"]
    })
    valid = set(pairs)
    print(f"v2 pairs in regions.json: {len(pairs)}")

    # Page through ALL rows to discover every (region, sub_entity) currently
    # in the table. We avoid the supabase row-tuple-IN ergonomics gap by
    # deleting per-pair when the pair is not in the valid set.
    all_pairs: set[tuple[str, str]] = set()
    page_size = 1000
    start = 0
    total_rows = 0
    while True:
        resp = (
            client.table("notices_v2")
            .select("region,sub_entity")
            .range(start, start + page_size - 1)
            .execute()
        )
        rows = resp.data or []
        if not rows:
            break
        for row in rows:
            all_pairs.add((row["region"], row["sub_entity"]))
        total_rows += len(rows)
        if len(rows) < page_size:
            break
        start += page_size

    print(f"current notices_v2 rows: {total_rows}")
    print(f"distinct (region, sub_entity) pairs in DB: {len(all_pairs)}")

    orphans = sorted(all_pairs - valid)
    print(f"orphan pairs to delete: {len(orphans)}")
    if not orphans:
        print("Nothing to do.")
        return

    for region, sub in orphans:
        resp = (
            client.table("notices_v2")
            .delete()
            .eq("region", region)
            .eq("sub_entity", sub)
            .execute()
        )
        n = len(resp.data) if resp.data else 0
        print(f"  deleted {n:>5} rows  ({region} / {sub})")

    # Final count
    head = client.table("notices_v2").select("notice_id", count="exact").limit(1).execute()
    remaining = head.count if hasattr(head, "count") else "?"
    print(f"\nRemaining rows: {remaining}")


if __name__ == "__main__":
    main()
