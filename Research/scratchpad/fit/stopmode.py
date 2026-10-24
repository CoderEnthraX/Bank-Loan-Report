import sys, os, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from volrec import recover
from adxfit import dmi
from engine import rma
from gtscore import load_gt
from gtfeat import impulse
from halfstop import ema, htf
def daybounds(P):
    st = [i for i, x in enumerate(P['daystart']) if x]
    return st
tr, win = load_gt(os.path.join(os.path.dirname(__file__), '..', 'gt', 'final'))
X = []
for t in tr:
    P = recover(t['sym']); T = P['T']
    if t['fill'] not in T or not t['stop'] or not t['entry']: continue
    f = T.index(t['fill']); err, i, n, cand, src = impulse(P, f, t['d'], t['entry'])
    if ('atr', 14) not in P: P[('atr', 14)] = rma(P['tr'], 14)
    if 'dmi' not in P: P['dmi'] = dmi(P['rows'], 14, 14)
    A = P[('atr', 14)][i]; O, H, L, C, V = P['O'], P['H'], P['L'], P['C'], P['V']; d = t['d']
    R = abs(t['entry'] - t['stop']) / A
    tight = R < 1.4
    dip, dim, adx = P['dmi']
    k = P['sinceStart'][i]; ds = i - k
    # previous day stats
    pk = P['sinceStart'][ds - 1] if ds > 0 else 0; pds = ds - 1 - pk
    pdH = max(H[pds:ds]) if ds > pds else H[ds]; pdL = min(L[pds:ds]) if ds > pds else L[ds]; pdC = C[ds - 1] if ds > 0 else C[ds]
    pdV = V[ds - 1] if ds > 0 else V[ds]
    dayO = O[ds]
    f_ = {}
    f_['d*(c-prevClose)/A'] = d * (C[i] - pdC) / A
    f_['d*(c-dayOpen)/A'] = d * (C[i] - dayO) / A
    f_['d*(c-prevVWAP)/A'] = d * (C[i] - pdV) / A
    f_['d*(vwap-prevVWAP)/A'] = d * (V[i] - pdV) / A
    f_['d*(dayOpen-prevClose)/A'] = d * (dayO - pdC) / A
    f_['d*(c-prevMid)/A'] = d * (C[i] - (pdH + pdL) / 2) / A
    f_['d*(vwap-dayOpen)/A'] = d * (V[i] - dayO) / A
    f_['DIal'] = d * (dip[i] - dim[i]); f_['ADX'] = adx[i]
    for nn in (20, 50, 100, 200):
        key = ('ema', nn)
        if key not in P: P[key] = ema(C, nn)
        f_[f'd*(c-ema{nn})/A'] = d * (C[i] - P[key][i]) / A
    for mins in (15, 60, 240):
        b, cl, e20, e50 = htf(P, mins); kk = b[i]
        f_[f'h{mins} d*(c-e20)/A'] = d * (cl[kk - 1] - e20[kk - 1]) / A if kk else 0
        f_[f'h{mins} d*(e20-e50)/A'] = d * (e20[kk - 1] - e50[kk - 1]) / A if kk else 0
    f_['impExt/A'] = (t['entry'] - L[i]) / A if d > 0 else (H[i] - t['entry']) / A
    f_['since'] = k
    f_['rng/A'] = (H[i] - L[i]) / A; f_['body/A'] = abs(C[i] - O[i]) / A
    sd = P['vsd'][i] or 1e-9; f_['z'] = d * (C[i] - V[i]) / sd
    f_['d*(open-vwap)/A'] = d * (O[i] - V[i]) / A
    f_['vwapSlope6/A'] = d * (V[i] - V[i - 6]) / A
    X.append((t['sym'], t['fill'], tight, round(R, 2), f_))
print(len(X), 'trades;', sum(x[2] for x in X), 'tight')
best = []
for key in X[0][4]:
    vals = sorted((x[4][key], x[2]) for x in X)
    for j in range(len(vals) + 1):
        thr = (vals[j - 1][0] + vals[j][0]) / 2 if 0 < j < len(vals) else (vals[0][0] - 1 if j == 0 else vals[-1][0] + 1)
        for sign in (1, -1):
            pred = [(sign * (x[4][key] - thr) > 0) for x in X]
            acc = sum(p == x[2] for p, x in zip(pred, X))
            best.append((acc, key, sign, thr))
best.sort(reverse=True)
for b in best[:15]: print(f'  acc {b[0]}/{len(X)}  tight if {"" if b[2] > 0 else "-"}{b[1]} > {b[3]:+.3f}')
for x in X:
    if x[2]: print('TIGHT', x[0], x[1], x[3], {k: round(v, 2) for k, v in x[4].items() if k in ('d*(c-prevClose)/A', 'd*(c-dayOpen)/A', 'h60 d*(c-e20)/A', 'h240 d*(c-e20)/A', 'd*(c-ema200)/A', 'DIal')})
