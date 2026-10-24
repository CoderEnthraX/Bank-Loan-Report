"""shared helpers for hookeval rule modules (key stop_levels)"""
import sys; sys.path.insert(0, '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fit/hunt/stop_levels')
from lv import levels, nlevels
def tight_stop(P, i, d, entry, A):
    ext = P['L'][i] if d > 0 else P['H'][i]
    return entry - d * max(0.9 * A, d * (entry - ext))
def make(feat, lo, hi):
    def stop_fn(P, i, d, entry, stop, A, ctx):
        x = nlevels(P, i, d, entry, A).get(feat)
        if x is not None and lo < x < hi: return tight_stop(P, i, d, entry, A)
        return stop
    return stop_fn
