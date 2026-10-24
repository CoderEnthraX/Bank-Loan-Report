"""Price-location / regime features, causal: value at bar i uses bars <= i only (HTF uses COMPLETED higher-timeframe buckets only).
feature(F, name, i, d) -> direction-signed value (for longs as defined; for shorts mirrored) or None."""
import sys, math, datetime as dt
S = '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad'
sys.path.insert(0, S + '/fit')
from engine2 import prepare
from engine import rma
_cache = {}
NAN = None

def wilder(x, n):
    o = [None] * len(x); s = None; k = 0
    for i, v in enumerate(x):
        if v is None: continue
        k += 1
        if s is None:
            if k == n: s = sum(y for y in x[i - n + 1:i + 1] if y is not None) / n; o[i] = s
            continue
        s = (s * (n - 1) + v) / n; o[i] = s
    return o

def ema(x, n):
    a = 2.0 / (n + 1); o = [None] * len(x); s = None
    for i, v in enumerate(x):
        if v is None: o[i] = s; continue
        s = v if s is None else s + a * (v - s); o[i] = s
    return o

def rsi(C, n):
    up = [None] + [max(C[i] - C[i - 1], 0) for i in range(1, len(C))]; dn = [None] + [max(C[i - 1] - C[i], 0) for i in range(1, len(C))]
    au, ad = wilder(up, n), wilder(dn, n); o = [None] * len(C)
    for i in range(len(C)):
        if au[i] is None: continue
        o[i] = 100.0 if ad[i] == 0 else 100 - 100 / (1 + au[i] / ad[i])
    return o

