import json,statistics as st,sys
D=json.load(open('/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/hunt5/altmetric/F.json'))
pos=[o for o in D if o['pos']]; neg=[o for o in D if not o['pos']]
lab=lambda o:o['sym'][:2]+o['t'][5:]
out=[]
for k in D[0]['f']:
    best=None
    for sgn in (1,-1):
        pv=[sgn*o['f'][k] for o in pos]; nv=[sgn*o['f'][k] for o in neg]
        # cost (positives lost) to remove all 5 / 4 / 3 negatives
        ns=sorted(nv,reverse=True)
        cost={m: sum(1 for x in pv if x<=ns[5-m]) for m in (3,4,5)}
        # mean rank of negatives among all (AUC)
        auc=sum((a>b)+0.5*(a==b) for a in pv for b in nv)/(len(pv)*len(nv))
        r=(cost[5],cost[4],cost[3],round(auc,3),sgn)
        if best is None or r<best: best=r
    out.append((best,k))
out.sort()
print('feature  lost-to-remove-5/5  4/5  3/5  AUC(pos>neg)  orientation')
for b,k in out[:int(sys.argv[1])]: print('%-16s %3d %3d %3d  %.3f %s'%(k,*b[:4],'+' if b[4]>0 else '-'))
