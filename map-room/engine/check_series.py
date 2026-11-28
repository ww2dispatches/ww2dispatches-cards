"""The Map Room checker, format 2 (FORMAT.md, The fact check, part 1). Checks a whole series at once, because every day
depends on the day before: who each unit is, where it came from, how far it went, which side of the line it is on, the
line itself, the sources, and the table (overlaps, blocks passing through each other, one focus).
Usage: check_series.py <series folder>      Exit code 1 if any day has an error."""
import os, sys, re, json, datetime
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import series as S, day as D, faces
SHORT = re.compile(r'\b(Div|Inf|Pz|Abn|Armd|Arm|Bn|Regt|Rgt|Bde|CCA|CCB|CCR|Co|Btn)\b\.?', re.I)
TYPES = {'infantry', 'armor', 'artillery', 'airborne', 'fighter', 'medium_bomber', 'heavy_bomber', 'transport',
         'carrier', 'battleship', 'destroyer', 'submarine', 'landing_craft'}
AIR = {'fighter', 'medium_bomber', 'heavy_bomber', 'transport'}

def roster_errors(s):
    out = []
    for u in s.units.values():
        who = f"roster {u.get('id')} ({u.get('name', '?')})"
        for k in ('id', 'name', 'label', 'nation', 'type', 'parent', 'sources'):
            if not u.get(k): out.append(f'{who}: missing {k}')
        lab = u.get('label', '')
        if len(lab) > 16: out.append(f'{who}: label is {len(lab)} characters, limit 16 (drop a word, never abbreviate)')
        if SHORT.search(lab): out.append(f'{who}: label uses a short form; write the words out')
        if re.search(r'\bSS\b', lab): out.append(f'{who}: no SS unit names on the table (use the parent army or corps)')
        if '-' in lab or '–' in lab or '—' in lab: out.append(f'{who}: no dashes in labels')
        if u.get('type') not in TYPES: out.append(f"{who}: unknown type {u.get('type')}")
        else:
            try: faces.sil_file(u['type'], u['nation'], u.get('heavy', False), u.get('variant'))
            except Exception: out.append(f"{who}: no silhouette in the kit for {u.get('nation')} {u.get('type')}")
        if re.search(r'airborne', u.get('name', ''), re.I) and u.get('type') != 'airborne': out.append(f'{who}: airborne divisions take the airborne block')
    return out

def crosses(line):
    def ccw(a, b, c): return (c[1] - a[1]) * (b[0] - a[0]) - (b[1] - a[1]) * (c[0] - a[0])
    n = len(line)
    for i in range(n - 1):
        for j in range(i + 2, n - 1):
            a, b, c, d = line[i], line[i + 1], line[j], line[j + 1]
            if ccw(a, c, d) * ccw(b, c, d) < 0 and ccw(a, b, c) * ccw(a, b, d) < 0: return True
    return False

