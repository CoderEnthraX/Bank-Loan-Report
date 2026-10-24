"""Conjunction search (2 atoms) over sequence (oracle-history) + price features; all 80 where available."""
import sys, pickle
sys.path.insert(0, '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fit/hunt/stop_sequence')
from pfeat import pf
from tightdata import TRADES
rows = pickle.load(open('/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fit/hunt/stop_sequence/rows.pkl', 'rb'))
seq = {(t['sym'], t['fill']): f for t, f in rows}
R = []
for t in TRADES:
    f = dict(pf(t)); s = seq.get((t['sym'], t['fill']))
    if s is None: continue
    for k, v in s.items(): f['q_' + k] = v
    R.append((t, f))
y = [t['tight'] for t, _ in R]; print(len(R), sum(y))
keys = list(R[0][1].keys()); atoms = []
for k in keys:
    vals = sorted({f.get(k, 0) for _, f in R})
    for th in vals:
        for sgn in (1, -1):
            p = [sgn * f.get(k, 0) >= sgn * th for _, f in R]
            tp = sum(a and b for a, b in zip(p, y)); fp = sum(a and not b for a, b in zip(p, y))
            if tp >= 7 and fp <= 50: atoms.append((k, sgn, th, p, tp, fp))
print(len(atoms), 'atoms')
best = []
for a in range(len(atoms)):
    A = atoms[a]
    for b in range(a + 1, len(atoms)):
        B = atoms[b]
        if A[0] == B[0]: continue
        p = [x and z for x, z in zip(A[3], B[3])]
        err = sum(x != z for x, z in zip(p, y))
        if err <= 3: best.append((err, A[0], '>=' if A[1] > 0 else '<=', round(A[2], 3), B[0], '>=' if B[1] > 0 else '<=', round(B[2], 3)))
best.sort(); seen = set()
for r in best:
    k = (r[1], r[4])
    if k in seen: continue
    seen.add(k); print(r)
    if len(seen) > 40: break
