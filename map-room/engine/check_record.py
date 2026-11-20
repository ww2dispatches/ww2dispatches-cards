"""Check the mapRoom block of Campaign Series day records before a clip is made.
Usage: python3 map-room/engine/check_record.py <day-NN.json | series folder> [more ...]
Prints ERROR lines (must fix) and WARN lines (look again). Exit code 1 if any error.
The format is in map-room/FORMAT.md. Run it in the build sitting after writing each day's block.
Frame and table limits come from map-room/series/<campaign>/table.json (the record's campaign field)."""
import json, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__))
LIB = json.load(open(os.path.join(HERE, '..', 'kit', 'silhouettes', 'library.json')))

# ---------- table geometry ----------
# Each series has map-room/series/<campaign>/table.json saying where its map sits on the table (LON0, LAT0, KX, KY).
# The camera, block size and frame are fixed (scene.py, comp.py, view.json).
TW, TH = 14.0, 14.4                                # table map size in table units
BS, BH = 1.35, 0.36                                # block size and height
CAM = json.load(open(os.path.join(HERE, 'view.json')))
LON0 = LAT0 = KX = KY = LON_MIN = LON_MAX = LAT_MIN = LAT_MAX = None
def use_table(path):
    global LON0, LAT0, KX, KY, LON_MIN, LON_MAX, LAT_MIN, LAT_MAX
    t = json.load(open(path)); LON0, LAT0, KX, KY = t['LON0'], t['LAT0'], t['KX'], t['KY']
    LON_MIN, LON_MAX = LON0 - TW / 2 / KX, LON0 + TW / 2 / KX
    LAT_MIN, LAT_MAX = LAT0 - TH / 2 / KY, LAT0 + TH / 2 / KY
def XY(ll): return ((ll[0] - LON0) * KX, (ll[1] - LAT0) * KY)
def proj(x, y, z=0.0):
    P = CAM['P']; v = [sum(P[r][c] * q for c, q in enumerate((x, y, z, 1.0))) for r in range(4)]
    return ((v[0] / v[3] + 1) / 2 * CAM['RX'], (1 - v[1] / v[3]) / 2 * CAM['RY'])
def in_frame(ll):
    """the whole block sits in the template's block zone: between the tab and the strip, clear of the apps' right rail"""
    import day
    return day.in_zone(XY(ll))
def on_table(ll): return LON_MIN <= ll[0] <= LON_MAX and LAT_MIN <= ll[1] <= LAT_MAX

# ---------- rules ----------
MOVES = {'advance', 'fall_back', 'arrive', 'hold', 'cut_off', 'surrender', 'air_mission', 'grounded'}
MOVING = {'advance', 'fall_back', 'arrive', 'surrender', 'air_mission'}
NEEDS_TO = {'advance', 'fall_back', 'arrive'}
STATIC = {'hold', 'cut_off', 'grounded', 'surrender'}
SHIPS = set(LIB['library']['ship_shared'])
AIR = {'fighter', 'medium_bomber', 'heavy_bomber', 'transport'}
SHARED = {t[:-7] for t in LIB['library'] if t.endswith('_shared') and t != 'ship_shared'}   # artillery, airborne: one silhouette, nation colors
TYPES = {t for t in LIB['library'] if not t.endswith('_shared')} | SHARED | SHIPS
ALLIED = {'us', 'britain', 'soviet'}
EDGES = {'north', 'south', 'east', 'west'}
LABEL_MAX, SUB_MAX = 16, 38
ABBREV = re.compile(r"\b(Div|Inf|Infy|Arm|Armd|Abn|Pz|Bn|Regt|Rgt|Bde|Gp|Grp|Mech|Cav|Coy|Co|Cmd|CC[ABR]?)\b\.?", re.I)
SS = re.compile(r"\bSS\b|Waffen", re.I)
DASH = re.compile(r"[‐-―-]")
DEFAULT_TONIGHT = 'The line tonight. It moves again tomorrow.'

