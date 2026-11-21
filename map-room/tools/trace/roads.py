"""Trace main roads from the grey print of a situation map scan, between waypoint towns (lon, lat), following the
cheapest path through grey road ink. Usage: roads.py <scan.jpg> <x0> <y0> <out.json>"""
import sys, json, numpy as np, cv2
from skimage.graph import route_through_array
from georef import px, ll
B = (5.716, 50.000)
ROADS = {
 'Bastogne-Houffalize-Manhay': [B,(5.763,50.061),(5.790,50.133),(5.735,50.245),(5.678,50.293)],
 'Bastogne-Clervaux': [B,(5.830,50.030),(6.030,50.055)],
 'Bastogne-Wiltz': [B,(5.800,49.975),(5.932,49.966)],
 'Bastogne-Arlon': [B,(5.700,49.950),(5.740,49.830),(5.817,49.683)],
 'Bastogne-Neufchateau': [B,(5.640,49.970),(5.435,49.842)],
 'Bastogne-Marche': [B,(5.660,50.030),(5.480,50.110),(5.344,50.227)],
 'Bastogne-St Hubert': [B,(5.540,50.010),(5.374,50.027)],
 'Houffalize-St Vith': [(5.790,50.133),(5.960,50.180),(6.125,50.280)],
 'St Vith-Vielsalm-Trois Ponts': [(6.125,50.280),(5.915,50.280),(5.870,50.370)],
 'Marche-Hotton-Manhay': [(5.344,50.227),(5.446,50.267),(5.678,50.293)],
 'Marche-Dinant': [(5.344,50.227),(5.100,50.230),(4.912,50.261)],
 'Malmedy-St Vith': [(6.030,50.426),(6.125,50.280)],
 'Clervaux-St Vith': [(6.030,50.055),(6.080,50.170),(6.125,50.280)],
}
def greyness_cost(im):
    f = im.astype(np.float32); mx, mn = f.max(2), f.min(2)
    grey = ((mx - mn) < 22) & (mx > 105) & (mx < 210)
    s = cv2.GaussianBlur(grey.astype(np.float32), (5, 5), 0)
    return 1 + 300 * (1 - np.clip(s * 1.6, 0, 1)) ** 3
def route(cost, wps, x0, y0):
    H, W = cost.shape; pts = []
    P = [(int(px(*w)[0] - x0), int(px(*w)[1] - y0)) for w in wps]
    for a, b in zip(P, P[1:]):
        m = 80; xa, xb = sorted((a[0], b[0])); ya, yb = sorted((a[1], b[1]))
        X0, X1, Y0, Y1 = max(0, xa - m), min(W, xb + m), max(0, ya - m), min(H, yb + m)
        path, _ = route_through_array(cost[Y0:Y1, X0:X1], (a[1]-Y0, a[0]-X0), (b[1]-Y0, b[0]-X0), fully_connected=True)
        seg = [(c + X0, r + Y0) for r, c in path]; pts += seg if not pts else seg[1:]
    pts = cv2.approxPolyDP(np.array(pts, np.float32).reshape(-1, 1, 2), 2.5, False).reshape(-1, 2)
    return [[round(float(v), 5) for v in ll(float(x) + x0, float(y) + y0)] for x, y in pts]
if __name__ == '__main__':
    scan, x0, y0, dst = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), sys.argv[4]
    cost = greyness_cost(cv2.imread(scan))
    out = {k: route(cost, v, x0, y0) for k, v in ROADS.items()}
    json.dump({'source': 'LOC HQ Twelfth Army Group situation map, grey road print, traced between towns', 'roads': out}, open(dst, 'w'))
    print({k: len(v) for k, v in out.items()})
