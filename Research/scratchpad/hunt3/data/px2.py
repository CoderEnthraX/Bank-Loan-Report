"""Entry source detail per matched trade: mid, level6, fill bar OHLC, rounding of model levels."""
import sys, os, json, math
S='/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad'
sys.path.insert(0, S+'/fit'); sys.path.insert(0, S+'/xl'); sys.path.insert(0, S+'/hunt3/data')
from load_xl import load
from engine2 import prepare
from engine import rma
import dm
fixT = {66: '09:40'}
for sym in ('SENSEX', 'CRUDE'):
    P = prepare(sym); T = P['T']; idx = {t: i for i, t in enumerate(T)}; O,H,L,C=P['O'],P['H'],P['L'],P['C']; A=rma(P['tr'],14)
    trades = dm.run(sym, {"dayStopR":0})
    print('=====', sym)
    for x in load():
        if x['sym'] != sym: continue
        f = idx.get(x['date'] + ' ' + fixT.get(x['n'], x['tin'])); m=None
        for t in trades:
            if t['dir'] == x['d'] and f is not None and abs(t['fill'] - f) <= 1 and (m is None or abs(t['fill']-f) < abs(m['fill']-f)): m = t
        if m is None: continue
        j = m['arm']; d = m['dir']; mid=(O[j]+C[j])/2; l6 = max(H[j-6:j]) if d>0 else min(L[j-6:j]); g=m['fill']
        src = 'mid' if m['entry']==mid else 'lvl6'
        print(f" #{x['n']} {'L' if d>0 else 'S'} log e {x['entry']:.0f} s {x['stop']:.0f} | model e {m['entry']:.2f} ({src}; mid {mid:.2f} lvl6 {l6:.2f}) s {m['stop']:.2f} | fillbar {T[g][11:]} O {O[g]} H {H[g]} L {L[g]} | signal O {O[j]} C {C[j]}  dE {x['entry']-m['entry']:+.2f} dS {x['stop']-m['stop']:+.2f} ({(x['stop']-m['stop'])/A[j]:+.3f} ATR)")
