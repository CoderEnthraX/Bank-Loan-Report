import sys, itertools; sys.path.insert(0,'/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fit/hunt/stop_levels')
from lv import *
def ema(x, n):
    o = [None]*len(x); a = 2/(n+1); s = None
    for i, v in enumerate(x):
        s = v if s is None else s + a*(v-s); o[i] = s
    return o
def sma(x, n):
    o = [None]*len(x); s = 0
    for i, v in enumerate(x):
        s += v
        if i >= n: s -= x[i-n]
        if i >= n-1: o[i] = s/n
    return o
LENS = (9, 20, 21, 34, 50, 60, 89, 100, 144, 200, 240, 600, 800, 2400)
def mafeat(P, i, d, entry, A):
    g = {}
    for n in LENS:
        for nm, f in (('ema', ema), ('sma', sma)):
            k = (nm, n)
            if k not in P: P[k] = f(P['C'], n)
            v = P[k][i]
            if v is not None: g[f'{nm}{n}'] = d*(v-entry)/A
    return g
if __name__ == '__main__':
    rows = []
    for t in TRADES:
        P = prepare(t['sym']); i = t['arm_i']; A = P[('atr',14)][i]
        rows.append((t, mafeat(P, i, t['d'], t['entry'], A)))
    keys = sorted({k for _, x in rows for k in x}); res = []
    for k in keys:
        vals = [(x.get(k), t['tight']) for t, x in rows if x.get(k) is not None]
        vs = sorted(set(v for v, _ in vals)); cuts = [-1e9] + [(a+b)/2 for a, b in zip(vs, vs[1:])] + [1e9]
        best = None
        for a, b in itertools.combinations(cuts, 2):
            tp = sum(1 for v, tg in vals if tg and a < v < b); fp = sum(1 for v, tg in vals if not tg and a < v < b)
            if best is None or tp - fp > best[0]: best = (tp - fp, tp, fp, a, b)
        z = {}
        for zn, (a, b) in {'stop18': (-1.8, 0), 'stop18o': (-1.8, -0.9), 'tgt36': (0, 3.6)}.items():
            z[zn] = (sum(1 for v, tg in vals if tg and a < v < b), sum(1 for v, tg in vals if not tg and a < v < b))
        res.append((best, k, z))
    for (sc, tp, fp, a, b), k, z in sorted(res, reverse=True)[:12]: print(f'   {k:8s} best {tp}/8 tight, {fp} normal in ({a:.2f},{b:.2f})  zones(tight,normal) {z}')
