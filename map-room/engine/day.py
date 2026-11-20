"""The Map Room: one day's table. Shared by scene.py (renders), clip.py (the compositor), check_record.py and the tools.
A Day reads a day record's mapRoom block, its series framing for the day's view, the fixed camera and the clip template,
and works out where everything goes on the table and on screen, and when each move happens."""
import json, math, os, hashlib
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, '..')
TPL = json.load(open(os.path.join(HERE, 'template.json')))
CAM = json.load(open(os.path.join(HERE, 'view.json')))          # the fixed camera, unpadded frame
LIB = json.load(open(os.path.join(ROOT, 'kit', 'silhouettes', 'library.json')))
TW, TH = 14.0, 14.4          # table map size in table units (scene.py)
BS, BH = 1.35, 0.36          # block size and height
RAKE_GAP = 0.12              # rake head to block face
W, H = TPL['frame']
ALLIED = {'us', 'britain', 'soviet'}
B = TPL['beats']

def table_file(campaign, view=None, test=False):
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
def rake_angle(direction):
    """the rake comes from behind the move: its pole points opposite to the direction of travel; nearest of 8 renders"""
    a = math.degrees(math.atan2(-direction[1], -direction[0])) % 360
    return min(RAKE_ANGLES, key=lambda r: min(abs(r - a), 360 - abs(r - a)))

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
        return None if p['move'] == 'arrive' else self.xy(p['from'])
    def rest_to(self, p):
        if p['move'] == 'surrender': return None
        if p['move'] in ('advance', 'fall_back', 'arrive'): return self.snap_to(p)
        return self.xy(p['from'])
    def snap_to(self, p):
        """with contact, the mover stops touching the other block along the main direction of travel"""
        to = self.xy(p['to'])
        if not p.get('contact'): return to
        q = self.by_id[p['contact']]; tq = self.rest_to(q) if q['id'] != p['id'] else None
        tq = tq or self.xy(q['from']); fr = self.rest_from(p) or to
        d = (to[0] - fr[0], to[1] - fr[1])
        if abs(d[0]) >= abs(d[1]): return (tq[0] - math.copysign(BS, d[0] or 1), to[1])
        return (to[0], tq[1] - math.copysign(BS, d[1] or 1))
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
    def surrender_end(self, p):
        """a surrendered block is pushed back off the table toward its own rear (Allied west, German east)"""
        fr = self.rest_from(p); step = (-1, 0) if self.allied(p) else (1, 0); pos = fr
        for _ in range(400):
            pos = (pos[0] + step[0] * 0.1, pos[1]); x0, y0, x1, y1 = block_box(pos, 1.0)
            if x1 < 0 or x0 > W: break
        return (pos[0] + step[0] * 0.4, pos[1])

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
            if mv in ('advance', 'fall_back', 'arrive', 'surrender'):
                if mv == 'arrive': a, b = self.arrive_start(p), self.snap_to(p)
                elif mv == 'surrender': a, b = self.rest_from(p), self.surrender_end(p)
                else: a, b = self.rest_from(p), self.snap_to(p)
                s.update(a=a, b=b, rake=rake_angle(unit((b[0] - a[0], b[1] - a[1]))),
                         t_move=t + B['rake_enter'], t_end=t + B['rake_enter'] + B['rake_move'],
                         t_out=t + B['rake_enter'] + B['rake_move'] + B['rake_hold'],
                         t_done=t + B['rake_enter'] + B['rake_move'] + B['rake_hold'] + B['rake_exit'])
                self.events += [(t, 'rake_in', 1.0), (s['t_move'] - 0.01, 'tap', 1.0), (s['t_move'], 'push', B['rake_move']),
                                (s['t_out'], 'rake_out', 1.0)]
                if p.get('contact'): self.events.append((s['t_end'] - 0.02, 'knock', 0.8))
                t += B['push_gap']
            elif mv == 'air_mission':
                a = self.rest_from(p); b = self.xy(p['target'])
                s.update(a=a, b=b, t_move=t, t_end=t + B['air_out'], t_back=t + B['air_out'] + B['air_dwell'],
                         t_done=t + B['air_out'] + B['air_dwell'] + B['air_back'])
                self.events += [(t, 'glide', B['air_out']), (s['t_back'], 'glide', B['air_back'])]
                t = s['t_done'] + B['mark_gap']
            elif mv in ('cut_off', 'grounded'):
                dur = B['ring'] if mv == 'cut_off' else B['grounded']
                s.update(t_done=t + dur); self.events.append((t, 'pencil', dur)); t += dur + B['mark_gap']
            self.slots.append(s)
        self.t_moves_end = t if movers else self.t_table + 0.6
        self.t_wipe = self.t_moves_end
        self.t_draw = self.t_wipe + B['wipe']
        self.t_shade = self.t_draw + B['draw'] * 0.6
        self.t_tonight = self.t_draw + B['draw'] + B['tonight_after_draw']
        self.T = self.t_draw + B['draw'] + B['end_hold']
        self.events += [(self.t_wipe, 'wipe', B['wipe']), (self.t_draw, 'pencil', B['draw'])]
    def slot(self, pid): return next((s for s in self.slots if s['id'] == pid), None)

    def pos(self, p, t):
        """where block p sits at time t (table units), or None if it is off the table"""
        s = self.slot(p['id']); mv = p['move']
        if s is None or mv in ('hold', 'cut_off', 'grounded'): return self.rest_from(p)
        if mv == 'air_mission':
            a, b = s['a'], s['b']
            if t < s['t_move']: return a
            if t < s['t_end']: k = ease((t - s['t_move']) / B['air_out'])
            elif t < s['t_back']: k = 1.0
            else: k = 1 - ease((t - s['t_back']) / B['air_back'])
            return (a[0] + (b[0] - a[0]) * k, a[1] + (b[1] - a[1]) * k)
        a, b = s['a'], s['b']
        if mv == 'arrive' and t < s['t_move']: return a
        k = ease((t - s['t_move']) / B['rake_move'])
        return (a[0] + (b[0] - a[0]) * k, a[1] + (b[1] - a[1]) * k)
    def rake(self, t):
        """(head position, angle, the piece it pushes) at time t, or None"""
        for s in self.slots:
            if 'rake' not in s or not (s['t0'] <= t < s['t_done']): continue
            p = self.by_id[s['id']]; ang = math.radians(s['rake'])
            back = (math.cos(ang), math.sin(ang))                      # from the block toward the hand
            bp = self.pos(p, t); off = BS / 2 + RAKE_GAP
            # the head sits against the block's back face; a diagonal push meets the corner, so step back a little more
            off *= 1.0 / max(abs(back[0]), abs(back[1]))
            head = (bp[0] + back[0] * off, bp[1] + back[1] * off)
            if t < s['t_move']: f = 9.0 * (1 - ease((t - s['t0']) / B['rake_enter']))
            elif t < s['t_out']: f = 0.0
            else: f = 9.0 * ease((t - s['t_out']) / B['rake_exit'])
            return (head[0] + back[0] * f, head[1] + back[1] * f), s['rake'], s['id']
        return None
