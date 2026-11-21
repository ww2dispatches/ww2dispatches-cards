"""The blind second read (FORMAT.md, The fact check, part 3).
A separate reader, who has not seen the day record, is given that day's situation map with a coordinate grid and the
roster entries of the units that move, and reports where the map shows each unit and the front line. This tool makes
the packet for the reader and then compares the reader's answers with the record.

  blind_read.py packet <series folder> <day number> <out dir> [night|start]
      writes tiles of the scan with a labelled grid (every 0.1 degree), units.txt (who to find, never where),
      INSTRUCTIONS.md and an empty answers.json. Give the reader ONLY this folder.
  blind_read.py compare <series folder> <day number> <answers.json> [night|start]
      night (the default) checks the night table against the NEXT day's map: the maps were drawn at noon, so a
      move made in the afternoon first shows on tomorrow's map. start checks the morning table against the day's own map.
      compares with the record, prints the result and writes <series folder>/verify/day-NN.json.
      A unit or a stretch of line more than one block (10 km) from the record sends the day back.
The reader must be a fresh agent or person with no access to the day records."""
import sys, os, json, math, numpy as np, cv2
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, '..', '..', 'engine'))
import series as S, register as R

def setup(folder, n, which='night'):
    """which: 'night' reads the NEXT day's map (the maps were drawn at noon, so tonight's table is first seen on
    tomorrow's map) and compares the night positions and line; 'start' reads the day's own map against the morning."""
    import datetime
    s = S.Series(folder); d = next(x for x in s.days if x['n'] == int(n)); date = d['rec']['date']
    if which == 'night': date = (datetime.date.fromisoformat(date) + datetime.timedelta(days=1)).isoformat()
    d = dict(d); d['cmp_pos'] = d['pm_true'] if which == 'night' else d['am_true']; d['cmp_line'] = d['line'] if which == 'night' else d['lineAM']; d['which'] = which
    if date not in s.cfg['maps']: raise SystemExit(f'no situation map listed for {date}')
    m = s.cfg['maps'][date]; g = m.get('georef') or R.register(s.campaign, date)
    def px(ll): return (g['X6'] + (ll[0] - 6) * 111.32 * math.cos(math.radians(ll[1])) * g['PXKM'], g['Y50'] - (ll[1] - 50) * 110.6 * g['PXKM'])
    return s, d, date, m, g, px
def targets(s, d):
    """the units the reader looks for: the ones that move today (and the ones they drive)"""
    return [u for u in dict.fromkeys(d['movers'])] or sorted(d['pm_true'])

