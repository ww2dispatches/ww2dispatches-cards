"""Routes (FORMAT.md, the move set, Routes; Brian, 28 Nov 2026): the way a block slides across the close table, in table
units. Shared by day.py (the engine) and check_series.py (the checker), so the checker tests the path that is drawn.

A move takes the straight way when it is clear. Otherwise the shortest clear route is found on a grid at block clearance,
pulled tight, smoothed into a gentle curve (Chaikin corner cutting, kept only while it stays clear) and kept inside the
frame. A goal can be a point (advance, fall back, arrive) or a region past a frame edge (leave). None means boxed in.

Clear means the moving block's centre stays at least CLEAR blocks (Chebyshev) from every other block's centre: closer
than that, the two overlap on screen. This is the checker's pass through test."""
import math, heapq
import numpy as np

CLEAR = 0.9                         # blocks: the overlap test
PLAN = (1.25, 1.1, 0.95)            # blocks: clearances tried for the grid search, widest first, so smoothing has room
STEP = 0.1                          # grid step, table units

def _sep(P, obs):
    """per point of P (n, 2): the smallest Chebyshev distance to each obstacle, as an (n, m) array"""
    P = np.asarray(P, float).reshape(-1, 2); O = np.asarray(obs, float).reshape(-1, 2)
    if not len(O): return np.full((len(P), 0), np.inf)
    return np.maximum(np.abs(P[:, None, 0] - O[None, :, 0]), np.abs(P[:, None, 1] - O[None, :, 1]))

def clear_pts(P, obs, need):
    """every point of P keeps each obstacle j at least need[j] away"""
    if not len(obs): return True
    return bool((_sep(P, obs) >= np.asarray(need)[None, :] - 1e-9).all())

def straight(a, b, n=80):
    return [(a[0] + (b[0] - a[0]) * k / n, a[1] + (b[1] - a[1]) * k / n) for k in range(n + 1)]

def straight_clear(a, b, obs, bs):
    """the checker's test of a straight slide: samples 1 to 79 of 80 stay CLEAR of every obstacle"""
    return clear_pts(straight(a, b)[1:-1], obs, [CLEAR * bs] * len(obs))

def _dense(path, step=0.05):
    out = [path[0]]
    for p, q in zip(path, path[1:]):
        n = max(1, int(math.ceil(math.hypot(q[0] - p[0], q[1] - p[1]) / step)))
        out += [(p[0] + (q[0] - p[0]) * k / n, p[1] + (q[1] - p[1]) * k / n) for k in range(1, n + 1)]
    return out

def _chaikin(P):
    out = [P[0]]
    for p, q in zip(P, P[1:]):
        out += [(0.75 * p[0] + 0.25 * q[0], 0.75 * p[1] + 0.25 * q[1]), (0.25 * p[0] + 0.75 * q[0], 0.25 * p[1] + 0.75 * q[1])]
    out.append(P[-1]); return out

