#!/usr/bin/env python3
"""The Chronicle tab of the Substack Dashboard (Campaign Series parts on Substack).

Reads every campaign-series/<series>/articles/part-NN.json and .md and returns,
for each part, what the dashboard needs: the part as it reads (with + Note per
day section), the copy for Substack (title, subtitle, body as rich text with raw
GitHub image URLs, plain text fallback), the cover, the Day by Day images, the
publish time, and the repo status. Parts not written yet show as placeholders.

Not run on its own: renderer/newsletter_page.py calls collect() on every build,
so the Friday run and a Campaign Series sitting both rebuild the whole dashboard
with `python3 renderer/newsletter_page.py`. Rules: docs/WW2 Dispatches Campaign
Series.md ("The Chronicle") and docs/WW2 Dispatches Newsletter.md.
"""
import base64, glob, html, io, json, os, re
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import markdown
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = "https://raw.githubusercontent.com/ww2dispatches/ww2dispatches-cards/main/"
GH_FILE = "https://github.com/ww2dispatches/ww2dispatches-cards/blob/main/"
MT = ZoneInfo("America/Denver")
KEEP_DAYS = 10  # a published part stays on the dashboard this many days after it goes live
SUB_MIN, SUB_MAX, SUB_CHARS = 6, 10, 250  # Substack subtitle rule (Brian, 21 Nov 2026)


def subtitle_check(text, where):
    """Substack subtitles: 6 to 10 words, never over 250 characters (Substack's limit).
    Returns (problems, notes)."""
    words = len(text.split())
    problems, notes = [], []
    if len(text) > SUB_CHARS:
        problems.append(f"{where}: subtitle is {len(text)} characters, Substack allows {SUB_CHARS}")
    if words > SUB_MAX:
        problems.append(f"{where}: subtitle is {words} words, keep it to {SUB_MIN} to {SUB_MAX}: {text!r}")
    elif text and words < SUB_MIN:
        notes.append(f"{where}: subtitle is only {words} words (aim for {SUB_MIN} to {SUB_MAX})")
    return problems, notes


def thumb(rel, width=720):
    full = os.path.join(ROOT, rel)
    if not os.path.isfile(full):
        return None
    im = Image.open(full).convert("RGB")
    if im.width > width:
        im = im.resize((width, round(im.height * width / im.width)), Image.LANCZOS)
    buf = io.BytesIO()
    im.save(buf, "JPEG", quality=76, optimize=True)
    return "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode()


def slug(t):
    return re.sub(r"[^a-z0-9]+", "-", t.lower()).strip("-")


def human_dates(first, last):
    a, b = datetime.fromisoformat(first), datetime.fromisoformat(last)
    if a.month == b.month:
        return f"{a.day} to {b.day} {b.strftime('%B %Y')}"
    return f"{a.day} {a.strftime('%B')} to {b.day} {b.strftime('%B %Y')}"


def to_html(md, image_src, problems, where):
    """Markdown to HTML; images become figures with captions; src via image_src(path)."""
    def img(m):
        cap, src = m.group(1), m.group(2)
        if not os.path.isfile(os.path.join(ROOT, src)):
            problems.append(f"{where}: missing image {src}")
        return f'\n\n<figure><img src="{image_src(src)}" alt="{html.escape(cap)}" data-raw="{RAW + src}"><figcaption>{html.escape(cap)}</figcaption></figure>\n\n'
    body = markdown.markdown(re.sub(r"!\[([^\]]*)\]\(([^)]+)\)", img, md))
    return body.replace("<p><figure>", "<figure>").replace("</figure></p>", "</figure>")


def sections(md):
    """Review sections: the opening, one per ## day section, then the close (Next and Sources)."""
    secs, cur = [], {"id": "opening", "label": "Opening", "md": []}
    for line in md.splitlines():
        if line.startswith("## "):
            secs.append(cur)
            label = line[3:].strip()
            cur = {"id": slug(label), "label": label, "md": [line]}
        elif line.strip() == "---" and cur["id"] != "close":
            secs.append(cur)
            cur = {"id": "close", "label": "Next and Sources", "md": [line]}
        else:
            cur["md"].append(line)
    secs.append(cur)
    return [s for s in secs if "".join(s["md"]).strip()]


