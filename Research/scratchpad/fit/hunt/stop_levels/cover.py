"""For each feature: minimal interval covering all 8 tight values -> mask of normals inside. Then AND pairs/triples."""
import sys, itertools, pickle, os; sys.path.insert(0,'/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fit/hunt/stop_levels')
from lv import *
cache = '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fit/hunt/stop_levels/feat.pkl'
rows = []
for t in TRADES:
    P = prepare(t['sym']); i = t['arm_i']; A = P[('atr',14)][i]
    rows.append((t, allfeat(P, i, t['d'], t['entry'], A)))
pickle.dump([(dict((k, v) for k, v in t.items()), x) for t, x in rows], open(cache, 'wb'))
keys = sorted({k for _, x in rows for k in x})
M = {}
for k in keys:
    tv = [x.get(k) for t, x in rows if t['tight']]
    if any(v is None for v in tv): continue
    lo, hi = min(tv), max(tv)
    m = 0
    for j, (t, x) in enumerate(rows):
        v = x.get(k)
        if not t['tight'] and v is not None and lo <= v <= hi: m |= 1 << j
    M[k] = (m, lo, hi)
nb = lambda m: bin(m).count('1')
print('single best:')
for k, (m, lo, hi) in sorted(M.items(), key=lambda kv: nb(kv[1][0]))[:15]: print(f'  {k} [{lo:.2f},{hi:.2f}] normals inside {nb(m)}')
print('pairs best:')
ks = list(M); pr = []
for a, b in itertools.combinations(ks, 2): pr.append((nb(M[a][0] & M[b][0]), a, b))
pr.sort()
for c, a, b in pr[:25]: print(f'  {c}  {a}[{M[a][1]:.2f},{M[a][2]:.2f}] & {b}[{M[b][1]:.2f},{M[b][2]:.2f}]')
