"""Exhaustive: can 2 or 3 CLEAN intervals (0 normals inside) on any features cover all 8 tight? (overfit check)"""
import sys, pickle, itertools; sys.path.insert(0,'/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fit/hunt/stop_levels')
from dispser import *; from vfeat import vfeat
rows = []
for t in TRADES:
    P = prepare(t['sym']); i = t['arm_i']; A = P[('atr',14)][i]; d = t['d']; e = t['entry']
    x = allfeat(P, i, d, e, A); x.update(pfeat(P, i, d, e, A)); x.update(vfeat(P, i, d, e, A))
    O,H,L,C = P['O'],P['H'],P['L'],P['C']
    x['rngA'] = (H[i]-L[i])/A; x['bodyA'] = abs(C[i]-O[i])/A; x['bodyP'] = abs(C[i]-O[i])/(H[i]-L[i]); x['brkA'] = d*(C[i]-(max(H[i-10:i]) if d>0 else min(L[i-10:i])))/A
    x['momA'] = d*(C[i]-C[i-10])/A; x['ent_mid'] = d*(e-(O[i]+C[i])/2)/A
    rows.append((t, x))
pickle.dump(rows, open('/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fit/hunt/stop_levels/feat2.pkl','wb'))
keys = sorted({k for _, x in rows for k in x})
tight = [j for j, (t, x) in enumerate(rows) if t['tight']]
cl = {}  # tightset(frozenset) -> list of (feature, a, b)
for k in keys:
    vals = sorted([(x[k], j, t['tight']) for j, (t, x) in enumerate(rows) if x.get(k) is not None])
    n = len(vals)
    # maximal runs of consecutive tight values without normals (in sorted order; ties broken conservatively)
    run = []
    for v, j, tg in vals + [(None, None, False)]:
        if tg: run.append((v, j))
        else:
            if run:
                # ensure no normal shares the value range
                lo, hi = run[0][0], run[-1][0]
                if not any((not tg2) and lo <= v2 <= hi for v2, j2, tg2 in vals):
                    cl.setdefault(frozenset(j for _, j in run), []).append((k, lo, hi))
            run = []
sets = list(cl)
print('distinct clean tight-subsets', len(sets), 'max size', max(len(s) for s in sets))
full = frozenset(tight)
for a, b in itertools.combinations(sets, 2):
    if a | b == full: print('PAIR', cl[a][:3], '|', cl[b][:3])
cnt = 0; TR = []
for a, b, c in itertools.combinations([s for s in sets if len(s) >= 2], 3):
    if a | b | c == full: cnt += 1; TR.append((cl[a][:2], cl[b][:2], cl[c][:2]))
print('triples covering all 8:', cnt)
for s in sorted(sets, key=len, reverse=True)[:12]:
    print(len(s), [rows[j][0]['sym'] + ' ' + rows[j][0]['arm'][5:] for j in sorted(s)], cl[s][:4])
print('TRIPLES', TR)
