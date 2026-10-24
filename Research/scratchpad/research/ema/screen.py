import sys, pickle, json
S='/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad'
sys.path.insert(0,S+'/research'); sys.path.insert(0,S+'/research/ema'); import lib, feats, ev
tab=pickle.load(open('tab.pkl','rb')); tn,te=lib.split(tab); N=feats.names()
E0n, E0t = ev.E(tn), ev.E(te); TRS=[s for s in ev.SYMS if any(x['sym']==s for x in tn)]
def keep(x,nm,op,th):
    v=x['f'][nm]; return v is None or (v>=th if op=='ge' else v<=th)
rows=[]
for nm in N:
    vals=sorted(x['f'][nm] for x in tn if x['f'][nm] is not None)
    if not vals: continue
    ths=set()
    for q in (0.6,0.7,0.8,0.9,0.95):
        ths.add(('ge', vals[int((1-q)*len(vals))])); ths.add(('le', vals[min(len(vals)-1,int(q*len(vals)))]))
    if len(set(vals))<=12:
        for u in set(vals): ths.add(('ge',u)); ths.add(('le',u))
    for op,th in ths:
        a=[x for x in tn if keep(x,nm,op,th)]; b=[x for x in te if keep(x,nm,op,th)]
        if len(a)<0.6*len(tn) or len(a)==len(tn): continue
        k,m=ev.syms_better(tn,a,TRS)
        rows.append(dict(nm=nm,op=op,th=th,ntr=len(a),ktr=len(a)/len(tn),dtr=ev.E(a)-E0n,str=k,
                         nte=len(b),kte=len(b)/len(te),dte=ev.E(b)-E0t, totall=sum(x['res'] for x in a+b)))
pickle.dump(rows,open('screen.pkl','wb'))
print('variants',len(rows))
# correlation TRAIN vs TEST deltas
import statistics as st
xs=[r['dtr'] for r in rows]; ys=[r['dte'] for r in rows]
mx,my=st.mean(xs),st.mean(ys); c=sum((a-mx)*(b-my) for a,b in zip(xs,ys))/((sum((a-mx)**2 for a in xs)*sum((b-my)**2 for b in ys))**.5)
print('corr(dTRAIN,dTEST) %.3f  mean dTRAIN %+.3f mean dTEST %+.3f  share dTEST>0 %.2f'%(c,mx,my,sum(y>0 for y in ys)/len(ys)))
top=[r for r in rows if r['dtr']>0]; print('TRAIN-positive variants',len(top),'their mean dTEST %+.3f share>0 %.2f'%(st.mean([r['dte'] for r in top]),sum(r['dte']>0 for r in top)/len(top)))
rows.sort(key=lambda r:-r['dtr'])
print('TOP 40 by TRAIN dE2 (ghost mode, exact):')
for r in rows[:40]: print('%-22s %s %8.3f | TRAIN keep %.0f%% dE %+.3f syms %d/8 | TEST keep %.0f%% dE %+.3f | totALL %+.0f'%(r['nm'],r['op'],r['th'],100*r['ktr'],r['dtr'],r['str'],100*r['kte'],r['dte'],r['totall']))
