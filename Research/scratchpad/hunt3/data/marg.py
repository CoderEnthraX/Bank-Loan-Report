"""Margins (in PRICE POINTS) of every displacement condition on given signal bars: could a 1-2 point data difference flip them?"""
import sys, os
S='/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad'
sys.path.insert(0, S+'/fit')
from engine2 import prepare
from engine import rma
CASES = [('CRUDE','2026-10-12 13:40',1),('CRUDE','2026-10-15 18:30',1),('CRUDE','2026-10-15 21:35',1),('CRUDE','2026-10-16 11:40',1),
         ('CRUDE','2026-10-06 20:55',1),('ETH','2026-10-11 00:05',1),('NIFTY','2026-10-07 09:35',-1),('SENSEX','2026-10-15 09:55',1),('SENSEX','2026-10-15 10:10',1)]
for sym, t, d in CASES:
    P = prepare(sym); T=P['T']; i=T.index(t); O,H,L,C,V=P['O'],P['H'],P['L'],P['C'],P['V']; A=rma(P['tr'],14)[i]
    rng=H[i]-L[i]; body=abs(C[i]-O[i])
    brk = d*(C[i]-(max(H[i-10:i]) if d>0 else min(L[i-10:i])))
    ext = 0.25*rng-((H[i]-C[i]) if d>0 else (C[i]-L[i]))
    m = dict(rng=rng-0.8*A, body=body-0.55*rng, ext=ext, brk10=brk, mom=d*(C[i]-C[i-10])-0.85*A, vwap=d*(C[i]-V[i]), slope=d*(V[i]-V[i-3]))
    k = min(m, key=lambda z: m[z])
    print(f"{sym:6s} {t} ATR {A:7.2f} | " + ' '.join(f"{a} {b:+.2f}" for a,b in m.items()) + f"  | thinnest: {k} {m[k]:+.2f} pts = {m[k]/A:+.3f} ATR")
