"""2-feature conjunction search over sequence + raw-signal features (oracle history)."""
import sys, pickle
sys.path.insert(0,'/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fit/hunt/stop_sequence')
from feat import *
from feat2 import tradeinfo
from sig import raw
rows, out = table(True)
for t, f in rows:
    if not f: continue
    s = t['sym']; P = prepare(s); i = t['arm_i']; d = t['d']; S = raw(P)
    prev = [x for x in out[s] if x['exit'] is not None and x['exit'] <= i]
    f.update({'p_' + k: v for k, v in tradeinfo(P, prev[-1]).items()})
    ds = i - P['sinceStart'][i]
    for N in (12, 48):
        f[f'sameSig{N}'] = sum(1 for j in range(max(0, i - N), i) if S[j] == d); f[f'oppSig{N}'] = sum(1 for j in range(max(0, i - N), i) if S[j] == -d)
    f['sameSigDay'] = sum(1 for j in range(ds, i) if S[j] == d); f['oppSigDay'] = sum(1 for j in range(ds, i) if S[j] == -d)
    lo = [j for j in range(0, i) if S[j] == -d]; ls = [j for j in range(0, i) if S[j] == d]
    f['barsOpp'] = i - lo[-1] if lo else 9999; f['barsSame'] = i - ls[-1] if ls else 9999
    f['lastSigOpp'] = int(bool(lo) and (not ls or lo[-1] > ls[-1]))
    f['dirL'] = int(d > 0); f['since'] = P['sinceStart'][i]
rows = [(t, f) for t, f in rows if f]
pickle.dump([(dict(sym=t['sym'], fill=t['fill'], tight=t['tight'], d=t['d']), f) for t, f in rows], open('/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fit/hunt/stop_sequence/rows.pkl', 'wb'))
keys = list(rows[0][1].keys()); y = [t['tight'] for t, _ in rows]
# candidate atoms: (key, op, th) that keep all 8 tight (fn=0) or at most 1 fn
atoms = []
for k in keys:
    vals = sorted({f[k] for _, f in rows})
    for th in vals:
        for sgn in (1, -1):
            p = [sgn * f[k] >= sgn * th for _, f in rows]
            tp = sum(a and b for a, b in zip(p, y)); fp = sum(a and not b for a, b in zip(p, y))
            if tp >= 7: atoms.append((k, sgn, th, p, tp, fp))
print(len(atoms), 'atoms')
best = []
for a in range(len(atoms)):
    for b in range(a + 1, len(atoms)):
        A, B = atoms[a], atoms[b]
        if A[0] == B[0]: continue
        p = [x and z for x, z in zip(A[3], B[3])]
        err = sum(x != z for x, z in zip(p, y))
        if err <= 4: best.append((err, A[0], '>=' if A[1] > 0 else '<=', A[2], B[0], '>=' if B[1] > 0 else '<=', B[2]))
best.sort()
seen = set()
for r in best:
    k = (r[1], r[4])
    if k in seen: continue
    seen.add(k); print(r)
    if len(seen) > 40: break
