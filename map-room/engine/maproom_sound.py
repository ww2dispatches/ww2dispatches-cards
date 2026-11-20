"""The Map Room sound kit, generated from code (original, owned by Brian Acquesta). Builds the three Day 1 test mixes."""
import numpy as np, scipy.signal as ss, scipy.io.wavfile as wf
SR = 48000; T = 17.5; N = int(SR * T)
rng = np.random.default_rng(16)
def bp(x, lo, hi, o=4): return ss.sosfilt(ss.butter(o, [lo, hi], 'bandpass', fs=SR, output='sos'), x)
def lp(x, f, o=4): return ss.sosfilt(ss.butter(o, f, 'lowpass', fs=SR, output='sos'), x)
def hp(x, f, o=2): return ss.sosfilt(ss.butter(o, f, 'highpass', fs=SR, output='sos'), x)
def env(n, a, r):
    e = np.ones(n); ai = int(a * SR); ri = int(r * SR)
    if ai: e[:ai] = np.linspace(0, 1, ai)
    if ri: e[-ri:] *= np.linspace(1, 0, ri)
    return e
def put(buf, x, t, g=1.0):
    i = int(t * SR); j = min(len(buf), i + len(x))
    if j > i: buf[i:j] += g * x[:j - i]
def room(x, mix=0.18):
    out = x.copy()
    for d, g in [(0.023, .5), (0.037, .4), (0.051, .33), (0.071, .25), (0.097, .18)]:
        k = int(d * SR); y = np.zeros_like(x); y[k:] = x[:-k] * g; out += lp(y, 3500) * mix * 2
    return out
# ---------- table sounds ----------
def slide(dur, bright=1.0):
    """wood block sliding on the glossy map: band limited noise, grain flutter, swells with speed"""
    n = int(dur * SR); t = np.arange(n) / SR
    x = rng.standard_normal(n)
    flutter = 1 + 0.35 * bp(rng.standard_normal(n), 8, 40, 2) * 6
    speed = np.sin(np.pi * np.clip(t / dur, 0, 1)) ** 0.8
    a = bp(x, 260, 1900 * bright, 3) * 0.9 + bp(x, 1900, 3800, 2) * 0.25 * bright
    return np.tanh(a * flutter * speed * 1.6) * 0.32 * env(n, 0.02, 0.05)
def push_slide(dur):
    """block pushed by the rake: loudness and brightness follow the block's own speed (the cubic ease in comp.py),
    so it swells as the push gets going and fades as friction stops it. No knock at the end: nothing hits anything."""
    n = int(dur * SR); x_ = np.clip(np.arange(n) / SR / dur, 0, 1)
    v = np.where(x_ < 0.5, 12 * x_ ** 2, 12 * (1 - x_) ** 2) / 3.0      # speed, 0 to 1
    x = rng.standard_normal(n)
    flutter = 1 + 0.35 * bp(rng.standard_normal(n), 8, 40, 2) * 6
    body = bp(x, 260, 1200, 3) * 0.9; air = bp(x, 1200, 3600, 2) * 0.4
    a = body * v ** 0.7 + air * v ** 1.6                                  # duller as it slows
    return np.tanh(a * flutter * 1.6) * 0.32 * env(n, 0.02, 0.02)
def knock(g=1.0, f0=420):
    """block set down: short wooden knock, two body modes plus a contact tick"""
    n = int(0.35 * SR); t = np.arange(n) / SR
    x = (np.sin(2 * np.pi * f0 * t) * np.exp(-t / 0.035) + 0.6 * np.sin(2 * np.pi * f0 * 2.37 * t) * np.exp(-t / 0.018)
         + 0.5 * np.sin(2 * np.pi * 150 * t) * np.exp(-t / 0.05))
    tick = bp(rng.standard_normal(n), 1200, 4000) * np.exp(-t / 0.004) * 0.6
    return np.tanh((x + tick) * 1.3) * 0.55 * g * env(n, 0.001, 0.02)
def tap(): return knock(0.30, 610)   # rake head meets the block: a light wood on wood touch
# ---------- war room bed ----------
def teletype(dur):
    n = int(dur * SR); out = np.zeros(n); t = 0.0
    while t < dur - 0.1:
        burst = rng.uniform(0.6, 1.8)
        for k in range(int(burst * 10)):
            put(out, knock(0.18, rng.uniform(900, 1300)) * rng.uniform(0.5, 1), t + k / 10 + rng.uniform(0, 0.015))
        t += burst + rng.uniform(0.3, 1.1)
    return bp(out, 400, 3200) * 0.9
def clock(dur):
    n = int(dur * SR); out = np.zeros(n)
    for k in range(int(dur)):
        put(out, knock(0.16, 1500 if k % 2 else 1250), k + 0.05)
    return out
def static(dur):
    n = int(dur * SR); x = bp(rng.standard_normal(n), 400, 3000)
    crack = (rng.random(n) < 0.0006) * rng.standard_normal(n) * 3
    return (x * 0.018 + bp(crack, 600, 3500) * 0.03) * (1 + 0.3 * np.sin(2 * np.pi * 0.21 * np.arange(n) / SR))
def hum(dur):
    t = np.arange(int(dur * SR)) / SR
    return (0.010 * np.sin(2 * np.pi * 60 * t) + 0.005 * np.sin(2 * np.pi * 120 * t)) + lp(rng.standard_normal(len(t)), 180) * 0.02
