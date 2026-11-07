import pickle, statistics, sys
from collections import defaultdict
S='/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad'
A=pickle.load(open(S+'/gold/monthly_trades.pkl','rb'))['trades'][('M15-S9','file1')]['trades']
B=pickle.load(open(S+'/gold/bestmonth_design.pkl','rb'))['M15-S7']
months=[(y,m) for y in range(2021,2027) for m in range(1,13) if (y,m)<=(2026,9)]
assert len(months)==69
def group(tr):
    g=defaultdict(list)
    for x in tr: g[(x['t'].year,x['t'].month)].append(x)
    return g
def runA(tr,LOCK=250,reset=False):
    g=group(tr); out={}
    for mo in months:
        pnl=0.0; L=[1,2,3]; n=0; mx=0.0; fall=0.0; maxr=0.0
        for x in g.get(mo,[]):
            if pnl>=LOCK: break
            units=L[0]+L[-1] if len(L)>=2 else L[0]
            risk=50*units
            if reset and risk>500:
                L=[1,2,3]; units=1; risk=50
            risk=min(risk,500)
            risk=min(risk,(10000+pnl)*x['levk'])
            p=risk*(x['res']-x['c'])/(1+x['c'])
            maxr=max(maxr,risk)
            if p>0:
                if len(L)>=2: L=L[1:-1]
                else: L=[]
                if not L: L=[1,2,3]
            else: L.append(units)
            pnl+=p; n+=1
            mx=max(mx,pnl); fall=max(fall,mx-pnl)
        out[mo]=(pnl,n,fall,maxr)
    return out
def runB(tr,LOCK=150):
    g=group(tr); out={}
    for mo in months:
        pnl=0.0; pool=0.0; n=0; k=0; mx=0.0; fall=0.0; maxr=0.0
        for x in g.get(mo,[]):
            if pnl>=LOCK: break
            risk=50*2**k
            risk=min(risk,500)
            risk=min(risk,(10000+pnl)*x['levk'])
            p=risk*(x['res']-x['c'])/(1+x['c'])
            maxr=max(maxr,risk)
            if p>0:
                pool=max(0,pool-p)
                if pool==0: k=0
            else: pool+=-p; k+=1
            pnl+=p; n+=1
            mx=max(mx,pnl); fall=max(fall,mx-pnl)
        out[mo]=(pnl,n,fall,maxr)
    return out
def rep(name,o):
    v=list(o.values()); p=[a[0] for a in v]
    print(name,'total %.1f'%sum(p),'worst %.1f'%min(p),'losing',sum(1 for a in p if a<=0),'(<0:',sum(1 for a in p if a<0),')',
      'maxrisk %.1f'%max(a[3] for a in v),'deepest fall %.1f'%max(a[2] for a in v),'median n',statistics.median(a[1] for a in v),
      'zero-trade months',sum(1 for a in v if a[1]==0))
    print('  losing:',[(m,round(a[0],1)) for m,a in o.items() if a[0]<=0])
rep('A',runA(A)); rep('A lock500',runA(A,500)); rep('A reset',runA(A,250,True))
rep('B',runB(B))
