import sys
sys.path.insert(0, '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fit')
from engine import prepare, rma
P = prepare('CRUDE'); rows = P['rows']; tr = P['tr']; ds = P['daystart']
# gapless TR: first bar of a session uses H-L
tr2 = [ (r['h']-r['l']) if ds[i] else tr[i] for i,r in enumerate(rows)]
a = rma(tr,14); b = rma(tr2,14)
from statistics import mean
idx={r['t']:r['i'] for r in rows}
# observed orig R at arm bars
obs = [('2026-10-06 14:45',44.84),('2026-10-06 21:50',41.3),('2026-10-07 11:30',27.9),('2026-10-07 13:20',34.94),('2026-10-07 19:00',39.7),
       ('2026-10-07 20:05',42.8),('2026-10-07 22:35',41.1),('2026-10-08 10:45',23.65),('2026-10-08 12:15',23.35),('2026-10-08 13:00',30.15),
       ('2026-10-08 20:20',46.7),('2026-10-09 10:25',15.13),('2026-10-09 11:50',29.8)]
for t,R in obs:
    i=idx[t]
    print(t, 'R', R, 'R/ATR14 %.3f' % (R/a[i]), 'R/gaplessATR %.3f' % (R/b[i]), 'ATR %.2f gapless %.2f' % (a[i], b[i]))
