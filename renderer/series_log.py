"""Build the WW2 Dispatches series log from the dispatch JSON files.

Writes two files:
  log/series-log.csv     one row per card: number, post date and time, series, format, event date, title
  log/series-counts.csv  running totals per series

Run from the repo root:  python3 renderer/series_log.py
The Friday batch runs this after scheduling, so the log never needs typing by hand.
"""
import csv, glob, json, os
from collections import Counter

LAUNCH_YEAR = 2026
SERIES = {"battle": "Battle Lines", "home": "Home Front", "blue": "Blueprint", "state": "Statecraft"}
FORMATS = {None: "Story", "photo": "Photo of the Day", "quote": "Quote of the Day", "spec": "Spec Sheet"}

root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
cards = []
for path in glob.glob(os.path.join(root, "dispatches", "*.json")):
    d = json.load(open(path, encoding="utf-8"))
    if d.get("num") is None:
        continue
    cards.append(d)
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
    posted = (d.get("links") or {}).get("posted") or f"{year}-{md}"
    time = d.get("time") or "08:00"
    rows.append({
        "dispatch_no": f"{d['num']:03d}",
        "post_date": posted,
        "post_time": time,
        "slot": "Evening" if time >= "12:00" else "Morning",
        "series": SERIES.get(d["series"], d["series"]),
        "format": FORMATS.get(d.get("format"), d.get("format")),
        "event_date": d["date"],
        "title": d.get("title", ""),
        "living_card": "yes" if d.get("kit") else "",
    })

os.makedirs(os.path.join(root, "log"), exist_ok=True)
with open(os.path.join(root, "log", "series-log.csv"), "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
    w.writeheader()
    w.writerows(rows)

total = len(rows)
by_series = Counter(r["series"] for r in rows)
by_slot = Counter((r["series"], r["slot"]) for r in rows)
with open(os.path.join(root, "log", "series-counts.csv"), "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["series", "cards", "morning", "evening", "share"])
    for s in SERIES.values():
        n = by_series[s]
        w.writerow([s, n, by_slot[(s, "Morning")], by_slot[(s, "Evening")], f"{n / total:.0%}" if total else "0%"])
    w.writerow(["All series", total, sum(1 for r in rows if r["slot"] == "Morning"),
                sum(1 for r in rows if r["slot"] == "Evening"), "100%"])

print(f"{total} cards logged, through No. {rows[-1]['dispatch_no']} on {rows[-1]['post_date']}")
