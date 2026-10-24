import pickle, sys, random
R='/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/research'
sys.path.insert(0,R); sys.path.insert(0,R+'/orderflow')
tr=pickle.load(open(R+'/orderflow/base_feats.pkl','rb'))
SPL='2026-10-01'
n=len(tr); res=[t['res'] for t in tr]; ist=[t['t']>=SPL for t in tr]
TRI=[i for i in range(n) if not ist[i]]; TEI=[i for i in range(n) if ist[i]]
mean=lambda idx:sum(res[i] for i in idx)/len(idx)
bTR=mean(TRI); bTE=mean(TEI)
keys=sorted({k for t in tr if t['f'] for k in t['f'] if t['f'][k] is not None and isinstance(t['f'][k],(int,float))})
rk=[k for k in keys if k.startswith('rand')]; real=[k for k in keys if not k.startswith('rand')]
print(len(real),'real feats',len(rk),'rand feats')
fr=[.70,.75,.80,.85,.90]
def variants(k):
    vals=[(i,tr[i]['f'].get(k) if tr[i]['f'] else None) for i in range(n)]
    known=[(i,v) for i,v in vals if v is not None]
    # thresholds from TRAIN quantiles only
    trv=sorted(v for i,v in known if not ist[i]); out=[]
    for side in ('le','ge'):
        for f in fr:
            if side=='le': thr=trv[min(len(trv)-1,int(f*len(trv)))]; ok=lambda v:v<=thr
            else: thr=trv[max(0,int((1-f)*len(trv)))]; ok=lambda v:v>=thr
            keep=[True]*n
            for i,v in known:
                if not ok(v): keep[i]=False
            a=[i for i in TRI if keep[i]]; b=[i for i in TEI if keep[i]]
            out.append((mean(a)-bTR,mean(b)-bTE,k,side,f,thr,sum(keep)/n))
    return out
V={k:variants(k) for k in keys}
allreal=[v for k in real for v in V[k]]
allreal.sort(key=lambda v:-v[0])
print('TOP-10 real variants by TRAIN dE2 (kept>=70%), with TEST dE2:')
for v in allreal[:12]: print('  %-14s %s f=%.2f thr=%.3f kept=%.2f TRAIN d %+.3f TEST d %+.3f'%(v[2],v[3],v[4],v[5],v[6],v[0],v[1]))
print('rank of z variants:',[(i+1,v[3],v[4],round(v[0],3),round(v[1],3)) for i,v in enumerate(allreal) if v[2]=='z'][:6])
# null: pick best TRAIN variant per random feature -> TEST dE2 ; and best among 29 random
best=[max(V[k],key=lambda v:v[0]) for k in rk]
print('rand feats (40): TRAIN-best variant: TRAIN d mean %+.3f max %+.3f ; TEST d mean %+.3f max %+.3f p90 %+.3f'%(sum(b[0] for b in best)/40,max(b[0] for b in best),sum(b[1] for b in best)/40,max(b[1] for b in best),sorted(b[1] for b in best)[36]))
print('rand 40 feats: #variants with TRAIN d>=+0.033 and TEST d>=+0.082:',sum(1 for k in rk for v in V[k] if v[0]>=0.033 and v[1]>=0.082),'of',sum(len(V[k]) for k in rk))
print('real 29 feats: #variants TRAIN>=.033&TEST>=.082:',sum(1 for k in real for v in V[k] if v[0]>=0.033 and v[1]>=0.082),'of',sum(len(V[k]) for k in real))
rbest=max(rk,key=lambda k:max(v[0] for v in V[k]))
# real family best TRAIN -> TEST
print('real best-by-TRAIN TEST d',allreal[0][1])
