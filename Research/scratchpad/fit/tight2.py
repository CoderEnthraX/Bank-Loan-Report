import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
exec(open('fpfeat.py').read().split('rows = []')[0])
from halfstop import ema
X = []
for t in tr:
    P = recover(t['sym']); T = P['T']
    if t['fill'] not in T or not t['entry'] or not t['stop']: continue
    a = arm_of(t); i = T.index(a); d = t['d']; O, H, L, C, V = P['O'], P['H'], P['L'], P['C'], P['V']
    A = P[('atr', 14)][i]; sd = P['vsd'][i] or 1e-9; e = t['entry']
    tight = d * (e - t['stop']) / A < 1.5
    k = P['sinceStart'][i]; ds = i - k
    f = {}
    f['s18-vwap/A'] = d * (e - d * 1.8 * A - V[i]) / A
    f['s18-vwap/sd'] = d * (e - d * 1.8 * A - V[i]) / sd
    f['s09-vwap/A'] = d * (e - d * 0.9 * A - V[i]) / A
    f['e-vwap/A'] = d * (e - V[i]) / A
    f['e-vwap/sd'] = d * (e - V[i]) / sd
    f['sd/A'] = sd / A
    f['dayRange/A'] = (max(H[ds:i+1]) - min(L[ds:i+1])) / A
    f['A/A50'] = A / (sum(P['tr'][i-49:i+1]) / 50)
    f['A/A100'] = A / (sum(P['tr'][i-99:i+1]) / 100)
    f['A/Aday'] = A / (sum(P['tr'][i-287:i+1]) / 288)
    f['e-dayExtOpp/A'] = d * (e - (min(L[ds:i+1]) if d > 0 else max(H[ds:i+1]))) / A
    f['e-dayExt/A'] = d * (e - (max(H[ds:i]) if d > 0 else min(L[ds:i]))) / A if i > ds else 0
    X.append((t['sym'], a, tight, f))
print(len(X), sum(x[2] for x in X))
for key in X[0][3]:
    vals = sorted((x[3][key], x[2]) for x in X); best = (0,)
    for j in range(len(vals) + 1):
        thr = (vals[j - 1][0] + vals[j][0]) / 2 if 0 < j < len(vals) else (vals[0][0] - 1 if j == 0 else vals[-1][0] + 1)
        for sign in (1, -1):
            acc = sum((sign * (x[3][key] - thr) > 0) == x[2] for x in X)
            if acc > best[0]: best = (acc, sign, thr)
    tv = sorted(round(x[3][key], 2) for x in X if x[2])
    print(f"{key:14s} best {best[0]}/{len(X)} tight if {'+' if best[1]>0 else '-'}x > {best[2]:+.3f}   tight vals {tv}")
