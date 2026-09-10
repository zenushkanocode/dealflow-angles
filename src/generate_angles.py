"""Deterministic content-angle templates — no LLM, no API keys."""
from __future__ import annotations

import hashlib
from typing import Any


def _pick(seed: str, options: list[str]) -> str:
    h = int(hashlib.md5(seed.encode()).hexdigest(), 16)
    return options[h % len(options)]


def _short(title: str, n: int = 90) -> str:
    t = title.strip()
    if len(t) <= n:
        return t
    return t[: n - 1].rsplit(" ", 1)[0] + "…"


def _entity(item: dict) -> str:
    e = item.get("company") or _short(item.get("title") or "this story", 40)
    return e.rstrip(" .")


def _money_bit(item: dict) -> str:
    parts = []
    if item.get("money"):
        parts.append(item["money"])
    if item.get("series"):
        parts.append(item["series"])
    return " ".join(parts) if parts else "a fresh round"


def generate_x(item: dict) -> dict:
    lane = item.get("lane")
    entity = _entity(item)
    title = item.get("title") or ""
    seed = item.get("id") or title

    if lane == "fundraises":
        money = _money_bit(item)
        hook = _pick(seed + "xh", [
            f"{entity} just raised {money}.\n\nThe quiet part: category winners aren't waiting for perfect timing.",
            f"Not another \"AI raises\" headline.\n\n{entity} closed {money} — here's the angle founders should steal.",
            f"{money} into {entity}.\n\nIf you're building adjacent, this changes your narrative this week.",
        ])
        beats = [
            f"1/ What happened: {_short(title, 120)}",
            f"2/ Why it matters: capital = distribution budget + hiring velocity. Neighbors feel it in 30–60 days.",
            f"3/ Pattern: rounds like this usually follow a wedge that finally converted (usage → revenue → story).",
            f"4/ Founder move: write the \"why now\" in one line using THEIR momentum as the market proof.",
            f"5/ CTA: if you're shipping in this space, comment your wedge — I'll roast/refine it.",
        ]
    elif lane == "launches":
        hook = _pick(seed + "xh", [
            f"New drop: {entity}.\n\nIgnore the feature list. Steal the distribution move.",
            f"{entity} just shipped.\n\nThe founders who win here won't \"announce\" — they'll teach.",
            f"Launch alert (no hype diet): {_short(title, 80)}\n\nThread: how to ride this without looking like a copycat.",
        ])
        beats = [
            f"1/ Product: {_short(title, 120)}",
            "2/ Attention half-life is short. First 72h = content, not polish.",
            "3/ Performing pattern: hook with the pain, show the before/after, then soft CTA.",
            "4/ Don't clone UI — clone the job-to-be-done framing they're winning with.",
            "5/ If you ship something related this week, reply with the link — community > cold launch.",
        ]
    else:
        hook = _pick(seed + "xh", [
            f"Tech move worth a screenshot: {_short(title, 90)}\n\nNot financial advice — narrative advice.",
            f"Market pulse: {entity}.\n\nHere's how operators turn this into a post (not a panic).",
            f"{_short(title, 100)}\n\n3 beats for founders who actually ship.",
        ])
        beats = [
            f"1/ Signal: {_short(title, 120)}",
            "2/ Second-order: who gains distribution, who loses the default story.",
            "3/ Content play: explain the shift in plain English for your ICP — be the translator.",
            "4/ Internal: update one slide / one landing line if this touches your category.",
            "5/ Save this if you're batching content — tomorrow's \"hot take\" is today's calm brief.",
        ]

    return {"hook": hook, "thread": beats[:5]}


