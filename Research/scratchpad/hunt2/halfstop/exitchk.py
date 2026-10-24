"""For each logged B trade: simulate exit with logged stop / normal 1.8 ATR / tight stop; report exit time and max TP (0.5R steps) vs log."""
import sys
S='/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad'
sys.path.insert(0, S+'/fit'); sys.path.insert(0, S+'/xl'); sys.path.insert(0, S+'/hunt2/halfstop')
from load_xl import load
from engine2 import prepare
from engine import rma
import bstops
X = {x['n']: x for x in load()}
def sim(P, f, d, e, s):
    H, L, T = P['H'], P['L'], P['T']; r = d * (e - s); mx = 0
    for i in range(f, min(f + 400, len(H))):
        if (L[i] <= s if d > 0 else H[i] >= s): return T[i][5:], mx
        fav = (H[i] - e) if d > 0 else (e - L[i])
        mx = max(mx, min(4, int(fav / r / 0.5 + 1e-9)))
        if mx >= 4: return T[i][5:], 4
    return 'open', mx
for o in bstops.OUT:
    x = X[o['n']]; P = prepare(o['sym']); O, H, L, C = P['O'], P['H'], P['L'], P['C']; A = rma(P['tr'], 14)
    j, f, d = o['j'], o['f'], o['d']; a = A[j]; mid = (O[j] + C[j]) / 2
    e = max(mid, max(H[j-6:j])) if d > 0 else min(mid, min(L[j-6:j]))
    hyp = dict(log=x['stop'], norm=e - d * 1.8 * a, tight=(min(e - 0.9 * a, L[j]) if d > 0 else max(e + 0.9 * a, H[j])))
    res = {k: sim(P, f, d, e, s) for k, s in hyp.items()}
    lg = (x['tout'], x['maxtp'])
    flag = '' if res['log'][0][6:] == x['tout'] else ' <-- logged stop inconsistent with exit'
    print(f"#{o['n']} {o['sym']:6s} {P['T'][f]} log exit {x['tout']} {x['maxtp']:5s} sr {o['sr']:.2f} | " + '  '.join(f"{k}:{v[0][6:]} TP{v[1]}" for k, v in res.items()) + flag)
