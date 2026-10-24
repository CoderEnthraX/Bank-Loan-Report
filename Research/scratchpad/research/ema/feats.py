"""Causal moving-average features at a bar i for a trade direction d (+1 long / -1 short).
5m series are computed on the 5m closes. 15m / 1h series use UTC-aligned buckets built from the 5m bars and only
COMPLETED buckets (a bucket is complete on its scheduled last 5m bar, otherwise when the next bucket starts), like
request.security(..., expr[1], lookahead_on) in Pine. Every value uses bars <= i only. Distances are in 5m ATR14 (RMA)."""
import sys, math, datetime
S = '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad'
sys.path.insert(0, S + '/fit')
from engine2 import prepare
from engine import rma

def ema(x, n):
    o = [None] * len(x); a = 2.0 / (n + 1); s = None
    for i in range(len(x)):
        if s is None:
            if i >= n - 1: s = sum(x[i - n + 1:i + 1]) / n
        else: s = a * x[i] + (1 - a) * s
        o[i] = s
    return o
def sma(x, n):
    o = [None] * len(x); s = 0.0
    for i in range(len(x)):
        s += x[i]
        if i >= n: s -= x[i - n]
        if i >= n - 1: o[i] = s / n
    return o
def wma(x, n):
    o = [None] * len(x); w = n * (n + 1) / 2
    for i in range(len(x)):
        if i >= n - 1 and all(v is not None for v in x[i - n + 1:i + 1]):
            o[i] = sum(x[i - n + 1 + k] * (k + 1) for k in range(n)) / w
    return o
