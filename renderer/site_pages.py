#!/usr/bin/env python3
"""Build the ww2dispatches.com pages that come from the records (Site Revamp doc).

Run from the repo root:  python3 renderer/site_pages.py
site_data.py runs this at its end (and series_log.py runs site_data.py), so every weekly run
and every Campaign Series sitting that rebuilds the logs refreshes these pages with no extra step.
Never edit the files it writes by hand.

Writes:
  site/campaign-series/index.html            the Campaign Shelf
  site/campaign-series/shelf.json            the shelf data (home page teaser)
  site/campaign-series/<series>/index.html   a volume page (list of days)
  site/campaign-series/<series>/day-NN.html  one page per day, its own address for sharing
  site/campaign-series/<series>.json         the volume data (sealed days are cut by the server)
  site/campaign-series/<series>/thumbs/      small day thumbnails; covers/ the shelf cover photos
  site/name-this/index.html, cases.json      Name This: the open case and the Evidence Drawer
  functions/_data/releases.json              post times the server gates on
and refreshes the shared header and footer (CHROME) in the hand written pages
(site/index.html, support.html, privacy.html), between their <!--chrome:...--> markers.

Release rule: a Campaign Series day shows once 6:30 a.m. Mountain on its run date has passed
(the record's time field), and a Name This puzzle joins the drawer once the next one has posted.
The server (functions/campaign-series and functions/name-this middleware) enforces both, so a
page never shows a day or an answer early. Shelf data: campaign-series/shelf.json (edit by hand).
"""
import base64, datetime as dt, glob, hashlib, html, json, os, re, sys
from zoneinfo import ZoneInfo

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(ROOT, "site")
URL = "https://ww2dispatches.com"
CDN = "https://cdn.jsdelivr.net/gh/ww2dispatches/ww2dispatches-cards@main/"
DENVER = ZoneInfo("America/Denver")
UTC = dt.timezone.utc
MONTHS = "January February March April May June July August September October November December".split()
DAYS = "Monday Tuesday Wednesday Thursday Friday Saturday Sunday".split()
SERIES = {"battle": ("Battle Lines", "s-battle", "#B04A3E"), "home": ("Home Front", "s-home", "#5E6B3A"),
          "blue": ("Blueprint", "s-blue", "#3D5884"), "state": ("Statecraft", "s-state", "#B8862B")}
THREADS = "https://www.threads.com/@ww2dispatches"
X = "https://x.com/ww2dispatches"
INSTAGRAM = "https://www.instagram.com/ww2dispatches"
PROBLEMS = []


def esc(s):
    return html.escape(str(s if s is not None else ""), quote=True)


def problem(msg):
    PROBLEMS.append(msg)


def cdn(rel):
    """jsDelivr link with a short content hash, so a changed file is never served stale."""
    path = os.path.join(ROOT, rel)
    if not os.path.exists(path):
        return None
    v = hashlib.sha1(open(path, "rb").read()).hexdigest()[:8]
    return f"{CDN}{rel}?v={v}"


