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


def _piece(label: str, inner_html: str) -> str:
    """Labeled block with a one-click Copy button targeting .copyable inside."""
    return (
        '<div class="angle-piece">'
        '<div class="angle-piece-head">'
        '<span class="label">' + _esc(label) + "</span>"
        '<button type="button" class="copy-btn" aria-label="Copy ' + _esc(label) + '">Copy</button>'
        "</div>"
        + inner_html
        + "</div>"
    )


def _card_html(item: dict) -> str:
    angles = item.get("angles") or {}
    x = angles.get("x") or {}
    ig = angles.get("instagram") or {}
    li = angles.get("linkedin") or ""
    thread = x.get("thread") or []
    carousel = ig.get("carousel") or []
    date = _ist_date(item.get("published"))
    money = item.get("money") or ""
    series = item.get("series") or ""

    # Soft meta: keep money when useful; series as quiet hint; drop dense conf badges
    badges = ""
    if money:
        badges += '<span class="badge money">' + _esc(money) + "</span>"
    if series:
        badges += '<span class="badge series">' + _esc(series) + "</span>"

    thread_html = "".join("<li>" + _esc(b) + "</li>" for b in thread)
    slides_html = "".join(
        '<div class="slide"><span class="sn">' + str(i + 1) + "</span>" + _esc(s) + "</div>"
        for i, s in enumerate(carousel)
    )
    # Plain text for carousel copy (newline-joined slides)
    carousel_plain = "\n".join(str(i + 1) + ". " + s for i, s in enumerate(carousel))
    thread_plain = "\n".join(thread)

    title = _esc(item.get("title") or "")
    url = _esc(item.get("url") or "#")
    source = _esc(item.get("source") or "RSS")
    why = _esc(item.get("why_it_matters") or "")
    lane = _esc(item.get("lane") or "")
    hook = _esc(x.get("hook") or "")
    li_esc = _esc(li)
    reel = _esc(ig.get("reel_hook") or "")
    voice = _esc(ig.get("voice") or "@zenushkascut")

    x_panel = (
        '<section class="plat-panel is-active" data-plat-panel="x" role="tabpanel">'
        + _piece("Hook", '<pre class="copyable">' + hook + "</pre>")
        + _piece(
            "Thread",
            '<pre class="copyable copyable-hidden">' + _esc(thread_plain) + "</pre>"
            '<ol class="thread">' + thread_html + "</ol>",
        )
        + "</section>"
    )
    li_panel = (
        '<section class="plat-panel" data-plat-panel="linkedin" role="tabpanel" hidden>'
        + _piece("Post", '<pre class="copyable">' + li_esc + "</pre>")
        + "</section>"
    )
    ig_panel = (
        '<section class="plat-panel" data-plat-panel="instagram" role="tabpanel" hidden>'
        + _piece("Reel hook", '<pre class="copyable">' + reel + "</pre>")
        + _piece(
            "5-slide carousel",
            '<pre class="copyable copyable-hidden">' + _esc(carousel_plain) + "</pre>"
            '<div class="carousel">' + slides_html + "</div>",
        )
        + "</section>"
    )

    return (
        '<article class="card" data-lane="' + lane + '" data-date="' + date + '">'
        '<header class="card-head">'
        '<div class="meta">'
        '<time datetime="' + date + '">' + date + "</time>"
        + badges
        + "</div>"
        "<h3><a href=\"" + url + '" target="_blank" rel="noopener">' + title + "</a></h3>"
        '<p class="source">' + source + ' · <a href="' + url + '" target="_blank" rel="noopener">open story</a></p>'
        '<p class="why">' + why + "</p>"
        "</header>"
        '<div class="angles">'
        '<div class="platform-tabs" role="tablist" aria-label="Platform">'
        '<button type="button" class="plat-tab is-active" role="tab" aria-selected="true" data-plat="x">X</button>'
        '<button type="button" class="plat-tab" role="tab" aria-selected="false" data-plat="linkedin">LinkedIn</button>'
        '<button type="button" class="plat-tab" role="tab" aria-selected="false" data-plat="instagram">Instagram</button>'
        "</div>"
        '<p class="angles-voice">Instagram voice: ' + voice + "</p>"
        + x_panel
        + li_panel
        + ig_panel
        + "</div>"
        "</article>"
    )


