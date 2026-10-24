import sys, time, pickle
S='/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad'
sys.path.insert(0,S+'/research'); sys.path.insert(0,S+'/research/ema'); import lib, feats
M=S+'/research/ema/score_ema.py'
base=pickle.load(open('base.pkl','rb')); key=lambda x:(x['sym'],x['arm'],x['fill'],x['dir'],x['res'])
t=time.time(); tr=lib.run_all(M,{}); print('default identical', [key(x) for x in tr]==[key(x) for x in base], time.time()-t)
t=time.time(); g=[['px_E20','ge',0.5]]
gh=lib.run_all(M,{'emaGate':g}); print('gate run', time.time()-t)
def val(x): return feats.value(feats.compute(x['sym']),'px_E20',x['arm'],x['dir'],x['entry'])
sub=[x for x in base if (lambda v: v is None or v>=0.5)(val(x))]
print('ghost == base minus vetoed', [key(x) for x in gh]==[key(x) for x in sub], len(gh), len(sub))
pv=lib.run_all(M,{'emaGate':g,'emaGhost':False}); print('plain', len(pv), lib.fmt(lib.stats(pv)))
