"""Build the Declass game catalog: functions/_data/catalog.json.

Every collectible card with what the game needs to show it: post time (UTC), series, short
name, title, date, place, period, story, photo credit, sources, live post links, the 4 by 5
card image, and the film for Living Cards. Name This cards also carry their answer, clue,
and the time the answer goes public (when the next Name This posts).

The file sits beside the server code (functions/), not in site/, so the website never serves
it. The server reads it and only shows or hands out a card once its post time has passed.

Run from the repo root:  python3 renderer/catalog.py
series_log.py runs this at the end, so every weekly run refreshes it on its own.
Never edit catalog.json by hand; the JSON records in dispatches/ and namethis/ are the source.
"""
import datetime, glob, hashlib, json, os
from zoneinfo import ZoneInfo

LAUNCH_YEAR = 2026
POST_TZ = ZoneInfo("America/Denver")  # Buffer posting times are Mountain
SERIES = {"battle": "Battle Lines", "home": "Home Front", "blue": "Blueprint", "state": "Statecraft", "flash": "Flash"}
CARDS_CDN = "https://cdn.jsdelivr.net/gh/ww2dispatches/ww2dispatches-cards@main/"
VIDEOS_CDN = "https://cdn.jsdelivr.net/gh/ww2dispatches/ww2dispatches-videos@main/videos/"
CARD_LINKS = {"x": "x", "instagram": "instagram", "threads": "threads", "facebook": "facebook"}
FILM_LINKS = {"youtube": "youtube", "tiktok": "tiktok", "x": "x_film", "instagram": "instagram_reel",
              "threads": "threads_film", "facebook": "facebook_film"}

root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def load(folder):
    return [json.load(open(p, encoding="utf-8")) for p in glob.glob(os.path.join(root, folder, "*.json"))]


def card_url(rel):
    path = os.path.join(root, rel)
    if not os.path.exists(path):
        return None
    v = hashlib.sha1(open(path, "rb").read()).hexdigest()[:8]
    return f"{CARDS_CDN}{rel}?v={v}"


