"""The key card (Brian, 21 Nov 2026): a cream index card lying on the table in the balcony shot on a series' opening
days, so new viewers learn the board. It builds itself from the series: the nations on the roster, the red front line,
black dashes only if the series has air missions, the size of a block, and a north mark.
It is a table object: placed once per clip, in the largest clear space of the balcony view (inside the safe area,
clear of the tab, the strip, every block and the front line, morning and night, and as clear of town names as it can
be), then carried by the camera like the map under it, so it slides out of view as the camera comes down."""
import os, json, math
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont, ImageFilter
HERE = os.path.dirname(os.path.abspath(__file__))
FONTS = os.path.join(HERE, '..', 'fonts')
LIB = json.load(open(os.path.join(HERE, '..', 'kit', 'silhouettes', 'library.json')))
NAMES = {'us': 'UNITED STATES', 'britain': 'BRITAIN', 'soviet': 'SOVIET UNION', 'germany': 'GERMANY', 'japan': 'JAPAN'}
ORDER = ['us', 'britain', 'soviet', 'germany', 'japan']
CW, CH = 600, 172                  # card size in frame pixels at the balcony, before any shrink
SS = 3                             # drawn at 3x, so it stays sharp as the camera comes down
INK = (52, 42, 32, 255)

def hexc(h): h = h.lstrip('#'); return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))

def make(nations, air, title, block_km):
    """the card as an RGBA float image at SS times its balcony size"""
    nations = [n for n in ORDER if n in nations]
    W, H = CW * SS, CH * SS
    im = Image.new('RGBA', (W, H), (239, 230, 210, 255))
    rng = np.random.default_rng(4); g = (rng.normal(0, 1, (H, W)) * 6).clip(-12, 12)
    a = np.asarray(im).astype(float); a[..., :3] += g[..., None]; im = Image.fromarray(a.clip(0, 255).astype(np.uint8)); d = ImageDraw.Draw(im)
    for y in range(52, CH, 30): d.line([0, y * SS, W, y * SS], fill=(170, 190, 210, 255), width=SS)      # index card rules
    d.line([0, 40 * SS, W, 40 * SS], fill=(196, 92, 82, 255), width=2 * SS)                                # red header rule
    osw = lambda s: ImageFont.truetype(os.path.join(FONTS, 'oswald700.ttf'), int(s * SS))
    sp = lambda s: ImageFont.truetype(os.path.join(FONTS, 'special-elite.ttf'), int(s * SS))
    d.text((18 * SS, 20 * SS), 'KEY', font=osw(22), fill=INK, anchor='lm')
    d.text((W - 18 * SS, 20 * SS), title.upper(), font=sp(17), fill=INK, anchor='rm')
    # nations: one row, spaced by their name lengths; a smaller face if a long roster would not fit
    f = 21
    while True:
        widths = [30 + d.textlength(NAMES[n], font=sp(f)) / SS for n in nations]
        if sum(widths) + 26 * (len(nations) - 1) <= CW - 36 or f <= 15: break
        f -= 1
    x, y = 18, 68
    for n, w in zip(nations, widths):
        d.rectangle([x * SS, (y - 11) * SS, (x + 22) * SS, (y + 11) * SS], fill=hexc(LIB['colors'][n]) + (255,), outline=(60, 40, 25, 255), width=2 * SS)
        d.text(((x + 30) * SS, y * SS), NAMES[n], font=sp(f), fill=INK, anchor='lm'); x += w + 26
    y = 102
    d.line([18 * SS, y * SS, 70 * SS, y * SS], fill=(153, 23, 18, 255), width=4 * SS)
    d.text((80 * SS, y * SS), 'FRONT LINE', font=sp(21), fill=INK, anchor='lm')
    if air:
        for x in range(270, 322, 13): d.line([x * SS, y * SS, (x + 8) * SS, y * SS], fill=(25, 22, 22, 255), width=4 * SS)
        d.text((330 * SS, y * SS), 'AIR MISSION', font=sp(21), fill=INK, anchor='lm')
    y = 136
    d.rectangle([18 * SS, (y - 11) * SS, 40 * SS, (y + 11) * SS], outline=(60, 40, 25, 255), width=2 * SS)
    d.text((50 * SS, y * SS), f'ONE BLOCK = {block_km:g} KM', font=sp(21), fill=INK, anchor='lm')
    nx = CW - 40
    d.polygon([(nx * SS, (y - 22) * SS), ((nx - 9) * SS, (y + 12) * SS), (nx * SS, (y + 5) * SS), ((nx + 9) * SS, (y + 12) * SS)], fill=INK)
    d.text(((nx - 24) * SS, (y - 4) * SS), 'N', font=osw(22), fill=INK, anchor='mm')
    return np.asarray(im).astype(np.float32) / 255

