"""hookeval rule (self-contained): TIGHT STOP on the first displacement of the session in its direction when the
previous session's candle closed against that direction.

  event(j, d)  = 'displacement candle' in direction d on bar j: candle closes in direction d, range >= 0.8 ATR14,
                 body >= 55% of range, close within 25% of its extreme, close beyond the prior 10-bar high (L) / low (S),
                 [optional: close beyond VWAP, close >= 0.85 ATR beyond close[10]], VWAP rising/falling vs 3 bars ago
                 (skipped in the first 3 bars of a session).  NOT gated by 'first bar of session' / 'Sunday UTC' / state.
  first        = no event(j, d) on any earlier bar j of the current session (session = VWAP reset; MERGE joins a <24-bar
                 stub session, e.g. NASDAQ Sunday 22:00-23:00 UTC, into the following one).
  prevAgainst  = d * (prevSessionClose - prevSessionOpen) < -PD_TH * ATR14
  stop         = entry - d * max(0.9*ATR14, d*(entry - displacement low/high))  if first and prevAgainst
                 else the default 1.8*ATR14 stop.
"""
EVENT_EXTRA = ('vsl',)      # subset of ('vw', 'mom', 'vsl', 'first', 'sun')
MERGE = True
PD_TH = 1.0
def _daily(P):
    key = ('ruleFD_daily', MERGE)
    if key in P: return P[key]
    T = P['T']; n = len(T); st = [i for i, x in enumerate(P['daystart']) if x] + [n]
    out = []; carry = None
    for a, b in zip(st[:-1], st[1:]):
        if carry is not None: a, carry = carry, None
        if MERGE and b - a < 24 and b < n: carry = a; continue
        out.append((a, b, P['O'][a], P['C'][b - 1]))
    idx = [0] * n
    for k, (a, b, o, c) in enumerate(out):
        for i in range(a, b): idx[i] = k
    P[key] = (out, idx); return P[key]
def _event(P, j, d):
    O, H, L, C, V = P['O'], P['H'], P['L'], P['C'], P['V']; A = P[('atr', 14)][j]
    if A is None or A <= 0 or j < 11: return False
    o, h, l, c = O[j], H[j], L[j], C[j]; rng = h - l
    if rng <= 0 or d * (c - o) <= 0 or rng < 0.8 * A or abs(c - o) / rng * 100 < 55: return False
    if ((h - c) if d > 0 else (c - l)) / rng * 100 > 25: return False
    if not ((c > max(H[j - 10:j])) if d > 0 else (c < min(L[j - 10:j]))): return False
    if 'vw' in EVENT_EXTRA and not (V[j] is not None and d * (c - V[j]) > 0): return False
    if 'mom' in EVENT_EXTRA and d * (c - C[j - 10]) < 0.85 * A: return False
    if 'vsl' in EVENT_EXTRA and P['sinceStart'][j] >= 3 and not d * (V[j] - V[j - 3]) > 0: return False
    if 'first' in EVENT_EXTRA and P['sinceStart'][j] < 1: return False
    if 'sun' in EVENT_EXTRA and P['dowutc'][j] == 6: return False
    return True
def is_tight(P, i, d):
    out, idx = _daily(P); k = idx[i]
    if k == 0: return False
    a = out[k][0]; pa, pb, po, pc = out[k - 1]
    if not d * (pc - po) < -PD_TH * P[('atr', 14)][i]: return False
    return not any(_event(P, j, d) for j in range(a, i))
def stop_fn(P, i, d, entry, stop, A, ctx):
    if is_tight(P, i, d):
        ext = P['L'][i] if d > 0 else P['H'][i]
        return entry - d * max(0.9 * A, d * (entry - ext))
    return stop
