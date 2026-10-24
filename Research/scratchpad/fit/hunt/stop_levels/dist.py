import sys; sys.path.insert(0,'/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fit/hunt/stop_levels')
from lv import *
keys = sys.argv[1].split(',')
rows = []
for t in TRADES:
    P = prepare(t['sym']); i = t['arm_i']; A = P[('atr',14)][i]
    x = allfeat(P, i, t["d"], t["entry"], A); rows.append((t, x))
for k in keys:
    print('==', k)
    for t, x in sorted(rows, key=lambda r: (r[1].get(k) is None, r[1].get(k) or 0)):
        v = x.get(k)
        print(f"  {'TIGHT' if t['tight'] else '     '} {v if v is None else round(v,2):>7} {t['sym']} {t['fill']} {'L' if t['d']>0 else 'S'} {t['out']}")
