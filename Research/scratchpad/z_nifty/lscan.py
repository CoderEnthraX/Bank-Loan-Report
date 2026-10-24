import sys
sys.path.insert(0,'/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fit')
from engine import prepare, rma
P=prepare('NIFTY'); rows=P['rows']; atr=rma(P['tr'],14); ts=[r['t'] for r in rows]
C=[('T1','2026-10-05 09:25',1,22564.60),('T2','2026-10-05 10:35',-1,22474.00),('T3','2026-10-06 09:45',1,22629.95),('T4','2026-10-07 10:25',1,22686.00),('T5','2026-10-07 10:55',1,22701.60),
('T6','2026-10-08 10:35',-1,22432.60),('T7','2026-10-08 13:15',-1,22254.30),('T8','2026-10-09 10:05',1,22480.45),('T9','2026-10-09 13:40',1,22517.65),('T10','2026-10-12 09:50',-1,22499.225),
('skA','2026-10-07 09:35',-1,None),('skB','2026-10-07 13:05',-1,None),('skC','2026-10-08 12:15',-1,None)]
for L in range(3,16):
    out=[]
    for nm,t,d,ent in C:
        i=ts.index(t); r=rows[i]
        ph=max(x['h'] for x in rows[i-L:i]); pl=min(x['l'] for x in rows[i-L:i])
        lvl=ph if d>0 else pl; mid=(r['o']+r['c'])/2
        e=max(mid,ph) if d>0 else min(mid,pl)
        brk=d*(r['c']-lvl)
        flag='' if ent is None else ('ok' if abs(e-ent)<0.6 else 'X%.1f'%e)
        out.append(f"{nm}:{brk/atr[i]:+.2f}{flag}")
    print(L,' '.join(out))
