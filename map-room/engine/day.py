"""The Map Room: one day's table. Shared by scene.py (renders), clip.py (the compositor), check_record.py and the tools.
A Day reads a day record's mapRoom block, its series framing for the day's view, the fixed camera and the clip template,
and works out where everything goes on the table and on screen, and when each move happens."""
import json, math, os, hashlib
import routes as R
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, '..')
TPL = json.load(open(os.path.join(HERE, 'template.json')))
CAM = json.load(open(os.path.join(HERE, 'view.json')))          # the fixed camera, unpadded frame
LIB = json.load(open(os.path.join(ROOT, 'kit', 'silhouettes', 'library.json')))
TW, TH = float(os.environ.get('MAPROOM_TW', 14.0)), float(os.environ.get('MAPROOM_TH', 14.4))   # table map size in table units (scene.py); env: test knobs
BS, BH = float(os.environ.get("MAPROOM_BS", 1.35)), float(os.environ.get("MAPROOM_BH", 0.36))   # block size and height (MAPROOM_BS: a test knob for trying sizes)
RAKE_GAP = 0.12              # rake head to block face
W, H = TPL['frame']
ALLIED = {'us', 'britain', 'soviet'}
B = TPL['beats']

def table_file(campaign, view=None, test=False):
    if os.environ.get('MAPROOM_TABLE'): return os.environ['MAPROOM_TABLE']      # format 2: the day's focus framing, made by series.py
    # test records without a campaign use the 19 Nov sketch framing; with one, the series framings
    if test and not campaign: return os.path.join(ROOT, 'test', 'table.json')
    return os.path.join(ROOT, 'series', str(campaign), f'table-{view}.json' if view else 'table.json')

class Table:
    """A series framing: where the map sits on the table and how the table plane lands on screen."""
    def __init__(self, path):
        t = json.load(open(path)); self.path = path
        self.LON0, self.LAT0, self.KX, self.KY = t['LON0'], t['LAT0'], t['KX'], t['KY']
        self.lon_min, self.lon_max = self.LON0 - TW / 2 / self.KX, self.LON0 + TW / 2 / self.KX
        self.lat_min, self.lat_max = self.LAT0 - TH / 2 / self.KY, self.LAT0 + TH / 2 / self.KY
    def XY(self, ll): return ((ll[0] - self.LON0) * self.KX, (ll[1] - self.LAT0) * self.KY)
    def LL(self, xy): return (xy[0] / self.KX + self.LON0, xy[1] / self.KY + self.LAT0)
    def on_table(self, ll): return self.lon_min <= ll[0] <= self.lon_max and self.lat_min <= ll[1] <= self.lat_max

def proj(x, y, z=0.0):
    """table point to frame pixel and depth (unpadded camera)"""
    P = CAM['P']; v = [sum(P[r][c] * q for c, q in enumerate((x, y, z, 1.0))) for r in range(4)]
    return ((v[0] / v[3] + 1) / 2 * CAM['RX'], (1 - v[1] / v[3]) / 2 * CAM['RY']), v[3]
def homography():
    """3x3 matrix: table plane (x, y, z=0) to frame pixels"""
    P = CAM['P']; RX, RY = CAM['RX'], CAM['RY']
    Pm = [[P[0][0], P[0][1], P[0][3]], [P[1][0], P[1][1], P[1][3]], [P[3][0], P[3][1], P[3][3]]]
    S = [[RX / 2, 0, RX / 2], [0, -RY / 2, RY / 2], [0, 0, 1]]
    return [[sum(S[i][k] * Pm[k][j] for k in range(3)) for j in range(3)] for i in range(3)]
def unproject(px, py):
    """frame pixel to table plane point"""
    import numpy as np
    Hm = np.array(homography()); v = np.linalg.solve(Hm, [px, py, 1.0]); return (v[0] / v[2], v[1] / v[2])

