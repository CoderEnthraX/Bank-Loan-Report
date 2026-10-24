import sys; sys.path.insert(0, '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fit/hunt/stop_author')
from alib import *
SN = [('CRUDE','2026-10-09 13:40','TRANS','B'),('EURUSD','2026-10-12 12:50','TRANS','B'),('GC','2026-10-12 12:45','T/R','N'),('GC','2026-10-12 12:55','T/R','N'),
      ('NASDAQ','2026-10-12 12:50','RANG','N'),('NASDAQ','2026-10-09 13:40','RANG','N'),('NIFTY','2026-10-12 12:40','TREND','B'),('NIFTY','2026-10-12 12:20','TREND','B'),
      ('SENSEX','2026-10-12 12:40','TRANS','B'),('US30','2026-10-12 12:50','RANG?','N?')]
for s, t, lab, b in SN:
    P = get(s); i = P['T'].index(t); out = []
    for m in (30, 60, 120, 240):
        h = htf_series(P, m)[i]
        p, q, a, rows = htf_dmi_at(P, m, i)
        C = [r['c'] for r in rows]; e20 = ema(C, 20); e50 = ema(C, 50)
        out.append(f"{m}: spr {h['spr']:+5.1f}/{p-q:+5.1f} e2050 {h['e2050']:+5.2f} adx {h['adx']:4.1f}/{a:4.1f}")
    print(f"{s:6s} {t[5:]} {lab:5s} {b:2s}| " + ' | '.join(out))
