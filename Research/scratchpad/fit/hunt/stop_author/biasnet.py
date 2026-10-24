import sys
sys.path.insert(0, '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fit/hunt/stop_author')
from dlib import *
from alib import get
SN = [('CRUDE','2026-10-09 13:40','BEAR'),('EURUSD','2026-10-12 12:50','BEAR'),('GC','2026-10-12 12:45','NEUT'),('GC','2026-10-12 13:00','NEUT'),
      ('NASDAQ','2026-10-12 12:45','NEUT'),('NASDAQ','2026-10-09 13:40','NEUT'),('NIFTY','2026-10-12 12:40','BEAR'),('NIFTY','2026-10-12 12:20','BEAR'),
      ('SENSEX','2026-10-12 12:40','BEAR'),('US30','2026-10-12 12:50','NEUT?'),('US30','2026-10-09 13:40','NEUT?')]
for s, t, b in SN:
    P = get(s); i = P['T'].index(t)
    for m in (False, True):
        out, idx = sessions(P, m); k = idx[i]; s0, s1 = out[k], out[k - 1]
        res = []
        for ex in (('vsl',), (), ('vsl', 'vw', 'mom'), ('vsl', 'wick')):
            pn = sum(1 for j in range(s1['a'], s1['b']) if event(P, j, 1, ex)) - sum(1 for j in range(s1['a'], s1['b']) if event(P, j, -1, ex))
            cn = sum(1 for j in range(s0['a'], i + 1) if event(P, j, 1, ex)) - sum(1 for j in range(s0['a'], i + 1) if event(P, j, -1, ex))
            r = sum(1 for j in range(i - 287, i + 1) if event(P, j, 1, ex)) - sum(1 for j in range(i - 287, i + 1) if event(P, j, -1, ex))
            r2 = sum(1 for j in range(i - 99, i + 1) if event(P, j, 1, ex)) - sum(1 for j in range(i - 99, i + 1) if event(P, j, -1, ex))
            res.append(f"{'+'.join(ex) or 'core':12s} prev {pn:+3d} cur {cn:+3d} r288 {r:+3d} r100 {r2:+3d}")
        print(f"{s:6s} {t[5:]} {b:5s} {'M' if m else 'U'} | " + ' | '.join(res))
