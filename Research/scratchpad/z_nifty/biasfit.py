import sys
sys.path.insert(0,'/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fit')
from arp_data import load
rows=load('NIFTY'); ts=[r['t'] for r in rows]
cl=[r['c'] for r in rows]
def ema(x,n):
    o=[];s=None;k=2/(n+1)
    for v in x: s=v if s is None else s+k*(v-s); o.append(s)
    return o
def sma(x,n): 
    o=[];acc=0
    for i,v in enumerate(x):
        acc+=v
        if i>=n: acc-=x[i-n]
        o.append(acc/min(i+1,n))
    return o
# HTF closes: build 15m/30m/60m series aligned (value of last completed HTF bar + current partial)
T=[('2026-10-05 09:25',1,'ctr'),('2026-10-05 10:35',-1,'with'),('2026-10-06 09:45',1,'with'),('2026-10-07 10:25',1,'with'),('2026-10-07 10:55',1,'with'),
('2026-10-08 10:35',-1,'with'),('2026-10-08 13:15',-1,'with'),('2026-10-09 10:05',1,'ctr'),('2026-10-09 13:40',1,'with'),('2026-10-12 09:50',-1,'with')]
idx=[ts.index(t) for t,_,_ in T]
good=[]
lens=[5,8,9,10,12,13,14,15,20,21,25,26,30,34,40,50,55,60,75,89,100,120,144,150,200,233,250,300]
MA={}
for n in lens: MA[('e',n)]=ema(cl,n); MA[('s',n)]=sma(cl,n)
keys=list(MA)
# price vs MA
for k in keys:
    ok=all(((d*(cl[i]-MA[k][i])>0)==(lab=='with')) for i,(t,d,lab) in zip(idx,T))
    if ok: good.append(('close vs',k))
for a in keys:
    for b in keys:
        if a[1]>=b[1] or a[0]!=b[0]: continue
        ok=all(((d*(MA[a][i]-MA[b][i])>0)==(lab=='with')) for i,(t,d,lab) in zip(idx,T))
        if ok: good.append(('cross',a,b))
print(len(good)); print(good[:40])
extra=[('2026-10-07 09:35',-1,'skip'),('2026-10-07 13:05',-1,'skip'),('2026-10-08 12:15',-1,'skip'),('2026-10-08 14:00',-1,'mine'),('2026-10-12 13:10',-1,'mine')]
for k in [('s',233),('e',250),('e',300),('e',200)]:
    print(k,[ (t[5:],lab,round(d*(cl[ts.index(t)]-MA[k][ts.index(t)]),1)) for t,d,lab in T+extra])
