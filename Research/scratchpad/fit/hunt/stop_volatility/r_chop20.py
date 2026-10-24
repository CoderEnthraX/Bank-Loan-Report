# tight (max(0.9A, disp extreme)) when Choppiness(20) at the displacement bar <= 30.2 (strong trend)
import sys; sys.path.insert(0, '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fit/hunt/stop_volatility')
from rulebase import *
def stop_fn(P, i, d, entry, stop, A, ctx):
    return tight_stop(P, i, d, entry, A) if chop(P, i, 20) <= 30.2 else stop
