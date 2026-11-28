#!/usr/bin/env python3
"""Daily dispatch pages and the On this day archive (Site Revamp doc, step 3 of the SEO work, 15 Nov 2026).

Called from renderer/site_pages.py main(), so every weekly run rebuilds them with no extra step.
Never edit the files it writes by hand.

Writes:
  site/dispatches/NNN-slug.html   one permanent page per dispatch card (slug from the record's short name)
  site/on-this-day/index.html     the archive calendar (Archive Site Design Notes, 28 Nov 2026): a month at a time,
                                  a mark per posted series on each day, series filters, month buttons, a preview panel
  site/on-this-day/<month>-<day>/ one page per calendar date (366): every banked event (timeline/onthisday.json,
                                  exported from the date bank by renderer/export_timeline.py) and every posted
                                  dispatch for that date, in year order, posted ones as card rows
Returns the release times for functions/_data/releases.json ("dispatches": {"045": {"slug", "at"}}).

Release rule: a dispatch page shows once its post time has passed (the record's time on its post date,
Mountain). functions/dispatches/_middleware.js sends an early visitor to the archive, and every gated
piece of a page (a later dispatch in "Also on this date", the next dispatch button, a video link
before its post, the archive's rows and dots) carries data-release or data-until for the server.

Brian's rules (15 Nov 2026): the title goes in the address (/dispatches/048-kristallnacht); the
Declassified extra stays off these pages (it is the Weekly Dispatch's); every page carries
"Collect this card in Declass" (it opens /declass?card=<card id>; the Declass side reads that).
"""
import datetime as dt, glob, json, os, re

import site_pages as sp
from site_pages import esc, ld, crumbs, page, iso, d_short, d_long, no_dash, problem, cdn, site_card

LAUNCH_YEAR = 2026
SHORTS = "https://www.youtube.com/@ww2dispatcheshq/shorts"
TIME_LABEL = {"08:00": "8 a.m.", "14:30": "2:30 p.m.", "17:00": "5 p.m."}
BACK = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M15 5l-7 7 7 7"/></svg>'
IG = ('<svg viewBox="0 0 24 24" aria-hidden="true"><rect x="3" y="3" width="18" height="18" rx="5"/><circle cx="12" cy="12" r="4"/>'
      '<circle cx="17.5" cy="6.5" r="1.2" class="fill"/></svg>')
PLAY = '<svg viewBox="0 0 24 24" aria-hidden="true"><path class="fill" d="M7 4l13 8-13 8z"/></svg>'


def slugify(s):
    s = re.sub(r"[^a-z0-9]+", "-", (s or "").lower().replace("'", "")).strip("-")
    return s or "dispatch"


def denver(day, hhmm):
    h, m = map(int, hhmm.split(":"))
    return dt.datetime.combine(day, dt.time(h, m), sp.DENVER)


def load():
    """Every dispatch card, with its post time worked out the same way as site_data.py and series_log.py:
    the recorded posted date, otherwise the event's month and day in the posting year (a year up after December)."""
    recs = [json.load(open(p, encoding="utf-8")) for p in glob.glob(os.path.join(sp.ROOT, "dispatches", "*.json"))]
    recs = sorted((r for r in recs if r.get("num") is not None), key=lambda r: r["num"])
    out, year, last_md = [], LAUNCH_YEAR, None
    for r in recs:
        md = r["date"][5:]
        if last_md and md < last_md:
            year += 1
        last_md = md
        links = r.get("links") or {}
        post = dt.date.fromisoformat(links.get("posted") or f"{year}-{md}")
        hhmm = r.get("time") or "08:00"
        num = f"{r['num']:03d}"
        img = site_card(f"dispatch-{num}-instagram")
        jpg = cdn(f"cards/dispatch-{num}-instagram.jpg")
        if not (img or jpg):
            problem(f"dispatch {num}: no card image, no page")
            continue
        sname, _cls, color = sp.SERIES.get(r.get("series"), ("", "", "#B04A3E"))
        hist = dt.date.fromisoformat(r["date"])
        d = {"r": r, "num": num, "id": r["id"], "slug": f"{num}-{slugify(r.get('short') or r.get('title'))}", "post": post, "hhmm": hhmm,
             "at": iso(denver(post, hhmm)), "dayStart": iso(denver(post, "00:00")),
             "dayEnd": iso(denver(post + dt.timedelta(days=1), "00:00")),
             "hist": hist, "md": r["date"][5:], "series": sname, "skey": r.get("series"), "color": color,
             "img": img[0] if img else jpg, "thumb": (img[1] if img and img[1] else (img[0] if img else jpg)), "og": jpg or img[0],
             "links": links}
        d["url"] = f"/dispatches/{d['slug']}"
        # The film that goes with the card, if it has one, and when it posts (as in site_data.py).
        buf = r.get("buffer") or {}
        if r.get("story") or (buf.get("youtube") and r.get("video")):
            vt = r.get("videoTime") or "12:00"
            d["video"] = {"at": iso(denver(post, vt)), "link": links.get("youtube") or SHORTS,
                          "label": "Watch the story" if r.get("story") else "Watch the footage"}
        out.append(d)
    slugs = [d["slug"] for d in out]
    for s in set(slugs):
        if slugs.count(s) > 1:
            problem(f"two dispatch pages share the address {s}")
    return out


