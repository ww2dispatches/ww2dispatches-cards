"""Composite a Map Room clip: one film quality plate, each block rendered once and slid in 2D.
Usage: comp.py <sprite dir> <out.mp4> [t1,t2,... stills only | check]
Sprites come from scene.py on the padded frame (room past every edge) and use platepad.png as their shadow base.
Before any frame is drawn, the pre render check refuses a block that is partly off screen at any spot it occupies.
Env: MAPROOM_WORK (work folder), MAPROOM_DAY (day record)."""
import json, sys, subprocess, math, os
import numpy as np, cv2
D = os.environ.get('MAPROOM_WORK', '/home/claude/mr'); S = sys.argv[1] if len(sys.argv) > 1 else 's2'
OUT = sys.argv[2] if len(sys.argv) > 2 else f'{D}/day01_silent.mp4'
ARG3 = sys.argv[3] if len(sys.argv) > 3 else None
ONLY = [float(x) for x in ARG3.split(',')] if ARG3 and ARG3 != 'check' else None
FPS = 30; W, H = 1080, 1920
DAY = json.load(open(os.environ.get('MAPROOM_DAY', f'{D}/day01.json')))
BS, BH = 1.35, 0.36   # block size and height, as in scene.py
RAKE_GAP = 0.12       # rake head to block face, as in scene.py (was 0.07)
EDGE = 8              # pixels a block must keep clear of the frame edge
LON0, LAT0, KX, KY = 5.95, 50.18, 7.15, 11.12
def XY(ll): return np.array([(ll[0] - LON0) * KX, (ll[1] - LAT0) * KY])
def load_cam(f):
    # frame pixel coordinates whichever camera wrote the file (the padded one is shifted back by its pad)
    c = json.load(open(f)); P = np.array(c['P']); RX, RY = c['RX'], c['RY']; px, py = c.get('PADX', 0), c.get('PADY', 0)
    def proj(x, y, z=0.0):
        v = P @ np.array([x, y, z, 1.0]); n = v[:3] / v[3]
        return np.array([(n[0] + 1) / 2 * RX - px, (1 - n[1]) / 2 * RY - py]), v[3]
    return proj, px, py
proj, _, _ = load_cam(f'{D}/cam.json')
_, PADX, PADY = load_cam(f'{D}/campad.json')
def rd(p, alpha=False):
    im = cv2.imread(p, cv2.IMREAD_UNCHANGED).astype(np.float32) / 65535.0
    im = im[..., [2, 1, 0, 3]] if im.shape[2] == 4 else im[..., ::-1]
    return im
PC = {p['id']: p for p in DAY['pieces']}

# ---------- pre render check: every block whole and inside the frame wherever it sits ----------
def block_box(xy, z=1.035, cx=560, cy=900):
    # screen box of a block at map spot xy, at the push in zoom z (worst case is the end of the clip)
    pts = []
    for dx in (-BS / 2, BS / 2):
        for dy in (-BS / 2, BS / 2):
            for dz in (0.0, BH):
                q = proj(xy[0] + dx, xy[1] + dy, dz)[0]; pts.append([cx + z * (q[0] - cx), cy + z * (q[1] - cy)])
    pts = np.array(pts); return pts.min(0), pts.max(0)
def check_frame():
    bad = []
    for pid, p in PC.items():
        spots = [] if p.get('move') == 'arrive' else [('starts', p['from'])]  # an arriving block slides in from the edge on purpose
        if 'to' in p: spots.append(('ends', p['to']))
        for what, ll in spots:
            lo, hi = block_box(XY(ll))
            if lo[0] < EDGE or lo[1] < EDGE or hi[0] > W - EDGE or hi[1] > H - EDGE:
                bad.append(f"{p.get('label', pid)} {what} partly off screen (box {lo.round().astype(int).tolist()} to {hi.round().astype(int).tolist()})")
    if bad:
        print('REFUSED, fix the record before rendering:'); [print('  ' + b) for b in bad]; sys.exit(2)
    print('CHECK OK: every block inside the frame')
check_frame()
if ARG3 == 'check': sys.exit(0)

plate = rd(f'{D}/plate.png')[..., :3]
platepad = rd(f'{D}/platepad.png')[..., :3]

