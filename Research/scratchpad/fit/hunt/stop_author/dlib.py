"""daily/session helpers for the first-of-session & prev-session-against rule."""
import sys
FIT = '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fit'
sys.path.insert(0, FIT); sys.path.insert(0, FIT + '/hunt/stop_author')
from engine2 import prepare
from engine import rma
def sessions(P, merge=False, minlen=24):
    key = ('dl_sess', merge, minlen)
    if key in P: return P[key]
    T = P['T']; n = len(T); st = [i for i, x in enumerate(P['daystart']) if x] + [n]
    out = []; carry = None
    for a, b in zip(st[:-1], st[1:]):
        if carry is not None: a, carry = carry, None
        if merge and b - a < minlen and b < n: carry = a; continue
        out.append(dict(a=a, b=b, o=P['O'][a], c=P['C'][b - 1], h=max(P['H'][a:b]), l=min(P['L'][a:b]), t=T[a]))
    idx = [0] * n
    for k, s in enumerate(out):
        for i in range(s['a'], s['b']): idx[i] = k
    P[key] = (out, idx); return P[key]
def event(P, j, d, extra=('vsl',)):
    O, H, L, C, V = P['O'], P['H'], P['L'], P['C'], P['V']; A = P[('atr', 14)][j]
    if A is None or A <= 0 or j < 11: return False
    o, h, l, c = O[j], H[j], L[j], C[j]; rng = h - l
    if rng <= 0 or d * (c - o) <= 0 or rng < 0.8 * A or abs(c - o) / rng * 100 < 55: return False
    if ((h - c) if d > 0 else (c - l)) / rng * 100 > 25: return False
    bl = 'wick' in extra
    if not (((h if bl else c) > max(H[j - 10:j])) if d > 0 else ((l if bl else c) < min(L[j - 10:j]))): return False
    if 'vw' in extra and not (V[j] is not None and d * (c - V[j]) > 0): return False
    if 'mom' in extra and d * (c - C[j - 10]) < 0.85 * A: return False
    if 'vsl' in extra and P['sinceStart'][j] >= 3 and not d * (V[j] - V[j - 3]) > 0: return False
    if 'first' in extra and P['sinceStart'][j] < 1: return False
    if 'sun' in extra and P['dowutc'][j] == 6: return False
    return True
def nprior(P, i, d, merge=True, extra=('vsl',)):
    out, idx = sessions(P, merge); a = out[idx[i]]['a']
    return sum(1 for j in range(a, i) if event(P, j, d, extra))
