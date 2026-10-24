"""hookeval rule (stop_tree, self-contained). TIGHT iff first vsl-event of the raw session in dir d AND previous raw session net vsl-event count * d <= -3 AND d*(close - session prior extreme) <= 0.75 ATR14.
Definitions as in r_pgen.py (parameters fixed below)."""
import os
AG = os.environ.get('PG_AG', 'net'); NET = float(os.environ.get('PG_NET', '2.5')); BODY = float(os.environ.get('PG_BODY', '1.0'))
GUARD = os.environ.get('PG_GUARD', 'gap'); GAP = float(os.environ.get('PG_GAP', '1.0')); MERGE = os.environ.get('PG_MERGE', '0') == '1'
OLOC = float(os.environ.get('PG_OLOC', '0.0')); FAV = float(os.environ.get('PG_FAV', '0.75')); FAVR = float(os.environ.get('PG_FAVR', '0.5')); NOFIRST = os.environ.get('PG_NOFIRST', '0') == '1'
EV = tuple(x for x in os.environ.get('PG_EV', 'vsl').split(',') if x)   # event extras: vsl, vw, mom, first, sun


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
    if not NOFIRST and any(sg[j] == d for j in range(a, i)): return False
    po, pc = P['O'][pa], P['C'][pb - 1]
    net_ok = d * sum(sg[pa:pb]) <= -NET; body_ok = d * (pc - po) < -BODY * A
    ok = net_ok if AG == 'net' else body_ok if AG == 'body' else (net_ok and body_ok)
    if not ok: return False
    so = P['O'][a]
    if GUARD == 'gap' and d * (so - pc) < -GAP * A: return False
    if GUARD == 'fav':      # displacement close must not exceed the session's prior extreme in dir d by more than FAV ATR
        if i > a:
            ext = max(P['H'][a:i]) if d > 0 else min(P['L'][a:i])
            if d * (P['C'][i] - ext) > FAV * A: return False
    if GUARD == 'favr':     # displacement close must not exceed the session's prior extreme by more than FAVR x its own range
        if i > a:
            ext = max(P['H'][a:i]) if d > 0 else min(P['L'][a:i])
            if d * (P['C'][i] - ext) > FAVR * (P['H'][i] - P['L'][i]): return False
    if GUARD == 'inside':
        ph, pl = max(P['H'][pa:pb]), min(P['L'][pa:pb])
        if not (pl <= so <= ph): return False
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

# fixed parameters
AG = "net"; NET = 2.5; MERGE = False; EV = ("vsl",); NOFIRST = False
GUARD='fav'; FAV=0.75
