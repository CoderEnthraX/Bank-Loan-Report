"""Session-first-bar displacement signals (blocked by minOpenBars=1): list with features + whether the original took them."""
import sys, os
S='/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad'
sys.path.insert(0, S+'/fit'); sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import dm
from engine2 import prepare
from engine import rma
for sym in ('SENSEX','NIFTY','CRUDE','GC','NASDAQ','US30','EURUSD','ETH'):
    P = prepare(sym); T=P['T']; D=P['daystart']; O,H,L,C,V=P['O'],P['H'],P['L'],P['C'],P['V']; A=rma(P['tr'],14)
    base = {t['arm'] for t in dm.run(sym, {"dayStopR":0})}
    alt = dm.run(sym, {"dayStopR":0, "minOpenBars":0})
    for t in alt:
        if D[t['arm']] and t['arm'] not in base:
            i=t['arm']; d=t['dir']; pv = V[i-1]
            print(f"{sym:6s} {T[i]} {'L' if d>0 else 'S'} fill {T[t['fill']][11:]} res {t['res']} | gap/ATR {d*(O[i]-C[i-1])/A[i]:+.2f} c-prevVWAP/ATR {d*(C[i]-pv)/A[i]:+.2f} c-hlc3/ATR {d*(C[i]-V[i])/A[i]:+.2f} rng/ATR {(H[i]-L[i])/A[i]:.2f} TR/ATRprev {P['tr'][i]/A[i-1]:.2f}")
