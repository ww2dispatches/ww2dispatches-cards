"""Build site/slides.json, the data behind "Today's Dispatches" on ww2dispatches.com.

One slide per post that has an image:
  08:00  the morning dispatch card
  10:00  Name This (Wednesday and Saturday)
  12:00  the noon video (Living Card or Story Card), shown with its poster frame
  17:00  the evening card

The page reads this file and only shows slides whose post time has passed in Denver,
so nothing appears before it is live. Before 8 a.m. it shows yesterday's slides.

Links point to the live post once the Friday run has recorded it in `links`,
otherwise to the account on that platform.

Run from the repo root:  python3 renderer/site_data.py
series_log.py runs this at the end, so every weekly run refreshes it on its own.
Cloudflare Pages rebuilds the site whenever site/ changes. Never edit slides.json by hand.
"""
import datetime, glob, hashlib, json, os, urllib.request

LAUNCH_YEAR = 2026
KEEP_DAYS = 7  # keep a week of past slides so "yesterday" always works
SERIES = {"battle": "Battle Lines", "home": "Home Front", "blue": "Blueprint", "state": "Statecraft"}
FORMATS = {"photo": "Photo of the Day", "quote": "Quote of the Day", "spec": "Spec Sheet"}
CARDS_RAW = "https://raw.githubusercontent.com/ww2dispatches/ww2dispatches-cards/main/"
VIDEOS_RAW = "https://raw.githubusercontent.com/ww2dispatches/ww2dispatches-videos/main/videos/"
X_PROFILE = "https://x.com/ww2dispatches"
SHORTS = "https://www.youtube.com/@ww2dispatcheshq/shorts"

root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def load(folder):
    return [json.load(open(p, encoding="utf-8")) for p in glob.glob(os.path.join(root, folder, "*.json"))]


def card_url(rel):
    """Raw GitHub link with a short content hash, so a re-rendered card is never served stale."""
    path = os.path.join(root, rel)
    if not os.path.exists(path):
        return None
    v = hashlib.sha1(open(path, "rb").read()).hexdigest()[:8]
    return f"{CARDS_RAW}{rel}?v={v}"


def exists(url):
    try:
        req = urllib.request.Request(url, method="HEAD")
        return urllib.request.urlopen(req, timeout=15).status == 200
    except Exception:
        return False


slides = []

# Dispatch cards, with the same post date rule as series_log.py: the recorded posted date,
# otherwise the event's month and day in the posting year (stepping up a year after December).
cards = sorted([d for d in load("dispatches") if d.get("num") is not None], key=lambda d: d["num"])
year, last_md = LAUNCH_YEAR, None
for d in cards:
    md = d["date"][5:]
    if last_md and md < last_md:
        year += 1
    last_md = md
    links = d.get("links") or {}
    post_date = links.get("posted") or f"{year}-{md}"
    time = d.get("time") or "08:00"
    num = f"{d['num']:03d}"
    img = card_url(f"cards/dispatch-{num}-instagram.jpg")
    if img:
        fmt = FORMATS.get(d.get("format"))
        slides.append({
            "date": post_date, "time": time, "kind": "card", "num": num,
            "label": "8 a.m." if time < "12:00" else "5 p.m.",
            "title": fmt or d.get("title", ""), "series": SERIES.get(d.get("series"), ""),
            "img": img,
            "alt": f"WW2 Dispatches card, Dispatch No. {num}, {SERIES.get(d.get('series'), '')}. {d.get('title', '')}.",
            "link": links.get("x") or X_PROFILE, "linkLabel": "Read on X",
        })

    # The noon video that goes with this dispatch, if it has one.
    story = d.get("story") or {}
    is_living = bool((d.get("buffer") or {}).get("youtube")) and bool(d.get("video")) and not story
    if story or is_living:
        poster = f"{VIDEOS_RAW}dispatch-{num}-instagram-poster.jpg"
        if not exists(poster):
            poster = img
        if poster:
            slides.append({
                "date": post_date, "time": "12:00", "kind": "video", "num": num,
                "label": "Noon", "title": "The Story" if story else "The Footage",
                "series": SERIES.get(d.get("series"), ""), "img": poster,
                "alt": f"Noon video for Dispatch No. {num}: {d.get('title', '')}.",
                "link": links.get("youtube") or SHORTS, "linkLabel": "Watch",
            })

# Name This, Wednesday and Saturday at 10 a.m.
for n in load("namethis"):
    if not n.get("post_date"):
        continue
    img = card_url(f"cards/namethis-{n['id']}-x.jpg")
    if not img:
        continue
    links = n.get("links") or {}
    slides.append({
        "date": n["post_date"], "time": "10:00", "kind": "namethis", "num": "",
        "label": "10 a.m.", "title": "Name This", "series": "", "img": img,
        "alt": "WW2 Dispatches Name This card. Can you name it?",
        "link": links.get("x") or X_PROFILE, "linkLabel": "Guess on X",
    })

cutoff = (datetime.date.today() - datetime.timedelta(days=KEEP_DAYS)).isoformat()
slides = sorted((s for s in slides if s["date"] >= cutoff), key=lambda s: (s["date"], s["time"]))
os.makedirs(os.path.join(root, "site"), exist_ok=True)
with open(os.path.join(root, "site", "slides.json"), "w", encoding="utf-8") as f:
    json.dump({"slides": slides}, f, ensure_ascii=False, indent=1)
print(f"site/slides.json: {len(slides)} slides, {slides[0]['date'] if slides else ''} to {slides[-1]['date'] if slides else ''}")