def zoomed(pt, z=None, c=(560, 900)):
    z = TPL['push_in'] if z is None else z
    return (c[0] + z * (pt[0] - c[0]), c[1] + z * (pt[1] - c[1]))
def block_box(xy, z=None):
    xs, ys = [], []
    for dx in (-BS / 2, BS / 2):
        for dy in (-BS / 2, BS / 2):
            for dz in (0.0, BH):
                p = zoomed(proj(xy[0] + dx, xy[1] + dy, dz)[0], z); xs.append(p[0]); ys.append(p[1])
    return min(xs), min(ys), max(xs), max(ys)
def in_zone(xy, z=None):
    """the whole block sits inside the template's block zone (between the tab and the strip, clear of the right rail)"""
    x0, y0, x1, y1 = block_box(xy, z); bz = TPL['block_zone']
    return x0 >= bz['left'] and y0 >= bz['top'] and x1 <= bz['right'] and y1 <= bz['bottom']
def in_frame(xy, z=None, edge=8):
    x0, y0, x1, y1 = block_box(xy, z); return x0 >= edge and y0 >= edge and x1 <= W - edge and y1 <= H - edge

def rot_deg(pid):
    """small fixed twist per unit id, so blocks never sit in a perfect grid"""
    return int(hashlib.md5(str(pid).encode()).hexdigest(), 16) % 7 - 3
def sil_key(p):
    t = p['type']
    if t + '_shared' in LIB['library'] or t in LIB['library']['ship_shared']: return t
    return p['nation'] + ('_special' if p.get('heavy') else '') + (('_' + p['variant']) if p.get('variant') else '')
def face_id(p):
    """one face image per nation, type and label"""
    return hashlib.md5(f"{p['nation']}|{p['type']}|{sil_key(p)}|{p['label']}".encode()).hexdigest()[:10]
CELL = 1.0
def cell(xy):
    """sprites are rendered once per table cell and reused: a block slid less than a cell keeps the look"""
    return (round(xy[0] / CELL) * CELL, round(xy[1] / CELL) * CELL)

def ease(x): x = min(1, max(0, x)); return 4 * x ** 3 if x < 0.5 else 1 - (-2 * x + 2) ** 3 / 2
def unit(v):
    n = math.hypot(*v); return (v[0] / n, v[1] / n) if n > 1e-9 else (1.0, 0.0)
RAKE_ANGLES = list(range(0, 360, 45))
ROUTE_ANGLES = list(range(0, 360, 10))       # a rake following a curved route turns in finer steps
def rake_angle(direction, angles=RAKE_ANGLES):
    """the rake comes from behind the move: its pole points opposite to the direction of travel; nearest render"""
    a = math.degrees(math.atan2(-direction[1], -direction[0])) % 360
    return min(angles, key=lambda r: min(abs(r - a), 360 - abs(r - a)))
STEER = False                                # straight lines only (FORMAT.md, Brian 28 Nov 2026): routes.py is kept, unused
FATES = ('withdrawn', 'destroyed', 'surrendered'); STRUCK = ('destroyed', 'surrendered')   # a leave's fate; struck ones get the pencil X
COMPASS = {'north': (0, 1), 'northeast': (1, 1), 'east': (1, 0), 'southeast': (1, -1), 'south': (0, -1),
           'southwest': (-1, -1), 'west': (-1, 0), 'northwest': (-1, 1)}    # a withdrawal's `toward`
LEAVE_FADE = 1.5                             # seconds a leaving block takes to fade (Brian: time to see it)
EDGE_STEP = {'north': (0, 1), 'south': (0, -1), 'east': (1, 0), 'west': (-1, 0)}
REAR = {'allied': 'west', 'axis': 'east'}    # a leave heads for its own side's rear edge (series.json `rear` overrides)
def frame_px(X, Y):
    """table points (numpy arrays) to frame pixels, unzoomed camera"""
    Hm = homography(); den = Hm[2][0] * X + Hm[2][1] * Y + Hm[2][2]
    return (Hm[0][0] * X + Hm[0][1] * Y + Hm[0][2]) / den, (Hm[1][0] * X + Hm[1][1] * Y + Hm[1][2]) / den
