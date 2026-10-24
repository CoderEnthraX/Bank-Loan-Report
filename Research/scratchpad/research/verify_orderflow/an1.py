import sys, pickle, random, statistics as st
R='/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/research'
rows=pickle.load(open(R+'/verify_orderflow/base_tab.pkl','rb'))
SPL='2026-10-01'
def e(ts,k='res'):
    if not ts: return float('nan')
    if k=='res': return sum(t['res'] for t in ts)/len(ts)
    if k=='e1': return sum(1 if t['hit1'] else -1 for t in ts)/len(ts)
    if k=='e15': return sum(1.5 if t['hit15'] else -1 for t in ts)/len(ts)
tr=[t for t in rows if t['t']<SPL]; te=[t for t in rows if t['t']>=SPL]
print('base TRAIN',len(tr),round(e(tr),3),'TEST',len(te),round(e(te),3))
def zf(t,key='z'): return None if t['fx'] is None else t['fx'][key]
# decile tables of z (signed stretch)
for nm,S in (('TRAIN',tr),('TEST',te),('ALL',rows)):
    v=[t for t in S if zf(t) is not None]
    v.sort(key=zf); n=len(v); print(nm,'z buckets (E2, n, median z)')
    for q in range(5):
        b=v[q*n//5:(q+1)*n//5]; print('  Q%d n=%d medz=%.2f E2=%+.3f E1=%+.3f'%(q+1,len(b),zf(b[len(b)//2]),e(b),e(b,'e1')))
    top=[t for t in v if zf(t)>2.4]; print('  z>2.4 n=%d E2=%+.3f ; z<=2.4 E2=%+.3f'%(len(top),e(top),e([t for t in v if zf(t)<=2.4])))
# threshold refit
grid=[1.4,1.6,1.8,2.0,2.2,2.4,2.6,2.8,3.0,3.5]
def keep(S,thr,key='z',side='le'):
    return [t for t in S if zf(t,key) is None or (zf(t,key)<=thr if side=='le' else zf(t,key)>=thr)]
print('z thr grid: kept%% and E2 on TRAIN / TEST')
for g in grid:
    a=keep(tr,g);b=keep(te,g); print(' z<=%.1f TRAIN keep %.0f%% E2 %+.3f (d %+.3f) | TEST keep %.0f%% E2 %+.3f (d %+.3f)'%(g,100*len(a)/len(tr),e(a),e(a)-e(tr),100*len(b)/len(te),e(b),e(b)-e(te)))
print('cvd thr grid')
for g in [-0.3,-0.15,-0.1,-0.05,-0.02,-0.006,0,0.02,0.05,0.1]:
    a=keep(tr,g,'cvd_clv','ge');b=keep(te,g,'cvd_clv','ge'); print(' cvd>=%.3f TRAIN keep %.0f%% E2 %+.3f (d %+.3f) | TEST keep %.0f%% E2 %+.3f (d %+.3f)'%(g,100*len(a)/len(tr),e(a),e(a)-e(tr),100*len(b)/len(te),e(b),e(b)-e(te)))
# early-session confound
print('bars since session start vs z')
for lo,hi in ((3,10),(10,25),(25,50),(50,500)):
    b=[t for t in rows if t['fx'] and lo<=t['bars']<hi]; vz=[t for t in b if t['fx']['z']>2.4]
    print(' bars[%d,%d) n=%d  frac z>2.4 %.0f%%  E2 all %+.3f  E2 z>2.4 %+.3f (n=%d)  E2 z<=2.4 %+.3f'%(lo,hi,len(b),100*len(vz)/max(1,len(b)),e(b),e(vz),len(vz),e([t for t in b if t['fx']['z']<=2.4])))
# per symbol: vetoed trades E2
for s in sorted({t['sym'] for t in rows}):
    S=[t for t in rows if t['sym']==s]; vt=[t for t in S if t['fx'] and t['fx']['z']>2.4]; kp=keep(S,2.4)
    print(' %-15s n=%d vetoed=%d E2(vetoed)=%+.3f E2 kept=%+.3f base %+.3f'%(s,len(S),len(vt),e(vt),e(kp),e(S)))
