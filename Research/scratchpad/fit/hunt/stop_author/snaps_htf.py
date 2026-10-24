import sys; sys.path.insert(0, '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fit/hunt/stop_author')
from alib import *
SN = [('CRUDE','2026-10-09 13:40','TRANS'),('EURUSD','2026-10-12 12:50','TRANS'),('GC','2026-10-12 12:45','T/R'),('GC','2026-10-12 12:55','T/R'),
      ('NASDAQ','2026-10-12 12:50','RANG'),('NASDAQ','2026-10-09 13:40','RANG'),('NIFTY','2026-10-12 12:40','TREND'),('NIFTY','2026-10-12 12:20','TREND'),
      ('SENSEX','2026-10-12 12:40','TRANS'),('US30','2026-10-12 12:50','RANG?')]
for s, t, lab in SN:
    P = get(s); i = P['T'].index(t); out = []
    for m in (15, 30, 60, 240):
        p, q, a, rows = htf_dmi_at(P, m, i)
        C = [r['c'] for r in rows]
        e = er(C, len(C) - 1, 10)
        out.append(f"{m}m adx {a:4.1f} spr {p-q:+5.1f} er10 {e:.2f}")
    print(f"{s:6s} {t[5:]} {lab:6s} | " + ' | '.join(out))