class Sprite:
    def __init__(self, full, mask, base, anchor, project, xoff=PADX, yoff=PADY):
        al = full[..., 3]; ys, xs = np.where(al > 0.5)
        y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
        f = full[y0:y1, x0:x1, :3]; b = base[y0:y1, x0:x1, :3] if base is not None else None
        m = mask[y0:y1, x0:x1]; a = m[..., 3:4]; C = m[..., :3]
        r = np.clip(f / np.maximum(b, 1e-3), 0.15, 1.6)
        valid = (cv2.erode((m[..., 3] < 0.003).astype(np.uint8), np.ones((5, 5), np.uint8)) > 0).astype(np.float32)[..., None]
        num = cv2.GaussianBlur(r * valid, (0, 0), 3); den = cv2.GaussianBlur(valid[..., 0], (0, 0), 3)[..., None]
        r = np.where(valid > 0, r, num / np.maximum(den, 1e-4)); r = np.where(den > 1e-4, r, 1.0)
        dev = np.abs(r - 1).max(axis=2, keepdims=True); k = np.clip((dev - 0.012) / 0.03, 0, 1)
        r = 1 + (r - 1) * k
        hh, ww = r.shape[:2]; e = 14
        fy = np.clip(np.minimum(np.arange(hh), hh - 1 - np.arange(hh)) / e, 0, 1)[:, None]; fx = np.clip(np.minimum(np.arange(ww), ww - 1 - np.arange(ww)) / e, 0, 1)[None, :]
        r = 1 + (r - 1) * (fy * fx)[..., None]
        self.r, self.a, self.C = r.astype(np.float32), a.astype(np.float32), C.astype(np.float32)
        self.o = np.array([x0 - xoff, y0 - yoff], float)  # crop origin in frame pixels (sprites carry a pad)
        self.A, self.wA = project(*anchor)
    def draw(self, F, Q, project=proj):
        q, wq = project(*Q); s = self.wA / wq
        # map crop pixel u -> frame: q + s*(o + u - A)
        tl = q + s * (self.o - self.A); hh, ww = self.r.shape[:2]
        X0, Y0 = int(math.floor(tl[0])), int(math.floor(tl[1])); Wd, Hd = int(ww * s) + 3, int(hh * s) + 3
        M = np.array([[s, 0, tl[0] - X0], [0, s, tl[1] - Y0]], np.float32)
        st = np.concatenate([self.r - 1, self.a, self.C], axis=2)
        out = cv2.warpAffine(st, M, (Wd, Hd), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=0)
        r, a, C = out[..., :3] + 1, out[..., 3:4], out[..., 4:7]
        fx0, fy0 = max(0, X0), max(0, Y0); fx1, fy1 = min(W, X0 + Wd), min(H, Y0 + Hd)
        if fx1 <= fx0 or fy1 <= fy0: return
        sl = (slice(fy0 - Y0, fy1 - Y0), slice(fx0 - X0, fx1 - X0))
        R = F[fy0:fy1, fx0:fx1]
        F[fy0:fy1, fx0:fx1] = R * r[sl] * (1 - a[sl]) + C[sl]

spr = {}
for pid, p in PC.items():
    spr[pid] = Sprite(rd(f'{D}/{S}/blk-{pid}.png'), rd(f'{D}/{S}/msk-{pid}.png'), platepad, (*XY(p['from']), 0.0), proj)
rakeA = XY(PC['5pz']['to']) + [BS / 2 + RAKE_GAP, 0]
rake = Sprite(rd(f'{D}/{S}/blk-rake.png'), rd(f'{D}/{S}/msk-rake.png'), platepad, (*rakeA, 0.0), proj)

def ease(x): x = min(1, max(0, x)); return 4 * x ** 3 if x < 0.5 else 1 - (-2 * x + 2) ** 3 / 2
ENTER, MOVE, HOLD, EXIT = 0.8, 1.9, 0.25, 0.75
PUSH = [{'id': '6pz', 't0': 2.0}, {'id': '5pz', 't0': 5.65}, {'id': '7a', 't0': 9.3}]
T_OPEN, T_X, T_END, T_TONIGHT = 1.1, 0.4, 17.5, 14.6

def piece_pos(pid, t):
    p = PC[pid]; a = XY(p['from'])
    if 'to' not in p: return a
    ps = next(x for x in PUSH if x['id'] == pid); k = ease((t - ps['t0'] - ENTER) / MOVE)
    return a + (XY(p['to']) - a) * k
def rake_pos(t):
    for ps in PUSH:
        lt = t - ps['t0']
        if 0 <= lt < ENTER + MOVE + HOLD + EXIT:
            bp = piece_pos(ps['id'], t); c = bp + [BS / 2 + RAKE_GAP, 0]
            if lt < ENTER: return c + [9.0 * (1 - ease(lt / ENTER)) ** 1.0, 0]
            if lt < ENTER + MOVE + HOLD: return c
            return c + [9.0 * ease((lt - ENTER - MOVE - HOLD) / EXIT), 0]
    return None
