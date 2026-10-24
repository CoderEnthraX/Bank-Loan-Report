import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
exec(open('scan.py').read().split('rows = []\nfor t in tr')[0])
rows = []
for t in tr:
    if t['fill'] not in recover(t['sym'])['T'] or not t['entry']: continue
    rows.append(('TP', t['sym'], arm_of(t), t['d']))
rows += [('FP', s, a, d) for s, a, d in FP]
for n in range(3, 21):
    for src in ('C', 'O', 'mid'):
        tp = []; fp = []
        for kind, s, a, d in rows:
            P = recover(s); i = P['T'].index(a); O, H, L, C = P['O'], P['H'], P['L'], P['C']; A = P[('atr', 14)][i]
            ref = C[i - n] if src == 'C' else (O[i - n + 1] if src == 'O' else (H[i - n] + L[i - n]) / 2)
            v = d * (C[i] - ref) / A
            (tp if kind == 'TP' else fp).append((v, s + ' ' + a[5:]))
        lo = min(tp)[0]; cut = [x for v, x in fp if v < lo]
        if len(cut) >= 3: print(n, src, 'TP min %.3f' % lo, 'TP 2nd %.3f' % sorted(tp)[1][0], 'FP cut', len(cut), cut)
print('---')
out = []
for kind, s, a, d in rows:
    P = recover(s); i = P['T'].index(a); C = P['C']; A = P[('atr', 14)][i]
    out.append((d * (C[i] - C[i - 10]) / A, kind, s, a[5:]))
for o in sorted(out)[:20]: print('%.3f %s %s %s' % o)
