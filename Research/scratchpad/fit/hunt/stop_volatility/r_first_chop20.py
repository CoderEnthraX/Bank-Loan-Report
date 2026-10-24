# tight when first displacement of the session in this direction AND Choppiness(20) <= 30.2
import sys; sys.path.insert(0, '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fit/hunt/stop_volatility')
from rulebase import *
def stop_fn(P, i, d, entry, stop, A, ctx):
    return tight_stop(P, i, d, entry, A) if first_in_session(P, i, d) and chop(P, i, 20) <= 30.2 else stop