CSS = """
:root {
  --bg: #0a0c0f;
  --panel: #12161c;
  --card: #181e27;
  --card-hover: #1c2430;
  --text: #eef3f9;
  --muted: #8b9bb0;
  --accent: #6ee7b7;
  --accent-dim: rgba(110, 231, 183, 0.14);
  --fund: #fbbf24;
  --fund-dim: rgba(251, 191, 36, 0.16);
  --launch: #60a5fa;
  --launch-dim: rgba(96, 165, 250, 0.16);
  --news: #c084fc;
  --news-dim: rgba(192, 132, 252, 0.16);
  --border: #2a3340;
  --border-soft: #222a35;
  --danger: #f87171;
  --radius: 14px;
  --shadow: 0 1px 0 rgba(255,255,255,0.04) inset, 0 8px 24px rgba(0,0,0,0.25);
  font-family: "IBM Plex Sans", ui-sans-serif, system-ui, sans-serif;
}
* { box-sizing: border-box; }
body {
  margin: 0;
  background: var(--bg);
  color: var(--text);
  line-height: 1.5;
  padding-top: 0;
}
a { color: var(--accent); }
.wrap { max-width: 1180px; margin: 0 auto; padding: 0 1rem; }

/* Sticky top bar */
.site-header {
  position: sticky;
  top: 0;
  z-index: 40;
  border-bottom: 1px solid var(--border);
  background: rgba(18, 22, 28, 0.92);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
}
.header-row {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  gap: 0.5rem 1rem;
  padding: 0.7rem 1rem;
}
.logo {
  font-weight: 700;
  font-size: 1.05rem;
  text-decoration: none;
  color: var(--text);
  letter-spacing: -0.01em;
}
.header-nav {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 0.35rem 0.85rem;
}
.header-nav a {
  color: var(--muted);
  text-decoration: none;
  font-size: 0.92rem;
  font-weight: 500;
  padding: 0.25rem 0.15rem;
}
.header-nav a:hover,
.header-nav a.is-current { color: var(--accent); }
.howto-strip {
  border-top: 1px solid var(--border-soft);
  background: var(--accent-dim);
  color: var(--text);
  font-size: 0.82rem;
  font-weight: 500;
}
.howto-strip .wrap {
  padding: 0.45rem 1rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}
.howto-strip .steps { color: var(--accent); letter-spacing: 0.01em; }
.howto-strip .hint { color: var(--muted); font-weight: 400; }

.hero { margin: 1.25rem 0 0.75rem; }
.hero h1 { margin: 0 0 0.35rem; font-size: 1.55rem; letter-spacing: -0.02em; }
.tz { font-size: 0.8rem; color: var(--muted); font-weight: 500; margin-left: 0.25rem; }
.counts {
  color: var(--muted);
  font-size: 0.9rem;
  margin: 0;
}
.counts strong { color: var(--text); }
.note, .gaps {
  background: var(--panel);
  border: 1px solid var(--border-soft);
  border-radius: 10px;
  padding: 0.65rem 0.9rem;
  margin: 0.85rem 0 0;
  font-size: 0.85rem;
  color: var(--muted);
}
.gaps ul { margin: 0.4rem 0 0; padding-left: 1.15rem; color: var(--danger); }

/* Lane board */
.board {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1rem;
  margin: 0.75rem 0 2.5rem;
  align-items: start;
}
.col {
  background: var(--panel);
  border: 1px solid var(--border-soft);
  border-radius: var(--radius);
  padding: 0.85rem;
  min-height: 120px;
}
.col h2 {
  font-size: 0.95rem;
  margin: 0 0 0.85rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 650;
}
.col[data-lane-col="fundraises"] h2 { color: var(--fund); }
.col[data-lane-col="launches"] h2 { color: var(--launch); }
.col[data-lane-col="tech_news"] h2 { color: var(--news); }
.count {
  background: var(--bg);
  color: var(--text);
  border-radius: 999px;
  padding: 0.12rem 0.55rem;
  font-size: 0.75rem;
  font-weight: 600;
}

/* Product-like cards */
.card {
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 1rem;
  margin-bottom: 0.85rem;
  box-shadow: var(--shadow);
  transition: border-color 0.15s ease, background 0.15s ease;
}
.card:hover {
  border-color: #3a4656;
  background: var(--card-hover);
}
.card-head h3 {
  font-size: 1rem;
  margin: 0.35rem 0 0.4rem;
  line-height: 1.35;
  letter-spacing: -0.01em;
}
.card-head h3 a { color: var(--text); text-decoration: none; }
.card-head h3 a:hover { color: var(--accent); }
.meta {
  display: flex;
  flex-wrap: wrap;
  gap: 0.4rem;
  align-items: center;
  font-size: 0.72rem;
  color: var(--muted);
}
.meta time {
  font-variant-numeric: tabular-nums;
}
.badge {
  border-radius: 999px;
  padding: 0.12rem 0.5rem;
  font-size: 0.68rem;
  font-weight: 600;
  background: #243041;
  color: var(--muted);
}
.badge.money {
  color: var(--fund);
  background: var(--fund-dim);
}
.badge.series {
  background: transparent;
  border: 1px solid var(--border);
  color: var(--muted);
  font-weight: 500;
}
.source {
  font-size: 0.78rem;
  color: var(--muted);
  margin: 0 0 0.55rem;
}
.why {
  font-size: 0.9rem;
  margin: 0;
  color: var(--text);
  opacity: 0.92;
  line-height: 1.45;
}

/* Angles + platform tabs (open by default) */
.angles {
  margin-top: 0.9rem;
  padding-top: 0.85rem;
  border-top: 1px solid var(--border-soft);
}
.platform-tabs {
  display: flex;
  gap: 0.35rem;
  margin-bottom: 0.75rem;
  background: var(--bg);
  padding: 0.3rem;
  border-radius: 10px;
  border: 1px solid var(--border-soft);
}
.plat-tab {
  flex: 1;
  background: transparent;
  border: none;
  color: var(--muted);
  padding: 0.45rem 0.5rem;
  border-radius: 7px;
  cursor: pointer;
  font-size: 0.82rem;
  font-weight: 600;
  font-family: inherit;
}
.plat-tab:hover { color: var(--text); }
.plat-tab.is-active {
  background: var(--card);
  color: var(--text);
  box-shadow: 0 1px 2px rgba(0,0,0,0.25);
}
.angles-voice {
  display: none;
  font-size: 0.72rem;
  color: var(--muted);
  margin: -0.25rem 0 0.55rem;
}
.angles:has([data-plat-panel="instagram"].is-active) .angles-voice { display: block; }
.plat-panel { display: none; }
.plat-panel.is-active { display: block; }

.angle-piece { margin-bottom: 0.7rem; }
.angle-piece:last-child { margin-bottom: 0; }
.angle-piece-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.5rem;
  margin-bottom: 0.3rem;
}
.label {
  color: var(--muted);
  font-size: 0.7rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  font-weight: 600;
}
.copy-btn {
  background: var(--accent-dim);
  color: var(--accent);
  border: 1px solid rgba(110, 231, 183, 0.35);
  border-radius: 7px;
  padding: 0.28rem 0.65rem;
  font-size: 0.72rem;
  font-weight: 650;
  cursor: pointer;
  font-family: inherit;
  line-height: 1;
}
.copy-btn:hover { background: rgba(110, 231, 183, 0.22); }
.copy-btn.copied {
  background: rgba(110, 231, 183, 0.28);
  color: var(--text);
  border-color: var(--accent);
}
pre.copyable {
  white-space: pre-wrap;
  background: var(--bg);
  border: 1px solid var(--border-soft);
  border-radius: 8px;
  padding: 0.7rem 0.75rem;
  margin: 0;
  font-family: "IBM Plex Mono", ui-monospace, monospace;
  font-size: 0.78rem;
  line-height: 1.45;
}
pre.copyable-hidden {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0,0,0,0);
  border: 0;
}
.thread {
  margin: 0;
  padding: 0.55rem 0.75rem 0.55rem 1.4rem;
  background: var(--bg);
  border: 1px solid var(--border-soft);
  border-radius: 8px;
  font-size: 0.8rem;
}
.thread li { margin: 0.25rem 0; }
.carousel { display: grid; gap: 0.4rem; }
.slide {
  background: var(--bg);
  border: 1px solid var(--border-soft);
  border-radius: 8px;
  padding: 0.5rem 0.65rem;
  font-size: 0.8rem;
}
.sn { display: inline-block; width: 1.2rem; color: var(--accent); font-weight: 700; }
.empty { color: var(--muted); font-size: 0.85rem; margin: 0.5rem 0; }

/* Stronger mobile lane tabs */
.mobile-tabs {
  display: none;
  gap: 0.45rem;
  margin: 0.85rem 0 0.35rem;
}
.mobile-tabs button {
  flex: 1;
  background: var(--panel);
  border: 1px solid var(--border);
  color: var(--muted);
  padding: 0.75rem 0.4rem;
  border-radius: 11px;
  cursor: pointer;
  font-family: inherit;
  font-size: 0.82rem;
  font-weight: 650;
  min-height: 48px;
}
.mobile-tabs button.active[data-tab="fundraises"] {
  color: var(--fund);
  border-color: var(--fund);
  background: var(--fund-dim);
}
.mobile-tabs button.active[data-tab="launches"] {
  color: var(--launch);
  border-color: var(--launch);
  background: var(--launch-dim);
}
.mobile-tabs button.active[data-tab="tech_news"] {
  color: var(--news);
  border-color: var(--news);
  background: var(--news-dim);
}

.archive-list { line-height: 1.9; padding-left: 1.1rem; }
.site-footer {
  border-top: 1px solid var(--border-soft);
  padding: 1.5rem 0 2.5rem;
  color: var(--muted);
  font-size: 0.85rem;
}

@media (max-width: 900px) {
  .board { grid-template-columns: 1fr; }
  .mobile-tabs { display: flex; }
  .col { display: none; }
  .col.active { display: block; }
  .hero h1 { font-size: 1.35rem; }
  .card { padding: 0.9rem; }
}
"""

