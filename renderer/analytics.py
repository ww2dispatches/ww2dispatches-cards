"""Score every WW2 Dispatches post from the weekly Buffer snapshots.

Run from the repo root:  python3 renderer/analytics.py
The Wednesday analytics review saves a snapshot to analytics/snapshots/YYYY-MM-DD.json,
then runs this script. The method is in the Project's Analytics doc; in short:

  * Each post is matched to its record in dispatches/ or namethis/ by its Buffer id.
    X Name This posts (sent by Typefully) match by their X link or their post date.
    Anything else is listed as unmatched, never guessed.
  * A post's reading is the latest one in any snapshot. Under 48 hours old it is
    "too early" and not scored; from 48 hours it is "provisional"; from 7 days "final".
  * Cards, Name This, and videos are each judged only against their own kind, on the
    same platform, over the last 28 days of posts.
  * Reach = (views + 10) / (typical views + 10). 1.0 is typical.
  * Response = weighted actions per 100 views (like 1, comment 3, repost, quote,
    share, or save 2), divided by the typical figure. Only posts with 50+ views.
  * A platform counts toward a post's score once its typical post reaches 50 views
    and at least 5 posts of that kind have been scored there.
  * Groups (series, format, slot, themes) need 5+ posts or they show "not enough data".
  * Videos also get hold: average seconds watched as a share of the video's length.

Writes:
  log/performance-log.csv      one row per post per platform (Excel friendly)
  analytics/scoreboard.json    everything the Scoreboard page shows
  analytics/scoreboard-page.html  the Scoreboard page with that data built in
Never edit these by hand; the snapshots and the JSON records are the source.
"""
import csv, glob, json, os, re, statistics
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MOUNTAIN = ZoneInfo("America/Denver")
SERIES = {"battle": "Battle Lines", "home": "Home Front", "blue": "Blueprint", "state": "Statecraft", "flash": "Flash"}
FORMATS = {None: "Story", "photo": "Photo of the Day", "quote": "Quote of the Day", "spec": "Spec Sheet"}
PLATFORM = {"twitter": "X", "instagram": "Instagram", "threads": "Threads", "facebook": "Facebook",
            "youtube": "YouTube", "tiktok": "TikTok"}
VIDEO_KEYS = {"x_film", "instagram_reel", "threads_film", "facebook_film", "youtube", "tiktok"}
SMOOTH, FLOOR, MIN_POSTS, WINDOW_DAYS = 10, 50, 5, 28
WEIGHTS = {"reactions": 1, "likes": 1, "comments": 3, "reposts": 2, "quotes": 2, "shares": 2, "saves": 2}


def p(*parts):
    return os.path.join(ROOT, *parts)


def ts(s):
    return datetime.fromisoformat(s.replace("Z", "+00:00")) if s else None


def load_records():
    recs = []
    for folder in ("dispatches", "namethis"):
        for path in sorted(glob.glob(p(folder, "*.json"))):
            d = json.load(open(path, encoding="utf-8"))
            d["_file"] = f"{folder}/{os.path.basename(path)}"
            d["_kind"] = "namethis" if folder == "namethis" else "card"
            recs.append(d)
    return recs


def theme_vocab():
    """Read the allowed tag values from analytics/themes.md (the one place they are listed)."""
    vocab, section = defaultdict(set), None
    path = p("analytics", "themes.md")
    if not os.path.exists(path):
        return vocab
    for line in open(path, encoding="utf-8"):
        m = re.match(r"## (\w+)", line)
        if m:
            section = m.group(1)
            continue
        if section and " · " in line:
            if line.startswith("* **"):
                m = re.match(r"\* \*\*(\w+):\*\* (.*)", line.strip())
                if m:
                    vocab["video." + m.group(1)].update(v.strip() for v in m.group(2).split(": ")[-1].split(" · "))
            else:
                vocab[section].update(v.strip() for v in line.strip().split(" · "))
    return vocab


def check_themes(recs, vocab):
    problems = []
    for d in recs:
        t = d.get("themes")
        if not t:
            problems.append(f"{d['_file']}: no themes block")
            continue
        for field in ("who", "story", "photo", "theater", "branch", "nations"):
            vals = t.get(field)
            vals = vals if isinstance(vals, list) else [vals] if vals else []
            for v in vals:
                if field == "nations" and v not in vocab["nations"]:
                    continue  # other nations are written by name
                if vocab.get(field) and v not in vocab[field]:
                    problems.append(f"{d['_file']}: {field} '{v}' is not in analytics/themes.md")
        for k, v in (t.get("video") or {}).items():
            if vocab.get("video." + k) and v not in vocab["video." + k]:
                problems.append(f"{d['_file']}: video {k} '{v}' is not in analytics/themes.md")
    return problems