def utc(day, hhmm):
    """A Mountain post date and time as a UTC ISO string (daylight saving handled)."""
    local = datetime.datetime.fromisoformat(f"{day}T{hhmm}:00").replace(tzinfo=POST_TZ)
    return local.astimezone(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def era(date):
    """By year tiles: the lead up before 1 Sep 1939, the aftermath after 2 Sep 1945."""
    if date < "1939-09-01":
        return "leadup"
    if date > "1945-09-02":
        return "aftermath"
    return date[:4]


def as_list(v):
    if not v:
        return []
    return v if isinstance(v, list) else [v]


def sources(d):
    out = []
    for s in d.get("sources") or []:
        if isinstance(s, dict) and s.get("url"):
            out.append({"title": s.get("title") or s["url"], "url": s["url"]})
        elif isinstance(s, str) and s:
            out.append({"title": s, "url": s})
    return out


def link_row(links, keys):
    return {name: links[k] for name, k in keys.items() if links.get(k)}


def tags(d):
    t = d.get("themes") or {}
    return {
        "subjects": as_list(d.get("subject")),
        "theater": as_list(t.get("theater")),
        "nations": as_list(t.get("nations")),
        # who, story, and branch drive the Declass subject filter (values from analytics/themes.md)
        "who": as_list(t.get("who")),
        "story": as_list(t.get("story")),
        "branch": as_list(t.get("branch")),
    }


catalog, skipped = [], []

# Dispatch cards. Same post date rule as series_log.py: the recorded posted date, otherwise the
# event's month and day in the posting year (stepping up a year after December).
dispatches = sorted([d for d in load("dispatches") if d.get("num") is not None], key=lambda d: d["num"])
year, last_md = LAUNCH_YEAR, None
for d in dispatches:
    md = d["date"][5:]
    if last_md and md < last_md:
        year += 1
    last_md = md
    links = d.get("links") or {}
    post_date = links.get("posted") or f"{year}-{md}"
    num = f"{d['num']:03d}"
    img = card_url(f"cards/dispatch-{num}-instagram.jpg")
    if not img:
        skipped.append(f"No. {num} (no card image yet)")
        continue

    film = None
    video, kit = d.get("video") or {}, d.get("kit") or {}
    if video and kit and not d.get("story"):  # a real Living Card, not a Story Card
        sound = ((d.get("themes") or {}).get("video") or {}).get("sound")
        film = {
            "postAt": utc(post_date, "12:00"),
            "mp4": f"{VIDEOS_CDN}dispatch-{num}-instagram.mp4",
            "poster": f"{VIDEOS_CDN}dispatch-{num}-instagram-poster.jpg",
            "caption": kit.get("filmCaption", ""),
            "sourceUrl": video.get("sourceUrl", ""),
            "sound": bool(video.get("sound")) or bool(sound and sound != "silent"),
            "links": link_row(links, FILM_LINKS),
        }

    catalog.append({
        "kind": "dispatch",
        "id": d["id"],
        "num": d["num"],
        "series": d["series"],
        "seriesName": SERIES.get(d["series"], d["series"]),
        # Flash cards (Roadmap, Flash cards plan): always Top Secret in the game, no serial, guaranteed
        # in that day's commemorative file, 1 in 200 as an archive pull.
        "flash": d["series"] == "flash",
        "short": d.get("short") or d.get("title", ""),
        "title": d.get("title", ""),
        "date": d["date"],
        "place": d.get("place", ""),
        "era": era(d["date"]),
        "format": d.get("format") or "story",
        "postAt": utc(post_date, d.get("time") or "08:00"),
        "img": img,
        "story": d.get("body", ""),
        "photoCredit": d.get("photoCredit") or "",
        "photoUrl": d.get("photoUrl") or "",
        "sources": sources(d),
        "links": link_row(links, CARD_LINKS),
        "film": film,
        **tags(d),
    })

# Name This cards. One joins the pool only when its answer is public, which is when the next
# Name This posts; the newest puzzle has no answer time yet and is never handed out.
puzzles = sorted([n for n in load("namethis") if n.get("post_date")], key=lambda n: (n["post_date"], n["id"]))
post_times = [utc(n["post_date"], n.get("time") or "10:00") for n in puzzles]
for i, n in enumerate(puzzles):
    fallback = card_url(f"cards/namethis-{n['id']}-x.jpg") or n.get("cardImage")
    img_a = card_url(f"cards/namethis-{n['id']}-game-a.jpg") or fallback
    img_q = card_url(f"cards/namethis-{n['id']}-game-q.jpg") or fallback
    if not img_a:
        skipped.append(f"Name This {n['id']} (no card image yet)")
        continue
    links = n.get("links") or {}
    catalog.append({
        "kind": "namethis",
        "id": f"namethis-{n['id']}",
        "num": None,
        "series": "namethis",
        "seriesName": "Name This",
        "short": n.get("short") or n.get("answer", ""),
        "title": n.get("answer", ""),
        "answer": n.get("answer", ""),
        "clue": (n.get("pull") or "").removeprefix("Clue:").strip(),
        "date": n.get("date", ""),
        "place": n.get("place", ""),
        "era": era(n.get("date", "")),
        "format": "namethis",
        "postAt": post_times[i],
        "answerAt": post_times[i + 1] if i + 1 < len(post_times) else None,
        "img": img_a,
        "imgPuzzle": img_q,
        "gameImages": bool(card_url(f"cards/namethis-{n['id']}-game-a.jpg")),
        "story": n.get("body", ""),
        "photoCredit": n.get("photoCredit") or "",
        "photoUrl": n.get("photoUrl") or "",
        "sources": sources(n),
        "links": link_row(links, CARD_LINKS),
        "film": None,
        **tags(n),
    })

catalog.sort(key=lambda c: (c["postAt"], c["id"]))
out = os.path.join(root, "functions", "_data", "catalog.json")
os.makedirs(os.path.dirname(out), exist_ok=True)
with open(out, "w", encoding="utf-8") as f:
    # One card per line: small, and a weekly run's change shows as a few changed lines.
    f.write('{"version": 1, "cards": [\n')
    f.write(",\n".join(json.dumps(c, ensure_ascii=False, separators=(",", ":")) for c in catalog))
    f.write("\n]}\n")

n_disp = sum(1 for c in catalog if c["kind"] == "dispatch")
n_film = sum(1 for c in catalog if c["film"])
print(f"functions/_data/catalog.json: {n_disp} dispatch cards ({n_film} with film), "
      f"{len(catalog) - n_disp} Name This cards" + (f"; skipped {', '.join(skipped)}" if skipped else ""))
