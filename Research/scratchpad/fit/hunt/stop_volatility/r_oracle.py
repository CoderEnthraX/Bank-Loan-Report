# ORACLE check (not a rule): tight exactly on the 8 known arm bars, to confirm the harness reaches 74/6/6
import sys; sys.path.insert(0, '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fit/hunt/stop_volatility')
from rulebase import *
from tightdata import TRADES
S = {(t['sym'], t['arm']) for t in TRADES if t['tight']}
def stop_fn(P, i, d, entry, stop, A, ctx):
    return tight_stop(P, i, d, entry, A) if (P['sym'], P['T'][i]) in S else stop
