import sys; S='/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad'; sys.path.insert(0,S+'/research')
import lib
from collections import Counter
base=lib.run_all(S+'/xl/../build/score_ref.py' if False else S+'/research/ema/score_ema.py', {})
for cap in (1.65,2.0):
    f=lib.run_all(S+'/research/ema/score_ema.py', {"emaGate":[["h6s_asl_E20_3","le",cap]],"emaGhost":True})
    for nm,tr in (('base',base),('cap%.2f'%cap,f)):
        tn,te=lib.split(tr); print(nm,'ALL',lib.fmt(lib.stats(tr))); print(nm,'TR ',lib.fmt(lib.stats(tn))); print(nm,'TE ',lib.fmt(lib.stats(te)))
    # per symbol on TEST
    bt=Counter(); bn=Counter(); ft=Counter(); fn=Counter()
    for x in lib.split(base)[1]: bt[x['sym']]+=x['res']; bn[x['sym']]+=1
    for x in lib.split(f)[1]: ft[x['sym']]+=x['res']; fn[x['sym']]+=1
    allb=Counter();alln=Counter();allf=Counter();allfn=Counter()
    for x in base: allb[x['sym']]+=x['res']; alln[x['sym']]+=1
    for x in f: allf[x['sym']]+=x['res']; allfn[x['sym']]+=1
    better=0
    for s in lib.SYMS:
        eb=allb[s]/max(1,alln[s]); ef=allf[s]/max(1,allfn[s]); better+= ef>eb
        print('  %-15s base n=%3d E %+.3f | filt n=%3d E %+.3f'%(s,alln[s],eb,allfn[s],ef))
    print('  syms improved (all-period E):',better,'kept',len(f)/len(base))