def packet(folder, n, out, which='night'):
    s, d, date, m, g, px = setup(folder, n, which); os.makedirs(out, exist_ok=True)
    b = s.box; x0, y0 = [int(v) - 150 for v in px((b[0], b[3]))]; x1, y1 = [int(v) + 150 for v in px((b[1], b[2]))]; x0, y0 = max(0, x0), max(0, y0)
    im = R.fetch(m['iiif'], f'{x0},{y0},{x1 - x0},{y1 - y0}', 'full', f'{date}-battle.jpg').copy()
    H, W = im.shape[:2]
    def P(ll): q = px(ll); return (int(q[0] - x0), int(q[1] - y0))
    lon_a, lon_b = math.floor((b[0] - 0.2) * 10) / 10, math.ceil((b[1] + 0.2) * 10) / 10
    lat_a, lat_b = math.floor((b[2] - 0.2) * 10) / 10, math.ceil((b[3] + 0.2) * 10) / 10
    lons = [round(lon_a + 0.1 * i, 1) for i in range(int(round((lon_b - lon_a) * 10)) + 1)]
    lats = [round(lat_a + 0.1 * i, 1) for i in range(int(round((lat_b - lat_a) * 10)) + 1)]
    for lo in lons:
        whole = abs(lo * 2 - round(lo * 2)) < 1e-6
        cv2.polylines(im, [np.array([P((lo, la)) for la in lats], np.int32)], False, (200, 0, 200), 2 if whole else 1, cv2.LINE_AA)
    for la in lats:
        whole = abs(la * 2 - round(la * 2)) < 1e-6
        cv2.polylines(im, [np.array([P((lo, la)) for lo in lons], np.int32)], False, (200, 0, 200), 2 if whole else 1, cv2.LINE_AA)
    def tag(img, text, xy):                       # no box behind it: a label must not hide a unit symbol
        cv2.putText(img, text, xy, cv2.FONT_HERSHEY_SIMPLEX, 0.42, (255, 255, 255), 3, cv2.LINE_AA)
        cv2.putText(img, text, xy, cv2.FONT_HERSHEY_SIMPLEX, 0.42, (160, 0, 160), 1, cv2.LINE_AA)
    T = 900; step = 700; names = []
    for ty in range(0, max(1, H - 200), step):
        for tx in range(0, max(1, W - 200), step):
            t = im[ty:ty + T, tx:tx + T].copy()
            for lo in lons:
                for la in lats:
                    q = P((lo, la)); x, y = q[0] - tx, q[1] - ty
                    if 0 <= x < t.shape[1] - 70 and 14 <= y < t.shape[0] and (round(lo * 10) + round(la * 10)) % 2 == 0:
                        tag(t, f'{lo:.1f}E {la:.1f}N', (x + 3, y - 3))
            nm = f'tile-r{ty // step + 1}-c{tx // step + 1}.jpg'; cv2.imwrite(os.path.join(out, nm), t, [cv2.IMWRITE_JPEG_QUALITY, 90]); names.append(nm)
    cv2.imwrite(os.path.join(out, 'overview.jpg'), cv2.resize(im, (W // 3, H // 3), interpolation=cv2.INTER_AREA), [cv2.IMWRITE_JPEG_QUALITY, 85])
    tg = targets(s, d)
    with open(os.path.join(out, 'units.txt'), 'w') as f:
        for u in tg:
            U = s.units[u]; f.write(f"{u} | {U['name']} | {U['nation']} | {U['type']} | {U['parent']}\n")
    json.dump({'day': d['n'], 'date': date, 'units': {u: {'found': None, 'at': None, 'note': ''} for u in tg}, 'line': [], 'lineNote': ''},
              open(os.path.join(out, 'answers.json'), 'w'), indent=1)
    open(os.path.join(out, 'INSTRUCTIONS.md'), 'w').write(f"""# Blind read: {m['label']}

You are reading a wartime situation map on your own. Do not look for or open any other files. Work only from the images in this folder.

The map is the HQ Twelfth Army Group situation map for {date}, at 1 to 1,000,000. Unit symbols are drawn in black: a box with an X through it is infantry, an oval is armor, "AB" is airborne; hatched (shaded) boxes are German units. XX above a box is a division, XXX a corps, XXXX an army. The number beside the box is the unit's number. The heavy black line with small ticks is the front line.

A purple grid has been drawn on the map every 0.1 degree, with labels such as `5.7E 50.0N` at the grid crossings. Thicker grid lines are the half and whole degrees. `overview.jpg` shows the whole area small; the `tile-rN-cM.jpg` files are the same area at full size, row by row from the north west, overlapping.

## What to report
1. **Each unit in `units.txt`** (id | name | nation | type | parent). Find its symbol and give the position of the middle of the symbol's box as `[longitude, latitude]` to two decimals, read from the grid. If you cannot find it, set `"found": false` and say why in `note`. If you find it but are unsure it is the right unit, give the position and say so in `note`. Do not guess a position for a unit you cannot see.
2. **The front line** across the whole area: 20 to 40 `[longitude, latitude]` points along the heavy ticked line, starting where it enters at the north and ending where it leaves at the south or east, following it around any bulge in order. Put anything unclear in `lineNote`.

Write your answers into `answers.json` in this folder, keeping its shape: for each unit `{{"found": true, "at": [lon, lat], "note": ""}}`, and `"line": [[lon, lat], ...]`. Then reply with one line saying you are done.
""")
    print('packet in', out, f'({len(names)} tiles, {len(tg)} units)')

def poly_dist(p, line):
    best = 1e9
    for a, b in zip(line, line[1:]):
        ax, ay = a[0] * S.KMX, a[1] * S.KMY; bx, by = b[0] * S.KMX, b[1] * S.KMY; qx, qy = p[0] * S.KMX, p[1] * S.KMY
        dx, dy = bx - ax, by - ay; L = dx * dx + dy * dy; t = 0 if L == 0 else max(0, min(1, ((qx - ax) * dx + (qy - ay) * dy) / L))
        best = min(best, math.hypot(qx - ax - t * dx, qy - ay - t * dy))
    return best
def compare(folder, n, answers, which='night'):
    s, d, date, m, g, px = setup(folder, n, which); A = json.load(open(answers)); tol = s.block; rows = []; back = []
    for u in targets(s, d):
        a = A['units'].get(u, {}); rec = d['cmp_pos'].get(u)
        if rec is None: rows.append((u, 'not on the table at this time in the record', None)); continue
        if not a.get('found') or not a.get('at'):
            rows.append((u, f"NOT FOUND by the reader ({a.get('note', '')})", None)); back.append(u); continue
        dist = S.km(rec, a['at']); ok = dist <= tol
        rows.append((u, f"record {list(rec)}  reader {a['at']}  {dist:.0f} km  {'ok' if ok else 'DIFFERS'}{'  note: ' + a['note'] if a.get('note') else ''}", dist))
        if not ok: back.append(u)
    b = s.box; inbox = lambda p: b[0] < p[0] < b[1] and b[2] < p[1] < b[3]
    line_bad = []; worst = 0.0
    if len(A.get('line', [])) >= 4:
        dense = []
        for p, q in zip(d['cmp_line'], d['cmp_line'][1:]):
            k = max(1, int(S.km(p, q) / 3)); dense += [(p[0] + (q[0] - p[0]) * i / k, p[1] + (q[1] - p[1]) * i / k) for i in range(k)]
        for p in dense:
            if not inbox(p): continue
            dd = poly_dist(p, A['line']); worst = max(worst, dd)
            if dd > tol: line_bad.append((round(p[0], 2), round(p[1], 2), round(dd)))
    else: line_bad = [('no line from the reader', '', '')]
    passed = not back and not line_bad
    print(f"Day {d['n']}  {d['which']} table  blind read against {m['label']}")
    for u, t, _ in rows: print(f"  {u:6s} {s.units[u]['label']:18s} {t}")
    print(f"  line: farthest point {worst:.0f} km from the reader's line; {len(line_bad)} sample points over {tol:.0f} km" + (f", worst near {max(line_bad, key=lambda x: x[2] if isinstance(x[2], int) else 0)[:2]}" if line_bad and isinstance(line_bad[0][2], int) else ''))
    print('PASSED' if passed else 'GOES BACK to the Campaign Series chat with both readings')
    vdir = os.path.join(s.folder, 'verify'); os.makedirs(vdir, exist_ok=True)
    json.dump({'day': d['n'], 'date': date, 'map': m['label'], 'part': 'blind second read', 'table': d['which'], 'passed': passed, 'toleranceKm': tol,
               'units': [{'unit': u, 'result': t, 'km': None if k is None else round(k, 1)} for u, t, k in rows],
               'line': {'worstKm': round(worst, 1), 'over': line_bad[:40]}, 'readerNotes': {'line': A.get('lineNote', '')}, 'sentBack': back},
              open(os.path.join(vdir, f"day-{int(d['n']):02d}-blind-{d['which']}.json"), 'w'), indent=1)
    return passed
if __name__ == '__main__':
    cmd = sys.argv[1]
    if cmd == 'packet': packet(*sys.argv[2:6])
    elif cmd == 'compare': sys.exit(0 if compare(*sys.argv[2:6]) else 1)
    else: raise SystemExit(__doc__)
