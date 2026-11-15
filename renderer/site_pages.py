#!/usr/bin/env python3
"""Build the ww2dispatches.com pages that come from the records (Site Revamp doc).

Run from the repo root:  python3 renderer/site_pages.py
site_data.py runs this at its end (and series_log.py runs site_data.py), so every weekly run
and every Campaign Series sitting that rebuilds the logs refreshes these pages with no extra step.
Never edit the files it writes by hand.

Writes:
  site/campaign-series/index.html            the Campaign Shelf
  site/campaign-series/shelf.json            the shelf data (home page teaser)
  site/campaign-series/<series>/index.html   the book's title page (Contents: chapters and day stamps)
  site/campaign-series/<series>/part-NN.html a chapter: the whole Substack part, each day's post as a slip
  site/campaign-series/<series>/parts/       the chapter cover photos
  site/campaign-series/<series>/day-NN.html  one page per day, its own address for sharing
  site/campaign-series/<series>.json         the volume data (sealed days are cut by the server)
  site/campaign-series/<series>/thumbs/      small day thumbnails; covers/ the shelf cover photos
  site/name-this/index.html, cases.json      Name This: the open case and the Evidence Drawer
  functions/_data/releases.json              post times the server gates on (days, parts with final flag, Name This)
and refreshes the shared header and footer (CHROME) in the hand written pages
(site/index.html, support.html, privacy.html), between their <!--chrome:...--> markers.

Chapters come from campaign-series/<series>/articles/part-NN.json and .md; a chapter shows once its
publish time has passed and its record says "status": "final" (a draft shows on preview addresses only).
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
PART_RELEASES = {}


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
            "n": n, "nn": nn, "date": r["date"], "hist": hist, "run": run, "release": iso(rel), "hhmm": hhmm,
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


# ---------------------------------------------------------------------------------------------
# The books (Site Revamp doc, 15 Nov 2026): each volume is a book. Its title page has Contents,
# with every Substack part as a chapter and a row of day stamps under each; a chapter page is the
# whole part with each day's post as a teletype slip beside its section; day pages carry a
# bookmark strip to their section. A part shows once its publish time has passed and its record
# is marked final ("status": "final"); a part not yet final shows on preview addresses only.
# ---------------------------------------------------------------------------------------------
BACK_SVG = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M15 5l-7 7 7 7"/></svg>'
CHEV_SVG = '<svg class="chev" viewBox="0 0 24 24" aria-hidden="true"><path d="M6 9l6 6 6-6"/></svg>'


def gate(at, final=True, live=True):
    """Attributes the server reads (functions/_lib/release.js) to show a live or a sealed version."""
    if live:
        return f' data-release="{at}"' + ("" if final else ' data-draft=""')
    return f' data-until="{at}"' if final else f' data-draft-until="{at}"'


def span_dates(a, b):
    a, b = dt.date.fromisoformat(a), dt.date.fromisoformat(b)
    if a.year != b.year:
        return f"{a.day} {MONTHS[a.month - 1]} {a.year} to {b.day} {MONTHS[b.month - 1]} {b.year}"
    if a.month != b.month:
        return f"{a.day} {MONTHS[a.month - 1]} to {b.day} {MONTHS[b.month - 1]} {b.year}"
    return f"{a.day} to {b.day} {MONTHS[a.month - 1]} {b.year}" if a != b else f"{a.day} {MONTHS[a.month - 1]} {a.year}"


def md_inline(s):
    s = esc(s)
    s = re.sub(r"\[([^\]]+)\]\((https?://[^)\s]+)\)", r'<a href="\2" target="_blank" rel="noopener">\1</a>', s)
    s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?![\w*])", r"<em>\1</em>", s)
    return s


def md_figure(line, where):
    m = re.match(r"!\[(.*)\]\(([^)\s]+)\)\s*$", line.strip())
    cap, src = m.group(1), m.group(2)
    url = src if src.startswith("http") else cdn(src)
    if not url:
        problem(f"{where}: image not found ({src})")
        return ""
    no_dash(cap, f"{where} caption")
    return f'<figure><img src="{esc(url)}" alt="{esc(re.sub(r"[*]", "", cap)[:200])}" loading="lazy"><figcaption>{md_inline(cap)}</figcaption></figure>'


def md_quote(lines):
    text = "\n".join(re.sub(r"^>\s?", "", l) for l in lines)
    paras = [p.strip().replace("\n", " ") for p in re.split(r"\n\s*\n", text) if p.strip()]
    out = []
    for i, p in enumerate(paras):
        cls = ""
        if i == len(paras) - 1 and i > 0 and not p.startswith('"') and not p.startswith("**"):
            cls = ' class="q-src"'
        out.append(f"<p{cls}>{md_inline(p)}</p>")
    return "<blockquote>" + "".join(out) + "</blockquote>"


def parse_part(md, where):
    """Split a part's markdown into the opening, the dated sections, and the closing matter.
    Each section: {title, dateline, html}. A "### Sources" heading in the closing matter is
    preceded by the {NAV} marker, where the chapter buttons go."""
    blocks = [b for b in re.split(r"\n\s*\n", md.strip()) if b.strip()]
    opening, sections, closing = [], [], []
    target, last_heading = opening, False
    no_dash(md.replace("---", ""), where)
    for b in blocks:
        lines = b.strip().split("\n")
        first = lines[0].strip()
        if first.startswith("## "):
            sections.append({"title": first[3:].strip(), "dateline": "", "parts": []})
            target, last_heading = sections[-1]["parts"], True
            continue
        if last_heading and re.fullmatch(r"\*[^*].*\*", first) and len(lines) == 1:
            sections[-1]["dateline"] = first.strip("*").strip()
            last_heading = False
            continue
        last_heading = False
        if first == "---":
            target = closing
            closing.append("<hr>")
            continue
        if first.startswith("### "):
            target.append("{NAV}" if target is closing and "{NAV}" not in closing else "")
            target.append(f"<h3>{md_inline(first[4:].strip())}</h3>")
        elif all(l.lstrip().startswith(">") for l in lines):
            target.append(md_quote(lines))
        elif first.startswith("!["):
            target.append(md_figure(first, where))
        elif all(re.match(r"\s*[*-] ", l) for l in lines):
            items = [md_inline(re.sub(r"^\s*[*-] ", "", l)) for l in lines]
            target.append("<ul>" + "".join("<li>" + it + "</li>" for it in items) + "</ul>")
        else:
            target.append(f"<p>{md_inline(' '.join(l.strip() for l in lines))}</p>")
    for s in sections:
        s["html"] = "\n".join(s.pop("parts"))
    if "{NAV}" not in closing:
        closing.append("{NAV}")
    return "\n".join(opening), sections, "\n".join(closing)


def load_parts(vol, days):
    """The Substack parts of a volume (campaign-series/<series>/articles/part-NN.json and .md)."""
    vid = vol["id"]
    folder = os.path.join(ROOT, "campaign-series", vid, "articles")
    by_n = {d["n"]: d for d in days}
    parts = []
    for p in sorted(glob.glob(os.path.join(folder, "part-[0-9][0-9].json"))):
        rec = json.load(open(p, encoding="utf-8"))
        n = int(rec["part"])
        nn = f"{n:02d}"
        where = f"{vid} part {nn}"
        md_path = os.path.join(folder, f"part-{nn}.md")
        if not os.path.exists(md_path):
            problem(f"{where}: no part-{nn}.md")
            continue
        first_day, last_day = rec["days"]
        pub = dt.datetime.fromisoformat(rec["publish"]).astimezone(DENVER)
        cover = None
        src = rec.get("coverPhoto") or ""
        if src and os.path.exists(os.path.join(ROOT, src)):
            save_jpeg(os.path.join(ROOT, src), os.path.join(SITE, "campaign-series", vid, "parts", f"part-{nn}.jpg"), 1600)
            cover = f"/campaign-series/{vid}/parts/part-{nn}.jpg"
        else:
            problem(f"{where}: cover photo not found ({src})")
        opening, sections, closing = parse_part(open(md_path, encoding="utf-8").read(), where)
        span = list(range(first_day, last_day + 1))
        if len(sections) != len(span):
            problem(f"{where}: {len(sections)} sections for {len(span)} days; slips left out")
        for k in ("title", "subtitle", "synopsis"):
            no_dash(rec.get(k), f"{where} {k}")
        parts.append({
            "n": n, "nn": nn, "of": rec.get("parts"), "title": rec.get("title", ""), "synopsis": rec.get("synopsis", ""),
            "subtitle": rec.get("subtitle", ""), "first": rec["first"], "last": rec["last"], "dates": span_dates(rec["first"], rec["last"]),
            "days": span, "release": iso(pub), "final": rec.get("status") == "final",
            "arrives": f"{DAYS[pub.weekday()][:3]} {pub.day} {MONTHS[pub.month - 1][:3]}, {clock(pub.strftime('%H:%M'))} MT",
            "arrivesShort": f"{DAYS[pub.weekday()][:3]} {pub.day} {MONTHS[pub.month - 1][:3]}",
            "cover": cover, "coverCredit": rec.get("coverCredit", ""), "focus": f"{rec.get('focusX', 50)}% {rec.get('focusY', 50)}%",
            "opening": opening, "sections": sections if len(sections) == len(span) else [], "rawSections": sections, "closing": closing,
            "url": f"/campaign-series/{vid}/part-{nn}",
            "dayMap": {d: (sections[i]["title"] if i < len(sections) else "") for i, d in enumerate(span) if d in by_n},
        })
    parts.sort(key=lambda x: x["n"])
    return parts


def stamps_html(days):
    out = []
    for d in days:
        out.append(f'<a class="stamp" href="{d["url"]}"{gate(d["release"])}><b>Day {d["n"]}</b>{esc(d_short(d["hist"]))}</a>'
                   f'<span class="stamp shut"{gate(d["release"], live=False)}><b>Day {d["n"]}</b>{esc(d_short(d["hist"]))}<span class="sr">, arrives {esc(d_short(d["run"]))}</span></span>')
    return f'<div class="stamps">{"".join(out)}</div>'


BOOK_SIGNUP = """<div class="subscribe book-sub">
    <h2>Get each chapter by email</h2>
    <p>A new chapter arrives the morning after its last day runs. Free, through our Substack.</p>
    <form class="nl-form" action="https://ww2dispatches.substack.com/api/v1/free?nojs=true" method="post" target="substack-signup">
      <label class="sr" for="{fid}">Email</label>
      <input id="{fid}" name="email" type="email" placeholder="you@example.com" required autocomplete="email">
      <button type="submit">Subscribe</button>
    </form>
    <p class="sent" hidden>Almost done. Check your inbox to confirm.</p>
    <p class="follow">Or follow each series live every morning at 6:30 MT on <a href="{threads}" target="_blank" rel="noopener">Threads</a>.</p>
  </div>"""


def build_book(vol, days, parts):
    """The title page: the clothbound plate, the introduction, and Contents."""
    vid, total = vol["id"], len(days)
    cover = f"/campaign-series/covers/{vid}.jpg"
    by_n = {d["n"]: d for d in days}
    # Status line: one version per stretch of time, the server keeps the right one.
    status = [f'<p class="vb-status"{gate(days[0]["release"], live=False)}>Begins {esc(d_short(days[0]["run"]))}, 6:30 a.m. MT</p>']
    for i, d in enumerate(days):
        until = days[i + 1]["release"] if i + 1 < total else None
        label = f"Now running · Day {d['n']} of {total}" if until else f"Complete · {total} days"
        status.append(f'<p class="vb-status"{gate(d["release"])}{gate(until, live=False) if until else ""}>{label}</p>')
    entries, covered = [], set()
    count = max([p["of"] or 0 for p in parts] + [len(parts)])
    for p in parts:
        covered.update(p["days"])
        pdays = [by_n[k] for k in p["days"] if k in by_n]
        pic_live = (f'<a class="pe-pic" href="{p["url"]}"><img src="{p["cover"] or cover}" alt="" loading="lazy" style="object-position:{esc(p["focus"])}"></a>')
        pic_sealed = f'<span class="pe-pic pe-seal" aria-hidden="true"><span>SEALED · ARRIVES {esc(p["arrivesShort"].upper())}</span></span>'
        entries.append(f"""<article class="pe">
      <div{gate(p["release"], p["final"])}>{pic_live}</div>
      <div{gate(p["release"], p["final"], live=False)}>{pic_sealed}</div>
      <div class="pe-txt">
        <p class="pe-k">Part {p["n"]} of {count}</p>
        <h3><a href="{p["url"]}"{gate(p["release"], p["final"])}>{esc(p["title"])}</a><span{gate(p["release"], p["final"], live=False)}>{esc(p["title"])}</span></h3>
        <p class="pe-d">{esc(p["dates"])}</p>
        <div class="pe-live"{gate(p["release"], p["final"])}><p class="pe-syn">{esc(p["synopsis"])}</p><a class="btn ink" href="{p["url"]}">Read Part {p["n"]}</a></div>
        <p class="pe-arr"{gate(p["release"], p["final"], live=False)}>Arrives {esc(p["arrives"])}</p>
        <p class="pe-dk">The daily dispatches</p>
        {stamps_html(pdays)}
      </div>
    </article>""")
    rest = [d for d in days if d["n"] not in covered]
    if rest:
        entries.append(f"""<article class="pe pe-more">
      <div class="pe-txt">
        <p class="pe-k">Days {rest[0]["n"]} to {rest[-1]["n"]}</p>
        <h3>More dispatches</h3>
        <p class="pe-d">{esc(span_dates(rest[0]["date"], rest[-1]["date"]))}</p>
        <p class="pe-syn">Their chapters arrive as the series runs. Each day opens here once it has posted.</p>
        {stamps_html(rest)}
      </div>
    </article>""")
    lede = esc(vol.get("intro", ""))
    blurb = esc(vol.get("blurb", ""))
    body = f"""<main class="bookpage">
  <div class="vb-top"><a class="backlink" href="/campaign-series/">{BACK_SVG} The Campaign Shelf</a><span class="meta">Vol. {esc(vol["vol"])}</span></div>
  <div class="vb-spread">
    <section class="vb-plate" style="--cloth:{esc(vol.get("cloth", "#24344F"))}">
      <img class="vb-cover{' color' if vol.get('coverColor') else ''}" src="{cover}" alt="" style="object-position:{esc(vol.get('coverPos', '50% 40%'))}">
      <p class="vb-k">Volume {esc(vol["vol"])} · {esc(vol.get("theater", ""))}</p>
      <h1>{esc(vol["title"])}</h1>
      <p class="vb-d">{esc(span_dates(days[0]["date"], days[-1]["date"]))}</p>
      {"".join(status)}
    </section>
    <section class="vb-paper">
      <p class="vb-lede">{lede}</p>
      <p class="vb-intro">{blurb} Each chapter tells part of it in full, with the maps, orders and first hand accounts behind every day. The short dispatches that ran each morning at 6:30 sit beside the days they belong to.</p>
      <h2>Contents</h2>
      {"".join(entries)}
    </section>
  </div>
  {BOOK_SIGNUP.format(fid="em-book", threads=THREADS)}
