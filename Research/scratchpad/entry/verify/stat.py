import sys; sys.path.insert(0,"/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/entry/verify")
from v import *
z=np.load('state.npz'); ic,dc,hc,ib,b1,b2=[z[k] for k in ('ic','dc','hc','ib','bl1','bl2')]
rng=np.random.default_rng(1)
day=u5//86400
spb=sp5[ib]
def ex(mask_t, dd, s_, bootstrap=False):
    pass
# baseline per split/dir
base={}
for s_ in range(3):
    base[(s_,1)]=b1[spb==s_].mean(0)*100; base[(s_,-1)]=b2[spb==s_].mean(0)*100
def excess_vec(m): # per-trade avg-over-TP hit minus baseline
    return None
# day-cluster bootstrap for excess
def boot(s_, dsel, B=3000):
    m=(sp5[ic]==s_)&np.isin(dc,dsel)
    h=hc[m].mean(1)*100  # per trade avg hit over TP
    dd=dc[m]; days=day[ic][m]
    b=np.array([base[(s_,x)].mean() for x in dd])
    x=h-b
    ud,inv=np.unique(days,return_inverse=True)
    sums=np.bincount(inv,x); cnt=np.bincount(inv)
    out=[]
    for _ in range(B):
        k=rng.integers(0,len(ud),len(ud)); out.append(sums[k].sum()/cnt[k].sum())
    out=np.array(out)
    return x.mean(),out.std(),np.percentile(out,[2.5,97.5]),m.sum()
for s_,nm in enumerate(['train','valid','test']):
    for dsel,dn in (([1],'long'),([-1],'short'),([1,-1],'both')):
        e,sd,ci,n_=boot(s_,dsel)
        print(nm,dn,n_,'excess %+.2f se %.2f CI [%+.2f,%+.2f]'%(e,sd,ci[0],ci[1]))
# pooled train+valid
for dsel,dn in (([1],'long'),([-1],'short'),([1,-1],'both')):
    xs=[];
    for s_ in (0,1):
        m=(sp5[ic]==s_)&np.isin(dc,dsel); xs.append(hc[m].mean(1)*100-np.array([base[(s_,x)].mean() for x in dc[m]]))
    x=np.concatenate(xs); print('train+valid',dn,len(x),'%+.2f'%x.mean())
# test half-splits and by-month
m=(sp5[ic]==2)
t=u5[ic][m].astype('datetime64[M]')
for mo in np.unique(t):
    mm=m.copy(); mm[m]=(t==mo)
    x=hc[mm].mean(1)*100-np.array([base[(2,x)].mean() for x in dc[mm]])
    print(mo,mm.sum(),'%+.1f'%x.mean())
# power: if true excess were E (train+valid both), prob test both excess<=observed
