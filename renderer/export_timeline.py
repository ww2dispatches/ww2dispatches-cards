#!/usr/bin/env python3
"""Export the public timeline for the On this day archive (Archive Site Design Notes, 28 Nov 2026).

The date bank (private repo ww2dispatches-datebank) holds every banked event with its notes and sources.
The archive's date pages show only a headline line per event (year, series, title), so this script copies
just those three fields into timeline/onthisday.json in this repo, which renderer/dispatch_pages.py reads.

Each row is [year, series, headline, bank id]; the id lets a date page hide the line once a dispatch tells that
event (renderer/dispatch_pages.py same_event).
Left out: events already posted as a dispatch (status "used"; the dispatch itself shows instead) and events
whose date is still disputed (date_check "disputed"), so no headline sits on a date we are unsure of.

Run it whenever the bank changes:  python3 renderer/export_timeline.py [path to the datebank repo]
"""
import glob, json, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SERIES = {"Battle Lines": "battle", "Home Front": "home", "Blueprint": "blue", "Statecraft": "state"}


def main():
    bank = sys.argv[1] if len(sys.argv) > 1 else os.environ.get("DATEBANK") or os.path.join(os.path.dirname(ROOT), "ww2dispatches-datebank")
    files = sorted(glob.glob(os.path.join(bank, "datebank", "*.json")))
    if len(files) < 366:
        sys.exit(f"export_timeline: expected 366 date files in {bank}/datebank, found {len(files)}")
    out, n, left = {}, 0, 0
    for f in files:
        md = os.path.basename(f)[:-5]
        rows = []
        for e in json.load(open(f, encoding="utf-8"))["events"]:
            if e.get("status") == "used" or e.get("date_check") == "disputed":
                left += 1
                continue
            t = (e.get("title") or "").strip()
            if not t or any(ch in t for ch in "–—"):
                left += 1
                continue
            rows.append([int(e["year"]), SERIES.get(e.get("series"), "battle"), t, e.get("id", "")])
        rows.sort(key=lambda r: (r[0], r[2]))
        out[md] = rows
        n += len(rows)
    os.makedirs(os.path.join(ROOT, "timeline"), exist_ok=True)
    path = os.path.join(ROOT, "timeline", "onthisday.json")
    json.dump(out, open(path, "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
    print(f"export_timeline: {n} headlines on {len(out)} dates written to timeline/onthisday.json ({left} left out)")


if __name__ == "__main__":
    main()
