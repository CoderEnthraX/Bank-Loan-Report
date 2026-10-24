import pickle,sys
tr=pickle.load(open('base_feats.pkl','rb')); SPL='2026-10-01'
def st(v):
    n=len(v); 
    return (n, sum(x['res'] for x in v)/n, sum(1 if x['hit1'] else -1 for x in v)/n, sum(1.5 if x['hit15'] else -1 for x in v)/n) if n else (0,0,0,0)
tn=[x for x in tr if x['t']<SPL]; te=[x for x in tr if x['t']>=SPL]
print('base TRAIN %d %+.3f %+.3f %+.3f  TEST %d %+.3f %+.3f %+.3f'%(st(tn)+st(te)))
keys=sorted({k for x in tr if x['f'] for k in x['f']})
res=[]
for k in keys:
    vals=sorted(x['f'][k] for x in tn if x['f'] and x['f'].get(k) is not None)
    for q in (0.1,0.2,0.3):
        for side in ('le','ge'):
            c = vals[int(len(vals)*(1-q))] if side=='le' else vals[int(len(vals)*q)]
            ok=lambda x: x['f'] is None or x['f'].get(k) is None or (x['f'][k]<=c if side=='le' else x['f'][k]>=c)
            a=[x for x in tn if ok(x)]; b=[x for x in te if ok(x)]
            res.append((st(a)[1]-st(tn)[1], k, side, round(c,3), q, st(a), st(b)))
res.sort(reverse=True)
for r in res[:30]:
    d,k,side,c,q,a,b=r
    print('%-14s %s %7.3f drop%.0f%% TRAIN n=%d E2 %+.3f E1 %+.3f E15 %+.3f | TEST n=%d E2 %+.3f E1 %+.3f E15 %+.3f'%((k,side,c,q*100)+a+b))
