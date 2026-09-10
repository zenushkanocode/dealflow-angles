"""Static site builder for GitHub Pages (docs/)."""
from __future__ import annotations

import json
from collections import defaultdict
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Any

IST = timezone(timedelta(hours=5, minutes=30))
LANE_ORDER = ["fundraises", "launches", "tech_news"]
LANE_LABELS = {
    "fundraises": "Fundraises",
    "launches": "Launches",
    "tech_news": "Tech news",
}


def _ist_date(iso: str | None) -> str:
    if not iso:
        return "unknown"
    try:
        dt = datetime.fromisoformat(iso)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(IST).strftime("%Y-%m-%d")
    except ValueError:
        return "unknown"


def _today_ist() -> str:
    return datetime.now(IST).strftime("%Y-%m-%d")


def _esc(s: str) -> str:
    return (
        (s or "")
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def _card_html(item: dict) -> str:
    angles = item.get("angles") or {}
    x = angles.get("x") or {}
    ig = angles.get("instagram") or {}
    li = angles.get("linkedin") or ""
    thread = x.get("thread") or []
    carousel = ig.get("carousel") or []
    date = _ist_date(item.get("published"))
    conf = item.get("confidence") or "low"
    money = item.get("money") or ""
    series = item.get("series") or ""
    badges = ""
    if money:
        badges += '<span class="badge money">' + _esc(money) + "</span>"
    if series:
        badges += '<span class="badge series">' + _esc(series) + "</span>"
    badges += '<span class="badge conf conf-' + _esc(conf) + '">' + _esc(conf) + "</span>"

    thread_html = "".join("<li>" + _esc(b) + "</li>" for b in thread)
    slides_html = "".join(
        '<div class="slide"><span class="sn">' + str(i + 1) + "</span>" + _esc(s) + "</div>"
        for i, s in enumerate(carousel)
    )

    title = _esc(item.get("title") or "")
    url = _esc(item.get("url") or "#")
    source = _esc(item.get("source") or "RSS")
    why = _esc(item.get("why_it_matters") or "")
    lane = _esc(item.get("lane") or "")
    lane_label = _esc(item.get("lane_label") or item.get("lane") or "")
    hook = _esc(x.get("hook") or "")
    li_esc = _esc(li)
    reel = _esc(ig.get("reel_hook") or "")
    voice = _esc(ig.get("voice") or "@zenushkascut")

    return (
        '<article class="card" data-lane="' + lane + '" data-date="' + date + '">'
        '<header class="card-head">'
        '<div class="meta">'
        '<time datetime="' + date + '">' + date + "</time>"
        '<span class="lane-pill">' + lane_label + "</span>"
        + badges
        + "</div>"
        "<h3><a href=\"" + url + '" target="_blank" rel="noopener">' + title + "</a></h3>"
        '<p class="source">Source: ' + source + ' · <a href="' + url + '" target="_blank" rel="noopener">open</a></p>'
        '<p class="why"><strong>Why it matters:</strong> ' + why + "</p>"
        "</header>"
        '<details class="angles">'
        "<summary>Content angles (X · LinkedIn · Instagram)</summary>"
        '<section class="angle-block">'
        "<h4>X / Twitter</h4>"
        '<p class="label">Hook</p>'
        '<pre class="copyable">' + hook + "</pre>"
        '<p class="label">Thread</p>'
        '<ol class="thread">' + thread_html + "</ol>"
        "</section>"
        '<section class="angle-block">'
        "<h4>LinkedIn</h4>"
        '<pre class="copyable">' + li_esc + "</pre>"
        "</section>"
        '<section class="angle-block">'
        "<h4>Instagram · " + voice + "</h4>"
        '<p class="label">Reel hook</p>'
        '<pre class="copyable">' + reel + "</pre>"
        '<p class="label">5-slide carousel</p>'
        '<div class="carousel">' + slides_html + "</div>"
        "</section>"
        "</details>"
        "</article>"
    )


CSS = """
:root {
  --bg: #0b0d10;
  --panel: #14181f;
  --card: #1a2029;
  --text: #e8eef7;
  --muted: #9aa8bc;
  --accent: #6ee7b7;
  --fund: #fbbf24;
  --launch: #60a5fa;
  --news: #c084fc;
  --border: #2a3340;
  --danger: #f87171;
  font-family: "IBM Plex Sans", ui-sans-serif, system-ui, sans-serif;
}
* { box-sizing: border-box; }
body { margin: 0; background: var(--bg); color: var(--text); line-height: 1.5; }
a { color: var(--accent); }
.wrap { max-width: 1200px; margin: 0 auto; padding: 0 1rem; }
.site-header { border-bottom: 1px solid var(--border); background: var(--panel); padding: 1rem 0; margin-bottom: 1.5rem; }
.logo { font-weight: 700; font-size: 1.25rem; text-decoration: none; color: var(--text); }
.tag { color: var(--muted); margin: 0.25rem 0 0.75rem; font-size: 0.9rem; }
nav a { margin-right: 1rem; color: var(--muted); text-decoration: none; }
nav a:hover { color: var(--accent); }
.hero h1 { margin: 0 0 0.5rem; font-size: 1.75rem; }
.tz { font-size: 0.85rem; color: var(--muted); font-weight: 500; }
.counts { color: var(--muted); }
.note, .gaps { background: var(--panel); border: 1px solid var(--border); border-radius: 8px; padding: 0.75rem 1rem; margin: 1rem 0; font-size: 0.9rem; }
.gaps ul { margin: 0.5rem 0 0; padding-left: 1.2rem; color: var(--danger); }
.board { display: grid; grid-template-columns: repeat(3, 1fr); gap: 1rem; margin: 1rem 0 2rem; }
.col { background: var(--panel); border: 1px solid var(--border); border-radius: 12px; padding: 0.75rem; min-height: 200px; }
.col h2 { font-size: 1rem; margin: 0 0 0.75rem; display: flex; justify-content: space-between; align-items: center; }
.col[data-lane-col="fundraises"] h2 { color: var(--fund); }
.col[data-lane-col="launches"] h2 { color: var(--launch); }
.col[data-lane-col="tech_news"] h2 { color: var(--news); }
.count { background: var(--bg); color: var(--text); border-radius: 999px; padding: 0.1rem 0.55rem; font-size: 0.8rem; }
.card { background: var(--card); border: 1px solid var(--border); border-radius: 10px; padding: 0.85rem; margin-bottom: 0.75rem; }
.card-head h3 { font-size: 0.98rem; margin: 0.4rem 0; line-height: 1.35; }
.card-head h3 a { color: var(--text); text-decoration: none; }
.card-head h3 a:hover { color: var(--accent); }
.meta { display: flex; flex-wrap: wrap; gap: 0.35rem; align-items: center; font-size: 0.75rem; color: var(--muted); }
.lane-pill { background: var(--bg); border-radius: 999px; padding: 0.15rem 0.5rem; }
.badge { border-radius: 4px; padding: 0.1rem 0.35rem; font-size: 0.7rem; background: #243041; }
.badge.money { color: var(--fund); }
.conf-high { color: var(--accent); }
.conf-medium { color: var(--launch); }
.conf-low { color: var(--muted); }
.source { font-size: 0.8rem; color: var(--muted); margin: 0.25rem 0; }
.why { font-size: 0.88rem; margin: 0.5rem 0; }
.angles { margin-top: 0.5rem; font-size: 0.85rem; }
.angles summary { cursor: pointer; color: var(--accent); }
.angle-block { margin-top: 0.75rem; padding-top: 0.75rem; border-top: 1px dashed var(--border); }
.angle-block h4 { margin: 0 0 0.35rem; font-size: 0.9rem; }
.label { color: var(--muted); font-size: 0.75rem; margin: 0.4rem 0 0.2rem; text-transform: uppercase; letter-spacing: 0.04em; }
pre.copyable { white-space: pre-wrap; background: var(--bg); border-radius: 8px; padding: 0.65rem; margin: 0; font-family: "IBM Plex Mono", ui-monospace, monospace; font-size: 0.8rem; }
.thread { margin: 0.25rem 0 0 1.1rem; padding: 0; }
.carousel { display: grid; gap: 0.4rem; }
.slide { background: var(--bg); border-radius: 8px; padding: 0.5rem 0.65rem; font-size: 0.82rem; }
.sn { display: inline-block; width: 1.2rem; color: var(--accent); font-weight: 700; }
.empty { color: var(--muted); font-size: 0.85rem; }
.mobile-tabs { display: none; gap: 0.4rem; margin-bottom: 0.75rem; }
.mobile-tabs button { flex: 1; background: var(--panel); border: 1px solid var(--border); color: var(--muted); padding: 0.55rem; border-radius: 8px; cursor: pointer; }
.mobile-tabs button.active { color: var(--text); border-color: var(--accent); }
.archive-list { line-height: 1.9; }
.site-footer { border-top: 1px solid var(--border); padding: 1.5rem 0 2.5rem; color: var(--muted); font-size: 0.85rem; }
@media (max-width: 900px) {
  .board { grid-template-columns: 1fr; }
  .mobile-tabs { display: flex; }
  .col { display: none; }
  .col.active { display: block; }
}
"""

JS = """
(function () {
  const tabs = document.querySelectorAll(".mobile-tabs button");
  const cols = document.querySelectorAll(".col");
  function activate(lane) {
    tabs.forEach((b) => b.classList.toggle("active", b.dataset.tab === lane));
    cols.forEach((c) => c.classList.toggle("active", c.dataset.laneCol === lane));
  }
  if (tabs.length) {
    activate("fundraises");
    tabs.forEach((b) => b.addEventListener("click", () => activate(b.dataset.tab)));
  }
})();
"""



def _layout(title: str, body: str, nav_extra: str = "", base: str = ".") -> str:
    return (
        "<!DOCTYPE html>\n"
        '<html lang="en">\n'
        "<head>\n"
        '  <meta charset="utf-8" />\n'
        '  <meta name="viewport" content="width=device-width, initial-scale=1" />\n'
        "  <title>" + _esc(title) + " · dealflow-angles</title>\n"
        '  <meta name="description" content="Free dated content war room: Fundraises, Launches, Tech news to X, LinkedIn, Instagram angles. No paid APIs." />\n'
        '  <link rel="stylesheet" href="' + base + '/css/style.css" />\n'
        "</head>\n"
        "<body>\n"
        '  <header class="site-header">\n'
        '    <div class="wrap">\n'
        '      <a class="logo" href="' + base + '/index.html">dealflow-angles</a>\n'
        '      <p class="tag">Dated content war room · FREE RSS only · no LLM keys</p>\n'
        "      <nav>" + nav_extra + "\n"
        '        <a href="' + base + '/index.html">Today</a>\n'
        '        <a href="' + base + '/archive/index.html">Archive</a>\n'
        '        <a href="https://github.com/zenushkanocode/dealflow-angles">GitHub</a>\n'
        "      </nav>\n"
        "    </div>\n"
        "  </header>\n"
        '  <main class="wrap">\n'
        + body + "\n"
        "  </main>\n"
        '  <footer class="site-footer wrap">\n'
        "    <p>MIT · Built by <a href=\"https://github.com/zenushkanocode\">zenushkanocode</a>"
        " · Angles in @zenushkascut voice where noted · We never invent deals; gaps are labeled.</p>\n"
        "  </footer>\n"
        '  <script src="' + base + '/js/app.js"></script>\n'
        "</body>\n"
        "</html>\n"
    )


def build(
    items: list[dict[str, Any]],
    gaps: list[dict] | None = None,
    out_dir: str | Path = "docs",
    generated_note: str | None = None,
) -> dict:
    out = Path(out_dir)
    (out / "css").mkdir(parents=True, exist_ok=True)
    (out / "js").mkdir(parents=True, exist_ok=True)
    (out / "archive").mkdir(parents=True, exist_ok=True)
    (out / "data").mkdir(parents=True, exist_ok=True)

    gaps = gaps or []
    today = _today_ist()
    by_date: dict[str, list] = defaultdict(list)
    for it in items:
        by_date[_ist_date(it.get("published"))].append(it)

    view_date = today
    if not by_date.get(today):
        dated = [d for d in by_date if d != "unknown"]
        if dated:
            view_date = max(dated)

    day_items = by_date.get(view_date, [])
    counts = {lane: 0 for lane in LANE_ORDER}
    for it in day_items:
        lane = it.get("lane") or "tech_news"
        counts[lane] = counts.get(lane, 0) + 1

    gap_html = ""
    if gaps:
        lis = "".join(
            "<li><strong>" + _esc(g.get("name") or g.get("feed") or "") + "</strong>: "
            + _esc(g.get("error") or "unavailable") + "</li>"
            for g in gaps
        )
        gap_html = (
            '<aside class="gaps"><strong>Feed gaps (labeled, not invented):</strong>'
            "<ul>" + lis + "</ul></aside>"
        )

    seed_note = ""
    if generated_note:
        seed_note = '<p class="note">' + _esc(generated_note) + "</p>"

    cols = []
    for lane in LANE_ORDER:
        lane_items = [it for it in day_items if it.get("lane") == lane]
        if lane_items:
            cards = "".join(_card_html(it) for it in lane_items)
        else:
            cards = '<p class="empty">No items this lane for this date. Check archive or feed gaps.</p>'
        cols.append(
            '<section class="col" data-lane-col="' + lane + '">'
            "<h2>" + LANE_LABELS[lane] + ' <span class="count">' + str(len(lane_items)) + "</span></h2>"
            + cards + "</section>"
        )

    body = (
        '<section class="hero">'
        "<h1>Today <time>" + view_date + '</time> <span class="tz">IST</span></h1>'
        '<p class="counts">'
        "Fundraises <strong>" + str(counts["fundraises"]) + "</strong> · "
        "Launches <strong>" + str(counts["launches"]) + "</strong> · "
        "Tech news <strong>" + str(counts["tech_news"]) + "</strong>"
        " · total <strong>" + str(len(day_items)) + "</strong>"
        "</p>"
        + seed_note + gap_html + "</section>"
        '<div class="mobile-tabs" role="tablist">'
        '<button type="button" data-tab="fundraises" class="active">Fundraises</button>'
        '<button type="button" data-tab="launches">Launches</button>'
        '<button type="button" data-tab="tech_news">Tech news</button>'
        "</div>"
        '<div class="board">' + "".join(cols) + "</div>"
    )
    (out / "index.html").write_text(_layout("Today " + view_date, body, base="."), encoding="utf-8")

    dates_sorted = sorted((d for d in by_date if d != "unknown"), reverse=True)
    archive_links = []
    for d in dates_sorted:
        d_items = by_date[d]
        c = {lane: sum(1 for it in d_items if it.get("lane") == lane) for lane in LANE_ORDER}
        archive_links.append(
            '<li><a href="' + d + '.html">' + d + "</a> — "
            "F " + str(c["fundraises"]) + " · L " + str(c["launches"]) + " · T " + str(c["tech_news"])
            + " (" + str(len(d_items)) + ")</li>"
        )
        cols_a = []
        for lane in LANE_ORDER:
            lane_items = [it for it in d_items if it.get("lane") == lane]
            cards = "".join(_card_html(it) for it in lane_items) if lane_items else '<p class="empty">—</p>'
            cols_a.append(
                '<section class="col" data-lane-col="' + lane + '">'
                "<h2>" + LANE_LABELS[lane] + ' <span class="count">' + str(len(lane_items)) + "</span></h2>"
                + cards + "</section>"
            )
        abody = (
            '<section class="hero">'
            "<h1>Archive <time>" + d + '</time> <span class="tz">IST</span></h1>'
            '<p><a href="index.html">← all dates</a></p>'
            "</section>"
            '<div class="mobile-tabs" role="tablist">'
            '<button type="button" data-tab="fundraises" class="active">Fundraises</button>'
            '<button type="button" data-tab="launches">Launches</button>'
            '<button type="button" data-tab="tech_news">Tech news</button>'
            "</div>"
            '<div class="board">' + "".join(cols_a) + "</div>"
        )
        (out / "archive" / (d + ".html")).write_text(
            _layout("Archive " + d, abody, base=".."), encoding="utf-8"
        )

    archive_body = (
        '<section class="hero">'
        "<h1>Archive</h1>"
        "<p>~6 months of BIG items from free RSS when available. Missing dates = feed gaps, not empty markets.</p>"
        "</section>"
        '<ul class="archive-list">'
        + ("".join(archive_links) or "<li>No dated items yet.</li>")
        + "</ul>"
    )
    (out / "archive" / "index.html").write_text(
        _layout("Archive", archive_body, base=".."), encoding="utf-8"
    )

    (out / "css" / "style.css").write_text(CSS, encoding="utf-8")
    (out / "js" / "app.js").write_text(JS, encoding="utf-8")

    payload = {
        "generated_at_ist": datetime.now(IST).isoformat(),
        "view_date": view_date,
        "counts": counts,
        "gaps": gaps,
        "items": items,
    }
    (out / "data" / "latest.json").write_text(
        json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    return {"view_date": view_date, "counts": counts, "dates": dates_sorted, "n_items": len(items)}
