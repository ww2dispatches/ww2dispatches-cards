"""The Map Room compositor: one day's clip from the renders (plates, block sprites, rake sprites, overlays).
Usage: clip.py <day.json> <work dir> <out.mp4> [t1,t2,... stills only]
Expects (render_day.py makes them): <work>/views/<view>/{plate,platepad}.png, sprites, rake sprites, faces, <work>/ov/<day>/...
Flat marks (grease pencil line, pockets, cut off rings, GROUNDED, the day's hatch) are drawn on a top down sheet in
table units and warped onto the table with the camera's homography, so they lie flat and in perspective."""
import json, sys, os, math, subprocess
import numpy as np, cv2
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import day as D
from PIL import Image, ImageDraw, ImageFont

W, H = D.W, D.H; FPS = D.TPL['fps']; B = D.B
def rd(p):
    im = cv2.imread(p, cv2.IMREAD_UNCHANGED)
    if im is None: raise SystemExit(f'missing render: {p}')
    im = im.astype(np.float32) / (65535.0 if im.dtype == np.uint16 else 255.0)
    return im[..., [2, 1, 0, 3]] if im.shape[2] == 4 else im[..., ::-1]
def load_rgba(p):
    im = cv2.imread(p, cv2.IMREAD_UNCHANGED).astype(np.float32) / 255
    if im.shape[2] == 3: im = np.concatenate([im, np.ones_like(im[..., :1])], axis=2)
    return np.concatenate([im[..., [2, 1, 0]], im[..., 3:4]], axis=2)
def over(F, L, k=1.0): a = L[..., 3:4] * k; F[:] = F * (1 - a) + L[..., :3] * a
def zoom(F, z, cx=560, cy=900):
    M = np.array([[z, 0, cx - z * cx], [0, z, cy - z * cy]], np.float32)
    return cv2.warpAffine(F, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)

# ---------- sprites ----------
PLATE_PAD = (270, 240)
class Sprite:
    """a render of one object over the table: its shadow and reflection become a ratio over the plate, its body comes
    from the mask render. Slid in 2D; it keeps the perspective of the spot it was rendered at."""
    def __init__(self, full, mask, platepad, anchor):
        px, py = (full.shape[1] - W) // 2, (full.shape[0] - H) // 2
        al = full[..., 3]; ys, xs = np.where(al > 0.5)
        y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
        f = full[y0:y1, x0:x1, :3]
        b = np.full_like(f, np.nan)                       # the plate behind, where the padded plate covers it
        ox, oy = px - PLATE_PAD[0], py - PLATE_PAD[1]
        sy0, sy1 = max(y0, oy), min(y1, oy + platepad.shape[0]); sx0, sx1 = max(x0, ox), min(x1, ox + platepad.shape[1])
        if sy1 > sy0 and sx1 > sx0: b[sy0 - y0:sy1 - y0, sx0 - x0:sx1 - x0] = platepad[sy0 - oy:sy1 - oy, sx0 - ox:sx1 - ox, :3]
        m = mask[y0:y1, x0:x1]; a = m[..., 3:4]; C = m[..., :3]
        r = np.where(np.isnan(b), 1.0, np.clip(f / np.maximum(np.nan_to_num(b, nan=1.0), 1e-3), 0.15, 1.6))
        valid = (cv2.erode((m[..., 3] < 0.003).astype(np.uint8), np.ones((5, 5), np.uint8)) > 0).astype(np.float32)[..., None]
        num = cv2.GaussianBlur(r * valid, (0, 0), 3); den = cv2.GaussianBlur(valid[..., 0], (0, 0), 3)[..., None]
        r = np.where(valid > 0, r, num / np.maximum(den, 1e-4)); r = np.where(den > 1e-4, r, 1.0)
        dev = np.abs(r - 1).max(axis=2, keepdims=True); k = np.clip((dev - 0.012) / 0.03, 0, 1); r = 1 + (r - 1) * k
        hh, ww = r.shape[:2]; e = 14
        fy = np.clip(np.minimum(np.arange(hh), hh - 1 - np.arange(hh)) / e, 0, 1)[:, None]
        fx = np.clip(np.minimum(np.arange(ww), ww - 1 - np.arange(ww)) / e, 0, 1)[None, :]
        r = 1 + (r - 1) * (fy * fx)[..., None]
        self.r, self.a, self.C = r.astype(np.float32), a.astype(np.float32), C.astype(np.float32)
        self.o = np.array([x0 - px, y0 - py], float)
        self.A, self.wA = D.proj(*anchor, 0.0)
        self.A = np.array(self.A)
    def draw(self, F, Q, alpha=1.0):
        q, wq = D.proj(*Q, 0.0); q = np.array(q); s = self.wA / wq
        tl = q + s * (self.o - self.A); hh, ww = self.r.shape[:2]
        X0, Y0 = int(math.floor(tl[0])), int(math.floor(tl[1])); Wd, Hd = int(ww * s) + 3, int(hh * s) + 3
        fx0, fy0 = max(0, X0), max(0, Y0); fx1, fy1 = min(W, X0 + Wd), min(H, Y0 + Hd)
        if fx1 <= fx0 or fy1 <= fy0: return
        M = np.array([[s, 0, tl[0] - X0], [0, s, tl[1] - Y0]], np.float32)
        st = np.concatenate([self.r - 1, self.a, self.C], axis=2)
        out = cv2.warpAffine(st, M, (Wd, Hd), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=0)
        r, a, C = out[..., :3] * alpha + 1, out[..., 3:4] * alpha, out[..., 4:7] * alpha
        sl = (slice(fy0 - Y0, fy1 - Y0), slice(fx0 - X0, fx1 - X0)); R = F[fy0:fy1, fx0:fx1]
        F[fy0:fy1, fx0:fx1] = R * r[sl] * (1 - a[sl]) + C[sl]

