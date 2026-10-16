#!/usr/bin/env python3
"""Build the Facebook day files that the Make scenario reads.

One file per posting day: facebook/YYYY-MM-DD.json, holding that day's
8 a.m. still card. The Make scenario fetches today's file every morning;
if there is no file, nothing posts.

Usage: python3 renderer/facebook_queue.py 2026-10-17 2026-10-24
(posting dates are inclusive; the posting year is the first argument's year)
"""
import json, sys, glob, os, datetime

RAW = "https://raw.githubusercontent.com/ww2dispatches/ww2dispatches-cards/main/"
start, end = (datetime.date.fromisoformat(a) for a in sys.argv[1:3])
year = start.year

by_day = {}
for f in glob.glob("dispatches/*.json"):
    d = json.load(open(f))
    m, dd = d["date"][5:7], d["date"][8:10]
    day = datetime.date(year, int(m), int(dd))
    if start <= day <= end:
        by_day.setdefault(day, []).append(d)

os.makedirs("facebook", exist_ok=True)
for day, items in sorted(by_day.items()):
    d = sorted(items, key=lambda x: x["num"])[0]   # the 8 a.m. dispatch
    caption = d["body"].rstrip() + "\n\n#OnThisDay #WW2"
    out = {
        "date": day.isoformat(),
        "dispatch": f'{d["num"]:03d}',
        "image": f'{RAW}cards/dispatch-{d["num"]:03d}-instagram.jpg',
        "caption": caption,
    }
    path = f"facebook/{day.isoformat()}.json"
    json.dump(out, open(path, "w"), indent=2, ensure_ascii=False)
    print("wrote", path, "No.", out["dispatch"], len(caption), "chars")