def find(start, obs, bs, allowed, goal=None, region=None, bounds=None, cost=None):
    """the shortest clear route from start to the point goal, or to any point where region(x, y) is true.
    obs: obstacle centres; allowed(X, Y) -> bool array: where the block may go (inside the frame, or past the edge a
    leave or arrive uses). bounds: (x0, y0, x1, y1) of the grid. Returns a list of table points, or None."""
    obs = [tuple(o) for o in obs]
    def need(c):
        """clearance per obstacle: c, but never more than the obstacle already is from the start or the goal point
        (a block that starts or ends touching a neighbour still has to get away from it)"""
        out = []
        for o in obs:
            r = max(abs(o[0] - start[0]), abs(o[1] - start[1]))
            if goal is not None: r = min(r, max(abs(o[0] - goal[0]), abs(o[1] - goal[1])))
            out.append(max(min(c, r - 0.01), min(CLEAR * bs, r - 0.01)))
        return np.array(out)
    x0, y0, x1, y1 = bounds
    xs = np.arange(x0, x1 + STEP / 2, STEP); ys = np.arange(y0, y1 + STEP / 2, STEP)
    X, Y = np.meshgrid(xs, ys); ok0 = np.asarray(allowed(X, Y), bool)
    CW = np.asarray(cost(X, Y), float) if cost is not None else np.ones(X.shape)    # price of stepping into each cell
    reg = np.asarray(region(X, Y), bool) if region is not None else None
    def cell(p): return (int(round((p[1] - y0) / STEP)), int(round((p[0] - x0) / STEP)))
    s = cell(start); g = cell(goal) if goal is not None else None
    ny, nx = X.shape
    if not (0 <= s[0] < ny and 0 <= s[1] < nx): return None
    final = None; verify = None
    for c in PLAN:
        nd = need(c * bs); ok = ok0.copy()
        for o, r in zip(obs, nd): ok &= np.maximum(np.abs(X - o[0]), np.abs(Y - o[1])) >= r
        ok[s] = True
        if g is not None:
            if not (0 <= g[0] < ny and 0 <= g[1] < nx): return None
            ok[g] = True
        dist = np.full(X.shape, np.inf); prev = {}; dist[s] = 0.0; pq = [(0.0, s)]; hit = None
        while pq:
            dd, (i, j) = heapq.heappop(pq)
            if dd > dist[i, j]: continue
            if (g is not None and (i, j) == g) or (reg is not None and reg[i, j]): hit = (i, j); break
            for di, dj, w in ((1, 0, 1), (-1, 0, 1), (0, 1, 1), (0, -1, 1), (1, 1, 1.4142), (1, -1, 1.4142), (-1, 1, 1.4142), (-1, -1, 1.4142)):
                a, b = i + di, j + dj
                if 0 <= a < ny and 0 <= b < nx and ok[a, b] and dd + w * CW[a, b] < dist[a, b]:
                    dist[a, b] = dd + w * CW[a, b]; prev[(a, b)] = (i, j); heapq.heappush(pq, (dist[a, b], (a, b)))
        if hit is None: continue
        cells = [hit]
        while cells[-1] != s: cells.append(prev[cells[-1]])
        P = [(xs[j], ys[i]) for i, j in reversed(cells)]; P[0] = tuple(start)
        if goal is not None: P[-1] = tuple(goal)
        # pull tight: from each kept point, jump to the farthest point it sees in a clear straight line
        tight = [P[0]]; i = 0
        while i < len(P) - 1:
            j = len(P) - 1
            while j > i + 1 and not _seg_clear(P[i], P[j], obs, nd, allowed, P[0], P[-1]): j -= 1
            tight.append(P[j]); i = j
        final = tight; verify = need(CLEAR * bs)
        break
    if final is None: return None
    best = final
    for _ in range(4):                                       # round the corners while the curve stays clear
        nxt = _chaikin(best)
        if clear_pts(_dense(nxt)[1:-1], obs, verify) and _in_allowed(_dense(nxt), allowed, nxt[0], nxt[-1]): best = nxt
        else: break
    return [tuple(map(float, p)) for p in best]

def _in_allowed(D, allowed, a, b):
    """every point is allowed, except near the two ends (a start or goal may sit past the edge)"""
    A = np.asarray(allowed(np.array([d[0] for d in D]), np.array([d[1] for d in D])), bool)
    near = np.array([min(math.hypot(d[0] - a[0], d[1] - a[1]), math.hypot(d[0] - b[0], d[1] - b[1])) < 1.0 for d in D])
    return bool((A | near).all())

def _seg_clear(p, q, obs, nd, allowed, a, b):
    D = _dense([p, q]); return clear_pts(D, obs, nd) and _in_allowed(D, allowed, a, b)

def resample(path, n=200):
    """n + 1 points evenly spaced along the path, and its length"""
    P = np.array(path, float); seg = np.r_[0, np.cumsum(np.hypot(*np.diff(P, axis=0).T))]; L = seg[-1]
    if L < 1e-9: return [tuple(P[0])] * (n + 1), 0.0
    u = np.linspace(0, L, n + 1); out = np.c_[np.interp(u, seg, P[:, 0]), np.interp(u, seg, P[:, 1])]
    return [tuple(p) for p in out], float(L)

def at(rs, k):
    """the point a fraction k (0 to 1) of the way along a resampled path"""
    n = len(rs) - 1; f = min(max(k, 0.0), 1.0) * n; i = min(int(f), n - 1); u = f - i
    return (rs[i][0] + (rs[i + 1][0] - rs[i][0]) * u, rs[i][1] + (rs[i + 1][1] - rs[i][1]) * u)

def heading(rs, k, span=0.04):
    """the direction of travel a fraction k of the way along a resampled path"""
    p, q = at(rs, k - span), at(rs, k + span)
    return (q[0] - p[0], q[1] - p[1])
