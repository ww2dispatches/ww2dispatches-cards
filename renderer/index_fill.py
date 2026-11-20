#!/usr/bin/env python3
"""Fill Wikidata numbers and place coordinates in entities/ from Wikipedia.

Run from the repo root:  python3 renderer/index_fill.py
For every entity whose `source` is an English Wikipedia page and whose `wikidata`
is null, asks Wikipedia for that page's Wikidata number (and, for places with no
coordinates, its coordinates) and writes them in. It never guesses: a missing
page, or a page that redirects to a different title, is listed for a person to
look at and left unchanged. Values are copied from the page, per the Index doc.
"""
import json, os, subprocess, sys, time, urllib.parse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FILES = ["people", "ships", "units", "aircraft", "machines", "places", "operations"]
API = "https://en.wikipedia.org/w/api.php"
PREFIX = "https://en.wikipedia.org/wiki/"


def ask(titles):
    # curl honors the workspace proxy; Wikipedia rate limits bursts, so back off and retry
    q = urllib.parse.urlencode({"action": "query", "prop": "pageprops|coordinates", "ppprop": "wikibase_item",
                                "redirects": 1, "format": "json", "titles": "|".join(titles)})
    for wait in (0, 10, 30, 60):
        time.sleep(wait)
        out = subprocess.run(["curl", "-sS", "-m", "40", API + "?" + q], capture_output=True, text=True).stdout
        try:
            return json.loads(out)["query"]
        except Exception:
            continue
    sys.exit("Wikipedia did not answer; nothing more written. Run again later.")


def main():
    filled, review = 0, []
    for name in FILES:
        path = os.path.join(ROOT, "entities", name + ".json")
        if not os.path.exists(path):
            continue
        data = json.load(open(path, encoding="utf-8"))
        want = {}
        for eid, e in data.items():
            src = e.get("source", "")
            need = not e.get("wikidata") or (eid.startswith("place-") and e.get("lat") is None)
            if need and src.startswith(PREFIX):
                want[urllib.parse.unquote(src[len(PREFIX):]).replace("_", " ")] = eid
            elif need:
                review.append(f"{eid}: source is not a Wikipedia page, fill by hand")
        titles = list(want)
        for i in range(0, len(titles), 40):
            q = ask(titles[i:i + 40])
            moved = {r["from"]: r["to"] for r in q.get("redirects", [])}
            moved.update({n["from"]: n["to"] for n in q.get("normalized", []) if n["from"] != n["to"].replace("_", " ")})
            pages = {pg["title"]: pg for pg in q["pages"].values()}
            for t in titles[i:i + 40]:
                eid = want[t]
                if t in moved:
                    review.append(f"{eid}: '{t}' redirects to '{moved[t]}'. Confirm it is the same thing, then fix the source link")
                    continue
                pg = pages.get(t)
                if pg is None or "missing" in pg:
                    review.append(f"{eid}: no Wikipedia page titled '{t}'")
                    continue
                e = data[eid]
                qn = pg.get("pageprops", {}).get("wikibase_item")
                if qn and not e.get("wikidata"):
                    e["wikidata"] = qn; filled += 1
                if eid.startswith("place-") and e.get("lat") is None:
                    c = pg.get("coordinates")
                    if c:
                        e["lat"], e["lon"] = round(c[0]["lat"], 4), round(c[0]["lon"], 4)
                    else:
                        review.append(f"{eid}: page has no coordinates")
            time.sleep(2)
        json.dump(data, open(path, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    print(f"Filled {filled} Wikidata numbers")
    for r in review:
        print("REVIEW", r)


if __name__ == "__main__":
    main()
