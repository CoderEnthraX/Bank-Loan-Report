import sys
sys.path.insert(0,'/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fit/hunt/stop_sequence')
from feat import *
from sig import raw
rows, out = table(True)
for t, f in rows:
    if not f: continue
    P = prepare(t['sym']); S = raw(P); i = t['arm_i']; d = t['d']
    ds = i - P['sinceStart'][i]
    for N in (6, 12, 24, 48, 96):
        f[f'sameSig{N}'] = sum(1 for j in range(max(0, i - N), i) if S[j] == d)
        f[f'oppSig{N}'] = sum(1 for j in range(max(0, i - N), i) if S[j] == -d)
    f['sameSigDay'] = sum(1 for j in range(ds, i) if S[j] == d); f['oppSigDay'] = sum(1 for j in range(ds, i) if S[j] == -d)
    lo = [j for j in range(0, i) if S[j] == -d]; ls = [j for j in range(0, i) if S[j] == d]
    f['barsOpp'] = i - lo[-1] if lo else 9999; f['barsSame'] = i - ls[-1] if ls else 9999
    f['lastSigOpp'] = int(bool(lo) and (not ls or lo[-1] > ls[-1]))
    f['firstSigDay'] = int(f['sameSigDay'] + f['oppSigDay'] == 0)
res, n = sep(rows)
seen = set()
for r in res:
    if r[2] in seen: continue
    seen.add(r[2]); print(r)
    if len(seen) > 15: break
K = ['sameSig12','oppSig12','sameSig48','oppSig48','sameSigDay','oppSigDay','barsOpp','barsSame','lastSigOpp','firstSigDay']
for t, f in rows:
    if f: print(f"{t['sym']:6s} {t['fill'][5:]} {'L' if t['d']>0 else 'S'} {'T' if t['tight'] else ' '}", ' '.join(f"{k}={f[k]}" for k in K))
