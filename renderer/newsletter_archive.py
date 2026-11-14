#!/usr/bin/env python3
"""Build the Weekly Dispatch issue archive on ww2dispatches.com.

Usage: python3 renderer/newsletter_archive.py

Reads every newsletter/issue-NNN.md and writes, in the site's Night Dispatch look:
  site/newsletter/index.html   the list of issues (newest first), at /newsletter
  site/newsletter/NNN.html     one page per issue, at /newsletter/NNN
  site/newsletter/issues.json  newest first, for the home page's Latest line
  functions/_data/newsletter.json   each issue's release time (UTC)
  site/sitemap.xml             the site map for search engines (released issues plus the main pages)

An issue is released at its send time, Sunday 7 a.m. Mountain. The pages for an
issue built ahead (the Friday run builds the coming Sunday's) are committed with
the rest, and functions/newsletter/_middleware.js hides them until release: an
unreleased issue page redirects to /newsletter, and any element carrying a
data-release time still in the future is stripped from the HTML. So the archive
updates itself at 7 a.m. on Sunday with no extra step.

Per issue it reads (all optional except the issue file):
  newsletter/share-NNN.json  "time" (send date), "tags", "link" (Substack post)
  newsletter/launch.json     the same for issue 001
  newsletter/story-NNN.json  "series" when there are no tags
The send date falls back to Sunday 1 Nov 2026 plus one week per issue.
Rules: docs/WW2 Dispatches Newsletter.md ("Issue archive on ww2dispatches.com").
"""
import glob, html, json, os, re, sys
from datetime import date, datetime, time, timedelta, timezone
from zoneinfo import ZoneInfo

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from newsletter_page import parse, inline  # same reading of the issue file as the review page

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = "https://raw.githubusercontent.com/ww2dispatches/ww2dispatches-cards/main/"
CDN = "https://cdn.jsdelivr.net/gh/ww2dispatches/ww2dispatches-cards@main/"
SITE = "https://ww2dispatches.com"
SUBSTACK = "https://ww2dispatches.substack.com"
DENVER = ZoneInfo("America/Denver")
FIRST_SEND = date(2026, 11, 1)
SERIES = {"Battle Lines": "s-battle", "Home Front": "s-home", "Blueprint": "s-blue", "Statecraft": "s-state"}
MONTHS = "January February March April May June July August September October November December".split()


def esc(s):
    return html.escape(str(s), quote=True)


def cdn(url):
    return CDN + url[len(RAW):] if url.startswith(RAW) else url


def long_date(d):
    return f"{d.strftime('%A')} {d.day} {MONTHS[d.month - 1]} {d.year}"


def short_date(d):
    return f"{d.day} {MONTHS[d.month - 1][:3]} {d.year}"


def substack_slug(title):
    s = re.sub(r"[^a-z0-9\s-]", "", title.lower())
    return re.sub(r"[\s-]+", "-", s).strip("-")


def send_date(num, share, story):
    t = (share or {}).get("time", "")
    m = re.search(r"(\d{4})-(\d{2})-(\d{2})", t)
    if m:
        return date(int(m[1]), int(m[2]), int(m[3]))
    m = re.search(r"(\d{1,2}) ([A-Z][a-z]{2}) (\d{4})", t)
    if m:
        return datetime.strptime(f"{m[1]} {m[2]} {m[3]}", "%d %b %Y").date()
    week = (story or {}).get("week")
    if isinstance(week, list) and week:
        return date.fromisoformat(str(week[-1])[:10]) + timedelta(days=1)
    if isinstance(week, dict) and week.get("end"):
        return date.fromisoformat(str(week["end"])[:10]) + timedelta(days=1)
    return FIRST_SEND + timedelta(weeks=num - 1)


def load(path):
    try:
        return json.load(open(path, encoding="utf-8"))
    except (OSError, ValueError):
        return None