def rake_target(t):
    # the block the rake is working at time t, or None
    for ps in PUSH:
        if 0 <= t - ps['t0'] < ENTER + MOVE + HOLD + EXIT: return ps['id']
    return None
LAM, LPM = np.array(DAY['lineAM']), np.array(DAY['linePM'])
def line_pts(t):
    pts = []
    for am, pm in zip(LAM, LPM):
        lat = am[1]; i = 0 if lat > 50.32 else (1 if lat > 50.0 else 2)
        k = ease((t - PUSH[i]['t0'] - ENTER - MOVE * 0.55) / 1.1); pts.append(XY(am + (pm - am) * k))
    return np.array(pts)
def catmull(P, n=14):
    P = np.vstack([P[0], P, P[-1]]); out = []
    for i in range(1, len(P) - 2):
        p0, p1, p2, p3 = P[i - 1], P[i], P[i + 1], P[i + 2]
        for tt in np.linspace(0, 1, n, endpoint=False):
            t2, t3 = tt * tt, tt * tt * tt
            out.append(0.5 * ((2 * p1) + (-p0 + p2) * tt + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t2 + (-p0 + 3 * p1 - 3 * p2 + p3) * t3))
    out.append(P[-2]); return np.array(out)
# ---------- grease pencil on the acetate (lies flat on the map, under the blocks) ----------
SS = 2
_rng = np.random.default_rng(5)
GRAIN = cv2.GaussianBlur(_rng.standard_normal((H, W)).astype(np.float32), (0, 0), 1.8)
GRAIN = (GRAIN - GRAIN.mean()) / GRAIN.std()
WAX = np.array([0.60, 0.09, 0.07], np.float32)
def screen(P):
    return np.array([proj(x, y, 0.0)[0] for x, y in P])
def jitter(c, seed):
    r = np.random.default_rng(seed); n = len(c)
    off = cv2.GaussianBlur(r.standard_normal((n, 1)).astype(np.float32), (0, 0), 6)[:, 0] * 0.02
    d = np.gradient(c, axis=0); nrm = np.stack([-d[:, 1], d[:, 0]], 1); nrm /= np.maximum(np.linalg.norm(nrm, axis=1, keepdims=True), 1e-6)
    return c + nrm * off[:, None]
def stroke_mask(pp, th):
    m = np.zeros((H * SS, W * SS), np.uint8)
    if len(pp) >= 2: cv2.polylines(m, [np.round(pp * SS * 16).astype(np.int32)], False, 255, int(th * SS), cv2.LINE_AA, shift=4)
    return cv2.resize(m, (W, H), interpolation=cv2.INTER_AREA).astype(np.float32) / 255
def wax_alpha(m):
    # waxy, slightly broken grease pencil: grain thins the stroke, a few dropouts
    a = m * np.clip(0.90 + 0.12 * GRAIN, 0, 1); a *= np.clip((GRAIN + 2.7) / 0.8, 0, 1); return a[..., None]
def paint(F, a, col=WAX):
    F[:] = F * (1 - a) + col * a
    sheen = a * np.clip(GRAIN[..., None] - 1.2, 0, 1) * 0.35; F[:] = F + sheen
AMc = jitter(catmull(np.array([XY(p) for p in DAY['lineAM']]), 24), 1)
PMc = jitter(catmull(np.array([XY(p) for p in DAY['linePM']]), 24), 2)
AMs, PMs = screen(AMc), screen(PMc)
AM_A = wax_alpha(stroke_mask(AMs, 7))
GHOST_A = cv2.GaussianBlur(AM_A[..., 0], (0, 0), 1.6)[..., None] * 0.28
seglen = np.r_[0, np.cumsum(np.linalg.norm(np.diff(PMs, axis=0), axis=1))]; TOT = seglen[-1]
def pm_partial(f):
    L = f * TOT; k = np.searchsorted(seglen, L)
    if k <= 0: return PMs[:1]
    if k >= len(PMs): return PMs
    u = (L - seglen[k - 1]) / max(seglen[k] - seglen[k - 1], 1e-6)
    return np.vstack([PMs[:k], PMs[k - 1] + (PMs[k] - PMs[k - 1]) * u])
# ground taken today: between the morning and evening lines, hatched in charcoal on the acetate
poly = np.vstack([AMs, PMs[::-1]])
gm = np.zeros((H * SS, W * SS), np.uint8); cv2.fillPoly(gm, [np.round(poly * SS * 16).astype(np.int32)], 255, cv2.LINE_AA, shift=4)
GAIN = cv2.resize(gm, (W, H), interpolation=cv2.INTER_AREA).astype(np.float32) / 255
hm = np.zeros((H * SS, W * SS), np.uint8)
for c0 in np.arange(-12, 12, 0.16):
    p0, p1 = proj(c0 - 6, -6, 0)[0], proj(c0 + 6, 6, 0)[0]
    cv2.line(hm, tuple(np.round(p0 * SS * 16).astype(int)), tuple(np.round(p1 * SS * 16).astype(int)), 255, 2 * SS, cv2.LINE_AA, shift=4)
