"""A stand in map for a view until the real traced map exists (step 4): parchment, a coordinate grid, and towns at
approximate positions, drawn over exactly the view's table area so blocks and lines land in the right places.
Every copy is watermarked PLACEHOLDER. Never for posting.
Usage: placeholder_map.py <table.json> <out.png>"""
import sys, os, json
from PIL import Image, ImageDraw, ImageFont
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); import day
FONT = os.path.join(HERE, '..', 'fonts', 'special-elite.ttf')
# approximate positions, for layout only (the traced map replaces them)
TOWNS = {'Bastogne': (5.72, 50.00), 'St. Vith': (6.12, 50.28), 'Houffalize': (5.79, 50.13), 'Malmedy': (6.03, 50.43),
         'Stavelot': (5.93, 50.39), 'Spa': (5.87, 50.49), 'Liege': (5.57, 50.63), 'Elsenborn': (6.22, 50.46),
         'Monschau': (6.24, 50.56), 'Clervaux': (6.03, 50.05), 'Wiltz': (5.93, 49.97), 'Echternach': (6.42, 49.81),
         'Diekirch': (6.16, 49.87), 'Luxembourg': (6.13, 49.61), 'Arlon': (5.82, 49.68), 'Marche': (5.35, 50.23),
         'Hotton': (5.45, 50.27), 'La Roche': (5.58, 50.18), 'Celles': (5.01, 50.23), 'Dinant': (4.91, 50.26),
         'Manhay': (5.68, 50.29), 'Vielsalm': (5.92, 50.28), 'Trois Ponts': (5.87, 50.37), 'Martelange': (5.74, 49.83),
         'Namur': (4.87, 50.47), 'Prum': (6.42, 50.21), 'Assenois': (5.70, 49.95), 'Noville': (5.76, 50.06),
         'Longvilly': (5.83, 50.03), 'Sibret': (5.64, 49.97), 'Champs': (5.67, 50.03), 'Mande St. Etienne': (5.66, 50.01)}
PPU = 300   # pixels per table unit

def draw(table_path, out):
    t = day.Table(table_path); Wp, Hp = int(day.TW * PPU), int(day.TH * PPU)
    im = Image.new('RGB', (Wp, Hp), (226, 206, 160)); d = ImageDraw.Draw(im)
    def px(ll):
        x, y = t.XY(ll); return ((x + day.TW / 2) * PPU, (day.TH / 2 - y) * PPU)
    span = t.lon_max - t.lon_min
    step = 0.5 if span > 3 else (0.1 if span > 0.8 else 0.05)
    import math
    lo = math.floor(t.lon_min / step) * step
    while lo <= t.lon_max:
        a, b = px((lo, t.lat_min)), px((lo, t.lat_max)); d.line([a, b], fill=(196, 172, 128), width=3); lo += step
    la = math.floor(t.lat_min / step) * step
    while la <= t.lat_max:
        a, b = px((t.lon_min, la)), px((t.lon_max, la)); d.line([a, b], fill=(196, 172, 128), width=3); la += step
    f = ImageFont.truetype(FONT, int(0.30 * PPU))
    MINOR = {'Assenois', 'Noville', 'Longvilly', 'Sibret', 'Champs', 'Mande St. Etienne'}
    for name, ll in TOWNS.items():
        if not t.on_table(ll) or (name in MINOR and span > 0.8): continue
        x, y = px(ll); r = 0.07 * PPU
        d.ellipse([x - r, y - r, x + r, y + r], fill=(40, 34, 28))
        d.text((x + r * 1.8, y), name.upper(), font=f, fill=(40, 34, 28), anchor='lm')
    wm = Image.new('RGBA', im.size, (0, 0, 0, 0)); wd = ImageDraw.Draw(wm)
    fw = ImageFont.truetype(FONT, int(0.9 * PPU))
    for k in range(-2, 3):
        wd.text((Wp / 2, Hp / 2 + k * 3.2 * PPU), 'PLACEHOLDER MAP, NOT TRACED', font=fw, fill=(150, 40, 30, 70), anchor='mm')
    wm = wm.rotate(28, center=(Wp / 2, Hp / 2))
    im = Image.alpha_composite(im.convert('RGBA'), wm).convert('RGB'); im.save(out); print('wrote', out)
if __name__ == '__main__': draw(sys.argv[1], sys.argv[2])