# ---------- quiet in house theme: original, D minor, low piano and a bowed drone ----------
def piano(f, dur, g):
    n = int(dur * SR); t = np.arange(n) / SR; x = np.zeros(n)
    for k in range(1, 8):
        fk = f * k * np.sqrt(1 + 0.0004 * k * k); x += np.sin(2 * np.pi * fk * t) * (0.8 ** k) * np.exp(-t * (0.7 + 0.5 * k))
    ham = bp(rng.standard_normal(n), 200, 2500) * np.exp(-t / 0.006) * 0.15
    return lp(x + ham, 3200) * g * env(n, 0.004, 0.3)
def bow(f, dur, g):
    n = int(dur * SR); t = np.arange(n) / SR
    ph = 2 * np.pi * np.cumsum(f * (1 + 0.004 * np.sin(2 * np.pi * 5.2 * t))) / SR
    saw = sum(np.sin(k * ph) / k for k in range(1, 14))
    return np.tanh(lp(saw, 900) * 0.8) * g * env(n, 1.2, 1.5)
def note(name):
    names = {'C': -9, 'D': -7, 'E': -5, 'F': -4, 'G': -2, 'A': 0, 'Bb': 1}
    return 440 * 2 ** ((names[name[:-1]] + 12 * (int(name[-1]) - 4)) / 12)
def theme():
    out = np.zeros(N)
    # four slow bars at 60 bpm from 1.5 s: Dm, Bb, Gm, A (left open for tomorrow)
    bars = [(['D2', 'A2'], ['F3', 'A3', 'D4']), (['Bb1', 'F2'], ['D3', 'F3', 'Bb3']), (['G1', 'D2'], ['Bb2', 'D3', 'G3']), (['A1', 'E2'], ['C3', 'E3', 'A3'])]
    tune = [['D4', None, 'F4', 'E4'], ['D4', None, None, 'C4'], ['D4', None, 'Bb3', None], ['A3', None, None, None]]
    for b, ((lo1, lo2), ch) in enumerate(bars):
        t0 = 1.5 + 3.6 * b
        hold = 5.6 if b == 3 else 4.1
        put(out, bow(note(lo1), hold, 0.05), t0); put(out, bow(note(lo2), hold, 0.03), t0)
        for i, nm in enumerate(ch): put(out, piano(note(nm), 3.2, 0.05), t0 + 0.06 * i)
        for i, nm in enumerate(tune[b]):
            if nm: put(out, piano(note(nm), 2.2, 0.09), t0 + 0.85 * i)
    put(out, piano(note('A2'), 2.5, 0.08), 15.0); put(out, piano(note('E3'), 2.4, 0.04), 15.06)
    return room(out, 0.35)
# ---------- clip timing (matches comp.py) ----------
ENTER, MOVE, HOLD, EXIT = 0.8, 1.9, 0.25, 0.75
PUSH = [2.0, 5.65, 9.3]
def pencil(dur):
    """grease pencil drawn across the acetate: soft waxy drag with small stick slip catches"""
    n = int(dur * SR); t = np.arange(n) / SR
    x = bp(rng.standard_normal(n), 500, 2600, 3)
    catch = 1 + 0.6 * np.clip(bp(rng.standard_normal(n), 15, 60, 2) * 8, 0, None)
    return np.tanh(x * catch * 1.3) * 0.16 * env(n, 0.05, 0.12)
def wipe(dur):
    n = int(dur * SR); x = bp(rng.standard_normal(n), 250, 1400, 2)
    return x * np.sin(np.pi * np.arange(n) / n) * 0.10
def table_track():
    out = np.zeros(N)
    for t0 in PUSH:
        put(out, slide(ENTER, 0.6), t0, 0.35)              # rake pole slides in
        put(out, tap(), t0 + ENTER - 0.01)                 # rake meets the block
        put(out, push_slide(MOVE), t0 + ENTER)              # block pushed across the glass, slows to a stop
        put(out, slide(EXIT, 0.6), t0 + ENTER + MOVE + HOLD, 0.3)  # rake withdraws
    put(out, wipe(0.5), 13.0); put(out, pencil(1.5), 13.5)
    return room(out, 0.15)
def bed():
    return teletype(T) * 0.5 + clock(T) * 0.55 + static(T) + hum(T)
def master(x, name):
    x = hp(x, 70); x = np.tanh(x * 1.2) / 1.2
    pk = np.max(np.abs(x)); x = x / pk * 10 ** (-1.5 / 20)
    x *= env(len(x), 0.01, 0.8)
    wf.write(name, SR, (x * 32767).astype(np.int16)); print(name)
tt, bd, th = table_track(), bed(), theme()
master(tt + hum(T) * 0.6, 'mix-a-table.wav')
master(tt + bd * 0.55, 'mix-b-table-warroom.wav')
master(tt + bd * 0.55 + th * 1.0, 'mix-c-table-warroom-theme.wav')
for nm, x in [('stem-table.wav', tt), ('stem-warroom.wav', bd), ('stem-theme.wav', th)]:
    wf.write(nm, SR, (x / max(1e-9, np.max(np.abs(x))) * 0.89 * 32767).astype(np.int16))
