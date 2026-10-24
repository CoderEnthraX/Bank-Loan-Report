import sys
sys.path.insert(0, '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fit/hunt/stop_sequence')
from sig import raw
def tight(P, i, d, entry, A):
    ext = P['L'][i] if d > 0 else P['H'][i]
    return entry - d * max(0.9 * A, d * (entry - ext))
def first_day(P, i, d):
    S = raw(P); ds = i - P['sinceStart'][i]
    return not any(S[j] == d for j in range(ds, i))
def prev(ctx): return ctx['trades'][-1] if ctx['trades'] else None
def flip(ctx, d): p = prev(ctx); return p is not None and p['dir'] == -d
def flip_loss(ctx, d): p = prev(ctx); return p is not None and p['dir'] == -d and p['res'] < 0
def sumR(ctx, n): return sum(x['res'] for x in ctx['trades'][-n:])
