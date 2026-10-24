# tight when first displacement signal of the session in this direction AND TR <= 0.8 x mean TR of previous 3 bars
import sys; sys.path.insert(0, '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fit/hunt/stop_volatility')
from rulebase import *
def stop_fn(P, i, d, entry, stop, A, ctx):
    tr = P['tr']
    return tight_stop(P, i, d, entry, A) if first_in_session(P, i, d) and tr[i] <= 0.8 * sum(tr[i - 3:i]) / 3 else stop
