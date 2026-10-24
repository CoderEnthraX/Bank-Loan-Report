import sys
sys.path.insert(0, '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fit/hunt/stop_author')
from dlib import *
from alib import get
SN = [('CRUDE','2026-10-09 13:40','BEAR'),('EURUSD','2026-10-12 12:50','BEAR'),('GC','2026-10-12 12:45','NEUT'),('GC','2026-10-12 13:00','NEUT'),
      ('NASDAQ','2026-10-12 12:45','NEUT'),('NASDAQ','2026-10-09 13:40','NEUT'),('NIFTY','2026-10-12 12:40','BEAR'),('NIFTY','2026-10-12 12:20','BEAR'),
      ('SENSEX','2026-10-12 12:40','BEAR'),('US30','2026-10-12 12:50','NEUT?'),('US30','2026-10-09 13:40','NEUT?')]
for s, t, b in SN:
    P = get(s); i = P['T'].index(t); A = P[('atr', 14)][i]
    for m in (True,):
        out, idx = sessions(P, m); k = idx[i]; s0, s1, s2 = out[k], out[k - 1], out[k - 2]
    evs = [(P['T'][j][11:], dd) for j in range(s0['a'], i + 1) for dd in (1, -1) if event(P, j, dd, ('vsl',))]
    evk = [(P['T'][j][11:], dd) for j in range(s0['a'], i + 1) for dd in (1, -1) if event(P, j, dd, ())]
    c = P['C'][i]; V = P['V']; sd = P['vsd'][i] or 0
    print(f"{s:6s} {t[5:]} {b:5s} pdBody {(s1['c']-s1['o'])/A:+6.2f} pdC2C {(s1['c']-s2['c'])/A:+6.2f} today {(c-s0['o'])/A:+6.2f} c-pdc {(c-s1['c'])/A:+6.2f} cv {(c-V[i])/A:+5.2f} cvsd {(c-V[i])/sd if sd else 0:+5.2f} vsl10 {(V[i]-V[i-10])/A:+5.2f} vsl3 {(V[i]-V[i-3])/A:+5.2f} lastEv {evs[-1] if evs else None} n {len(evs)} lastK {evk[-1] if evk else None}")
