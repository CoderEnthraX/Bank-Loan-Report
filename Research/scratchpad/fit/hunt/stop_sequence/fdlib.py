"""Rule library: tight stop = max(0.9 ATR, beyond displacement candle) when the displacement is the FIRST displacement-candle
of the session in its direction AND the previous session closed against it."""
import sys
sys.path.insert(0, '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fit'); sys.path.insert(0, '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fit/hunt/stop_sequence')
from nearsig import conds
from daily2 import daily2, dayidx2
from bias import daily, dayidx
_c = {}
def evd(P, j, d, inc):
    key = (P['sym'], j, d)
    if key not in _c: _c[key] = conds(P, j, d)
    r = _c[key]
    if not r: return False
    if not (r['dir'] and r['rng'] and r['body'] and r['clos'] and r['brk']): return False
    for k in ('vw', 'mom', 'vsl', 'first'):
        if k in inc and not r[k]: return False
    if 'sun' in inc and P['dowutc'][j] == 6: return False
    return True
def first_today(P, i, d, inc, merged=True):
    ds = (daily2(P)[dayidx2(P, i)]['a']) if merged else i - P['sinceStart'][i]
    return not any(evd(P, j, d, inc) for j in range(ds, i))
def prevday(P, i, merged=True):
    if merged: Dd = daily2(P); k = dayidx2(P, i)
    else: Dd = daily(P); k = dayidx(P, i)
    return Dd[k - 1], Dd[k - 2], Dd[k]
def tight(P, i, d, entry, A):
    ext = P['L'][i] if d > 0 else P['H'][i]
    return entry - d * max(0.9 * A, d * (entry - ext))
