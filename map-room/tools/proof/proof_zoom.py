"""PROOF (20 Nov 2026): the balcony to close zoom. Blocks cover a fixed 10 km of ground. From the balcony the whole
battle shows as small chips; the camera comes down to the day's action, where the rendered table takes over (rake,
readable labels), then goes back up for the new line.
The travelling camera is drawn here in 2D: the map is vectors (rivers, borders, roads, towns) projected per frame, so
line widths and town names keep their screen size and more towns appear as the camera comes down. The close view is
the engine's own render; the two meet at the same camera position and cross fade.
Usage: proof_zoom.py <close day.json> <all pieces day.json> <work dir> <out.mp4> [t1,t2,... stills]
Env: MAPROOM_BH, MAPROOM_TW, MAPROOM_TH as the close render used."""
import sys, os, json, math, subprocess
import numpy as np, cv2
HERE = os.path.dirname(os.path.abspath(__file__)); ENG = os.path.join(HERE, '..', '..', 'engine'); sys.path.insert(0, ENG)
import day as D, clip as C
from PIL import Image, ImageDraw, ImageFont
W, H, FPS = D.W, D.H, 30
KMX, KMY = 71.5, 110.6                      # km per degree at 50 N
def ll2km(ll): return (ll[0] * KMX, ll[1] * KMY)
PAPER = np.array([226, 206, 160], np.float32) / 255
COL = {'river': (78, 104, 124), 'road': (150, 118, 78), 'border': (110, 70, 52), 'ink': (52, 42, 32), 'wax': (153, 23, 18)}
FONT = os.path.join(ENG, '..', 'fonts', 'special-elite.ttf')

class Proof:
    def __init__(self, close_json, all_json, work):
        self.c = C.Clip(close_json, work); self.d = d = self.c.d; t = d.table
        self.allrec = json.load(open(all_json)); self.far = [p for p in self.allrec['mapRoom']['pieces'] if p['id'] not in d.by_id]
        G = os.path.join(ENG, '..', 'series', d.rec['campaign'], 'geo')
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
        self.t_bal = 1.5; self.t_push = 2.9; self.t_close = 4.6
        self.tau_end = d.t_draw + D.B['draw'] + 0.6
        self.t_pull = self.t_close + (self.tau_end - d0); self.t_up = self.t_pull + 1.6; self.T = self.t_up + 2.2
        self.shift = self.t_close - d0
        # balcony camera: the whole battle from nearly straight above
        cx, cy = ll2km((5.66, 49.98)); w = 134.0; h = w * H / W
        self.Q0 = np.array([[cx - w * 0.54, cy + h / 2], [cx + w * 0.54, cy + h / 2], [cx + w * 0.47, cy - h / 2], [cx - w * 0.47, cy - h / 2]])
        self.SCR = np.array([[0, 0], [W, 0], [W, H], [0, H]], np.float32)
        self._cache = {}

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
    def drawn(self, Hm, tau, k, pm):
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
        key = 'linePM' if pm else 'lineAM'
        poly(C.catmull([tuple(p) for p in d.mr[key]], 12), COL['wax'], 6 + 2 * k)
        if not pm:
            for pk in d.mr.get('pocketsAM', []): poly(C.catmull([tuple(p) for p in pk['ring']], 8, closed=True), COL['wax'], 6 + 2 * k)
        F = np.asarray(im.resize((W, H), Image.LANCZOS), np.float32) / 255
        # blocks: thin tiles, far ones first
        items = []
        for p in d.pieces:
            q = d.pos(p, tau)
            if q is not None: items.append((p, d.table.LL(q)))
        for p in self.far: items.append((p, tuple(p['from'])))
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
        ev = [(t + self.shift, kind, g) for t, kind, g in self.d.events if t >= self.d.t_table - 1e-6]
        return ev

if __name__ == '__main__':
    close_json, all_json, work, out = sys.argv[1:5]
    P = Proof(close_json, all_json, work)
    print(f'T {P.T:.1f} s  push {P.t_push}  close {P.t_close}  pull {P.t_pull:.2f}  up {P.t_up:.2f}')
    if len(sys.argv) > 5:
        for t in [float(x) for x in sys.argv[5].split(',')]:
            fn = f'{os.path.splitext(out)[0]}-{t:05.2f}.png'; cv2.imwrite(fn, (np.clip(P.frame(t), 0, 1)[..., ::-1] * 255).astype(np.uint8)); print('wrote', fn)
        sys.exit(0)
    n = int(round(P.T * FPS)); silent = out + '.silent.mp4'
    ff = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                           '-c:v', 'libx264', '-crf', '18', '-preset', 'veryfast', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', silent], stdin=subprocess.PIPE)
    for i in range(n): ff.stdin.write((np.clip(P.frame(i / FPS), 0, 1) * 255 + 0.5).astype(np.uint8).tobytes())
    ff.stdin.close(); ff.wait()
    try:
        import maproom_sound as snd
        wav = out + '.wav'; snd.build(P.events(), P.T, wav)
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', silent, '-i', wav, '-map', '0:v', '-map', '1:a', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', '-shortest', out], check=True)
        os.remove(silent); os.remove(wav)
    except Exception as e:
        print('sound skipped:', e); os.replace(silent, out)
    print('OK', out, f'{P.T:.1f} s')
