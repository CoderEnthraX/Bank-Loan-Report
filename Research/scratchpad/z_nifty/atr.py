import sys
sys.path.insert(0,'/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fit')
from arp_data import load
rows=load('NIFTY'); byt={r['t']:r for r in rows}
def atr_series(n):
    out={}; a=None; pc=None
    for r in rows:
        tr=r['h']-r['l'] if pc is None else max(r['h']-r['l'],abs(r['h']-pc),abs(r['l']-pc))
        a=tr if a is None else (a*(n-1)+tr)/n
        out[r['t']]=a; pc=r['c']
    return out
A={n:atr_series(n) for n in (10,14,20)}
trades=[('2026-10-05 09:35',22564.60,22528.45),('2026-10-05 10:40',22474.00,22540.8),('2026-10-06 09:50',22629.95,22580.4),
('2026-10-07 10:30',22686.00,22637.15),('2026-10-07 11:00',22701.60,22652.15),('2026-10-08 10:40',22432.60,22482.4),
('2026-10-08 13:20',22254.30,22303.0),('2026-10-09 10:10',22480.45,22449.4),('2026-10-09 13:50',22517.65,22485.2),('2026-10-12 09:55',22499.225,22559.8)]
ts=[r['t'] for r in rows]
for t,e,s in trades:
    i=ts.index(t); R=abs(e-s)
    prev=ts[i-1]; prev2=ts[i-2]
    print(t,'R %.2f'%R, ' '.join('atr%d[fill-1] %.2f R/atr %.3f'%(n,A[n][prev],R/A[n][prev]) for n in (14,)), ' atr14[fill-2] %.2f R/ %.3f'%(A[14][prev2],R/A[14][prev2]))
