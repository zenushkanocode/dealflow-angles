# dealflow-angles

**Dated content war room** for founders & marketers: free tech RSS → ready-to-post angles for **X**, **LinkedIn**, and **Instagram**.

- **FREE only** — no paid APIs, no required LLM keys
- Three lanes: **Fundraises** · **Launches** · **Tech news**
- Deterministic templates (show-not-tell below)
- Static site for **GitHub Pages** + daily **GitHub Action** cron
- Never invents deals — feed gaps are labeled

> Built for [zenushkanocode](https://github.com/zenushkanocode) · Instagram angles in [@zenushkascut](https://www.instagram.com/) voice

## Sample output (real pipeline)

From a live fundraise card (Boring Co. / Bloomberg, 2026-09-10 IST):

**Why it matters:** Musk's Boring Co. just locked $23B — signal for category heat + competitor pace.

**X — hook**
```
$23B into Musk's Boring Co.

If you're building adjacent, this changes your narrative this week.
```

**X — thread beats**
1. What happened: Musk's Boring Co. Raises Capital, Valuing Firm at $23 Billion
2. Why it matters: capital = distribution budget + hiring velocity. Neighbors feel it in 30–60 days.
3. Pattern: rounds like this usually follow a wedge that finally converted (usage → revenue → story).
4. Founder move: write the "why now" in one line using THEIR momentum as the market proof.
5. CTA: if you're shipping in this space, comment your wedge — I'll roast/refine it.

**Instagram Reel hook** (`@zenushkascut`)
```
not me refreshing funding news like it's a sport — Musk's Boring Co. closed $23B.
```

**Instagram 5-slide carousel**
1. hook: Musk's Boring Co. → $23B. that's the post. everything else is commentary.
2. why i care: capital isn't vanity — it's ad budget, hiring, and narrative oxygen.
3. steal this: write your why-now using THEIR round as proof the market is moving.
4. founder truth: features don't raise. distribution stories do. …
5. comment ANGLE if you want me to turn this into a week of content prompts.

**LinkedIn** — founder/operator post with checklist + source URL (see any card on the site).

## Quick start

```bash
git clone https://github.com/zenushkanocode/dealflow-angles.git
cd dealflow-angles
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python -m src.pipeline --since-days 180 --max-per-feed 50
# browse
python -m http.server -d docs 8080
# → http://127.0.0.1:8080
```

Or: `bash scripts/run_local.sh`

Offline / no network: `python -m src.pipeline --skip-fetch` (uses `data/seed_items.json` + any cached `data/items.json` merge).

## What you get on each card

| Field | Notes |
|-------|--------|
| Date | Shown in **IST** |
| Lane | Fundraises / Launches / Tech news (heuristics) |
| Headline + source URL | From free RSS or curated public seed |
| Why it matters | 1 line |
| X | Hook tweet + 3–5 beat thread |
| LinkedIn | Founder/operator post |
| Instagram | Reel hook + 5-slide carousel |

## Site

- **Today view** — IST date + lane counts; 3 columns (tabs on mobile)
- **Archive** — by date (`docs/archive/`)
- **~6 months backfill** — live RSS where retained + curated **BIG public** items in `data/seed_items.json` (never invented; gaps labeled on the page)
- JSON dump: `docs/data/latest.json` and `data/items.json`

## GitHub Pages

1. Repo **Settings → Pages**
2. Source: **GitHub Actions** (recommended), *or* Deploy from branch `main` / folder `/docs`
3. After merge to `main`, the daily workflow builds `docs/` and deploys Pages on `main`
4. Site URL: `https://zenushkanocode.github.io/dealflow-angles/`

Enable the Action under **Actions** tab if workflows are restricted on a new repo.

## Daily Action

`.github/workflows/daily.yml`

- Cron: `30 1 * * *` UTC (~07:00 IST)
- Also `workflow_dispatch` + push path filters
- Fetches free RSS → classify → angles → commits `docs/` + `data/items.json` → deploys Pages on `main`

## Stack

- Python 3.12+ · `feedparser` · `PyYAML` · stdlib HTML builder
- Heuristic lane classification (keywords + $ / Series signals)
- Template angle generation — **zero OpenAI / Anthropic / etc.**

## Project layout

```
config/feeds.yaml     # free RSS sources + lane keywords
src/fetch_rss.py      # polite fetch + normalize
src/classify.py       # heuristics
src/generate_angles.py
src/build_site.py     # docs/ static site
src/pipeline.py       # CLI entry: python -m src.pipeline
data/seed_items.json  # BIG public backfill
docs/                 # GitHub Pages root
```

## Ethics / accuracy

- We **do not invent** funding rounds or launches.
- RSS retention is short; older archive dates may be sparse — that's a **feed gap**, called out in the UI.
- Seed pack only includes **publicly reported** items with source URLs.

## License

MIT © 2026 Anushka Tyagi (zenushkanocode)
