import sys
sys.path.insert(0, '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fit/hunt/stop_sequence')
from pdlib import *
def stop_fn(P, i, d, entry, stop, A, ctx):
    return tight(P, i, d, entry, A) if (first_e(P, i, d, 'E1') and pd2(P, i, d) < 0) else stop
