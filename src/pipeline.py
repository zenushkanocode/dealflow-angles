"""End-to-end: fetch RSS → classify → angles → static site + data pack."""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.fetch_rss import fetch_all, load_config
from src.classify import classify_all
from src.generate_angles import attach_all
from src.build_site import build

IST = timezone(timedelta(hours=5, minutes=30))


def merge_seed(live: list[dict], seed_path: Path) -> list[dict]:
    if not seed_path.exists():
        return live
    seed = json.loads(seed_path.read_text(encoding="utf-8"))
    seed_items = seed if isinstance(seed, list) else seed.get("items", [])
    by_id = {it["id"]: it for it in seed_items if it.get("id")}
    for it in live:
        by_id[it["id"]] = it  # live wins on id collision
    merged = list(by_id.values())
    merged.sort(key=lambda x: x.get("published") or "", reverse=True)
    return merged


def run(
    since_days: int = 180,
    max_per_feed: int = 50,
    out_dir: str = "docs",
    data_dir: str = "data",
    seed: bool = True,
    skip_fetch: bool = False,
) -> dict:
    config = load_config(str(ROOT / "config" / "feeds.yaml"))
    lanes_cfg = config.get("lanes") or {}
    gaps: list[dict] = []

    if skip_fetch:
        live = []
        cache_path = ROOT / data_dir / "items.json"
        if cache_path.exists():
            cached = json.loads(cache_path.read_text(encoding="utf-8"))
            live = cached.get("items") or []
            gaps.extend(cached.get("gaps") or [])
        gaps.append({"feed": "skip_fetch", "name": "live fetch", "error": "skipped (--skip-fetch); using seed/cache"})
    else:
        live, gaps = fetch_all(config, since_days=since_days, max_per_feed=max_per_feed)

    classified = classify_all(live, lanes_cfg)
    with_angles = attach_all(classified)

    data_path = ROOT / data_dir
    data_path.mkdir(parents=True, exist_ok=True)
    seed_path = data_path / "seed_items.json"

    if seed:
        # re-classify seed if present (seed stores raw-ish items)
        merged_raw = merge_seed(with_angles, seed_path)
        # seed items may already have angles; ensure classification + angles
        need = []
        ready = []
        for it in merged_raw:
            if it.get("angles") and it.get("lane"):
                ready.append(it)
            else:
                need.append(it)
        if need:
            ready.extend(attach_all(classify_all(need, lanes_cfg)))
        items = ready
        items.sort(key=lambda x: x.get("published") or "", reverse=True)
    else:
        items = with_angles

    # Persist pack
    pack = {
        "generated_at_ist": datetime.now(IST).isoformat(),
        "since_days": since_days,
        "gaps": gaps,
        "items": items,
    }
    (data_path / "items.json").write_text(json.dumps(pack, indent=2, ensure_ascii=False), encoding="utf-8")

    note = (
        "Seeded + live free-RSS pack. BIG items only where feeds provide them; "
        "gaps labeled below. Never invents deals."
    )
    summary = build(items, gaps=gaps, out_dir=str(ROOT / out_dir), generated_note=note)
    summary["gaps"] = gaps
    return summary


def main() -> None:
    p = argparse.ArgumentParser(description="flowD daily pipeline")
    p.add_argument("--since-days", type=int, default=180)
    p.add_argument("--max-per-feed", type=int, default=50)
    p.add_argument("--skip-fetch", action="store_true")
    p.add_argument("--no-seed", action="store_true")
    args = p.parse_args()
    summary = run(
        since_days=args.since_days,
        max_per_feed=args.max_per_feed,
        skip_fetch=args.skip_fetch,
        seed=not args.no_seed,
    )
    print(json.dumps({k: summary[k] for k in ("view_date", "counts", "n_items", "dates") if k in summary}, indent=2))
    if summary.get("gaps"):
        print("gaps:", len(summary["gaps"]))


if __name__ == "__main__":
    main()
