# OVERFIT upper-bound demo (not a plausible rule): tight when Choppiness(20) <= 30.16 OR 5-bar VWAP slope against the trade <= -0.0385 ATR
import sys; sys.path.insert(0, '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fit/hunt/stop_volatility')
from rulebase import *
def stop_fn(P, i, d, entry, stop, A, ctx):
    V = P['V']; s0 = i - P['sinceStart'][i]
    vs = d * (V[i] - V[i - 5]) / A if i - 5 >= s0 and V[i - 5] is not None else 0.0
    return tight_stop(P, i, d, entry, A) if (chop(P, i, 20) <= 30.161 or vs <= -0.0385) else stop
