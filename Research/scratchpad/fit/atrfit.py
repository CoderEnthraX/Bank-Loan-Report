import sys, os, itertools
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from arp_data import load, find
# (symbol, displacement bar, direction, entry, stop, R from targets)
T = [('GC','2026-10-09 20:50',1,4214.3,4205.5,None),('GC','2026-10-12 05:50',1,4234.3,4226.1,None),
     ('EURUSD','2026-10-09 12:45',1,1.12290,1.12224,(1.12421-1.12290)/2),
     ('SENSEX','2026-10-12 11:10',-1,71977.95,72131.62,(71977.95-71670.61)/2),
     ('NASDAQ','2026-10-12 11:10',-1,30984.1,31014.2,(30984.1-30923.9)/2),
     ('NASDAQ','2026-10-09 12:50',1,31000.2,30963.8,None)]
def tr(rows):
    out=[rows[0]['h']-rows[0]['l']]
    for a,b in zip(rows,rows[1:]): out.append(max(b['h']-b['l'],abs(b['h']-a['c']),abs(b['l']-a['c'])))
    return out
def rma(x,n):
    o=[None]*len(x); s=None
    for i in range(len(x)):
        if i<n-1: continue
        s = sum(x[i-n+1:i+1])/n if s is None else (s*(n-1)+x[i])/n
        o[i]=s
    return o
def sma(x,n): return [None if i<n-1 else sum(x[i-n+1:i+1])/n for i in range(len(x))]
def ema(x,n):
    o=[None]*len(x); a=2/(n+1); s=None
    for i in range(len(x)):
        if i<n-1: continue
        s = sum(x[i-n+1:i+1])/n if s is None else a*x[i]+(1-a)*s
        o[i]=s
    return o
cache={}
res={}
for sym,t,d,e,s,rt in T:
    rows=cache.setdefault(sym,load(sym)); i=find(rows,t); x=tr(rows)
    R = rt if rt else d*(e-s)
    for m,f in [('rma',rma),('sma',sma),('ema',ema)]:
        for n in range(5,31):
            a=f(x,n)
            for lag in (0,1):
                res.setdefault((m,n,lag),[]).append(R/a[i-lag])
best=sorted(res.items(), key=lambda kv: (max(kv[1])-min(kv[1]))/ (sum(kv[1])/len(kv[1])))
for k,v in best[:12]:
    mean=sum(v)/len(v); print(k, 'k=%.4f'%mean, 'spread=%.2f%%'%(100*(max(v)-min(v))/mean), ['%.3f'%r for r in v])
print('--- rma14 lag0:', ['%.4f'%r for r in res[('rma',14,0)]])
