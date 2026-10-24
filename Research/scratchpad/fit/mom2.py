import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
exec(open('mom.py').read().split('for n in range(3, 21)')[0])
for n in range(5, 21):
    for inc in (0, 1):
        tp = []; fp = []
        for kind, s, a, d in rows:
            P = recover(s); i = P['T'].index(a); H, L, C = P['H'], P['L'], P['C']; A = P[('atr', 14)][i]
            seg = range(i - n + inc, i + inc)
            opp = min(L[j] for j in seg) if d > 0 else max(H[j] for j in seg)
            v = d * (C[i] - opp) / A
            (tp if kind == 'TP' else fp).append((v, s + ' ' + a[5:]))
        lo = min(tp)[0]; cut = sorted([(round(v, 2), x) for v, x in fp if v < lo])
        print(n, inc, 'TP min %.3f 2nd %.3f' % (lo, sorted(tp)[1][0]), 'FP cut', len(cut), cut)