</main>"""
    desc = f"{vol['title']}, {vol.get('dates', '')}: {vol.get('blurb', '')}"
    open(os.path.join(SITE, "campaign-series", vid, "index.html"), "w", encoding="utf-8").write(
        page(f"{vol['title']} | Campaign Series | WW2 Dispatches", desc, f"/campaign-series/{vid}/", body, "campaign",
             image=f"{URL}{cover}", ogtitle=f"{vol['title']}: the campaign, day by day, in full"))


def slip_html(d, total, vol):
    paras = "".join(f"<p>{esc(p.strip())}</p>" for p in d["body"].split("\n\n") if p.strip())
    hhmm = clock(d["hhmm"])
    return (f'<details class="slip"><summary><img src="{d["thumb"]}" alt="" width="30" height="38" loading="lazy">'
            f'<span class="tt"><b>As it ran</b> · Day {d["n"]} of {total}<br>{hhmm} MT, {esc(d_short(d["run"]))} {d["run"].year}</span>{CHEV_SVG}</summary>'
            f'<div class="slipbody"><p class="sliph">{esc(d["subtitle"])}</p>{paras}'
            f'<p class="sliplinks"><a href="{d["url"]}">Open the day page</a></p></div></details>')


def build_parts(vol, days, parts):
    vid, total = vol["id"], len(days)
    by_n = {d["n"]: d for d in days}
    out_dir = os.path.join(SITE, "campaign-series", vid)
    keep = set()
    for i, p in enumerate(parts):
        count = max(p["of"] or 0, len(parts))
        secs = []
        for k, s in enumerate(p["rawSections"]):
            dn = p["days"][k] if p["sections"] and k < len(p["days"]) else None
            d = by_n.get(dn)
            slip = slip_html(d, total, vol) if d else ""
            anchor = f' id="day-{d["nn"]}"' if d else ""
            dl = '<p class="dateline">' + md_inline(s["dateline"]) + "</p>" if s["dateline"] else ""
            sl = '<div class="ch-slip">' + slip + "</div>" if slip else ""
            secs.append(f'<section class="ch-sec"{anchor}><h2>{esc(s["title"])}</h2>{dl}{sl}<div class="ch-body">{s["html"]}</div></section>')
        nxt = parts[i + 1] if i + 1 < len(parts) else None
        prev = parts[i - 1] if i else None
        nav = ['<nav class="ch-nav" aria-label="Chapters">']
        if prev:
            nav.append(f'<a class="btn ghostink" href="{prev["url"]}">Part {prev["n"]}</a>')
        nav.append(f'<a class="btn ink" href="/campaign-series/{vid}/">Contents</a>')
        if nxt:
            nav.append(f'<a class="btn red" href="{nxt["url"]}"{gate(nxt["release"], nxt["final"])}>Part {nxt["n"]}</a>'
                       f'<span class="btn shut" aria-disabled="true"{gate(nxt["release"], nxt["final"], live=False)}>Part {nxt["n"]} · Arrives {esc(nxt["arrivesShort"])}</span>')
        elif p["n"] < count:
            nav.append(f'<span class="btn shut" aria-disabled="true">Part {p["n"] + 1} · In preparation</span>')
        nav.append("</nav>")
        closing = p["closing"].replace("{NAV}", "".join(nav))
        img = p["cover"] or f"/campaign-series/covers/{vid}.jpg"
        body = f"""<main class="chapter">
  <div class="vb-top"><a class="backlink" href="/campaign-series/{vid}/">{BACK_SVG} {esc(vol["title"])}</a><span class="meta">Part {p["n"]} of {count}</span></div>
  <figure class="ch-cover"><img src="{img}" alt="{esc(p["coverCredit"])}" style="object-position:{esc(p["focus"])}"></figure>
  <header class="ch-head">
    <p class="ch-k">Campaign Series · {esc(vol["title"])} · <b>Part {p["n"]} of {count}</b></p>
    <h1>{esc(p["title"])}</h1>
    <p class="ch-syn">{esc(p["synopsis"])}</p>
    <p class="ch-k">{esc(p["dates"])}</p>
  </header>
  <article class="ch-paper">
    <div class="ch-open">{p["opening"]}</div>
    {"".join(secs)}
    <div class="ch-end">{closing}<p class="ch-credit">Cover: {esc(p["coverCredit"])}</p></div>
  </article>
  {BOOK_SIGNUP.format(fid=f"em-part-{p['nn']}", threads=THREADS)}
