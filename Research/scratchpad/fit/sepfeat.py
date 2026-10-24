import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from volrec import recover
from adxfit import dmi
from engine import rma
from gtscore import load_gt
from gtfeat import impulse
FP = [('CRUDE','2026-10-06 20:55',1),('CRUDE','2026-10-07 10:20',-1),('EURUSD','2026-10-09 12:15',-1),('GC','2026-10-09 16:35',-1),
      ('NIFTY','2026-10-07 09:35',-1),('NIFTY','2026-10-07 13:05',-1),('NIFTY','2026-10-08 12:15',-1)]
def F(sym, t, d):
    P = recover(sym); T = P['T']; i = T.index(t); O, H, L, C, V = P['O'], P['H'], P['L'], P['C'], P['V']
    if ('atr', 14) not in P: P[('atr', 14)] = rma(P['tr'], 14)
    if 'dmi' not in P: P['dmi'] = dmi(P['rows'], 14, 14)
    A = P[('atr', 14)][i]; dip, dim, adx = P['dmi']; vol = P['vol']
    k = P['sinceStart'][i]
    prev = [vol[j] for j in range(max(i - 20, i - k), i) if vol[j] is not None]
    rv = vol[i] / (sum(prev) / len(prev)) if prev and vol[i] is not None and sum(prev) > 0 else float('nan')
    sd = P['vsd'][i] or 1e-9
    return dict(rv=rv, adx=adx[i], dial=d * (dip[i] - dim[i]), since=k, z=d * (C[i] - V[i]) / sd, cv=d * (C[i] - V[i]) / A,
                vsl=d * (V[i] - V[i - 6]) / A, rng=(H[i] - L[i]) / A, body=abs(C[i] - O[i]) / A, hour=t[11:])
tr, win = load_gt(os.path.join(os.path.dirname(__file__), '..', 'gt', 'final'))
print('kind sym     time              relVol  ADX  DIal  since  z(sd)  c-vwap/A vwapSlope6/A rng/A body/A')
rows = []
for t in tr:
    P = recover(t['sym']); T = P['T']
    if t['fill'] not in T: continue
    f = T.index(t['fill']); err, j, n, cand, src = impulse(P, f, t['d'], t['entry'])
    rows.append(('TP', t['sym'], T[j], t['d']))
rows += [('FP', s, tt, d) for s, tt, d in FP]
for kind, s, tt, d in rows:
    f = F(s, tt, d)
    print(f"{kind} {s:7s} {tt} {f['rv']:6.2f} {f['adx']:4.0f} {f['dial']:+5.0f} {f['since']:5d} {f['z']:+6.2f} {f['cv']:+7.2f} {f['vsl']:+8.2f} {f['rng']:6.2f} {f['body']:5.2f}")