_FONT = None
def label_scale(label):
    """the face maker's own sizing (faces.py): the label shrinks until it fits 80% of the face"""
    global _FONT
    from PIL import ImageFont, Image, ImageDraw
    S = 800; t = label.upper(); s = int(S * 0.15); d = ImageDraw.Draw(Image.new('L', (8, 8)))
    fp = os.path.join(HERE, '..', 'fonts', 'oswald700.ttf')
    while s > 20 and d.textlength(t, font=ImageFont.truetype(fp, s)) > S * 0.80: s -= 2
    return s / S
def is_ll(v): return isinstance(v, list) and len(v) == 2 and all(isinstance(c, (int, float)) for c in v)
def too_precise(ll): return any(len(f'{c}'.split('.')[-1]) > 2 for c in ll if isinstance(c, float))
def near(a, b): return abs(a[0] - b[0]) < BS / KX * 0.98 and abs(a[1] - b[1]) < BS / KY * 0.98
def axis_ground(line):
    """German held ground: the area on the left of the line walked from its north end to its south end,
    closed through the east (Germany). The ends are carried straight north and south off the table."""
    pts = [list(p) for p in line]; far = 10
    pts = [[pts[0][0], LAT_MAX + far]] + pts + [[pts[-1][0], LAT_MIN - far]]
    return pts + [[LON_MAX + far, LAT_MIN - far], [LON_MAX + far, LAT_MAX + far]]
def inside(pt, poly):
    x, y = pt; c = False; j = len(poly) - 1
    for i in range(len(poly)):
        xi, yi = poly[i]; xj, yj = poly[j]
        if (yi > y) != (yj > y) and x < (xj - xi) * (y - yi) / (yj - yi) + xi: c = not c
        j = i
    return c