</main>"""
        name = f"part-{p['nn']}.html"
        keep.add(name)
        desc = p["subtitle"] or p["synopsis"]
        head = f'<meta name="robots" content="noindex">\n' if not p["final"] else ""
        open(os.path.join(out_dir, name), "w", encoding="utf-8").write(
            page(f"{vol['title']}, Part {p['n']}: {p['title']} | WW2 Dispatches", desc, p["url"], body, "campaign",
                 image=f"{URL}{img}", ogtype="article", ogtitle=f"{vol['title']}, Part {p['n']}: {p['title']}", head_extra=head,
                 script='<script>if(matchMedia("(min-width: 900px)").matches)document.querySelectorAll("details.slip").forEach(function(d){d.open=true;});</script>\n'))
    return keep


def bookmark_html(d, parts):
    for p in parts:
        if d["n"] in p["days"]:
            sec = p["dayMap"].get(d["n"]) if p["sections"] else ""
            where = f"Part {p['n']}, {esc(p['title'])}" + (f": {esc(sec)}" if sec else "")
            href = p["url"] + (f"#day-{d['nn']}" if sec else "")
            return (f'<a class="bookmark" href="{href}"{gate(p["release"], p["final"])}><span class="bm-t"><span class="bm-k">This day in the book</span>'
                    f'<span class="bm-w">{where}</span></span><span class="bm-go">Read it in full</span></a>'
                    f'<p class="bookmark shut"{gate(p["release"], p["final"], live=False)}><span class="bm-t"><span class="bm-k">This day in the book</span>'
                    f'<span class="bm-w">The full chapter arrives {esc(p["arrives"])}</span></span></p>')
    return ""


def build_volume(vol, days):
    vid, total = vol["id"], len(days)
    out_dir = os.path.join(SITE, "campaign-series", vid)
    os.makedirs(out_dir, exist_ok=True)
    parts = load_parts(vol, days)
    build_book(vol, days, parts)
    keep = {"index.html"} | build_parts(vol, days, parts)
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
        bm = bookmark_html(d, parts)
        bm = f'<div class="daybm">{bm}</div>' if bm else ""
        body = f"""<main class="dayview">
  <div class="daytop"><a class="backlink" href="/campaign-series/{vid}/"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M15 5l-7 7 7 7"/></svg> {esc(vol['title'])}</a><span class="dayof">Day {d['n']} of {total}</span></div>
  <article class="dayart">
    {bm}<figure class="daypic"><img src="{esc(d['img'] or '')}" alt="{esc(d['alt'])}" width="1080" height="1350"></figure>
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
    return parts


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
    PART_RELEASES.clear()
    for vol in shelf:
        days = load_volume(vol) if os.path.isdir(os.path.join(ROOT, "campaign-series", vol["id"])) else []
        cover = None
        src = vol.get("cover") or ""
        if src and os.path.exists(os.path.join(ROOT, src)):
            save_jpeg(os.path.join(ROOT, src), os.path.join(SITE, "campaign-series", "covers", f"{vol['id']}.jpg"), 1200)
            cover = f"/campaign-series/covers/{vol['id']}.jpg"
        live = bool(days)
        if live:
            parts = build_volume(vol, days)
            releases[vol["id"]] = {d["nn"]: d["release"] for d in days}
            if parts:
                PART_RELEASES[vol["id"]] = {p["nn"]: {"at": p["release"], "final": p["final"]} for p in parts}
        for k in ("blurb", "note", "intro", "dates"):
            no_dash(vol.get(k), f"shelf {vol['id']} {k}")
        out.append({
            "id": vol["id"], "vol": vol["vol"], "title": vol["title"], "dates": vol["dates"], "theater": vol["theater"], "year": vol["year"],
            "status": "live" if live else vol.get("status", "proposed"), "cloth": vol.get("cloth", "#3F4034"),
            "w": spine_size(len(days) or vol.get("days"))[0], "h": spine_size(len(days) or vol.get("days"))[1],
            "days": len(days) or vol.get("days"), "approx": bool(vol.get("approx")) and not live, "cover": cover, "coverPos": vol.get("coverPos", "50% 40%"), "coverColor": bool(vol.get("coverColor")),
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
      <a class="btn red" id="st-open" href="#">Open the book</a>
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
def site_card(stem):
    """The site's own webp copy of a card and its small thumbnail, with a content hash, or None."""
    full = os.path.join(SITE, "declass", "cards", stem + ".webp")
    if not os.path.exists(full):
        return None
    v = lambda p: hashlib.sha1(open(p, "rb").read()).hexdigest()[:8]
    thumb = os.path.join(SITE, "declass", "cards", "t", stem + ".webp")
    return (f"/declass/cards/{stem}.webp?v={v(full)}", f"/declass/cards/t/{stem}.webp?v={v(thumb)}" if os.path.exists(thumb) else None)


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
        # Light copies first: the 720 px and 288 px webp cards the Declass catalog writes (about 46 KB and 8 KB),
        # falling back to the full 1080 px JPEG (about 300 KB) only if they are missing (14 Nov 2026, Brian saw lag).
        q, qt = site_card(f"namethis-{r['id']}-game-q") or (cdn(f"cards/namethis-{r['id']}-game-q.jpg") or cdn(f"cards/namethis-{r['id']}-x.jpg") or r.get("cardImage"), None)
        a, at = site_card(f"namethis-{r['id']}-game-a") or (cdn(f"cards/namethis-{r['id']}-game-a.jpg"), None)
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
        if qt:
            c["qT"] = qt
        if a:
            c["aImg"] = a
        if at:
            c["aT"] = at
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
    json.dump({"campaigns": campaigns, "parts": PART_RELEASES, "namethis": namethis}, open(os.path.join(ROOT, "functions", "_data", "releases.json"), "w", encoding="utf-8"), indent=1)
    sync_chrome()
    n_days = sum(len(v) for v in campaigns.values())
    print(f"site pages: {len(campaigns)} live volume(s), {n_days} day pages, {len(namethis)} Name This cases")
    for p in PROBLEMS:
        print("PROBLEM " + p)


if __name__ == "__main__":
    main()
