"""One contact sheet per series: every day's table at nightfall, drawn flat and fast (no Blender), for Brian and the
Campaign Series chat to review straight after the build sitting, before anything is rendered.
Each tile shows the day's view as the camera sees it: the map, the morning line faint, the night line red, pockets, the
blocks where they stand at night in nation colors with their labels, the tab and strip areas shaded, and any check errors.
Usage: contact_sheet.py <series folder or day files ...> <out.png>"""
import sys, os, json, glob, subprocess
import numpy as np, cv2
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import day as D
from PIL import Image, ImageDraw, ImageFont
import placeholder_map
W, H = D.W, D.H
OSW = os.path.join(HERE, '..', 'fonts', 'oswald700.ttf'); ELITE = os.path.join(HERE, '..', 'fonts', 'special-elite.ttf')
HEX = {k: tuple(int(v.lstrip('#')[i:i + 2], 16) for i in (0, 2, 4)) for k, v in D.LIB['colors'].items()}
Hs = np.array(D.homography())

def map_image(d, table, vname, cache):
    traced = os.path.join(HERE, '..', 'series', str(d.rec.get('campaign')), 'maps', f'{vname}.png')
    if os.path.exists(traced): return cv2.imread(traced)
    p = os.path.join(cache, f'{d.rec.get("campaign")}-{vname}-placeholder.png')
    if not os.path.exists(p): placeholder_map.draw(table.path, p)
    return cv2.imread(p)
def tile(d, cache):
    vname = d.view or 'main'; m = map_image(d, d.table, vname, cache)
    ppu = m.shape[1] / D.TW; C = np.array([[1 / ppu, 0, -D.TW / 2], [0, -1 / ppu, D.TH / 2], [0, 0, 1]])
    F = cv2.warpPerspective(m, Hs @ C, (W, H), borderValue=(20, 16, 12))
    im = Image.fromarray(np.ascontiguousarray(F[..., ::-1])); dr = ImageDraw.Draw(im, 'RGBA')   # RGB base, so translucent fills blend
    bz = D.TPL['block_zone']
    dr.rectangle([0, 0, W, bz['top']], fill=(0, 0, 0, 90)); dr.rectangle([0, bz['bottom'], W, H], fill=(0, 0, 0, 90))
    dr.rectangle([bz['right'], 0, W, H], fill=(0, 0, 0, 60))
    def scr(ll): return D.proj(*d.table.XY(ll), 0.0)[0]
    for key, col, wd in (('lineAM', (150, 40, 30, 110), 4), ('linePM', (180, 25, 20, 255), 7)):
        dr.line([scr(p) for p in d.mr[key]], fill=col, width=wd, joint='curve')
    for pk in d.mr.get('pocketsPM', []):
        r = [scr(p) for p in pk['ring']]; dr.line(r + [r[0]], fill=(180, 25, 20, 255), width=6)
    f = ImageFont.truetype(OSW, int(26 * D.BS / 1.35))
    for p in d.pieces:
        xy = d.rest_to(p)
        if xy is None: continue   # surrendered: gone by night
        q = [D.proj(xy[0] + dx, xy[1] + dy, D.BH)[0] for dx, dy in ((-D.BS / 2, -D.BS / 2), (D.BS / 2, -D.BS / 2), (D.BS / 2, D.BS / 2), (-D.BS / 2, D.BS / 2))]
        dr.polygon(q, fill=HEX[p['nation']] + (255,), outline=(240, 232, 212, 255))
        cx = sum(x for x, _ in q) / 4; cy = sum(y for _, y in q) / 4
        tag = {'cut_off': ' (cut off)', 'grounded': ' (grounded)'}.get(p['move'], '')
        dr.text((cx, cy), p['label'].upper() + tag, font=f, fill=(240, 232, 212, 255), anchor='mm')
    return im

def main(args):
    out = args[-1]; files = []
    for a in args[:-1]: files += sorted(glob.glob(os.path.join(a, 'day-*.json'))) if os.path.isdir(a) else [a]
    cache = os.path.join(os.path.dirname(os.path.abspath(out)), '.sheet-cache'); os.makedirs(cache, exist_ok=True)
    tw, th, cols = 360, 640, 6; rows = (len(files) + cols - 1) // cols
    sheet = Image.new('RGB', (cols * tw, rows * (th + 110)), (14, 12, 10)); dr = ImageDraw.Draw(sheet)
    fh = ImageFont.truetype(OSW, 22); fs = ImageFont.truetype(ELITE, 17)
    for i, fpath in enumerate(files):
        x, y = (i % cols) * tw, (i // cols) * (th + 110)
        chk = subprocess.run([sys.executable, os.path.join(HERE, 'check_record.py'), fpath], capture_output=True, text=True)
        errs = [l.strip()[6:] for l in chk.stdout.splitlines() if l.strip().startswith('ERROR')]
        try:
            d = D.Day(fpath); sheet.paste(tile(d, cache).resize((tw - 10, th - 10)), (x + 5, y + 5))
            head = f"DAY {d.rec.get('day', '?')} · {d.rec.get('date', '')} · {(d.view or 'whole battle').upper()} · {d.T:.0f} S"
            dr.text((x + 8, y + th + 4), head, font=fh, fill=(240, 232, 212))
            dr.text((x + 8, y + th + 42), d.rec.get('subtitle', '')[:38], font=fs, fill=(220, 210, 190))
        except Exception as e:
            errs = errs or [str(e)]
        if errs:
            dr.rectangle([x + 5, y + 5, x + tw - 5, y + th - 5], outline=(220, 40, 30), width=6)
            real = [e for e in errs if 'placeholder' not in e] or errs
            dr.text((x + 8, y + th + 66), f'{len(errs)} ERRORS', font=fs, fill=(240, 90, 80))
            dr.text((x + 8, y + th + 86), real[0][:44], font=fs, fill=(240, 90, 80))
    sheet.save(out); print('wrote', out, f'{len(files)} days')
if __name__ == '__main__': main(sys.argv[1:])
