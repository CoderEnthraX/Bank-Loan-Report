import sys
sys.path.insert(0, '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fit'); sys.path.insert(0, D := '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fit/hunt/stop_sequence')
from bstate import *
SNAP = [('CRUDE','2026-10-09 13:40',-1),('EURUSD','2026-10-12 12:50',-1),('GC','2026-10-12 13:00',0),('NASDAQ','2026-10-12 12:45',0),('NASDAQ','2026-10-09 13:40',0),
        ('NIFTY','2026-10-12 12:10',-1),('NIFTY','2026-10-12 12:40',-1),('SENSEX','2026-10-12 12:40',-1),('US30','2026-10-12 13:00',0)]
for s, t, b in SNAP:
    P = prepare(s); i = P['T'].index(t); Dd = daily(P); k = dayidx(P, i); pd = Dd[k - 1]; td = Dd[k]
    ev = events(P, 'E2'); todays = [(P['T'][j][11:], ev[j]) for j in range(td['a'], i + 1) if ev[j]]
    print(f"{s:6s} {t} table {b:+d} pdDir {1 if pd['c']>pd['o'] else -1:+d} pd2 {1 if pd['c']>Dd[k-2]['c'] else -1:+d} today(o->c) {1 if P['C'][i]>td['o'] else -1:+d} vsPDH/L {1 if P['C'][i]>pd['h'] else (-1 if P['C'][i]<pd['l'] else 0):+d} B_E2 {bstate(P,i,'E2'):+d} sigs {todays}")
