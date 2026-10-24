import sys, pickle, random
S='/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad'
sys.path.insert(0,S+'/research/ema'); import feats
base=pickle.load(open('base.pkl','rb')); rnd=random.Random(3); smp=rnd.sample(base,60); N=feats.names(); bad=0; cnt=0
for x in smp:
    P=feats.prepare(x['sym']); i=x['arm']
    Q={k:(v[:i+1] if isinstance(v,list) else v) for k,v in P.items()}
    Ft=feats.compute(x['sym'],Q); Ff=feats.compute(x['sym'])
    for nm in N:
        a=feats.value(Ff,nm,i,x['dir'],x['entry']); b=feats.value(Ft,nm,i,x['dir'],x['entry']); cnt+=1
        if (a is None)!=(b is None) or (a is not None and abs(a-b)>1e-9): bad+=1; print('MISMATCH',x['sym'],i,nm,a,b) if bad<10 else None
print('checked',cnt,'mismatches',bad, 'features',len(N))