def place(Wf, Hf, hard, soft, top, bottom, left, right, angle=1.8):
    """the clear spot for the card at the balcony: corners in frame pixels, or None if it fits nowhere.
    hard: 0/1 mask the card must not touch (blocks, the line, tab, strip); soft: 0/1 mask to cover as little as
    possible (town names). Tries the full size, then 90% and 80%."""
    hard_d = cv2.dilate(hard.astype(np.uint8), np.ones((15, 15), np.uint8))
    best = None
    for s in (1.0, 0.9, 0.8):
        w, h = CW * s, CH * s
        c, sn = math.cos(math.radians(angle)), math.sin(math.radians(angle))
        def corners(cx, cy):
            return np.array([[cx + dx * c - dy * sn, cy + dx * sn + dy * c] for dx, dy in ((-w / 2, -h / 2), (w / 2, -h / 2), (w / 2, h / 2), (-w / 2, h / 2))], np.float32)
        hw, hh = w / 2 + 6, h / 2 + 10
        for cy in np.arange(top + hh, bottom - hh, 8):
            for cx in np.arange(left + hw, right - hw, 8):
                Q = corners(cx, cy); m = np.zeros((Hf, Wf), np.uint8); cv2.fillConvexPoly(m, Q.astype(np.int32), 1)
                if (m & hard_d).any(): continue
                cost = float((m & soft).sum())
                if best is None or cost < best[0]: best = (cost, Q)
        if best is not None: return best[1]
    return None

def draw(F, card, Q, alpha=1.0):
    """lay the card on frame F (float RGB) with its corners at Q (frame pixels), with a soft shadow under it"""
    h, w = card.shape[:2]; src = np.array([[0, 0], [w, 0], [w, h], [0, h]], np.float32)
    x0, y0 = np.floor(Q.min(0)).astype(int) - 30; x1, y1 = np.ceil(Q.max(0)).astype(int) + 30
    X0, Y0, X1, Y1 = max(0, x0), max(0, y0), min(F.shape[1], x1), min(F.shape[0], y1)
    if X1 <= X0 or Y1 <= Y0: return
    side = float(np.linalg.norm(Q[1] - Q[0]))
    M = cv2.getPerspectiveTransform(src, (Q - [X0, Y0]).astype(np.float32))
    wp = cv2.warpPerspective(card, M, (X1 - X0, Y1 - Y0), flags=cv2.INTER_AREA if side < w else cv2.INTER_LINEAR, borderValue=0)
    sh = np.zeros((Y1 - Y0, X1 - X0), np.float32); off = side / CW
    cv2.fillConvexPoly(sh, (Q - [X0, Y0] + [7 * off, 9 * off]).astype(np.int32), 1.0, cv2.LINE_AA)
    sh = cv2.GaussianBlur(sh, (0, 0), max(1.0, 7 * off))[..., None] * 0.45 * alpha
    R = F[Y0:Y1, X0:X1]; R[:] = R * (1 - sh) + np.array([0.16, 0.11, 0.07], np.float32) * sh
    a = wp[..., 3:4] * alpha; R[:] = R * (1 - a) + wp[..., :3] * a