def check(s):
    box = s.box; maps = s.cfg.get('maps', {})
    def outside(p): return p[0] <= box[0] or p[0] >= box[1] or p[1] <= box[2] or p[1] >= box[3]
    for i, d in enumerate(s.days):
        mr, rec = d['mr'], d['rec']; E = lambda m: s.err(i, m)
        if not mr: E('no mapRoom block'); continue
        # Which map (FORMAT.md, 21 Nov 2026): the maps were drawn at noon, so a night table is normally read from the next
        # day's map; the day's own map is accepted where it already shows the night position. Day 1's set stays on its own map.
        date = rec.get('date'); daymap = maps.get(date, {}).get('label')
        try: nextmap = maps.get((datetime.date.fromisoformat(date) + datetime.timedelta(days=1)).isoformat(), {}).get('label')
        except (TypeError, ValueError): nextmap = None; E(f'date "{date}" is not YYYY-MM-DD')
        allowed = [m for m in (nextmap, daymap) if m]
        names = ' or '.join(f'"{m}"' for m in allowed)
        if not allowed: E(f'no situation map listed in series.json for {date} or the day after')
        elif mr.get('map') not in allowed: E(f'map must be the next day\'s situation map (or this day\'s): {names}')
        def sourced(what, src, two, own_only=False):
            src = src or []
            if own_only:
                if daymap and daymap not in src: E(f"{what}: sources must name the day's own situation map (Day 1 sets the table from it)")
            elif allowed and not any(m in src for m in allowed): E(f"{what}: sources must name the next day's situation map (or this day's): {names}")
            if two and len(src) < 2: E(f'{what}: needs a second source')
            if any('...' in x or 'TODO' in x.upper() for x in src): E(f'{what}: a source is still a placeholder')
        if not mr.get('asOf'): E('missing asOf')
        # the line
        ln = mr.get('line')
        if not ln: E('missing line, the front at the end of the day')
        else:
            sourced('line', mr.get('lineSources'), True)
            if len(ln) < 4: E('line: too few points')
            if not (outside(ln[0]) and outside(ln[-1])): E('line: must run from the north edge of the map to the south edge (both ends past the edge)')
            if ln[0][1] < ln[-1][1]: E('line: runs north to south, German ground on the left')
            if crosses(ln): E('line: crosses itself')
        if i == 0 and mr.get('lineStart'):                 # the front before the battle: Day 1's own map, two sources or more
            if not mr.get('lineStartSources'): E("lineStart: needs lineStartSources, two or more, one of them the day's own situation map")
            else: sourced('lineStart', mr.get('lineStartSources'), True, own_only=True)
        line = d['line']
        # moves
        mvs = mr.get('moves', []); orders = sorted(m.get('order', 0) for m in mvs)
        if orders != list(range(1, len(mvs) + 1)): E(f'moves: order must run 1 to {len(mvs)} with no gaps or repeats')
        if len(mvs) > 3: E(f'{len(mvs)} moves; three at most in a day')
        for m in mvs:
            u = m.get('unit'); who = f"move {u}"
            if u not in s.units: continue
            mv = m.get('move')
            if mv == 'grounded': E(f'{who}: grounded is not used (Brian, 21 Nov 2026); leave the aircraft off the table'); continue
            if mv not in ('advance', 'fall_back', 'arrive', 'leave', 'air_mission'): E(f'{who}: unknown move {mv}'); continue
            if mv == 'air_mission':
                if s.units[u]['type'] not in AIR: E(f'{who}: air_mission is for aircraft only')
                if not m.get('target'): E(f'{who}: needs target, the [lon, lat] of the drop zone or the place struck')
                if m.get('enters') not in ('north', 'south', 'east', 'west'): E(f'{who}: needs enters, the frame edge toward its bases')
                if m.get('drives'): E(f'{who}: aircraft do not drive blocks')
                lab = m.get('label', '')
                if not lab: E(f'{who}: needs label, what the block says the aircraft are doing (Supply Drop, Glider Drop, Air Strike)')
                elif len(lab) > 16 or SHORT.search(lab) or '-' in lab: E(f'{who}: label must be 16 characters at most, words written out, no dashes')
            elif s.units[u]['type'] in AIR: E(f'{who}: aircraft only fly air_mission (they are not kept on the table)')
            sourced(who, m.get('sources'), True)
            if mv in ('advance', 'fall_back'):
                if u in d['am_true'] and 'to' in m:
                    dist = S.km(d['am_true'][u], m['to'])
                    if dist > 40: E(f'{who}: {dist:.0f} km in a day; over 40 km is an error (check the positions, or split it across days)')
                    if dist < 2: E(f'{who}: barely moves ({dist:.1f} km); use a shift')
                else: E(f'{who}: needs to')
            if mv == 'arrive' and m.get('enters') not in ('north', 'south', 'east', 'west'): E(f'{who}: arrive needs enters (north, south, east or west)')
            if mv == 'leave' and not m.get('why'): E(f'{who}: leave needs why')
            if 'fate' in m:
                if mv != 'leave': E(f'{who}: fate belongs to a leave only')
                elif m['fate'] not in D.FATES: E(f"{who}: fate must be withdrawn, destroyed or surrendered (not {m['fate']})")
            if m.get('drives') and mv != 'advance': E(f'{who}: only an advance drives another block')
            for dv in m.get('drives', []):
                x = dv.get('unit')
                if x in s.units and u in s.units and s.allied(x) == s.allied(u): E(f'{who}: drives {x}, which is on its own side')
        for sh in mr.get('shifts', []): sourced(f"shift {sh.get('unit')}", sh.get('sources'), False)
        for st in mr.get('set', []):
            sourced(f"set {st.get('unit')}", st.get('sources'), False, own_only=(i == 0))
            if st.get('unit') in s.units and s.units[st['unit']]['type'] in AIR: E(f"set {st['unit']}: aircraft are not kept on the table; they appear only on their air_mission day")
        if i > 0 and mr.get('lineStart'): E('lineStart belongs to day 1 only')
        # sides, spacing, the table
        for when, true, shown, l, pk in (('morning', d['am_true'], d['am'], d['lineAM'], d['pocketsAM']), ('night', d['pm_true'], d['pm'], line, d['pockets'])):
            if not l: continue
            s._pk = pk
            for u, p in true.items():
                if s.units[u]['type'] in AIR: continue
                if not s.right_side(l, u, p): E(f"{u} ({s.units[u]['label']}): on the wrong side of the {when} line")
                elif not s.right_side(l, u, shown[u]): E(f"{u}: spacing would put it across the {when} line; that stretch is too crowded")
                if S.km(p, shown[u]) > S.NUDGE_KM + 0.5:
                    near = [v for v in true if v != u and S.cheb(true[v], p) < s.sep]
                    E(f"{u}: too crowded at {when} (it would sit {S.km(p, shown[u]):.0f} km from its true place; near {', '.join(near) or 'others'}). Show their corps as one block there")
            ids = sorted(shown)
            for a in ids:
                for b in ids[ids.index(a) + 1:]:
                    if S.cheb(shown[a], shown[b]) < s.block * 0.99: E(f'{a} and {b} overlap at {when}')
        # a driven block's end spot is clear of every ground block, even if the driven unit leaves later that day
        for m in sorted(mvs, key=lambda m: m.get('order', 0)):
            u = m.get('unit')
            for dv in m.get('drives', []):
                x = dv.get('unit'); spot = d['pm'].get(x) or (tuple(dv['to']) if dv.get('to') else None)
                if x not in s.units or not spot: continue
                later = {mm['unit'] for mm in mvs if mm.get('move') == 'leave' and mm.get('order', 0) > m.get('order', 0)}
                others = {v: p for v, p in d['pm'].items() if v != x}
                others.update({v: d['am'][v] for v in later if v in d['am'] and v != x})
                for v, p in others.items():
                    if s.units[v]['type'] in AIR: continue
                    if S.cheb(spot, p) < s.block * 0.99: E(f"drive {u}: pushes {x} onto {v}; move the driven spot, or let it leave first"); break
        # nothing passes through anything: every slide on the path the engine draws (routes included)
        if any(m.get('move') in ('advance', 'fall_back', 'arrive', 'leave') for m in mvs):
            errs, notes = drawn_moves(s, i)
            for e in errs: E(e)
            for n_ in notes: s.notes.setdefault(i, []).append(n_)
        ok, bad = s.fits(d)
        if not ok: E(f"the day's moves do not fit one focus ({', '.join(bad)} would be outside the close view); pick one story for the day")
        if not mvs and i > 0 and not mr.get('shifts') and line == d['lineAM']:
            s.notes.setdefault(i, []).append('nothing changes on the table today: a balcony only clip with the line unchanged; confirm the front really held still')

