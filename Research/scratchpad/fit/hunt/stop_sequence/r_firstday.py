"""Tight stop (max(0.9 ATR, beyond displacement candle extreme)) on the FIRST raw displacement of the session in that direction."""
import sys
sys.path.insert(0, '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fit/hunt/stop_sequence')
from sig import raw
def tight(P, i, d, entry, A):
    ext = P['L'][i] if d > 0 else P['H'][i]
    return entry - d * max(0.9 * A, d * (entry - ext))
def is_first(P, i, d):
    S = raw(P); ds = i - P['sinceStart'][i]
    return not any(S[j] == d for j in range(ds, i))
def stop_fn(P, i, d, entry, stop, A, ctx):
    return tight(P, i, d, entry, A) if is_first(P, i, d) else stop
