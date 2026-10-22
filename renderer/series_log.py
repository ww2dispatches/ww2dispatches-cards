"""Build the WW2 Dispatches logs from the JSON records.

Writes three files:
  log/series-log.csv     one row per dispatch card: everything worth keeping for later
                         (archive site, newsletter, analytics, shop): number, dates, series,
                         format, title, place, video kind and film source, photo credit,
                         growth flags, newsletter issue, sources, theme tags, and every live post link
  log/series-counts.csv  running totals per series
  log/namethis-log.csv   one row per Name This card

Run from the repo root:  python3 renderer/series_log.py
Both weekly runs (Thursday cards, Friday videos) and the Saturday Name This run run this
after their changes, so the logs never need typing by hand. The CSVs are written
with a UTF-8 byte order mark so Excel shows accented names and the · separator correctly. Never edit the CSVs by hand;
the JSON files in dispatches/ and namethis/ are the source.
"""
import csv, glob, json, os
from collections import Counter

LAUNCH_YEAR = 2026
SERIES = {"battle": "Battle Lines", "home": "Home Front", "blue": "Blueprint", "state": "Statecraft"}
FORMATS = {None: "Story", "photo": "Photo of the Day", "quote": "Quote of the Day", "spec": "Spec Sheet"}

root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def load(folder):
    out = []
    for path in glob.glob(os.path.join(root, folder, "*.json")):
        d = json.load(open(path, encoding="utf-8"))
        d["_file"] = f"{folder}/{os.path.basename(path)}"
        out.append(d)
    return out


def yes(v):
    return "yes" if v else ""


def sources(d):
    urls = [s.get("url", "") if isinstance(s, dict) else str(s) for s in d.get("sources") or []]
    return len(urls), " | ".join(u for u in urls if u)


def theme_cols(d):
    """The themes block as flat columns (see analytics/themes.md)."""
    t = d.get("themes") or {}
    v = t.get("video") or {}
    j = lambda x: " | ".join(x) if isinstance(x, list) else (x or "")
    return {
        "theme_who": j(t.get("who")),
        "theme_story": j(t.get("story")),
        "theme_photo": j(t.get("photo")),
        "theater": j(t.get("theater")),
        "branch": j(t.get("branch")),
        "nations": j(t.get("nations")),
        "video_opening": j(v.get("opening")),
        "video_sound": j(v.get("sound")),
    }


# Dispatch cards
cards = [d for d in load("dispatches") if d.get("num") is not None]
cards.sort(key=lambda d: d["num"])

# Post date: the recorded posted date when there is one, otherwise the event's month and day
# in the posting year. Cards are numbered in posting order, so the year steps up when the
# calendar wraps from December to January.
rows, year, last_md = [], LAUNCH_YEAR, None
for d in cards:
    md = d["date"][5:]
    if last_md and md < last_md:
        year += 1
    last_md = md
    links = d.get("links") or {}
    posted = links.get("posted") or f"{year}-{md}"
    time = d.get("time") or "08:00"
    story = d.get("story") or {}
    video = d.get("video") or {}
    if d.get("kit") or video:
        kind = "Living Card"
    elif story:
        kind = "Story Card"
    else:
        kind = ""
    n_src, src = sources(d)
    rows.append({
        "dispatch_no": f"{d['num']:03d}",
        "post_date": posted,
        "post_time": time,
        "slot": "Evening" if time >= "12:00" else "Morning",
        "series": SERIES.get(d["series"], d["series"]),
        "format": FORMATS.get(d.get("format"), d.get("format")),
        "event_date": d["date"],
        "title": d.get("title", ""),
        "place": d.get("place", ""),
        "pull": d.get("pull", ""),
        "quote_by": d.get("quoteBy", ""),
        "spec_title": d.get("specTitle", ""),
        "noon_video": kind,
        "film_source": video.get("sourceUrl", ""),
        "film_sound": yes(video.get("sound")),
        "photo_credit": d.get("photoNote", ""),
        "photo_page": d.get("photoUrl", ""),
        "carousel_slides": len(d.get("slides") or []) or "",
        "question": yes(d.get("question")),
        "soft_ask": yes(d.get("soft_ask")),
        "newsletter_mention": yes(d.get("newsletter_mention")),
        "newsletter_issue": d.get("newsletter", ""),
        "source_count": n_src,
        "sources": src,
        **theme_cols(d),
        "link_x": links.get("x", ""),
        "link_instagram": links.get("instagram", ""),
        "link_threads": links.get("threads", ""),
        "link_facebook": links.get("facebook", ""),
        "link_video_x": links.get("x_film", ""),
        "link_video_instagram": links.get("instagram_reel", ""),
        "link_video_threads": links.get("threads_film", ""),
        "link_video_facebook": links.get("facebook_film", ""),
        "link_tiktok": links.get("tiktok", ""),
        "link_youtube": links.get("youtube", ""),
        "posted": links.get("posted", ""),
        "json_file": d["_file"],
    })

os.makedirs(os.path.join(root, "log"), exist_ok=True)
with open(os.path.join(root, "log", "series-log.csv"), "w", newline="", encoding="utf-8-sig") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
    w.writeheader()
    w.writerows(rows)

total = len(rows)
by_series = Counter(r["series"] for r in rows)
by_slot = Counter((r["series"], r["slot"]) for r in rows)
with open(os.path.join(root, "log", "series-counts.csv"), "w", newline="", encoding="utf-8-sig") as f:
    w = csv.writer(f)
    w.writerow(["series", "cards", "morning", "evening", "share"])
    for s in SERIES.values():
        n = by_series[s]
        w.writerow([s, n, by_slot[(s, "Morning")], by_slot[(s, "Evening")], f"{n / total:.0%}" if total else "0%"])
    w.writerow(["All series", total, sum(1 for r in rows if r["slot"] == "Morning"),
                sum(1 for r in rows if r["slot"] == "Evening"), "100%"])

# Name This cards
puzzles = sorted(load("namethis"), key=lambda d: (d.get("post_date") or "", d.get("id", "")))
nrows = []
for d in puzzles:
    links = d.get("links") or {}
    n_src, src = sources(d)
    nrows.append({
        "post_date": d.get("post_date", ""),
        "event_date": d.get("date", ""),
        "answer": d.get("answer", ""),
        "place": d.get("place", ""),
        "clue": d.get("pull", ""),
        "x_community": d.get("community", ""),
        "photo_credit": d.get("photoNote", ""),
        "photo_page": d.get("photoUrl", ""),
        "source_count": n_src,
        "sources": src,
        **{k: v for k, v in theme_cols(d).items() if not k.startswith("video_")},
        "link_x": links.get("x", ""),
        "link_threads": links.get("threads", ""),
        "link_facebook": links.get("facebook", ""),
        "link_instagram": links.get("instagram", ""),
        "posted": links.get("posted", ""),
        "json_file": d["_file"],
    })
if nrows:
    with open(os.path.join(root, "log", "namethis-log.csv"), "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=list(nrows[0].keys()))
        w.writeheader()
        w.writerows(nrows)

print(f"{total} cards logged, through No. {rows[-1]['dispatch_no']} on {rows[-1]['post_date']}; "
      f"{len(nrows)} Name This cards logged")

# Refresh the "Today's Dispatches" data for ww2dispatches.com (site/slides.json).
# Kept separate so a problem there never stops the logs from being written.
try:
    import runpy
    runpy.run_path(os.path.join(root, "renderer", "site_data.py"), run_name="__main__")
except Exception as e:
    print(f"site/slides.json not refreshed: {e}")
