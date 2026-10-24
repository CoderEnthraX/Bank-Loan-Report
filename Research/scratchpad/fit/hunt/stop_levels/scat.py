import sys; sys.path.insert(0,'/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fit/hunt/stop_levels')
from lv import *
pts = []
for t in TRADES:
    P = prepare(t['sym']); recover(t['sym']); i = t['arm_i']; A = P[('atr',14)][i]; d = t['d']
    u = d*(t['entry']-P['V'][i])/A; w = (P['vsd'][i] or 0)/A
    pts.append((u, w, t))
for u, w, t in sorted(pts, key=lambda p: p[1]):
    print(f"{'TIGHT' if t['tight'] else '     '} u(entry-vwap)/A={u:6.2f} sd/A={w:5.2f} u/sd={u/w if w else 0:6.2f} {t['sym']} {t['arm']} since={prepare(t['sym'])['sinceStart'][t['arm_i']]}")
