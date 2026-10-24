import sys
sys.path.insert(0,'/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fit')
from arp_data import load
rows=load('NIFTY'); ts=[r['t'] for r in rows]
tr=[rows[0]['h']-rows[0]['l']]+[max(b['h']-b['l'],abs(b['h']-a['c']),abs(b['l']-a['c'])) for a,b in zip(rows,rows[1:])]
def rma(x,n):
    o=[];s=None
    for v in x: s=v if s is None else (s*(n-1)+v)/n; o.append(s)
    return o
def sma(x,n): return [sum(x[max(0,i-n+1):i+1])/len(x[max(0,i-n+1):i+1]) for i in range(len(x))]
a14=rma(tr,14); a50=rma(tr,50); a100=rma(tr,100); s200=sma(tr,200); a72=rma(tr,72)
C=[('0.9 L','2026-10-05 09:25'),('1.8 S','2026-10-05 10:35'),('1.8 L','2026-10-06 09:45'),('1.8 L','2026-10-07 10:25'),('1.8 L','2026-10-07 10:55'),('1.8 S','2026-10-08 10:35'),('1.8 S','2026-10-08 13:15'),('0.9 L','2026-10-09 10:05'),('1.8 L','2026-10-09 13:40'),('1.8 S','2026-10-12 09:50'),
('skipS','2026-10-07 09:35'),('skipS','2026-10-07 13:05'),('skipS','2026-10-08 12:15')]
for m,t in C:
    i=ts.index(t)
    print(m,t,'atr14 %.1f  /a50 %.2f /a100 %.2f /s200 %.2f /a72 %.2f  bars-since-open %d'%(a14[i],a14[i]/a50[i],a14[i]/a100[i],a14[i]/s200[i],a14[i]/a72[i], i-max(j for j in range(i+1) if ts[j][11:]=='09:15')))
