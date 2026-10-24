"""hookeval rule (stop_tree, self-contained).  TIGHT iff first vsl-event of the raw session in dir d AND previous raw session net vsl-event count * d <= -4 AND overnight gap >= -1.0 ATR14 (net threshold at the tight edge).
Generated from r_pgen.py with fixed parameters (see r_pgen.py docstring for the definitions)."""
import os
AG = 'net'; NET = 3.5; BODY = 1.0
GUARD = 'gap'; GAP = 1.0; MERGE = False
OLOC = 0.0
EV = ('vsl',)   # event extras: vsl, vw, mom, first, sun


def _ev(P, j, d):
    O, H, L, C, V = P['O'], P['H'], P['L'], P['C'], P['V']; A = P[('atr', 14)][j]
    if A is None or A <= 0 or j < 11: return False
    o, h, l, c = O[j], H[j], L[j], C[j]; rng = h - l
    if rng <= 0 or d * (c - o) <= 0 or rng < 0.8 * A or abs(c - o) / rng * 100 < 55: return False
    if ((h - c) if d > 0 else (c - l)) / rng * 100 > 25: return False
    if not ((c > max(H[j - 10:j])) if d > 0 else (c < min(L[j - 10:j]))): return False
    if 'vsl' in EV and P['sinceStart'][j] >= 3 and not d * (V[j] - V[j - 3]) > 0: return False
    if 'vw' in EV and not (V[j] is not None and d * (c - V[j]) > 0): return False
    if 'mom' in EV and d * (c - C[j - 10]) < 0.85 * A: return False
    if 'first' in EV and P['sinceStart'][j] < 1: return False
    if 'sun' in EV and P['dowutc'][j] == 6: return False
    return True


def _prep(P):
    key = ('PGprep', MERGE, EV)
    if key in P: return P[key]
    n = len(P['C'])
    sg = [1 if _ev(P, j, 1) else (-1 if _ev(P, j, -1) else 0) for j in range(n)]
    st = [i for i, x in enumerate(P['daystart']) if x] + [n]
    S = []; carry = None
    for a, b in zip(st[:-1], st[1:]):
        if carry is not None: a, carry = carry, None
        if MERGE and b - a < 24 and b < n: carry = a; continue
        S.append((a, b))
    idx = [0] * n
    for k, (a, b) in enumerate(S):
        for i in range(a, b): idx[i] = k
    P[key] = (sg, S, idx); return P[key]


def is_tight(P, i, d):
    sg, S, idx = _prep(P); k = idx[i]
    if k == 0: return False
    a = S[k][0]; pa, pb = S[k - 1]; A = P[('atr', 14)][i]
    if any(sg[j] == d for j in range(a, i)): return False
    po, pc = P['O'][pa], P['C'][pb - 1]
    net_ok = d * sum(sg[pa:pb]) <= -NET; body_ok = d * (pc - po) < -BODY * A
    ok = net_ok if AG == 'net' else body_ok if AG == 'body' else (net_ok and body_ok)
    if not ok: return False
    so = P['O'][a]
    if GUARD == 'gap' and d * (so - pc) < -GAP * A: return False
    if GUARD == 'oloc':
        ph, pl = max(P['H'][pa:pb]), min(P['L'][pa:pb])
        loc = (so - pl) / (ph - pl) if d > 0 else (ph - so) / (ph - pl)
        if loc < OLOC: return False
    return True


def stop_fn(P, i, d, entry, stop, A, ctx):
    if is_tight(P, i, d):
        ext = P['L'][i] if d > 0 else P['H'][i]
        return entry - d * max(0.9 * A, d * (entry - ext))
    return stop