def past_edge(edge, X, Y):
    """the block is wholly past this edge of the frame"""
    h = BS / 2 + 0.05
    if edge == 'west': return frame_px(X + h, Y)[0] < 0
    if edge == 'east': return frame_px(X - h, Y)[0] > W
    if edge == 'north': return frame_px(X, Y - h)[1] < 0
    return frame_px(X, Y + h)[1] > H
def allowed_fn(edge=None):
    """where a moving block may go: its centre inside the frame, or past the one edge a leave or arrive uses"""
    def ok(X, Y):
        px, py = frame_px(X, Y); inside = (px >= 0) & (px <= W) & (py >= 0) & (py <= H)
        if edge in ('west', 'east'): inside = inside | (((px < 0) if edge == 'west' else (px > W)) & (py >= 0) & (py <= H))
        if edge in ('north', 'south'): inside = inside | (((py < 0) if edge == 'north' else (py > H)) & (px >= 0) & (px <= W))
        return inside
    return ok
def route_cost(X, Y):
    """the price of each step: three times as dear under the tab or the strip, so a route keeps to the open table
    unless the way round is much longer"""
    import numpy as np
    bz = TPL['block_zone']; py = frame_px(X, Y)[1]
    return np.where((py >= bz['top']) & (py <= bz['bottom']), 1.0, 3.0)
def grid_bounds():
    import numpy as np
    c = np.array([unproject(x, y) for x, y in ((0, 0), (W, 0), (W, H), (0, H))])
    return (c[:, 0].min() - 2.5, c[:, 1].min() - 2.5, c[:, 0].max() + 2.5, c[:, 1].max() + 2.5)

