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
def face(nation, typ, label, out, S=800):
    im = Image.new('RGB', (S, S), hexc(lib['colors'][nation])); d = ImageDraw.Draw(im)
    m = int(S * 0.045); d.rectangle([m, m, S - m, S - m], outline=CREAM, width=max(4, S // 160))
    sil = Image.open(K + lib['library'][typ][nation]).convert('RGBA'); bb = sil.getbbox(); sil = sil.crop(bb)
    bw, bh = S * 0.68, S * 0.42; k = min(bw / sil.width, bh / sil.height); sil = sil.resize((int(sil.width * k), int(sil.height * k)), Image.LANCZOS)
    im.paste(Image.new('RGB', sil.size, CREAM), ((S - sil.width) // 2, int(S * 0.50) - sil.height), sil.split()[3])
    t = label.upper(); size = int(S * 0.15)
    while True:
        f = ImageFont.truetype(FONT, size); w = d.textlength(t, font=f)
        if w <= S * 0.80: break
        size -= 2
    d.text((S / 2, S * 0.72), t, font=f, fill=CREAM, anchor='mm')
    im.save(out)
P = json.load(open(os.environ.get('MAPROOM_DAY', os.path.join(D, 'day01.json'))))['pieces']
for p in P: face(p['nation'], p['type'], p['label'], os.path.join(D, f"face-{p['id']}.png"))