def id_map(recs):
    """Buffer post id -> (record, is_video)."""
    out = {}
    for d in recs:
        for k, v in (d.get("buffer") or {}).items():
            if isinstance(v, str):
                out[v] = (d, k in VIDEO_KEYS)
        story = d.get("story") or {}
        for k, v in (story.get("buffer") or {}).items():
            if isinstance(v, str):
                out[v] = (d, True)
    return out


def load_snapshots():
    snaps = []
    for path in sorted(glob.glob(p("analytics", "snapshots", "*.json"))):
        s = json.load(open(path, encoding="utf-8"))
        s["_file"] = os.path.basename(path)
        snaps.append(s)
    return snaps


def match(post, ids, recs):
    if post["id"] in ids:
        return ids[post["id"]]
    alt = post.get("alt") or ""
    if post["service"] == "twitter" and alt.startswith("WW2 Dispatches Name This"):
        status = (post.get("link") or "").rstrip("/").split("/")[-1]
        sent_day = ts(post["sent"]).astimezone(MOUNTAIN).strftime("%Y-%m-%d")
        for d in recs:
            if d["_kind"] != "namethis":
                continue
            if status and status in ((d.get("links") or {}).get("x") or ""):
                return d, False
            if d.get("post_date") == sent_day:
                return d, False
    return None


def thumb(*names):
    """A small JPEG of the first card image found, as a data URI (the page can't load GitHub images)."""
    try:
        from PIL import Image
        import base64, io
    except ImportError:
        return None
    for name in names:
        path = p("cards", name)
        if name and os.path.exists(path):
            im = Image.open(path).convert("RGB")
            im.thumbnail((180, 180))
            buf = io.BytesIO()
            im.save(buf, "JPEG", quality=70)
            return "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode()
    return None


def views_of(m):
    return m.get("views", m.get("impressions"))


