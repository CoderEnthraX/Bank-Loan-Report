import sys, os, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
exec(open('fpfeat.py').read().split('rows = []')[0])
from engine2 import hh, ll
FP = [('CRUDE','2026-10-06 20:55',1),('CRUDE','2026-10-06 21:10',1),('CRUDE','2026-10-06 21:30',1),('CRUDE','2026-10-07 10:20',-1),
      ('ETH','2026-10-10 03:30',-1),('ETH','2026-10-10 05:30',-1),('ETH','2026-10-10 05:45',1),('ETH','2026-10-11 00:05',1),
      ('NIFTY','2026-10-07 09:35',-1),('NIFTY','2026-10-07 13:05',-1),('NIFTY','2026-10-08 12:15',-1),('CRUDE','2026-10-07 17:55',1)]
def F(s, a, d):
    P = recover(s); T = P['T']; i = T.index(a); O, H, L, C, V = P['O'], P['H'], P['L'], P['C'], P['V']; vol = P['vol']
    feat(s, a, d); A = P[('atr', 14)][i]; dip, dim, adx = P['dmi']; sd = P['vsd'][i] or 1e-9; k = P['sinceStart'][i]; ds = i - k
    rng = H[i] - L[i]; body = abs(C[i] - O[i]); f = {}
    def rv(n):
        pv = [vol[j] for j in range(max(ds, i - n), i) if vol[j] is not None]
        return vol[i] / (sum(pv) / len(pv)) if pv and vol[i] and sum(pv) > 0 else 1.0
    f['relvol10'] = rv(10); f['relvol20'] = rv(20); f['relvol50'] = rv(50)
    f['upwick/A'] = (H[i] - max(O[i], C[i])) / A if d > 0 else (min(O[i], C[i]) - L[i]) / A
    f['backwick/A'] = (min(O[i], C[i]) - L[i]) / A if d > 0 else (H[i] - max(O[i], C[i])) / A
    f['brk10/A'] = d * (C[i] - (hh(H, i, 10) if d > 0 else ll(L, i, 10))) / A
    f['brk10/rng'] = f['brk10/A'] * A / rng
    f['prevbar_dir'] = d * (C[i - 1] - O[i - 1]) / A
    f['prev2'] = d * (C[i - 1] - C[i - 3]) / A
    f['mom10'] = d * (C[i] - C[i - 10]) / A
    f['mom20'] = d * (C[i] - C[i - 20]) / A
    f['range10/A'] = (hh(H, i, 10) - ll(L, i, 10)) / A
    f['range20/A'] = (hh(H, i, 20) - ll(L, i, 20)) / A
    f['A/A50'] = A / (sum(P['tr'][i - 49:i + 1]) / 50)
    f['tr/A'] = P['tr'][i] / A
    f['dayExtDist/A'] = d * (C[i] - (max(H[ds:i]) if d > 0 else min(L[ds:i]))) / A if i > ds else 0
    f['dayOppDist/A'] = d * (C[i] - (min(L[ds:i + 1]) if d > 0 else max(H[ds:i + 1]))) / A
    f['vwapCross10'] = sum(1 for j in range(i - 10, i) if (C[j] - V[j]) * (C[j - 1] - V[j - 1]) < 0)
    f['barsAboveV10'] = sum(1 for j in range(i - 10, i) if d * (C[j] - V[j]) > 0)
    f['barsAboveV20'] = sum(1 for j in range(i - 20, i) if d * (C[j] - V[j]) > 0)
    f['diPlusAl'] = (dip[i] if d > 0 else dim[i]); f['diOpp'] = (dim[i] if d > 0 else dip[i])
    f['adx'] = adx[i]; f['adxSlope'] = adx[i] - adx[i - 3]
    f['z'] = d * (C[i] - V[i]) / sd; f['cv'] = d * (C[i] - V[i]) / A
    f['since'] = k; f['hourIST'] = int(a[11:13]) + int(a[14:16]) / 60
    f['sd/A'] = sd / A
    return f
rows = []
for t in tr:
    if t['fill'] not in recover(t['sym'])['T'] or not t['entry']: continue
    a = arm_of(t); rows.append(('TP', t['sym'], a, F(t['sym'], a, t['d'])))
for s, a, d in FP: rows.append(('FP', s, a, F(s, a, d)))
for key in rows[0][3]:
    tp = [r[3][key] for r in rows if r[0] == 'TP']; fps = [(r[3][key], r[1] + ' ' + r[2][5:]) for r in rows if r[0] == 'FP']
    lo, hi = min(tp), max(tp)
    below = [n for v, n in fps if v < lo]; above = [n for v, n in fps if v > hi]
    if below or above: print(f"{key:12s} TP range [{lo:.3f}, {hi:.3f}]  FP below: {below}  FP above: {above}")
