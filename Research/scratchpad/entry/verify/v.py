import sys, os
os.environ['NUMBA_NUM_THREADS']='2'; os.environ['OMP_NUM_THREADS']='2'
S='/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/entry'
sys.path.insert(0,S)
import numpy as np, datetime
from numba import njit
from zoneinfo import ZoneInfo
import signals
m5=np.load(S+'/cache_M5.npz'); m1=np.load(S+'/cache_M1.npz')
u5=m5['utc']; O5,H5,L5,C5=[m5[k] for k in 'OHLC']
u1=m1['utc']; H1,L1=m1['H'],m1['L']
n=len(u5)
# ATR own
tr=np.empty(n); tr[0]=H5[0]-L5[0]
tr[1:]=np.maximum(H5[1:]-L5[1:],np.maximum(abs(H5[1:]-C5[:-1]),abs(L5[1:]-C5[:-1])))
atr=np.full(n,np.nan); s=tr[:14].mean(); atr[13]=s
for i in range(14,n):
    s=(s*13+tr[i])/14; atr[i]=s
@njit(cache=True)
def sim(H1,L1,start,d,e,R,tps):
    N=len(start); out=np.zeros((N,4),np.bool_)
    for s in range(N):
        q=start[s]
        if q<0: continue
        st=e[s]-d[s]*R[s]
        # first M1 bar: only stop counts
        if d[s]==1:
            if L1[q]<=st: continue
        else:
            if H1[q]>=st: continue
        best=e[s]; q+=1
        while q<len(H1):
            if d[s]==1:
                if L1[q]<=st: break
                if H1[q]>best: best=H1[q]
                mf=(best-e[s])/R[s]
            else:
                if H1[q]>=st: break
                if L1[q]<best: best=L1[q]
                mf=(e[s]-best)/R[s]
            for k in range(4):
                if mf>=tps[k]-1e-12: out[s,k]=True
            if out[s,3]: break
            q+=1
    return out
TP=np.array([0.6,1,1.5,2.0])
def run(idx,d):
    idx=np.asarray(idx); d=np.asarray(d,np.int64)
    start=np.searchsorted(u1,u5[idx]+300,'left')
    start=np.where(start<len(u1),start,-1)
    return sim(H1,L1,start,d,C5[idx],1.8*atr[idx],TP)
# time
def ny_min(u):
    z=ZoneInfo('America/New_York')
    out=np.empty(len(u),int); 
    for k,t in enumerate(u):
        x=datetime.datetime.fromtimestamp(int(t),z); out[k]=x.hour*60+x.minute
    return out
def split(u):
    t=u.astype('datetime64[s]')
    return np.where(t<np.datetime64('2024-01-01'),0,np.where(t<np.datetime64('2025-07-01'),1,2))
sp5=split(u5)
wd=((u5//86400)+3)%7
ok=(~np.isnan(atr))&(wd!=6)&(np.arange(n)<n-3)
