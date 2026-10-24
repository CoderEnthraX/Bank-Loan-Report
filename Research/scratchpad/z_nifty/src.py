import sys
sys.path.insert(0,'/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fit')
from engine import prepare, rma
P=prepare('NIFTY'); rows=P['rows']; atr=rma(P['tr'],14); ts=[r['t'] for r in rows]
C=[('2026-10-05 09:25',1,22564.69,22528.47,0.9),('2026-10-05 10:35',-1,22473.87,22540.80,1.8),('2026-10-06 09:45',1,22630.18,22580.26,1.8),('2026-10-07 10:25',1,22686.13,22637.15,1.8),
('2026-10-07 10:55',1,22701.71,22652.15,1.8),('2026-10-08 10:35',-1,22432.67,22482.42,1.8),('2026-10-08 13:15',-1,22254.31,22302.91,1.8),('2026-10-09 10:05',1,22480.60,22449.38,0.9),
('2026-10-09 13:40',1,22517.51,22485.20,1.8),('2026-10-12 09:50',-1,22499.25,22559.84,1.8)]
for t,d,em,sm,k in C:
    i=ts.index(t); r=rows[i]; mid=(r['o']+r['c'])/2
    cands=[('mid %s'%t[11:],mid)]
    for j in range(i-8,i+1):
        cands.append(('H %s'%ts[j][11:],rows[j]['h'])); cands.append(('L %s'%ts[j][11:],rows[j]['l']))
        cands.append(('mid %s'%ts[j][11:],(rows[j]['o']+rows[j]['c'])/2))
    best=sorted(cands,key=lambda c:abs(c[1]-em))[:3]
    print(t,d,'meas e %.2f s %.2f'%(em,sm),'best',[(a,round(b,3)) for a,b in best],'| mid %.3f atr %.3f stop_k %.2f  measR %.2f  kATR %.2f'%(mid,atr[i],sm,abs(em-sm),k*atr[i]))
