import sys, pickle
S='/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad'
sys.path.insert(0,S+'/research'); sys.path.insert(0,S+'/research/ema'); import lib, ev
M=S+'/research/ema/score_ema.py'; base=pickle.load(open('base.pkl','rb'))
k=lambda x:(x['sym'],x['arm'],x['dir'])
pv=lib.run_all(M,{'emaGate':[['h60_asl_E20_3','le',1.652]],'emaGhost':False}); B={k(x) for x in base}; Pk={k(x) for x in pv}
new=[x for x in pv if k(x) not in B]; gone=[x for x in base if k(x) not in Pk]
print('plain veto: removed %d base trades (E %+.3f), added %d replacement trades (E %+.3f)'%(len(gone),ev.E(gone),len(new),ev.E(new)))
