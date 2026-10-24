import sys, pickle, math
sys.path.insert(0, '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fit/hunt/stop_volatility')
from vlib import *
from tightdata import TRADES
rows = []
for t in TRADES:
    P = prepare(t['sym']); i = t['arm_i']; A = P[('atr', 14)]; tr = P['tr']; f = {}
    O, H, L, C = P['O'], P['H'], P['L'], P['C']
    rng = H[i] - L[i]
    for N in (50, 100, 200, 300, 500, 1000, 2000):
        if i - N < 20: continue
        w = [x for x in A[i - N:i] if x]
        f[f'atrPR{N}'] = sum(1 for x in w if x < A[i]) / len(w)
        f[f'atrXmax{N}'] = A[i] / max(w); f[f'atrXmin{N}'] = A[i] / min(w)
        m = sum(w) / len(w); sd = math.sqrt(sum((x - m) ** 2 for x in w) / len(w))
        f[f'atrZ{N}'] = (A[i] - m) / sd if sd else 0
        wt = tr[i - N:i]
        f[f'trPR{N}'] = sum(1 for x in wt if x < tr[i]) / N
        f[f'rngPR{N}'] = sum(1 for j in range(i - N, i) if H[j] - L[j] < rng) / N
        f[f'bodyPR{N}'] = sum(1 for j in range(i - N, i) if abs(C[j] - O[j]) < abs(C[i] - O[i])) / N
        f[f'riskXrng{N}'] = 1.8 * A[i] / (max(H[i - N:i]) - min(L[i - N:i]))
    f['first_bar_idx'] = i
    rows.append((t, f))
pickle.dump(rows, open('/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fit/hunt/stop_volatility/feat2.pkl', 'wb'))
