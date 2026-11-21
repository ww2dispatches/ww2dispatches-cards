"""The Map Room zoom compositor, format 2: balcony, focus, balcony (FORMAT.md, The idea).
From the balcony the whole battle shows as small blocks; the camera comes down to the day's focus, where the rendered
table takes over (rake, readable labels), then goes back up for the new line.
The travelling camera is drawn here in 2D: the map is vectors (rivers, borders, roads, towns) projected per frame, so
line widths and town names keep their screen size and more towns appear as the camera comes down. The close view is
the table render; the two meet at the same camera position and cross fade.
Used by render_series.py."""
import sys, os, json, math, subprocess
import numpy as np, cv2
HERE = os.path.dirname(os.path.abspath(__file__)); ENG = HERE; sys.path.insert(0, ENG)
import series as S, day as D, clip as C, keycard as K
from PIL import Image, ImageDraw, ImageFont
W, H, FPS = D.W, D.H, 30
KMX, KMY = 71.5, 110.6                      # km per degree at 50 N
def ll2km(ll): return (ll[0] * KMX, ll[1] * KMY)
PAPER = np.array([226, 206, 160], np.float32) / 255
COL = {'river': (78, 104, 124), 'road': (150, 118, 78), 'border': (110, 70, 52), 'ink': (52, 42, 32), 'wax': (153, 23, 18)}
FONT = os.path.join(ENG, '..', 'fonts', 'special-elite.ttf')

