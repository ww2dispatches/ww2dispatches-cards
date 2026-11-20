#!/usr/bin/env python3
"""Fill Wikidata numbers and place coordinates in entities/ from Wikidata.

Run from the repo root:  python3 renderer/index_fill.py
For each entity whose `source` is an English Wikipedia page, looks the page up on
Wikidata by its title (sitelink enwiki). Writes the Q number when `wikidata` is
null, and for places with no coordinates, the coordinate location (P625).
It never guesses: a title with no Wikidata item is listed for a person to check.
Places that already have a Q number get their coordinates from that item.
"""
import json, os, subprocess, sys, time, urllib.parse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FILES = ["people", "ships", "units", "aircraft", "machines", "places", "operations"]
API = "https://www.wikidata.org/w/api.php"
PREFIX = "https://en.wikipedia.org/wiki/"


def get(params):
    q = urllib.parse.urlencode(dict(params, format="json"))
    for wait in (0, 10, 30, 60):
        time.sleep(wait)
        out = subprocess.run(["curl", "-sS", "-m", "60", "-A", "ww2dispatches-index/1.0 (contact@ww2dispatches.com)",
                              API + "?" + q], capture_output=True, text=True).stdout
        try:
            return json.loads(out)["entities"]
        except Exception:
            continue
    sys.exit("Wikidata did not answer; files keep what was written so far. Run again later.")


def coord(item):
    for c in item.get("claims", {}).get("P625", []):
        v = c.get("mainsnak", {}).get("datavalue", {}).get("value")
        if v:
            return round(v["latitude"], 4), round(v["longitude"], 4)
    return None


def main():
    filled_q, filled_c, review = 0, 0, []
    for name in FILES:
        path = os.path.join(ROOT, "entities", name + ".json")
        if not os.path.exists(path):
            continue
        data = json.load(open(path, encoding="utf-8"))
        by_title, by_q = {}, {}
        for eid, e in data.items():
            place_needs = eid.startswith("place-") and e.get("lat") is None
            if e.get("wikidata"):
                if place_needs:
                    by_q[e["wikidata"]] = eid
                continue
            src = e.get("source", "")
            if src.startswith(PREFIX):
                by_title[urllib.parse.unquote(src[len(PREFIX):]).replace("_", " ").split("#")[0]] = eid
            else:
                review.append(f"{eid}: source is not a Wikipedia page, fill by hand")
        titles = list(by_title)
        for i in range(0, len(titles), 50):
            ents = get({"action": "wbgetentities", "sites": "enwiki", "titles": "|".join(titles[i:i + 50]),
                        "props": "sitelinks|claims", "sitefilter": "enwiki", "normalize": 1})
            seen = set()
            for qid, item in ents.items():
                t = item.get("sitelinks", {}).get("enwiki", {}).get("title")
                if not t or qid.startswith("-"):
                    continue
                eid = by_title.get(t)
                if not eid:
                    continue
                seen.add(t)
                data[eid]["wikidata"] = qid; filled_q += 1
                if eid.startswith("place-") and data[eid].get("lat") is None:
                    c = coord(item)
                    if c:
                        data[eid]["lat"], data[eid]["lon"] = c; filled_c += 1
                    else:
                        review.append(f"{eid}: Wikidata item {qid} has no coordinates")
            for t in titles[i:i + 50]:
                if t not in seen:
                    review.append(f"{by_title[t]}: no Wikidata item found for '{t}' (redirect or renamed page?)")
            json.dump(data, open(path, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
            time.sleep(1)
        qs = list(by_q)
        for i in range(0, len(qs), 50):
            ents = get({"action": "wbgetentities", "ids": "|".join(qs[i:i + 50]), "props": "claims"})
            for qid, item in ents.items():
                eid = by_q.get(qid)
                c = coord(item) if eid else None
                if c:
                    data[eid]["lat"], data[eid]["lon"] = c; filled_c += 1
                elif eid:
                    review.append(f"{eid}: Wikidata item {qid} has no coordinates")
            json.dump(data, open(path, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
            time.sleep(1)
    print(f"Filled {filled_q} Wikidata numbers and {filled_c} coordinates")
    for r in review:
        print("REVIEW", r)


if __name__ == "__main__":
    main()