def card_alt(d):
    r = d["r"]
    return r.get("alt") or f"WW2 Dispatches card, Dispatch No. {d['num']}, {d['series']}. {r.get('title', '')}."


def meta_line(d):
    return f"{d['series']} · {d['hist'].year} · No. {d['num']}"


def mini(d, tag="li"):
    """A small linked row: thumbnail, title, series and year. Gated on its post time."""
    return (f'<{tag} class="dmini" data-release="{d["at"]}" data-s="{esc(d["skey"])}"><a href="{d["url"]}">'
            f'<img src="{esc(d["thumb"])}" alt="" width="72" height="90" loading="lazy">'
            f'<span><span class="dmini-t">{esc(d["r"]["title"])}</span><span class="dmini-m"><span class="swatch" style="background:{d["color"]}"></span>{esc(meta_line(d))}</span></span>'
            f'</a></{tag}>')


def md_label(md):
    m, day = map(int, md.split("-"))
    return f"{day} {sp.MONTHS[m - 1]}"


def day_url(md):
    m, day = map(int, md.split("-"))
    return f"/on-this-day/{sp.MONTHS[m - 1].lower()}-{day}/"


# Platform buttons (Brian, 27 Nov 2026): one per platform the dispatch went to, each opening that exact post
# (the record's links section), else the platform's profile. A film only link opens at the film's post time.
PLATFORMS = [("x", "X", sp.X, ("x", "x_film")), ("instagram", "Instagram", sp.INSTAGRAM, ("instagram", "instagram_reel")),
             ("threads", "Threads", sp.THREADS, ("threads", "threads_film")),
             ("facebook", "Facebook", "https://www.facebook.com/ww2dispatches", ("facebook", "facebook_film")),
             ("tiktok", "TikTok", "https://www.tiktok.com/@ww2dispatches", ("tiktok",)),
             ("youtube", "YouTube", "https://www.youtube.com/@ww2dispatcheshq", ("youtube",))]


def platform_buttons(d):
    links, buf = d["links"], (d["r"].get("buffer") or {})
    vat = (d.get("video") or {}).get("at")
    out = []
    for key, label, profile, keys in PLATFORMS:
        card_key, film_keys = keys[0], keys[1:] if key not in ("tiktok", "youtube") else keys
        posted_card = key not in ("tiktok", "youtube") and (links.get(card_key) or card_key in buf)
        film = next((links.get(k) for k in film_keys if links.get(k)), None) or next((profile for k in film_keys if k in buf), None)
        if posted_card:
            out.append(f'<a class="btn ghost" href="{esc(links.get(card_key) or profile)}" target="_blank" rel="noopener">{label}</a>')
        elif film:
            gate = f' data-release="{vat}"' if vat else ""
            out.append(f'<a class="btn ghost" href="{esc(film)}" target="_blank" rel="noopener"{gate}>{label}</a>')
    if not out:
        return ""
    return f'<p class="dp-seek">See it on</p><div class="dp-plats">{"".join(out)}</div>'


