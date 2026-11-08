import sys; sys.path.insert(0,"/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/entry/verify")
from v import *
sg=signals.raw('M5'); i=sg['i']; ds=sg['d'].astype(int)
print('raw signals',len(i), 'ATR match', np.nanmax(abs(atr-__import__('data').load('M5')['atr'])))
nm=ny_min(u5[i])
nogap=np.r_[u5[1:]-u5[:-1]==300,False][i]
keep=(nm>=720)&(nm<1080)&nogap
print('kept',keep.sum(),'of',len(i))
ic=i[keep]; dc=-ds[keep]
hc=run(ic,dc)
# baseline: all eligible bars, both dirs
ib=np.flatnonzero(ok)
res={}
bl={}
for dd in (1,-1):
    h=run(ib,np.full(len(ib),dd)); bl[dd]=h
    # also time-of-day matched
nmall=ny_min(u5[ib])
tod=(nmall>=720)&(nmall<1080)
spb=sp5[ib]
for s_,name in enumerate(['train','valid','test']):
    for dd,dn in ((1,'long'),(-1,'short')):
        r_all=bl[dd][spb==s_].mean(0)*100
        r_tod=bl[dd][(spb==s_)&tod].mean(0)*100
        m=(sp5[ic]==s_)&(dc==dd)
        hit=hc[m].mean(0)*100
        print(name,dn,'n',m.sum(),'hit',np.round(hit,1),'rand',np.round(r_all,1),'ex %+.2f'%(hit-r_all).mean(),'| rand NY12-18',np.round(r_tod,1),'ex_tod %+.2f'%(hit-r_tod).mean(), 'nrand',(spb==s_).sum())
    m=(sp5[ic]==s_)
    print(name,'both hit',np.round(hc[m].mean(0)*100,1))
np.savez('state.npz',ic=ic,dc=dc,hc=hc,ib=ib,bl1=bl[1],bl2=bl[-1])
