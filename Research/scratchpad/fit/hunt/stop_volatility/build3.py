import sys, pickle, math
sys.path.insert(0, '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fit/hunt/stop_volatility')
from vlib import *
from tightdata import TRADES
rows = []
for t in TRADES:
    P = prepare(t['sym']); i = t['arm_i']; fi = t['fill_i']; d = t['d']; e = t['entry']
    A = P[('atr', 14)]; tr = P['tr']; O, H, L, C = P['O'], P['H'], P['L'], P['C']; f = {}
    a = A[i]
    f['fillRngA'] = (H[fi] - L[fi]) / a; f['fillTrA'] = tr[fi] / a
    f['atrFillXarm'] = A[fi] / a; f['atrFillm1Xarm'] = A[fi - 1] / a
    f['fillBody'] = d * (C[fi] - O[fi]) / a
    f['fillPen'] = d * (e - (L[fi] if d > 0 else H[fi])) / a
    f['fillClose'] = d * (C[fi] - e) / a
    f['fillOpen'] = d * (O[fi] - e) / a
    f['fillGap'] = d * (O[fi] - C[fi - 1]) / a
    mids = range(i + 1, fi)
    if fi > i + 1:
        f['runup'] = d * ((max(H[j] for j in mids) if d > 0 else min(L[j] for j in mids)) - e) / a
        f['midMaxRng'] = max(H[j] - L[j] for j in mids) / a
    else:
        f['runup'] = d * ((H[i] if d > 0 else L[i]) - e) / a; f['midMaxRng'] = 0
    f['runupInclArm'] = d * ((max(H[j] for j in range(i, fi)) if d > 0 else min(L[j] for j in range(i, fi))) - e) / a
    f['nbars'] = fi - i
    f['retraceFrac'] = d * ((max(H[j] for j in range(i, fi)) if d > 0 else min(L[j] for j in range(i, fi))) - (L[fi] if d > 0 else H[fi])) / max(1e-12, (max(H[j] for j in range(i, fi)) - min(L[j] for j in range(i, fi))))
    # fill bar features in candle terms (relative to its own ATR)
    f['fillRngAf'] = (H[fi] - L[fi]) / A[fi]
    f['fillOppDisp'] = int(raw_disp(P, fi, A[fi]) == -d)
    f['fillSameDisp'] = int(raw_disp(P, fi, A[fi]) == d)
    rows.append((t, f))
pickle.dump(rows, open('/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fit/hunt/stop_volatility/feat3.pkl', 'wb'))
