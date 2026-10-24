"""Among V1-positive arms (8 tight + 4 FP), search a 3rd condition (price + daily + sequence feats)."""
import sys
sys.path.insert(0, '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fit'); sys.path.insert(0, D := '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fit/hunt/stop_sequence')
from engine2 import prepare
from tightdata import TRADES
from pfeat import pf
from fdlib import first_today, prevday
import copy
items = []
for t in TRADES:
    tt = dict(t)
    if t['sym'] == 'US30' and t['fill'] == '2026-10-07 05:30':
        P = prepare('US30'); tt['arm_i'] = P['T'].index('2026-10-07 05:10'); tt['arm'] = '2026-10-07 05:10'
    P = prepare(tt['sym']); i = tt['arm_i']; d = tt['d']; A = P[('atr', 14)][i]
    pd, p2, td = prevday(P, i, True)
    if not (first_today(P, i, d, ('vsl',), True) and d * (pd['c'] - p2['c']) < 0): continue
    f = pf(tt)
    f['pdBody'] = d * (pd['c'] - pd['o']) / A; f['pd2'] = d * (pd['c'] - p2['c']) / A; f['pdRng'] = (pd['h'] - pd['l']) / A
    f['c-pdO'] = d * (P['C'][i] - pd['o']) / A; f['c-pdC'] = d * (P['C'][i] - pd['c']) / A; f['gapPd'] = d * (td['o'] - pd['c']) / A
    f['p2Body'] = d * (p2['c'] - p2['o']) / A; f['tdO-pdO'] = d * (td['o'] - pd['o']) / A
    f['pdClosePos'] = (((pd['c'] - pd['l']) if d > 0 else (pd['h'] - pd['c'])) / (pd['h'] - pd['l']))
    f['atrPct'] = A / P['C'][i] * 100
    items.append((tt, f))
print(len(items), [f"{t['sym']} {t['fill'][5:]} {'T' if t['tight'] else 'N'}" for t, _ in items])
y = [t['tight'] for t, _ in items]; res = []
for k in items[0][1]:
    vals = sorted({f[k] for _, f in items})
    for th in vals:
        for sg in (1, -1):
            p = [sg * f[k] >= sg * th for _, f in items]
            err = sum(a != b for a, b in zip(p, y))
            res.append((err, k, '>=' if sg > 0 else '<=', round(th, 3)))
res.sort(); seen = set()
for r in res:
    if r[1] in seen: continue
    seen.add(r[1]); print(r)
    if len(seen) > 25: break
K = ['pdBody','pd2','pdRng','c-pdO','c-pdC','gapPd','since','dVW','rng','mom10','adx','atrRel50','oppSigDay','hr']
for t, f in items: print(f"{t['sym']:6s} {t['fill'][5:]} {'T' if t['tight'] else 'N'}", ' '.join(f"{k}={f[k]:.2f}" for k in K))
