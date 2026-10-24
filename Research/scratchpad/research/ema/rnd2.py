"""plain-veto random null at q (signal veto share) for seeds sd%2==part; checkpoint rnd2_<q>_<part>.pkl"""
import sys, pickle, os
S='/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad'
sys.path.insert(0,S+'/research'); sys.path.insert(0,S+'/research/ema'); import lib, ev
M=S+'/research/ema/score_ema.py'; base=pickle.load(open(S+'/research/ema/base.pkl','rb')); bn,be=lib.split(base)
q=float(sys.argv[1]); part=int(sys.argv[2]); f=S+'/research/ema/rnd2_%s_%d.pkl'%(q,part)
out=pickle.load(open(f,'rb')) if os.path.exists(f) else {}
for sd in range(part,200,2):
    k=(q,False,sd)
    if k in out: continue
    tr=lib.run_all(M,{'rndVeto':(q,sd),'emaGhost':False}); tn,te=lib.split(tr)
    out[k]=dict(keep=len(tr)/len(base), dtr=ev.E(tn)-ev.E(bn), dte=ev.E(te)-ev.E(be), tot=sum(x['res'] for x in tr), syms=ev.syms_better(base,tr)[0])
    pickle.dump(out,open(f,'wb'))
print('done',q,part,len(out))
