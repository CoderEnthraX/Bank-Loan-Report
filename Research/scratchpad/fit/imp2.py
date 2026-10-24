import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gtscore import load_gt
from volrec import recover
from engine import rma
tr, win = load_gt(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'gt', 'final'))
out = []
for t in sorted(tr, key=lambda t: (t['sym'], t['fill'])):
    P = recover(t['sym']); T = P['T']; O, H, L, C, V = P['O'], P['H'], P['L'], P['C'], P['V']
    if ('atr', 14) not in P: P[('atr', 14)] = rma(P['tr'], 14)
    A = P[('atr', 14)]; mt = P['mt']
    if t['fill'] not in T or not t['entry']: continue
    fi = T.index(t['fill']); d = t['d']; best = None
    for k in range(1, 10):
        j = fi - k
        mid = (O[j] + C[j]) / 2
        cands = [('mid', mid)] + [('lv%d' % n, max(H[j - n:j]) if d > 0 else min(L[j - n:j])) for n in (6,)]
        for nm, v in cands:
            e = abs(v - t['entry']) / A[j]
            s = abs((t['entry'] + (-d) * 1.8 * A[j]) - t['stop']) / A[j] if t['stop'] else 0
            sc = e + 0.3 * s + 0.01 * k
            if best is None or sc < best[0]: best = (sc, j, nm, v, e, s)
    sc, j, nm, v, e, s = best
    rng = H[j] - L[j]; body = abs(C[j] - O[j])
    # largest N such that close breaks the N-bar extreme
    brk = 0
    for n in range(1, 31):
        ok = C[j] > max(H[j - n:j]) if d > 0 else C[j] < min(L[j - n:j])
        if ok: brk = n
        else: break
    ext = ((H[j] - C[j]) if d > 0 else (C[j] - L[j])) / rng * 100
    z = d * (C[j] - V[j]) / P['vsd'][j] if P['vsd'][j] else 0
    lv6 = max(H[j - 6:j]) if d > 0 else min(L[j - 6:j])
    rule = max((O[j] + C[j]) / 2, lv6) if d > 0 else min((O[j] + C[j]) / 2, lv6)
    dirok = (C[j] > O[j]) if d > 0 else (C[j] < O[j])
    print(f"{t['sym']:6s} {t['fill']} {'L' if d>0 else 'S'} arm {T[j][11:]} k{fi-j} src {nm:4s} eErr {e:4.2f} sErr {s:4.2f} | brkN {brk:2d} rng/A {rng/A[j]:4.2f} body% {100*body/rng if rng else 0:5.1f} ext% {ext:5.1f} z {z:+5.2f} dir {'ok' if dirok else 'XX'} ruleE {'=' if abs(rule-t['entry'])/A[j]<0.08 else 'NO'}")
