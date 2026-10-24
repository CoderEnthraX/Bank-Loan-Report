"""Volatility / candle-structure feature library (stop_volatility hunt)."""
import sys, math, datetime as dt
FIT = '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fit'
sys.path.insert(0, FIT)
from engine2 import prepare
from engine import rma
from volrec import recover

def sma(x, n):
    o = [None] * len(x); s = 0.0
    for i in range(len(x)):
        s += x[i]
        if i >= n: s -= x[i - n]
        if i >= n - 1: o[i] = s / n
    return o

def ema(x, n):
    o = [None] * len(x); a = 2.0 / (n + 1); s = None
    for i in range(len(x)):
        if i < n - 1: continue
        s = sum(x[i - n + 1:i + 1]) / n if s is None else a * x[i] + (1 - a) * s
        o[i] = s
    return o

def wma(x, n):
    o = [None] * len(x); w = sum(range(1, n + 1))
    for i in range(n - 1, len(x)):
        o[i] = sum(x[i - n + 1 + k] * (k + 1) for k in range(n)) / w
    return o

def series(P, key, fn):
    if key not in P: P[key] = fn()
    return P[key]

def utc(t):
    return dt.datetime.strptime(t, '%Y-%m-%d %H:%M') - dt.timedelta(hours=5, minutes=30)

