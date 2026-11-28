#!/usr/bin/env python3
"""Fill Wikidata numbers and place coordinates in entities/ from Wikidata.

Uses the Wikidata query service (query.wikidata.org), which looks up many
Wikipedia pages per request and is far less rate limited than the API.

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


def sparql(query):
    for wait in (0, 15, 45, 90):
        time.sleep(wait)
        out = subprocess.run(["curl", "-sS", "-m", "120", "-A", "ww2dispatches-index/1.0 (contact@ww2dispatches.com)",
                              "-H", "Accept: application/sparql-results+json",
                              "--data-urlencode", "query=" + query, "https://query.wikidata.org/sparql"],
                             capture_output=True, text=True).stdout
        try:
            return json.loads(out)["results"]["bindings"]
        except Exception:
            continue
    sys.exit("Wikidata did not answer; files keep what was written so far. Run again later.")


def lookup(urls):
    """Map each enwiki URL to (Q number, (lat, lon) or None)."""
    vals = " ".join("<" + u + ">" for u in urls)
    rows = sparql("SELECT ?a ?item (SAMPLE(?c) AS ?coord) WHERE { VALUES ?a { " + vals + " } "
                  "?a schema:about ?item ; schema:isPartOf <https://en.wikipedia.org/> . "
                  "OPTIONAL { ?item wdt:P625 ?c } } GROUP BY ?a ?item")
    got = {}
    for r in rows:
        q = r["item"]["value"].rsplit("/", 1)[1]
        c = None
        if "coord" in r:
            lon, lat = r["coord"]["value"][6:-1].split()[:2]
            c = (round(float(lat), 4), round(float(lon), 4))
        got[r["a"]["value"]] = (q, c)
    return got


def canon(src):
    t = urllib.parse.unquote(src[len(PREFIX):]).split("#")[0].replace(" ", "_")
    t = t[:1].upper() + t[1:]  # Wikipedia titles start with a capital
    return PREFIX + urllib.parse.quote(t, safe="_(),!:*;@$&+=-.~")


def main():
    filled_q, filled_c, review = 0, 0, []
    for name in FILES:
        path = os.path.join(ROOT, "entities", name + ".json")
        if not os.path.exists(path):
            continue
        data = json.load(open(path, encoding="utf-8"))
        want = {}
        for eid, e in data.items():
            need = not e.get("wikidata") or (eid.startswith("place-") and e.get("lat") is None)
            if not need:
                continue
            src = e.get("source", "")
            if src.startswith(PREFIX):
                want[canon(src)] = eid
            else:
                review.append(f"{eid}: source is not a Wikipedia page, fill by hand")
        urls = list(want)
        for i in range(0, len(urls), 150):
            got = lookup(urls[i:i + 150])
            for u in urls[i:i + 150]:
                eid = want[u]
                if u not in got:
                    review.append(f"{eid}: no Wikidata item for {u} (redirect or renamed page?)")
                    continue
                q, c = got[u]
                e = data[eid]
                if not e.get("wikidata"):
                    e["wikidata"] = q; filled_q += 1
                elif e["wikidata"] != q:
                    review.append(f"{eid}: stored {e['wikidata']} but page is {q}")
                if eid.startswith("place-") and e.get("lat") is None:
                    if c:
                        e["lat"], e["lon"] = c; filled_c += 1
                    else:
                        review.append(f"{eid}: Wikidata item {q} has no coordinates")
            json.dump(data, open(path, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
            time.sleep(2)
    print(f"Filled {filled_q} Wikidata numbers and {filled_c} coordinates")
    for r in review:
        print("REVIEW", r)


if __name__ == "__main__":
    main()