def main():
    recs = load_records()
    vocab = theme_vocab()
    ids = id_map(recs)
    snaps = load_snapshots()
    now = max((ts(s["pulled_at"]) for s in snaps), default=datetime.now(timezone.utc))

    latest, unmatched = {}, {}
    for s in snaps:
        for post in s["posts"]:
            hit = match(post, ids, recs)
            if not hit:
                if not (post.get("via") == "network" and post["service"] == "facebook"):
                    unmatched[post["id"]] = post
                continue
            unmatched.pop(post["id"], None)
            prev = latest.get(post["id"])
            if not prev or (post.get("updated") or "") >= (prev[0].get("updated") or ""):
                latest[post["id"]] = (post, hit)

    rows = []
    for pid, (post, (d, is_video)) in latest.items():
        m = post.get("m") or {}
        sent, updated = ts(post["sent"]), ts(post.get("updated")) or now
        age = (updated - sent).total_seconds() / 3600
        status = "final" if age >= 168 else "provisional" if age >= 48 else "too early"
        kind = "video" if is_video else d["_kind"]
        t = d.get("themes") or {}
        tv = t.get("video") or {}
        views = views_of(m)
        points = sum(WEIGHTS.get(k, 0) * (v or 0) for k, v in m.items())
        dur = post.get("dur") or 0
        avg = m.get("averageTimeWatched")
        join = lambda x: " | ".join(x) if isinstance(x, list) else (x or "")
        rows.append({
            "dispatch_no": f"{d['num']:03d}" if d.get("num") else "",
            "kind": {"card": "Card", "namethis": "Name This", "video": "Video"}[kind],
            "title": d.get("title") or d.get("answer", ""),
            "post_date": sent.astimezone(MOUNTAIN).strftime("%Y-%m-%d"),
            "post_time": sent.astimezone(MOUNTAIN).strftime("%H:%M"),
            "slot": {"08": "8 a.m.", "10": "10 a.m.", "12": "Noon", "17": "5 p.m."}.get(
                sent.astimezone(MOUNTAIN).strftime("%H"), sent.astimezone(MOUNTAIN).strftime("%H:%M")),
            "series": SERIES.get(d.get("series"), ""),
            "format": "" if d["_kind"] == "namethis" else
                      (tv.get("kind") or "Video") if is_video else FORMATS.get(d.get("format"), d.get("format")),
            "platform": PLATFORM.get(post["service"], post["service"]),
            "status": status,
            "age_hours": round(age),
            "views": views if views is not None else "",
            "reach_people": m.get("reach", ""),
            "likes": m.get("reactions", m.get("likes", "")),
            "comments": m.get("comments", ""),
            "reposts": (m.get("reposts") or 0) + (m.get("quotes") or 0) if ("reposts" in m or "quotes" in m) else "",
            "shares": m.get("shares", ""),
            "saves": m.get("saves", ""),
            "follows": m.get("follows", ""),
            "avg_watch_s": avg if avg is not None else "",
            "length_s": round(dur / 1000, 1) if dur else "",
            "hold_pct": round(avg / (dur / 1000) * 100) if (avg and dur) else "",
            "points": points,
            "response": round(points / views * 100, 2) if views and views >= FLOOR else "",
            "reach_lift": "", "response_lift": "", "counts": "",
            "theme_who": join(t.get("who")), "theme_story": join(t.get("story")),
            "theme_photo": join(t.get("photo")), "theater": join(t.get("theater")),
            "branch": join(t.get("branch")), "nations": join(t.get("nations")),
            "video_opening": tv.get("opening", "") if is_video else "",
            "video_sound": tv.get("sound", "") if is_video else "",
            "question": "yes" if d.get("question") else "",
            "carousel": "yes" if d.get("slides") and kind == "card" else "",
            "link": post.get("link", ""),
            "buffer_id": pid,
            "json_file": d["_file"],
            "_kind": kind, "_sent": sent,
        })

    # Baselines: same kind, same platform, scored posts from the last 28 days.
    cutoff = now - timedelta(days=WINDOW_DAYS)
    base = {}
    groups = defaultdict(list)
    for r in rows:
        if r["status"] != "too early" and r["views"] != "" and r["_sent"] >= cutoff:
            groups[(r["_kind"], r["platform"])].append(r)
    for key, rs in groups.items():
        vs = [r["views"] for r in rs]
        resp = [r["response"] for r in rs if r["response"] != ""]
        typical = statistics.median(vs)
        base[key] = {"posts": len(rs), "typical_views": typical,
                     "typical_response": statistics.median(resp) if resp else None,
                     "counts": typical >= FLOOR and len(rs) >= MIN_POSTS}
    for r in rows:
        b = base.get((r["_kind"], r["platform"]))
        if not b or r["status"] == "too early" or r["views"] == "":
            continue
        r["reach_lift"] = round((r["views"] + SMOOTH) / (b["typical_views"] + SMOOTH), 2)
        if r["response"] != "" and b["typical_response"]:
            r["response_lift"] = round(r["response"] / b["typical_response"], 2)
        r["counts"] = "yes" if b["counts"] else ""

    rows.sort(key=lambda r: (r["_sent"], r["platform"]))
    fields = ["dispatch_no", "kind", "title", "post_date", "post_time", "slot", "series", "format", "platform",
              "status", "age_hours", "views", "reach_people", "likes", "comments", "reposts", "shares", "saves",
              "follows", "avg_watch_s", "length_s", "hold_pct", "points", "response", "reach_lift",
              "response_lift", "counts", "theme_who", "theme_story", "theme_photo", "theater", "branch",
              "nations", "video_opening", "video_sound", "question", "carousel", "link", "buffer_id", "json_file"]
    os.makedirs(p("log"), exist_ok=True)
    with open(p("log", "performance-log.csv"), "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)

    # One score per post: the average over the platforms that count.
    posts = defaultdict(lambda: {"reach": [], "response": [], "rows": []})
    for r in rows:
        key = (r["json_file"], r["_kind"])
        posts[key]["rows"].append(r)
        if r["counts"] == "yes":
            posts[key]["reach"].append(r["reach_lift"])
            if r["response_lift"] != "":
                posts[key]["response"].append(r["response_lift"])
    by_file = {d["_file"]: d for d in recs}
    post_list = []
    for (file, kind), v in posts.items():
        d, r0 = by_file[file], v["rows"][0]
        statuses = {r["status"] for r in v["rows"]}
        status = "too early" if statuses == {"too early"} else "final" if "final" in statuses else "provisional"
        num = d.get("num")
        if num:
            image = thumb(f"dispatch-{num:03d}-instagram.jpg", f"dispatch-{num:03d}-x.jpg")
        else:
            image = thumb(f"namethis-{d.get('id', '')}-x.jpg")
        post_list.append({
            "id": f"{file}#{kind}", "kind": r0["kind"], "num": r0["dispatch_no"], "title": r0["title"],
            "date": min(r["post_date"] for r in v["rows"]), "slot": r0["slot"], "series": r0["series"],
            "format": r0["format"], "status": status, "image": image,
            "reach": round(statistics.mean(v["reach"]), 2) if v["reach"] else None,
            "response": round(statistics.mean(v["response"]), 2) if v["response"] else None,
            "themes": d.get("themes") or {},
            "question": bool(d.get("question")),
            "platforms": [{k: r[k] for k in ("platform", "status", "views", "likes", "comments", "reach_lift",
                                               "response_lift", "counts", "hold_pct", "link")} for r in v["rows"]],
        })
    post_list.sort(key=lambda x: (x["date"], x["slot"]), reverse=True)

    # Groups, within each kind, over posts that have a score.
    def group_table(kind, label, getter):
        acc = defaultdict(lambda: {"reach": [], "response": []})
        for x in post_list:
            if x["kind"] != kind or x["reach"] is None:
                continue
            vals = getter(x)
            for val in (vals if isinstance(vals, list) else [vals]):
                if val:
                    acc[val]["reach"].append(x["reach"])
                    if x["response"] is not None:
                        acc[val]["response"].append(x["response"])
        out = []
        for val, a in sorted(acc.items()):
            n = len(a["reach"])
            out.append({"group": label, "value": val, "posts": n,
                        "reach": round(statistics.mean(a["reach"]), 2),
                        "response": round(statistics.mean(a["response"]), 2) if a["response"] else None,
                        "usable": n >= MIN_POSTS})
        return out

    th = lambda f: (lambda x: x["themes"].get(f))
    group_tables = {
        "Card": [t for g in [
            ("Series", lambda x: x["series"]), ("Format", lambda x: x["format"]), ("Slot", lambda x: x["slot"]),
            ("Who", th("who")), ("Story", th("story")), ("Photo", th("photo")), ("Theater", th("theater")),
            ("Branch", th("branch")), ("Nations", th("nations")),
            ("Question", lambda x: "with question" if x["question"] else "no question")]
            for t in group_table("Card", *g)],
        "Video": [t for g in [
            ("Kind", lambda x: x["format"]), ("Opening", lambda x: (x["themes"].get("video") or {}).get("opening")),
            ("Sound", lambda x: (x["themes"].get("video") or {}).get("sound")), ("Series", lambda x: x["series"])]
            for t in group_table("Video", *g)],
        "Name This": [t for g in [("Photo", th("photo")), ("Theater", th("theater"))]
                      for t in group_table("Name This", *g)],
    }

    # Weekly views per platform (weeks run Sunday to Saturday by post date).
    weekly = defaultdict(lambda: defaultdict(int))
    for r in rows:
        if r["views"] == "":
            continue
        d0 = datetime.strptime(r["post_date"], "%Y-%m-%d")
        week = (d0 - timedelta(days=(d0.weekday() + 1) % 7)).strftime("%Y-%m-%d")
        weekly[week][r["platform"]] += r["views"]
    follows = defaultdict(int)
    for r in rows:
        if r["follows"] not in ("", None):
            follows[r["platform"]] += r["follows"]

    playbook = open(p("analytics", "playbook.md"), encoding="utf-8").read() if os.path.exists(p("analytics", "playbook.md")) else ""
    reviews = sorted(os.path.basename(f)[:-3] for f in glob.glob(p("analytics", "reviews", "*.md")))
    latest_review = open(p("analytics", "reviews", reviews[-1] + ".md"), encoding="utf-8").read() if reviews else ""

    board = {
        "generated": now.astimezone(MOUNTAIN).strftime("%Y-%m-%d %H:%M"),
        "snapshots": [s["_file"] for s in snaps],
        "first_review": "2026-10-28",
        "rules": {"floor": FLOOR, "min_posts": MIN_POSTS, "window_days": WINDOW_DAYS,
                  "weights": "like 1, comment 3, repost, quote, share, or save 2"},
        "baselines": [{"kind": k[0], "platform": k[1], **v} for k, v in sorted(base.items())],
        "posts": post_list,
        "groups": group_tables,
        "weekly_views": [{"week": w, **v} for w, v in sorted(weekly.items())],
        "instagram_follows_from_posts": follows.get("Instagram", 0),
        "playbook": playbook,
        "latest_review": latest_review,
        "reviews": reviews,
        "unmatched": [{"id": u["id"], "service": u["service"], "sent": u["sent"], "link": u.get("link")}
                      for u in unmatched.values()],
        "tag_problems": check_themes(recs, vocab),
    }
    json.dump(board, open(p("analytics", "scoreboard.json"), "w", encoding="utf-8"), indent=1,
              ensure_ascii=False, default=str)

    template = p("analytics", "scoreboard-template.html")
    if os.path.exists(template):
        html = open(template, encoding="utf-8").read()
        data = json.dumps(board, ensure_ascii=False, default=str).replace("</", "<\\/")
        open(p("analytics", "scoreboard-page.html"), "w", encoding="utf-8").write(
            html.replace("/*SCOREBOARD_DATA*/null", data))

    scored = sum(1 for x in post_list if x["reach"] is not None)
    print(f"{len(snaps)} snapshots, {len(rows)} post readings, {len(post_list)} posts, {scored} scored; "
          f"{len(board['unmatched'])} unmatched; {len(board['tag_problems'])} tag problems")
    for t in board["tag_problems"]:
        print("  tag:", t)
    for u in board["unmatched"]:
        print("  unmatched:", u)


if __name__ == "__main__":
    main()
