import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gtscore import load_gt
from engine2 import prepare
from engine import rma
tr, win = load_gt(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'gt', 'final'))
for t in sorted(tr, key=lambda t: (t['sym'], t['fill'])):
    P = prepare(t['sym']); T = P['T']; O, H, L, C, V = P['O'], P['H'], P['L'], P['C'], P['V']
    if ('atr', 14) not in P: P[('atr', 14)] = rma(P['tr'], 14)
    A = P[('atr', 14)]
    if t['fill'] not in T or not t['entry'] or not t['stop']: print(t['sym'], t['fill'], '?'); continue
    fi = T.index(t['fill']); d = t['d']; best = None
    for k in range(1, 10):
        j = fi - k; mid = (O[j] + C[j]) / 2
        lv = max(H[j - 6:j]) if d > 0 else min(L[j - 6:j]); e = max(mid, lv) if d > 0 else min(mid, lv)
        brk = C[j] > max(H[j - 10:j]) if d > 0 else C[j] < min(L[j - 10:j])
        sc = abs(e - t['entry']) / A[j] + (0 if brk else 0.5) + 0.01 * k
        if best is None or sc < best[0]: best = (sc, j)
    j = best[1]; sd = d * (t['entry'] - t['stop']) / A[j]
    ext = d * (t['entry'] - (L[j] if d > 0 else H[j])) / A[j]
    print(f"{t['sym']:6s} {t['fill']} {'L' if d>0 else 'S'} {'TIGHT' if sd<1.7 else '     '} sd {sd:4.2f} impExt {ext:4.2f} exit {t['exit']} {t['out']}  since {P['sinceStart'][j]}")
