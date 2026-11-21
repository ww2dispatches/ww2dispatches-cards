"""Trace rivers from the blue ink of a situation map scan. Each river is a list of waypoints (lon, lat) near its
course; the trace follows the cheapest path through blue ink between them, so it keeps the map's own course.
Usage: rivers.py <scan.jpg> <scan_x0> <scan_y0> <out.json> [check.jpg]"""
import sys, json, numpy as np, cv2
from skimage.graph import route_through_array
from georef import px, ll
RIVERS = {
 'Meuse':   [(5.38,49.16),(5.17,49.50),(4.94,49.70),(4.72,49.77),(4.73,49.88),(4.83,50.14),(4.91,50.26),(4.87,50.47),
             (5.24,50.52),(5.57,50.63),(5.69,50.85),(5.99,51.19),(6.17,51.37),(5.95,51.70)],
 'Ourthe':  [(5.57,50.63),(5.57,50.53),(5.58,50.47),(5.46,50.35),(5.45,50.27),(5.58,50.18),(5.66,50.13),(5.79,50.13)],
 'Ambleve': [(5.58,50.47),(5.67,50.47),(5.81,50.41),(5.87,50.37),(5.93,50.39),(6.10,50.35)],
 'Salm':    [(5.87,50.37),(5.90,50.33),(5.92,50.28)],
 'Sure':    [(5.74,49.83),(5.94,49.91),(6.10,49.85),(6.16,49.87),(6.29,49.87),(6.42,49.81),(6.50,49.72)],
 'Our':     [(6.13,50.14),(6.13,50.05),(6.21,49.93),(6.29,49.87)],
 'Moselle': [(6.18,49.12),(6.17,49.36),(6.37,49.47),(6.37,49.55),(6.44,49.68),(6.50,49.72),(6.64,49.75),(6.95,49.92),
             (7.08,50.03),(7.30,50.15),(7.59,50.36)],
 'Rhine':   [(7.90,49.97),(7.77,50.06),(7.71,50.15),(7.59,50.23),(7.59,50.36),(7.23,50.58),(7.10,50.73),(6.96,50.94),(6.77,51.22),(6.76,51.43),(6.60,51.67)],
 'Lesse':   [(4.91,50.24),(5.00,50.19),(5.22,50.16)],
 'Semois':  [(4.73,49.88),(5.07,49.79),(5.31,49.70),(5.55,49.68)],
 'Roer':    [(6.24,50.56),(6.48,50.80),(6.36,50.92),(6.10,51.07),(5.99,51.19)],
}
def blueness(im):
    b, g, r = [im[..., i].astype(np.float32) for i in range(3)]
    return b - np.maximum(r, g)
def trace(scan, x0, y0):
    im = cv2.imread(scan); bl = blueness(im)
    sc = np.clip((bl - 2) / 14.0, 0, 1); cost = 1 + 300 * (1 - sc) ** 3
    strong = bl > 9
    H, W = bl.shape; out = {}
    def snap(x, y, r=30):
        ys, xs = np.nonzero(strong[max(0,y-r):y+r, max(0,x-r):x+r])
        if not len(xs): return x, y
        k = np.argmin((xs + max(0,x-r) - x) ** 2 + (ys + max(0,y-r) - y) ** 2)
        return xs[k] + max(0, x - r), ys[k] + max(0, y - r)
    for name, wps in RIVERS.items():
        pts = []
        P = [snap(int(px(*w)[0] - x0), int(px(*w)[1] - y0)) for w in wps]
        P = [p for p in P if 0 <= p[0] < W and 0 <= p[1] < H]
        for a, b in zip(P, P[1:]):
            m = 120; xa, xb = sorted((a[0], b[0])); ya, yb = sorted((a[1], b[1]))
            X0, X1, Y0, Y1 = max(0, xa - m), min(W, xb + m), max(0, ya - m), min(H, yb + m)
            path, _ = route_through_array(cost[Y0:Y1, X0:X1], (a[1]-Y0, a[0]-X0), (b[1]-Y0, b[0]-X0), fully_connected=True)
            seg = [(c + X0, r + Y0) for r, c in path]
            pts += seg if not pts else seg[1:]
        pts = cv2.approxPolyDP(np.array(pts, np.float32).reshape(-1, 1, 2), 2.0, False).reshape(-1, 2)
        out[name] = [[round(float(v), 5) for v in ll(float(x) + x0, float(y) + y0)] for x, y in pts]
    return im, out
if __name__ == '__main__':
    scan, x0, y0, dst = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), sys.argv[4]
    im, out = trace(scan, x0, y0)
    json.dump({'source': 'LOC HQ Twelfth Army Group situation map, blue ink, traced', 'rivers': out}, open(dst, 'w'), indent=0)
    if len(sys.argv) > 5:
        for name, pl in out.items():
            p = np.array([[px(*q)[0] - x0, px(*q)[1] - y0] for q in pl], np.int32)
            cv2.polylines(im, [p], False, (0, 0, 255), 5)
        cv2.imwrite(sys.argv[5], im)
    print({k: len(v) for k, v in out.items()})
