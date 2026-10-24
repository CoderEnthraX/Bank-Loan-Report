import sys, os, pickle
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, H)
import numpy as np
from collections import Counter
res = pickle.load(open(os.path.join(H, 'grid.pkl'), 'rb'))
keys = ['disp', 'body', 'close', 'brk', 'wick', 'vslag']
GRID = dict(disp=[0.6, 0.7, 0.8, 0.9, 1.0], body=[45, 50, 55, 60, 65], close=[15, 20, 25, 30, 35], brk=[6, 8, 10, 12, 14], wick=[True, False], vslag=[0, 2, 3, 4])
BASE = (0.8, 55, 25, 10, True, 3)
allsc = [(v, N, s) for v, r in res.items() for N, s in r['sc'].items()]
print('configs x NET:', len(allsc), ' 80/80:', sum(s == 80 for _, _, s in allsc), ' >=79:', sum(s >= 79 for _, _, s in allsc), ' >=78:', sum(s >= 78 for _, _, s in allsc), ' >=72(never-tight baseline):', sum(s >= 72 for _, _, s in allsc))
print('score hist over grid x NET', sorted(Counter(s for *_, s in allsc).items())[-12:])
best_per_cfg = {v: max(r['sc'].values()) for v, r in res.items()}
print('configs (any NET 1..6) reaching 80:', sum(b == 80 for b in best_per_cfg.values()), '/ 5000;  >=79:', sum(b >= 79 for b in best_per_cfg.values()))
# at NET=3 only
print('at NET=3: 80:', sum(r['sc'][3] == 80 for r in res.values()), ' >=79:', sum(r['sc'][3] >= 79 for r in res.values()), ' >=78:', sum(r['sc'][3] >= 78 for r in res.values()), 'of 5000')
# one-at-a-time perturbation from BASE
print('one-at-a-time from claimed (score at NET=2/3/4):')
for j, k in enumerate(keys):
    row = []
    for val in GRID[k]:
        v = list(BASE); v[j] = val; r = res[tuple(v)]
        row.append(f"{val}:{r['sc'][2]}/{r['sc'][3]}/{r['sc'][4]}")
    print('  ', k, ' '.join(row))
# marginal: fraction of grid at NET=3 with >=79 per parameter value
for j, k in enumerate(keys):
    print('  marg', k, {val: round(np.mean([r['sc'][3] >= 79 for v, r in res.items() if v[j] == val]), 3) for val in GRID[k]})
