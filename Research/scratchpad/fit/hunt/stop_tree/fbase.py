"""Per-symbol indicator series (cached in P) for the stop_tree feature bank. All functions are causal (use bars <= i)."""
import sys, math
FIT = '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fit'
sys.path.insert(0, FIT)
from engine2 import prepare
from engine import rma


def ema(x, n):
    o = [None] * len(x); a = 2.0 / (n + 1); s = None
    for i, v in enumerate(x):
        s = v if s is None else s + a * (v - s)
        o[i] = s
    return o


def sma(x, n):
    o = [None] * len(x); s = 0.0
    for i, v in enumerate(x):
        s += v
        if i >= n: s -= x[i - n]
        if i >= n - 1: o[i] = s / n
    return o


def dmi_series(P, L):
    key = ('st_dmi', L)
    if key in P: return P[key]
    H, Lo, C = P['H'], P['L'], P['C']; n = len(C)
    up = [0.0] * n; dn = [0.0] * n
    for i in range(1, n):
        u = H[i] - H[i - 1]; d = Lo[i - 1] - Lo[i]
        up[i] = u if (u > d and u > 0) else 0.0; dn[i] = d if (d > u and d > 0) else 0.0
    trr = rma(P['tr'], L); pu = rma(up, L); pd = rma(dn, L)
    dip = [None] * n; dim = [None] * n; dx = [0.0] * n
    for i in range(n):
        if trr[i] is None or trr[i] == 0: continue
        p = 100 * pu[i] / trr[i]; m = 100 * pd[i] / trr[i]; dip[i] = p; dim[i] = m
        dx[i] = abs(p - m) / (p + m if p + m else 1) * 100
    first = next(i for i in range(n) if trr[i] is not None)
    adx = [None] * n; ax = rma(dx[first:], L)
    for k, v in enumerate(ax): adx[first + k] = v
    P[key] = (dip, dim, adx); return P[key]


def rsi(P, n=14):
    key = ('st_rsi', n)
    if key in P: return P[key]
    C = P['C']; g = [0.0] + [max(C[i] - C[i - 1], 0) for i in range(1, len(C))]
    l = [0.0] + [max(C[i - 1] - C[i], 0) for i in range(1, len(C))]
    ag = rma(g, n); al = rma(l, n); out = [None] * len(C)
    for i in range(len(C)):
        if ag[i] is None: continue
        out[i] = 100.0 if al[i] == 0 else 100 - 100 / (1 + ag[i] / al[i])
    P[key] = out; return out


def sessions(P, merge):
    """list of (a, b) session index ranges; merge joins <24-bar stubs into the following session."""
    key = ('st_sess', merge)
    if key in P: return P[key]
    n = len(P['T']); st = [i for i, x in enumerate(P['daystart']) if x] + [n]
    out = []; carry = None
    for a, b in zip(st[:-1], st[1:]):
        if carry is not None: a, carry = carry, None
        if merge and b - a < 24 and b < n: carry = a; continue
        out.append((a, b))
    idx = [0] * n
    for k, (a, b) in enumerate(out):
        for i in range(a, b): idx[i] = k
    P[key] = (out, idx); return P[key]


def core_sig(P, j, d, extra=()):
    """displacement-candle conditions of the best model at bar j in direction d (no state). extra: subset of vw, mom, vsl, first, sun."""
    O, H, L, C, V = P['O'], P['H'], P['L'], P['C'], P['V']; A = P[('atr', 14)][j]
    if A is None or A <= 0 or j < 11: return False
    o, h, l, c = O[j], H[j], L[j], C[j]; rng = h - l
    if rng <= 0 or d * (c - o) <= 0 or rng < 0.8 * A or abs(c - o) / rng * 100 < 55: return False
    if ((h - c) if d > 0 else (c - l)) / rng * 100 > 25: return False
    if not ((c > max(H[j - 10:j])) if d > 0 else (c < min(L[j - 10:j]))): return False
    if 'vw' in extra and not (V[j] is not None and d * (c - V[j]) > 0): return False
    if 'mom' in extra and d * (c - C[j - 10]) < 0.85 * A: return False
    if 'vsl' in extra and P['sinceStart'][j] >= 3 and not d * (V[j] - V[j - 3]) > 0: return False
    if 'first' in extra and P['sinceStart'][j] < 1: return False
    if 'sun' in extra and P['dowutc'][j] == 6: return False
    return True


SIGSETS = {'core': (), 'vsl': ('vsl',), 'full': ('vw', 'mom', 'vsl'), 'arm': ('vw', 'mom', 'vsl', 'first', 'sun')}


def sigs(P, name):
    key = ('st_sig', name)
    if key in P: return P[key]
    n = len(P['C']); ex = SIGSETS[name]; out = [0] * n
    for j in range(11, n):
        if core_sig(P, j, 1, ex): out[j] = 1
        elif core_sig(P, j, -1, ex): out[j] = -1
    P[key] = out; return out


def base(sym):
    P = prepare(sym)
    if 'st_base' in P: return P
    if ('atr', 14) not in P: P[('atr', 14)] = rma(P['tr'], 14)
    from volrec import recover
    recover(sym)
    C = P['C']
    P['st_atr5'] = rma(P['tr'], 5); P['st_atr50'] = rma(P['tr'], 50)
    P['st_trs100'] = sma(P['tr'], 100); P['st_trs288'] = sma(P['tr'], 288)
    for n in (9, 20, 50, 100, 200): P[('st_ema', n)] = ema(C, n)
    e12 = ema(C, 12); e26 = ema(C, 26); macd = [a - b for a, b in zip(e12, e26)]; sig = ema(macd, 9)
    P['st_macdh'] = [a - b for a, b in zip(macd, sig)]
    P['st_sma20'] = sma(C, 20)
    sd = [None] * len(C)
    for i in range(19, len(C)):
        w = C[i - 19:i + 1]; m = sum(w) / 20; sd[i] = math.sqrt(sum((x - m) ** 2 for x in w) / 20)
    P['st_sd20'] = sd
    for L in (7, 14, 28): dmi_series(P, L)
    rsi(P, 14)
    for nm in SIGSETS: sigs(P, nm)
    P['st_base'] = True
    return P