# ---------- flat marks on the table ----------
PPU = 200                                            # sheet pixels per table unit
SW, SH = int(D.TW * PPU), int(D.TH * PPU)
Hs = np.array(D.homography())
Csheet = np.array([[1 / PPU, 0, -D.TW / 2], [0, -1 / PPU, D.TH / 2], [0, 0, 1]])
WARP = Hs @ Csheet
def to_sheet(xy): return ((xy[0] + D.TW / 2) * PPU, (D.TH / 2 - xy[1]) * PPU)
def warp(sheet): return cv2.warpPerspective(sheet, WARP, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=0)
_rng = np.random.default_rng(5)
GRAIN = cv2.GaussianBlur(_rng.standard_normal((H, W)).astype(np.float32), (0, 0), 1.8); GRAIN = (GRAIN - GRAIN.mean()) / GRAIN.std()
WAX = np.array([0.60, 0.09, 0.07], np.float32)
AIR_INK = np.array([0.09, 0.08, 0.08], np.float32)     # air tracks in black grease pencil, apart from the red front
LINE_W = 0.05                                       # grease pencil width in table units
def catmull(P, n=16, closed=False):
    P = np.array(P, float)
    P = np.vstack([P[-1], P, P[0], P[1]]) if closed else np.vstack([P[0], P, P[-1]])
    out = []
    for i in range(1, len(P) - 2):
        p0, p1, p2, p3 = P[i - 1], P[i], P[i + 1], P[i + 2]
        for tt in np.linspace(0, 1, n, endpoint=False):
            t2, t3 = tt * tt, tt * tt * tt
            out.append(0.5 * ((2 * p1) + (-p0 + p2) * tt + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t2 + (-p0 + 3 * p1 - 3 * p2 + p3) * t3))
    out.append(P[-2]); return np.array(out)
def jitter(c, seed, amt=0.012):
    r = np.random.default_rng(seed); n = len(c)
    off = cv2.GaussianBlur(r.standard_normal((n, 1)).astype(np.float32), (0, 0), 6)[:, 0] * amt
    d = np.gradient(c, axis=0); nrm = np.stack([-d[:, 1], d[:, 0]], 1); nrm /= np.maximum(np.linalg.norm(nrm, axis=1, keepdims=True), 1e-6)
    return c + nrm * off[:, None]
