#!/usr/bin/env python3
"""Daily dispatch pages and the On this day archive (Site Revamp doc, step 3 of the SEO work, 15 Nov 2026).

Called from renderer/site_pages.py main(), so every weekly run rebuilds them with no extra step.
Never edit the files it writes by hand.

Writes:
  site/dispatches/NNN-slug.html   one permanent page per dispatch card (slug from the record's short name)
  site/on-this-day/index.html     the archive: today's dispatches, a calendar by month, every posted
                                  dispatch filed by its date, the series filters and the Name This drawer
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
    recs = sorted((r for r in recs if r.get("num") is not None and not r.get("test")), key=lambda r: r["num"])
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
    links = d["links"]
    threads = links.get("threads") or sp.THREADS
    ig = links.get("instagram") or sp.INSTAGRAM
    video = ""
    if d.get("video"):
        v = d["video"]
        video = f'<a class="btn ghost dp-watch" href="{esc(v["link"])}" target="_blank" rel="noopener" data-release="{v["at"]}">{PLAY}{esc(v["label"])}</a>'
    acts = (f'<a class="btn dp-collect" href="/declass?card={esc(d["id"])}">Collect this card in Declass</a>'
            f'<div class="dp-acts"><a class="btn cream" href="{esc(threads)}" target="_blank" rel="noopener">Read on Threads</a>'
            f'<a class="btn ghost dp-ig" href="{esc(ig)}" target="_blank" rel="noopener" aria-label="See it on Instagram">{IG}</a>{video}</div>')
    srcs = ", ".join(f'<a href="{esc(s["url"])}" target="_blank" rel="noopener">{esc(s["title"])}</a>' for s in (r.get("sources") or []) if s.get("url"))
    credit = r.get("photoCredit") or ""
    src = f'<p class="daysrc dp-src">{"Photo: " + esc(credit) + "<br>" if credit else ""}{"Sources: " + srcs if srcs else ""}</p>'
    also = ""
    if same_day:
        also = (f'<section class="dp-also" data-release="{min(x["at"] for x in same_day)}"><h2>Also on {esc(md_label(d["md"]))}</h2>'
                f'<ul class="dminis">{"".join(mini(x) for x in same_day)}</ul>'
                f'<a class="backlink dp-more" href="/on-this-day/#d-{d["md"]}">Every {esc(md_label(d["md"]))} dispatch</a></section>')

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
  <div class="daytop"><a class="backlink" href="/on-this-day/#d-{d['md']}">{BACK} On this day, {esc(md_label(d['md']))}</a><span class="dayof">Dispatch No. {d['num']}</span></div>
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
    head = ld(art, crumbs(("On this day", "/on-this-day/"), (md_label(d["md"]), f"/on-this-day/#d-{d['md']}"), (r["title"], d["url"])))
    return page(f"{r['title']}, {d['hist'].day} {sp.MONTHS[d['hist'].month - 1]} {d['hist'].year} | WW2 Dispatches", desc, d["url"], body,
                "dispatches", image=d["og"], ogtype="article", head_extra=head)


def build_archive(ds):
    by_md = {}
    for d in ds:
        by_md.setdefault(d["md"], []).append(d)
    for v in by_md.values():
        v.sort(key=lambda x: (x["hist"], x["num"]))
    months_with = {int(md[:2]) for md in by_md}
    chips = ('<div class="chips otd-chips" role="group" aria-label="Filter by series"><button class="toggle" type="button" data-s="" aria-pressed="true">All series</button>'
             + "".join(f'<button class="toggle" type="button" data-s="{k}" aria-pressed="false"><span class="swatch" style="background:{c}"></span>{esc(n)}</button>'
                       for k, (n, _x, c) in sp.SERIES.items())
             + '<button class="toggle otd-ntbtn" type="button" aria-expanded="false" aria-controls="otd-nt">Name This</button></div>')
    nt = ('<section class="otd-nt" id="otd-nt" hidden aria-labelledby="otd-nt-h"><span class="otd-nt-k">The Evidence Drawer</span>'
          '<h2 id="otd-nt-h">Name This</h2><p>A mystery photo from the war, every Wednesday and Saturday at 10 a.m. Each answer opens when the next puzzle posts.</p>'
          '<ul class="otd-ntlist" id="otd-ntlist"></ul><a class="btn ghostink" href="/name-this/">Open the Evidence Drawer</a></section>')
    mbtns = "".join(f'<button class="otd-mo" type="button" data-m="{m}"{"" if m in months_with else " disabled"} aria-pressed="false">{sp.MONTHS[m - 1][:3]}</button>'
                    for m in range(1, 13))
    lengths = [31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    cals = []
    for m in sorted(months_with):
        cells = []
        for day in range(1, lengths[m - 1] + 1):
            md = f"{m:02d}-{day:02d}"
            if md in by_md:
                dots = "".join(f'<i data-release="{x["at"]}" data-s="{esc(x["skey"])}" style="background:{x["color"]}"></i>' for x in by_md[md])
                cells.append(f'<a class="otd-dy" href="#d-{md}" data-md="{md}" aria-label="{esc(md_label(md))}"><span>{day}</span><span class="otd-dots">{dots}</span></a>')
            else:
                cells.append(f'<span class="otd-dy" aria-hidden="true"><span>{day}</span></span>')
        cals.append(f'<section class="otd-cal" data-m="{m}" aria-label="{sp.MONTHS[m - 1]}"><h2 class="otd-calh">{sp.MONTHS[m - 1]}</h2><div class="otd-grid">{"".join(cells)}</div></section>')
    panels = []
    for md in sorted(by_md):
        lst = by_md[md]
        panels.append(f'<section class="otd-day" id="d-{md}" data-release="{min(x["at"] for x in lst)}"><h2>{esc(md_label(md))}</h2>'
                      f'<ul class="dminis">{"".join(mini(x) for x in lst)}</ul></section>')
    # Today: one block per post day, shown only on that day (Denver), each row live from its post time;
    # before then the row shows its time and series only, never the title.
    by_post = {}
    for d in ds:
        by_post.setdefault(d["post"], []).append(d)
    todays = []
    for post, lst in sorted(by_post.items()):
        lst.sort(key=lambda x: x["hhmm"])
        rows = ""
        for x in lst:
            t = esc(TIME_LABEL.get(x["hhmm"], sp.clock(x["hhmm"])))
            rows += (f'<a class="otd-row" href="{x["url"]}" data-release="{x["at"]}"><span class="otd-tm">{t}</span><span><span class="otd-tt">{esc(x["r"]["title"])}</span>'
                     f'<span class="otd-yr">{esc(x["series"])} · {x["hist"].year}</span></span></a>'
                     f'<div class="otd-row later" data-until="{x["at"]}"><span class="otd-tm">{t}</span><span><span class="otd-tt">Posts at {t}</span>'
                     f'<span class="otd-yr">{esc(x["series"])}</span></span></div>')
        todays.append(f'<section class="otd-today" data-release="{x["dayStart"]}" data-until="{x["dayEnd"]}" aria-label="Today">'
                      f'<p class="otd-k">Today, {post.day} {sp.MONTHS[post.month - 1]}</p>{rows}</section>')
    body = f"""<main class="otdpage">
  <header class="pagehead">
    <span class="kicker">Dispatches</span>
    <h1>On this day</h1>
    <p>Every dispatch we have posted, filed by its date. Pick a day to see what happened on it, across every year of the war.</p>
  </header>
  <div class="otd-wrap">
    <div class="otd-todays">{"".join(todays)}</div>
    <div class="otd-main">
      {chips}
      {nt}
      <div class="otd-months" role="group" aria-label="Month">{mbtns}</div>
      {"".join(cals)}
      <p class="otd-key">Dots show each dispatch by series. Days fill in as their dispatches post. Each date holds every year we cover, so one day can carry 1938 and 1944 side by side.</p>
    </div>
    <div class="otd-days">{"".join(panels)}</div>
  </div>
</main>"""
    head = ld({"@type": "CollectionPage", "name": "On this day", "url": f"{sp.URL}/on-this-day/", "isPartOf": {"@id": sp.SITE_ID},
               "description": "Every WW2 Dispatches post, filed by calendar date: what happened on this day in the Second World War, across every year of the war."},
              crumbs(("On this day", "/on-this-day/")))
    os.makedirs(os.path.join(sp.SITE, "on-this-day"), exist_ok=True)
    open(os.path.join(sp.SITE, "on-this-day", "index.html"), "w", encoding="utf-8").write(
        page("On this day in World War II | WW2 Dispatches",
             "What happened on this day in the Second World War: every WW2 Dispatches post, filed by its date, with real archival photos and sources.",
             "/on-this-day/", body, "dispatches", head_extra=head,
             script=f'<script src="/on-this-day/otd.js?v={sp.asset_v("on-this-day/otd.js")}"></script>\n'))


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
