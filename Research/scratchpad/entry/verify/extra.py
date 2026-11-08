import sys; sys.path.insert(0,"/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/entry/verify")
from v import *
z=np.load('state.npz'); ic,dc,hc,ib,b1,b2=[z[k] for k in ('ic','dc','hc','ib','bl1','bl2')]
spb=sp5[ib]
base={(s,1):b1[spb==s].mean(0)*100 for s in range(3)}; base.update({(s,-1):b2[spb==s].mean(0)*100 for s in range(3)})
# DST check: UTC hour range of kept signals in summer vs winter
t=u5[ic].astype('datetime64[s]'); mon=t.astype('datetime64[M]').astype(int)%12+1
for nm,sel in (('Jul',mon==7),('Jan',mon==1)):
    h=(u5[ic][sel]//3600)%24; print(nm,'UTC hours of kept',h.min(),h.max())
# transition weeks 2026 : Mar 8 2026, Nov 1 2025 -> check mapping directly
for ts in ('2025-10-31T16:00','2025-11-03T16:00','2026-03-06T16:00','2026-03-09T16:00'):
    u=int(np.datetime64(ts).astype('datetime64[s]').astype(int)); print(ts,'UTC -> NY min',ny_min(np.array([u]))[0]/60)
# test monthly
m=(sp5[ic]==2); mo=t.astype('datetime64[M]')
for x in np.unique(mo[m]):
    mm=m&(mo==x); e=hc[mm].mean(1)*100-np.array([base[(2,d)].mean() for d in dc[mm]])
    print(x,mm.sum(),'%+.1f'%e.mean())
# alt split boundary: test starting 2025-07-01 in NY/server time irrelevant; shift +-1 month
for sh in ('2025-06-01','2025-08-01','2025-09-01'):
    mm=u5[ic].astype('datetime64[s]')>=np.datetime64(sh)
    # baseline recomputed for the window
    sb=u5[ib].astype('datetime64[s]')>=np.datetime64(sh)
    ex=[]
    for dd,b in ((1,b1),(-1,b2)):
        x=mm&(dc==dd); ex.append(hc[x].mean(0).mean()*100-b[sb].mean()*100)
    print('test from',sh,'long/short excess %+.2f %+.2f'%tuple(ex),'n',mm.sum())
# variant: first M1 bar ignored for stop (i.e. both count from start) 
