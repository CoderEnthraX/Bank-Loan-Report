import sys
sys.path.insert(0, D := '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fit/hunt/stop_sequence')
from feat import *
rows, out = table(True)
for t, f in rows:
    if not f: continue
    s = t['sym']; i = t['arm_i']
    R = [x['res'] for x in out[s] if x['exit'] is not None and x['exit'] <= i]
    for k in list(f.keys()): del f[k]
    for N in range(13, 41):
        f[f'sumR{N}'] = sum(R[-N:]); f[f'wins{N}'] = sum(1 for r in R[-N:] if r > 0)
    # equity vs its EMA / SMA of trades
    eq = [0]
    for r in R: eq.append(eq[-1] + r)
    for N in (5, 10, 20, 30):
        f[f'eqSMA{N}'] = eq[-1] - sum(eq[-N:]) / len(eq[-N:])
        f[f'eqMax{N}'] = eq[-1] - max(eq[-N:]); f[f'eqMin{N}'] = eq[-1] - min(eq[-N:])
res, n = sep(rows)
seen = set()
for r in res:
    if r[2] in seen: continue
    seen.add(r[2]); print(r)
    if len(seen) > 12: break
