"""The overlay sheet (FORMAT.md, The fact check, part 2): a day's blocks and night line drawn on that day's situation
map scan, so each block can be compared with the unit symbol printed on the map.
Writes <out>.jpg (the whole battle) and <out>-units.jpg (a close crop per unit, moved units first).
Each block is drawn at its true place, 10 km square: blue for Allied, black for German, with its roster id. A unit that
moved has an arrow from where it stood in the morning. The night line is bright green; the morning line is thin.
Usage: overlay.py <series folder> <day number> <out base> [night|start]
night (the default) draws the night table on the NEXT day's map, because the maps were drawn at noon; start draws the
morning table on the day's own map."""
import sys, os, json, math, numpy as np, cv2
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, '..', '..', 'engine'))
import series as S, register as R
def main(folder, n, out, which='night'):
    import datetime
    s = S.Series(folder); d = dict(next(x for x in s.days if x['n'] == int(n))); date = d['rec']['date']
    if which == 'night': date = (datetime.date.fromisoformat(date) + datetime.timedelta(days=1)).isoformat()   # tonight's table is first seen on tomorrow's noon map
    else: d['pm_true'] = d['am_true']; d['line'] = d['lineAM']; d['movers'] = []
    if date not in s.cfg['maps']: raise SystemExit(f'no situation map listed for {date}')
    m = s.cfg['maps'][date]; g = m.get('georef') or R.register(s.campaign, date)
    def px(ll): return (g['X6'] + (ll[0] - 6) * 111.32 * math.cos(math.radians(ll[1])) * g['PXKM'], g['Y50'] - (ll[1] - 50) * 110.6 * g['PXKM'])
    b = s.box; x0, y0 = [int(v) - 150 for v in px((b[0], b[3]))]; x1, y1 = [int(v) + 150 for v in px((b[1], b[2]))]; x0, y0 = max(0, x0), max(0, y0)
    im = R.fetch(m['iiif'], f'{x0},{y0},{x1 - x0},{y1 - y0}', 'full', f'{date}-battle.jpg'); clean = im.copy()
    P = lambda ll: (int(px(ll)[0] - x0), int(px(ll)[1] - y0)); half = s.block / 2 * g['PXKM']
    def line(pts, col, w):
        cv2.polylines(im, [np.array([P(p) for p in pts], np.int32)], False, (255, 255, 255), w + 4, cv2.LINE_AA)
        cv2.polylines(im, [np.array([P(p) for p in pts], np.int32)], False, col, w, cv2.LINE_AA)
    if d['lineAM'] != d['line']: line(d['lineAM'], (0, 150, 0), 2)
    line(d['line'], (0, 220, 0), 5)
    def block(img, c, u, w=4):
        col = (230, 90, 0) if s.allied(u) else (0, 0, 0)
        cv2.rectangle(img, (int(c[0] - half), int(c[1] - half)), (int(c[0] + half), int(c[1] + half)), (255, 255, 255), w + 3)
        cv2.rectangle(img, (int(c[0] - half), int(c[1] - half)), (int(c[0] + half), int(c[1] + half)), col, w)
        for cc, ww in (((255, 255, 255), 6), (col, 2)): cv2.putText(img, u, (int(c[0] - half), int(c[1] - half) - 8), cv2.FONT_HERSHEY_SIMPLEX, 0.8, cc, ww, cv2.LINE_AA)
    for u, p in d['pm_true'].items():
        if u in d['movers'] and u in d['am_true']: cv2.arrowedLine(im, P(d['am_true'][u]), P(p), (0, 0, 255), 4, cv2.LINE_AA, tipLength=0.15)
        block(im, P(p), u)
    head = f"Day {d['n']} {which} table on {m['label']}  ({g['by']})"
    cv2.rectangle(im, (0, 0), (im.shape[1], 44), (255, 255, 255), -1); cv2.putText(im, head, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 0, 0), 2, cv2.LINE_AA)
    cv2.imwrite(out + '.jpg', im, [cv2.IMWRITE_JPEG_QUALITY, 88])
    # a close crop per unit on the clean scan: the block outline thin, so the printed symbol under it can be read
    order = [u for u in d['pm_true'] if u in d['movers']] + [u for u in sorted(d['pm_true']) if u not in d['movers']]
    tiles = []; r = int(half * 3.2)
    for u in order:
        c = P(d['pm_true'][u]); pad = cv2.copyMakeBorder(clean, r, r, r, r, cv2.BORDER_CONSTANT, value=(255, 255, 255))
        t = pad[c[1]:c[1] + 2 * r, c[0]:c[0] + 2 * r].copy(); t = cv2.resize(t, (480, 480), interpolation=cv2.INTER_CUBIC); k = 480 / (2 * r)
        col = (230, 90, 0) if s.allied(u) else (0, 0, 0); h2 = int(half * k)
        cv2.rectangle(t, (240 - h2, 240 - h2), (240 + h2, 240 + h2), col, 2)
        cv2.rectangle(t, (0, 0), (480, 30), (255, 255, 255), -1)
        cv2.putText(t, f"{u}: {s.units[u]['name']}{' (MOVED)' if u in d['movers'] else ''}"[:44], (6, 21), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 0, 200) if u in d['movers'] else (0, 0, 0), 2, cv2.LINE_AA)
        tiles.append(t)
    cols = 4; rows = (len(tiles) + cols - 1) // cols; sheet = np.full((rows * 480, cols * 480, 3), 255, np.uint8)
    for i, t in enumerate(tiles): sheet[(i // cols) * 480:(i // cols + 1) * 480, (i % cols) * 480:(i % cols + 1) * 480] = t
    cv2.imwrite(out + '-units.jpg', sheet, [cv2.IMWRITE_JPEG_QUALITY, 88]); print('wrote', out + '.jpg', out + '-units.jpg')
if __name__ == '__main__': main(*sys.argv[1:5])
