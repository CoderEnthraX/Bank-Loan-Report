"""random signal-veto null through the full engine, plain-veto mode AND ghost mode; checkpointed to rndnull.pkl"""
import sys, pickle, os
S='/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad'
sys.path.insert(0,S+'/research'); sys.path.insert(0,S+'/research/ema'); import lib, ev
M=S+'/research/ema/score_ema.py'; base=pickle.load(open('base.pkl','rb')); bn,be=lib.split(base)
out=pickle.load(open('rndnull.pkl','rb')) if os.path.exists('rndnull.pkl') else {}
for q in (0.1,0.2,0.3,0.4):
  for ghost in (False,):
    for sd in range(200):
        k=(q,ghost,sd)
        if k in out: continue
        tr=lib.run_all(M,{'rndVeto':(q,sd),'emaGhost':ghost}); tn,te=lib.split(tr)
        out[k]=dict(keep=len(tr)/len(base), dtr=ev.E(tn)-ev.E(bn), dte=ev.E(te)-ev.E(be), tot=sum(x['res'] for x in tr), syms=ev.syms_better(base,tr)[0])
        if sd%20==19: pickle.dump(out,open('rndnull.pkl','wb')); print(q,ghost,sd,flush=True)
pickle.dump(out,open('rndnull.pkl','wb')); print('done')
