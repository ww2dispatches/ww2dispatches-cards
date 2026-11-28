"""The Map Room, format 2 (FORMAT.md): a series of days. Reads series.json, units.json and the day records, carries every
unit and the front line forward from day to day, spaces the blocks, picks each day's focus, and compiles a day into what
the table renderer and the zoom compositor need.
A series folder holds day-NN.json files; each names its campaign, whose settings live in map-room/series/<campaign>/."""
import os, sys, json, glob, math, hashlib
os.environ.setdefault('MAPROOM_BH', '0.14'); os.environ.setdefault('MAPROOM_TW', '21'); os.environ.setdefault('MAPROOM_TH', '29')
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import day as D
KMX, KMY = 71.5, 110.6                         # km per degree at 50 N
NUDGE_KM = 5.0                                 # how far spacing may move a block from its true place
def km(a, b): return math.hypot((a[0] - b[0]) * KMX, (a[1] - b[1]) * KMY)
def cheb(a, b): return max(abs(a[0] - b[0]) * KMX, abs(a[1] - b[1]) * KMY)

class Series:
    def __init__(self, folder):
        self.folder = os.path.abspath(folder)
        self.files = sorted(glob.glob(os.path.join(self.folder, 'day-*.json')))
        if not self.files: raise SystemExit(f'{folder}: no day-NN.json files')
        self.recs = [json.load(open(f)) for f in self.files]
        self.campaign = self.recs[0].get('campaign'); self.cdir = os.path.join(HERE, '..', 'series', str(self.campaign))
        self.cfg = json.load(open(os.path.join(self.cdir, 'series.json')))
        up = os.path.join(self.folder, 'units.json')                 # a test series may carry its own roster
        self.units = {u['id']: u for u in json.load(open(up if os.path.exists(up) else os.path.join(self.cdir, 'units.json')))['units']}
        self.block = float(self.cfg.get('blockKm', 10)); self.sep = self.block * 1.04
        c = self.cfg['balcony']['center']; w = self.cfg['balcony']['widthKm']; h = w * D.H / D.W
        self.box = (c[0] - 0.54 * w / KMX, c[0] + 0.54 * w / KMX, c[1] - h / 2 / KMY, c[1] + h / 2 / KMY)   # ground the balcony sees
        self.errors = {}; self.days = []; self._pk = []; self._carry()

    def err(self, i, msg): self.errors.setdefault(i, []).append(msg)
    def allied(self, uid): return self.units[uid]['nation'] in D.ALLIED
    def rear(self, uid):
        """the side's rear edge for a unit: series.json `rear` by nation ("germany") or by side ("allied", "axis"),
        else west for the Allies and east for the Axis"""
        r = self.cfg.get('rear', {}); nat = self.units[uid]['nation']; side = 'allied' if self.allied(uid) else 'axis'
        return r.get(nat) or r.get(side) or D.REAR[side]

    # ---------- the front ----------
    def german_side(self, line, ll):
        """inside the polygon made by the line (north to south, German ground on the left) closed through the east"""
        P = [tuple(p) for p in line] + [(14.0, line[-1][1] - 0.5), (14.0, line[0][1] + 0.5)]
        x, y = ll; inside = False
        for (x1, y1), (x2, y2) in zip(P, P[1:] + P[:1]):
            if (y1 > y) != (y2 > y) and x < x1 + (y - y1) * (x2 - x1) / (y2 - y1): inside = not inside
        return inside
    def right_side(self, line, uid, ll):
        g = self.german_side(line, ll)
        for pk in self._pk:                                  # a pocket is ground held inside the other side's area
            R = [tuple(p) for p in pk['ring']]; x, y = ll; ins = False
            for (x1, y1), (x2, y2) in zip(R, R[1:] + R[:1]):
                if (y1 > y) != (y2 > y) and x < x1 + (y - y1) * (x2 - x1) / (y2 - y1): ins = not ins
            if ins: g = pk.get('side') != 'allied'
        return g != self.allied(uid)

    # ---------- spacing ----------
    def space(self, true, pinned, line):
        """nudge blocks apart so none overlap; pinned blocks (already shown standing there) stay put where they can"""
        P = {u: list(pinned.get(u, true[u])) for u in true}; ids = sorted(P)
        for _ in range(200):
            moved = False
            for i, a in enumerate(ids):
                for b in ids[i + 1:]:
                    dx = (P[a][0] - P[b][0]) * KMX; dy = (P[a][1] - P[b][1]) * KMY
                    if max(abs(dx), abs(dy)) >= self.sep: continue
                    moved = True; ax = 0 if abs(dx) >= abs(dy) else 1; d = (dx, dy)[ax]; need = self.sep - abs(d) + 0.02
                    sgn = 1 if d >= 0 else -1; wa, wb = (0.0 if a in pinned else 1.0), (0.0 if b in pinned else 1.0)
                    if wa + wb == 0: wa = wb = 1.0
                    for u, wgt, s in ((a, wa, sgn), (b, wb, -sgn)):
                        step = need * wgt / (wa + wb) * s / (KMX, KMY)[ax]; q = list(P[u]); q[ax] += step
                        if line is None or self.right_side(line, u, q) or not self.right_side(line, u, P[u]): P[u] = q
            if not moved: break
        return {u: (round(P[u][0], 4), round(P[u][1], 4)) for u in P}

    # ---------- carrying the table from day to day ----------
    def _carry(self):
        true = {}; shown = {}; line = None; pockets = []
        for i, rec in enumerate(self.recs):
            mr = rec.get('mapRoom') or {}; d = {'rec': rec, 'mr': mr, 'file': self.files[i], 'n': rec.get('day', i + 1)}
            if i == 0:
                line = mr.get('lineStart'); pockets = mr.get('pocketsStart', [])
                if not line: self.err(i, 'day 1 needs lineStart, the front before the battle')
            d['lineAM'] = line or mr.get('line') or []
            def known(uid, what):
                if uid not in self.units: self.err(i, f'{what}: unit "{uid}" is not on the roster (units.json)'); return False
                return True
            for s in mr.get('set', []):
                if not known(s.get('unit'), 'set'): continue
                if s['unit'] in true: self.err(i, f"set: {s['unit']} is already on the table; use a move or a shift")
                true[s['unit']] = tuple(s['at'])
            for s in mr.get('shifts', []):
                u = s.get('unit')
                if not known(u, 'shift'): continue
                if u not in true: self.err(i, f'shift: {u} is not on the table'); continue
                dist = km(true[u], s['to'])
                if dist > 15: self.err(i, f'shift: {u} goes {dist:.0f} km; over 15 km must be a move shown on some day')
                true[u] = tuple(s['to']); shown.pop(u, None)
            am_true = dict(true); d['pocketsAM'] = pockets; d['pockets'] = mr.get('pockets', []); self._pk = pockets
            am = self.space(am_true, {u: shown[u] for u in shown if u in am_true}, d['lineAM'] or None)
            pm_true = dict(am_true); movers = []; gone = []
            for m in sorted(mr.get('moves', []), key=lambda m: m.get('order', 0)):
                u = m.get('unit')
                if not known(u, 'move'): continue
                mv = m.get('move')
                if mv == 'air_mission':                 # aircraft are on the table only for their mission
                    d.setdefault('air', []).append(m); continue
                if mv == 'arrive':
                    if u in am_true: self.err(i, f'arrive: {u} is already on the table')
                    pm_true[u] = tuple(m['to'])
                elif u not in am_true: self.err(i, f'{mv}: {u} is not on the table (set it on day 1 or let it arrive)'); continue
                elif mv in ('advance', 'fall_back'): pm_true[u] = tuple(m['to'])
                elif mv == 'leave': gone.append(u)
                movers.append(u)
                for dv in m.get('drives', []):
                    if known(dv.get('unit'), 'drives') and dv['unit'] in am_true: pm_true[dv['unit']] = tuple(dv['to']); movers.append(dv['unit'])
                    else: self.err(i, f"drives: {dv.get('unit')} is not on the table")
            for u in gone: pm_true.pop(u, None)
            d['line'] = mr.get('line') or d['lineAM']
            pinned = {u: am[u] for u in pm_true if u in am and u not in movers}
            self._pk = d['pockets']; pm = self.space(pm_true, pinned, d['line'] or None)
            d.update(am_true=am_true, am=am, pm_true=pm_true, pm=pm, movers=movers)
            self.days.append(d); true = dict(pm_true); shown = dict(pm); line = d['line']; pockets = d['pockets']

    # ---------- the focus and the compiled day ----------
    def focus(self, d):
        """center of the day's moves, snapped to a coarse grid so days in the same place reuse their renders"""
        if d['mr'].get('focus'): c = d['mr']['focus']
        else:
            pts = [p for u in d['movers'] for p in (d['am'].get(u), d['pm'].get(u)) if p] + [tuple(m['target']) for m in d.get('air', []) if m.get('target')]
            if not pts: return None
            c = ((min(p[0] for p in pts) + max(p[0] for p in pts)) / 2, (min(p[1] for p in pts) + max(p[1] for p in pts)) / 2)
        return (round(c[0] / 0.05) * 0.05, round(c[1] / 0.05) * 0.05)
    def table(self, f):
        """the close framing: a block is D.BS table units and covers blockKm; the focus sits in the middle of the block zone"""
        bz = D.TPL['block_zone']; ax, ay = D.unproject((bz['left'] + bz['right']) / 2, (bz['top'] + bz['bottom']) / 2)
        KX = D.BS * KMX / self.block; KY = D.BS * KMY / self.block
        return {'LON0': round(f[0] - ax / KX, 4), 'LAT0': round(f[1] - ay / KY, 4), 'KX': round(KX, 3), 'KY': round(KY, 3)}
    def compile(self, i, work):
        """write what the renderers need for day i into <work>/days/<day>/: the close table, its record, and every block.
        A quiet day (no moves) still gets a close table, at the balcony's centre, shared by every quiet day: its render
        lights the drawn balcony frames, and the camera never comes down"""
        d = self.days[i]; mr = d['mr']; f = self.focus(d); quiet = f is None
        if quiet: c = self.cfg['balcony']['center']; f = (round(c[0] / 0.05) * 0.05, round(c[1] / 0.05) * 0.05)
        out = os.path.join(work, 'days', os.path.splitext(os.path.basename(d['file']))[0]); os.makedirs(out, exist_ok=True)
        def piece(u, **k):
            U = self.units[u]; p = {'id': u, 'nation': U['nation'], 'type': U['type'], 'label': U['label']}
            for x in ('heavy', 'variant'):
                if x in U: p[x] = U[x]
            p.update(k); return p
        allp = [piece(u, am=d['am'].get(u), pm=d['pm'].get(u)) for u in sorted(set(d['am']) | set(d['pm']))]
        key = None
        if i < int(self.cfg.get('keyDays', 3)):            # the key card, on the series' opening days only
            used = {u for x in self.days for u in x['pm']} | {m['unit'] for x in self.days for m in x.get('air', [])}
            year = str(self.recs[0].get('date', ''))[:4]
            key = {'nations': sorted({self.units[u]['nation'] for u in used}), 'air': any(x.get('air') for x in self.days),
                   'title': f"{self.cfg.get('name', '')} · {year}".strip(' ·'), 'blockKm': self.block}
        res = {'dir': out, 'focus': f, 'quiet': quiet, 'key': key, 'all': allp, 'lineAM': d['lineAM'], 'linePM': d['line'], 'vname': None, 'pocketsAM': d['pocketsAM'], 'pockets': d['pockets'], 'rec': d['rec'], 'mr': mr}
        json.dump({'all': allp, 'lineAM': d['lineAM'], 'linePM': d['line'], 'focus': f, 'quiet': quiet}, open(os.path.join(out, 'table-state.json'), 'w'))
        tj = self.table(f); tpath = os.path.join(out, 'table.json'); json.dump(tj, open(tpath, 'w'))
        t = D.Table(tpath); pieces = []; driven = {}
        for m in mr.get('moves', []):
            for dv in m.get('drives', []): driven[dv['unit']] = m['unit']
        order = {m['unit']: m for m in mr.get('moves', []) if m.get('move') != 'air_mission'}
        for p in allp:
            u = p['id']; a, b = p['am'], p['pm']
            vis = any(q and self._in_view(t, q) for q in (a, b))
            if not vis and u not in order and u not in driven: continue
            if u in order:
                m = order[u]; mv = {'leave': 'surrender'}.get(m['move'], m['move'])
                q = piece(u, move=mv, order=m['order'], sources=m.get('sources', []))
                if a: q['from'] = list(a)
                if mv in ('advance', 'fall_back', 'arrive'): q['to'] = list(b)
                if mv == 'surrender':                      # a leave fades where it stands: arrow first if withdrawn, X if destroyed or surrendered
                    q['fate'] = m.get('fate', 'withdrawn'); q['toward'] = m.get('toward') or self.rear(u)
                for x in ('enters', 'target'):
                    if x in m: q[x] = m[x]
            elif u in driven: q = piece(u, move='driven', by=driven[u], to=list(b)); q['from'] = list(a)
            else: q = piece(u, move='hold'); q['from'] = list(a)
            pieces.append(q)
        for m in d.get('air', []):
            q = piece(m['unit'], move='air_mission', order=m['order'], enters=m['enters'], target=list(m['target']), sources=m.get('sources', []))
            q['label'] = m.get('label') or q['label']               # an aircraft block says what it is doing
            pieces.append(q)
        rec = {k: d['rec'].get(k) for k in ('campaign', 'seriesName', 'day', 'days', 'date', 'subtitle')}
        rec['seriesName'] = rec.get('seriesName') or self.cfg.get('name'); rec['days'] = rec.get('days') or self.cfg.get('days')
        rec['mapRoom'] = {'asOf': mr.get('asOf', ''), 'lineAM': d['lineAM'], 'linePM': d['line'], 'lineSources': mr.get('lineSources', []), 'pieces': pieces}
        if mr.get('tonight'): rec['mapRoom']['tonight'] = mr['tonight']
        cj = os.path.join(out, os.path.basename(d['file'])); json.dump(rec, open(cj, 'w'), indent=1)
        res.update(table=tpath, close=cj, vname=f'f_{f[0]:.2f}_{f[1]:.2f}')
        return res
    def _in_view(self, t, ll):
        x0, y0, x1, y1 = D.block_box(t.XY(ll), 1.0); return x1 > -60 and x0 < D.W + 60 and y1 > -60 and y0 < D.H + 60
    def fits(self, d):
        """every place a mover stands today is inside the close view's block zone"""
        f = self.focus(d)
        if f is None: return True, []
        bad0 = []
        t = D.Table.__new__(D.Table); tj = self.table(f); t.LON0, t.LAT0, t.KX, t.KY = tj['LON0'], tj['LAT0'], tj['KX'], tj['KY']
        bz = D.TPL['block_zone']; bad = []
        for u in d['movers']:
            q = d['pm'].get(u)                                  # where it ends must be readable; it may start at the edge
            if q is None: continue
            x0, y0, x1, y1 = D.block_box(t.XY(q), 1.0)
            if x0 < bz['left'] or x1 > bz['right'] or y0 < bz['top'] or y1 > bz['bottom']: bad.append(u)
        for m in d.get('air', []):                              # the target must be well inside the close view
            if m.get('target') and not D.in_zone(t.XY(m['target'])): bad.append(m['unit'] + ' (its target)')
        return not bad, bad
