import sys, copy, random
R='/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/research'
sys.path.insert(0,R); sys.path.insert(0,R+'/orderflow')
import of, pickle
rows=pickle.load(open(R+'/verify_orderflow/base_tab.pkl','rb'))
orig=of.eprep
P0={}
def trunc(P,k):
    Q={}
    for key,v in P.items():
        if isinstance(v,list) and len(v)==len(P['rows']): Q[key]=v[:k]
        else: Q[key]=v
    return Q
bad=0; tot=0; maxd=0
rnd=random.Random(3)
for sym in sorted({t['sym'] for t in rows}):
    full=orig(sym); n=len(full['rows'])
    of._c.clear(); of.eprep=orig; Ff=of.features(sym)
    arms=sorted({(t['arm'],t['dir'],t['entry']) for t in rows if t['sym']==sym})
    for cut in rnd.sample(arms,8):
        k=cut[0]+1   # data ends at the signal bar (inclusive)
        of._c.clear(); of.eprep=lambda s,k=k,full=full: trunc(full,k)
        Ft=of.features(sym)
        for (a,d,e) in arms:
            if a!=k-1: continue
            f1=of.sig_features(Ff,a,d,e,10); f2=of.sig_features(Ft,a,d,e,10)
            tot+=1
            if (f1 is None)!=(f2 is None): bad+=1; print('NONE mismatch',sym,a); continue
            if f1 is None: continue
            for key in ('z','zT','cvd_clv','zEntry'):
                x,y=f1[key],f2[key]
                if (x is None)!=(y is None): bad+=1; print('mismatch none',sym,a,key); continue
                if x is not None:
                    maxd=max(maxd,abs(x-y))
                    if abs(x-y)>1e-9: bad+=1; print('DIFF',sym,a,key,x,y)
of.eprep=orig
print('checked',tot,'signals (features recomputed from data truncated AT the signal bar) mismatches',bad,'max abs diff',maxd)