HATCH = cv2.resize(hm, (W, H), interpolation=cv2.INTER_AREA).astype(np.float32) / 255
SHADE_A = (GAIN * (0.10 + 0.22 * HATCH) * np.clip(0.85 + 0.2 * GRAIN, 0, 1))[..., None]
SHADE = np.array([0.20, 0.21, 0.23], np.float32)
T_WIPE, T_DRAW, DRAW_LEN, T_SHADE = 13.0, 13.5, 1.5, 14.4
def grease(F, t):
    if t < T_WIPE: paint(F, AM_A); return
    k = ease((t - T_WIPE) / 0.5); paint(F, AM_A * (1 - k) + GHOST_A * k)
    if t >= T_SHADE: F[:] = F * (1 - SHADE_A * ease((t - T_SHADE) / 0.9)) + SHADE * SHADE_A * ease((t - T_SHADE) / 0.9)
    if t >= T_DRAW:
        f = min(1.0, (t - T_DRAW) / DRAW_LEN); f = f * f * (3 - 2 * f)
        paint(F, wax_alpha(stroke_mask(pm_partial(f), 7)))

def load_rgba(p):
    im = cv2.imread(p, cv2.IMREAD_UNCHANGED).astype(np.float32) / 255; return np.concatenate([im[..., [2, 1, 0]], im[..., 3:4]], axis=2)
TAB, SA, SB = load_rgba(f'{D}/ov/tab.png'), load_rgba(f'{D}/ov/stripA.png'), load_rgba(f'{D}/ov/stripB.png')
OPEN = load_rgba(f'{D}/ov/opener.png')[..., :3]; OPEN_BG = load_rgba(f'{D}/ov/openbg.png')[..., :3]; OPEN_OV = load_rgba(f'{D}/ov/openov.png')
def over(F, L, k=1.0): a = L[..., 3:4] * k; F[:] = F * (1 - a) + L[..., :3] * a
def zoom(F, z, cx=540, cy=960):
    M = np.array([[z, 0, cx - z * cx], [0, z, cy - z * cy]], np.float32); return cv2.warpAffine(F, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)

def table(t, ov=True):
    F = plate.copy(); grease(F, t)
    order = sorted(PC, key=lambda pid: -XY(PC[pid]['from'])[1])
    rp, rt = rake_pos(t), rake_target(t)
    for pid in order:
        if pid == rt and rp is not None: rake.draw(F, (*rp, 0.0))  # rake first, so its block sits over the head
        spr[pid].draw(F, (*piece_pos(pid, t), 0.0))
    F = zoom(F, 1.0 + 0.035 * min(1, max(0, (t - T_OPEN) / (T_END - T_OPEN))), 560, 900)
    if not ov: return F
    over(F, TAB)
    kb = min(1, max(0, (t - T_TONIGHT) / 0.35)); over(F, SA, 1 - kb); over(F, SB, kb)
    return F
def frame(t):
    if t < T_OPEN: return zoom(OPEN.copy(), 1.0 + 0.02 * t / (T_OPEN + T_X))
    if t < T_OPEN + T_X:
        k = ease((t - T_OPEN) / T_X); bg = zoom(OPEN_BG.copy(), 1.0 + 0.02 * t / (T_OPEN + T_X)) * (1 - k) + table(t, False) * k
        if t < T_OPEN + T_X / 2: over(bg, OPEN_OV)
        else: over(bg, TAB); over(bg, SA)
        return bg
    return table(t)
if ONLY:
    for t in ONLY:
        cv2.imwrite(f'{D}/check-{t:05.2f}.png', (np.clip(frame(t), 0, 1)[..., ::-1] * 255).astype(np.uint8)); print('wrote', t)
    sys.exit(0)
n = int(T_END * FPS)
ff = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                       '-c:v', 'libx264', '-crf', '18', '-preset', 'veryfast', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', OUT + '.tmp.mp4'], stdin=subprocess.PIPE)
for i in range(n):
    ff.stdin.write((np.clip(frame(i / FPS), 0, 1) * 255 + 0.5).astype(np.uint8).tobytes())
ff.stdin.close(); ff.wait()
import os; os.replace(OUT + '.tmp.mp4', OUT); print('OK', OUT)
