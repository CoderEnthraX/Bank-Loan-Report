"""full-engine evaluation of gates through lib.run_all (ghost and plain veto). usage: evalfull.py '<json list of [tag, gate]>'"""
import sys, pickle, json, os
S='/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad'
sys.path.insert(0,S+'/research'); sys.path.insert(0,S+'/research/ema'); import lib, ev
M=S+'/research/ema/score_ema.py'; base=pickle.load(open('base.pkl','rb')); bn,be=lib.split(base)
RN=pickle.load(open('rndnull.pkl','rb')) if os.path.exists('rndnull.pkl') else {}
import glob
for _f in glob.glob('rnd2_*.pkl'): RN.update(pickle.load(open(_f,'rb')))
def ghost_null(share, it=300):
    """exact ghost-mode random null: random subsets of the baseline list keeping `share` (independent per trade)."""
    import random; r=random.Random(5); te=[];ss=[];tot=[]
    for _ in range(it):
        s=[x for x in base if r.random()<share]; a,b=lib.split(s); te.append(ev.E(b)-ev.E(be)); ss.append(ev.syms_better(base,s)[0]); tot.append(sum(x['res'] for x in s))
    return te,ss,tot
def plain_null(keep):
    """random plain-veto runs whose kept share is within 4 points of `keep`."""
    v=[r for k,r in RN.items() if abs(r['keep']-keep)<=0.04]; return [r['dte'] for r in v],[r['syms'] for r in v],[r['tot'] for r in v]
def evaluate(tag, gate, ghost):
    tr=lib.run_all(M,{'emaGate':gate,'emaGhost':ghost}); tn,te=lib.split(tr); keep=len(tr)/len(base)
    lo,hi=ev.paired_ci(be,te); llo,lhi=lib.boot_diff(be,te); k,m=ev.syms_better(base,tr); tot=sum(x['res'] for x in tr)
    nt,ns,ntot=(ghost_null(keep) if ghost else plain_null(keep)); d=ev.E(te)-ev.E(be)
    pr=ev.pct(sorted(nt),d) if nt else float('nan')
    s=lib.stats(te)
    out=('%-30s %-5s | TRAIN n=%d E2 %+.3f (d %+.3f) | TEST n=%d E2 %+.3f (d %+.3f) hit2 %.1f%% pairedCI [%+.3f,%+.3f] libCI [%+.3f,%+.3f] | syms %d/10 | kept %.0f%% tot %+.0f (base +197) | null(n=%d) pct %.2f p95 %+.3f'%(
        tag,'ghost' if ghost else 'plain',len(tn),ev.E(tn),ev.E(tn)-ev.E(bn),len(te),ev.E(te),d,100*s['hit2'],lo,hi,llo,lhi,k,keep*100,tot,len(nt),pr,sorted(nt)[int(.95*len(nt))] if nt else float('nan')))
    return out, tr
if __name__=='__main__':
    C=json.loads(sys.argv[1])
    for tag,g in C:
        for gh in (True,False):
            o,_=evaluate(tag,g,gh); print(o,flush=True)
            open('progress.md','a').write('- evalfull %s %s\n'%(json.dumps(g),o))
