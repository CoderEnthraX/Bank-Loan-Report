import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gtscore import load_gt
from engine2 import prepare
from engine import rma
tr, win = load_gt(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'gt', 'final'))
rows = []
for t in sorted(tr, key=lambda t: (t['sym'], t['fill'])):
    P = prepare(t['sym']); T = P['T']; O, H, L, C = P['O'], P['H'], P['L'], P['C']
    if ('atr', 14) not in P: P[('atr', 14)] = rma(P['tr'], 14)
    A = P[('atr', 14)]
    if t['fill'] not in T or not t['entry'] or not t['stop']: continue
    fi = T.index(t['fill']); d = t['d']; best = None
    for k in range(1, 10):
        j = fi - k; mid = (O[j] + C[j]) / 2
        lv = max(H[j - 6:j]) if d > 0 else min(L[j - 6:j]); e = max(mid, lv) if d > 0 else min(mid, lv)
        brk = C[j] > max(H[j - 10:j]) if d > 0 else C[j] < min(L[j - 10:j])
        sc = abs(e - t['entry']) / A[j] + (0 if brk else 0.5) + 0.01 * k
        if best is None or sc < best[0]: best = (sc, j)
    j = best[1]; e = t['entry']; sd = d * (e - t['stop']) / A[j]
    tight = sd < 1.7
    rows.append((t, j, e, sd, tight, P, A))
def test(fn, name):
    ok = 0; bad = []
    for t, j, e, sd, tight, P, A in rows:
        dist = fn(P, j, t['d'], e) / A[j]
        pred = min(max(dist, 0.9), 1.8)
        if abs(pred - sd) < 0.06: ok += 1
        else: bad.append(f"{t['sym']} {t['fill'][5:]} {'T' if tight else 'N'} sd{sd:.2f} pred{pred:.2f}")
    return ok, bad
res = []
for N in range(1, 31):
    for inc in (0, 1):
        for src in ('wick', 'body', 'close'):
            def fn(P, j, d, e, N=N, inc=inc, src=src):
                H, L, O, C = P['H'], P['L'], P['O'], P['C']
                rng = range(j - N + inc, j + inc)
                if src == 'wick': lv = min(L[x] for x in rng) if d > 0 else max(H[x] for x in rng)
                elif src == 'body': lv = min(min(O[x], C[x]) for x in rng) if d > 0 else max(max(O[x], C[x]) for x in rng)
                else: lv = min(C[x] for x in rng) if d > 0 else max(C[x] for x in rng)
                return d * (e - lv)
            ok, bad = test(fn, '')
            res.append((ok, N, inc, src, bad))
res.sort(key=lambda r: -r[0])
print('n trades', len(rows), 'tight', sum(r[4] for r in rows))
for ok, N, inc, src, bad in res[:8]: print(ok, 'N', N, 'incImpulse', inc, src, bad[:12])
print('--- pivots')
res = []
for a in range(1, 11):
    for b in range(1, 11):
        for mode in ('last', 'lastBelow', 'nearestBelow'):
            def fn(P, j, d, e, a=a, b=b, mode=mode):
                H, L = P['H'], P['L']
                piv = []
                for p in range(j - b, max(j - 400, a), -1):
                    if p + b > j: continue
                    if d > 0:
                        v = L[p]
                        if all(L[q] > v for q in range(p - a, p)) and all(L[q] >= v for q in range(p + 1, p + b + 1)): piv.append(v)
                    else:
                        v = H[p]
                        if all(H[q] < v for q in range(p - a, p)) and all(H[q] <= v for q in range(p + 1, p + b + 1)): piv.append(v)
                    if len(piv) > 30: break
                if not piv: return 99
                if mode == 'last': return d * (e - piv[0])
                bel = [v for v in piv if d * (e - v) > 0]
                if not bel: return 99
                if mode == 'lastBelow': return d * (e - bel[0])
                return min(d * (e - v) for v in bel[:5])
            ok, bad = test(fn, '')
            res.append((ok, a, b, mode, bad))
res.sort(key=lambda r: -r[0])
for ok, a, b, mode, bad in res[:8]: print(ok, a, b, mode, bad[:10])
