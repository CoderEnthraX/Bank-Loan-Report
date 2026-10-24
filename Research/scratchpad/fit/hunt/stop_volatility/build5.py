import sys, pickle, math
sys.path.insert(0, '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fit/hunt/stop_volatility')
from vlib import *
from tightdata import TRADES
def bbw(C, j, N=20, k=2.0):
    cs = C[j - N + 1:j + 1]; m = sum(cs) / N; sd = math.sqrt(sum((x - m) ** 2 for x in cs) / N)
    return 2 * k * sd
rows = []
for t in TRADES:
    P = prepare(t['sym']); i = t['arm_i']; d = t['d']; A = P[('atr', 14)]; O, H, L, C = P['O'], P['H'], P['L'], P['C']; f = {}
    a = A[i]
    for k in (1, 2):
        j = i - k
        f[f'sqz{k}'] = int(bbw(C, j) < 2 * 1.5 * A[j])
        f[f'bbwA{k}'] = bbw(C, j) / A[j]
    f['bbwA0'] = bbw(C, i) / a
    f['sqzCount20'] = sum(1 for j in range(i - 20, i) if bbw(C, j) < 2 * 1.5 * A[j])
    r = [H[j] - L[j] for j in range(i - 7, i)]
    f['nr7prev'] = int(r[-1] == min(r))
    f['insidePrev'] = int(H[i - 1] <= H[i - 2] and L[i - 1] >= L[i - 2])
    f['outsideDisp'] = int(H[i] >= H[i - 1] and L[i] <= L[i - 1])
    f['engulfBody'] = int(max(O[i], C[i]) >= max(O[i - 1], C[i - 1]) and min(O[i], C[i]) <= min(O[i - 1], C[i - 1]))
    f['prevSameColor'] = int(d * (C[i - 1] - O[i - 1]) > 0)
    k = 0
    while d * (C[i - 1 - k] - O[i - 1 - k]) > 0: k += 1
    f['runSameColor'] = k
    k = 0
    while d * (C[i - 1 - k] - O[i - 1 - k]) < 0: k += 1
    f['runOppColor'] = k
    # displacement relative to prior swing: bars since the 10-bar extreme being broken was set
    seg = H[i - 10:i] if d > 0 else L[i - 10:i]
    ext = max(seg) if d > 0 else min(seg)
    f['barsSinceBrokenExt'] = 10 - max(idx for idx, x in enumerate(seg) if x == ext)
    # fraction of disp range beyond the broken level
    f['beyondFrac'] = d * (C[i] - ext) / (H[i] - L[i])
    f['openBeyond'] = int(d * (O[i] - ext) > 0)
    rows.append((t, f))
pickle.dump(rows, open('/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fit/hunt/stop_volatility/feat5.pkl', 'wb'))
