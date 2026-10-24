import sys
sys.path.insert(0, '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fit/hunt/stop_volatility')
from vlib import *
from tightdata import TRADES
SNAP = [('CRUDE','2026-10-09 13:40','TRANSITION'),('GC','2026-10-12 13:00','TRANSITION'),
        ('NASDAQ','2026-10-12 12:45','RANGING'),('NASDAQ','2026-10-09 13:40','RANGING'),('NIFTY','2026-10-12 12:10','TRENDING'),('NIFTY','2026-10-12 12:40','TRENDING'),
        ('SENSEX','2026-10-12 12:40','TRANSITION'),('US30','2026-10-12 13:00','RANGING')]
F = {}
for s, t, lab in SNAP:
    P = prepare(s)
    if t not in P['T']: print('missing', s, t); continue
    i = P['T'].index(t)
    F[(s, t)] = (lab, features(P, i, -1, P['C'][i]))
keys = sorted(F[('NIFTY', '2026-10-12 12:40')][1])
a = F[('NIFTY', '2026-10-12 12:40')][1]; b = F[('SENSEX', '2026-10-12 12:40')][1]
diff = []
for k in keys:
    if k in b and a[k] is not None and b[k] is not None:
        den = max(abs(a[k]), abs(b[k]), 1e-9)
        diff.append((abs(a[k] - b[k]) / den, k, a[k], b[k]))
diff.sort(reverse=True)
for r in diff[:40]:
    print(f"{r[1]:26s} NIFTY {r[2]:9.4g} SENSEX {r[3]:9.4g} | " + ' '.join(f"{s[:3]}{t[8:10]}{t[11:13]}:{lab[:3]}={F[(s,t)][1].get(r[1], float('nan')):.3g}" for (s, t), (lab, _) in F.items()))
