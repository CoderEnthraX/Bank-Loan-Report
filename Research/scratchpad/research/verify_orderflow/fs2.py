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

byte=sorted(allreal,key=lambda v:-v[1])
print('TOP-8 by TEST d (oracle):')
for v in byte[:8]: print('  %-14s %s f=%.2f kept=%.2f TRAIN d %+.3f TEST d %+.3f'%(v[2],v[3],v[4],v[6],v[0],v[1]))
print('n variants',len(allreal),' TEST d>=0.05:',sum(1 for v in allreal if v[1]>=0.05),' TEST d>=0.082:',sum(1 for v in allreal if v[1]>=0.082))
print('real family: variants with TRAIN d>0 & TEST d>0:',sum(1 for v in allreal if v[0]>0 and v[1]>0),'of',len(allreal))
