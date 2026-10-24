import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
exec(open('fpfeat.py').read().split('rows = []')[0])
X = []
for t in tr:
    P = recover(t['sym']); T = P['T']
    if t['fill'] not in T or not t['entry'] or not t['stop']: continue
    a = arm_of(t); i = T.index(a); f = T.index(t['fill']); d = t['d']; O, H, L, C, V = P['O'], P['H'], P['L'], P['C'], P['V']
    A = P[('atr', 14)][i]; e = t['entry']
    tight = d * (e - t['stop']) / A < 1.5
    pen = d * (e - (L[f] if d > 0 else H[f])) / A
    fo = d * (O[f] - e) / A
    fc = d * (C[f] - e) / A
    # bars between arm and fill: did any bar come within x of entry?
    near = min(d * ((L[x] if d > 0 else H[x]) - e) / A for x in range(i + 1, f)) if f > i + 1 else 9
    X.append((t['sym'], t['fill'], tight, dict(k=f - i, pen=pen, fo=fo, fc=fc, near=near, Afill_A=P[('atr', 14)][f] / A,
              cl_e=d*(C[i]-e)/A, src=int(abs(e-(O[i]+C[i])/2) < 1e-9 * max(1, abs(e))))))
for x in sorted(X, key=lambda x: -x[2]):
    print('T' if x[2] else ' ', x[0], x[1], {k: round(v, 2) for k, v in x[3].items()})
