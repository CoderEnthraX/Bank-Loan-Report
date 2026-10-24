"""hookeval rule (self-contained) - "counter-trend first impulse of the day -> half risk", author-style (stop_author).

Pine-style reading (one pair of per-session counters, reset when the VWAP/daily session changes = timeframe.change("D")):
    var int bullN = 0, bearN = 0, prevNet = 0
    if timeframe.change("D")  ->  prevNet := bullN - bearN ; bullN := 0 ; bearN := 0
    tightLong  = bullDisp and bullN == 0 and prevNet <= -NET   // first bullish impulse today, yesterday dominated by bearish impulses
    tightShort = bearDisp and bearN == 0 and prevNet >=  NET
    if bullDisp -> bullN += 1 ; if bearDisp -> bearN += 1
  impulse event(j, d) = candle closing in direction d, range >= 0.8 ATR14, body >= 55% of range, close within 25% of its extreme,
        WICK beyond the prior 10-bar high (L: high > highest(high,10)[1]) / low (S), VWAP rising/falling vs 3 bars ago
        (skipped in the first 3 bars of a session). Not gated by position state, first-bar or Sunday gates.
        (WICK=False -> close beyond the 10-bar extreme, the arming condition.)
  sessions = raw VWAP resets (TradingView daily bars): IG NASDAQ's Sunday 22:00-23:00 UTC hour is its own 'day'.
  tight stop = entry - d * max(0.9*ATR14, d*(entry - impulse low/high)); otherwise the default 1.8*ATR14 stop.
"""
NET = 4        # prevNet <= -NET (long) / >= NET (short); 2..4 give identical results on the 80 trades
WICK = True    # True: 'first' and the counts use the wick breakout; False: close breakout (NIFTY 10-12 09:55 S becomes a false tight)
def _sess(P):
    key = ('rcn_sess',)
    if key in P: return P[key]
    n = len(P['C']); st = [i for i, x in enumerate(P['daystart']) if x] + [n]
    S = list(zip(st[:-1], st[1:])); idx = [0] * n
    for k, (a, b) in enumerate(S):
        for i in range(a, b): idx[i] = k
    P[key] = (S, idx); return P[key]
def _ev(P, j, d):
    O, H, L, C, V = P['O'], P['H'], P['L'], P['C'], P['V']; A = P[('atr', 14)][j]
    if A is None or A <= 0 or j < 11: return False
    o, h, l, c = O[j], H[j], L[j], C[j]; rng = h - l
    if rng <= 0 or d * (c - o) <= 0 or rng < 0.8 * A or abs(c - o) / rng * 100 < 55: return False
    if ((h - c) if d > 0 else (c - l)) / rng * 100 > 25: return False
    x = (h if d > 0 else l) if WICK else c
    if not ((x > max(H[j - 10:j])) if d > 0 else (x < min(L[j - 10:j]))): return False
    if P['sinceStart'][j] >= 3 and not d * (V[j] - V[j - 3]) > 0: return False
    return True
def _sig(P):
    key = ('rcn_sig', WICK)
    if key not in P: P[key] = [1 if _ev(P, j, 1) else (-1 if _ev(P, j, -1) else 0) for j in range(len(P['C']))]
    return P[key]
def is_tight(P, i, d):
    S, idx = _sess(P); k = idx[i]
    if k == 0: return False
    sg = _sig(P); a = S[k][0]; pa, pb = S[k - 1]
    if any(sg[j] == d for j in range(a, i)): return False
    return d * sum(sg[pa:pb]) <= -NET
def stop_fn(P, i, d, entry, stop, A, ctx):
    if is_tight(P, i, d):
        ext = P['L'][i] if d > 0 else P['H'][i]
        return entry - d * max(0.9 * A, d * (entry - ext))
    return stop
