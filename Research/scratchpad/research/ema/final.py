import sys, pickle
S='/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad'
sys.path.insert(0,S+'/research'); sys.path.insert(0,S+'/research/ema'); import lib, ev, feats
M=S+'/research/ema/score_ema.py'; base=pickle.load(open('base.pkl','rb')); bn,be=lib.split(base)
for th in (1.65,2.0):
    tr=lib.run_all(M,{'emaGate':[['h6s_asl_E20_3','le',th]],'emaGhost':True}); tn,te=lib.split(tr)
    print('cap %.2f'%th); print('  BASE TEST',lib.fmt(lib.stats(be))); print('  FILT TEST',lib.fmt(lib.stats(te))); print('  BASE TRAIN',lib.fmt(lib.stats(bn))); print('  FILT TRAIN',lib.fmt(lib.stats(tn)))
    for s in ev.SYMS:
        b=[x for x in base if x['sym']==s]; f=[x for x in tr if x['sym']==s]; print('   %-15s %3d %+.3f -> %3d %+.3f'%(s,len(b),ev.E(b),len(f),ev.E(f)))
o=pickle.load(open('orig.pkl','rb'))
for x in o:
    F=feats.compute(x['sym']); P=feats.prepare(x['sym']); fi=P['T'].index(x['t'])
    # recompute at the stored arm (orig.py used matched arm or fill-1): reuse h60 key presence to find arm bar is not stored; recompute arm via ref run
import ref_ema
RUN={}
for th in (1.65,2.0):
    kw=kl=rw=rl=0
    for x in o:
        P=feats.prepare(x['sym']); fi=P['T'].index(x['t'])
        if x['sym'] not in RUN: RUN[x['sym']]=ref_ema.run(x['sym'])
        m=[y for y in RUN[x['sym']] if y['fill']==fi and y['dir']==x['d']]; arm=m[0]['arm'] if m else fi-1
        v=feats.value(feats.compute(x['sym']),'h6s_asl_E20_3',arm,x['d'])
        k=v is None or v<=th
        if x['win']: kw+=k; rw+=not k
        else: kl+=k; rl+=not k
    print('orig trades cap %.2f: kept %dW/%dL (win %.0f%%), removed %dW/%dL'%(th,kw,kl,100*kw/(kw+kl),rw,rl))
