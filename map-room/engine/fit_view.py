"""Fit a series view: the largest map scale (and its center) at which every place in a box can hold a whole block
inside the template's block zone and on the table map. Prints the table.json numbers.
Usage: fit_view.py lon_min lon_max lat_min lat_max [margin]   (margin: fraction to step back from the tightest fit, default 0.05)"""
import sys, day

def fits(s, lon0, lat0, pts):
    t = day.Table.__new__(day.Table)
    t.LON0, t.LAT0, t.KX, t.KY = lon0, lat0, 7.15 * s, 11.12 * s   # keeps the sketch's aspect (1 / cos 50 N)
    t.lon_min, t.lon_max = lon0 - day.TW / 2 / t.KX, lon0 + day.TW / 2 / t.KX
    t.lat_min, t.lat_max = lat0 - day.TH / 2 / t.KY, lat0 + day.TH / 2 / t.KY
    for p in pts:
        xy = t.XY(p)
        if abs(xy[0]) > day.TW / 2 - 0.7 or abs(xy[1]) > day.TH / 2 - 0.7 or not day.in_zone(xy): return False
    return True
def fit(lon_min, lon_max, lat_min, lat_max, margin=0.05):
    pts = [(lo, la) for lo in (lon_min, (lon_min + lon_max) / 2, lon_max) for la in (lat_min, (lat_min + lat_max) / 2, lat_max)]
    cx, cy = (lon_min + lon_max) / 2, (lat_min + lat_max) / 2
    def centers(s, step):
        span = 4.0 / s
        return [(cx - span + i * step, cy - span + j * step) for i in range(int(2 * span / step) + 1) for j in range(int(2 * span / step) + 1)]
    best = None
    for s in [x / 100 for x in range(20, 600, 2)]:
        step = 0.4 / (7.15 * s)            # about 0.4 table units
        ok = [c for c in centers(s, step) if fits(s, c[0], c[1], pts)]
        if ok: best = (s, ok)
        elif best: break
    if not best: raise SystemExit('no fit: the box is too large for the table at any scale')
    s = best[0] * (1 - margin); step = 0.2 / (7.15 * s)
    ok = [c for c in centers(s, step) if fits(s, c[0], c[1], pts)]
    lon0 = sum(c[0] for c in ok) / len(ok); lat0 = sum(c[1] for c in ok) / len(ok)
    return {'LON0': round(lon0, 3), 'LAT0': round(lat0, 3), 'KX': round(7.15 * s, 3), 'KY': round(11.12 * s, 3),
            'block_km': round(day.BS / (7.15 * s) * 71.5, 1)}
if __name__ == '__main__':
    a = [float(x) for x in sys.argv[1:5]]; m = float(sys.argv[5]) if len(sys.argv) > 5 else 0.05
    print(fit(*a, m))