def hma(x, n):
    a = wma(x, n // 2); b = wma(x, n)
    d = [None if (u is None or v is None) else 2 * u - v for u, v in zip(a, b)]
    m = int(math.sqrt(n)); o = [None] * len(x)
    for i in range(len(x)):
        seg = d[i - m + 1:i + 1] if i >= m - 1 else []
        if len(seg) == m and all(v is not None for v in seg):
            o[i] = sum(seg[k] * (k + 1) for k in range(m)) / (m * (m + 1) / 2)
    return o
def kama(x, n=10, f=2, s=30):
    fa, sa = 2.0 / (f + 1), 2.0 / (s + 1); o = [None] * len(x); k = None
    for i in range(len(x)):
        if i < n: continue
        ch = abs(x[i] - x[i - n]); vol = sum(abs(x[j] - x[j - 1]) for j in range(i - n + 1, i + 1))
        er = ch / vol if vol > 0 else 0.0; sc = (er * (fa - sa) + sa) ** 2
        k = x[i - 1] if k is None else k; k = k + sc * (x[i] - k); o[i] = k
    return o

EM5 = (9, 20, 21, 50, 100, 200)
EMH = {'h15': (9, 20, 21, 50, 100, 200), 'h60': (9, 20, 21, 50), 'h6s': (9, 20, 50), 'h6a': (9, 20, 50), 'h6b': (9, 20, 50)}
_C = {}
_EP = datetime.datetime(1970, 1, 1)
def _mins(t):
    """UTC minutes since epoch of an IST bar-open time string."""
    u = datetime.datetime.strptime(t, '%Y-%m-%d %H:%M') - datetime.timedelta(hours=5, minutes=30)
    return int((u - _EP).total_seconds() // 60)
def htf(T, C, minutes, anchor=None, strict=False):
    """per-5m-bar index into the completed-bucket sequence + bucket closes. anchor = daystart flags -> buckets anchored at the
    session's first bar (TradingView-style session-aligned HTF bars); strict -> always the previous bucket (Pine expr[1] + lookahead_on)."""
    n = len(T); key = []; ends = []; s0 = None; si = -1
    for i, t in enumerate(T):
        m = _mins(t)
        if anchor is None: key.append(m // minutes); ends.append((m // minutes + 1) * minutes); continue
        if anchor[i] or s0 is None: s0 = m; si += 1
        k = (m - s0) // minutes; key.append((si, k)); ends.append(s0 + (k + 1) * minutes)
    bc = []; bidx = [None] * n; last = None   # bc = closes of buckets in order; bidx[i] = index of latest completed bucket at bar i
    for i in range(n):
        if last is None or key[i] != last:
            bc.append(C[i]); last = key[i]
        else: bc[-1] = C[i]
        cur = len(bc) - 1
        closes = (not strict) and _mins(T[i]) + 5 >= ends[i]
        bidx[i] = cur if closes else (cur - 1 if cur >= 1 else None)
    return bc, bidx

def compute(sym, P=None):
    if P is None and sym in _C: return _C[sym]
    cache = P is None; P = P or prepare(sym); C, H, L, V, T = P['C'], P['H'], P['L'], P['V'], P['T']; n = len(C)
    F = dict(C=C, H=H, L=L, V=V, A=rma(P['tr'], 14), n=n)
    for k in EM5: F['E%d' % k] = ema(C, k)
    for k in (20, 50): F['S%d' % k] = sma(C, k)
    F['HMA'] = hma(C, 20); F['KAMA'] = kama(C, 10, 2, 30)
    for tf, mins, anc, strict in (('h15', 15, None, False), ('h60', 60, None, False), ('h6s', 60, None, True), ('h6a', 60, P['daystart'], False), ('h6b', 60, P['daystart'], True)):
        bc, bidx = htf(T, C, mins, anc, strict); F[tf + 'idx'] = bidx; F[tf + 'C'] = bc
        for k in EMH[tf]: F[tf + 'E%d' % k] = ema(bc, k)
    # sign arrays for cross counts
    def crosses(a, b):
        s = [0] * n; cum = [0] * n; prev = 0; c = 0
        for i in range(n):
            if a[i] is None or b[i] is None: cum[i] = c; continue
            sg = 1 if a[i] > b[i] else -1
            if prev and sg != prev: c += 1
            prev = sg; cum[i] = c
        return cum
    F['xc_C_E20'] = crosses(C, F['E20']); F['xc_E9_E21'] = crosses(F['E9'], F['E21']); F['xc_C_V'] = crosses(C, V)
    F['xc_C_E50'] = crosses(C, F['E50'])
    # HTF crosses of HTF close vs HTF EMA20 (in bucket units)
    for tf in ('h15', 'h60', 'h6s', 'h6a', 'h6b'):
        bc = F[tf + 'C']; e = F[tf + 'E20']; cum = []; prev = 0; c = 0
        for j in range(len(bc)):
            if e[j] is not None:
                sg = 1 if bc[j] > e[j] else -1
                if prev and sg != prev: c += 1
                prev = sg
            cum.append(c)
        F[tf + 'xc'] = cum
    if cache: _C[sym] = F
    return F

def _h(F, tf, name, i, back=0):
    j = F[tf + 'idx'][i]
    if j is None or j - back < 0: return None
    return F[tf + name][j - back]

def value(F, name, i, d, entry=None):
    """signed (d) feature value at bar i; None = not available (gate passes)."""
    A = F['A'][i]; C = F['C']; V = F['V']
    if not A: return None
    try:
        p = name.split('_')
        if p[0] == 'px':            # px_E20 : d*(C-E20)/A
            e = F[p[1]][i]; return None if e is None else d * (C[i] - e) / A
        if p[0] == 'en':            # en_E20 : d*(entry-E20)/A
            e = F[p[1]][i]; return None if e is None else d * (entry - e) / A
        if p[0] in ('sl', 'asl'):   # sl_E20_5 : d*(E20[i]-E20[i-5])/A ; asl = abs
            k = int(p[2]); a, b = F[p[1]][i], F[p[1]][i - k]
            if a is None or b is None: return None
            v = (a - b) / A; return d * v if p[0] == 'sl' else abs(v)
        if p[0] == 'rs':            # rs_E9_E21 : d*(E9-E21)/A (signed ribbon), rw = abs
            a, b = F[p[1]][i], F[p[2]][i]; return None if a is None or b is None else d * (a - b) / A
        if p[0] == 'rw':
            a, b = F[p[1]][i], F[p[2]][i]; return None if a is None or b is None else abs(a - b) / A
        if p[0] == 'sp':            # sp_9.21.50 : (max-min)/A of those EMAs
            vs = [F['E' + k][i] for k in p[1].split('.')]
            return None if any(v is None for v in vs) else (max(vs) - min(vs)) / A
        if p[0] == 'spr':           # spr_9.21.50_48 : sp now / mean sp over last N bars (compression ratio)
            ks = p[1].split('.'); N = int(p[2]); acc = []
            for j in range(i - N + 1, i + 1):
                vs = [F['E' + k][j] for k in ks]; aj = F['A'][j]
                if any(v is None for v in vs) or not aj: return None
                acc.append((max(vs) - min(vs)) / aj)
            m = sum(acc) / len(acc); return acc[-1] / m if m > 0 else None
        if p[0] == 'stk':           # stk_9.21.50 : number of adjacent pairs aligned with d minus opposed
            vs = [F['E' + k][i] for k in p[1].split('.')]
            if any(v is None for v in vs): return None
            return sum((1 if d * (vs[j] - vs[j + 1]) > 0 else -1) for j in range(len(vs) - 1))
        if p[0] == 'xc':            # xc_C_E20_24 : crosses in the last N bars
            cum = F['xc_%s_%s' % (p[1], p[2])]; N = int(p[3]); return cum[i] - cum[i - N] if i - N >= 0 else None
        if p[0] == 'pb':            # pb_E20_6 : min over last k bars (excl. signal bar) of d*(adverse extreme - E)/A ; <=0 = touched
            e = F[p[1]]; k = int(p[2]); best = None
            for j in range(i - k, i):
                if e[j] is None: return None
                x = (F['L'][j] - e[j]) if d > 0 else (e[j] - F['H'][j]); best = x if best is None else min(best, x)
            return best / A
        if p[0] == 've':            # ve_E20 : d*(E20-VWAP)/A ; ave = abs
            e = F[p[1]][i]; return None if e is None else d * (e - V[i]) / A
        if p[0] == 'ave':
            e = F[p[1]][i]; return None if e is None else abs(e - V[i]) / A
        if p[0] in ('h15', 'h60', 'h6s', 'h6a', 'h6b'):  # h15_px_E20 | h15_sl_E20_3 | h15_rs_E20_E50 | h15_rw_E20_E50 | h15_xc_8 | h15_stk_9.21.50
            tf = p[0]; q = p[1]
            if q == 'px':
                e = _h(F, tf, p[2], i); return None if e is None else d * (C[i] - e) / A
            if q in ('sl', 'asl'):
                a, b = _h(F, tf, p[2], i), _h(F, tf, p[2], i, int(p[3]))
                if a is None or b is None: return None
                v = (a - b) / A; return d * v if q == 'sl' else abs(v)
            if q in ('rs', 'rw'):
                a, b = _h(F, tf, p[2], i), _h(F, tf, p[3], i)
                if a is None or b is None: return None
                return d * (a - b) / A if q == 'rs' else abs(a - b) / A
            if q == 'xc':
                j = F[tf + 'idx'][i]; N = int(p[2])
                if j is None or j - N < 0: return None
                return F[tf + 'xc'][j] - F[tf + 'xc'][j - N]
            if q == 'stk':
                vs = [_h(F, tf, 'E' + k, i) for k in p[2].split('.')]
                if any(v is None for v in vs): return None
                return sum((1 if d * (vs[j] - vs[j + 1]) > 0 else -1) for j in range(len(vs) - 1))
            if q == 've':
                e = _h(F, tf, p[2], i); return None if e is None else d * (e - V[i]) / A
        raise KeyError(name)
    except IndexError:
        return None

def names():
    N = []
    for k in EM5: N += ['px_E%d' % k, 'sl_E%d_3' % k, 'sl_E%d_5' % k, 'sl_E%d_10' % k, 'asl_E%d_5' % k]
    N += ['px_S20', 'px_S50', 'sl_S20_5', 'sl_S50_5', 'rs_E20_S20', 'px_HMA', 'sl_HMA_3', 'px_KAMA', 'sl_KAMA_5', 'asl_KAMA_5']
    N += ['stk_9.21.50', 'stk_9.21', 'stk_20.50', 'stk_50.200', 'stk_9.20.50.100.200', 'rs_E9_E21', 'rs_E20_E50', 'rs_E50_E200']
    N += ['rw_E9_E21', 'rw_E20_E50', 'sp_9.21.50', 'sp_9.20.50.100.200', 'spr_9.21.50_48', 'spr_9.21_48']
    N += ['xc_C_E20_12', 'xc_C_E20_24', 'xc_C_E20_48', 'xc_C_E50_48', 'xc_E9_E21_24', 'xc_E9_E21_48', 'xc_E9_E21_96', 'xc_C_V_24', 'xc_C_V_48']
    for k in ('E9', 'E20', 'E50'): N += ['pb_%s_3' % k, 'pb_%s_6' % k, 'pb_%s_10' % k]
    N += ['ve_E20', 've_E50', 'ave_E20', 'ave_E50', 'en_E9', 'en_E20', 'en_E50']
    for tf in ('h15', 'h60'):
        ks = (9, 20, 50) + ((100, 200) if tf == 'h15' else ())
        for k in ks: N += ['%s_px_E%d' % (tf, k), '%s_sl_E%d_3' % (tf, k)]
        N += ['%s_asl_E20_3' % tf, '%s_rs_E9_E21' % tf, '%s_rs_E20_E50' % tf, '%s_rw_E9_E21' % tf, '%s_rw_E20_E50' % tf,
              '%s_stk_9.21.50' % tf, '%s_xc_8' % tf, '%s_xc_16' % tf, '%s_ve_E20' % tf]
    return N
