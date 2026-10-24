import sys
sys.path.insert(0, D := '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fit/hunt/stop_sequence')
from pfeat import *
T = {(t['sym'], t['fill']): t for t in TRADES}
a = pf(T[('NIFTY', '2026-10-09 10:10')]); b = pf(T[('SENSEX', '2026-10-09 10:10')])
rows = [(t, pf(t)) for t in TRADES]
out = []
for k in a:
    if a[k] == b[k]: continue
    lo, hi = min(a[k], b[k]), max(a[k], b[k]); th = (lo + hi) / 2
    sgn = 1 if a[k] > b[k] else -1   # NIFTY (tight) side
    p = [sgn * f[k] > sgn * th for _, f in rows]
    tp = sum(x and t['tight'] for x, (t, _) in zip(p, rows)); fp = sum(x and not t['tight'] for x, (t, _) in zip(p, rows))
    out.append((8 - tp + fp, k, round(a[k], 3), round(b[k], 3), tp, fp))
out.sort()
for o in out: print(o)
