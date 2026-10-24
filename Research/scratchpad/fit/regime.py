import sys, os, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from engine2 import prepare
from adxfit import dmi
from engine import rma
OBS = [('GC','2026-10-09 14:00','TRANSITION',20,'BULLISH'),('GC','2026-10-09 21:05','RANGING',13,'BULLISH'),('GC','2026-10-10 01:05','RANGING',15,'BULLISH'),
       ('GC','2026-10-12 06:40','TRANSITION',30,'NEUTRAL'),('EURUSD','2026-10-09 12:50','TRANSITION',21,'BULLISH'),('EURUSD','2026-10-09 13:40','RANGING',15,'NEUTRAL'),
       ('EURUSD','2026-10-12 06:40','TRENDING',41,'BULLISH'),('NIFTY','2026-10-12 12:40','TRENDING',36,'BEARISH'),('SENSEX','2026-10-12 12:40','TRANSITION',38,'BEARISH'),
       ('NASDAQ','2026-10-12 12:50','RANGING',32,'NEUTRAL')]
def er(C, i, n): 
    ch = abs(C[i] - C[i-n]); vol = sum(abs(C[k] - C[k-1]) for k in range(i-n+1, i+1)); return ch / vol if vol else 0
def chop(P, i, n=14):
    H, L = P['H'], P['L']; tr = P['tr']; s = sum(tr[i-n+1:i+1]); rg = max(H[i-n+1:i+1]) - min(L[i-n+1:i+1])
    return 100 * math.log10(s / rg) / math.log10(n) if rg > 0 else 0
for sym, t, reg, adxv, bias in OBS:
    P = prepare(sym); T = P['T']; i = T.index(t); C, V = P['C'], P['V']
    if 'dmi' not in P: P['dmi'] = dmi(P['rows'], 14, 14)
    dip, dim, adx = P['dmi']
    if ('atr', 14) not in P: P[('atr', 14)] = rma(P['tr'], 14)
    A = P[('atr', 14)][i]
    print(f"{sym:6s} {t[5:]} {reg:10s} {bias:7s} | ADX {adx[i]:4.1f} (shown {adxv}) dADX1 {adx[i]-adx[i-1]:+4.1f} dADX5 {adx[i]-adx[i-5]:+5.1f} DI+ {dip[i]:4.1f} DI- {dim[i]:4.1f} "
          f"spr {dip[i]-dim[i]:+5.1f} | c-vwap {(C[i]-V[i])/A:+5.2f}A vwapSlope10 {(V[i]-V[i-10])/A:+5.2f}A ER10 {er(C,i,10):.2f} ER20 {er(C,i,20):.2f} CHOP {chop(P,i):4.1f}")