def iso(t):
    return t.astimezone(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def clock(hhmm):
    h, m = map(int, hhmm.split(":"))
    return f"{h % 12 or 12}:{m:02d} {'a.m.' if h < 12 else 'p.m.'}" if m else f"{h % 12 or 12} {'a.m.' if h < 12 else 'p.m.'}"


def d_short(d):
    return f"{d.day} {MONTHS[d.month - 1][:3]}"


def d_long(d):
    return f"{DAYS[d.weekday()]}, {d.day} {MONTHS[d.month - 1]} {d.year}"


def no_dash(text, where):
    if re.search(r"[–—]| - ", text or ""):
        problem(f"dash in {where}")


# ---------------------------------------------------------------------------------------------
# Shared header and footer (CHROME). One copy, written into every page except inside Declass.
# ---------------------------------------------------------------------------------------------
BADGE = ('<svg viewBox="0 0 120 120" aria-hidden="true"><circle cx="60" cy="60" r="58" fill="#B04A3E"/><circle cx="60" cy="60" r="50" fill="none" stroke="#EDE4CF" stroke-width="3"/>'
         '<circle cx="60" cy="60" r="44" fill="none" stroke="#EDE4CF" stroke-width="1.5"/><g transform="translate(28.00 73.58) scale(0.03354 -0.03354)" fill="#EDE4CF">'
         '<path d="M125 0 27 810H179L227 338L288 809H407L471 341L520 810H670L573 0H417L348 489L283 0Z"/>'
         '<path transform="translate(697 0)" d="M125 0 27 810H179L227 338L288 809H407L471 341L520 810H670L573 0H417L348 489L283 0Z"/>'
         '<path transform="translate(1394 0)" d="M41 0V118L235 416Q257 449 276.5 480.0Q296 511 308.5 543.0Q321 575 321 610Q321 645 307.0 662.0Q293 679 269 679Q242 679 227.0 664.0Q212 649 206.5 624.0Q201 599 201 568V528H39V571Q39 643 62.0 699.5Q85 756 135.0 788.5Q185 821 266 821Q375 821 430.5 764.5Q486 708 486 607Q486 558 470.5 516.0Q455 474 429.5 434.5Q404 395 375 352L227 131H464V0Z"/></g></svg>')
NAV = [("today", "/#today", "Today"), ("campaign", "/campaign-series/", "Campaign Series"), ("namethis", "/name-this/", "Name This"),
       ("newsletter", "/newsletter/", "Weekly Dispatch"), ("support", "/support", "Support")]
MENU_ICON = ('<svg class="m-open" viewBox="0 0 24 24" aria-hidden="true"><path d="M4 7h16M4 12h16M4 17h16"/></svg>'
             '<svg class="m-close" viewBox="0 0 24 24" aria-hidden="true"><path d="M6 6l12 12M18 6L6 18"/></svg>')


def header(active="", home=False):
    cur = lambda k: ' aria-current="page"' if k == active else ""
    links = "".join(f'<a href="{href}"{cur(k)}>{label}</a>' for k, href, label in NAV)
    # The phone menu lists Declass as a plain row near the end; the gold button is desktop only.
    menu = "".join(f'<a href="{href}"{cur(k)}>{label}</a>' for k, href, label in NAV[:4])
    menu += f'<a class="declass-link" href="/declass">Play Declass</a><a href="/support"{cur("support")}>Support</a>'
    return ("<!--chrome:header-->\n"
            f'<header class="sitebar{" home" if home else ""}">'
            f'<a class="brand" href="/" aria-label="WW2 Dispatches home">{BADGE}<span>WW2 Dispatches</span></a>'
            f'<nav class="mainnav" aria-label="Main"><a class="nav-play" href="/declass">Play Declass</a>{links}</nav>'
            f'<button class="menubtn" type="button" aria-label="Menu" aria-expanded="false" aria-controls="sitemenu">{MENU_ICON}</button></header>\n'
            f'<div class="sitemenu" id="sitemenu" hidden><nav aria-label="Menu">{menu}</nav></div>\n'
            "<!--/chrome:header-->")


def footer(year=2026):
    return ("<!--chrome:footer-->\n"
            '<footer class="sitefoot"><span>@ww2dispatches</span><span>Every dispatch checked against sources.</span>'
            f'<span>WW2 Dispatches is a Wraithlight Digital project.</span><span>© {year} Wraithlight Digital LLC</span>'
            '<span><a href="/privacy">Privacy</a></span></footer>\n'
            "<!--/chrome:footer-->")


FONTS = ('<link rel="preconnect" href="https://fonts.googleapis.com">\n<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
         '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Oswald:wght@400;500;600;700&family=Special+Elite'
         '&family=Source+Sans+3:wght@400;600&family=Libre+Baskerville:ital,wght@0,400;0,700;1,400&display=swap">')


def page(title, desc, path, body, active="", image=None, ogtype="website", ogtitle=None, head_extra="", script=""):
    image = image or f"{URL}/img/og.jpg"
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<script>/* www.ww2dispatches.com shows the same site; send it to the main address so sign in and saved state stay in one place (13 Nov 2026). */if(location.hostname==="www.ww2dispatches.com")location.replace("https://ww2dispatches.com"+location.pathname+location.search+location.hash);</script>
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<meta name="theme-color" content="#120F0C">
<link rel="canonical" href="{URL}{path}">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="icon" href="/favicon-32.png" sizes="32x32" type="image/png">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
<meta property="og:type" content="{ogtype}">
<meta property="og:site_name" content="WW2 Dispatches">
<meta property="og:title" content="{esc(ogtitle or title)}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:url" content="{URL}{path}">
<meta property="og:image" content="{esc(image)}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:site" content="@ww2dispatches">
{FONTS}
<link rel="stylesheet" href="/site.css?v={asset_v('site.css')}">
{head_extra}</head>
<body>
<!-- Built by renderer/site_pages.py; do not edit by hand. -->
{header(active)}
{body}
{footer()}
<script src="/site.js?v={asset_v('site.js')}"></script>
{script}<script src="/hit.js" defer></script>
</body>
</html>
"""


def asset_v(name):
    p = os.path.join(SITE, name)
    return hashlib.sha1(open(p, "rb").read()).hexdigest()[:8] if os.path.exists(p) else "1"


def sync_chrome():
    """Rewrite the header and footer blocks in the hand written pages so every page matches."""
    pages = {"index.html": dict(active="today", home=True), "support.html": dict(active="support"), "privacy.html": dict(active=""), "404.html": dict(active="")}
    for name, kw in pages.items():
        path = os.path.join(SITE, name)
        if not os.path.exists(path):
            continue
        text = open(path, encoding="utf-8").read()
        new = re.sub(r"<!--chrome:header-->.*?<!--/chrome:header-->", lambda m: header(**kw), text, flags=re.S)
        new = re.sub(r"<!--chrome:footer-->.*?<!--/chrome:footer-->", lambda m: footer(), new, flags=re.S)
        new = re.sub(r'(/site\.(css|js))\?v=[0-9a-f]+', lambda m: f"{m[1]}?v={asset_v('site.' + m[2])}", new)
        if "<!--chrome:header-->" not in text:
            problem(f"site/{name} has no <!--chrome:header--> markers; its header was not refreshed")
        if new != text:
            open(path, "w", encoding="utf-8").write(new)


# ---------------------------------------------------------------------------------------------
# Campaign Series
# ---------------------------------------------------------------------------------------------
def save_jpeg(src, dest, width, height=None, quality=78):
    """Resize a photo for the site (the same input always gives the same file, so git sees no change)."""
    from PIL import Image, ImageOps
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    im = ImageOps.exif_transpose(Image.open(src)).convert("RGB")
    if height:
        im = ImageOps.fit(im, (width, height), Image.LANCZOS, centering=(0.5, 0.4))
    elif im.width > width:
        im = im.resize((width, round(im.height * width / im.width)), Image.LANCZOS)
    im.save(dest, "JPEG", quality=quality, optimize=True, progressive=True)


def load_volume(vol):
    """The day records of a live volume, each with its run date and release time."""
    folder = os.path.join(ROOT, "campaign-series", vol["id"])
    recs = sorted((json.load(open(p, encoding="utf-8")) for p in glob.glob(os.path.join(folder, "day-[0-9][0-9].json"))), key=lambda r: r["day"])
    year, last = vol.get("runYear", 2026), None
    days = []
    for r in recs:
        hist = dt.date.fromisoformat(r["date"])
        if r.get("postDate"):
            run = dt.date.fromisoformat(r["postDate"])
        else:
            md = r["date"][5:]
            if last and md < last:
                year += 1
            last = md
            run = dt.date(year, hist.month, hist.day)
        hhmm = r.get("time") or "06:30"
        rel = dt.datetime.combine(run, dt.time(*map(int, hhmm.split(":"))), DENVER)
        n = int(r["day"])
        nn = f"{n:02d}"
        img_rel = f"campaign-series/{vol['id']}/images/day-{nn}-instagram.jpg"
        img = cdn(img_rel)
        if not img:
            problem(f"{vol['id']} day {nn}: no post image ({img_rel})")
        else:
            save_jpeg(os.path.join(ROOT, img_rel), os.path.join(SITE, "campaign-series", vol["id"], "thumbs", f"day-{nn}.jpg"), 300, 375, 72)
        sources = []
        for s in r.get("sources") or []:
            u = s.get("url") if isinstance(s, dict) else s
            t = s.get("title") if isinstance(s, dict) else None
            host = re.sub(r"^www\.", "", re.sub(r"^https?://([^/]+).*$", r"\1", u or ""))
            sources.append({"url": u, "label": t or host})
        for key in ("subtitle", "body", "photoCredit", "place"):
            no_dash(r.get(key), f"{vol['id']} day {nn} {key}")
        name, cls, color = SERIES.get(r.get("series"), ("", "", "#C9B98F"))
        days.append({
            "n": n, "nn": nn, "date": r["date"], "hist": hist, "run": run, "release": iso(rel),
            "arrives": f"Arrives {d_short(run)}, {clock(hhmm)} MT",
            "subtitle": r.get("subtitle", ""), "place": r.get("place", ""), "series": name, "seriesCls": cls, "seriesColor": color,
            "body": r.get("body", ""), "credit": r.get("photoCredit", ""), "sources": sources, "img": img,
            "alt": r.get("alt") or f"{vol['title']}, Day {n}. {r.get('photoCredit', '')}",
            "thumb": f"/campaign-series/{vol['id']}/thumbs/day-{nn}.jpg",
            "url": f"/campaign-series/{vol['id']}/day-{nn}",
        })
    return days


def tab_html(vol, days):
    return (f'<div class="vtab"><span class="vtab-k">VOL. {esc(vol["vol"])} · CAMPAIGN SERIES</span>'
            f'<span class="vtab-t" style="color:{esc(vol["cloth"])}">{esc(vol["title"])}</span>'
            f'<span class="vtab-d">{esc(vol["dates"])} · {len(days)} days</span></div>')


def build_volume(vol, days):
    vid, total = vol["id"], len(days)
    out_dir = os.path.join(SITE, "campaign-series", vid)
    os.makedirs(out_dir, exist_ok=True)
    cover = f"/campaign-series/covers/{vid}.jpg"
    first = days[0]
    start = (f'<a class="btn red start" href="{first["url"]}" data-release="{first["release"]}">Start at Day 1</a>'
             f'<p class="btn ghost start sealed" aria-disabled="true" data-until="{first["release"]}">Day 1 {esc(first["arrives"][0].lower() + first["arrives"][1:])}</p>')
    rows = []
    for d in days:
        rows.append(
            f'<li class="day" data-release="{d["release"]}"><a href="{d["url"]}">'
            f'<img src="{d["thumb"]}" alt="" width="64" height="80" loading="lazy">'
            f'<span class="day-t"><span class="day-k">Day {d["n"]} · {d_short(d["hist"])}</span><span class="day-s">{esc(d["subtitle"])}</span></span>'
            f'<svg class="chev" viewBox="0 0 24 24" aria-hidden="true"><path d="M9 5l7 7-7 7"/></svg></a></li>'
            f'<li class="day sealed" data-until="{d["release"]}"><span class="seal-img" aria-hidden="true"><span>SEALED</span></span>'
            f'<span class="day-t"><span class="day-k">Day {d["n"]} · {d_short(d["hist"])}</span><span class="day-s">{esc(d["arrives"])}</span></span></li>')
    body = f"""<main class="volume">
  <a class="backlink" href="/campaign-series/"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M15 5l-7 7 7 7"/></svg> The Campaign Shelf</a>
  <div class="vbanner"><img src="{cover}" alt="" style="object-position:{esc(vol.get('coverPos', '50% 40%'))}">{tab_html(vol, days)}</div>
  <div class="vbody">
    <p class="vintro">{esc(vol.get("intro", ""))} Tap a day to read it. A new day posts each morning at 6:30 Mountain.</p>
    {start}
    <ol class="days" aria-label="Days of {esc(vol['title'])}">
      {chr(10).join("      " + r for r in rows).strip()}
    </ol>
  </div>
</main>"""
    desc = f"{vol['title']}, day by day: {vol.get('blurb', '')}"
    open(os.path.join(out_dir, "index.html"), "w", encoding="utf-8").write(
        page(f"{vol['title']} | Campaign Series | WW2 Dispatches", desc, f"/campaign-series/{vid}/", body, "campaign",
             image=f"{URL}{cover}", ogtitle=f"{vol['title']}, day by day"))

    keep = {"index.html"}
    for i, d in enumerate(days):
        prev = days[i - 1] if i else None
        nxt = days[i + 1] if i + 1 < total else None
        ticks = "".join(f'<span class="{"on" if k <= d["n"] else ""}"></span>' for k in range(1, total + 1))
        prev_btn = (f'<a class="btn ghost" href="{prev["url"]}">Day before</a>' if prev
                    else '<span class="btn ghost" aria-disabled="true">Day before</span>')
        if nxt:
            next_btn = (f'<a class="btn cream" href="{nxt["url"]}" data-release="{nxt["release"]}">Next day</a>'
                        f'<span class="btn cream" aria-disabled="true" data-until="{nxt["release"]}">Day {nxt["n"]} {esc(d_short(nxt["run"]))}</span>')
        else:
            next_btn = f'<a class="btn cream" href="/campaign-series/{vid}/">All days</a>'
        paras = "".join(f"<p>{esc(p.strip())}</p>" for p in d["body"].split("\n\n") if p.strip())
        srcs = ", ".join(f'<a href="{esc(s["url"])}" target="_blank" rel="noopener">{esc(s["label"])}</a>' for s in d["sources"])
        body = f"""<main class="dayview">
  <div class="daytop"><a class="backlink" href="/campaign-series/{vid}/"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M15 5l-7 7 7 7"/></svg> {esc(vol['title'])}</a><span class="dayof">Day {d['n']} of {total}</span></div>
  <article class="dayart">
    <figure class="daypic"><img src="{esc(d['img'] or '')}" alt="{esc(d['alt'])}" width="1080" height="1350"></figure>
    <div class="daytxt">
      <p class="dayline"><span class="swatch" style="background:{d['seriesColor']}" title="{esc(d['series'])}"></span><span class="sr">{esc(d['series'])}. </span>{esc(d_long(d['hist']))} · {esc(d['place'])}</p>
      <h1>{esc(d['subtitle'])}</h1>
      <div class="daycap">{paras}</div>
      <p class="daysrc">Photo: {esc(d['credit'])}<br>Sources: {srcs}</p>
    </div>
  </article>
  <nav class="daynav" aria-label="Days">
    <div class="ticks" aria-hidden="true">{ticks}</div>
    <div class="daybtns">{prev_btn}{next_btn}</div>
  </nav>
</main>"""
        name = f"day-{d['nn']}.html"
        keep.add(name)
        desc = d["body"].split("\n")[0][:200]
        open(os.path.join(out_dir, name), "w", encoding="utf-8").write(
            page(f"{vol['title']}, Day {d['n']}: {d['subtitle']} | WW2 Dispatches", desc, d["url"], body, "campaign",
                 image=d["img"], ogtype="article", ogtitle=f"{vol['title']}, Day {d['n']}: {d['subtitle']}"))
    for f in os.listdir(out_dir):  # a day that was removed takes its page with it
        if f.endswith(".html") and f not in keep:
            os.remove(os.path.join(out_dir, f))

    data = {"id": vid, "vol": vol["vol"], "title": vol["title"], "dates": vol["dates"], "url": f"/campaign-series/{vid}/", "days": [
        {"n": d["n"], "release": d["release"], "arrives": d["arrives"], "date": d["date"], "place": d["place"], "series": d["series"],
         "subtitle": d["subtitle"], "url": d["url"], "img": d["img"], "thumb": d["thumb"]} for d in days]}
    json.dump(data, open(os.path.join(SITE, "campaign-series", f"{vid}.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)


def spine_size(days):
    """Spine width and height from the series length, so a longer series is a thicker book.
    7 days or fewer is the thinnest (40 x 180 px), 30 days (the cap) the thickest (68 x 210);
    a volume with no length yet gets the size of a 20 day series."""
    d = min(30, max(7, days or 20))
    t = (d - 7) / 23
    return round(40 + 28 * t), round(180 + 30 * t)


def build_shelf():
    shelf = json.load(open(os.path.join(ROOT, "campaign-series", "shelf.json"), encoding="utf-8"))["volumes"]
    releases, out = {}, []
    for vol in shelf:
        days = load_volume(vol) if os.path.isdir(os.path.join(ROOT, "campaign-series", vol["id"])) else []
        cover = None
        src = vol.get("cover") or ""
        if src and os.path.exists(os.path.join(ROOT, src)):
            save_jpeg(os.path.join(ROOT, src), os.path.join(SITE, "campaign-series", "covers", f"{vol['id']}.jpg"), 1200)
            cover = f"/campaign-series/covers/{vol['id']}.jpg"
        live = bool(days)
        if live:
            build_volume(vol, days)
            releases[vol["id"]] = {d["nn"]: d["release"] for d in days}
        for k in ("blurb", "note", "intro", "dates"):
            no_dash(vol.get(k), f"shelf {vol['id']} {k}")
        out.append({
            "id": vol["id"], "vol": vol["vol"], "title": vol["title"], "dates": vol["dates"], "theater": vol["theater"], "year": vol["year"],
            "status": "live" if live else vol.get("status", "proposed"), "cloth": vol.get("cloth", "#3F4034"),
            "w": spine_size(len(days) or vol.get("days"))[0], "h": spine_size(len(days) or vol.get("days"))[1],
            "days": len(days) or vol.get("days"), "approx": bool(vol.get("approx")) and not live, "cover": cover, "coverPos": vol.get("coverPos", "50% 40%"),
            "blurb": vol.get("blurb", ""), "note": vol.get("note", ""), "url": f"/campaign-series/{vol['id']}/" if live else "",
            "start": days[0]["release"] if days else None, "end": days[-1]["release"] if days else None,
            "startLabel": d_short(days[0]["run"]) if days else "", "intro": vol.get("intro", ""), "times": [d["release"] for d in days],
        })
    json.dump({"volumes": out}, open(os.path.join(SITE, "campaign-series", "shelf.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    build_shelf_page(out)
    return releases


def spine(v):
    return (f'<button type="button" class="spine" data-id="{esc(v["id"])}" aria-haspopup="dialog" '
            f'aria-label="Vol. {esc(v["vol"])}, {esc(v["title"])}" style="--cloth:{esc(v["cloth"])};width:{v["w"]}px;height:{v["h"]}px">'
            f'<span class="sp-vol">{esc(v["vol"])}</span><span class="sp-title">{esc(v["title"])}</span></button>')


def build_shelf_page(vols):
    groups = {}
    for v in vols:
        groups.setdefault(v["theater"], []).append(v)
    order = ["The Pacific", "The Western Front", "The Mediterranean", "The Eastern Front", "The Atlantic"]
    names = [g for g in order if g in groups] + [g for g in groups if g not in order]
    shelves = "\n".join(
        f'    <section class="shelf" aria-label="{esc(g)}"><h2>{esc(g)}</h2><div class="board hs">{"".join(spine(v) for v in groups[g])}'
        f'{"<span class=gap aria-hidden=true></span>" * 4}</div><div class="plank" aria-hidden="true"></div></section>' for g in names)
    data = json.dumps(vols, ensure_ascii=False).replace("</", "<\\/")
    body = f"""<main class="shelfpage">
  <header class="pagehead">
    <span class="kicker">Campaign Series</span>
    <h1>The Campaign Shelf</h1>
    <p>Whole campaigns told one day at a time, as they happened. Tap a spine to pull it off the shelf.</p>
    <div class="modes" role="group" aria-label="Shelve by"><button type="button" class="toggle" data-mode="theater" aria-pressed="true">By theater</button><button type="button" class="toggle" data-mode="year" aria-pressed="false">By year</button></div>
  </header>
  <div class="shelfwrap">
    <div class="shelves" id="shelves">
{shelves}
      <p class="shelfnote">More volumes are shelved as each series finishes.</p>
    </div>
    <div class="scrim" id="scrim" hidden></div>
    <aside class="stand" id="stand" role="dialog" aria-modal="false" aria-labelledby="st-title" tabindex="-1">
      <span class="grab" aria-hidden="true"></span>
      <span class="st-k">On the reading stand</span>
      <div class="st-row">
        <a class="book" id="st-book" href="#"></a>
        <div class="st-meta"><span class="st-theater" id="st-theater"></span><h2 class="st-title" id="st-title"></h2><span class="st-dates" id="st-dates"></span><span class="st-status" id="st-status"></span></div>
      </div>
      <p class="st-blurb" id="st-blurb"></p>
      <a class="btn red" id="st-open" href="#">Open the volume</a>
      <p class="st-note" id="st-note"></p>
      <button type="button" class="st-close" id="st-close">Put it back</button>
    </aside>
  </div>
  <noscript><ul class="nojs">{"".join(f'<li><a href="{v["url"]}">Vol. {esc(v["vol"])}: {esc(v["title"])}</a></li>' if v["url"] else f'<li>Vol. {esc(v["vol"])}: {esc(v["title"])} ({esc(v["note"])})</li>' for v in vols)}</ul></noscript>
</main>
<script type="application/json" id="shelf-data">{data}</script>"""
    open(os.path.join(SITE, "campaign-series", "index.html"), "w", encoding="utf-8").write(
        page("The Campaign Shelf | WW2 Dispatches", "Whole WW2 campaigns told one day at a time, as they happened: Pearl Harbor, the Bulge, and more.",
             "/campaign-series/", body, "campaign", script=f'<script src="/campaign-series/shelf.js?v={asset_v("campaign-series/shelf.js")}"></script>\n'))


# ---------------------------------------------------------------------------------------------
# Name This
# ---------------------------------------------------------------------------------------------
def category(body):
    m = re.search(r"Can you name th(?:is|ese) ([a-z ]+?)\?", body or "", re.I)
    w = (m[1] if m else "").lower()
    if re.search(r"ship|vessel|sub|carrier|boat|battleship", w):
        return "Ships"
    if re.search(r"aircraft|plane|bomber|fighter|airship", w):
        return "Aircraft"
    if re.search(r"\b(man|woman|person|people|men|women|leader|general|admiral|soldier|pilot)\b", w):
        return "People"
    return "Machines"


def build_namethis():
    recs = [json.load(open(p, encoding="utf-8")) for p in glob.glob(os.path.join(ROOT, "namethis", "*.json"))]
    recs = sorted((r for r in recs if r.get("post_date")), key=lambda r: r["post_date"])
    cases, releases = [], {}
    for i, r in enumerate(recs):
        q = cdn(f"cards/namethis-{r['id']}-game-q.jpg") or cdn(f"cards/namethis-{r['id']}-x.jpg") or r.get("cardImage")
        a = cdn(f"cards/namethis-{r['id']}-game-a.jpg")
        if not q:
            problem(f"Name This {r['id']}: no card image")
            continue
        post = dt.date.fromisoformat(r["post_date"])
        rel = iso(dt.datetime.combine(post, dt.time(10, 0), DENVER))
        hist = dt.date.fromisoformat(r["date"])
        links = r.get("links") or {}
        releases[r["id"]] = rel
        c = {"id": r["id"], "case": f"CASE {i + 1:02d}", "release": rel, "posted": f"{DAYS[post.weekday()][:3]} {d_short(post)}",
             "place": r.get("place", ""), "clue": (r.get("pull") or "").removeprefix("Clue:").strip(), "cat": category(r.get("body")),
             "q": q, "threads": links.get("threads") or THREADS, "x": links.get("x") or X, "ig": links.get("instagram") or INSTAGRAM,
             "hist": f"{hist.day} {MONTHS[hist.month - 1][:3]} {hist.year}"}
        if a:
            c["aImg"] = a
        if r.get("answer"):  # lightly encoded, as on the home page; the server drops it from the open case
            c["a"] = base64.b64encode(r["answer"].encode("utf-8")).decode("ascii")
        cases.append(c)
    os.makedirs(os.path.join(SITE, "name-this"), exist_ok=True)
    json.dump({"cases": cases}, open(os.path.join(SITE, "name-this", "cases.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    body = """<main class="ntpage">
  <header class="pagehead">
    <span class="kicker nt">Name This</span>
    <h1>Can you name it?</h1>
    <p>One mystery photo from the war, every Wednesday and Saturday.</p>
  </header>
  <div class="ntwrap">
    <section class="opencase" id="opencase" aria-labelledby="oc-clue" hidden>
      <img id="oc-img" src="" alt="This week's Name This puzzle photo" width="1080" height="1350">
      <div class="oc-txt">
        <span class="oc-tag">Open case</span>
        <span class="oc-posted" id="oc-posted"></span>
        <h2 class="oc-clue" id="oc-clue"></h2>
        <p>Think you know it? Post your guess. The answer goes in the drawer when the next case opens.</p>
        <div class="oc-go"><a class="btn cream" id="oc-threads" href="https://www.threads.com/@ww2dispatches" target="_blank" rel="noopener">Guess on Threads</a><a class="btn ghost" id="oc-x" href="https://x.com/ww2dispatches" target="_blank" rel="noopener">Guess on X</a></div>
      </div>
    </section>
    <section class="drawer" aria-labelledby="drawer-h">
      <div class="drawerfront" aria-hidden="true"><div class="plate"><div><small>Name This</small><b>The Evidence Drawer</b></div></div><span class="pull"></span></div>
      <h2 class="sr" id="drawer-h">The Evidence Drawer</h2>
      <div class="drawerin">
        <p>Every closed case, newest first. Make your guess, then open the file.</p>
        <div class="chips hs" id="chips" role="group" aria-label="Filter cases"></div>
        <ol class="files" id="files"></ol>
        <p class="nofiles" id="nofiles" hidden>The first case closes when the next puzzle posts.</p>
      </div>
    </section>
  </div>
</main>"""
    open(os.path.join(SITE, "name-this", "index.html"), "w", encoding="utf-8").write(
        page("Name This | WW2 Dispatches", "Can you name it? One mystery photo from the war, every Wednesday and Saturday, and every closed case in the Evidence Drawer.",
             "/name-this/", body, "namethis", script=f'<script src="/name-this/namethis.js?v={asset_v("name-this/namethis.js")}"></script>\n'))
    return releases


def main():
    os.makedirs(os.path.join(SITE, "campaign-series"), exist_ok=True)
    campaigns = build_shelf()
    namethis = build_namethis()
    json.dump({"campaigns": campaigns, "namethis": namethis}, open(os.path.join(ROOT, "functions", "_data", "releases.json"), "w", encoding="utf-8"), indent=1)
    sync_chrome()
    n_days = sum(len(v) for v in campaigns.values())
    print(f"site pages: {len(campaigns)} live volume(s), {n_days} day pages, {len(namethis)} Name This cases")
    for p in PROBLEMS:
        print("PROBLEM " + p)


if __name__ == "__main__":
    main()