JS = """
(function () {
  // Lane tabs (mobile)
  const tabs = document.querySelectorAll(".mobile-tabs button");
  const cols = document.querySelectorAll(".col");
  function activateLane(lane) {
    tabs.forEach((b) => b.classList.toggle("active", b.dataset.tab === lane));
    cols.forEach((c) => c.classList.toggle("active", c.dataset.laneCol === lane));
  }
  if (tabs.length) {
    activateLane("fundraises");
    tabs.forEach((b) => b.addEventListener("click", () => activateLane(b.dataset.tab)));
  }

  // Platform tabs inside each card
  document.querySelectorAll(".angles").forEach((root) => {
    const platTabs = root.querySelectorAll(".plat-tab");
    const panels = root.querySelectorAll(".plat-panel");
    platTabs.forEach((tab) => {
      tab.addEventListener("click", () => {
        const plat = tab.dataset.plat;
        platTabs.forEach((t) => {
          const on = t.dataset.plat === plat;
          t.classList.toggle("is-active", on);
          t.setAttribute("aria-selected", on ? "true" : "false");
        });
        panels.forEach((p) => {
          const on = p.dataset.platPanel === plat;
          p.classList.toggle("is-active", on);
          if (on) p.removeAttribute("hidden");
          else p.setAttribute("hidden", "");
        });
      });
    });
  });

  // One-click Copy
  function copyText(text) {
    if (navigator.clipboard && navigator.clipboard.writeText) {
      return navigator.clipboard.writeText(text);
    }
    return new Promise(function (resolve, reject) {
      const ta = document.createElement("textarea");
      ta.value = text;
      ta.setAttribute("readonly", "");
      ta.style.position = "fixed";
      ta.style.left = "-9999px";
      document.body.appendChild(ta);
      ta.select();
      try {
        document.execCommand("copy");
        resolve();
      } catch (e) {
        reject(e);
      } finally {
        document.body.removeChild(ta);
      }
    });
  }

  document.addEventListener("click", function (e) {
    const btn = e.target.closest(".copy-btn");
    if (!btn) return;
    const piece = btn.closest(".angle-piece");
    if (!piece) return;
    const source = piece.querySelector(".copyable");
    if (!source) return;
    const text = (source.textContent || "").trim();
    if (!text) return;
    copyText(text).then(function () {
      const prev = btn.textContent;
      btn.textContent = "Copied";
      btn.classList.add("copied");
      setTimeout(function () {
        btn.textContent = prev || "Copy";
        btn.classList.remove("copied");
      }, 1400);
    }).catch(function () {
      btn.textContent = "Failed";
      setTimeout(function () { btn.textContent = "Copy"; }, 1400);
    });
  });
})();
"""


