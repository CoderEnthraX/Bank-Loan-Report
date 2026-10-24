import sys; S='/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad'; sys.path.insert(0,S+'/research')
import lib
from collections import Counter, defaultdict
M=S+'/research/chop/score_chop.py'
base=lib.run_all(M,{})
def day_ci(a,b,it=2000):
    import random; r=random.Random(7)
    da=defaultdict(list); db=defaultdict(list)
    for x in a: da[(x['sym'],x['t'][:10])].append(x['res'])
    for x in b: db[(x['sym'],x['t'][:10])].append(x['res'])
    days=sorted(set(da)|set(db)); ds=[]
    for _ in range(it):
        s=[days[r.randrange(len(days))] for _ in days]
        A=[v for d in s for v in da.get(d,[])]; B=[v for d in s for v in db.get(d,[])]
        ds.append(sum(B)/max(1,len(B))-sum(A)/max(1,len(A)))
    ds.sort(); return ds[50],ds[1949]
for nm,o in (('F5 xR2<=9.73 ghost',{"chopRules":[["xR2","le",9.73]],"chopMode":"ghost"}),
             ('F5b xR2<=11.8 ghost',{"chopRules":[["xR2","le",11.8]],"chopMode":"ghost"}),
             ('F5 veto',{"chopRules":[["xR2","le",9.73]],"chopMode":"veto"})):
    f=lib.run_all(M,o); tn,te=lib.split(f); btn,bte=lib.split(base)
    imp=0
    for s in lib.SYMS:
        b_=[x['res'] for x in base if x['sym']==s]; f_=[x['res'] for x in f if x['sym']==s]
        imp+= (sum(f_)/max(1,len(f_)))>(sum(b_)/max(1,len(b_)))
    ng=[x['res'] for x in f if x['sym']=='MCX_NATURALGAS']
    print(nm,'| TRAIN %+.3f TEST %+.3f | dTEST %+.3f CI %s | kept %.0f%% | tot %+.0f | improved %d/10 | NATGAS n=%d E %+.3f'%(
        lib.stats(tn)['E2'],lib.stats(te)['E2'],lib.stats(te)['E2']-lib.stats(bte)['E2'],tuple(round(v,3) for v in day_ci(bte,te)),100*len(f)/len(base),sum(x['res'] for x in f),imp,len(ng),sum(ng)/max(1,len(ng))))
