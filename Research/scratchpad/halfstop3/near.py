"""Near-miss impulses: bars in [a,b] that fail the impulse test in exactly one condition (impBody 50), with the margins."""
import sys, datetime
sys.path.insert(0, '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fit')
from engine2 import prepare
from engine import rma
sym, a, b = sys.argv[1], sys.argv[2], sys.argv[3]
P = prepare(sym); T = P['T']; O, H, L, C, V = P['O'], P['H'], P['L'], P['C'], P['V']; A = rma(P['tr'], 14); ds = P['daystart']
vb = 0
for i in range(len(T)):
    vb = 0 if ds[i] else vb + 1
    if not (a <= T[i] <= b) or i < 12: continue
    rng = H[i] - L[i]; body = abs(C[i] - O[i])
    for d in (1, -1):
        dirOk = (C[i] > O[i]) if d > 0 else (C[i] < O[i])
        if not dirOk or rng <= 0: continue
        c = {}
        c['rng'] = rng / A[i] - 0.8
        c['body'] = body / rng * 100 - 50
        c['close'] = 25 - ((H[i] - C[i]) if d > 0 else (C[i] - L[i])) / rng * 100
        c['brk'] = ((H[i] - max(H[i-10:i])) if d > 0 else (min(L[i-10:i]) - L[i])) / A[i]
        sl = (V[i] - V[i-3]) * d if vb >= 3 else 1
        c['slope'] = sl / A[i]
        fails = [k for k, v in c.items() if v < 0 or (k == 'brk' and v <= 0) or (k == 'slope' and v <= 0)]
        if len(fails) <= 1:
            print(T[i], 'BULL' if d > 0 else 'BEAR', 'IMPULSE' if not fails else 'fails ' + fails[0], ' '.join(f'{k} {v:+.2f}' for k, v in c.items()), 'k', vb)