def build_page(d, prev, nxt, same_day):
    r = d["r"]
    paras = [p.strip() for p in (r.get("body") or "").split("\n\n") if p.strip()]
    no_dash(r.get("body"), f"dispatch {d['num']} caption")
    cap = "".join(f"<p>{esc(p)}</p>" for p in paras)
    extra = ""
    if r.get("format") == "spec" and r.get("specs"):
        rows = "".join(f"<tr><th scope=\"row\">{esc(k)}</th><td>{esc(v)}</td></tr>" for k, v in r["specs"])
        extra = f'<table class="dp-spec"><caption>{esc(r.get("specTitle") or "Spec sheet")}</caption>{rows}</table>'
    elif r.get("format") == "quote" and r.get("quote"):
        extra = f'<blockquote class="dp-quote"><p>{esc(r["quote"])}</p><footer>{esc(r.get("quoteBy") or "")}</footer></blockquote>'
    acts = f'<a class="btn dp-collect" href="/declass?card={esc(d["id"])}">Collect this card in Declass</a>{platform_buttons(d)}'
    srcs = ", ".join(f'<a href="{esc(s["url"])}" target="_blank" rel="noopener">{esc(s["title"])}</a>' for s in (r.get("sources") or []) if s.get("url"))
    credit = r.get("photoCredit") or ""
    src = f'<p class="daysrc dp-src">{"Photo: " + esc(credit) + "<br>" if credit else ""}{"Sources: " + srcs if srcs else ""}</p>'
    also = f'<p class="dp-back"><a class="backlink" href="{day_url(d["md"])}">{BACK} Back to {esc(md_label(d["md"]))}</a></p>'

    def pn(x, cls, word):
        if not x:
            return f'<span class="dp-pn {cls} none"></span>'
        lab = f'<span class="dp-pn-d">{word} · No. {x["num"]} · {esc(d_short(x["hist"]))}</span><span class="dp-pn-h">{esc(x["r"]["title"])}</span>'
        live = f'<a class="dp-pn {cls}" href="{x["url"]}" data-release="{x["at"]}">{lab}</a>'
        if cls == "next":
            live += (f'<span class="dp-pn {cls} shut" data-until="{x["at"]}"><span class="dp-pn-d">Next · No. {x["num"]}</span>'
                     f'<span class="dp-pn-h">Posts {esc(d_short(x["post"]))} at {esc(TIME_LABEL.get(x["hhmm"], sp.clock(x["hhmm"])))}</span></span>')
        return live
    nav = f'<nav class="dp-nav" aria-label="Dispatches">{pn(prev, "prev", "Before")}{pn(nxt, "next", "Next")}</nav>'
    body = f"""<main class="dayview dpview">
  <div class="daytop"><a class="backlink" href="{day_url(d['md'])}">{BACK} {esc(md_label(d['md']))}</a><span class="dayof">Dispatch No. {d['num']}</span></div>
  <article class="dayart">
    <div class="dp-side">
      <figure class="daypic"><img src="{esc(d['img'])}" alt="{esc(card_alt(d))}" width="1080" height="1350"></figure>
      {acts}
    </div>
    <div class="daytxt">
      <p class="dayline"><span class="swatch" style="background:{d['color']}" title="{esc(d['series'])}"></span><span class="sr">{esc(d['series'])}. </span>{esc(d_long(d['hist']))} · {esc(r.get('place', ''))}</p>
      <h1>{esc(r['title'])}</h1>
      <div class="daycap">{cap}</div>
      {extra}
      {src}
      {also}
      {nav}
    </div>
  </article>
</main>"""
    desc = (paras[0] if paras else r.get("pull") or r["title"])[:200]
    art = {"@type": "Article", "@id": f"{sp.URL}{d['url']}#article", "headline": r["title"], "description": desc, "image": d["og"],
           "datePublished": d["at"], "author": {"@id": sp.ORG_ID}, "publisher": {"@id": sp.ORG_ID}, "inLanguage": "en",
           "articleSection": d["series"], "url": f"{sp.URL}{d['url']}", "isPartOf": {"@id": sp.SITE_ID},
           "about": {"@type": "Event", "name": r["title"], "startDate": r["date"], "location": {"@type": "Place", "name": r.get("place", "")}}}
    head = ld(art, crumbs(("On this day", "/on-this-day/"), (md_label(d["md"]), day_url(d["md"])), (r["title"], d["url"])))
    return page(f"{r['title']}, {d['hist'].day} {sp.MONTHS[d['hist'].month - 1]} {d['hist'].year} | WW2 Dispatches", desc, d["url"], body,
                "dispatches", image=d["og"], ogtype="article", head_extra=head)