MOVE_NAME = {'advance': 'advance', 'fall_back': 'fall_back', 'arrive': 'arrive', 'surrender': 'leave'}

def drawn_moves(s, i):
    """(errors, notes): day i's slides tested on the path the engine draws (straight lines only, FORMAT.md). The day's
    close table is built as the renderer builds it (series.compile, then day.Day with that table), and every block's
    place is sampled through each advance, fall back and arrive: blocks that moved earlier are met where they now stand,
    and a block's own driven blocks go with it. A leave never travels, so it has nothing to test."""
    import tempfile
    errs, notes = [], []
    with tempfile.TemporaryDirectory() as tmp:
        res = s.compile(i, tmp); old = os.environ.get('MAPROOM_TABLE'); os.environ['MAPROOM_TABLE'] = res['table']
        try: d = D.Day(res['close'])
        finally:
            if old is None: os.environ.pop('MAPROOM_TABLE', None)
            else: os.environ['MAPROOM_TABLE'] = old
    ground = [p for p in d.pieces if p['type'] not in AIR]
    for p in ground:
        sl = d.slot(p['id']); mv = p['move']
        if sl is None or mv not in MOVE_NAME: continue
        who = f"{MOVE_NAME[mv]} {p['id']}"
        if sl.get('how') in ('strike', 'fade'): continue
        mine = {q['id'] for q in ground if q['move'] == 'driven' and q.get('by') == p['id']}
        for k in range(1, 80):                                      # the start may be off the frame, the end is its spot
            t = sl['t_move'] + (sl['t_end'] - sl['t_move']) * k / 80; a = d.pos(p, t)
            hit = next((q for q in ground if q is not p and q['id'] not in mine and (b := d.pos(q, t)) is not None
                        and max(abs(a[0] - b[0]), abs(a[1] - b[1])) < D.BS * 0.9), None)
            if hit:
                if mv == 'arrive': errs.append(f"{who}: passes through {hit['id']} on the way in; pick another enters edge, or check the positions")
                else: errs.append(f"{who}: passes through {hit['id']} on the way; list it under drives, or check the positions")
                break
    return errs, notes

if __name__ == '__main__':
    s = S.Series(sys.argv[1]); s.notes = {}; re_ = roster_errors(s); check(s)
    for e in re_: print('  ERROR', e)
    bad = len(re_) > 0
    for i, d in enumerate(s.days):
        errs = s.errors.get(i, []); name = os.path.basename(d['file'])
        print(f"{name}: {'OK' if not errs else str(len(errs)) + ' errors'}  ({len(d['pm'])} blocks, {len(d['mr'].get('moves', []))} moves)")
        for e in errs: print('  ERROR', e)
        for n_ in s.notes.get(i, []): print('  NOTE', n_)
        bad = bad or bool(errs)
    print('series passes' if not bad else 'series has errors; nothing is rendered until they are fixed')
    sys.exit(1 if bad else 0)
