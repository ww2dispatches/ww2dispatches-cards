"""Pull traced rivers onto true positions. The 1:1,000,000 scans are generalized and drift a few km in places, so
each river is bent to pass through the towns that stand on it (true positions), with the shift spread along the
river between them. Usage: truefit.py <rivers.json>  (rewrites it, keeping the raw trace as rivers-raw.json)"""
import sys, json, math, numpy as np
C = {
 'Meuse': [(5.384,49.160),(4.944,49.702),(4.720,49.772),(4.731,49.882),(4.706,49.993),(4.826,50.138),(4.912,50.261),
           (4.867,50.466),(5.240,50.519),(5.570,50.633),(5.689,50.851),(5.987,51.194),(6.168,51.370)],
 'Ourthe': [(5.578,50.625),(5.567,50.533),(5.578,50.475),(5.456,50.352),(5.446,50.267),(5.576,50.183),(5.790,50.133)],
 'Ambleve': [(5.578,50.475),(5.676,50.474),(5.871,50.371),(5.931,50.394)],
 'Salm': [(5.871,50.371),(5.916,50.284)],
 'Sure': [(5.739,49.832),(5.935,49.911),(6.104,49.847),(6.159,49.868),(6.421,49.812),(6.501,49.715)],
 'Our': [(6.134,50.140),(6.132,50.049),(6.208,49.935),(6.290,49.872)],
 'Moselle': [(6.176,49.120),(6.168,49.358),(6.367,49.545),(6.443,49.679),(6.501,49.715),(6.641,49.750),(7.070,49.916),
             (7.167,50.147),(7.605,50.365)],
 'Rhine': [(7.896,49.967),(7.605,50.365),(7.231,50.578),(7.098,50.735),(6.958,50.938),(6.773,51.227),(6.762,51.434),(6.618,51.659)],
 'Lesse': [(4.909,50.237),(5.007,50.190),(5.222,50.162)],
 'Semois': [(4.731,49.882),(5.067,49.794),(5.310,49.700)],
 'Roer': [(6.243,50.555),(6.483,50.804),(6.268,50.981),(5.987,51.194)],
}
def km(a, b): return math.hypot((a[0]-b[0])*111.32*math.cos(math.radians(50)), (a[1]-b[1])*110.6)
def fit(pl, ctl):
    P = np.array(pl, float); n = len(P)
    # densify so the shift spreads smoothly
    D = [P[0]]
    for a, b in zip(P, P[1:]):
        k = max(1, int(km(a, b) / 0.4)); D += [a + (b - a) * s / k for s in range(1, k + 1)]
    P = np.array(D); idx, dv, report = [], [], []
    for c in ctl:
        d = [km(p, c) for p in P]; i = int(np.argmin(d))
        if d[i] > 9: report.append((c, round(d[i], 1), 'skipped')); continue
        idx.append(i); dv.append(np.array(c) - P[i]); report.append((c, round(d[i], 1)))
    if not idx: return P.tolist(), report
    o = np.argsort(idx); idx = np.array(idx)[o]; dv = np.array(dv)[o]
    sx = np.interp(np.arange(len(P)), idx, dv[:, 0]); sy = np.interp(np.arange(len(P)), idx, dv[:, 1])
    Q = P + np.stack([sx, sy], 1)
    return [[round(a, 5), round(b, 5)] for a, b in Q[::2].tolist() + [Q[-1].tolist()]], report
if __name__ == '__main__':
    src = sys.argv[1]; g = json.load(open(src))
    raw = src.replace('rivers.json', 'rivers-raw.json')
    try: g = json.load(open(raw))
    except FileNotFoundError: json.dump(g, open(raw, 'w'))
    for name, pl in g['rivers'].items():
        if name in C:
            g['rivers'][name], rep = fit(pl, C[name]); print(name, [r[1] for r in rep])
    g['source'] += '; bent to pass through the true positions of towns on each river'
    json.dump(g, open(src, 'w'))
