import sys, math
FIT='/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fit'
sys.path.insert(0, FIT)
from engine2 import prepare
from adxfit import dmi
def ema(x, n):
    a = 2 / (n + 1); o = []; s = None
    for v in x: s = v if s is None else a * v + (1 - a) * s; o.append(s)
    return o
SNAP = [('CRUDE','2026-10-09 13:40','TRANSITION 20 BEAR'),('EURUSD','2026-10-12 12:50','TRANSITION 21 BEAR'),('GC','2026-10-12 13:00','TRANSITION/RANGING 34 NEUT'),
        ('NASDAQ','2026-10-12 12:45','RANGING 32 NEUT'),('NASDAQ','2026-10-09 13:40','RANGING 36 NEUT'),('NIFTY','2026-10-12 12:10','TRENDING 39 BEAR'),('NIFTY','2026-10-12 12:40','TRENDING 36 BEAR'),
        ('SENSEX','2026-10-12 12:40','TRANSITION 38 BEAR'),('US30','2026-10-12 13:00','RANGING 29 NEUT')]
for s, t, lab in SNAP:
    P = prepare(s); T = P['T']
    if 'dmi' not in P: P['dmi'] = dmi(P['rows'], 14, 14)
    dip, dim, adx = P['dmi']; C = P['C']
    e20 = P.setdefault('e20', ema(C, 20)); e50 = P.setdefault('e50', ema(C, 50)); e200 = P.setdefault('e200', ema(C, 200))
    for tt in [t]:
        if tt not in T: print(s, tt, 'missing'); continue
        i = T.index(tt)
        print(f"{s:6s} {tt} {lab:28s} ADX {adx[i]:5.1f} sl3 {adx[i]-adx[i-3]:+5.1f} sl1 {adx[i]-adx[i-1]:+5.1f} DI+ {dip[i]:5.1f} DI- {dim[i]:5.1f} C-e20 {C[i]-e20[i]:+8.2f} e20-e50 {e20[i]-e50[i]:+8.2f} e50-e200 {e50[i]-e200[i]:+8.2f} V {C[i]-P['V'][i]:+8.2f}")
