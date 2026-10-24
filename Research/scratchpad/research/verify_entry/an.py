import sys, json, pickle, random, math
sys.path.insert(0,'/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/research')
import lib
res=pickle.load(open('grid.pkl','rb'))
base=res['{}']; bn,be=lib.split(base)
def E(tr,k='E2'): s=lib.stats(tr); return s[k] if s['n'] else float('nan')
print('base TRAIN %.3f TEST %.3f ALL %.3f n=%d'%(E(bn),E(be),E(base),len(base)))
rows=[]
for k,tr in res.items():
    tn,te=lib.split(tr); o=json.loads(k)
    imp=sum(1 for s in lib.SYMS if E([x for x in tr if x['sym']==s])>E([x for x in base if x['sym']==s]))
    sn,se=lib.stats(tn),lib.stats(te)
    print('%-34s n=%4d TRAIN E2 %+.3f (d %+.3f) TEST E2 %+.3f (d %+.3f) E1 %+.3f E15 %+.3f tot %+4.0f imp %d/10'%(k,len(tr),sn['E2'],sn['E2']-E(bn),se['E2'],se['E2']-E(be),se['E1'],se['E15'],lib.stats(tr)['totR2'],imp))
# per-symbol for two methods
for k in ['{"beR": 1.0}','{"beR": 1.0, "retestBars": 3}']:
    tr=res[k]; print(k)
    print('  per-sym d E2 ALL:',' '.join('%s %+.2f'%(s[:5],E([x for x in tr if x['sym']==s])-E([x for x in base if x['sym']==s])) for s in lib.SYMS))
    tn,te=lib.split(tr)
    for key in ['E2','E1','E15']:
        pass
    lo,hi=lib.boot_diff(be,te); print('  TEST E2 CI',lo,hi)
    # ALL-data CI
    lo,hi=lib.boot_diff(base,tr); print('  ALL E2 diff %.3f CI [%.3f %.3f]'%(E(tr)-E(base),lo,hi))
    # train CI
    lo,hi=lib.boot_diff(bn,tn); print('  TRAIN E2 diff %.3f CI [%.3f %.3f]'%(E(tn)-E(bn),lo,hi))
    # E1/E15 CI via key conversion
    for nm,f in [('E1',lambda x:1 if x['hit1'] else -1),('E15',lambda x:1.5 if x['hit15'] else -1)]:
        a=[dict(x,v=f(x)) for x in be]; b=[dict(x,v=f(x)) for x in te]
        lo,hi=lib.boot_diff(a,b,key='v'); print('  TEST %s diff %.3f CI [%.3f %.3f]'%(nm,E(te,nm)-E(be,nm),lo,hi))
    # all-data E1/E15
    print('  ALL E1 %.3f vs %.3f ; E15 %.3f vs %.3f'%(E(tr,'E1'),E(base,'E1'),E(tr,'E15'),E(base,'E15')))
