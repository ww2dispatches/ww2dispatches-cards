"""Line a situation map scan up with real coordinates. The Twelfth Army Group maps are all printed on the same base
sheet, so a scan is registered by finding four patches of the reference scan (25 Dec 1944, registered from its printed
grid) in it. Writes the result into series.json under maps[date].georef.
Usage: register.py <campaign> <date YYYY-MM-DD>"""
import sys, os, json, subprocess, numpy as np, cv2
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.join(HERE, '..', '..')
CACHE = os.environ.get('MAPROOM_SCANS', os.path.expanduser('~/.cache/maproom-scans'))
IIIF = 'https://tile.loc.gov/image-services/iiif/'
def fetch(iiif, region, size, name):
    os.makedirs(CACHE, exist_ok=True); p = os.path.join(CACHE, name)
    if not os.path.exists(p) or os.path.getsize(p) < 20000:
        subprocess.run(['curl', '-s', '--max-time', '400', '-o', p, f'{IIIF}{iiif}/{region}/{size}/0/default.jpg'], check=True)
    im = cv2.imread(p)
    if im is None: os.remove(p); raise SystemExit(f'could not fetch the scan {iiif} ({region})')
    return im
def register(campaign, date):
    cf = os.path.join(ROOT, 'series', campaign, 'series.json'); cfg = json.load(open(cf)); maps = cfg['maps']
    ref_date = next(d for d, m in maps.items() if m.get('georef', {}).get('by', '').startswith('printed')); R = maps[ref_date]['georef']
    if date == ref_date: return R
    ref = cv2.cvtColor(fetch(maps[ref_date]['iiif'], 'full', 'pct:25', f'{ref_date}-q.jpg'), cv2.COLOR_BGR2GRAY)
    tgt = cv2.cvtColor(fetch(maps[date]['iiif'], 'full', 'pct:25', f'{date}-q.jpg'), cv2.COLOR_BGR2GRAY)
    import math
    def px(lon, lat): return (R['X6'] + (lon - 6) * 111.32 * math.cos(math.radians(lat)) * R['PXKM'], R['Y50'] - (lat - 50) * 110.6 * R['PXKM'])
    offs = []
    for ll in [(3.5, 49.0), (7.6, 51.4), (3.6, 51.3), (7.6, 48.9), (4.4, 50.9), (4.2, 48.6)]:    # away from the Ardennes overprint
        x, y = [int(v / 4) for v in px(*ll)]; h = 110
        if x - h < 0 or y - h < 0 or x + h > ref.shape[1] or y + h > ref.shape[0]: continue
        res = cv2.matchTemplate(tgt, ref[y - h:y + h, x - h:x + h], cv2.TM_CCOEFF_NORMED); _, sc, _, loc = cv2.minMaxLoc(res)
        offs.append((loc[0] - (x - h), loc[1] - (y - h), sc))
    good = [o for o in offs if o[2] > 0.45]
    if len(good) < 3: raise SystemExit(f'{date}: could not register the scan (matches {[round(o[2], 2) for o in offs]}); register it by hand')
    dx = float(np.median([o[0] for o in good])) * 4; dy = float(np.median([o[1] for o in good])) * 4
    spread = max(max(abs(o[0] * 4 - dx), abs(o[1] * 4 - dy)) for o in good)
    g = {'X6': R['X6'] + dx, 'Y50': R['Y50'] + dy, 'PXKM': R['PXKM'], 'by': f'matched to {ref_date} ({len(good)} patches, spread {spread:.0f} px, {spread / R["PXKM"]:.1f} km)'}
    if spread > 30: raise SystemExit(f'{date}: registration patches disagree by {spread:.0f} px; register it by hand')
    maps[date]['georef'] = g; json.dump(cfg, open(cf, 'w'), indent=1); print(date, g['by']); return g
if __name__ == '__main__': print(register(sys.argv[1], sys.argv[2]))
