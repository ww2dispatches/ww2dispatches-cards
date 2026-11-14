#!/usr/bin/env python3
"""Build the Weekly Dispatch issue archive on ww2dispatches.com.

Usage: python3 renderer/newsletter_archive.py

Reads every newsletter/issue-NNN.md and writes, with the shared site header and Substack style covers
(Site Revamp doc; the cover is made from the issue's first photo, so it needs no new artwork):
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
            "pos": (share or {}).get("coverPos") or "50% 30%",
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


import site_pages  # shared header, footer, and page frame (Site Revamp, Nov 2026)

# Covers (Site Revamp doc, board 7 and P5): made by the page from the issue's lead photo, styled
# after Substack's: full bleed black and white photo, dark shadow at the bottom, the title in large
# white Libre Baskerville, the summary, "WW2 Dispatches · date" in italic, and a cream tab top left.
# coverPos in share-NNN.json (or launch.json for 001) sets the photo's focus; default 50% 30%.
NL_CSS = """<style>
/* Built by renderer/newsletter_archive.py; do not edit by hand. */
.cover { position: relative; display: block; overflow: hidden; background: #222; text-decoration: none; color: #fff; }
.cover > img { position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; filter: grayscale(1) contrast(1.05); }
.cover::after { content: ""; position: absolute; inset: 0; background: linear-gradient(180deg, rgba(0,0,0,0) 30%, rgba(0,0,0,.6) 55%, rgba(0,0,0,.86) 100%); }
.ctab { position: absolute; z-index: 1; top: 20px; left: 20px; background: var(--cream); color: var(--ink); padding: 4px 9px; font: 600 11px var(--display); letter-spacing: 2.5px; text-transform: uppercase; }
.ctext { position: absolute; z-index: 1; left: 20px; right: 20px; bottom: 20px; display: flex; flex-direction: column; gap: 10px; }
.ctitle { font-family: var(--serif); font-weight: 400; font-size: 32px; line-height: 1.12; margin: 0; text-wrap: balance; }
.cdek { font-family: var(--serif); font-size: 16px; line-height: 1.5; color: #F2EEE6; margin: 0; }
.cdate { font-family: var(--serif); font-style: italic; font-size: 14px; color: #D8D2C6; }
.nlpage .pagehead h1 { font-family: var(--serif); font-weight: 400; text-transform: none; font-size: 34px; line-height: 1.1; }
.nlgrid { max-width: 1180px; margin: 0 auto; padding: 14px 16px 10px; display: flex; flex-direction: column; gap: 22px; }
.lead .cover { height: 600px; max-height: 82vh; min-height: 480px; }
.earlier h2 { margin: 8px 0 12px; font-family: var(--display); font-weight: 400; font-size: 15px; letter-spacing: 3px; color: var(--sand); text-transform: uppercase; }
.issues { list-style: none; margin: 0; padding: 0; display: flex; flex-direction: column; gap: 14px; }
.issue a { display: flex; gap: 14px; text-decoration: none; color: var(--paper); }
.issue .cover { flex: none; width: 112px; height: 190px; }
.issue .cover .ctitle { font-size: 13px; line-height: 1.15; } .issue .ctext { left: 8px; right: 8px; bottom: 8px; }
.issue .itxt { display: flex; flex-direction: column; gap: 6px; padding-top: 4px; min-width: 0; }
.issue .ino { font-family: var(--type); font-size: 12px; color: var(--sand); }
.issue .ititle { font-family: var(--serif); font-size: 19px; line-height: 1.2; }
.issue .idek { font-size: 14px; line-height: 1.45; color: var(--dim); display: -webkit-box; -webkit-line-clamp: 4; -webkit-box-orient: vertical; overflow: hidden; }
.issue a:hover .ititle { text-decoration: underline; }
.empty { margin: 0; font-family: var(--type); color: var(--sand); }
@media (min-width: 900px) {
  .nlpage .pagehead { padding: 40px 40px 6px; } .nlpage .pagehead h1 { font-size: 48px; }
  .nlgrid { padding: 20px 40px 20px; display: grid; grid-template-columns: minmax(0, 1.25fr) minmax(0, 1fr); gap: 28px 40px; align-items: start; }
  .lead .cover { height: 640px; max-height: none; } .lead .ctitle { font-size: 42px; } .lead .cdek { font-size: 18px; }
  .nlside { position: sticky; top: 100px; }
  .earlier { grid-column: 1 / -1; }
  .issues { display: grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); gap: 24px; }
}
/* issue page: the same contained cover as the list's latest issue, with the article sheet under it */
.iwrap { max-width: 760px; margin: 0 auto; padding: 4px 16px 30px; }
.iwrap .backlink { padding-left: 0; }
.icover .cover { height: 560px; max-height: 80vh; min-height: 460px; }
.icover .ctitle { font-size: 34px; }
.paper { background: var(--sheet); color: var(--ink); }
.paperin { max-width: 720px; margin: 0 auto; padding: 22px 20px 30px; display: flex; flex-direction: column; gap: 16px; }
.imeta { margin: 0; font-family: var(--type); font-size: 12.5px; color: #5A4E3E; }
.covercap { margin: -8px 0 0; font-size: 13px; line-height: 1.45; color: #5A4E3E; }
.tags { display: flex; flex-wrap: wrap; gap: 8px; }
.tag { font-family: var(--display); font-weight: 700; letter-spacing: 1.5px; text-transform: uppercase; font-size: 11.5px; border: 2px solid currentColor; padding: 1px 6px; transform: rotate(-2deg); white-space: nowrap; }
.paper .s-battle { color: var(--red); } .paper .s-home { color: #5E6B3A; } .paper .s-blue { color: var(--navy); } .paper .s-state { color: #8E6618; } .paper .s-theater { color: #6b604d; }
.body { font-family: var(--serif); font-size: 17px; line-height: 1.75; }
.body p { margin: 0 0 1.05em; }
.body p.first::first-letter { float: left; font-family: var(--display); font-weight: 700; font-size: 4.1em; line-height: .82; padding: .06em .1em 0 0; color: var(--red); }
.body h2 { font-family: var(--serif); font-weight: 700; font-size: 22px; line-height: 1.25; margin: 1.5em 0 .6em; }
.body figure { margin: 1.4em -20px; }
.body img { display: block; width: 100%; height: auto; background: #2a241d; filter: grayscale(1); }
.body figcaption { font-family: var(--body); font-size: 13.5px; line-height: 1.45; color: #5A4E3E; padding: 8px 20px 0; }
.body a { color: var(--navy); text-decoration-thickness: 1px; text-underline-offset: 2px; }
.body hr { border: 0; height: 18px; margin: 2em 0 1.4em; background: radial-gradient(circle, rgba(26,22,18,.45) 2px, transparent 2.5px) center / 18px 18px repeat-x; }
.body hr ~ h2 { font-family: var(--display); text-transform: uppercase; font-size: 17px; letter-spacing: 2px; color: #5e5546; margin-top: .4em; }
.body hr ~ p { font-family: var(--body); font-size: 15.5px; line-height: 1.5; margin-bottom: .7em; }
.body hr ~ p:last-child { font-family: var(--serif); font-style: italic; }
.paper .subscribe { box-shadow: inset 0 0 0 1px rgba(26,22,18,.25); }
.substack { margin: 0; text-align: center; font-family: var(--type); font-size: 14px; color: #5A4E3E; }
.substack a { color: var(--ink); }
.pager { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }
.pager a { display: flex; flex-direction: column; gap: 3px; padding: 12px 14px; min-height: 44px; border: 1px solid rgba(26,22,18,.3); text-decoration: none; min-width: 0; }
.pager a:hover { border-color: var(--ink); }
.pager small { font-family: var(--display); letter-spacing: 1.5px; text-transform: uppercase; font-size: 11.5px; color: #5A4E3E; }
.pager b { font-family: var(--serif); font-weight: 400; font-size: 15px; line-height: 1.25; }
.pager .next { grid-column: 2; text-align: right; }
.allbtn { color: var(--ink); box-shadow: inset 0 0 0 1px var(--ink); }
@media (min-width: 700px) {
  .iwrap { padding: 16px 32px 50px; }
  .icover .cover { height: 620px; max-height: none; } .icover .ctab { top: 24px; left: 28px; } .icover .ctext { left: 28px; right: 28px; bottom: 28px; }
  .icover .ctitle { font-size: 44px; } .icover .cdek { font-size: 18px; }
  .paperin { padding: 36px 34px 44px; } .body { font-size: 18px; } .body figure { margin: 1.4em -34px; } .body figcaption { padding: 8px 34px 0; }
}
</style>
"""

SIGNUP = """<div class="subscribe">
    <h2>Get the next one free</h2>
    <p>One remarkable story from that week in the war, told in full. Every Sunday morning.</p>
    <form class="nl-form" action="https://ww2dispatches.substack.com/api/v1/free?nojs=true" method="post" target="substack-signup">
      <label class="sr" for="{fid}">Email</label>
      <input id="{fid}" name="email" type="email" placeholder="you@example.com" required autocomplete="email">
      <button type="submit">Subscribe</button>
    </form>
    <p class="sent" hidden>Almost done. Check your inbox to confirm.</p>
  </div>"""

BACK = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M15 5l-7 7 7 7"/></svg>'


def tag_html(tags):
    return "".join(f'<span class="tag {SERIES.get(t, "s-theater")}">{esc(t)}</span>' for t in tags)


def article_html(blocks):
    """The article body, the Also this week list, sources, and sign off."""
    out, i, first_p = [], 0, True
    while i < len(blocks):
        kind, val = blocks[i]
        if kind == "img":
            alt, src = val
            cap = blocks[i + 1][1] if i + 1 < len(blocks) and blocks[i + 1][0] == "cap" else ""
            out.append(f'<figure><img src="{esc(cdn(src))}" alt="{esc(alt)}" loading="lazy">'
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


def split_lead(blocks):
    """The first photo becomes the cover, so the article starts after it (and its caption)."""
    if blocks and blocks[0][0] == "img":
        cap = blocks[1][1] if len(blocks) > 1 and blocks[1][0] == "cap" else ""
        return cap, blocks[2 if cap else 1:]
    return "", blocks


def cover_html(it, tag="div", href="", heading="span", eager=False):
    img = (f'<img src="{esc(it["lead"][1])}" alt="" style="object-position:{esc(it["pos"])}" loading="{"eager" if eager else "lazy"}">' if it["lead"] else "")
    attrs = f' href="{href}"' if href else ""
    return (f'<{tag} class="cover"{attrs}>{img}<span class="ctab">The Weekly Dispatch · No. {it["id"]}</span>'
            f'<span class="ctext"><{heading} class="ctitle">{esc(it["title"])}</{heading}>'
            + (f'<span class="cdek">{inline(it["preview"])}</span>' if it["preview"] and heading != "small" else "")
            + f'<span class="cdate">WW2 Dispatches · {long_date(it["sent"])}</span></span></{tag}>')


def build_list(issues, year):
    items = []
    for it in reversed(issues):
        items.append(
            f'      <li class="issue" data-release="{it["release"]}" data-id="{it["id"]}"><a href="/newsletter/{it["id"]}" aria-label="Read {esc(it["title"])}">'
            f'<span class="cover">{f"""<img src="{esc(it["lead"][1])}" alt="" style="object-position:{esc(it["pos"])}" loading="lazy">""" if it["lead"] else ""}'
            f'<span class="ctext"><span class="ctitle">{esc(it["title"])}</span></span></span>'
            f'<span class="itxt"><span class="ino">No. {it["id"]} · {it["sent"].day} {MONTHS[it["sent"].month - 1]}</span>'
            f'<span class="ititle">{esc(it["title"])}</span><span class="idek">{esc(it["preview"])}</span></span></a>'
            f'<template>{cover_html(it, "a", "/newsletter/" + it["id"])}</template></li>')
    newest = issues[-1] if issues else None
    body = f"""<main class="nlpage">
  <header class="pagehead"><span class="kicker">Every Sunday</span><h1>The Weekly Dispatch</h1><p>One story from the war, told in full.</p></header>
  <div class="nlgrid">
    <div class="lead" id="lead"></div>
    <div class="nlside">{SIGNUP.replace("{fid}", "em")}</div>
    <section class="earlier" id="earlier" aria-labelledby="earlier-h">
      <h2 id="earlier-h">Earlier issues</h2>
      <ol class="issues" id="issues">
{chr(10).join(items)}
      </ol>
    </section>
    <p class="empty" id="empty" hidden>The first issue lands Sunday morning.</p>
  </div>
</main>
<iframe name="substack-signup" title="Newsletter signup" hidden></iframe>
<script>
// The server already drops unreleased issues; the newest one left becomes the tall cover on top.
(function () {{
  var li = document.querySelector("#issues .issue");
  if (!li) {{ document.getElementById("empty").hidden = false; document.getElementById("earlier").hidden = true; return; }}
  document.getElementById("lead").appendChild(li.querySelector("template").content.cloneNode(true));
  li.remove();
  if (!document.querySelector("#issues .issue")) document.getElementById("earlier").hidden = true;
}})();
</script>"""
    return site_pages.page("The Weekly Dispatch | WW2 Dispatches",
                           "Every issue of The Weekly Dispatch, the free Sunday newsletter from WW2 Dispatches: one story from the war, told in full.",
                           "/newsletter/", body, "newsletter", image=newest["lead"][1] if newest and newest["lead"] else None, head_extra=NL_CSS)


def build_issue(it, prev, nxt, year):
    cap, blocks = split_lead(it["blocks"])
    nav = []
    if prev:
        nav.append(f'<a class="prev" href="/newsletter/{prev["id"]}"><small>Previous issue</small><b>{esc(prev["title"])}</b></a>')
    if nxt:
        nav.append(f'<a class="next" href="/newsletter/{nxt["id"]}" data-release="{nxt["release"]}"><small>Next issue</small><b>{esc(nxt["title"])}</b></a>')
    tags = tag_html(it["tags"])
    body = f"""<main class="issuepage">
  <div class="iwrap">
  <a class="backlink" href="/newsletter/">{BACK} All issues</a>
  <div class="icover">{cover_html(it, "div", heading="h1", eager=True)}</div>
  <article class="paper"><div class="paperin">
    <p class="imeta">{long_date(it["sent"])} · about {max(1, round(it["words"] / 230))} minute read · By WW2 Dispatches</p>
    {f'<p class="covercap">Cover: {inline(cap)}</p>' if cap else ""}
    {f'<div class="tags">{tags}</div>' if tags else ""}
    <div class="body">
{article_html(blocks)}
    </div>
    {SIGNUP.replace("{fid}", "em")}
    <p class="substack">Also on <a href="{esc(it["link"])}" target="_blank" rel="noopener">Substack</a>, where you can comment and share.</p>
    {'<nav class="pager" aria-label="More issues">' + "".join(nav) + "</nav>" if nav else ""}
    <a class="btn allbtn" href="/newsletter/">Back to all issues</a>
  </div></article>
  </div>
</main>
<iframe name="substack-signup" title="Newsletter signup" hidden></iframe>"""
    return site_pages.page(f'{it["title"]} | The Weekly Dispatch', it["preview"] or it["title"], f'/newsletter/{it["id"]}', body, "newsletter",
                           image=it["lead"][1] if it["lead"] else None, ogtype="article", ogtitle=it["title"], head_extra=NL_CSS)


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
    feed = [{"id": it["id"], "title": it["title"], "date": it["sent"].isoformat(), "release": it["release"],
             "cover": it["lead"][1] if it["lead"] else "", "pos": it["pos"], "dek": it["preview"]} for it in reversed(issues)]
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
PAGES = ["/", "/declass", "/newsletter/", "/campaign-series/", "/name-this/", "/support", "/privacy"]


def campaign_urls():
    """Campaign Series volume pages and the day pages already posted (renderer/site_pages.py writes the times)."""
    path = os.path.join(ROOT, "functions", "_data", "releases.json")
    if not os.path.exists(path):
        return []
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    out = []
    for vid, days in (json.load(open(path, encoding="utf-8")).get("campaigns") or {}).items():
        out.append(f"{SITE}/campaign-series/{vid}/")
        out += [f"{SITE}/campaign-series/{vid}/day-{nn}" for nn, at in sorted(days.items()) if at <= now]
    return out


def write_sitemap(issues):
    urls = [SITE + p for p in PAGES] + [f'{SITE}/newsletter/{it["id"]}' for it in issues] + campaign_urls()
    body = "".join(f"  <url><loc>{html.escape(u)}</loc></url>\n" for u in urls)
    xml = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + body + "</urlset>\n"
    open(os.path.join(ROOT, "site", "sitemap.xml"), "w", encoding="utf-8").write(xml)


if __name__ == "__main__":
    main()
