import sys; sys.path.insert(0,'/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fit/hunt/stop_levels')
from lv import *
rows = []
for t in TRADES:
    P = prepare(t['sym']); i = t['arm_i']; A = P[('atr',14)][i]; d = t['d']; e = t['entry']
    x = allfeat(P, i, d, e, A)
    rows.append((t, x))
keys = sorted({k for _, x in rows for k in x})
res = []
for k in keys:
    vals = [(x.get(k), t['tight']) for t, x in rows if x.get(k) is not None]
    vs = sorted(set(v for v, _ in vals))
    cuts = [(a+b)/2 for a, b in zip(vs, vs[1:])]
    best = None
    # interval [a,b] inclusion = tight
    for ia, a in enumerate([-1e9]+cuts):
        for b in ([1e9]+cuts):
            if b <= a: continue
            tp = sum(1 for v, tg in vals if tg and a < v < b); fp = sum(1 for v, tg in vals if not tg and a < v < b)
            sc = tp - fp
            if best is None or sc > best[0]: best = (sc, tp, fp, a, b)
    res.append((best[0], k, best[1:], len(vals)))
for r in sorted(res, reverse=True)[:40]:
    sc, k, (tp, fp, a, b), n = r
    print(f'{k:8s} n={n} tight-in-interval {tp}/8 normal-in {fp}  interval ({a:.2f},{b:.2f})')