def compute(sym):
    if sym in _cache: return _cache[sym]
    P = prepare(sym); O, H, L, C, V, T = P['O'], P['H'], P['L'], P['C'], P['V'], P['T']; n = len(C); DS = P['daystart']
    A = rma(P['tr'], 14); F = dict(n=n, A=A, C=C, H=H, L=L, O=O, V=V, T=T)
    # session state
    sesH = [0.0] * n; sesL = [0.0] * n; sesO = [0.0] * n; pdH = [None] * n; pdL = [None] * n; pdC = [None] * n; vb = [0] * n
    orH = [None] * n; orL = [None] * n; sd = [None] * n
    h = l = o = None; ph = pl = pc = None; k = 0; s1 = s2 = 0.0; oh = ol = None
    for i in range(n):
        if DS[i]:
            if i > 0: ph, pl, pc = h, l, C[i - 1]
            h, l, o = H[i], L[i], O[i]; k = 0; s1 = s2 = 0.0; oh, ol = H[i], L[i]
        else:
            h = max(h, H[i]); l = min(l, L[i]); k += 1
        if k < 6: oh = max(oh, H[i]); ol = min(ol, L[i])
        tp = (H[i] + L[i] + C[i]) / 3; s1 += tp; s2 += tp * tp; m = k + 1
        var = s2 / m - 2 * V[i] * s1 / m + V[i] * V[i]; sd[i] = math.sqrt(max(var, 0)) if m >= 3 else None
        sesH[i], sesL[i], sesO[i], vb[i] = h, l, o, k; pdH[i], pdL[i], pdC[i] = ph, pl, pc
        if k >= 5: orH[i], orL[i] = oh, ol
    F.update(sesH=sesH, sesL=sesL, sesO=sesO, pdH=pdH, pdL=pdL, pdC=pdC, vb=vb, orH=orH, orL=orL, sd=sd)
    F['rsi14'] = rsi(C, 14); F['rsi7'] = rsi(C, 7)
    kr = [None] * n
    for i in range(13, n):
        hh, ll = max(H[i - 13:i + 1]), min(L[i - 13:i + 1]); kr[i] = 50.0 if hh == ll else 100 * (C[i] - ll) / (hh - ll)
    F['stoch'] = [None if i < 15 or kr[i - 2] is None else (kr[i] + kr[i - 1] + kr[i - 2]) / 3 for i in range(n)]
    # ADX14
    pdm = [0.0] * n; mdm = [0.0] * n
    for i in range(1, n):
        u = H[i] - H[i - 1]; dd = L[i - 1] - L[i]; pdm[i] = u if u > dd and u > 0 else 0.0; mdm[i] = dd if dd > u and dd > 0 else 0.0
    trs = wilder(P['tr'], 14); sp = wilder(pdm, 14); sm = wilder(mdm, 14); dx = [None] * n
    for i in range(n):
        if trs[i] and sp[i] is not None and sm[i] is not None:
            a, b = 100 * sp[i] / trs[i], 100 * sm[i] / trs[i]; dx[i] = 0.0 if a + b == 0 else 100 * abs(a - b) / (a + b)
    F['adx'] = wilder(dx, 14)
    F['atrma'] = [None if i < 113 or A[i - 99] is None else sum(A[i - 99:i + 1]) / 100 for i in range(n)]
    # pivots (3,3) confirmed 3 bars later
    piv_lo = [None] * n; piv_hi = [None] * n; lastlo = lasthi = None
    for i in range(n):
        j = i - 3
        if j >= 3:
            if L[j] < min(L[j - 3:j]) and L[j] <= min(L[j + 1:i + 1]): lastlo = j
            if H[j] > max(H[j - 3:j]) and H[j] >= max(H[j + 1:i + 1]): lasthi = j
        piv_lo[i], piv_hi[i] = lastlo, lasthi
    F['plo'], F['phi'] = piv_lo, piv_hi
    # HTF (UTC-aligned buckets), EMA on completed buckets only
    mins = [int((dt.datetime.strptime(t, '%Y-%m-%d %H:%M') - dt.datetime(2026, 1, 1)).total_seconds() // 60) - 330 for t in T]
    for tf in (15, 60):
        bid = [m // tf for m in mins]; closes = []; e20 = e50 = None; a20, a50 = 2 / 21, 2 / 51
        E20 = [None] * n; E50 = [None] * n
        for i in range(n):
            if i > 0 and bid[i] != bid[i - 1]:      # bucket of i-1 completed: update HTF EMAs with its close
                c = C[i - 1]; e20 = c if e20 is None else e20 + a20 * (c - e20); e50 = c if e50 is None else e50 + a50 * (c - e50); closes.append(c)
            if len(closes) >= 50: E20[i], E50[i] = e20, e50
        F['e20_%d' % tf], F['e50_%d' % tf] = E20, E50
    F['hour'] = [int(t[11:13]) + int(t[14:16]) / 60.0 for t in T]
    _cache[sym] = F
    return F

def feature(F, name, i, d):
    A = F['A'][i]; C, H, L, O, V = F['C'], F['H'], F['L'], F['O'], F['V']
    if A is None or A <= 0: return None
    c = C[i]
    def don(N):
        if i < N: return None
        hh, ll = max(H[i - N + 1:i + 1]), min(L[i - N + 1:i + 1]); return hh, ll
    if name == 'vwExtA': return d * (c - V[i]) / A
    if name == 'vwSig':
        s = F['sd'][i]; return None if not s else d * (c - V[i]) / s
    if name.startswith('donPos'):                # position inside N-bar range (1 = at the trade-direction extreme)
        N = int(name[6:]); r = don(N)
        if r is None or r[0] == r[1]: return None
        p = (c - r[1]) / (r[0] - r[1]); return p if d > 0 else 1 - p
    if name.startswith('donRng'):
        N = int(name[6:]); r = don(N); return None if r is None else (r[0] - r[1]) / A
    if name.startswith('leg'):                   # distance from the opposite N-bar extreme (move size) in ATR
        N = int(name[3:]); r = don(N); return None if r is None else (c - r[1]) / A if d > 0 else (r[0] - c) / A
    if name.startswith('legBars'): pass
    if name == 'sesPos':
        hh, ll = F['sesH'][i], F['sesL'][i]
        if hh == ll: return None
        p = (c - ll) / (hh - ll); return p if d > 0 else 1 - p
    if name == 'sesMove': return d * (c - F['sesO'][i]) / A
    if name == 'consec':
        k = 0; j = i
        while j >= 0 and d * (C[j] - O[j]) > 0: k += 1; j -= 1
        return k
    if name == 'consecC':
        k = 0; j = i
        while j >= 1 and d * (C[j] - C[j - 1]) > 0: k += 1; j -= 1
        return k
    if name in ('swMove', 'swBars'):             # move from the last confirmed opposite pivot (3,3)
        j = F['plo'][i] if d > 0 else F['phi'][i]
        if j is None: return None
        return (d * (c - (L[j] if d > 0 else H[j])) / A) if name == 'swMove' else i - j
    if name in ('ext30Bars',):                   # bars since the opposite 30-bar extreme
        if i < 30: return None
        seg = L[i - 29:i + 1] if d > 0 else H[i - 29:i + 1]
        m = min(seg) if d > 0 else max(seg); idx = max(k for k, v in enumerate(seg) if v == m); return 29 - idx
    if name in ('rsi14', 'rsi7', 'stoch'):
        v = F[name][i]; return None if v is None else (v if d > 0 else 100 - v)
    if name in ('htf15', 'htf60'):               # EMA20-EMA50 of the completed HTF bars, signed, in ATR
        tf = name[3:]; a, b = F['e20_' + tf][i], F['e50_' + tf][i]; return None if a is None else d * (a - b) / A
    if name in ('htf15px', 'htf60px'):           # price vs HTF EMA20
        tf = name[3:5]; a = F['e20_' + tf][i]; return None if a is None else d * (c - a) / A
    if name == 'pdRoom':                         # room to the previous session extreme in the trade direction (neg = already beyond)
        ph, pl = F['pdH'][i], F['pdL'][i]
        if ph is None: return None
        return (ph - c) / A if d > 0 else (c - pl) / A
    if name == 'pdC': p = F['pdC'][i]; return None if p is None else d * (c - p) / A
    if name == 'gap':
        p = F['pdC'][i]; return None if p is None else d * (F['sesO'][i] - p) / A
    if name == 'orLoc':                          # beyond the 30-min opening range in the trade direction (ATR)
        oh, ol = F['orH'][i], F['orL'][i]
        if oh is None: return None
        return (c - oh) / A if d > 0 else (ol - c) / A
    if name == 'hour': return F['hour'][i]
    if name == 'vb': return F['vb'][i]
    if name == 'atrReg': m = F['atrma'][i]; return None if not m else A / m
    if name == 'adx': return F['adx'][i]
    if name == 'cmo':
        if i < 10: return None
        path = sum(abs(C[j] - C[j - 1]) for j in range(i - 9, i + 1)); return None if path == 0 else 100 * d * (c - C[i - 10]) / path
    if name == 'rngA': return (H[i] - L[i]) / A
    if name == 'mom10': return d * (c - C[i - 10]) / A
    if name == 'vwSlope': return d * (V[i] - V[i - 3]) / A
    if name == 'wick':                           # opposite-side (rejection) wick of the signal bar as share of range
        r = H[i] - L[i]; return None if r == 0 else ((min(O[i], c) - L[i]) if d > 0 else (H[i] - max(O[i], c))) / r
    raise KeyError(name)

NAMES = ['vwExtA', 'vwSig', 'donPos20', 'donPos50', 'donRng20', 'donRng50', 'leg20', 'leg50', 'sesPos', 'sesMove', 'consec', 'consecC',
         'swMove', 'swBars', 'ext30Bars', 'rsi14', 'rsi7', 'stoch', 'htf15', 'htf60', 'htf15px', 'htf60px', 'pdRoom', 'pdC', 'gap', 'orLoc',
         'hour', 'vb', 'atrReg', 'adx', 'cmo', 'rngA', 'mom10', 'vwSlope', 'wick']