def htf_atr(P, minutes, L=14, mode='rma', include_current=True):
    """ATR on a resampled timeframe (UTC-aligned buckets of `minutes`; minutes=='D' = session buckets via daystart).
    Returns per-5m-bar value: ATR of completed HTF bars plus (optionally) the developing HTF bar, as request.security would show
    (lookahead off, developing bar on realtime ~ on historical bars the value is the one from the bar's close: use completed + current partial)."""
    key = ('htf', minutes, L, mode, include_current)
    if key in P: return P[key]
    O, H, L_, C, T = P['O'], P['H'], P['L'], P['C'], P['T']; n = len(O)
    bid = [0] * n; b = -1; prevk = None
    for i in range(n):
        if minutes == 'D':
            k = b + 1 if (P['daystart'][i] or i == 0) else b
            b = k
        else:
            u = utc(T[i]); k0 = int(u.timestamp() // (60 * minutes))
            if k0 != prevk: b += 1; prevk = k0
        bid[i] = b
    # build HTF bars incrementally
    hb = []  # list of [o,h,l,c]
    out = [None] * n
    trs = []; atrv = None; prevC = None; hist_tr = []
    cur = None; curb = -1
    for i in range(n):
        if bid[i] != curb:
            if cur is not None:
                # finalize cur
                tr = (cur[1] - cur[2]) if prevC is None else max(cur[1] - cur[2], abs(cur[1] - prevC), abs(cur[2] - prevC))
                hist_tr.append(tr); prevC = cur[3]
            cur = [O[i], H[i], L_[i], C[i]]; curb = bid[i]
        else:
            cur[1] = max(cur[1], H[i]); cur[2] = min(cur[2], L_[i]); cur[3] = C[i]
        trc = (cur[1] - cur[2]) if prevC is None else max(cur[1] - cur[2], abs(cur[1] - prevC), abs(cur[2] - prevC))
        seq = hist_tr + [trc] if include_current else hist_tr
        if len(seq) >= L:
            out[i] = ('x', len(seq))
    # compute properly with an incremental RMA over the finalized list
    final = hist_tr
    # recompute: rma over finalized TR list
    fin_rma = rma(final, L) if mode == 'rma' else (sma(final, L) if mode == 'sma' else ema(final, L))
    # second pass
    curb = -1; cur = None; prevC = None; nf = 0
    for i in range(n):
        if bid[i] != curb:
            if cur is not None:
                prevC = cur[3]; nf += 1
            cur = [O[i], H[i], L_[i], C[i]]; curb = bid[i]
        else:
            cur[1] = max(cur[1], H[i]); cur[2] = min(cur[2], L_[i]); cur[3] = C[i]
        trc = (cur[1] - cur[2]) if prevC is None else max(cur[1] - cur[2], abs(cur[1] - prevC), abs(cur[2] - prevC))
        if include_current:
            if nf >= L:
                prev = fin_rma[nf - 1]
                if prev is None: out[i] = None; continue
                if mode == 'rma': out[i] = (prev * (L - 1) + trc) / L
                elif mode == 'sma': out[i] = (sum(final[nf - L + 1:nf]) + trc) / L
                else: out[i] = (2 / (L + 1)) * trc + (1 - 2 / (L + 1)) * prev
            else: out[i] = None
        else:
            out[i] = fin_rma[nf - 1] if nf >= L else None
    P[key] = out
    return out

def sess_start(P, i):
    j = i
    while j > 0 and not P['daystart'][j]: j -= 1
    return j

RAWC = dict(bodyPct=55, closePct=25, dispAtr=0.8)
def raw_disp(P, j, A):
    """candle-only displacement (no breakout/vwap/mom): returns +1 / -1 / 0"""
    O, H, L, C = P['O'], P['H'], P['L'], P['C']
    rng = H[j] - L[j]
    if rng <= 0 or A is None or rng < 0.8 * A: return 0
    body = abs(C[j] - O[j])
    if body / rng * 100 < 55: return 0
    if C[j] > O[j] and (H[j] - C[j]) / rng * 100 <= 25: return 1
    if C[j] < O[j] and (C[j] - L[j]) / rng * 100 <= 25: return -1
    return 0

def full_disp(P, j):
    O, H, L, C, V = P['O'], P['H'], P['L'], P['C'], P['V']
    A = P[('atr', 14)][j]
    d = raw_disp(P, j, A)
    if d == 0 or j < 11: return 0
    if d > 0 and not C[j] > max(H[j - 10:j]): return 0
    if d < 0 and not C[j] < min(L[j - 10:j]): return 0
    if d * (C[j] - C[j - 10]) < 0.85 * A: return 0
    if V[j] is None or d * (C[j] - V[j]) <= 0: return 0
    if P['sinceStart'][j] >= 3 and d * (V[j] - V[j - 3]) <= 0: return 0
    if P['sinceStart'][j] < 1: return 0
    if P['dowutc'][j] == 6: return 0
    return d

def features(P, i, d, entry):
    O, H, L, C, V, T = P['O'], P['H'], P['L'], P['C'], P['V'], P['T']
    tr = P['tr']; A = P[('atr', 14)][i]; f = {}
    rng = H[i] - L[i]; body = abs(C[i] - O[i])
    f['rngA'] = rng / A; f['trA'] = tr[i] / A; f['bodyA'] = body / A; f['bodyPct'] = body / rng
    fav = (H[i] - C[i]) if d > 0 else (C[i] - L[i]); adv = (O[i] - L[i]) if d > 0 else (H[i] - O[i])
    f['favWick'] = fav / rng; f['advWick'] = adv / rng; f['advWickA'] = adv / A; f['favWickA'] = fav / A
    f['gapA'] = d * (O[i] - C[i - 1]) / A; f['absgapA'] = abs(O[i] - C[i - 1]) / A
    f['brk10A'] = d * (C[i] - (max(H[i - 10:i]) if d > 0 else min(L[i - 10:i]))) / A
    f['brk6A'] = d * (C[i] - (max(H[i - 6:i]) if d > 0 else min(L[i - 6:i]))) / A
    f['mom10A'] = d * (C[i] - C[i - 10]) / A
    for N in (1, 2, 3, 5, 10, 20, 50):
        pr = [H[j] - L[j] for j in range(i - N, i)]; pt = tr[i - N:i]
        f[f'rngXmax{N}'] = rng / max(max(pr), 1e-12)
        f[f'rngXmean{N}'] = rng / max(sum(pr) / N, 1e-12)
        f[f'trXmean{N}'] = tr[i] / max(sum(pt) / N, 1e-12)
        f[f'bodyXmean{N}'] = body / max(sum(abs(C[j] - O[j]) for j in range(i - N, i)) / N, 1e-12)
        f[f'boxA{N}'] = (max(H[i - N:i]) - min(L[i - N:i])) / A
        f[f'mom{N}A'] = d * (C[i] - C[i - N]) / A
    # ATR variants vs ATR14 rma
    for Ln in (5, 7, 10, 14, 20, 50, 100):
        for mode, fn in (('rma', rma), ('sma', sma), ('ema', ema), ('wma', wma)):
            if Ln == 100 and mode == 'wma': continue
            s = series(P, ('atrv', mode, Ln), lambda: fn(P['tr'], Ln))
            if s[i]: f[f'atr_{mode}{Ln}'] = s[i] / A
            if s[i - 1]: f[f'atrp_{mode}{Ln}'] = s[i - 1] / A
    rs = series(P, ('rngrma', 14), lambda: rma([h - l for h, l in zip(H, L)], 14))
    f['atr_hl14'] = rs[i] / A
    f['atr_prev'] = P[('atr', 14)][i - 1] / A
    f['dAtr'] = (A - P[('atr', 14)][i - 1]) / A
    # HTF ATR
    for m in (15, 30, 60, 240, 'D'):
        for inc in (True, False):
            for mode in ('rma', 'sma'):
                for Ln in (14, 5):
                    s = htf_atr(P, m, Ln, mode, inc)
                    if s[i]: f[f'htf{m}_{mode}{Ln}_{"c" if inc else "p"}'] = s[i] / A
    # risk
    mt = P['mt']
    f['riskTicks'] = 1.8 * A / mt; f['riskBps'] = 1.8 * A / C[i] * 1e4; f['atrBps'] = A / C[i] * 1e4
    # retest depth
    f['depthA'] = d * (C[i] - entry) / A; f['depthR'] = d * (C[i] - entry) / rng
    f['entryAdvA'] = d * (entry - (L[i] if d > 0 else H[i])) / A
    f['entryOpenA'] = d * (entry - O[i]) / A
    f['entryMid'] = int(abs(entry - (O[i] + C[i]) / 2) < 1e-9 * max(1, abs(entry)) * 10 or abs(entry - (O[i] + C[i]) / 2) < P['mt'])
    # displacement counts
    for N in (3, 5, 10, 20, 50, 100):
        rs_ = [raw_disp(P, j, P[('atr', 14)][j]) for j in range(i - N, i)]
        f[f'rawSame{N}'] = sum(1 for x in rs_ if x == d); f[f'rawOpp{N}'] = sum(1 for x in rs_ if x == -d)
        fs_ = [full_disp(P, j) for j in range(i - N, i)]
        f[f'fullSame{N}'] = sum(1 for x in fs_ if x == d); f[f'fullOpp{N}'] = sum(1 for x in fs_ if x == -d)
    # efficiency, chop
    for N in (10, 14, 20):
        path = sum(abs(C[j] - C[j - 1]) for j in range(i - N + 1, i + 1))
        f[f'er{N}'] = abs(C[i] - C[i - N]) / path if path else 0
        hi = max(H[i - N + 1:i + 1]); lo = min(L[i - N + 1:i + 1]); s_tr = sum(tr[i - N + 1:i + 1])
        f[f'chop{N}'] = 100 * math.log10(s_tr / (hi - lo)) / math.log10(N) if hi > lo else 0
    # stdev of close / ATR, BB width
    for N in (10, 20):
        cs = C[i - N + 1:i + 1]; m = sum(cs) / N; sd = math.sqrt(sum((x - m) ** 2 for x in cs) / N)
        f[f'sdC{N}A'] = sd / A
        rets = [C[j] - C[j - 1] for j in range(i - N + 1, i + 1)]; mr = sum(rets) / N
        f[f'sdR{N}A'] = math.sqrt(sum((x - mr) ** 2 for x in rets) / N) / A
    # volume (in-session), delta proxy
    recover(P['sym'])
    vol = P['vol']; s0 = sess_start(P, i)
    v = vol[i] or 0.0
    def clv(j):
        r = H[j] - L[j]
        return 0.0 if r <= 0 else ((C[j] - L[j]) - (H[j] - C[j])) / r
    for N in (3, 5, 10, 20):
        js = [j for j in range(max(s0, i - N), i)]
        if js:
            vv = [vol[j] or 0 for j in js]
            f[f'rvol{N}'] = v / (sum(vv) / len(vv)) if sum(vv) > 0 else None
            dl = sum(clv(j) * (vol[j] or 0) for j in js)
            f[f'delta{N}'] = d * dl / sum(vv) if sum(vv) > 0 else None
    js = list(range(s0, i + 1)); tot = sum(vol[j] or 0 for j in js)
    f['sessDelta'] = d * sum(clv(j) * (vol[j] or 0) for j in js) / tot if tot else None
    f['dispDeltaShare'] = d * clv(i) * v / tot if tot else None
    f['since'] = P['sinceStart'][i]
    return {k: x for k, x in f.items() if x is not None}
