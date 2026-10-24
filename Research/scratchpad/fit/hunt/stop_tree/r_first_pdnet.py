"""hookeval rule (stop_tree R1, self-contained): TIGHT stop when
   (1) no earlier displacement-candle event in the same direction in the current session, and
   (2) the previous session's NET event count (events in trade direction minus events against it) <= -NET_MAX.
event(j, d) = candle closes in direction d, range >= 0.8 ATR14, body >= 55% of range, close within 25% of its extreme,
              close beyond the prior 10-bar high (L) / low (S), VWAP rising (L) / falling (S) vs 3 bars ago
              (slope test skipped in the first 3 bars of a session).   [EVENTS = 'vsl']
session = VWAP reset (P['daystart']), no merging.
tight stop = entry - d * max(0.9 * ATR14, d * (entry - displacement low/high)); otherwise the default 1.8 ATR stop."""
import os, json
NET_MAX = float(os.environ.get('R1_NET', '2.5'))
EXTRA = tuple(os.environ.get('R1_EXTRA', 'vsl').split(',')) if os.environ.get('R1_EXTRA', 'vsl') else ()


def _ev(P, j, d):
    O, H, L, C, V = P['O'], P['H'], P['L'], P['C'], P['V']; A = P[('atr', 14)][j]
    if A is None or A <= 0 or j < 11: return False
    o, h, l, c = O[j], H[j], L[j], C[j]; rng = h - l
    if rng <= 0 or d * (c - o) <= 0 or rng < 0.8 * A or abs(c - o) / rng * 100 < 55: return False
    if ((h - c) if d > 0 else (c - l)) / rng * 100 > 25: return False
    if not ((c > max(H[j - 10:j])) if d > 0 else (c < min(L[j - 10:j]))): return False
    if 'vw' in EXTRA and not (V[j] is not None and d * (c - V[j]) > 0): return False
    if 'mom' in EXTRA and d * (c - C[j - 10]) < 0.85 * A: return False
    if 'vsl' in EXTRA and P['sinceStart'][j] >= 3 and not d * (V[j] - V[j - 3]) > 0: return False
    if 'first' in EXTRA and P['sinceStart'][j] < 1: return False
    if 'sun' in EXTRA and P['dowutc'][j] == 6: return False
    return True


def _sig(P):
    key = ('R1sig', EXTRA)
    if key not in P:
        P[key] = [1 if _ev(P, j, 1) else (-1 if _ev(P, j, -1) else 0) for j in range(len(P['C']))]
    return P[key]


def is_tight(P, i, d):
    sg = _sig(P); a = i - P['sinceStart'][i]
    if any(sg[j] == d for j in range(a, i)): return False
    if a == 0: return False
    pa = a - 1 - P['sinceStart'][a - 1]
    net = d * sum(sg[j] for j in range(pa, a))
    return net <= -NET_MAX


def stop_fn(P, i, d, entry, stop, A, ctx):
    if is_tight(P, i, d):
        ext = P['L'][i] if d > 0 else P['H'][i]
        return entry - d * max(0.9 * A, d * (entry - ext))
    return stop
