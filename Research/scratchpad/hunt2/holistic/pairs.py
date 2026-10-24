import sys, json, os, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ev import ev, fmt
from grid import GRID
import m as M
base = json.loads(sys.argv[1]); thr = int(sys.argv[2])
b = ev(base); print('BASE', fmt(b), flush=True)
singles = []
G = dict(GRID); G.update(rearmMode=[None, 'better', 'worse', 'oppKeep'], atrLen=[10, 12, 14, 16, 20])
for k, vals in G.items():
    for v in vals:
        if v == base.get(k, M.IN[k]): continue
        c = dict(base); c[k] = v; r = ev(c)
        if r['obj'] >= b['obj'] - thr: singles.append((k, v, r))
print('singles', [(k, v, r['obj']) for k, v, r in singles], flush=True)
best = b['obj']
for a in range(len(singles)):
    for c2 in range(a + 1, len(singles)):
        k1, v1, r1 = singles[a]; k2, v2, r2 = singles[c2]
        if k1 == k2: continue
        c = dict(base); c[k1] = v1; c[k2] = v2; r = ev(c)
        if r['obj'] >= b['obj']:
            print(f"{k1}={v1} + {k2}={v2}: {fmt(r)} GAIN {sorted(b['bad']-r['bad'])} LOSE {sorted(r['bad']-b['bad'])}", flush=True)
print('DONE', flush=True)
