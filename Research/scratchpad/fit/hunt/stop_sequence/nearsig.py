"""For each first-of-day-in-dir GT trade: earlier same-day bars in direction d failing exactly k conditions of the displacement test."""
import sys
sys.path.insert(0, D := '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fit/hunt/stop_sequence')
from pfeat import *
def conds(P, i, d):
    O, H, L, C, V = P['O'], P['H'], P['L'], P['C'], P['V']; a = P[('atr', 14)][i]
    if a is None or a <= 0 or i < 11: return None
    o, h, l, c = O[i], H[i], L[i], C[i]; rng = h - l
    if rng <= 0: return None
    r = {}
    r['dir'] = d * (c - o) > 0
    r['rng'] = rng >= 0.8 * a
    r['body'] = abs(c - o) / rng * 100 >= 55
    r['clos'] = ((h - c) if d > 0 else (c - l)) / rng * 100 <= 25
    r['brk'] = (c > max(H[i-10:i])) if d > 0 else (c < min(L[i-10:i]))
    r['vw'] = V[i] is not None and d * (c - V[i]) > 0
    r['mom'] = d * (c - C[i - 10]) >= 0.85 * a
    r['vsl'] = (P['sinceStart'][i] < 3) or d * (V[i] - V[i - 3]) > 0
    r['first'] = P['sinceStart'][i] >= 1
    return r
if __name__ == '__main__':
  for t in TRADES:
    P = prepare(t['sym']); i = t['arm_i']; d = t['d']; ds = i - P['sinceStart'][i]
    f = pf(t)
    if f['sameSigDay'] != 0: continue
    near = []
    for j in range(ds, i):
        r = conds(P, j, d)
        if not r or not r['dir']: continue
        fail = [k for k, v in r.items() if not v]
        if len(fail) <= 1: near.append(f"{P['T'][j][11:]}:{'/'.join(fail) or 'ALL'}")
    print(f"{t['sym']:6s} {t['fill']} {'L' if d>0 else 'S'} {'TIGHT' if t['tight'] else '     '} since={P['sinceStart'][i]:3d} near1: {' '.join(near)}")
