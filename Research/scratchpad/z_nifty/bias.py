import sys
sys.path.insert(0,'/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fit')
from arp_data import load
rows=load('NIFTY'); ts=[r['t'] for r in rows]
def ema(n):
    o=[];e=None;k=2/(n+1)
    for r in rows:
        e=r['c'] if e is None else e+k*(r['c']-e); o.append(e)
    return o
E={n:ema(n) for n in (20,50,100,200)}
cases=[('0.9','2026-10-05 09:25',1),('1.8','2026-10-05 10:35',-1),('1.8','2026-10-06 09:45',1),('1.8','2026-10-07 10:25',1),('1.8','2026-10-07 10:55',1),
('1.8','2026-10-08 10:35',-1),('1.8','2026-10-08 13:15',-1),('0.9','2026-10-09 10:05',1),('1.8','2026-10-09 13:40',1),('1.8','2026-10-12 09:50',-1),
('skip','2026-10-07 09:35',-1),('skip','2026-10-07 13:05',-1),('skip','2026-10-08 12:15',-1)]
# previous-day refs
days=sorted(set(t[:10] for t in ts))
def prevday(t):
    d=t[:10]; k=days.index(d); pd=days[k-1]
    pr=[r for r in rows if r['t'][:10]==pd]
    return dict(o=pr[0]['o'],h=max(r['h'] for r in pr),l=min(r['l'] for r in pr),c=pr[-1]['c'],vw=pr[-1]['vwap'])
for m,t,d in cases:
    i=ts.index(t); c=rows[i]['c']; p=prevday(t)
    s=' '.join(f"e{n}:{d*(c-E[n][i]):+6.1f}" for n in (20,50,100,200))
    print(m,t,f"d{d:+d}",s, f" vs PDC {d*(c-p['c']):+6.1f} PDH {c-p['h']:+6.1f} PDL {c-p['l']:+6.1f} PDvwap {d*(c-p['vw']):+6.1f} pday {'up' if p['c']>p['o'] else 'dn'}")