def part_record(series, jpath, now, problems):
    meta = json.load(open(jpath, encoding="utf-8"))
    n = meta["part"]
    pid = f"ch-{series}-{n:02d}"
    adir = os.path.dirname(jpath)
    mdpath = os.path.join(adir, f"part-{n:02d}.md")
    publish = datetime.fromisoformat(meta["publish"]).astimezone(MT)
    where = f"{series} part {n}"
    rec = {
        "id": pid, "series": series, "seriesName": meta.get("seriesName", series),
        "part": n, "parts": meta.get("parts"), "title": meta.get("title", ""),
        "publish": publish.isoformat(), "publishLabel": publish.strftime("%A, %B %-d, %Y"),
        "publishTime": publish.strftime("%-I:%M %p").lower().replace("am", "a.m.").replace("pm", "p.m."),
        "published": publish <= now, "repoStatus": meta.get("status", "draft"),
        "days": meta.get("days"), "written": os.path.isfile(mdpath),
    }
    if not rec["written"]:
        return rec
    md = open(mdpath, encoding="utf-8").read()
    rec.update({
        "substackTitle": meta.get("substackTitle", ""), "subtitle": meta.get("subtitle", ""),
        "synopsis": meta.get("synopsis", ""), "dates": human_dates(meta["first"], meta["last"]),
        "github": GH_FILE + os.path.relpath(mdpath, ROOT),
    })
    for k in ("substackTitle", "subtitle"):
        if not rec[k]:
            problems.append(f"{where}: no {k} in part-{n:02d}.json")
    sp, sn = subtitle_check(rec["subtitle"], where)
    problems += sp
    for x in sn:
        print("NOTE", x)
    rec["subtitleWords"] = len(rec["subtitle"].split())
    for t in [rec["substackTitle"], rec["subtitle"], md]:
        for bad in ("—", "–", " - "):
            if bad in t:
                problems.append(f"{where}: dash found ({bad!r})")
                break
    if rec["repoStatus"] != "final" and not rec["published"]:
        problems.append(f"{where}: status is {rec['repoStatus']!r}, set \"final\" before {publish:%a %-d %b} or the site keeps it sealed")

    # Cover: the rendered cover image goes at the top of the post and is the thumbnail.
    cover = os.path.relpath(os.path.join(adir, "images", f"part-{n:02d}-cover.jpg"), ROOT)
    rec["cover"] = {"preview": thumb(cover), "raw": RAW + cover, "credit": meta.get("coverCredit", "")}
    if not rec["cover"]["preview"]:
        problems.append(f"{where}: cover missing, run node renderer/campaign_article.js {series} {n}")

    # Day by Day gallery: the part's daily images.
    d1, d2 = meta["days"]
    gal = []
    for d in range(d1, d2 + 1):
        rel = f"campaign-series/{series}/images/day-{d:02d}-instagram.jpg"
        p = thumb(rel, 360)
        if p:
            gal.append({"day": d, "preview": p, "raw": RAW + rel})
        else:
            problems.append(f"{where}: missing Day by Day image {rel}")
    rec["gallery"] = gal
    rec["galleryHeading"] = f"Day by Day: Days {d1} to {d2}"

    # Review: each section with embedded previews and a + Note button.
    secs = sections(md)
    rec["sections"] = [{"id": s["id"], "label": s["label"]} for s in secs]
    day_secs = [s for s in secs if s["id"] not in ("opening", "close")]
    if len(day_secs) != d2 - d1 + 1:
        problems.append(f"{where}: {len(day_secs)} day sections (##) for days {d1} to {d2}; the site needs one per day")
    review = []
    for s in secs:
        body = to_html("\n".join(s["md"]), lambda src: thumb(src) or "", problems, where)
        review.append(f'<section class="sec" id="{pid}-{s["id"]}" data-sec="{s["id"]}">'
                      f'<div class="sechead"><button class="chnotebtn" data-chsec="{s["id"]}">+ Note</button></div>{body}</section>')
    rec["reviewHtml"] = "".join(review)

    # Copy for Substack: cover with its credit first, the article, the Day by Day
    # images under their heading just before Sources, then Sources.
    full = to_html(md, lambda src: RAW + src, [], where)
    gallery_html = f"<h3>{html.escape(rec['galleryHeading'])}</h3>" + "".join(
        f'<figure><img src="{g["raw"]}" alt="Day {g["day"]}"></figure>' for g in gal)
    if "<h3>Sources</h3>" in full:
        full = full.replace("<h3>Sources</h3>", gallery_html + "<h3>Sources</h3>", 1)
    else:
        problems.append(f"{where}: no ### Sources heading")
        full += gallery_html
    full = re.sub(r' data-raw="[^"]*"', "", full)
    cover_html = (f'<figure><img src="{rec["cover"]["raw"]}" alt="{html.escape(rec["substackTitle"])}">'
                  f'<figcaption>{html.escape(rec["cover"]["credit"])}</figcaption></figure>')
    rec["copyHtml"] = cover_html + full
    text = re.sub(r"!\[([^\]]*)\]\(([^)]+)\)", r"[Photo: \1]", md)
    text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r"\1 (\2)", text)
    rec["copyText"] = re.sub(r"\*\*|(?<!\*)\*(?!\*)|^#+ |^> ?", "", text, flags=re.M).strip()
    return rec


def collect(now=None):
    """All Chronicle parts worth showing, upcoming first. Returns (parts, problems)."""
    now = now or datetime.now(MT)
    problems, out = [], []
    for sdir in sorted(glob.glob(os.path.join(ROOT, "campaign-series", "*", "articles"))):
        series = os.path.basename(os.path.dirname(sdir))
        recs = [part_record(series, j, now, problems) for j in sorted(glob.glob(os.path.join(sdir, "part-*.json")))]
        if not recs:
            continue
        have = {r["part"] for r in recs}
        total = max([r.get("parts") or 0 for r in recs] + list(have))
        for n in range(1, total + 1):
            if n not in have:
                recs.append({"id": f"ch-{series}-{n:02d}", "series": series, "seriesName": recs[0]["seriesName"],
                             "part": n, "parts": total, "written": False, "title": "", "publish": "",
                             "publishLabel": "", "published": False, "repoStatus": "not started"})
        cutoff = now - timedelta(days=KEEP_DAYS)
        for r in sorted(recs, key=lambda r: r["part"]):
            if r["publish"] and datetime.fromisoformat(r["publish"]) < cutoff:
                continue  # long gone, off the dashboard
            out.append(r)
    out.sort(key=lambda r: (r["publish"] or "9999", r["series"], r["part"]))
    return out, problems