def stroke(pts_xy, width=LINE_W, frac=1.0):
    """a pencil stroke (table units) drawn on the sheet up to `frac` of its length, warped to the frame"""
    pts = np.array([to_sheet(p) for p in pts_xy])
    if frac < 1:
        seg = np.r_[0, np.cumsum(np.linalg.norm(np.diff(pts, axis=0), axis=1))]; L = frac * seg[-1]; k = np.searchsorted(seg, L)
        if k <= 0: return np.zeros((H, W), np.float32)
        if k < len(pts):
            u = (L - seg[k - 1]) / max(seg[k] - seg[k - 1], 1e-6); pts = np.vstack([pts[:k], pts[k - 1] + (pts[k] - pts[k - 1]) * u])
    m = np.zeros((SH, SW), np.uint8)
    if len(pts) >= 2: cv2.polylines(m, [np.round(pts * 16).astype(np.int32)], False, 255, max(1, int(width * PPU)), cv2.LINE_AA, shift=4)
    return warp(m.astype(np.float32) / 255)
def dashes(pts_xy, frac=1.0, dash=0.20, gap=0.13, width=LINE_W):
    """a dashed pencil track (table units), drawn one dash at a time up to `frac` of its length"""
    pts = np.array([to_sheet(p) for p in pts_xy]); seg = np.r_[0, np.cumsum(np.linalg.norm(np.diff(pts, axis=0), axis=1))]
    L = frac * seg[-1]; dpx, gpx = dash * PPU, gap * PPU; m = np.zeros((SH, SW), np.uint8); s0 = 0.0
    def at(x): k = min(max(np.searchsorted(seg, x), 1), len(pts) - 1); u = (x - seg[k - 1]) / max(seg[k] - seg[k - 1], 1e-6); return pts[k - 1] + (pts[k] - pts[k - 1]) * u
    while s0 < L:
        s1 = min(s0 + dpx, L); xs = [s0] + [v for v in seg if s0 < v < s1] + [s1]
        q = np.array([at(x) for x in xs]); cv2.polylines(m, [np.round(q * 16).astype(np.int32)], False, 255, max(1, int(width * PPU)), cv2.LINE_AA, shift=4)
        s0 += dpx + gpx
    return warp(m.astype(np.float32) / 255)
def wax(a):
    a = a * np.clip(0.90 + 0.12 * GRAIN, 0, 1); a *= np.clip((GRAIN + 2.7) / 0.8, 0, 1); return a[..., None]
def paint(F, a, col=WAX):
    F[:] = F * (1 - a) + col * a; F[:] = F + a * np.clip(GRAIN[..., None] - 1.2, 0, 1) * 0.35
