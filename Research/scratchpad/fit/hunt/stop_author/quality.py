"""Signal-quality score rules: score = #(component beyond threshold); tight iff score>=k (or <=k). Exhaustive over 2-4 components x small grids."""
import sys, itertools, pickle; sys.path.insert(0, '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fit/hunt/stop_author')
from alib import *
from tightdata import TRADES
Q = []
for t in TRADES:
    P = get(t['sym']); i = t['arm_i']; d = t['d']; A = P[('atr', 14)][i]
    O, H, L, C, V = P['O'], P['H'], P['L'], P['C'], P['V']; rng = H[i] - L[i]
    vol = P['vol']; vr = (vol[i] or 0) / max(1e-9, sum((vol[j] or 0) for j in range(i - 20, i)) / 20)
    q = dict(body=abs(C[i] - O[i]) / rng * 100, clos=((H[i] - C[i]) if d > 0 else (C[i] - L[i])) / rng * 100, rngA=rng / A,
             brk=d * (C[i] - (max(H[i - 10:i]) if d > 0 else min(L[i - 10:i]))) / A, mom=d * (C[i] - C[i - 10]) / A, cv=d * (C[i] - V[i]) / A,
             cvs=d * (C[i] - V[i]) / (P['vsd'][i] or 1e9), vsl=d * (V[i] - V[i - 3]) / A, adx=P['dmi'][2][i], vr=vr,
             ent=d * (t['entry'] - (O[i] + C[i]) / 2) / A, bodyA=abs(C[i] - O[i]) / A, tight=t['tight'], name=f"{t['sym']} {t['fill'][5:]}")
    Q.append(q)
pickle.dump(Q, open('/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fit/hunt/stop_author/quality.pkl', 'wb'))
G = dict(body=[60, 65, 70, 75, 80, 85, 90], clos=[5, 10, 15, 20], rngA=[1.0, 1.2, 1.5, 2.0], brk=[0.1, 0.25, 0.5, 1.0], mom=[1.5, 2, 3, 4, 5],
         cv=[0.5, 1, 1.5, 2, 2.5, 3], cvs=[0.5, 1, 1.5, 2], vsl=[0.1, 0.25, 0.5, 1], adx=[20, 25, 30, 40], vr=[1, 1.5, 2, 3], bodyA=[0.5, 0.75, 1.0, 1.5])
comps = list(G)
print('tight values:'); [print('  ', q['name'], {k: round(q[k], 2) for k in comps}) for q in Q if q['tight']]
best = []
for r in (2, 3, 4):
    for cs in itertools.combinations(comps, r):
        for ths in itertools.product(*[[(th, s) for th in G[c] for s in (1, -1)] for c in cs]):
            sc = [sum(1 for c, (th, s) in zip(cs, ths) if s * (q[c] - th) >= 0) for q in Q]
            for k in range(1, r + 1):
                tp = sum(1 for v, q in zip(sc, Q) if v >= k and q['tight']); fp = sum(1 for v, q in zip(sc, Q) if v >= k and not q['tight'])
                best.append((8 - tp + fp, tp, fp, cs, ths, k))
best.sort(key=lambda x: (x[0], len(x[3])))
for b in best[:15]: print(b)
