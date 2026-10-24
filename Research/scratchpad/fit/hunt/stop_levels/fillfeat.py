"""same level features evaluated at the fill bar (and fill-1), entry/A from arm bar"""
import sys, itertools; sys.path.insert(0,'/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fit/hunt/stop_levels')
from lv import *
for off, nm in ((0, 'fill'), (-1, 'fill-1')):
    rows = []
    for t in TRADES:
        P = prepare(t['sym']); i = t['arm_i']; A = P[('atr',14)][i]; j = t['fill_i'] + off
        x = nlevels(P, j, t['d'], t['entry'], A); x.update(adrfeat(P, j, t['d'], t['entry'], A))
        f = t['fill_i']; d = t['d']
        x['fpen'] = d*(t['entry'] - (P['L'][f] if d > 0 else P['H'][f]))/A
        x['fclose'] = d*(P['C'][f]-t['entry'])/A
        x['fcv'] = d*(P['C'][f]-P['V'][f])/A
        rows.append((t, x))
    keys = sorted({k for _, x in rows for k in x}); res = []
    for k in keys:
        vals = [(x.get(k), t['tight']) for t, x in rows if x.get(k) is not None]
        vs = sorted(set(v for v, _ in vals)); cuts = [-1e9] + [(a+b)/2 for a, b in zip(vs, vs[1:])] + [1e9]
        best = None
        for a, b in itertools.combinations(cuts, 2):
            tp = sum(1 for v, tg in vals if tg and a < v < b); fp = sum(1 for v, tg in vals if not tg and a < v < b)
            if best is None or tp - fp > best[0]: best = (tp - fp, tp, fp, a, b)
        res.append((best, k))
    print('==', nm)
    for (sc, tp, fp, a, b), k in sorted(res, reverse=True)[:8]: print(f'   {k:12s} {tp}/8 tight, {fp} normal in ({a:.2f},{b:.2f})')
