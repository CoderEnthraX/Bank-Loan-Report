import sys, pickle, math
sys.path.insert(0, '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fit/hunt/stop_volatility')
from vlib import *
from tightdata import TRADES
rows = []
for t in TRADES:
    P = prepare(t['sym']); recover(t['sym']); i = t['arm_i']; d = t['d']; A = P[('atr', 14)][i]; V = P['V']; f = {}
    s0 = sess_start(P, i)
    for k in (1, 2, 3, 5, 10):
        if i - k >= s0: f[f'vwSlope{k}'] = d * (V[i] - V[i - k]) / A
    f['vsdA'] = (P['vsd'][i] or 0) / A
    f['vsdA_prev'] = (P['vsd'][i - 1] or 0) / A if i - 1 >= s0 else None
    # VWAP slope sign-run: bars since VWAP slope (1-bar) turned in direction d
    k = 0
    while i - k - 1 >= s0 and d * (V[i - k] - V[i - k - 1]) > 0: k += 1
    f['vwRun'] = k
    # cumulative session volume-weighted vol (VWAP-dev of hlc3 sd normalised by ATR) already vsdA; also close-VWAP in sd
    sd = P['vsd'][i]
    f['zVW'] = d * (P['C'][i] - V[i]) / sd if sd else None
    rows.append((t, {a: b for a, b in f.items() if b is not None}))
pickle.dump(rows, open('/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fit/hunt/stop_volatility/feat4.pkl', 'wb'))
