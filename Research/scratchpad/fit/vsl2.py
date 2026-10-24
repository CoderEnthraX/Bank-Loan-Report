import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
exec(open('fpfeat.py').read().split('rows = []')[0])
FP2 = FP + [('CRUDE','2026-10-07 17:55',1),('CRUDE','2026-10-07 12:35',-1)]
rows = []
for t in tr:
    if t['fill'] not in recover(t['sym'])['T'] or not t['entry']: continue
    rows.append(('TP', t['sym'], arm_of(t), t['d']))
rows += [('FP', s, a, d) for s, a, d in FP2]
out = []
for kind, s, a, d in rows:
    P = recover(s); i = P['T'].index(a); V = P['V']; A = P[('atr', 14)][i]
    out.append((d * (V[i] - V[i - 3]) / A, kind, s, a[5:], d * (V[i] - V[i - 3]) / (P['vsd'][i] or 1e-9), d * (V[i] - V[i - 1]) / A))
for o in sorted(out)[:40]: print('%.4f %s %s %s  sd-norm %.3f  lag1 %.4f' % o)