def text_mask(text, xy, height=0.36, angle=-4, frac=1.0):
    f = ImageFont.truetype(os.path.join(HERE, '..', 'fonts', 'special-elite.ttf'), int(height * PPU))
    w = int(f.getlength(text)) + 20; h = int(height * PPU * 1.6)
    im = Image.new('L', (w, h), 0); ImageDraw.Draw(im).text((10, h // 2), text, font=f, fill=255, anchor='lm')
    im = im.crop((0, 0, int(10 + (w - 10) * frac), h)).rotate(angle, expand=True, resample=Image.BICUBIC)
    m = np.zeros((SH, SW), np.uint8); sx, sy = to_sheet(xy); x0, y0 = int(sx), int(sy - im.height / 2)
    arr = np.array(im); x1, y1 = min(SW, x0 + arr.shape[1]), min(SH, y0 + arr.shape[0])
    if x1 > x0 and y1 > y0 and x0 >= 0 and y0 >= 0: m[y0:y1, x0:x1] = arr[:y1 - y0, :x1 - x0]
    return warp(m.astype(np.float32) / 255)

class Clip:
    def __init__(self, day_path, work):
        self.d = D.Day(day_path); self.work = work; d = self.d
        vname = os.environ.get('MAPROOM_VNAME') or d.view or 'main'; vdir = os.path.join(work, 'views', vname)
        self.plate = rd(os.path.join(vdir, 'plate.png'))[..., :3]; platepad = rd(os.path.join(vdir, 'platepad.png'))
        self.spr = {}
        for p in d.pieces:
            fid = D.face_id(p); c = d.anchor(p); key = f"{fid}_{c[0]:+.1f}_{c[1]:+.1f}"
            self.spr[p['id']] = Sprite(rd(os.path.join(vdir, 'sprites', f'blk-{key}.png')), rd(os.path.join(vdir, 'sprites', f'msk-{key}.png')), platepad, c)
        self.rake = {}
        ra = rake_anchor()
        for ang in d.rake_angles():
            self.rake[ang] = Sprite(rd(os.path.join(vdir, 'rake', f"rake-{ang}.png")), rd(os.path.join(vdir, 'rake', f"rmsk-{ang}.png")), platepad, ra)
        # overview: the whole battle before the push in
        if d.view:
            self.main_plate = rd(os.path.join(work, 'views', 'main', 'plate.png'))[..., :3]
            self.push_box = self._push_box()
        self._marks()
        ov = os.path.join(work, 'ov', os.path.splitext(os.path.basename(day_path))[0])
        self.TAB, self.SA, self.SB = load_rgba(f'{ov}/tab.png'), load_rgba(f'{ov}/stripA.png'), load_rgba(f'{ov}/stripB.png')
        self.OPEN = load_rgba(f'{ov}/opener.png')[..., :3]; self.OPEN_BG = load_rgba(f'{ov}/openbg.png')[..., :3]; self.OPEN_OV = load_rgba(f'{ov}/openov.png')

    def _push_box(self):
        """where the day's view sits on the whole battle table, as a frame rectangle to zoom into"""
        d = self.d; pts = []
        for px, py in [(0, 0), (W, 0), (W, H), (0, H), (W / 2, 0), (W / 2, H)]:
            ll = d.table.LL(D.unproject(px, py)); xy = d.main.XY(ll); pts.append(D.proj(*xy, 0.0)[0])
        pts = np.array(pts); x0, y0 = pts.min(0); x1, y1 = pts.max(0)
        cx, cy = (x0 + x1) / 2, (y0 + y1) / 2; z = min(W / max(x1 - x0, 1), H / max(y1 - y0, 1))
        return cx, cy, max(1.0, z)

    def _line_xy(self, key, table=None):
        t = table or self.d.table; ln = self.d.mr[key]
        return jitter(catmull([t.XY(p) for p in ln], 24), 1 if key == 'lineAM' else 2)
    def _pockets_xy(self, key, table=None):
        t = table or self.d.table
        return [jitter(catmull([t.XY(p) for p in pk['ring']], 16, closed=True), 3 + i) for i, pk in enumerate(self.d.mr.get(key, []))]
    def _marks(self):
        d = self.d
        am = stroke(self._line_xy('lineAM'))
        for r in self._pockets_xy('pocketsAM'): am = np.maximum(am, stroke(r))
        self.AM_A = wax(am); self.GHOST_A = cv2.GaussianBlur(self.AM_A[..., 0], (0, 0), 1.6)[..., None] * 0.28
        self.PM_LINE = self._line_xy('linePM'); self.PM_POCKETS = self._pockets_xy('pocketsPM')
        if d.view:
            m = stroke(self._line_xy('lineAM', d.main))
            for r in self._pockets_xy('pocketsAM', d.main): m = np.maximum(m, stroke(r))
            self.MAIN_AM_A = wax(m)
        # the day's changed ground, hatched
        def axis_mask(lkey, pkey):
            ln = [d.table.XY(p) for p in d.mr[lkey]]; far = D.TW * 3
            poly = [(ln[0][0], ln[0][1] + far)] + ln + [(ln[-1][0], ln[-1][1] - far), (far, ln[-1][1] - far), (far, ln[0][1] + far)]
            m = np.zeros((SH, SW), np.uint8); cv2.fillPoly(m, [np.round(np.array([to_sheet(p) for p in poly]) * 16).astype(np.int32)], 255, cv2.LINE_AA, shift=4)
            for pk in d.mr.get(pkey, []):
                ring = np.round(np.array([to_sheet(d.table.XY(p)) for p in pk['ring']]) * 16).astype(np.int32)
                cv2.fillPoly(m, [ring], 255 if pk['side'] == 'axis' else 0, cv2.LINE_AA, shift=4)
            return m.astype(np.float32) / 255
        changed = np.abs(axis_mask('linePM', 'pocketsPM') - axis_mask('lineAM', 'pocketsAM'))
        # drop slivers thinner than about 0.12 table units: where the two lines' ends differ slightly, their straight
        # extensions off the table would otherwise hatch a hairline strip; real gains (the Bastogne corridor) are wider
        k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (25, 25))
        changed = cv2.morphologyEx((changed > 0.5).astype(np.uint8), cv2.MORPH_OPEN, k).astype(np.float32)
        hm = np.zeros((SH, SW), np.uint8)
        for c0 in np.arange(-SH, SW, int(0.16 * PPU)): cv2.line(hm, (int(c0), SH), (int(c0 + SH), 0), 255, 3, cv2.LINE_AA)
        shade = changed * (0.10 + 0.22 * hm.astype(np.float32) / 255)
        self.SHADE_A = (warp(shade) * np.clip(0.85 + 0.2 * GRAIN, 0, 1))[..., None]
        self.marks = {}                                  # cut off rings and GROUNDED, by piece
        for s in d.slots:
            p = d.by_id[s['id']]
            if s['move'] == 'cut_off':
                c = d.rest_from(p); th = np.linspace(0, 2 * math.pi * 1.08, 90) + 0.6
                pts = [(c[0] + 1.12 * math.cos(a) * (1 + 0.04 * math.sin(3 * a)), c[1] + 1.12 * math.sin(a)) for a in th]
                self.marks[p['id']] = ('ring', jitter(np.array(pts), 7, 0.02), s)
            elif s['move'] == 'grounded':
                self.marks[p['id']] = ('text', self._text_spot(p, 'GROUNDED'), s)
            elif s['move'] == 'air_mission':
                self.marks[p['id']] = ('track', d.air_track(p), s)

    def _text_spot(self, p, text, height=0.36):
        """beside the block, in the first of east, west, below, above that is clear of every other block and in the zone"""
        d = self.d; c = d.rest_from(p)
        f = ImageFont.truetype(os.path.join(HERE, '..', 'fonts', 'special-elite.ttf'), int(height * PPU)); w = f.getlength(text) / PPU
        g = D.BS / 2 + 0.12
        spots = [(c[0] + g, c[1]), (c[0] - g - w, c[1]), (c[0] - w / 2, c[1] - g - height * 0.6), (c[0] - w / 2, c[1] + g + height * 0.6)]
        others = [q for q in (d.rest_to(o) for o in d.pieces if o['id'] != p['id']) if q] + [q for q in (d.rest_from(o) for o in d.pieces if o['id'] != p['id']) if q]
        bz = D.TPL['block_zone']
        def cost(xy):
            """how much of the word other blocks would hide; off screen or under the tab or strip rules a spot out"""
            x0, x1, y0, y1 = xy[0], xy[0] + w, xy[1] - height * 0.6, xy[1] + height * 0.6
            for cx, cy in [(x0, y0), (x1, y0), (x0, y1), (x1, y1)]:
                px, py = D.zoomed(D.proj(cx, cy, 0.0)[0])
                if not (bz['left'] <= px <= bz['right'] and bz['top'] <= py <= bz['bottom']): return float('inf')
            hidden = 0.0
            for q in others:
                ox = min(x1, q[0] + D.BS / 2) - max(x0, q[0] - D.BS / 2); oy = min(y1, q[1] + D.BS / 2) - max(y0, q[1] - D.BS / 2)
                if ox > 0 and oy > 0: hidden += ox * oy
            return hidden
        return min(spots, key=cost)

    def flat(self, F, t):
        d = self.d
        if t < d.t_wipe: paint(F, self.AM_A)
        else:
            k = D.ease((t - d.t_wipe) / B['wipe']); paint(F, self.AM_A * (1 - k) + self.GHOST_A * k)
            if t >= d.t_shade:
                k = D.ease((t - d.t_shade) / B['shade']); a = self.SHADE_A * k; F[:] = F * (1 - a) + np.array([0.20, 0.21, 0.23], np.float32) * a
            if t >= d.t_draw:
                f = min(1.0, (t - d.t_draw) / B['draw']); f = f * f * (3 - 2 * f)
                fl = min(1.0, f / 0.75); m = stroke(self.PM_LINE, frac=fl)
                if f > 0.75:
                    for r in self.PM_POCKETS: m = np.maximum(m, stroke(r, frac=(f - 0.75) / 0.25))
                paint(F, wax(m))
        for pid, (kind, geo, s) in self.marks.items():
            if kind == 'track':
                (a0, a1), (f0, f1) = s['track'], s['fade']
                if t < a0 or t >= f1: continue
                f = min(1.0, (t - a0) / (a1 - a0)); fade = 1.0 if t < f0 else 1 - D.ease((t - f0) / (f1 - f0))
                paint(F, wax(dashes(geo, f)) * fade, AIR_INK); continue
            if t < s['t0']: continue
            f = min(1.0, (t - s['t0']) / (s['t_done'] - s['t0']))
            paint(F, wax(stroke(geo, frac=f) if kind == 'ring' else text_mask('GROUNDED', geo, frac=f)))

    def table_frame(self, t, ov=True):
        d = self.d; F = self.plate.copy(); self.flat(F, t)
        # far blocks first, by where each one is at this moment, so a block moving past another is drawn in the right order
        rk = d.rake(t); order = sorted(d.pieces, key=lambda p: -((d.pos(p, t) or d.rest_from(p) or d.snap_to(p))[1]))
        drawn_rake = False
        for p in order:
            pull = rk and rk[2] == p['id'] and rk[3] == 'pull'
            if rk and rk[2] == p['id'] and not drawn_rake and not pull: self.rake[rk[1]].draw(F, rk[0]); drawn_rake = True
            q = d.pos(p, t)
            if q is not None:
                al = d.alpha(p, t); self.spr[p['id']].draw(F, q, al)
                s = d.slot(p['id'])
                if s and s.get('how') == 'strike': self.strike(F, s, t, al)
            if pull and not drawn_rake: self.rake[rk[1]].draw(F, rk[0]); drawn_rake = True   # a pull reaches over the block
        if rk and not drawn_rake: self.rake[rk[1]].draw(F, rk[0])
        for s in d.slots:                               # a withdrawal's pencil arrow, over the blocks so a neighbour never hides it
            if s.get('how') == 'fade' and s['strokes'][0][2] <= t < s['fade'][1]: self.arrow(F, s, t, d.alpha(d.by_id[s['id']], t))
        F = zoom(F, 1.0 + (D.TPL['push_in'] - 1) * min(1, max(0, (t - d.t_table) / max(d.T - d.t_table, 1e-3))))
        if not ov: return F
        over(F, self.TAB); kb = min(1, max(0, (t - d.t_tonight) / 0.35)); over(F, self.SA, 1 - kb); over(F, self.SB, kb)
        return F
    def strike(self, F, s, t, alpha):
        """the red grease pencil X across a block that has no way out, drawn on the block's top face, stroke by stroke
        at the night line's pace, fading with the block"""
        m = np.zeros((H, W), np.float32)
        for i, (a, b, t0, t1) in enumerate(s['strokes']):
            if t < t0: break
            f = min(1.0, (t - t0) / (t1 - t0)); f = f * f * (3 - 2 * f)
            pts = jitter(np.array([(a[0] + (b[0] - a[0]) * u, a[1] + (b[1] - a[1]) * u) for u in np.linspace(0, f, 40)]), 11 + i, 0.02)
            px = np.array([D.proj(x, y, D.BH)[0] for x, y in pts])
            c = pts[len(pts) // 2]; ppu = math.hypot(*np.subtract(D.proj(c[0] + 1, c[1], D.BH)[0], D.proj(c[0], c[1], D.BH)[0]))
            if len(px) >= 2 and f > 0: cv2.polylines(m, [np.round(px * 16).astype(np.int32)], False, 1.0, max(1, int(round(LINE_W * ppu * 1.2))), cv2.LINE_AA, shift=4)
        paint(F, wax(m) * alpha)
    def arrow(self, F, s, t, alpha):
        """the red grease pencil arrow off a withdrawing block, stroke by stroke at the night line's pace"""
        m = None
        for i, (a, b, t0, t1) in enumerate(s['strokes']):
            if t < t0: break
            f = min(1.0, (t - t0) / (t1 - t0)); f = f * f * (3 - 2 * f)
            pts = jitter(np.array([(a[0] + (b[0] - a[0]) * u, a[1] + (b[1] - a[1]) * u) for u in np.linspace(0, 1, 24)]), 21 + i, 0.01)
            st = stroke(pts, frac=f); m = st if m is None else np.maximum(m, st)
        if m is not None: paint(F, wax(m) * alpha)
    def overview_frame(self, t):
        """the whole battle with the morning line, then a push in to the day's view"""
        d = self.d; F = self.main_plate.copy(); paint(F, self.MAIN_AM_A)
        t0 = B['still'] + B['dissolve'] + B['overview']
        if t < t0: return F
        k = D.ease((t - t0) / B['push_view']); cx, cy, z = self.push_box
        zz = 1 + (z - 1) * k; ccx, ccy = 540 + (cx - 540) * k, 960 + (cy - 960) * k
        M = np.array([[zz, 0, 540 - zz * ccx], [0, zz, 960 - zz * ccy]], np.float32)
        F = cv2.warpAffine(F, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
        if k > 0.4: F = F * (1 - (k - 0.4) / 0.6) + self.table_frame(d.t_table, False) * ((k - 0.4) / 0.6)   # dissolve early: a blown up plate goes soft
        return F
    def frame(self, t):
        d = self.d; T_OPEN, T_X = B['still'], B['dissolve']
        def opener(): return zoom(self.OPEN.copy(), 1.0 + 0.02 * t / (T_OPEN + T_X))
        if t < T_OPEN: return opener()
        if t < T_OPEN + T_X:
            k = D.ease((t - T_OPEN) / T_X)
            nxt = self.overview_frame(t) if d.view else self.table_frame(t, False)
            bg = zoom(self.OPEN_BG.copy(), 1.0 + 0.02 * t / (T_OPEN + T_X)) * (1 - k) + nxt * k
            if t < T_OPEN + T_X / 2: over(bg, self.OPEN_OV)
            else: over(bg, self.TAB); over(bg, self.SA)
            return bg
        if d.view and t < d.t_table:
            F = self.overview_frame(t); over(F, self.TAB); over(F, self.SA); return F
        F = self.table_frame(t)
        if t > d.T - B['loop']:                       # dissolve back to the opening still so the loop runs on
            k = D.ease((t - (d.T - B['loop'])) / B['loop']); F = F * (1 - k) + self.OPEN * k
        return F

def rake_anchor():
    """the rake sprites are rendered with the head at the table point under the middle of the block zone"""
    bz = D.TPL['block_zone']; return D.unproject((bz['left'] + bz['right']) / 2, (bz['top'] + bz['bottom']) / 2)

if __name__ == '__main__':
    day_path, work, out = sys.argv[1], sys.argv[2], sys.argv[3]
    c = Clip(day_path, work)
    if len(sys.argv) > 4:
        for t in [float(x) for x in sys.argv[4].split(',')]:
            fn = f'{os.path.splitext(out)[0]}-{t:05.2f}.png'
            cv2.imwrite(fn, (np.clip(c.frame(t), 0, 1)[..., ::-1] * 255).astype(np.uint8)); print('wrote', fn)
        sys.exit(0)
    n = int(round(c.d.T * FPS))
    ff = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                           '-c:v', 'libx264', '-crf', '18', '-preset', 'veryfast', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', out + '.tmp.mp4'], stdin=subprocess.PIPE)
    for i in range(n): ff.stdin.write((np.clip(c.frame(i / FPS), 0, 1) * 255 + 0.5).astype(np.uint8).tobytes())
    ff.stdin.close(); ff.wait(); os.replace(out + '.tmp.mp4', out); print('OK', out, f'{c.d.T:.1f} s')