def _layout(title: str, body: str, nav_extra: str = "", base: str = ".", current: str = "") -> str:
    today_cls = ' class="is-current"' if current == "today" else ""
    archive_cls = ' class="is-current"' if current == "archive" else ""
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
        '    <div class="wrap header-row">\n'
        '      <a class="logo" href="' + base + '/index.html">dealflow-angles</a>\n'
        '      <nav class="header-nav">' + nav_extra + "\n"
        '        <a href="' + base + '/index.html"' + today_cls + ">Today</a>\n"
        '        <a href="' + base + '/archive/index.html"' + archive_cls + ">Archive</a>\n"
        '        <a href="https://github.com/zenushkanocode/dealflow-angles">GitHub</a>\n'
        "      </nav>\n"
        "    </div>\n"
        '    <div class="howto-strip">\n'
        '      <div class="wrap">\n'
        '        <span class="steps">Pick a card → copy angle → post</span>\n'
        '        <span class="hint">· free RSS · no paid APIs</span>\n'
        "      </div>\n"
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
        '<div class="mobile-tabs" role="tablist" aria-label="Lanes">'
        '<button type="button" data-tab="fundraises" class="active">Fundraises</button>'
        '<button type="button" data-tab="launches">Launches</button>'
        '<button type="button" data-tab="tech_news">Tech news</button>'
        "</div>"
        '<div class="board">' + "".join(cols) + "</div>"
    )
    (out / "index.html").write_text(
        _layout("Today " + view_date, body, base=".", current="today"), encoding="utf-8"
    )

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
            '<div class="mobile-tabs" role="tablist" aria-label="Lanes">'
            '<button type="button" data-tab="fundraises" class="active">Fundraises</button>'
            '<button type="button" data-tab="launches">Launches</button>'
            '<button type="button" data-tab="tech_news">Tech news</button>'
            "</div>"
            '<div class="board">' + "".join(cols_a) + "</div>"
        )
        (out / "archive" / (d + ".html")).write_text(
            _layout("Archive " + d, abody, base="..", current="archive"), encoding="utf-8"
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
        _layout("Archive", archive_body, base="..", current="archive"), encoding="utf-8"
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
