import sys
sys.path.insert(0, '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fit'); sys.path.insert(0, '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fit/hunt/stop_sequence')
from bstate import events, daily, dayidx
def tight(P, i, d, entry, A):
    ext = P['L'][i] if d > 0 else P['H'][i]
    return entry - d * max(0.9 * A, d * (entry - ext))
def first_e(P, i, d, kind='E1'):
    ev = events(P, kind); ds = i - P['sinceStart'][i]
    return not any(ev[j] == d for j in range(ds, i))
def pdbody(P, i, d):
    Dd = daily(P); k = dayidx(P, i); pd = Dd[k - 1]; return d * (pd['c'] - pd['o']) / P[('atr', 14)][i]
def pd2(P, i, d):
    Dd = daily(P); k = dayidx(P, i); return d * (Dd[k - 1]['c'] - Dd[k - 2]['c']) / P[('atr', 14)][i]
