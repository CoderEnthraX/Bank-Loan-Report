"""grid over event definitions for 'first-of-session' (static, 80 trades), prev-session body against d (< -th*ATR)."""
import sys, itertools
sys.path.insert(0, '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fit/hunt/stop_author')
from dlib import *
from tightdata import TRADES
def comps(P, j, d, N):
    O, H, L, C, V = P['O'], P['H'], P['L'], P['C'], P['V']; A = P[('atr', 14)][j]
    o, h, l, c = O[j], H[j], L[j], C[j]; rng = h - l
    if rng <= 0 or A is None: return None
    return dict(dir=d * (c - o) > 0, rng=rng / A, body=abs(c - o) / rng, clos=((h - c) if d > 0 else (c - l)) / rng,
                brk=(c > max(H[j - N:j])) if d > 0 else (c < min(L[j - N:j])),
                brkw=(h > max(H[j - N:j])) if d > 0 else (l < min(L[j - N:j])),
                vsl=P['sinceStart'][j] < 3 or d * (V[j] - V[j - 3]) > 0, vw=d * (c - V[j]) > 0, mom=d * (c - C[j - 10]) >= 0.85 * A,
                nsh=None)
def ev(cm, spec):
    if cm is None: return False
    for k, v in spec.items():
        if k in ('rng',) and not cm[k] >= v: return False
        if k == 'body' and not cm[k] >= v: return False
        if k == 'clos' and not cm[k] <= v: return False
        if k in ('dir', 'brk', 'brkw', 'vsl', 'vw', 'mom') and v and not cm[k]: return False
    return True
th = float(sys.argv[1]) if len(sys.argv) > 1 else 1.0
merge = True
base = []
for t in TRADES:
    P = prepare(t['sym']); P.setdefault(('atr', 14), rma(P['tr'], 14)); i = t['arm_i']; d = t['d']; A = P[('atr', 14)][i]
    out, idx = sessions(P, merge); k = idx[i]; s1 = out[k - 1]
    pa = d * (s1['c'] - s1['o']) < -th * A
    base.append((t, P, i, d, pa, out[k]['a']))
cache = {}
specs = []
for rng in (None, 0.5, 0.8):
    for body in (None, 0.4, 0.55):
        for clos in (None, 0.25, 0.5):
            for brk in ('brk', 'brkw', None):
                for N in ((5, 10, 20) if brk else (10,)):
                    for vsl in (0, 1):
                        for vw in (0, 1):
                            for mom in (0, 1):
                                s = {'dir': True}
                                if rng: s['rng'] = rng
                                if body: s['body'] = body
                                if clos: s['clos'] = clos
                                if brk: s[brk] = True
                                if vsl: s['vsl'] = True
                                if vw: s['vw'] = True
                                if mom: s['mom'] = True
                                specs.append((N, s))
res = []
for N, s in specs:
    tp = fp = fn = 0; fps = []; fns = []
    for t, P, i, d, pa, a in base:
        if pa:
            first = True
            for j in range(a, i):
                key = (P['sym'], j, d, N)
                if key not in cache: cache[key] = comps(P, j, d, N)
                if ev(cache[key], s): first = False; break
        else: first = False
        if first and t['tight']: tp += 1
        elif first: fp += 1; fps.append(f"{t['sym']} {t['fill'][5:]}")
        elif t['tight']: fn += 1; fns.append(f"{t['sym']} {t['fill'][5:]}")
    res.append((fp + fn, fn, N, s, fps, fns))
res.sort(key=lambda x: (x[0], x[1]))
for x in res[:30]: print(x[0], 'fn', x[1], 'N', x[2], x[3], 'FP', x[4], 'FN', x[5])
