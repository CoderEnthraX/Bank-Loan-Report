import sys
sys.path.insert(0, '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fit'); sys.path.insert(0, D := '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fit/hunt/stop_sequence')
from engine2 import prepare
from tightdata import TRADES
from bias import daily, dayidx
SEL = {('CRUDE','2026-10-08 10:50'), ('NASDAQ','2026-10-12 06:20'), ('NIFTY','2026-10-12 09:55'), ('NIFTY','2026-10-06 09:50'), ('ETH','2026-10-10 12:30')}
for t in TRADES:
    if not (t['tight'] or (t['sym'], t['fill']) in SEL): continue
    P = prepare(t['sym']); i = t['arm_i']; d = t['d']; A = P[('atr', 14)][i]; Dd = daily(P); k = dayidx(P, i); pd = Dd[k - 1]; td = Dd[k]; p2 = Dd[k-2]
    c = P['C'][i]
    def r(x): return d * (c - x) / A
    print(f"{t['sym']:6s} {t['fill']} {'L' if d>0 else 'S'} {'T' if t['tight'] else ' '} pd[{P['T'][pd['a']][5:]}..{P['T'][pd['b']-1][11:]}] O {pd['o']:.5g} H {pd['h']:.5g} L {pd['l']:.5g} C {pd['c']:.5g} | todayO {td['o']:.5g} arm C {c:.5g} | c-pdO {r(pd['o']):+.2f} c-pdC {r(pd['c']):+.2f} c-pdH {r(pd['h']):+.2f} c-pdL {r(pd['l']):+.2f} c-p2C {r(p2['c']):+.2f} c-tdO {r(td['o']):+.2f}  pdATRrng {(pd['h']-pd['l'])/A:.1f}")
