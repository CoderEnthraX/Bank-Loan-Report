import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gtscore import load_gt
from volrec import recover
from engine import rma
from adxfit import dmi
tr, win = load_gt(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'gt', 'final'))
FP = [('CRUDE','2026-10-06 20:55',1),('CRUDE','2026-10-06 21:10',1),('CRUDE','2026-10-06 21:30',1),('CRUDE','2026-10-07 10:20',-1),
      ('ETH','2026-10-10 03:30',-1),('ETH','2026-10-10 05:30',-1),('ETH','2026-10-10 05:45',1),('ETH','2026-10-11 00:05',1),
      ('EURUSD','2026-10-09 12:15',-1),('EURUSD','2026-10-12 04:55',1),('EURUSD','2026-10-12 05:05',1),('EURUSD','2026-10-12 08:15',-1),
      ('GC','2026-10-09 16:35',-1),('NASDAQ','2026-10-12 05:00',1),('NASDAQ','2026-10-12 08:45',-1),
      ('NIFTY','2026-10-07 09:35',-1),('NIFTY','2026-10-07 13:05',-1),('NIFTY','2026-10-08 12:15',-1)]
def arm_of(t):
    P = recover(t['sym']); T = P['T']; O, H, L, C = P['O'], P['H'], P['L'], P['C']
    if ('atr', 14) not in P: P[('atr', 14)] = rma(P['tr'], 14)
    A = P[('atr', 14)]; fi = T.index(t['fill']); d = t['d']; best = None
    for k in range(1, 10):
        j = fi - k; mid = (O[j] + C[j]) / 2
        lv = max(H[j - 6:j]) if d > 0 else min(L[j - 6:j]); e = max(mid, lv) if d > 0 else min(mid, lv)
        brk = C[j] > max(H[j - 10:j]) if d > 0 else C[j] < min(L[j - 10:j])
        sc = abs(e - t['entry']) / A[j] + (0 if brk else 0.5) + 0.01 * k
        if best is None or sc < best[0]: best = (sc, j)
    return T[best[1]]
def feat(sym, t, d):
    P = recover(sym); T = P['T']; i = T.index(t); O, H, L, C, V = P['O'], P['H'], P['L'], P['C'], P['V']
    if ('atr', 14) not in P: P[('atr', 14)] = rma(P['tr'], 14)
    if 'dmi' not in P: P['dmi'] = dmi(P['rows'], 14, 14)
    A = P[('atr', 14)][i]; dip, dim, adx = P['dmi']; sd = P['vsd'][i] or 1e-9
    rng = H[i] - L[i]
    k = P['sinceStart'][i]; ds = i - k
    dayH = max(H[ds:i]) if i > ds else H[i]; dayL = min(L[ds:i]) if i > ds else L[i]
    newext = (C[i] > dayH) if d > 0 else (C[i] < dayL)
    return dict(ov=d*(O[i]-V[i])/A, cv=d*(C[i]-V[i])/A, z=d*(C[i]-V[i])/sd, rng=rng/A, body=abs(C[i]-O[i])/A,
                adx=adx[i], di=d*(dip[i]-dim[i]), since=k, newDayExt=int(newext), lowv=d*((L[i] if d>0 else H[i])-V[i])/A,
                vslope=d*(V[i]-V[i-3])/A)
rows = []
for t in tr:
    if t['fill'] not in recover(t['sym'])['T'] or not t['entry']: continue
    a = arm_of(t); rows.append(('TP', t['sym'], a, t['d'], feat(t['sym'], a, t['d'])))
for s, a, d in FP: rows.append(('FP', s, a, d, feat(s, a, d)))
keys = list(rows[0][4])
for k in keys:
    tp = sorted(r[4][k] for r in rows if r[0] == 'TP'); fp = sorted(r[4][k] for r in rows if r[0] == 'FP')
    print(f"{k:9s} TP min {tp[0]:7.2f} p10 {tp[len(tp)//10]:7.2f} med {tp[len(tp)//2]:7.2f} max {tp[-1]:7.2f} | FP {' '.join('%.2f'%x for x in fp)}")
for r in rows:
    if r[0]=='FP': print(r[0], r[1], r[2], r[3], {k: round(v, 2) for k, v in r[4].items()})
