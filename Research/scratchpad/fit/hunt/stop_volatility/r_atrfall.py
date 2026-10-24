# tight when ATR14 fell on the displacement bar (ATR[i-1] >= 1.014 ATR[i], i.e. TR well below the prior ATR)
import sys; sys.path.insert(0, '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fit/hunt/stop_volatility')
from rulebase import *
def stop_fn(P, i, d, entry, stop, A, ctx):
    a = P[('atr', 14)]
    return tight_stop(P, i, d, entry, A) if a[i - 1] is not None and a[i - 1] >= 1.014 * a[i] else stop
