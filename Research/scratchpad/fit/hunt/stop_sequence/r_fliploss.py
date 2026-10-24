import sys
sys.path.insert(0, '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fit/hunt/stop_sequence')
from seqlib import *
def stop_fn(P, i, d, entry, stop, A, ctx):
    return tight(P, i, d, entry, A) if (flip_loss(ctx, d)) else stop