def read_issues():
    issues = []
    for path in sorted(glob.glob(os.path.join(ROOT, "newsletter", "issue-[0-9][0-9][0-9].md"))):
        num = int(re.search(r"issue-(\d{3})\.md$", path)[1])
        title, preview, blocks = parse(open(path, encoding="utf-8").read())
        share = load(os.path.join(ROOT, "newsletter", f"share-{num:03d}.json"))
        if share is None and num == 1:
            share = load(os.path.join(ROOT, "newsletter", "launch.json"))
        story = load(os.path.join(ROOT, "newsletter", f"story-{num:03d}.json"))
        tags = list((share or {}).get("tags") or [])
        if not tags and story and story.get("series"):
            tags = [story["series"]]
        sent = send_date(num, share, story)
        release = datetime.combine(sent, time(7, 0), DENVER).astimezone(timezone.utc)
        lead = next((v for k, v in blocks if k == "img"), None)
        issues.append({
            "num": num, "id": f"{num:03d}", "title": title, "preview": preview, "blocks": blocks,
            "tags": tags, "sent": sent, "release": release.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "link": (share or {}).get("link") or f"{SUBSTACK}/p/{substack_slug(title)}",
            "lead": (lead[0], cdn(lead[1])) if lead else None,
            "words": sum(len(v.split()) for k, v in blocks if k == "p"),
        })
    return issues


def tag_html(tags):
    out = []
    for t in tags:
        out.append(f'<span class="tag {SERIES.get(t, "s-theater")}">{esc(t)}</span>')
    return "".join(out)


def article_html(blocks):
    """The article body, the Also this week list, sources, and sign off."""
    out, i, first_p = [], 0, True
    while i < len(blocks):
        kind, val = blocks[i]
        if kind == "img":
            alt, src = val
            cap = blocks[i + 1][1] if i + 1 < len(blocks) and blocks[i + 1][0] == "cap" else ""
            out.append(f'<figure><img src="{esc(cdn(src))}" alt="{esc(alt)}" loading="{"eager" if not out else "lazy"}">'
                       + (f"<figcaption>{inline(cap)}</figcaption>" if cap else "") + "</figure>")
            i += 2 if cap else 1
            continue
        if kind == "h2":
            out.append(f"<h2>{inline(val)}</h2>")
        elif kind == "hr":
            out.append('<hr>')
        elif kind == "p":
            cls = ' class="first"' if first_p else ""
            first_p = False
            out.append(f"<p{cls}>{inline(val)}</p>")
        i += 1
    body = "\n".join(out)
    # Links leave the site in a new tab.
    return body.replace('<a href="http', '<a target="_blank" rel="noopener" href="http')


HEAD = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{title}</title>
<meta name="description" content="{desc}">
<meta name="theme-color" content="#120F0C">
<link rel="canonical" href="{url}">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="icon" href="/favicon-32.png" sizes="32x32" type="image/png">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
<meta property="og:type" content="{ogtype}">
<meta property="og:site_name" content="WW2 Dispatches">
<meta property="og:title" content="{ogtitle}">
<meta property="og:description" content="{desc}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{image}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:site" content="@ww2dispatches">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Oswald:wght@500;600;700&family=Special+Elite&family=Source+Sans+3:wght@400;600&family=Libre+Baskerville:ital,wght@0,400;0,700;1,400&display=swap">
<style>
/* Night Dispatch, like the home page: a sepia archival photo behind, paper on top. Built by renderer/newsletter_archive.py; do not edit by hand. */
:root {
  --night: #120F0C; --paper: #EDE4CF; --sheet: #F4EDDC; --ink: #1A1612; --red: #B04A3E; --navy: #3D5884; --brass: #D9A84A; --teal: #2B6A6C;
  --sand: #C9B98F; --line: rgba(237,228,207,.18); --panel: rgba(18,15,12,.62);
  --display: "Oswald", "Arial Narrow", Impact, sans-serif;
  --type: "Special Elite", "Courier New", Courier, monospace;
  --body: "Source Sans 3", "Segoe UI", system-ui, sans-serif;
  --serif: "Libre Baskerville", Georgia, "Times New Roman", serif;
  color-scheme: dark;
}
* { box-sizing: border-box; }
html { background: var(--night); }
body { margin: 0; background: var(--night); color: var(--paper); font-family: var(--body); min-height: 100vh; overflow-x: hidden; -webkit-text-size-adjust: 100%; }
a { color: inherit; }
:focus-visible { outline: 3px solid var(--brass); outline-offset: 3px; }
.backdrop { position: fixed; inset: 0; z-index: 0; pointer-events: none; background: url("/img/bg-dday.jpg") center 45% / cover no-repeat; filter: sepia(.35) contrast(1.05); }
.backdrop::after { content: ""; position: absolute; inset: 0;
  background: linear-gradient(180deg, rgba(18,15,12,.42) 0px, rgba(18,15,12,.74) 300px, rgba(18,15,12,.92) 600px, rgba(18,15,12,.95) 100%); }
