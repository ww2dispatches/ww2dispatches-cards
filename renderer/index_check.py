#!/usr/bin/env python3
"""Check the WW2 Dispatches index: the date bank and the entity layer.

Run from the repo root:  python3 renderer/index_check.py
Rules live in the Project doc "WW2 Dispatches Index". Exit code 1 on any error.
Reads entities/<type>.json and entities/links.json here, dispatches/, namethis/ and
bank/ to confirm linked record ids exist, and the date bank from the private repo
ww2dispatches-datebank, cloned beside this one (or pass --datebank <its folder>).
"""
import glob, json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TYPES = {"person": "people", "ship": "ships", "unit": "units", "aircraft": "aircraft",
         "machine": "machines", "place": "places", "op": "operations"}
SERIES = {"Battle Lines", "Home Front", "Blueprint", "Statecraft"}
THEATERS = {"Western Europe", "Eastern Front", "Mediterranean and North Africa", "Atlantic",
            "Pacific", "China Burma India", "home front", "worldwide"}
LENSES = {"us", "commonwealth", "soviet", "other_allied", "axis_germany", "axis_japan",
          "axis_italy", "civilian_neutral"}
ROLES = {"subject", "involved", "mentioned"}
DAYS = [31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
DASH = re.compile("[‒–—―]| - ")
errors, warns = [], []
BANK = os.path.join(os.path.dirname(ROOT), "ww2dispatches-datebank", "datebank")
if "--datebank" in sys.argv:
    BANK = os.path.abspath(sys.argv[sys.argv.index("--datebank") + 1])


def p(*parts):
    return os.path.join(ROOT, *parts)


def load(path):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:  # a broken file is an error, not a crash
        errors.append(f"{os.path.relpath(path, ROOT)}: cannot read ({e})")
        return None


def text_ok(where, s):
    if isinstance(s, str) and DASH.search(s):
        errors.append(f"{where}: dash used as punctuation (house rule: commas or a new sentence)")


def check_entities():
    reg = {}
    for prefix, fname in TYPES.items():
        path = p("entities", fname + ".json")
        if not os.path.exists(path):
            continue
        data = load(path) or {}
        for eid, e in data.items():
            where = f"entities/{fname}.json {eid}"
            if not re.fullmatch(prefix + r"-[a-z0-9]+(-[a-z0-9]+)*", eid):
                errors.append(f"{where}: id must be '{prefix}-' plus lowercase words joined by hyphens")
            if eid in reg:
                errors.append(f"{where}: id used twice")
            for k in ("name", "kind", "nation", "source"):
                if not e.get(k):
                    errors.append(f"{where}: missing {k}")
            q = e.get("wikidata")
            if q is not None and not re.fullmatch(r"Q[0-9]+", str(q)):
                errors.append(f"{where}: wikidata must be a Q number or null")
            if prefix == "place":
                lat, lon = e.get("lat"), e.get("lon")
                if (lat is None) != (lon is None):
                    errors.append(f"{where}: give both lat and lon, or neither")
                elif lat is not None and not (-90 <= lat <= 90 and -180 <= lon <= 180):
                    errors.append(f"{where}: lat or lon out of range")
            text_ok(where, e.get("name")); text_ok(where, e.get("note"))
            reg[eid] = e
    # same name or same Q number under two ids is almost always a duplicate
    seen = {}
    for eid, e in reg.items():
        for key in (("n", (e.get("name") or "").lower()), ("q", e.get("wikidata"))):
            if key[1]:
                if key in seen:
                    warns.append(f"possible duplicate entity: {seen[key]} and {eid}")
                seen[key] = eid
    return reg


def record_ids():
    ids = set()
    for folder in ("dispatches", "namethis", "bank"):
        for path in glob.glob(p(folder, "*.json")):
            ids.add(os.path.basename(path)[:-5])
    return ids


def check_links(reg, recs):
    path = p("entities", "links.json")
    if not os.path.exists(path):
        return {}
    links = load(path) or {}
    for rid, items in links.items():
        where = f"entities/links.json {rid}"
        if recs and rid not in recs:
            errors.append(f"{where}: no such record in dispatches/, namethis/ or bank/")
        got = [i.get("id") for i in items]
        if len(got) != len(set(got)):
            errors.append(f"{where}: an entity is listed twice")
        if not any(i.get("role") == "subject" for i in items):
            errors.append(f"{where}: needs at least one subject")
        for i in items:
            if i.get("id") not in reg:
                errors.append(f"{where}: unknown entity {i.get('id')}")
            if i.get("role") not in ROLES:
                errors.append(f"{where}: role must be one of {sorted(ROLES)}")
    return links


def check_datebank(reg, recs):
    files, events, ids = 0, 0, set()
    thin = []
    for path in sorted(glob.glob(os.path.join(BANK, "*.json"))):
        name = os.path.basename(path)[:-5]
        m = re.fullmatch(r"(\d\d)-(\d\d)", name)
        if not m or not (1 <= int(m[1]) <= 12 and 1 <= int(m[2]) <= DAYS[int(m[1]) - 1]):
            errors.append(f"datebank/{name}.json: file name must be a real MM-DD date")
            continue
        d = load(path)
        if d is None:
            continue
        files += 1
        if d.get("date") != name:
            errors.append(f"datebank/{name}.json: date field must be {name}")
        evs = d.get("events", [])
        events += len(evs)
        open_evs = [e for e in evs if e.get("status") == "open"]
        if len(open_evs) < 8 or sum(e.get("lens", "").startswith("axis") for e in open_evs) < 2 \
                or not any(e.get("series") == "Home Front" for e in open_evs):
            if not d.get("thin"):
                warns.append(f"datebank/{name}.json: under target (8 open events, 2 Axis lens, 1 Home Front) "
                             f"and not marked thin: {len(open_evs)} open")
            else:
                thin.append(name)
        for e in evs:
            where = f"datebank/{name}.json {e.get('id')}"
            eid = e.get("id", "")
            if not re.fullmatch(r"\d{4}-" + name + r"-[a-z0-9]+(-[a-z0-9]+)*", eid):
                errors.append(f"{where}: id must be YYYY-{name}-short-name")
            elif int(eid[:4]) != e.get("year"):
                errors.append(f"{where}: year does not match id")
            if eid in ids:
                errors.append(f"{where}: id used twice")
            ids.add(eid)
            if not (1930 <= (e.get("year") or 0) <= 1949):
                errors.append(f"{where}: year outside 1930 to 1949")
            for k, allowed in (("series", SERIES), ("theater", THEATERS), ("lens", LENSES),
                               ("tier", {"A", "B", "C"}), ("status", {"open", "used", "related"}),
                               ("date_check", {"confirmed", "disputed"})):
                if e.get(k) not in allowed:
                    errors.append(f"{where}: {k} must be one of {sorted(allowed)}")
            for k in ("title", "summary", "nations"):
                if not e.get(k):
                    errors.append(f"{where}: missing {k}")
            if len(e.get("sources", [])) < 2:
                errors.append(f"{where}: needs two independent sources")
            for s in e.get("sources", []):
                if not (s.get("title") and str(s.get("url", "")).startswith("http")):
                    errors.append(f"{where}: each source needs a title and a url")
            if e.get("date_check") == "disputed" and not e.get("date_note"):
                errors.append(f"{where}: a disputed date needs a date_note saying what the sources give")
            if e.get("status") in ("used", "related"):
                if not e.get("dispatch"):
                    errors.append(f"{where}: status {e.get('status')} needs the dispatch id")
                elif recs and e["dispatch"] not in recs:
                    errors.append(f"{where}: dispatch {e['dispatch']} not found")
            st = e.get("story") or {}
            if e.get("tier") == "A" and not all(st.get(k) for k in ("person", "stakes", "twist")):
                errors.append(f"{where}: tier A needs a person, stakes and a twist")
            for x in e.get("entities", []):
                if x not in reg:
                    errors.append(f"{where}: unknown entity {x}")
            for k in ("title", "summary", "date_note", "note"):
                text_ok(where, e.get(k))
            for k in ("person", "stakes", "twist"):
                text_ok(where, st.get(k))
    return files, events, thin


def main():
    reg = check_entities()
    recs = record_ids()
    links = check_links(reg, recs)
    if not os.path.isdir(BANK):
        warns.append(f"date bank folder not found at {BANK}; clone ww2dispatches-datebank beside this repo")
    files, events, thin = check_datebank(reg, recs)
    unlinked = sorted(recs - set(links)) if recs else []
    no_coords = [k for k, e in reg.items() if k.startswith("place-") and e.get("lat") is None]
    no_q = [k for k, e in reg.items() if not e.get("wikidata")]
    print(f"Date bank: {files} of 366 dates, {events} events" + (f", {len(thin)} marked thin" if thin else ""))
    print(f"Entities: {len(reg)} ({len(no_q)} without a Wikidata number, {len(no_coords)} places without coordinates)")
    if recs:
        print(f"Records linked: {len(links)} of {len(recs)}" + (f"; next unlinked: {', '.join(unlinked[:5])}" if unlinked else ""))
    for w in warns:
        print("WARN ", w)
    for e in errors:
        print("ERROR", e)
    print("OK" if not errors else f"{len(errors)} errors")
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
