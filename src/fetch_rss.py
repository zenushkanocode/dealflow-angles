"""Fetch free RSS feeds and normalize items."""
from __future__ import annotations

import hashlib
import time
from datetime import datetime, timezone, timedelta
from email.utils import parsedate_to_datetime
from typing import Any
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError

import feedparser
import yaml

IST = timezone(timedelta(hours=5, minutes=30))
USER_AGENT = "flowD/1.0 (+https://github.com/zenushkanocode/flowD; free OSS)"


def load_config(path: str = "config/feeds.yaml") -> dict:
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def _parse_date(entry: dict) -> datetime | None:
    for key in ("published_parsed", "updated_parsed"):
        st = entry.get(key)
        if st:
            try:
                return datetime(*st[:6], tzinfo=timezone.utc)
            except (TypeError, ValueError):
                pass
    for key in ("published", "updated"):
        raw = entry.get(key)
        if not raw:
            continue
        try:
            dt = parsedate_to_datetime(raw)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt.astimezone(timezone.utc)
        except (TypeError, ValueError, IndexError):
            pass
    return None


def _item_id(title: str, link: str) -> str:
    return hashlib.sha1(f"{title}|{link}".encode()).hexdigest()[:16]


def fetch_feed(url: str, timeout: int = 25) -> feedparser.FeedParserDict:
    req = Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urlopen(req, timeout=timeout) as resp:
            data = resp.read()
        return feedparser.parse(data)
    except (URLError, HTTPError, TimeoutError, OSError) as e:
        # fall back to feedparser's own fetch
        parsed = feedparser.parse(url)
        if getattr(parsed, "bozo", False) and not parsed.entries:
            raise RuntimeError(f"fetch failed for {url}: {e}") from e
        return parsed


def fetch_all(
    config: dict | None = None,
    since_days: int | None = None,
    max_per_feed: int = 40,
) -> tuple[list[dict[str, Any]], list[dict[str, str]]]:
    """Return (items, gaps). Gaps list failed feeds for labeling."""
    config = config or load_config()
    cutoff = None
    if since_days is not None:
        cutoff = datetime.now(timezone.utc) - timedelta(days=since_days)

    items: list[dict[str, Any]] = []
    gaps: list[dict[str, str]] = []
    seen: set[str] = set()

    for feed in config.get("feeds", []):
        fid = feed["id"]
        try:
            parsed = fetch_feed(feed["url"])
            time.sleep(0.35)  # be polite
        except Exception as e:
            gaps.append({"feed": fid, "name": feed.get("name", fid), "error": str(e)[:200]})
            continue

        if not parsed.entries:
            gaps.append({"feed": fid, "name": feed.get("name", fid), "error": "empty feed"})
            continue

        count = 0
        for entry in parsed.entries:
            if count >= max_per_feed:
                break
            title = (entry.get("title") or "").strip()
            link = (entry.get("link") or "").strip()
            if not title or not link:
                continue
            dt = _parse_date(entry)
            if cutoff and dt and dt < cutoff:
                continue
            iid = _item_id(title, link)
            if iid in seen:
                continue
            seen.add(iid)
            summary = (entry.get("summary") or entry.get("description") or "")[:800]
            # strip crude HTML
            import re
            summary = re.sub(r"<[^>]+>", " ", summary)
            summary = re.sub(r"\s+", " ", summary).strip()
            items.append({
                "id": iid,
                "title": title,
                "url": link,
                "source": feed.get("name", fid),
                "source_id": fid,
                "published": dt.isoformat() if dt else None,
                "summary": summary,
                "feed_lanes": list(feed.get("lanes") or []),
            })
            count += 1

    items.sort(key=lambda x: x.get("published") or "", reverse=True)
    return items, gaps


if __name__ == "__main__":
    items, gaps = fetch_all(since_days=14, max_per_feed=20)
    print(f"fetched {len(items)} items, {len(gaps)} gaps")
    for g in gaps:
        print("  gap:", g)
    for it in items[:5]:
        print("-", it["published"], it["title"][:70])
