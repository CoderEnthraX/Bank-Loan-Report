import sys
sys.path.insert(0,'/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fit')
from arp_data import load
rows=load('NIFTY'); ts=[r['t'] for r in rows]
T=[('2026-10-05 09:25',1,'ctr'),('2026-10-05 10:35',-1,'with'),('2026-10-06 09:45',1,'with'),('2026-10-07 10:25',1,'with'),('2026-10-07 10:55',1,'with'),
('2026-10-08 10:35',-1,'with'),('2026-10-08 13:15',-1,'with'),('2026-10-09 10:05',1,'ctr'),('2026-10-09 13:40',1,'with'),('2026-10-12 09:50',-1,'with')]
extra=[('2026-10-07 09:35',-1,'skip'),('2026-10-07 13:05',-1,'skip'),('2026-10-08 12:15',-1,'skip'),('2026-10-12 12:40',-1,'tableBEARISH')]
def bucket(t,mins):
    h,m=int(t[11:13]),int(t[14:16]); tot=h*60+m-(9*60+15)
    return t[:10]+'-%03d'%(tot//mins)
res=[]
for mins in (15,30,60,75,125,375):
    # build HTF bars
    keys=[];closes=[];last_of={}
    for i,r in enumerate(rows):
        b=bucket(r['t'],mins) if mins<375 else r['t'][:10]
        if not keys or keys[-1]!=b: keys.append(b); closes.append(r['c'])
        else: closes[-1]=r['c']
        last_of[i]=len(keys)-1
    for n in (5,8,9,10,12,13,14,20,21,26,34,50,55,100,200):
        for mode in ('confirmed','live'):
            # EMA on HTF closes
            k=2/(n+1); e=[];s=None
            for c in closes: s=c if s is None else s+k*(c-s); e.append(s)
            def val(i):
                j=last_of[i]
                if mode=='confirmed':
                    return e[j-1]
                # live: EMA including partial current HTF bar
                prev=e[j-1]; return prev+k*(rows[i]['c']-prev)
            ok=all(((d*(rows[ts.index(t)]['c']-val(ts.index(t)))>0)==(lab=='with')) for t,d,lab in T)
            if ok:
                res.append((mins,n,mode,[(t[5:],lab,round(d*(rows[ts.index(t)]['c']-val(ts.index(t))),1)) for t,d,lab in T+extra]))
for r in res: print(r[:3]); print('   ',r[3])
