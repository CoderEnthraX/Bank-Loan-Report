import json, sys, numpy as np
S='/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad'
sys.path.insert(0,S+'/fit')
from engine2 import prepare
D=json.load(open(S+'/hunt3/pooled/featV.json'))
EX={('CRUDE','2026-10-06 20:55'),('CRUDE','2026-10-12 13:40'),('CRUDE','2026-10-15 18:30'),('CRUDE','2026-10-16 11:40'),('ETH','2026-10-11 00:05')}
items=[o for o in D if o['lab'] in('takenA','takenB') or (o['sym'],o['t']) in EX]
print(len(items))
real=np.array([(o['sym'],o['t']) in EX for o in items]); assert real.sum()==5
syms=np.array([o['sym'] for o in items])
# features
F={}
for k in items[0]['f']: F[k]=np.array([np.nan if o['f'][k] is None else float(o['f'][k]) for o in items])
Pc={}
for n in range(5,21):
    v=[]
    for o in items:
        P=Pc.setdefault(o['sym'],prepare(o['sym'])); C=P['C']; i=o['i']; d=o['d']
        path=sum(abs(C[j]-C[j-1]) for j in range(i-n+1,i+1)); v.append(d*(C[i]-C[i-n])/path if path else 0)
    F['ER%d'%n]=np.array(v)
ER=['ER%d'%n for n in range(5,21)]
S30=['mom5','mom10','mom15','brk10','brkC10','hbrk10','brk5','body%','ext%','rng/A','body/A','cv','vs3','z','since','atr/sma20','atr/sma50',
     'e9-e20','e20-e50','c-e50','c-e200','htf15prev','htf60prev','consecBefore','dayPos','dayMove','sinceExit','sinceOppSig','barsAboveV','ageExt10']
assert len(S30)==30 and all(k in F for k in S30)
ALL=[k for k in F]
def nsep(mask_ex, X):
    # X: features x items ; returns per-feature count of extras beyond taken range (best side)
    out=np.zeros(X.shape[0],int)
    tk=~mask_ex
    T=X[:,tk]; E=X[:,mask_ex]
    lo=np.nanmin(T,axis=1)[:,None]; hi=np.nanmax(T,axis=1)[:,None]
    below=np.sum(E<lo,axis=1); above=np.sum(E>hi,axis=1)
    return np.maximum(below,above)
sets={'S30':S30,'S30+ER16':S30+ER,'ALL('+str(len(ALL))+')':ALL,'ALL minus ER':[k for k in ALL if k not in ER]}
Xs={k:np.array([F[f] for f in v]) for k,v in sets.items()}
# observed
for name,X in Xs.items():
    r=nsep(real,X); print('OBSERVED',name,'features sep>=4:',int((r>=4).sum()),' ==5:',int((r==5).sum()),[ (sets[name][i],int(r[i])) for i in np.argsort(-r)[:6]])
rng=np.random.default_rng(12345)
N=10000
def sim(strat):
    res={k:[0,0,0] for k in sets}  # any>=4, any==5, count of perms
    maxs={k:[] for k in sets}
    idxC=np.where(syms=='CRUDE')[0]; idxE=np.where(syms=='ETH')[0]; n=len(items)
    for _ in range(N):
        m=np.zeros(n,bool)
        if strat=='uniform': m[rng.choice(n,5,replace=False)]=True
        elif strat=='stratified': m[rng.choice(idxC,4,replace=False)]=True; m[rng.choice(idxE,1)]=True
        elif strat=='crudeonly': m[rng.choice(idxC,5,replace=False)]=True
        for k,X in Xs.items():
            r=nsep(m,X); mx=r.max(); maxs[k].append(mx)
            res[k][0]+= mx>=4; res[k][1]+= mx==5
    return res,maxs
out={}
for strat in ('uniform','stratified','crudeonly'):
    res,maxs=sim(strat)
    for k in sets:
        a=np.array(maxs[k]); print(strat,k,'P(any feat sep>=4/5)=%.4f (%d/%d)  P(any ==5/5)=%.4f (%d/%d)  mean max sep %.2f'%(res[k][0]/N,res[k][0],N,res[k][1]/N,res[k][1],N,a.mean()))