@media (max-width: 700px) { .backdrop { background-image: url("/img/bg-dday-sm.jpg"); } }
.page { position: relative; z-index: 1; max-width: {width}px; margin: 0 auto;
  padding-left: max(16px, env(safe-area-inset-left, 0px)); padding-right: max(16px, env(safe-area-inset-right, 0px));
  padding-top: calc(22px + env(safe-area-inset-top, 0px)); padding-bottom: calc(40px + env(safe-area-inset-bottom, 0px));
  display: flex; flex-direction: column; gap: 24px; }
@media (min-width: 700px) { .page { padding-top: 40px; } }
.topbar { display: flex; align-items: center; justify-content: space-between; gap: 12px; }
.home, .back { display: flex; align-items: center; gap: 8px; text-decoration: none; font-family: var(--display); font-weight: 600;
  letter-spacing: 1.5px; text-transform: uppercase; font-size: 13px; color: var(--sand); }
.home svg { width: 28px; height: 28px; }
.home:hover, .back:hover { color: var(--paper); }
.mast { display: flex; flex-direction: column; align-items: center; text-align: center; gap: 10px; }
.mast h1 { font-family: var(--display); font-weight: 700; text-transform: uppercase; margin: 0; font-size: 42px; line-height: .98; letter-spacing: .5px;
  text-wrap: balance; text-shadow: 0 2px 18px rgba(0,0,0,.7); }
.mast h1 span { display: block; color: var(--brass); font-size: .5em; letter-spacing: 3px; margin-bottom: 8px; }
.lede { font-family: var(--type); margin: 0; font-size: 16px; line-height: 1.45; max-width: 40ch; text-shadow: 0 1px 8px rgba(0,0,0,.85); }
.tags { display: flex; flex-wrap: wrap; gap: 8px; }
.tag { font-family: var(--display); font-weight: 700; letter-spacing: 1.5px; text-transform: uppercase; font-size: 11.5px;
  border: 2px solid currentColor; padding: 1px 6px; transform: rotate(-2deg); white-space: nowrap; }