LENGTHS = [31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
DOT = '<span class="ad-dot" style="background:{c}"></span>'


def timeline():
    path = os.path.join(sp.ROOT, "timeline", "onthisday.json")
    if not os.path.exists(path):
        problem("timeline/onthisday.json missing: run renderer/export_timeline.py; date pages show dispatches only")
        return {}
    return json.load(open(path, encoding="utf-8"))


def count_words(n, one, many):
    return f"{n} {one if n == 1 else many}"


def build_date_page(md, lst, bank):
    """One calendar date: two short lines, the series filter, then every event in year order. Posted dispatches
    are card rows that appear at their post time; banked events are plain headline lines."""
    label = md_label(md)
    ats = sorted(x["at"] for x in lst)
    # The two opening lines change as each dispatch posts, so each state carries its own time window.
    counts = []
    for k in range(len(ats) + 1):
        live = [x for x in lst if k and x["at"] <= ats[k - 1]]
        years = [r[0] for r in bank] + [x["hist"].year for x in live]
        total = len(years)
        c1 = f"{count_words(total, 'event', 'events')} on record, {min(years)} to {max(years)}." if total else "No events on record yet."
        c2 = ("One has a full dispatch. Open its card to read it." if len(live) == 1 else f"{len(live)} have a full dispatch. Open a card to read it.") if live \
            else "No dispatch has been posted for this date yet."
        gate = (f' data-release="{ats[k - 1]}"' if k else "") + (f' data-until="{ats[k]}"' if k < len(ats) else "")
        counts.append(f'<div class="ad-count"{gate}><p class="ad-c1">{esc(c1)}</p><p class="ad-c2">{esc(c2)}</p></div>')
    rows = []
    for x in lst:
        rows.append((x["hist"].year, 0, x["num"],
                     f'<li class="ad-row" data-release="{x["at"]}" data-s="{esc(x["skey"])}"><a class="ad-card" href="{x["url"]}">'
                     f'<img src="{esc(x["thumb"])}" alt="" width="60" height="75" loading="lazy">'
                     f'<span class="ad-cb"><span class="ad-k">{DOT.format(c=x["color"])}{esc(x["series"])}, {x["hist"].year}, No. {x["num"]}</span>'
                     f'<span class="ad-ct">{esc(x["r"]["title"])}</span><span class="ad-go">Read the dispatch</span></span></a></li>'))
    for i, (yr, sk, title) in enumerate(bank):
        name, _c, color = sp.SERIES.get(sk, sp.SERIES["battle"])
        rows.append((yr, 1, i, f'<li class="ad-row" data-s="{esc(sk)}"><span class="ad-y">{yr}</span>{DOT.format(c=color)}'
                               f'<span class="ad-t">{esc(title)}<span class="sr">, {esc(name)}</span></span></li>'))
    rows.sort(key=lambda r: (r[0], r[1], r[2]))
    chips = ('<div class="chips ad-chips" role="group" aria-label="Filter by series"><button class="toggle" type="button" data-s="" aria-pressed="true">All series</button>'
             + "".join(f'<button class="toggle" type="button" data-s="{k}" aria-pressed="false"><span class="swatch" style="background:{c}"></span>{esc(n)}</button>'
                       for k, (n, _x, c) in sp.SERIES.items()) + '</div>')
    m = int(md[:2])
    body = f"""<main class="adpage">
  <div class="ad-wrap">
    <a class="backlink" href="/on-this-day/?m={m}">{BACK} {sp.MONTHS[m - 1]} calendar</a>
    <h1 class="ad-h"><span class="ad-d">{esc(label)}</span><span class="ad-w">in World War II</span></h1>
    {"".join(counts)}
    {chips}
    <h2 class="ad-div"><span>On this day</span></h2>
    <ol class="ad-list">{"".join(r[3] for r in rows)}</ol>
    <p class="ad-empty" hidden>No events in this series on this date.</p>
  </div>
</main>"""
    url = day_url(md)
    yrs = [r[0] for r in bank]
    span = f", {min(yrs)} to {max(yrs)}" if yrs else ""
    desc = f"What happened on {label} in the Second World War{span}: every event we have filed for the date, with full dispatches, archival photos and sources."
    head = ld({"@type": "CollectionPage", "name": f"{label} in World War II", "url": f"{sp.URL}{url}", "isPartOf": {"@id": sp.SITE_ID}, "description": desc},
              crumbs(("On this day", "/on-this-day/"), (label, url)))
    folder = os.path.join(sp.SITE, url.strip("/"))
    os.makedirs(folder, exist_ok=True)
    open(os.path.join(folder, "index.html"), "w", encoding="utf-8").write(
        page(f"{label} in World War II | WW2 Dispatches", desc, url, body, "dispatches", head_extra=head,
             script=f'<script src="/on-this-day/otd.js?v={sp.asset_v("on-this-day/otd.js")}"></script>\n'))
    return url


def build_archive(ds):
    """The archive calendar and the 366 date pages (Archive Site Design Notes, 28 Nov 2026)."""
    by_md = {}
    for d in ds:
        by_md.setdefault(d["md"], []).append(d)
    for v in by_md.values():
        v.sort(key=lambda x: (x["hist"], x["num"]))
    bank = timeline()
    year = dt.datetime.now(sp.DENVER).year
    chips = ('<div class="chips otd-chips" role="group" aria-label="Filter by series"><button class="toggle" type="button" data-s="" aria-pressed="true">All series</button>'
             + "".join(f'<button class="toggle" type="button" data-s="{k}" aria-pressed="false"><span class="swatch" style="background:{c}"></span>{esc(n)}</button>'
                       for k, (n, _x, c) in sp.SERIES.items()) + '</div>')
    mbtns = "".join(f'<button class="otd-mo" type="button" data-m="{m}" aria-pressed="false">{sp.MONTHS[m - 1][:3]}</button>' for m in range(1, 13))
    week = "".join(f'<span class="otd-wd" aria-hidden="true">{w}</span>' for w in "SMTWTFS")
    cals, panels, urls = [], [], []
    for m in range(1, 13):
        first = (dt.date(year, m, 1).weekday() + 1) % 7  # Sunday first, as a phone calendar
        cells = ['<span class="otd-blank" aria-hidden="true"></span>'] * first
        for day in range(1, LENGTHS[m - 1] + 1):
            md = f"{m:02d}-{day:02d}"
            lst = by_md.get(md, [])
            url = build_date_page(md, lst, bank.get(md, []))
            urls.append(url)
            marks = "".join(f'<i data-release="{x["at"]}" data-s="{esc(x["skey"])}" style="background:{x["color"]}"></i>' for x in lst)
            none = f'<i class="none" data-until="{min(x["at"] for x in lst)}"></i>' if lst else '<i class="none"></i>'
            cells.append(f'<a class="otd-dy" href="{url}" data-md="{md}" aria-label="{esc(md_label(md))}"><span class="otd-n">{day}</span>'
                         f'<span class="otd-marks">{none}{marks}</span></a>')
            nb = len(bank.get(md, []))
            posts = "".join(f'<div class="pv-post" data-release="{x["at"]}" data-s="{esc(x["skey"])}"><span class="pv-k">{DOT.format(c=x["color"])}{esc(x["series"])}, {x["hist"].year}</span>'
                            f'<span class="pv-t">{esc(x["r"]["title"])}</span></div>' for x in lst)
            if lst:
                gate_none = f' data-until="{min(x["at"] for x in lst)}"'
                more = f'<p class="pv-more" data-release="{min(x["at"] for x in lst)}">{count_words(nb, "more event", "more events")} on this day</p>' if nb else ""
            else:
                gate_none, more = "", ""
            none_block = (f'<div class="pv-none"{gate_none}><span class="pv-k">No dispatch yet</span>'
                          f'<span class="pv-t">{count_words(nb, "event", "events")} on record for this date</span></div>')
            panels.append(f'<section class="otd-pv" id="pv-{md}" data-md="{md}" hidden aria-label="{esc(md_label(md))}">'
                          f'<div class="pv-head"><h2>{esc(md_label(md))}</h2><span class="pv-today" hidden>Today</span></div>'
                          f'{none_block}{posts}{more}<a class="btn pv-open" href="{url}">Open {esc(md_label(md))}</a></section>')
        cells += ['<span class="otd-blank" aria-hidden="true"></span>'] * ((7 - len(cells) % 7) % 7)
        cals.append(f'<section class="otd-cal" data-m="{m}" aria-label="{sp.MONTHS[m - 1]}"><h2 class="otd-calh">{sp.MONTHS[m - 1]}</h2>'
                    f'<div class="otd-grid">{week}{"".join(cells)}</div></section>')
    legend = "".join(f'<span><i style="background:{c}"></i>{esc(n)}</span>' for k, (n, _x, c) in sp.SERIES.items()) + '<span><i class="none"></i>No dispatch yet</span>'
    body = f"""<main class="otdpage">
  <header class="pagehead">
    <span class="kicker">The Archive</span>
    <h1>Every day of the war</h1>
    <p>Pick a date to see what happened on it, from the 1930s to 1949.</p>
  </header>
  <div class="otd-wrap">
    <div class="otd-main">
      {chips}
      <div class="otd-months" role="group" aria-label="Jump to a month">{mbtns}</div>
      <div class="otd-nav" hidden><button class="otd-arrow" type="button" data-step="-1" aria-label="Previous month">{BACK}</button>
        <span class="otd-mname"></span><button class="otd-arrow next" type="button" data-step="1" aria-label="Next month">{BACK}</button></div>
      {"".join(cals)}
      <p class="otd-legend">{legend}</p>
    </div>
    <aside class="otd-side">
      {"".join(panels)}
      <p class="otd-hint" hidden>Tap a day to preview it. Tap it again to open it.</p>
    </aside>
  </div>
</main>"""
    head = ld({"@type": "CollectionPage", "name": "On this day in World War II", "url": f"{sp.URL}/on-this-day/", "isPartOf": {"@id": sp.SITE_ID},
               "description": "Every day of the Second World War, filed by calendar date: what happened on each date from the 1930s to 1949, with full dispatches, archival photos and sources."},
              crumbs(("On this day", "/on-this-day/")))
    os.makedirs(os.path.join(sp.SITE, "on-this-day"), exist_ok=True)
    open(os.path.join(sp.SITE, "on-this-day", "index.html"), "w", encoding="utf-8").write(
        page("On this day in World War II | WW2 Dispatches",
             "What happened on every day of the Second World War: pick a date for every event we have filed, with full dispatches, real archival photos and sources.",
             "/on-this-day/", body, "dispatches", head_extra=head,
             script=f'<script src="/on-this-day/otd.js?v={sp.asset_v("on-this-day/otd.js")}"></script>\n'))
    return urls


def main():
    ds = load()
    out_dir = os.path.join(sp.SITE, "dispatches")
    os.makedirs(out_dir, exist_ok=True)
    keep = set()
    for i, d in enumerate(ds):
        prev = ds[i - 1] if i else None
        nxt = ds[i + 1] if i + 1 < len(ds) else None
        same = [x for x in ds if x["md"] == d["md"] and x is not d]
        name = d["slug"] + ".html"
        keep.add(name)
        open(os.path.join(out_dir, name), "w", encoding="utf-8").write(build_page(d, prev, nxt, same))
    for f in os.listdir(out_dir):  # a renamed or removed dispatch takes its old page with it
        if f.endswith(".html") and f not in keep:
            os.remove(os.path.join(out_dir, f))
    build_archive(ds)
    return {d["num"]: {"slug": d["slug"], "at": d["at"]} for d in ds}