class ZoomClip:
    def __init__(self, ser, res, work):
        """ser: the Series; res: what Series.compile returned for the day"""
        os.environ['MAPROOM_TABLE'] = res['table']; os.environ['MAPROOM_VNAME'] = res['vname']
        self.res = res; self.c = C.Clip(res['close'], work); self.d = d = self.c.d; t = d.table
        self.far = [p for p in res['all'] if p['id'] not in d.by_id]
        G = os.path.join(ser.cdir, 'geo')
        self.rivers = json.load(open(f'{G}/rivers.json'))['rivers']; self.roads = json.load(open(f'{G}/roads.json'))['roads']
        self.borders = json.load(open(f'{G}/borders.json'))['borders']; self.towns = json.load(open(f'{G}/towns.json'))['towns']
        self.faces = {}
        for p in d.pieces + self.far:
            fp = os.path.join(work, 'faces', f'face-{D.face_id(p)}.png')
            if not os.path.exists(fp):
                import faces; faces.face(p['nation'], p['type'], p['label'], fp)
            self.faces[p['id']] = cv2.imread(fp)[..., ::-1].astype(np.float32) / 255
        # close camera: km -> table -> frame
        self.A = np.array([[t.KX / KMX, 0, -t.KX * t.LON0], [0, t.KY / KMY, -t.KY * t.LAT0], [0, 0, 1]])
        self.Hs = np.array(D.homography())
        # light: what the lamp does to bare paper in the render, as a soft field over the frame
        L = cv2.GaussianBlur(self.c.plate, (0, 0), 45) / PAPER; self.L = np.clip(L, 0.05, 1.6).astype(np.float32)
        rng = np.random.default_rng(3); g = cv2.GaussianBlur(rng.standard_normal((H, W)).astype(np.float32), (0, 0), 1.2)
        self.grain = 1 + 0.018 * g[..., None] / g.std()
        # times
        d0 = d.t_table                                    # clip time when the close table starts
        self.quiet = res.get('quiet', False)
        self.t_bal = 1.5; self.t_push = 2.9; self.t_close = 4.6
        self.tau_end = d.t_draw + D.B['draw'] + 0.6
        self.t_pull = self.t_close + (self.tau_end - d0); self.t_up = self.t_pull + 1.6; self.T = self.t_up + 2.2
        self.shift = self.t_close - d0
        if self.quiet:                                    # balcony only: hold, wipe the morning line, draw the night line
            self.q_wipe = 3.3; self.q_draw = self.q_wipe + D.B['wipe']; self.q_end = self.q_draw + D.B['draw']
            self.T = self.q_end + D.B['end_hold']
        # balcony camera: the whole battle from nearly straight above
        cx, cy = ll2km(ser.cfg['balcony']['center']); w = float(ser.cfg['balcony']['widthKm']); h = w * H / W
        self.Q0 = np.array([[cx - w * 0.54, cy + h / 2], [cx + w * 0.54, cy + h / 2], [cx + w * 0.47, cy - h / 2], [cx - w * 0.47, cy - h / 2]])
        self.SCR = np.array([[0, 0], [W, 0], [W, H], [0, H]], np.float32)
        self._cache = {}
        # the key card: placed once, at the balcony, then carried by the camera with the table
        self.key = self.key_km = None
        if res.get('key'):
            k = res['key']; self.key = K.make(k['nations'], k['air'], k['title'], k['blockKm']); self._place_key()

    # ---------- cameras ----------
    def Hclose(self, tau):
        z = 1.0 + (D.TPL['push_in'] - 1) * min(1, max(0, (tau - self.d.t_table) / max(self.d.T - self.d.t_table, 1e-3)))
        Z = np.array([[z, 0, 560 - z * 560], [0, z, 900 - z * 900], [0, 0, 1]]); return Z @ self.Hs @ self.A
    def Hmix(self, k, tau):
        """camera between the balcony (k=0) and the close view (k=1): the ground it sees, blended"""
        Hc = self.Hclose(tau); Hi = np.linalg.inv(Hc)
        Q1 = np.array([(lambda v: v[:2] / v[2])(Hi @ [x, y, 1.0]) for x, y in self.SCR])
        def split(Q): c = Q.mean(0); s = np.linalg.norm(Q - c, axis=1).mean(); return c, s, (Q - c) / s
        c0, s0, u0 = split(self.Q0); c1, s1, u1 = split(Q1)
        s = s0 ** (1 - k) * s1 ** k; f = (s0 - s) / (s0 - s1)          # the center travels with the zoom, so the target stays put
        Q = (c0 + (c1 - c0) * f) + s * (u0 + (u1 - u0) * k)
        return cv2.getPerspectiveTransform(Q.astype(np.float32), self.SCR).astype(float)

    # ---------- the drawn frame ----------
    def pts(self, Hm, lls):
        P = np.array([ll2km(p) + (1.0,) for p in lls]) @ Hm.T
        sg = np.sign((Hm @ [5.716 * KMX, 50.0 * KMY, 1.0])[2]); w = np.where(P[:, 2:3] * sg > 1e-6, P[:, 2:3], np.nan)      # behind the camera: dropped
        return np.nan_to_num(P[:, :2] / w, nan=1e6)
    def drawn(self, Hm, tau, k, pm, redraw=None):
        """redraw: (am_alpha, pm_frac) for a quiet day's line redraw on the balcony"""
        d = self.d; SS = 2                                                    # supersample the line work
        im = Image.new('RGB', (W * SS, H * SS), tuple(int(v * 255) for v in PAPER)); dr = ImageDraw.Draw(im)
        c = np.array([W / 2, 820.0]); o = np.linalg.inv(Hm) @ [c[0], c[1], 1]; o = o[:2] / o[2]
        e = Hm @ [o[0] + 1, o[1], 1]; pxkm = float(np.linalg.norm(e[:2] / e[2] - c))          # frame pixels per km at the middle
        def poly(lls, col, w, dash=None):
            P = self.pts(Hm, lls) * SS
            if dash is None:
                run = []
                for p in list(P) + [None]:
                    if p is not None and abs(p[0]) < 9000 and abs(p[1]) < 12000: run.append(tuple(p)); continue
                    if len(run) > 1: dr.line(run, fill=col, width=max(1, int(round(w * SS))), joint='curve')
                    run = []
                return
            on, off = dash[0] * SS, dash[1] * SS; acc, pen = 0.0, True
            for a, b in zip(P, P[1:]):
                Ls = float(np.linalg.norm(b - a)); s = 0.0
                if Ls < 1e-6 or max(abs(a).max(), abs(b).max()) > 8000: continue
                while s < Ls:
                    st = min((on if pen else off) - acc, Ls - s)
                    if pen: dr.line([tuple(a + (b - a) * s / Ls), tuple(a + (b - a) * (s + st) / Ls)], fill=col, width=max(1, int(round(w * SS))))
                    s += st; acc += st
                    if acc >= (on if pen else off) - 1e-6: acc, pen = 0.0, not pen
        rk = min(1, max(0, (pxkm - 8.0) / 3.0))                               # roads come in as the camera comes down
        if rk > 0:
            col = tuple(int(PAPER[i] * 255 * (1 - rk) + COL['road'][i] * rk) for i in range(3))
            for pl in self.roads.values(): poly(pl, col, 4.5)
        for b in self.borders: poly(b, COL['border'], 2.6 + 0.6 * k, dash=(13, 6))
        for n, pl in self.rivers.items(): poly(pl, COL['river'], (7 if n in ('Meuse', 'Rhine', 'Moselle') else 4) * (1 + 0.35 * k))
        # towns: the same list at every height; smaller places appear as the camera comes down, names keep their size
        f = ImageFont.truetype(FONT, 24 * SS); boxes = []
        def hit(b): return any(b[0] < q[2] and q[0] < b[2] and b[1] < q[3] and q[1] < b[3] for q in boxes)
        lay = Image.new('RGBA', im.size, (0, 0, 0, 0)); ld = ImageDraw.Draw(lay)
        for tw in sorted(self.towns, key=lambda q: -q['span']):
            need = {6.0: 0.0, 3.5: 9.0, 1.0: 99.0}[tw['span']]; a = min(1, max(0, (pxkm - need) / 2.0 + (1 if need == 0 else 0)))
            if a <= 0: continue
            x, y = self.pts(Hm, [(tw['lon'], tw['lat'])])[0] * SS
            if not (-200 < x < W * SS + 200 and -100 < y < H * SS + 100): continue
            r = 6 * SS; label = tw['name'].upper(); wt = ld.textlength(label, font=f); hh = 24 * SS
            dot = (x - r * 1.6, y - r * 1.6, x + r * 1.6, y + r * 1.6)
            if hit(dot): continue
            for ox, anc in ((r * 1.8, 'lm'), (-r * 1.8, 'rm')):
                bx = (x + ox, y - hh / 2, x + ox + wt, y + hh / 2) if anc == 'lm' else (x + ox - wt, y - hh / 2, x + ox, y + hh / 2)
                if not hit(bx): break
            else: continue
            boxes += [dot, bx]; ink = COL['ink'] + (int(255 * a),)
            ld.ellipse([x - r, y - r, x + r, y + r], fill=ink); ld.text((x + ox, y), label, font=f, fill=ink, anchor=anc)
        im = Image.alpha_composite(im.convert('RGBA'), lay).convert('RGB'); dr = ImageDraw.Draw(im)
        # the grease pencil line
        def mix(a): return tuple(int(PAPER[i] * 255 * (1 - a) + COL['wax'][i] * a) for i in range(3))
        if redraw is None:
            key = 'linePM' if pm else 'lineAM'
            poly(C.catmull([tuple(p) for p in d.mr[key]], 12), COL['wax'], 6 + 2 * k)
            for pk in self.res['pockets' if pm else 'pocketsAM']: poly(C.catmull([tuple(p) for p in pk['ring']], 8, closed=True), COL['wax'], 6 + 2 * k)
        else:
            am_a, pm_f = redraw
            poly(C.catmull([tuple(p) for p in d.mr['lineAM']], 12), mix(am_a), 6)
            for pk in self.res['pocketsAM']: poly(C.catmull([tuple(p) for p in pk['ring']], 8, closed=True), mix(am_a), 6)
            if pm_f > 0:
                P = C.catmull([tuple(p) for p in d.mr['linePM']], 12); seg = np.r_[0, np.cumsum(np.hypot(*np.diff(np.array(P), axis=0).T))]
                n = max(2, int(np.searchsorted(seg, pm_f * seg[-1])) + 1); poly(P[:n], COL['wax'], 6)
                if pm_f >= 1:
                    for pk in self.res['pockets']: poly(C.catmull([tuple(p) for p in pk['ring']], 8, closed=True), COL['wax'], 6)
        F = np.asarray(im.resize((W, H), Image.LANCZOS), np.float32) / 255
        if k == 0: self._tboxes = [tuple(v / SS for v in b) for b in boxes]
        ka = 1 - D.ease(min(1, max(0, (k - 0.25) / 0.4)))  # it fades early in the descent, so it never ghosts into the close view
        if self.key_km is not None and ka > 0:             # the key card lies on the table, under nothing
            P = np.c_[self.key_km, np.ones(4)] @ Hm.T; K.draw(F, self.key, (P[:, :2] / P[:, 2:3]).astype(np.float32), ka)
        # blocks: thin tiles, far ones first
        items = []
        for p in d.pieces:
            q = d.pos(p, tau)
            if q is not None: items.append((p, d.table.LL(q)))
        for p in self.far:
            q = p['pm'] if pm else p['am']
            if q: items.append((p, tuple(q)))
        hk = D.BS / 2 / d.table.KX; hl = D.BS / 2 / d.table.KY; liftk = 0.25 + 0.75 * k
        def corners(p, ll):
            a = math.radians(D.rot_deg(p['id'])); out = []
            for sx, sy in ((-1, 1), (1, 1), (1, -1), (-1, -1)):
                ux, uy = sx * math.cos(a) - sy * math.sin(a), sx * math.sin(a) + sy * math.cos(a)
                out.append((ll[0] + ux * hk, ll[1] + uy * hl))
            return self.pts(Hm, out)
        geo = sorted([(p, corners(p, ll)) for p, ll in items], key=lambda it: it[1][:, 1].mean())
        sh = np.zeros((H, W), np.float32)
        for p, Q in geo:
            side = float(np.linalg.norm(Q[1] - Q[0])); lift = liftk * (D.BH / D.BS) * side
            cv2.fillConvexPoly(sh, (Q + [lift * 0.5 + side * 0.03, side * 0.04]).astype(np.int32), 1.0, cv2.LINE_AA)
        sh = cv2.GaussianBlur(sh, (0, 0), 3 + 4 * k); F *= (1 - 0.42 * sh[..., None])
        for p, Q in geo:
            side = float(np.linalg.norm(Q[1] - Q[0]))
            if Q[:, 0].max() < -50 or Q[:, 0].min() > W + 50 or Q[:, 1].max() < -50 or Q[:, 1].min() > H + 50: continue
            lift = liftk * (D.BH / D.BS) * side; T = Q - [0, lift]
            hull = cv2.convexHull(np.vstack([Q, T]).astype(np.float32)).astype(np.int32)
            cv2.fillConvexPoly(F, hull, (0.26, 0.16, 0.09), cv2.LINE_AA)
            face = self.faces[p['id']]; n = int(min(800, max(24, side * 2)))
            fs = cv2.resize(face, (n, n), interpolation=cv2.INTER_AREA)
            x0, y0 = np.floor(T.min(0)).astype(int) - 2; x1, y1 = np.ceil(T.max(0)).astype(int) + 2
            x0c, y0c, x1c, y1c = max(0, x0), max(0, y0), min(W, x1), min(H, y1)
            if x1c <= x0c or y1c <= y0c: continue
            m = 0.045; src = np.array([[-m * n, -m * n], [n + m * n, -m * n], [n + m * n, n + m * n], [-m * n, n + m * n]], np.float32)   # the face sits inside a walnut edge
            M = cv2.getPerspectiveTransform(src, (T - [x0c, y0c]).astype(np.float32))
            st = np.dstack([fs, np.ones((n, n), np.float32)])
            wp = cv2.warpPerspective(st, M, (x1c - x0c, y1c - y0c), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=0)
            a = wp[..., 3:4]; R = F[y0c:y1c, x0c:x1c]; F[y0c:y1c, x0c:x1c] = R * (1 - a) + wp[..., :3] * a
        return F * self.L * self.grain

    def _place_key(self):
        """find the card's spot in the balcony view: clear of the tab, the strip, every block and both lines"""
        d = self.d; tau0 = d.t_table; Hm = self.Hmix(0.0, tau0)
        self.drawn(Hm, tau0, 0.0, False)                   # also records where the town names fall
        hard = np.zeros((H, W), np.uint8)
        for L in (self.c.TAB, self.c.SA, self.c.SB): hard |= (L[..., 3] > 0.05).astype(np.uint8)
        for key in ('lineAM', 'linePM'):
            cv2.polylines(hard, [self.pts(Hm, C.catmull([tuple(p) for p in d.mr[key]], 12)).astype(np.int32)], False, 1, 12)
        for pk in self.res['pocketsAM'] + self.res['pockets']:
            cv2.polylines(hard, [self.pts(Hm, C.catmull([tuple(p) for p in pk['ring']], 8, closed=True)).astype(np.int32)], True, 1, 12)
        hk = D.BS / 2 / d.table.KX * 1.15; hl = D.BS / 2 / d.table.KY * 1.15
        spots = [d.table.LL(q) for p in d.pieces for q in (d.pos(p, tau0), d.pos(p, self.tau_end)) if q is not None]
        spots += [tuple(q) for p in self.far for q in (p['am'], p['pm']) if q]
        for ll in spots:
            Q = self.pts(Hm, [(ll[0] - hk, ll[1] - hl), (ll[0] + hk, ll[1] - hl), (ll[0] + hk, ll[1] + hl), (ll[0] - hk, ll[1] + hl)])
            cv2.fillConvexPoly(hard, Q.astype(np.int32), 1)
        soft = np.zeros((H, W), np.uint8)
        for b in getattr(self, '_tboxes', []): cv2.rectangle(soft, (int(b[0]), int(b[1])), (int(b[2]), int(b[3])), 1, -1)
        sf = D.TPL['safe']
        Q = K.place(W, H, hard, soft, sf['top'], H - sf['bottom'], sf['left'], W - sf['right'])
        if Q is None: print('key card: no clear space on the balcony; left off'); return
        Hi = np.linalg.inv(Hm); P = np.c_[Q, np.ones(4)] @ Hi.T; self.key_km = P[:, :2] / P[:, 2:3]

    # ---------- the clip ----------
    def overlays(self, F, strip_b=0.0):
        C.over(F, self.c.TAB); C.over(F, self.c.SA, 1 - strip_b); C.over(F, self.c.SB, strip_b); return F
    def frame(self, t):
        c, d = self.c, self.d; B = D.B; tau0 = d.t_table
        def balcony(pm):
            key = 'pm' if pm else 'am'
            if key not in self._cache: self._cache[key] = self.drawn(self.Hmix(0.0, self.tau_end if pm else tau0), self.tau_end if pm else tau0, 0.0, pm)
            return self._cache[key].copy()
        if t < B['still']: return C.zoom(c.OPEN.copy(), 1.0 + 0.02 * t / 1.5)
        if t < self.t_bal:
            k = D.ease((t - B['still']) / (self.t_bal - B['still']))
            F = C.zoom(c.OPEN_BG.copy(), 1.0 + 0.02 * t / 1.5) * (1 - k) + balcony(False) * k
            if k < 0.5: C.over(F, c.OPEN_OV)
            else: self.overlays(F)
            return F
        if self.quiet and t >= self.t_bal:
            if t < self.q_wipe: return self.overlays(balcony(False))
            am_a = 1 - 0.72 * D.ease(min(1, (t - self.q_wipe) / B['wipe'])); pm_f = min(1, max(0, (t - self.q_draw) / B['draw']))
            if t >= self.q_end:
                if 'qend' not in self._cache: self._cache['qend'] = self.drawn(self.Hmix(0.0, tau0), tau0, 0.0, False, (0.28, 1.0))
                F = self.overlays(self._cache['qend'].copy(), 1.0)
            else: F = self.overlays(self.drawn(self.Hmix(0.0, tau0), tau0, 0.0, False, (am_a, pm_f)), min(1, max(0, (t - self.q_end + 0.2) / 0.35)))
            if t > self.T - B['loop']: k = D.ease((t - (self.T - B['loop'])) / B['loop']); F = F * (1 - k) + c.OPEN * k
            return F
        if t < self.t_push: return self.overlays(balcony(False))
        if t < self.t_close:
            k = D.ease((t - self.t_push) / (self.t_close - self.t_push)); F = self.drawn(self.Hmix(k, tau0), tau0, k, False)
            if k > 0.8: x = (k - 0.8) / 0.2; F = F * (1 - x) + c.table_frame(tau0, False) * x
            return self.overlays(F)
        if t < self.t_pull:
            tau = tau0 + (t - self.t_close); F = c.table_frame(tau, False)
            return self.overlays(F, min(1, max(0, (tau - d.t_tonight) / 0.35)))
        if t < self.t_up:
            k = 1 - D.ease((t - self.t_pull) / (self.t_up - self.t_pull)); F = self.drawn(self.Hmix(k, self.tau_end), self.tau_end, k, True)
            if k > 0.8: x = (k - 0.8) / 0.2; F = F * (1 - x) + c.table_frame(self.tau_end, False) * x
            return self.overlays(F, 1.0)
        F = self.overlays(balcony(True), 1.0)
        if t > self.T - B['loop']: k = D.ease((t - (self.T - B['loop'])) / B['loop']); F = F * (1 - k) + c.OPEN * k
        return F
    def events(self):
        if self.quiet: return [(self.q_wipe, 'wipe', D.B['wipe']), (self.q_draw, 'pencil', D.B['draw'])]
        ev = [(t + self.shift, kind, g) for t, kind, g in self.d.events if t >= self.d.t_table - 1e-6]
        return ev

def write(zc, out):
    n = int(round(zc.T * FPS)); silent = out + '.silent.mp4'
    ff = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                           '-c:v', 'libx264', '-crf', '18', '-preset', 'veryfast', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', silent], stdin=subprocess.PIPE)
    for i in range(n): ff.stdin.write((np.clip(zc.frame(i / FPS), 0, 1) * 255 + 0.5).astype(np.uint8).tobytes())
    ff.stdin.close(); ff.wait()
    import maproom_sound as snd
    wav = out + '.wav'; snd.build(zc.events(), zc.T, wav, seed=zc.res['rec']['day'])
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', silent, '-i', wav, '-map', '0:v', '-map', '1:a', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', '-shortest', out], check=True)
    os.remove(silent); os.remove(wav); print('OK', out, f'{zc.T:.1f} s')
def still(zc, t, fn): cv2.imwrite(fn, (np.clip(zc.frame(t), 0, 1)[..., ::-1] * 255).astype(np.uint8)); print('wrote', fn)