class Day:
    def __init__(self, path, test=None):
        self.path = path; d = json.load(open(path)); self.rec = d
        self.mr = d['mapRoom'] if 'mapRoom' in d else None
        if self.mr is None: raise ValueError(f'{path}: no mapRoom block')
        self.test = (os.sep + 'map-room' + os.sep + 'test' + os.sep in os.path.abspath(path)) if test is None else test
        self.view = self.mr.get('view')
        self.table = Table(table_file(d.get('campaign'), self.view, self.test))
        self.main = Table(table_file(d.get('campaign'), None, self.test)) if self.view else self.table
        self.pieces = self.mr['pieces']; self.by_id = {p['id']: p for p in self.pieces}
        self.allied = lambda p: p['nation'] in ALLIED
        self._timeline()

    # ---------- where things are ----------
    def xy(self, ll): return self.table.XY(ll)
    def rest_from(self, p):
        return None if p['move'] in ('arrive', 'air_mission') else self.xy(p['from'])
    def rest_to(self, p):
        if p['move'] in ('surrender', 'air_mission'): return None
        if p['move'] == 'driven': return self.xy(p['to'])
        if p['move'] in ('advance', 'fall_back', 'arrive'): return self.snap_to(p)
        return self.xy(p['from'])
    def snap_to(self, p):
        """with contact, the mover stops touching the other block along the main direction of travel"""
        if p['move'] == 'air_mission': return self.park_spot(p)
        to = self.xy(p['to'])
        if not p.get('contact'): return to
        q = self.by_id[p['contact']]; tq = self.rest_to(q) if q['id'] != p['id'] else None
        tq = tq or self.xy(q['from']); fr = self.rest_from(p) or to
        d = (to[0] - fr[0], to[1] - fr[1])
        if abs(d[0]) >= abs(d[1]): return (tq[0] - math.copysign(BS, d[0] or 1), to[1])
        return (to[0], tq[1] - math.copysign(BS, d[1] or 1))
    def park_spot(self, p):
        """an aircraft block stops a short way in from the frame edge it enters by, level with its target where that is
        clear of every ground block, otherwise the nearest clear place along that edge"""
        if '_park' in p: return p['_park']
        T = self.xy(p['target']); step = {'north': (0, 1), 'south': (0, -1), 'east': (1, 0), 'west': (-1, 0)}[p['enters']]
        ground = [q for q in (self.rest_from(o) for o in self.pieces if o['move'] != 'air_mission') if q] + \
                 [q for q in (self.rest_to(o) for o in self.pieces if o['move'] != 'air_mission') if q]
        def clear(c): return all(max(abs(c[0] - g[0]), abs(c[1] - g[1])) >= BS * 1.08 for g in ground)
        cands = []
        for k in range(0, 60):
            off = (k + 1) // 2 * 0.2 * (1 if k % 2 else -1)                # 0, +0.2, -0.2, +0.4 ...
            c = (T[0] + abs(step[1]) * off, T[1] + abs(step[0]) * off)
            if not in_zone(c): continue
            while in_zone((c[0] + step[0] * 0.05, c[1] + step[1] * 0.05)): c = (c[0] + step[0] * 0.05, c[1] + step[1] * 0.05)
            if clear(c) and math.hypot(c[0] - T[0], c[1] - T[1]) > BS * 2.2: cands.append((k, c))
        def hidden(c, D, side):
            """how much of the track would lie under blocks other than the target's own"""
            p['_turnSide'] = side; tr = self.air_track(p, c, D); p.pop('_turnSide')
            pts = [q for q in tr if max(abs(q[0] - T[0]), abs(q[1] - T[1])) >= BS / 2 + 0.06]
            return sum(any(max(abs(q[0] - g[0]), abs(q[1] - g[1])) < BS / 2 + 0.06 for g in ground if max(abs(g[0] - T[0]), abs(g[1] - T[1])) > 0.05) for q in pts) / max(1, len(pts))
        opts = [(round(hidden(c, D, sd), 2), k, D, sd, c) for k, c in cands for D in (BS * 1.0, BS * 1.5, BS * 2.0) for sd in (1, -1)
                if in_zone(self.air_track(p, c, D)[41 + 14])]          # the turn stays in view
        best = None
        if opts:
            h, k, D, sd, best = min(opts, key=lambda o: (o[0], o[1], o[2]))
            p['_turnD'] = D; p['_turnSide'] = sd
        p['_park'] = best or c; return p['_park']
    def air_track(self, p, P=None, D=None):
        """the flight: straight from the block over the target (a drop zone is flown over, not around), on for D past it,
        a half circle turn, and back to the block beside the way in (table units)"""
        P = P or self.park_spot(p); T = self.xy(p['target']); D = D if D is not None else p.get('_turnD', BS * 1.2)
        d = (T[0] - P[0], T[1] - P[1]); L = math.hypot(*d); u = (d[0] / L, d[1] / L); n = (-u[1], u[0])
        side = p.get('_turnSide', 1); r = BS * 0.42; w = BS * 0.22; s0 = BS / 2 + 0.12
        def at(o, a, b): return (o[0] + u[0] * a + n[0] * b * side, o[1] + u[1] * a + n[1] * b * side)
        out = [at(P, s0 + (L + D - s0) * i / 40, w * (1 - i / 40)) for i in range(41)]           # aims at the target from just beside the block
        C = at(P, L + D, -r)
        turn = [(C[0] + u[0] * r * math.sin(a) + n[0] * side * r * math.cos(a), C[1] + u[1] * r * math.sin(a) + n[1] * side * r * math.cos(a)) for a in [math.pi * i / 30 for i in range(1, 30)]]
        back = [at(P, s0 + (L + D - s0) * (40 - i) / 40, -2 * r + (2 * r - w) * (i / 40) ** 2) for i in range(41)]
        return out + turn + back
    def rake_angles(self):
        out = {ph['angle'] for s in self.slots for ph in s.get('phases', [])}
        for s in self.slots:                       # a curved route uses every angle the rake passes through
            for ph in s.get('phases', []):
                if ph.get('path'): out |= {rake_angle(R.heading(ph['path'], i / 400), ROUTE_ANGLES) for i in range(401)}
        return sorted(out)
    def alpha(self, p, t):
        """how solid block p is at time t: a block struck off with the X fades with it"""
        s = self.slot(p['id'])
        if not s or s.get('how') not in ('strike', 'fade') or t < s['fade'][0]: return 1.0
        return max(0.0, 1 - ease((t - s['fade'][0]) / (s['fade'][1] - s['fade'][0])))
    def anchor(self, p):
        """where the block's sprite is rendered: its first resting place, in a table cell"""
        return cell(self.rest_from(p) or self.snap_to(p))
    def arrive_start(self, p):
        """an arriving block starts just past the edge of the frame it enters from"""
        to = self.snap_to(p); step = {'north': (0, 1), 'south': (0, -1), 'east': (1, 0), 'west': (-1, 0)}[p['enters']]
        pos = to
        for _ in range(400):
            pos = (pos[0] + step[0] * 0.1, pos[1] + step[1] * 0.1)
            x0, y0, x1, y1 = block_box(pos, 1.0)
            if x1 < 0 or x0 > W or y1 < 0 or y0 > H: break
        return (pos[0] + step[0] * 0.4, pos[1] + step[1] * 0.4)
    def rear(self, p):
        return p.get('rear') or REAR['allied' if self.allied(p) else 'axis']
    def surrender_end(self, p):
        """a block that leaves goes straight off the table toward its own rear edge (Allied west, German east)"""
        fr = self.rest_from(p); step = EDGE_STEP[self.rear(p)]; pos = fr
        for _ in range(400):
            pos = (pos[0] + step[0] * 0.1, pos[1] + step[1] * 0.1); x0, y0, x1, y1 = block_box(pos, 1.0)
            if x1 < 0 or x0 > W or y1 < 0 or y0 > H: break
        return (pos[0] + step[0] * 0.4, pos[1] + step[1] * 0.4)

    # ---------- routes (FORMAT.md, Routes) ----------
    def obstacles(self, p):
        """every ground block on the table while p moves: blocks that moved before it where they ended, the rest where
        they started; blocks p drives go with it, and blocks that arrive later or have left are off the table"""
        mine = {q['id'] for q in self.pieces if q['move'] == 'driven' and q.get('by') == p['id']}
        out = []
        for q in self.pieces:
            if q is p or q['move'] == 'air_mission' or q['id'] in mine: continue
            qo = self.by_id[q['by']].get('order') if q['move'] == 'driven' else q.get('order')
            if isinstance(qo, int) and qo < p['order']:
                if q['move'] == 'surrender': continue
                spot = self.rest_to(q)
            else:
                if q['move'] == 'arrive': continue
                spot = self.rest_from(q)
            if spot: out.append(spot)
        return out
    def route(self, p):
        """(a, b, path, how): the slide for a moving block. path is None for a clear straight slide (as before routes);
        otherwise the curve the rake steers it along. how: 'straight', 'route', 'strike' (a leave with no way out) or
        'blocked' (another move with no clear route: drawn straight, and the checker fails it)"""
        if '_route' not in p: p['_route'] = self._find_route(p)
        return p['_route']
    def _find_route(self, p):
        mv = p['move']; obs = self.obstacles(p)
        if mv == 'surrender' and not STEER:                # a leave never travels: it fades where it stands
            a = self.rest_from(p); return a, a, None, ('strike' if p.get('fate') in STRUCK else 'fade')
        if mv == 'arrive': a, b = self.arrive_start(p), self.snap_to(p)
        elif mv == 'surrender': a, b = self.rest_from(p), self.surrender_end(p)
        else: a, b = self.rest_from(p), self.snap_to(p)
        if R.straight_clear(a, b, obs, BS): return a, b, None, 'straight'
        if not STEER: return a, b, None, 'blocked'         # straight lines only: drawn straight, and the checker fails it
        bounds = grid_bounds()
        if mv == 'surrender':
            e = self.rear(p); path = R.find(a, obs, BS, allowed_fn(e), region=lambda X, Y: past_edge(e, X, Y), bounds=bounds, cost=route_cost)
            if path is None: return a, a, None, 'strike'
        elif mv == 'arrive':
            e = p['enters']; path = R.find(b, obs, BS, allowed_fn(e), region=lambda X, Y: past_edge(e, X, Y), bounds=bounds, cost=route_cost)
            if path is not None: path = path[::-1]
        else: path = R.find(a, obs, BS, allowed_fn(), goal=b, bounds=bounds, cost=route_cost)
        if path is None: return a, b, None, 'blocked'
        return path[0], path[-1], R.resample(path)[0], 'route'
    def along(self, s, k):
        """a fraction k of the way through slot s's slide"""
        if s.get('path'): return R.at(s['path'], k)
        a, b = s['a'], s['b']; return (a[0] + (b[0] - a[0]) * k, a[1] + (b[1] - a[1]) * k)
    def strike_x(self, p):
        """the two grease pencil strokes of the X across a block that has no way out (table units)"""
        c = self.rest_from(p); h = BS * 0.6
        return [((c[0] - h, c[1] + h), (c[0] + h, c[1] - h)), ((c[0] + h, c[1] + h), (c[0] - h, c[1] - h))]
    def withdraw_arrow(self, p):
        """the pencil arrow for a withdrawal (table units): a shaft about one block long from just off the block's back
        edge toward `toward` (else the side's rear), then the two strokes of a small head at its tip"""
        c = self.rest_from(p); d = COMPASS.get(p.get('toward')) or COMPASS[self.rear(p)]   # the checker refuses a bad toward
        n = math.hypot(*d); u = (d[0] / n, d[1] / n)
        e = (BS / 2) / max(abs(u[0]), abs(u[1])) + 0.12          # the block's edge in that direction, plus a gap
        a = (c[0] + u[0] * e, c[1] + u[1] * e); tip = (a[0] + u[0] * BS, a[1] + u[1] * BS)
        h = 0.32; out = [(a, tip)]
        for sgn in (1, -1):
            ang = math.atan2(-u[1], -u[0]) + sgn * math.radians(28)
            out.append((tip, (tip[0] + h * math.cos(ang), tip[1] + h * math.sin(ang))))
        return out
    def pencil_speed(self):
        """table units a second: the pace of the night line's grease pencil"""
        P = [self.xy(q) for q in (self.mr.get('linePM') or [])]
        L = sum(math.hypot(b[0] - a[0], b[1] - a[1]) for a, b in zip(P, P[1:]))
        return max(L, 4.0) / (0.75 * B['draw'])

    # ---------- when things happen ----------
    def _timeline(self):
        t = B['still'] + B['dissolve']
        self.t_table = t                           # the table is fully in view
        self.t_overview = None
        if self.view:
            self.t_overview = B['still']; t = B['still'] + B['dissolve'] + B['overview'] + B['push_view']; self.t_table = t
        self.events = []                            # for the sound: (time, kind, gain)
        self.slots = []
        movers = sorted([p for p in self.pieces if isinstance(p.get('order'), int)], key=lambda p: p['order'])
        for p in movers:
            mv = p['move']; s = {'id': p['id'], 'move': mv, 't0': t}
            if mv == 'air_mission':
                a, b = self.arrive_start(p), self.park_spot(p); c = a
                def phase(t, a, b, mode):
                    trav = unit((b[0] - a[0], b[1] - a[1]))
                    ang = rake_angle(trav) if mode == 'push' else rake_angle((-trav[0], -trav[1]))
                    ph = dict(a=a, b=b, mode=mode, angle=ang, t0=t, t_move=t + B['rake_enter'], t_end=t + B['rake_enter'] + B['rake_move'],
                              t_out=t + B['rake_enter'] + B['rake_move'] + B['rake_hold'])
                    ph['t_done'] = ph['t_out'] + B['rake_exit']
                    self.events.extend([(t, 'rake_in', 1.0), (ph['t_move'] - 0.01, 'tap', 1.0), (ph['t_move'], 'push', B['rake_move']), (ph['t_out'], 'rake_out', 1.0)])
                    return ph
                p1 = phase(t, a, b, 'push')
                tk0 = p1['t_out'] + B['air_pause']; tk1 = tk0 + B['air_track']
                self.events.append((tk0, 'dashes', B['air_track']))
                p2 = phase(tk1 + B['air_pause'], b, c, 'pull')
                s.update(phases=[p1, p2], track=(tk0, tk1), fade=(p2['t_end'], p2['t_end'] + B['air_fade']), t_done=p2['t_done'])
                self.events.append((p2['t_end'], 'wipe', B['air_fade']))
                t = p2['t_done'] + 0.2
            elif mv == 'surrender':
                # a leave never travels. Withdrawn: the red grease pencil draws a short arrow off the block's back edge
                # the way the unit went. Destroyed or surrendered: an X across the block. Then a slow fade, marks and all.
                how = self.route(p)[3]; geo = self.strike_x(p) if how == 'strike' else self.withdraw_arrow(p)
                sp = self.pencil_speed(); strokes = []; u = t
                for k, (a, b) in enumerate(geo):
                    dur = math.hypot(b[0] - a[0], b[1] - a[1]) / sp
                    dur = min(0.9, max(0.3, dur)) if how == 'strike' or k == 0 else min(0.35, max(0.12, dur))
                    strokes.append((a, b, u, u + dur)); self.events.append((u, 'pencil', dur)); u += dur + (0.12 if how == 'strike' else 0.04)
                f0 = strokes[-1][3] + 0.45                  # hold a beat so the mark registers
                s.update(how=how, strokes=strokes, fade=(f0, f0 + LEAVE_FADE), t_done=f0 + LEAVE_FADE)
                t = s['t_done'] + B['mark_gap']
            elif mv in ('advance', 'fall_back', 'arrive', 'surrender'):
                a, b, path, how = self.route(p)
                s.update(how=how, path=path)
                ang = rake_angle(unit((b[0] - a[0], b[1] - a[1]))) if path is None else rake_angle(R.heading(path, 0.0), ROUTE_ANGLES)
                s.update(a=a, b=b, rake=ang,
                         t_move=t + B['rake_enter'], t_end=t + B['rake_enter'] + B['rake_move'],
                         t_out=t + B['rake_enter'] + B['rake_move'] + B['rake_hold'],
                         t_done=t + B['rake_enter'] + B['rake_move'] + B['rake_hold'] + B['rake_exit'])
                s['phases'] = [dict(a=a, b=b, mode='push', angle=s['rake'], path=path, t0=t, t_move=s['t_move'], t_end=s['t_end'], t_out=s['t_out'], t_done=s['t_done'])]
                self.events += [(t, 'rake_in', 1.0), (s['t_move'] - 0.01, 'tap', 1.0), (s['t_move'], 'push', B['rake_move']),
                                (s['t_out'], 'rake_out', 1.0)]
                if p.get('contact'): self.events.append((s['t_end'] - 0.02, 'knock', 0.8))
                t += B['push_gap']
            elif mv in ('cut_off', 'grounded'):
                dur = B['ring'] if mv == 'cut_off' else B['grounded']
                s.update(t_done=t + dur); self.events.append((t, 'pencil', dur)); t += dur + B['mark_gap']
            self.slots.append(s)
        for p in self.pieces:
            if p['move'] == 'driven':
                s = self.slot(p['by']); sc = self.touch(p)
                tk = next(i / 200 for i in range(201) if ease(i / 200) >= sc - 1e-9)
                self.events.append((s['t_move'] + tk * B['rake_move'], 'knock', 0.8))
        self.t_moves_end = t if movers else self.t_table + 0.6
        self.t_wipe = self.t_moves_end
        self.t_draw = self.t_wipe + B['wipe']
        self.t_shade = self.t_draw + B['draw'] * 0.6
        self.t_tonight = self.t_draw + B['draw'] + B['tonight_after_draw']
        self.T = self.t_draw + B['draw'] + B['end_hold']
        self.events += [(self.t_wipe, 'wipe', B['wipe']), (self.t_draw, 'pencil', B['draw'])]
    def touch(self, p):
        """how far along its move (0 to 1) the attacker is when it meets the block it drives back"""
        s = self.slot(p['by']); q = self.xy(p['from'])
        for i in range(101):
            k = i / 100; m = self.along(s, k)
            if abs(m[0] - q[0]) < BS + 0.04 and abs(m[1] - q[1]) < BS + 0.04: return k
        return 1.0
    def slot(self, pid): return next((s for s in self.slots if s['id'] == pid), None)

    def pos(self, p, t):
        """where block p sits at time t (table units), or None if it is off the table"""
        s = self.slot(p['id']); mv = p['move']
        if mv == 'driven':
            # driven back: an attacker's block meets this one and carries it off; it moves only once they touch
            s = self.slot(p['by']); a, b = self.xy(p['from']), self.xy(p['to'])
            k = ease((t - s['t_move']) / B['rake_move']); sc = self.touch(p)
            if k <= sc: return a
            f = (k - sc) / max(1 - sc, 1e-6); return (a[0] + (b[0] - a[0]) * f, a[1] + (b[1] - a[1]) * f)
        if s is None or mv in ('hold', 'cut_off', 'grounded'): return self.rest_from(p)
        if mv == 'air_mission':
            p1, p2 = s['phases']
            if t < p1['t_move']: return p1['a']
            if t < p1['t_end']: k = ease((t - p1['t_move']) / B['rake_move']); a, b = p1['a'], p1['b']
            elif t < p2['t_move']: return p1['b']
            elif t < p2['t_end']: k = ease((t - p2['t_move']) / B['rake_move']); a, b = p2['a'], p2['b']
            else: return None
            return (a[0] + (b[0] - a[0]) * k, a[1] + (b[1] - a[1]) * k)
        if s.get('how') in ('strike', 'fade'): return self.rest_from(p) if t < s['fade'][1] else None
        if mv == 'arrive' and t < s['t_move']: return s['a']
        return self.along(s, ease((t - s['t_move']) / B['rake_move']))
    def rake(self, t):
        """(head position, angle, the piece it moves, push or pull) at time t, or None. A push comes from behind the move;
        a pull reaches from beyond the frame edge, hooks the block's far face and draws it back out"""
        for s in self.slots:
            for ph in s.get('phases', []):
                if not (ph['t0'] <= t < ph['t_done']): continue
                p = self.by_id[s['id']]; deg = ph['angle']
                if ph.get('path'):                                         # a curved route: the rake turns with the block
                    deg = rake_angle(R.heading(ph['path'], ease((t - ph['t_move']) / B['rake_move'])), ROUTE_ANGLES)
                ang = math.radians(deg)
                back = (math.cos(ang), math.sin(ang))                      # from the head toward the hand
                bp = self.pos(p, t) or ph['b']; off = BS / 2 + RAKE_GAP
                off *= 1.0 / max(abs(back[0]), abs(back[1]))               # a diagonal push meets the corner
                sgn = 1 if ph['mode'] == 'push' else -1
                head = (bp[0] + back[0] * off * sgn, bp[1] + back[1] * off * sgn)
                if t < ph['t_move']: f = 9.0 * (1 - ease((t - ph['t0']) / B['rake_enter']))
                elif t < ph['t_out']: f = 0.0
                else: f = 9.0 * ease((t - ph['t_out']) / B['rake_exit'])
                return (head[0] + back[0] * f, head[1] + back[1] * f), deg, s['id'], ph['mode']
        return None
