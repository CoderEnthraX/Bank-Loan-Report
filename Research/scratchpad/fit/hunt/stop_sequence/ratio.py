import sys
sys.path.insert(0, D := '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fit/hunt/stop_sequence')
from feat import *
rows, out = table(True)
for t, f in rows:
    if not f: continue
    s = t['sym']; i = t['arm_i']; d = t['d']; P = prepare(s); A = P[('atr', 14)]; H, L = P['H'], P['L']
    cl = [x for x in out[s] if x['exit'] is not None and x['exit'] <= i]
    k = {}
    for n_ in (1, 2, 3):
        if len(cl) >= n_:
            p = cl[-n_]; pr = p['dir'] * (p['entry'] - p['stop'])
            k[f'atrR{n_}'] = A[i] / A[p['arm']]; k[f'riskR{n_}'] = 1.8 * A[i] / pr
            k[f'rngR{n_}'] = (H[i] - L[i]) / (H[p['arm']] - L[p['arm']])
    k['riskVsAvg5'] = 1.8 * A[i] / (sum(p['dir'] * (p['entry'] - p['stop']) for p in cl[-5:]) / len(cl[-5:]))
    f.clear(); f.update(k)
res, n = sep(rows)
seen = set()
for r in res:
    if r[2] in seen: continue
    seen.add(r[2]); print(r)