def check(path, test=False):
    E, Wn = [], []
    err = lambda m: E.append(m); warn = lambda m: Wn.append(m)
    d = json.load(open(path)); mr = d.get('mapRoom')
    if mr is None: return ['no mapRoom block'], []
    root = os.path.join(HERE, '..')
    view = mr.get('view')   # optional close view, e.g. "bastogne" uses series/<campaign>/table-bastogne.json
    name = f'table-{view}.json' if view else 'table.json'
    tbl = os.path.join(root, 'test', 'table.json') if (test and not d.get('campaign')) else os.path.join(root, 'series', str(d.get('campaign')), name)
    if not os.path.exists(tbl): return [f"no table framing {name} for campaign {d.get('campaign')!r} (map-room/series/<campaign>/)"], []
    use_table(tbl)
    def placeholder(s): return isinstance(s, str) and ('<' in s or 'EXAMPLE' in s)
    # day level
    sub = d.get('subtitle', '')
    if not sub: err('day subtitle missing (the clip strip uses it)')
    elif len(sub) > SUB_MAX: err(f'day subtitle is {len(sub)} characters, limit {SUB_MAX}')
    if not re.match(r'^\d{4} hrs, \d{1,2} [A-Z][a-z]{2} \d{4}$', mr.get('asOf', '')): err('asOf must read like "2400 hrs, 16 Dec 1944"')
    for k in ('asOf', 'tonight'):
        if isinstance(mr.get(k), str) and DASH.search(mr[k]): err(f'{k} contains a dash')
    if DASH.search(sub): err('subtitle contains a dash')
    # lines
    lines = {}
    for k in ('lineAM', 'linePM'):
        ln = mr.get(k)
        if not (isinstance(ln, list) and 3 <= len(ln) <= 24 and all(is_ll(p) for p in ln)): err(f'{k} must be 3 to 24 [lon, lat] points'); continue
        # the line runs from the north end of the front to the south end, around any bulge, German ground on its left;
        # it may run past the table edges (the drawing clips it), but some of it must be on this view's table
        if sum(on_table(p) for p in ln) < 2: err(f'{k} needs at least two points on this view\'s table')
        if any(abs(p[0] - LON0) * KX > TW * 2 or abs(p[1] - LAT0) * KY > TH * 2 for p in ln): err(f'{k} has points far off the table; stop the line a little past the edge')
        if any(too_precise(p) for p in ln): warn(f'{k}: use two decimals at most')
        lines[k] = ln
    ls = mr.get('lineSources', [])
    if len(ls) < 2: err('lineSources needs at least two sources')
    if not test and any(placeholder(s) for s in ls): err('lineSources still has a placeholder')
    pockets = {k: mr.get(k, []) for k in ('pocketsAM', 'pocketsPM')}
    for k, pl in pockets.items():
        for i, pk in enumerate(pl):
            if pk.get('side') not in ('allied', 'axis') or not (isinstance(pk.get('ring'), list) and len(pk['ring']) >= 3 and all(is_ll(p) for p in pk['ring'])):
                err(f'{k}[{i}] needs side (allied or axis) and a ring of 3 or more [lon, lat] points')
    def own_side(pt, allied, when):
        ln = lines.get('lineAM' if when == 'AM' else 'linePM')
        if not ln: return True
        axis = inside(pt, axis_ground(ln))
        for pk in pockets['pockets' + when]:
            if inside(pt, pk['ring']): axis = pk['side'] == 'axis'
        return axis != allied
    # pieces
    P = mr.get('pieces', [])
    if not 1 <= len(P) <= 8: err(f'{len(P)} pieces; the table shows 8 at most')
    elif len(P) < 4: warn(f'only {len(P)} pieces; six to eight reads best')
    ids = [p.get('id') for p in P]
    if len(set(ids)) != len(ids): err('piece ids must be unique')
    orders = []
    for p in P:
        pid = p.get('id', '?'); who = f"piece {pid} ({p.get('label', '')})"
        nat, typ, mv, lab = p.get('nation'), p.get('type'), p.get('move'), p.get('label', '')
        if nat not in LIB['colors'] or nat == 'face_ink': err(f'{who}: nation must be one of us, britain, germany, soviet, japan')
        if typ not in TYPES: err(f'{who}: type must be one of {sorted(TYPES)}')
        elif typ not in SHIPS and typ not in SHARED:
            key = nat + ('_special' if p.get('heavy') else '') + (('_' + p['variant']) if p.get('variant') else '')
            if key not in LIB['library'][typ]: err(f'{who}: no {typ} silhouette for {key} in the kit')
        # airborne rule (Brian, 20 Nov 2026): airborne divisions take the airborne block even on the ground;
        # German parachute divisions fighting as infantry keep the helmet unless the day is an actual drop
        if re.search(r'\bAirborne\b', lab + ' ' + p.get('name', '')) and nat != 'germany' and typ != 'airborne':
            err(f'{who}: airborne divisions use the airborne block, even when fighting on the ground')
        if nat == 'germany' and typ == 'airborne' and mv != 'arrive':
            warn(f'{who}: German parachute divisions fighting as infantry keep the infantry helmet; airborne only on an actual drop')
        if p.get('heavy') and not (nat == 'germany' and typ == 'armor'): err(f'{who}: heavy (the Tiger) is only for German armor')
        if p.get('heavy') and not p.get('heavyNamed'): err(f'{who}: heavy needs heavyNamed, the tank unit the day\'s story names')
        if mv not in MOVES: err(f'{who}: move must be one of {sorted(MOVES)}')
        # label
        if not lab: err(f'{who}: label missing')
        if len(lab) > LABEL_MAX: err(f'{who}: label is {len(lab)} characters, limit {LABEL_MAX} (shorten by dropping a word, never by abbreviating)')
        if ABBREV.search(lab): err(f'{who}: label uses a short form ({ABBREV.search(lab).group(0)}); write names out in full')
        if SS.search(lab) or SS.search(p.get('name', '')): err(f'{who}: no SS unit names on the table (use the parent army or corps)')
        if DASH.search(lab): err(f'{who}: label contains a dash')
        elif lab and label_scale(lab) < 0.085: err(f'{who}: label is too wide to read on the block (letters shrink to {label_scale(lab):.3f} of the face); drop a word')
        if p.get('name') and p['name'] == lab: warn(f'{who}: name only needed when the label had to be shortened')
        # positions
        fr, to = p.get('from'), p.get('to')
        if mv == 'arrive':
            if fr is not None: err(f'{who}: arrive has no from; give enters (north, south, east or west) and to')
            if p.get('enters') not in EDGES: err(f'{who}: arrive needs enters: north, south, east or west')
        elif not is_ll(fr): err(f'{who}: from must be [lon, lat]')
        if mv in NEEDS_TO and not is_ll(to): err(f'{who}: {mv} needs to [lon, lat]')
        if mv in STATIC and to is not None: err(f'{who}: {mv} stays put, so no to')
        if mv == 'air_mission':
            if typ not in AIR: err(f'{who}: air_mission is for aircraft')
            if not is_ll(p.get('target')): err(f'{who}: air_mission needs target [lon, lat], the place hit')
        if mv == 'grounded' and typ not in AIR: err(f'{who}: grounded is for aircraft')
        if typ in AIR and mv not in ('air_mission', 'grounded', 'hold', 'arrive'): warn(f'{who}: aircraft usually take air_mission, grounded or hold')
        for nm, ll in (('from', fr), ('to', to), ('target', p.get('target'))):
            if is_ll(ll):
                if not on_table(ll): err(f'{who}: {nm} {ll} is off the table map')
                elif nm != 'target' and not in_frame(ll): err(f'{who}: {nm} {ll} puts the block outside the safe area (partly off screen, or under the tab, the strip or the apps\' buttons)')
                if too_precise(ll): warn(f'{who}: {nm}: use two decimals at most (positions are approximate)')
        if is_ll(fr) and is_ll(to) and fr == to: err(f'{who}: from and to are the same; use hold')
        if p.get('contact') is not None:
            if mv not in ('advance', 'fall_back'): err(f'{who}: contact only goes with advance or fall_back')
            elif p['contact'] not in ids or p['contact'] == pid: err(f'{who}: contact must name another piece id')
        # side of the line
        allied = nat in ALLIED
        if typ not in AIR and mv not in ('cut_off', 'surrender'):
            if is_ll(fr) and not own_side(fr, allied, 'AM'): err(f'{who}: starts on the wrong side of the morning line')
            end = to if is_ll(to) else fr
            if is_ll(end) and not own_side(end, allied, 'PM'): err(f'{who}: ends on the wrong side of the night line')
        # sources and order
        src = p.get('sources', [])
        if mv in MOVING or mv in ('cut_off', 'grounded'):
            if len(src) < 2: err(f'{who}: {mv} needs at least two sources')
            if not isinstance(p.get('order'), int): err(f'{who}: {mv} needs order (1, 2, 3 ...), the sequence on the clip')
            else: orders.append(p['order'])
        elif p.get('order') is not None: warn(f'{who}: hold pieces take no order')
        if not test and any(placeholder(s) for s in src): err(f'{who}: sources still have a placeholder')
    if orders and sorted(orders) != list(range(1, len(orders) + 1)): err(f'order must run 1 to {len(orders)} with no gaps or repeats')
    if len(orders) > 4: warn(f'{len(orders)} moves; more than four makes a long clip')
    if not orders: warn('nothing moves today; check the story has a move (a quiet day can still shift one block)')
    # overlaps at start and end of day
    def rest(p, end):
        if end: return p.get('to') if is_ll(p.get('to')) else (p.get('from') if p.get('move') not in ('surrender',) else None)
        return p.get('from')
    for end in (False, True):
        pts = [(p['id'], rest(p, end)) for p in P if is_ll(rest(p, end))]
        for i in range(len(pts)):
            for j in range(i + 1, len(pts)):
                if near(pts[i][1], pts[j][1]):
                    pair = {pts[i][0], pts[j][0]}
                    if not any(p.get('contact') in pair and p['id'] in pair for p in P):
                        err(f"blocks {pts[i][0]} and {pts[j][0]} overlap at the {'end' if end else 'start'} of the day")
    return E, Wn

def main(args):
    files = []
    for a in args:
        files += sorted(os.path.join(a, f) for f in os.listdir(a) if re.match(r'day-\d+\.json$', f)) if os.path.isdir(a) else [a]
    bad = 0
    for f in files:
        test = os.sep + 'map-room' + os.sep + 'test' + os.sep in os.path.abspath(f)
        E, Wn = check(f, test)
        print(f"{'FAIL' if E else 'OK  '} {f}" + (' (test file: placeholders allowed)' if test else ''))
        for m in E: print('  ERROR ' + m)
        for m in Wn: print('  WARN  ' + m)
        bad += bool(E)
    print(f'{len(files) - bad} of {len(files)} records pass')
    return 1 if bad else 0
if __name__ == '__main__': sys.exit(main(sys.argv[1:]))
