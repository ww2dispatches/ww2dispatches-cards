"""Draw a view's table map from the series geography (step 4): parchment, sea, borders, rivers, roads, towns and
country names, over exactly the view's table area, so blocks and lines land on the right ground.
Geography lives in series/<campaign>/geo/: rivers.json and roads.json traced from the situation maps, borders.json
from Natural Earth, towns.json (positions and the widest view each town is named in).
Usage: draw_map.py <campaign> <view> [out.png]   (view: main, opening, salient, bastogne)"""
import sys, os, json, math
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); import day
FONT = os.path.join(HERE, '..', 'fonts', 'special-elite.ttf')
FONT_BIG = os.path.join(HERE, '..', 'fonts', 'oswald700.ttf')
PPU = 300
PAPER, SEA = (226, 206, 160), (196, 196, 172)
INK, RIVER, ROAD, BORDER = (52, 42, 32), (78, 104, 124), (150, 118, 78), (110, 70, 52)
BIG_RIVERS = {'Meuse', 'Rhine', 'Moselle'}

def table_for(campaign, view):
    f = 'table.json' if view == 'main' else f'table-{view}.json'
    return day.Table(os.path.join(HERE, '..', 'series', campaign, f))

def draw(campaign, view, out=None):
    G = os.path.join(HERE, '..', 'series', campaign, 'geo')
    t = table_for(campaign, view); Wp, Hp = int(day.TW * PPU), int(day.TH * PPU)
    span = t.lon_max - t.lon_min
    def px(ll):
        x, y = t.XY(ll); return ((x + day.TW / 2) * PPU, (day.TH / 2 - y) * PPU)
    def line(d, pl, fill, w, dash=None):
        P = [px(p) for p in pl]
        if not dash: d.line(P, fill=fill, width=int(w), joint='curve'); return
        on, off = dash; acc, draw_on = 0.0, True
        for a, b in zip(P, P[1:]):
            L = math.dist(a, b); s = 0.0
            while s < L:
                step = min((on if draw_on else off) - acc, L - s)
                if draw_on:
                    p0 = (a[0] + (b[0] - a[0]) * s / L, a[1] + (b[1] - a[1]) * s / L)
                    p1 = (a[0] + (b[0] - a[0]) * (s + step) / L, a[1] + (b[1] - a[1]) * (s + step) / L)
                    d.line([p0, p1], fill=fill, width=int(w))
                s += step; acc += step
                if acc >= (on if draw_on else off) - 1e-6: acc, draw_on = 0.0, not draw_on
    borders = json.load(open(os.path.join(G, 'borders.json')))
    im = Image.new('RGB', (Wp, Hp), SEA); d = ImageDraw.Draw(im)
    for ring in borders['land']:
        if len(ring) > 2: d.polygon([px(p) for p in ring], fill=PAPER)
    # paper grain, so the table is not a flat fill
    rng = np.random.default_rng(7)
    grain = Image.fromarray((rng.normal(0, 1, (Hp // 6, Wp // 6)) * 255).clip(-255, 255).astype(np.int16).clip(0, 255).astype(np.uint8))
    grain = grain.resize((Wp, Hp), Image.BICUBIC).filter(ImageFilter.GaussianBlur(3))
    g = (np.asarray(grain, np.float32) / 255 - 0.5) * 10
    im = Image.fromarray((np.asarray(im, np.float32) + g[..., None]).clip(0, 255).astype(np.uint8)); d = ImageDraw.Draw(im)
    # graticule, faint
    step = 1.0 if span > 3 else (0.5 if span > 1.5 else 0.25)
    lo = math.floor(t.lon_min / step) * step
    while lo <= t.lon_max + step:
        line(d, [(lo, la) for la in np.linspace(t.lat_min - 1, t.lat_max + 1, 40)], (206, 184, 138), 0.012 * PPU); lo += step
    la = math.floor(t.lat_min / step) * step
    while la <= t.lat_max + step:
        line(d, [(lo2, la) for lo2 in np.linspace(t.lon_min - 1, t.lon_max + 1, 40)], (206, 184, 138), 0.012 * PPU); la += step
    for c in borders['coast']: line(d, c, (120, 120, 100), 0.03 * PPU)
    if os.path.exists(os.path.join(G, 'roads.json')) and span < 3.2:
        for name, pl in json.load(open(os.path.join(G, 'roads.json')))['roads'].items():
            line(d, pl, ROAD, (0.05 if span < 1.5 else 0.035) * PPU)
    for b in borders['borders']: line(d, b, BORDER, 0.035 * PPU, dash=(0.16 * PPU, 0.07 * PPU))
    for name, pl in json.load(open(os.path.join(G, 'rivers.json')))['rivers'].items():
        w = (0.075 if name in BIG_RIVERS else 0.045) * (1.4 if span < 1.5 else 1.0)
        line(d, pl, RIVER, w * PPU)
    # country names, large and faint, at fixed anchors; skipped when the anchor is off the table
    names = {'BELGIUM': (4.75, 50.62), 'GERMANY': (7.05, 50.25), 'FRANCE': (4.6, 49.35), 'LUXEMBOURG': (6.1, 49.73),
             'NETHERLANDS': (5.6, 51.55)}
    if span < 1.5: names = {'BELGIUM': (5.42, 50.18), 'LUXEMBOURG': (5.98, 49.80), 'GERMANY': (6.10, 50.30)}
    lay = Image.new('RGBA', im.size, (0, 0, 0, 0)); ld = ImageDraw.Draw(lay)
    fb = ImageFont.truetype(FONT_BIG, int(0.55 * PPU))
    for n, ll in names.items():
        if not t.on_table(ll): continue
        x, y = px(ll); ld.text((x, y), ' '.join(n), font=fb, fill=(120, 92, 60, 70), anchor='mm')
    im = Image.alpha_composite(im.convert('RGBA'), lay).convert('RGB'); d = ImageDraw.Draw(im)
    # towns: a dot and a name, most important first; a name that would sit on another is dropped
    towns = json.load(open(os.path.join(G, 'towns.json')))['towns']
    f = ImageFont.truetype(FONT, int(0.26 * PPU)); boxes = []
    def hits(b): return any(b[0] < c[2] and c[0] < b[2] and b[1] < c[3] and c[1] < b[3] for c in boxes)
    for tw in sorted(towns, key=lambda q: -q['span']):
        ll = (tw['lon'], tw['lat'])
        if span > tw['span'] + 1e-9 or not t.on_table(ll): continue
        x, y = px(ll); r = 0.065 * PPU; label = tw['name'].upper()
        dot = (x - r * 1.6, y - r * 1.6, x + r * 1.6, y + r * 1.6)
        if hits(dot): continue
        wtx = d.textlength(label, font=f); h = 0.26 * PPU
        for ox, oy, anc in ((r * 1.8, 0, 'lm'), (-r * 1.8, 0, 'rm'), (0, -r * 1.6 - h / 2, 'mm'), (0, r * 1.6 + h / 2, 'mm')):
            lx, ly = x + ox, y + oy
            bx = {'lm': (lx, ly - h / 2, lx + wtx, ly + h / 2), 'rm': (lx - wtx, ly - h / 2, lx, ly + h / 2),
                  'mm': (lx - wtx / 2, ly - h / 2, lx + wtx / 2, ly + h / 2)}[anc]
            if not hits(bx) and 0 <= bx[0] and bx[2] <= Wp and 0 <= bx[1] and bx[3] <= Hp: break
        else: continue
        boxes += [dot, bx]
        d.ellipse([x - r, y - r, x + r, y + r], fill=INK)
        d.text((lx, ly), label, font=f, fill=INK, anchor=anc)
    out = out or os.path.join(HERE, '..', 'series', campaign, 'maps', f'{view}.png')
    os.makedirs(os.path.dirname(out), exist_ok=True); im.save(out); print('wrote', os.path.relpath(out)); return out

if __name__ == '__main__':
    draw(sys.argv[1], sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else None)
