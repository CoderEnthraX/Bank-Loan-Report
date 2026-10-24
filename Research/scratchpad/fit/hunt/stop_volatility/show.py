import sys
sys.path.insert(0, '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fit')
from tightdata import TRADES
from engine2 import prepare
from volrec import recover
for t in TRADES:
    if not t['tight'] and '-v' not in sys.argv: continue
    P = prepare(t['sym']); recover(t['sym']); i = t['arm_i']; A = P[('atr',14)]
    O,H,L,C,V,T = P['O'],P['H'],P['L'],P['C'],P['V'],P['T']
    print('====', t['sym'], t['fill'], 'arm', t['arm'], 'd', t['d'], 'TIGHT' if t['tight'] else '', 'stopR', round(t['stopR'],2), 'entry', t['entry'], t['out'], 'A', round(A[i],5))
    for j in range(i-12, t['fill_i']+1):
        print(f"  {j-i:+3d} {T[j]} O {O[j]:<10g} H {H[j]:<10g} L {L[j]:<10g} C {C[j]:<10g} rng/A {(H[j]-L[j])/A[i]:.2f} tr/A {P['tr'][j]/A[i]:.2f} vol {P['vol'][j] if P['vol'][j] is None else round(P['vol'][j],2)} ds {int(P['daystart'][j])}")