def generate_linkedin(item: dict) -> str:
    lane = item.get("lane")
    entity = _entity(item)
    title = item.get("title") or ""
    why = item.get("why_it_matters") or ""
    url = item.get("url") or ""

    if lane == "fundraises":
        money = _money_bit(item)
        return (
            f"Operator note: {entity} raised {money}.\n\n"
            f"{why}\n\n"
            f"What I'm telling teams this week:\n"
            f"1) Don't envy the round — reverse-engineer the wedge that made it fundable.\n"
            f"2) Update your \"why now\" with a real external proof point (this is one).\n"
            f"3) Distribution still compounds faster than feature parity.\n\n"
            f"Source: {_short(title, 100)}\n{url}\n\n"
            f"If you're fundraising or competing in-category — what's your one-line wedge right now?"
        )
    if lane == "launches":
        return (
            f"Launch worth watching: {entity}.\n\n"
            f"{why}\n\n"
            f"Founder/operator checklist I use on days like this:\n"
            f"• Capture the JTBD in one sentence (theirs, then yours).\n"
            f"• Ship one piece of teaching content in 48h — not a feature dump.\n"
            f"• Decide: ride the narrative, differentiate hard, or stay quiet.\n\n"
            f"{_short(title, 110)}\n{url}\n\n"
            f"Curious how others are responding — building adjacent, or ignoring the noise?"
        )
    return (
        f"Market brief for builders: {_short(title, 110)}\n\n"
        f"{why}\n\n"
        f"My default response isn't a hot take — it's a translation:\n"
        f"What changed → who cares → what we say differently on the site / in sales / on social.\n\n"
        f"Source: {url}\n\n"
        f"Operators: which part of this actually touches your roadmap?"
    )


def generate_instagram(item: dict) -> dict:
    """@zenushkascut voice: conversational lowercase-leaning, hook-first, concrete, cheeky."""
    lane = item.get("lane")
    entity = _entity(item)
    money = _money_bit(item)
    title = _short(item.get("title") or "", 80)
    seed = item.get("id") or title

    if lane == "fundraises":
        reel = _pick(seed + "ir", [
            f"okay but {entity} just raised {money} and you're still \"finalizing the deck\"?",
            f"{money}. one headline. your whole category just got louder.",
            f"not me refreshing funding news like it's a sport — {entity} closed {money}.",
        ])
        slides = [
            f"hook: {entity} → {money}. that's the post. everything else is commentary.",
            f"why i care: capital isn't vanity — it's ad budget, hiring, and narrative oxygen.",
            f"steal this: write your why-now using THEIR round as proof the market is moving.",
            f"founder truth: features don't raise. distribution stories do. {title}",
            f"comment ANGLE if you want me to turn this into a week of content prompts.",
        ]
    elif lane == "launches":
        reel = _pick(seed + "ir", [
            f"new launch dropped and i'm already thinking about the carousel. {entity}.",
            f"someone shipped. the timeline will forget in 72 hours unless you teach.",
            f"launch day energy: {_short(title, 60)} — don't announce, demonstrate.",
        ])
        slides = [
            f"hook: {entity} just shipped. cool. what's your move?",
            "slide energy: pain → before/after → soft CTA. not a feature laundry list.",
            "meme-aware take: cloning UI is easy. cloning the job-to-be-done framing is the real game.",
            f"concrete: batch 5 posts off this launch while attention is free. title ref: {title}",
            "comment ANGLE for a carousel outline in my voice — yes i recycle formats, that's the point.",
        ]
    else:
        reel = _pick(seed + "ir", [
            f"tech news that actually changes your caption strategy: {_short(title, 55)}",
            f"market moved. your content calendar didn't. awkward.",
            f"quick pulse check — {entity} is in the feed. translate it for your icp.",
        ])
        slides = [
            f"hook: {_short(title, 70)}",
            "don't panic-post. translate: what changed → who cares → what you say differently.",
            "cheeky reminder: hot takes age like milk. teaching posts age like… slightly better milk.",
            f"numbers > vibes when you can find them. otherwise: clear POV + one CTA.",
            "comment ANGLE if you want this turned into a reel script + 5-slide pack.",
        ]

    return {"reel_hook": reel, "carousel": slides, "voice": "@zenushkascut"}


def attach_angles(item: dict[str, Any]) -> dict[str, Any]:
    out = dict(item)
    out["angles"] = {
        "x": generate_x(item),
        "linkedin": generate_linkedin(item),
        "instagram": generate_instagram(item),
    }
    return out


def attach_all(items: list[dict]) -> list[dict]:
    return [attach_angles(it) for it in items]
