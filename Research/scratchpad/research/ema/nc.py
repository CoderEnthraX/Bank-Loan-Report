import sys, pickle
S='/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad'
sys.path.insert(0,S+'/research'); sys.path.insert(0,S+'/research/ema'); import lib, ev
M=S+'/research/ema/score_ema.py'
b=lib.run_all(M,{'noChase':True}); bn,be=lib.split(b)
print('noChase base: ALL n=%d E %+.3f tot %+.0f | TRAIN %+.3f | TEST n=%d %+.3f'%(len(b),ev.E(b),sum(x['res'] for x in b),ev.E(bn),len(be),ev.E(be)))
for th in (1.652,2.0):
  for gh in (True,False):
    t=lib.run_all(M,{'noChase':True,'emaGate':[['h60_asl_E20_3','le',th]],'emaGhost':gh}); tn,te=lib.split(t); lo,hi=ev.paired_ci(be,te)
    print(' + h60cap %.2f %s: n=%d keep %.0f%% tot %+.0f | TRAIN %+.3f (d %+.3f) | TEST %+.3f (d %+.3f) CI [%+.3f,%+.3f] syms %d/10'%(th,'ghost' if gh else 'plain',len(t),100*len(t)/len(b),sum(x['res'] for x in t),ev.E(tn),ev.E(tn)-ev.E(bn),ev.E(te),ev.E(te)-ev.E(be),lo,hi,ev.syms_better(b,t)[0]))
