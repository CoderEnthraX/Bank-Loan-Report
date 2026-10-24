"""X = level from the previous same-direction raw signal / arm / trade; dist = d*(entry-X)/A. Want tight <=~1.06 (or <0), normal >=1.8."""
import sys
sys.path.insert(0, '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fit/hunt/stop_sequence')
from rec import *
from sig import raw
out = runall(True)
ARMS = {s: [(a[0], a[1]) for a in REC[s]] for s in REC}
def lv(P, j, d, kind):
    O, H, L, C = P['O'], P['H'], P['L'], P['C']
    return {'ext': L[j] if d > 0 else H[j], 'oppext': H[j] if d > 0 else L[j], 'close': C[j], 'open': O[j], 'mid': (O[j] + C[j]) / 2}[kind]
res = {}
for t in TRADES:
    s = t['sym']; P = prepare(s); i = t['arm_i']; d = t['d']; A = P[('atr', 14)][i]; S = raw(P)
    e = t['entry']; r = {}
    ps = [j for j in range(i) if S[j] == d]; po = [j for j in range(i) if S[j] == -d]
    pa = [a[0] for a in ARMS[s] if a[0] < i and a[1] == d]; pao = [a[0] for a in ARMS[s] if a[0] < i and a[1] == -d]
    tr = [x for x in out[s] if x['fill'] < i]
    trs = [x for x in tr if x['dir'] == d]; tro = [x for x in tr if x['dir'] == -d]
    for kind in ('ext', 'oppext', 'close', 'open', 'mid'):
        if ps: r[f'sig_{kind}'] = d * (e - lv(P, ps[-1], d, kind)) / A
        if po: r[f'osig_{kind}'] = d * (e - lv(P, po[-1], -d, kind)) / A
        if pa: r[f'arm_{kind}'] = d * (e - lv(P, pa[-1], d, kind)) / A
        if pao: r[f'oarm_{kind}'] = d * (e - lv(P, pao[-1], -d, kind)) / A
    if trs: r['trS_entry'] = d * (e - trs[-1]['entry']) / A; r['trS_stop'] = d * (e - trs[-1]['stop']) / A; r['trS_t4'] = d * (e - trs[-1]['t4']) / A
    if tro: r['trO_entry'] = d * (e - tro[-1]['entry']) / A; r['trO_stop'] = d * (e - tro[-1]['stop']) / A; r['trO_t4'] = d * (e - tro[-1]['t4']) / A
    if tr: r['tr_entry'] = d * (e - tr[-1]['entry']) / A; r['tr_stop'] = d * (e - tr[-1]['stop']) / A
    res[(s, t['fill'])] = (t, r)
keys = sorted({k for _, r in res.values() for k in r})
print('key: tight values | normal violators (between 1.06 and 1.8 or <=1.06)')
sc = []
for k in keys:
    tv = [r.get(k) for t, r in res.values() if t['tight']]; nv = [r.get(k) for t, r in res.values() if not t['tight']]
    # tight correct if value <= 1.07 ; normal correct if value >= 1.79 (clamped at 1.8)
    tc = sum(1 for v in tv if v is not None and v <= 1.07); nc = sum(1 for v in nv if v is not None and v >= 1.79)
    sc.append((len(tv) - tc + len(nv) - nc, k, tc, nc, [None if v is None else round(v, 2) for v in tv]))
sc.sort()
for x in sc[:20]: print(x)
