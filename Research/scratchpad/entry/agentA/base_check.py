import sys; S='/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad'; sys.path.insert(0,S+'/entry')
import os; os.environ.setdefault('NUMBA_NUM_THREADS','2')
import numpy as np, data, outcomes, dataset
rng=np.random.default_rng(1)
TPR=np.array([.6,1,1.5,2])
for tf in ('M5','M15'):
    b=data.load(tf); n=b['n']
    ok=np.flatnonzero(~np.isnan(b['atr'])&(b['utc_wd']!=6)); ok=ok[(ok<n-10)]
    i=np.sort(rng.choice(ok,40000,replace=False)); sp=dataset.split_of(b['utc'][i])
    print(tf,'median atr',np.nanmedian(b['atr']),'median spread',np.median(b['SP']))
    for k in (0.6,1.0,1.8,3.0,5.0):
        for d in (1,-1):
            dd=np.full(len(i),d); e=b['C'][i]; st=e-d*k*b['atr'][i]
            o=outcomes.simulate(tf,i,dd,e,st,mode=1); m=o['mfe_m']
            s=' '.join('%s %s'%(s_, ' '.join('%5.1f'%(100*np.mean(m[(sp==s_)&~np.isnan(m)]>=r-1e-9)) for r in TPR)) for s_ in ('train','valid'))
            print(tf,k,d,s)
