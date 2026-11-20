"""Block faces from the silhouette kit. Env: MAPROOM_WORK (writes face-<id>.png there), MAPROOM_DAY (day record)."""
import json, sys, os
from PIL import Image, ImageDraw, ImageFont
HERE = os.path.dirname(os.path.abspath(__file__))
K = os.path.join(HERE, '..', 'kit', 'silhouettes') + os.sep
FONT = os.path.join(HERE, '..', 'fonts', 'oswald700.ttf')
D = os.environ.get('MAPROOM_WORK', '.')
lib = json.load(open(K + 'library.json'))
def hexc(h): h = h.lstrip('#'); return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))
CREAM = hexc(lib['colors']['face_ink'])
def sil_file(typ, nation, heavy=False, variant=None):
    """kit file for a block: shared types (artillery, airborne, ships) have one silhouette for every nation"""
    L = lib['library']
    if typ + '_shared' in L: return L[typ + '_shared']['all']
    if typ in L['ship_shared']: return L['ship_shared'][typ]
    return L[typ][nation + ('_special' if heavy else '') + (('_' + variant) if variant else '')]
def load_sil(path):
    """silhouette as an alpha mask: PNGs are cream on transparent; SVGs are drawn in black (white lines are cut seams)"""
    if path.endswith('.svg'):
        import subprocess, io
        png = subprocess.run(['rsvg-convert', '-w', '1200', path], check=True, capture_output=True).stdout
        im = Image.open(io.BytesIO(png)).convert('RGBA'); r, g, b, a = im.split()
        dark = Image.eval(Image.merge('RGB', (r, g, b)).convert('L'), lambda v: 255 - v)
        from PIL import ImageChops
        out = Image.new('RGBA', im.size, (0, 0, 0, 0)); out.putalpha(ImageChops.multiply(a, dark)); return out
    return Image.open(path).convert('RGBA')
def face(nation, typ, label, out, S=800, heavy=False, variant=None):
    im = Image.new('RGB', (S, S), hexc(lib['colors'][nation])); d = ImageDraw.Draw(im)
    m = int(S * 0.045); d.rectangle([m, m, S - m, S - m], outline=CREAM, width=max(4, S // 160))
    sil = load_sil(K + sil_file(typ, nation, heavy, variant)); bb = sil.getbbox(); sil = sil.crop(bb)
    if (typ + '_shared' in lib['library'] or typ in lib['library']['ship_shared']) and nation in ('germany', 'japan'):
        sil = sil.transpose(Image.FLIP_LEFT_RIGHT)   # shared silhouettes face right; Axis blocks face left (the facing rule)
    bw, bh = S * 0.68, S * 0.42; k = min(bw / sil.width, bh / sil.height); sil = sil.resize((int(sil.width * k), int(sil.height * k)), Image.LANCZOS)
    im.paste(Image.new('RGB', sil.size, CREAM), ((S - sil.width) // 2, int(S * 0.50) - sil.height), sil.split()[3])
    t = label.upper(); size = int(S * 0.15)
    while True:
        f = ImageFont.truetype(FONT, size); w = d.textlength(t, font=f)
        if w <= S * 0.80: break
        size -= 2
    d.text((S / 2, S * 0.72), t, font=f, fill=CREAM, anchor='mm')
    im.save(out)
if __name__ == '__main__':
    day = json.load(open(os.environ.get('MAPROOM_DAY', os.path.join(D, 'day01.json'))))
    P = day.get('mapRoom', day)['pieces']   # new day records keep pieces in the mapRoom block; the old test record at top level
    for p in P: face(p['nation'], p['type'], p['label'], os.path.join(D, f"face-{p['id']}.png"), heavy=p.get('heavy', False), variant=p.get('variant'))
