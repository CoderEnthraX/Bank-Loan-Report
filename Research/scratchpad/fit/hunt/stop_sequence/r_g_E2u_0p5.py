import sys
sys.path.insert(0, '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fit/hunt/stop_sequence')
from fdlib import *
def stop_fn(P, i, d, entry, stop, A, ctx):
    pd, p2, td = prevday(P, i, False)
    return tight(P, i, d, entry, A) if (first_today(P, i, d, ('vw','mom','vsl'), False) and d * (pd['c'] - pd['o']) < -0.5 * A) else stop
