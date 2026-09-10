"""Heuristic lane classification — no ML, no paid APIs."""
from __future__ import annotations

import re
from typing import Any


AMOUNT_RE = re.compile(
    r"\$?\s*(\d+(?:\.\d+)?)\s*(million|billion|m|b|mn|bn)\b",
    re.I,
)
SERIES_RE = re.compile(
    r"\b(pre[- ]?seed|seed|series\s*[a-f]|growth round|extension)\b",
    re.I,
)
COMPANY_RAISE_RE = re.compile(
    r"^(.{2,60}?)\s+(raises?|raised|closes?|closed|secures?|secured)\b",
    re.I,
)


def _score(text: str, keywords: list[str]) -> int:
    t = text.lower()
    score = 0
    for kw in keywords:
        if kw.lower() in t:
            # longer phrases weigh more
            score += 1 + (1 if " " in kw else 0)
    return score


def extract_money(text: str) -> str | None:
    m = AMOUNT_RE.search(text)
    if not m:
        return None
    num, unit = m.group(1), m.group(2).lower()
    if unit in ("b", "bn", "billion"):
        return f"${num}B"
    return f"${num}M"


def extract_series(text: str) -> str | None:
    m = SERIES_RE.search(text)
    if not m:
        return None
    s = m.group(1).strip()
    # normalize
    s = re.sub(r"\s+", " ", s)
    if s.lower().startswith("series"):
        return "Series " + s.split()[-1].upper()
    return s.title().replace("Pre Seed", "Pre-seed").replace("Pre-Seed", "Pre-seed")


def extract_company_hint(title: str) -> str | None:
    m = COMPANY_RAISE_RE.match(title.strip())
    if m:
        return m.group(1).strip(" -–—:|")
    # fallback: first proper-ish chunk before colon/dash
    parts = re.split(r"\s+[–—:-]\s+", title, maxsplit=1)
    head = parts[0].strip()
    if 2 <= len(head) <= 48 and not head.lower().startswith(("how ", "why ", "what ")):
        return head
    return None


def classify_item(item: dict[str, Any], lanes_cfg: dict) -> dict[str, Any]:
    blob = f"{item.get('title', '')} {item.get('summary', '')}"
    scores: dict[str, int] = {}
    for lane_id, meta in lanes_cfg.items():
        scores[lane_id] = _score(blob, meta.get("keywords") or [])

    # Prefer feed's declared lanes as soft prior
    for fl in item.get("feed_lanes") or []:
        if fl in scores:
            scores[fl] += 1

    # Strong fundraise signals
    money = extract_money(blob)
    series = extract_series(blob)
    if money or series:
        scores["fundraises"] = scores.get("fundraises", 0) + 4

    best = max(scores, key=scores.get) if scores else "tech_news"
    if scores.get(best, 0) <= 0:
        best = "tech_news"
        confidence = "low"
    elif scores[best] >= 4:
        confidence = "high"
    else:
        confidence = "medium"

    out = dict(item)
    out["lane"] = best
    out["lane_label"] = lanes_cfg.get(best, {}).get("label", best)
    out["confidence"] = confidence
    out["money"] = money
    out["series"] = series
    out["company"] = extract_company_hint(item.get("title") or "")
    out["why_it_matters"] = _why_it_matters(out)
    return out


def _why_it_matters(item: dict) -> str:
    lane = item.get("lane")
    money = item.get("money")
    series = item.get("series")
    company = item.get("company") or "This player"
    if lane == "fundraises":
        bits = []
        if money:
            bits.append(f"{money}")
        if series:
            bits.append(series)
        detail = " ".join(bits) if bits else "fresh capital"
        return f"{company} just locked {detail} — signal for category heat + competitor pace."
    if lane == "launches":
        return f"New ship from {company} — distribution window is open while attention is fresh."
    return f"Market move around {company} — useful for positioning, narrative, or timing your own push."


def classify_all(items: list[dict], lanes_cfg: dict) -> list[dict]:
    return [classify_item(it, lanes_cfg) for it in items]