.s-battle { color: #E07A6C; } .s-home { color: #A9B87A; } .s-blue { color: #8FA6D6; } .s-state { color: #D9A84A; } .s-theater { color: var(--sand); }
.sheet .s-battle { color: var(--red); } .sheet .s-home { color: #5E6B3A; } .sheet .s-blue { color: var(--navy); } .sheet .s-state { color: #8E6618; } .sheet .s-theater { color: #6b604d; }

/* signup, same as the home page box */
.signup { background: var(--paper); color: var(--ink); border-radius: 6px; padding: 14px 14px 14px 18px; box-shadow: 0 0 0 2px var(--ink) inset, 0 10px 24px rgba(0,0,0,.45); }
.signup .head { display: flex; align-items: center; justify-content: space-between; gap: 10px; margin-bottom: 6px; }
.signup h3 { font-family: var(--display); font-weight: 700; text-transform: uppercase; font-size: 19px; letter-spacing: 1px; margin: 0; line-height: 1.05; }
.stampline { font-family: var(--display); font-weight: 700; letter-spacing: 2px; text-transform: uppercase; color: var(--teal); border: 2px solid var(--teal);
  padding: 1px 6px; transform: rotate(-3deg); font-size: 11px; white-space: nowrap; }
.signup p { font-family: var(--type); color: var(--navy); margin: 0 0 12px; font-size: 13.5px; line-height: 1.4; }
.signup form { display: flex; gap: 6px; }
.signup input { flex: 1 1 auto; min-width: 0; font: 16px var(--type); padding: 10px; border: 2px solid var(--ink); background: #F7F1E2; color: var(--ink); border-radius: 4px; }
.signup button { flex: 0 0 auto; font: 600 15px var(--display); letter-spacing: 1.5px; text-transform: uppercase; padding: 10px 14px;
  background: var(--teal); color: var(--paper); border: 2px solid var(--ink); border-radius: 4px; cursor: pointer; }
.signup button:hover { background: var(--ink); }
.signup .sent { margin: 10px 0 0; font-size: 13px; color: #4E5A2F; }
footer { text-align: center; font-family: var(--type); font-size: 13px; color: var(--sand); display: flex; flex-direction: column; gap: 4px; }
{css}
@media (prefers-reduced-motion: reduce) { * { transition: none !important; } }
</style>
</head>
<body>
<div class="backdrop" aria-hidden="true"></div>
<main class="page">
"""

BADGE = ('<svg viewBox="0 0 120 120" aria-hidden="true"><circle cx="60" cy="60" r="58" fill="#B04A3E"/><circle cx="60" cy="60" r="50" fill="none" '
         'stroke="#EDE4CF" stroke-width="4"/><text x="60" y="73" text-anchor="middle" font-family="Oswald, Arial Narrow, sans-serif" '
         'font-weight="700" font-size="38" fill="#EDE4CF">WW2</text></svg>')

SIGNUP = """<div class="signup">
    <div class="head"><h3>The Weekly Dispatch</h3><span class="stampline">Every Sunday</span></div>
    <p>{line}</p>
    <form class="nl-form" action="https://ww2dispatches.substack.com/api/v1/free?nojs=true" method="post" target="substack-signup">
      <input name="email" type="email" placeholder="your@email.com" required autocomplete="email" aria-label="Email address">
      <button type="submit">Subscribe</button>
    </form>
    <p class="sent" hidden>Almost done. Check your inbox to confirm.</p>
  </div>"""

TAIL = """  <footer><span>@ww2dispatches</span><span>Every dispatch checked against sources.</span><span>WW2 Dispatches is a Wraithlight Digital project.</span><span>© {year} Wraithlight Digital LLC</span><span><a href="/">Home</a> · <a href="/newsletter/">Past issues</a> · <a href="/privacy">Privacy</a></span></footer>
</main>
<iframe name="substack-signup" title="Newsletter signup" hidden></iframe>
<script>
// Signup posts to Substack in a hidden frame, so the reader stays on this page (same as the home page box).
document.querySelectorAll(".nl-form").forEach(function (f) {
  f.addEventListener("submit", function () {
    f.parentNode.querySelector(".sent").hidden = false;
    setTimeout(function () { f.reset(); }, 300);
  });
});
</script>
</body>
</html>
"""

LIST_CSS = """
.issues { list-style: none; margin: 0; padding: 0; display: flex; flex-direction: column; gap: 16px; }
.issue a { display: grid; grid-template-columns: 132px 1fr; text-decoration: none; background: var(--paper); color: var(--ink);
  border-radius: 6px; overflow: hidden; box-shadow: 0 10px 24px rgba(0,0,0,.45); transition: transform .15s, background .15s; }
.issue a:hover { background: #F5D6A0; transform: translateY(-2px); }
.issue .pic { background: #2a241d center / cover no-repeat; filter: sepia(.25); min-height: 150px; }
.issue .txt { padding: 14px 16px 16px; display: flex; flex-direction: column; gap: 6px; min-width: 0; }
.issue .meta { font-family: var(--display); font-weight: 600; letter-spacing: 1.5px; text-transform: uppercase; font-size: 12px; color: var(--teal); }
.issue h2 { margin: 0; font-family: var(--display); font-weight: 700; text-transform: uppercase; font-size: 22px; line-height: 1.05; letter-spacing: .3px; }
.issue p { margin: 0; font-family: var(--serif); font-size: 14px; line-height: 1.5; color: #3b342b; }
.issue .tags { margin-top: 4px; }
.issue.latest a { grid-template-columns: 1fr; }
.issue.latest .pic { min-height: 0; aspect-ratio: 16 / 9; }
.issue.latest h2 { font-size: 28px; }
.issue.latest .meta::after { content: " · Latest"; color: var(--red); }
@media (max-width: 520px) { .issue a { grid-template-columns: 1fr; } .issue .pic { min-height: 0; aspect-ratio: 16 / 9; } }
.empty { margin: 0; text-align: center; font-family: var(--type); color: var(--sand); }
"""

ISSUE_CSS = """
.sheet { background: var(--sheet); color: var(--ink); border-radius: 6px; box-shadow: 0 0 0 2px var(--ink) inset, 0 18px 40px rgba(0,0,0,.55); overflow: hidden; }
.band { display: flex; align-items: center; justify-content: space-between; gap: 10px; background: var(--ink); color: var(--paper); padding: 11px 18px; }
.band b { font-family: var(--display); font-weight: 700; font-size: 16px; letter-spacing: 3px; text-transform: uppercase; }
.band i { font-style: normal; font-family: var(--display); font-weight: 700; font-size: 11px; letter-spacing: 1.5px; color: #6FB3B5;
  border: 2px solid #6FB3B5; border-radius: 3px; padding: 2px 7px; transform: rotate(-4deg); white-space: nowrap; }
.art { padding: 26px 34px 34px; }
@media (max-width: 560px) { .art { padding: 20px 18px 26px; } }
.art header { text-align: center; padding-bottom: 18px; margin-bottom: 22px; border-bottom: 3px double rgba(26,22,18,.4); }
.art .dateline { font-family: var(--type); font-size: 13.5px; color: #5e5546; margin: 0 0 10px; }
.art h1 { font-family: var(--display); font-weight: 700; text-transform: uppercase; font-size: 44px; line-height: 1; margin: 0 0 12px; text-wrap: balance; letter-spacing: .3px; }
.art .standfirst { font-family: var(--serif); font-style: italic; font-size: 17px; line-height: 1.55; color: #3b342b; margin: 0 auto 14px; max-width: 34em; }
.art header .tags { justify-content: center; }
.art .byline { font-family: var(--display); font-weight: 600; letter-spacing: 1.5px; text-transform: uppercase; font-size: 12px; color: #6b604d; margin: 12px 0 0; }
.body { font-family: var(--serif); font-size: 17.5px; line-height: 1.75; }
@media (max-width: 560px) { .art h1 { font-size: 34px; } .body { font-size: 16.5px; } }
.body p { margin: 0 0 1.05em; }
.body p.first::first-letter { float: left; font-family: var(--display); font-weight: 700; font-size: 4.1em; line-height: .82; padding: .06em .1em 0 0; color: var(--red); }
.body h2 { font-family: var(--display); font-weight: 700; text-transform: uppercase; letter-spacing: .6px; font-size: 23px; line-height: 1.15; margin: 1.6em 0 .6em; }
.body figure { margin: 1.4em -34px; }
@media (max-width: 560px) { .body figure { margin: 1.3em -18px; } }
.body figure:first-child { margin-top: 0; }
.body img { display: block; width: 100%; height: auto; background: #2a241d; filter: sepia(.12); }
.body figcaption { font-family: var(--body); font-size: 14px; line-height: 1.45; color: #5e5546; padding: 8px 34px 0; }
@media (max-width: 560px) { .body figcaption { padding: 8px 18px 0; } }
.body a { color: var(--navy); text-decoration-thickness: 1px; text-underline-offset: 2px; }
.body hr { border: 0; height: 18px; margin: 2em 0 1.4em; background: radial-gradient(circle, rgba(26,22,18,.45) 2px, transparent 2.5px) center / 18px 18px repeat-x; }
.body hr ~ h2 { font-size: 18px; letter-spacing: 2px; color: #5e5546; margin-top: .4em; }
.body hr ~ p { font-family: var(--body); font-size: 15.5px; line-height: 1.5; margin-bottom: .7em; }
.body hr ~ p:last-child { font-family: var(--serif); font-style: italic; }
.after { display: flex; flex-direction: column; gap: 14px; }
.substack { text-align: center; font-family: var(--type); font-size: 14px; color: var(--sand); margin: 0; }
.substack a { color: var(--paper); }
.pager { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }
.pager a { display: flex; flex-direction: column; gap: 3px; padding: 12px 14px; border-radius: 4px; background: var(--panel); border: 1px solid var(--line); text-decoration: none; min-width: 0; }
.pager a:hover { border-color: var(--sand); }
.pager small { font-family: var(--display); font-weight: 600; letter-spacing: 1.5px; text-transform: uppercase; font-size: 11.5px; color: var(--sand); }
.pager b { font-family: var(--display); font-weight: 600; text-transform: uppercase; letter-spacing: .5px; font-size: 15px; line-height: 1.15; }
.pager .next { grid-column: 2; text-align: right; }
"""


def topbar(back):
    left = f'<a class="home" href="/" aria-label="WW2 Dispatches home">{BADGE} WW2 Dispatches</a>'
    right = '<a class="back" href="/newsletter/">All issues</a>' if back else ""
    return f'  <div class="topbar">{left}{right}</div>\n'


def head(**kw):
    out = HEAD
    for k, v in kw.items():
        out = out.replace("{" + k + "}", str(v))
    return out


def build_list(issues, year):
    items = []
    for n, it in enumerate(reversed(issues)):
        pic = f' style="background-image:url(\'{esc(it["lead"][1])}\')"' if it["lead"] else ""
        items.append(
            f'    <li class="issue" data-release="{it["release"]}"><a href="/newsletter/{it["id"]}">'
            f'<span class="pic" role="img" aria-label="{esc(it["lead"][0]) if it["lead"] else ""}"{pic}></span>'
            f'<span class="txt"><span class="meta">Issue {it["id"]} · {short_date(it["sent"])}</span>'
            f'<h2>{esc(it["title"])}</h2><p>{esc(it["preview"])}</p>'
            f'<span class="tags">{tag_html(it["tags"])}</span></span></a></li>')
    newest = issues[-1] if issues else None
    page = head(title="The Weekly Dispatch: past issues | WW2 Dispatches",
                desc="Every issue of The Weekly Dispatch, the free Sunday newsletter from WW2 Dispatches: one story from the war, told in full.",
                url=f"{SITE}/newsletter/", ogtype="website", ogtitle="The Weekly Dispatch: past issues",
                image=newest["lead"][1] if newest and newest["lead"] else f"{SITE}/img/og.jpg",
                width=560, css=LIST_CSS)
    page += topbar(False)
    page += ('  <header class="mast">\n    <h1><span>The Weekly Dispatch</span>Past issues</h1>\n'
             '    <p class="lede">One story from the war, told in full, every Sunday morning. Here is every issue so far.</p>\n  </header>\n')
    page += "  " + SIGNUP.replace("{line}", "Get the next one in your inbox, free.") + "\n"
    page += '  <ol class="issues" id="issues" reversed>\n' + "\n".join(items) + "\n  </ol>\n"
    page += '  <p class="empty" id="empty" hidden>The first issue lands Sunday morning.</p>\n'
    page += ('  <script>\n  // The server already drops unreleased issues; this marks the newest left as Latest.\n'
             '  (function () { var li = document.querySelector("#issues .issue"); if (li) li.classList.add("latest"); else document.getElementById("empty").hidden = false; })();\n'
             '  </script>\n')
    page += TAIL.replace("{year}", str(year))
    return page


def build_issue(it, prev, nxt, year):
    sent = it["sent"]
    desc = it["preview"] or it["title"]
    page = head(title=f'{esc(it["title"])} | The Weekly Dispatch', desc=esc(desc), url=f'{SITE}/newsletter/{it["id"]}',
                ogtype="article", ogtitle=esc(it["title"]), image=esc(it["lead"][1]) if it["lead"] else f"{SITE}/img/og.jpg",
                width=720, css=ISSUE_CSS)
    page += topbar(True)
    page += ('  <article class="sheet">\n'
             f'    <div class="band"><b>The Weekly Dispatch</b><i>Issue {it["id"]}</i></div>\n'
             '    <div class="art">\n      <header>\n'
             f'        <p class="dateline">{long_date(sent)} · about {max(1, round(it["words"] / 230))} minute read</p>\n'
             f'        <h1>{esc(it["title"])}</h1>\n'
             + (f'        <p class="standfirst">{inline(it["preview"])}</p>\n' if it["preview"] else "")
             + f'        <div class="tags">{tag_html(it["tags"])}</div>\n'
             '        <p class="byline">By WW2 Dispatches</p>\n      </header>\n'
             f'      <div class="body">\n{article_html(it["blocks"])}\n      </div>\n    </div>\n  </article>\n')
    page += '  <section class="after">\n'
    page += "    " + SIGNUP.replace("{line}", "Enjoyed this? Get the next story in your inbox every Sunday, free.") + "\n"
    page += f'    <p class="substack">Also on <a href="{esc(it["link"])}" target="_blank" rel="noopener">Substack</a>, where you can comment and share.</p>\n'
    nav = []
    if prev:
        nav.append(f'<a class="prev" href="/newsletter/{prev["id"]}"><small>Previous issue</small><b>{esc(prev["title"])}</b></a>')
    if nxt:
        nav.append(f'<a class="next" href="/newsletter/{nxt["id"]}" data-release="{nxt["release"]}"><small>Next issue</small><b>{esc(nxt["title"])}</b></a>')
    if nav:
        page += '    <nav class="pager" aria-label="More issues">' + "".join(nav) + "</nav>\n"
    page += "  </section>\n"
    page += TAIL.replace("{year}", str(year))
    return page


def main():
    issues = read_issues()
    out_dir = os.path.join(ROOT, "site", "newsletter")
    os.makedirs(out_dir, exist_ok=True)
    keep = set()
    for i, it in enumerate(issues):
        prev = issues[i - 1] if i > 0 else None
        nxt = issues[i + 1] if i + 1 < len(issues) else None
        name = f'{it["id"]}.html'
        keep.add(name)
        open(os.path.join(out_dir, name), "w", encoding="utf-8").write(build_issue(it, prev, nxt, it["sent"].year))
    keep.add("index.html")
    year = max([it["sent"].year for it in issues] + [2026])
    open(os.path.join(out_dir, "index.html"), "w", encoding="utf-8").write(build_list(issues, year))
    for f in os.listdir(out_dir):  # an issue file that was removed takes its page with it
        if f.endswith(".html") and f not in keep:  # issues.json is rewritten above
            os.remove(os.path.join(out_dir, f))
    # The home page's Latest line reads issues.json; the middleware drops unreleased issues from it.
    feed = [{"id": it["id"], "title": it["title"], "date": it["sent"].isoformat(), "release": it["release"]} for it in reversed(issues)]
    open(os.path.join(out_dir, "issues.json"), "w", encoding="utf-8").write(json.dumps(feed, indent=1, ensure_ascii=False) + "\n")
    data = {it["id"]: it["release"] for it in issues}
    open(os.path.join(ROOT, "functions", "_data", "newsletter.json"), "w", encoding="utf-8").write(json.dumps(data, indent=2) + "\n")
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    for it in issues:
        state = "live" if it["release"] <= now else "goes live " + it["release"]
        tags = ", ".join(it["tags"]) or "NOTE no tags"
        print(f'Issue {it["id"]} "{it["title"]}" sent {it["sent"]} ({state}), {tags}, {it["words"]} words')
        if "—" in it["title"] or "–" in it["title"]:
            print(f"PROBLEM dash in the title of issue {it['id']}")
    print(f"Wrote site/newsletter/ ({len(issues)} issues) and functions/_data/newsletter.json")
    write_sitemap([it for it in issues if it["release"] <= now])


# The site map search engines read (13 Nov 2026), rebuilt here because the issue list is what changes
# week to week. Released issues only. robots.txt points at it. Pages added later go in PAGES.
PAGES = ["/", "/declass", "/newsletter/", "/support", "/privacy"]


def write_sitemap(issues):
    urls = [SITE + p for p in PAGES] + [f'{SITE}/newsletter/{it["id"]}' for it in issues]
    body = "".join(f"  <url><loc>{html.escape(u)}</loc></url>\n" for u in urls)
    xml = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + body + "</urlset>\n"
    open(os.path.join(ROOT, "site", "sitemap.xml"), "w", encoding="utf-8").write(xml)


if __name__ == "__main__":
    main()
