import sys, pickle
sys.path.insert(0, '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fit/hunt/stop_volatility')
from vlib import *
from tightdata import TRADES
rows = []
for t in TRADES:
    P = prepare(t['sym'])
    rows.append((t, features(P, t['arm_i'], t['d'], t['entry'])))
pickle.dump(rows, open('/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fit/hunt/stop_volatility/feat.pkl', 'wb'))
print(len(rows), 'rows', len(rows[0][1]), 'features')
