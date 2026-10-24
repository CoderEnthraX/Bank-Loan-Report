import sys
sys.path.insert(0,'/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fit')
from arp_data import load
rows=load('NIFTY'); ts=[r['t'] for r in rows]
T=[('2026-10-05 09:35',1,22564.60,22528.45),('2026-10-05 10:40',-1,22474.00,22540.80),('2026-10-06 09:50',1,22629.95,22580.30),
('2026-10-07 10:30',1,22686.00,22637.15),('2026-10-07 11:00',1,22701.60,22652.15),('2026-10-08 10:40',-1,22432.60,22482.42),
('2026-10-08 13:20',-1,22254.31,22302.91),('2026-10-09 10:10',1,22480.45,22449.38),('2026-10-09 13:50',1,22517.51,22485.20),('2026-10-12 09:55',-1,22499.25,22559.84)]
for t,d,e,s in T:
    i=ts.index(t); R=abs(e-s); tp=e+d*2*R
    for j in range(i,len(rows)):
        r=rows[j]
        hs = (r['l']<=s) if d>0 else (r['h']>=s)
        ht = (r['h']>=tp) if d>0 else (r['l']<=tp)
        if hs or ht:
            print(t,d,'R%.2f tp4 %.2f'%(R,tp),'exit',r['t'],'STOP' if hs else '','TP4' if ht else '', 'O%.2f H%.2f L%.2f C%.2f'%(r['o'],r['h'],r['l'],r['c']), 'prevbar',rows[i-1]['t']); break
    # fill check
    p=rows[i-1]; f=rows[i]
    print('   fillbar L%.2f H%.2f ; prev L%.2f H%.2f'%(f['l'],f['h'],p['l'],p['h']))
